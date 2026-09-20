"""
Evidence primitives.

Every check in this suite ultimately calls one of the functions here, and every one
of them returns an :class:`Evidence` carrying a FACTUAL string: a resolved path, a
matched line with its line number, a record count, a git object listing, a captured
stdout. That is what makes a PASS defensible.

Hard rules encoded here:

* A check that cannot find what it is looking for returns ``ok=False``. It never
  returns "probably", "appears to", or a benefit of the doubt.
* Nothing under ``requirements_validation_tests/`` is ever scanned as implementation
  evidence. The QA layer must not be able to satisfy the requirements it is grading.
* "Committed" means git-tracked in the implementation repository, per the source
  document's Evidence-in-Repo Rule. If the target is not a git repository, committed
  checks fail and say so.
"""

from __future__ import annotations

import ast
import csv
import json
import os
import re
import subprocess
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Callable, Iterable, Sequence

SUITE_ROOT = Path(__file__).resolve().parent.parent

#: Never traversed when looking for implementation evidence.
EXCLUDED_DIR_NAMES = frozenset(
    {
        "requirements_validation_tests",  # this QA layer
        ".git",
        ".hg",
        ".svn",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".tox",
        ".venv",
        "venv",
        "env",
        "site-packages",
        "node_modules",
        ".idea",
        ".vscode",
        "dist",
        "build",
        ".eggs",
    }
)

TEXT_SUFFIXES = frozenset(
    {
        ".py", ".md", ".txt", ".json", ".jsonl", ".yaml", ".yml", ".toml", ".cfg",
        ".ini", ".csv", ".env", ".example", ".sh", ".bat", ".ps1", ".rst", ".gitignore",
    }
)

UNSPECIFIED = "UNSPECIFIED_BY_REQUIREMENT"


# --------------------------------------------------------------------------------------
# Evidence
# --------------------------------------------------------------------------------------


@dataclass
class Evidence:
    """The outcome of one primitive check, with the factual evidence behind it."""

    ok: bool
    summary: str
    details: dict = field(default_factory=dict)

    def __bool__(self) -> bool:  # pragma: no cover - convenience
        return self.ok

    def as_dict(self) -> dict:
        return {"ok": self.ok, "evidence": self.summary, "details": self.details}


def found(summary: str, **details) -> Evidence:
    return Evidence(True, summary, details)


def missing(summary: str, **details) -> Evidence:
    return Evidence(False, summary, details)


def combine(label: str, parts: Sequence[Evidence], mode: str = "all") -> Evidence:
    """Aggregate sub-evidence. ``mode`` is ``all`` or ``any``."""
    oks = [p.ok for p in parts]
    ok = all(oks) if mode == "all" else any(oks)
    lines = [f"[{'OK' if p.ok else 'NOT FOUND'}] {p.summary}" for p in parts]
    return Evidence(
        ok,
        f"{label} ({mode.upper()}: {sum(oks)}/{len(parts)} satisfied)\n" + "\n".join(lines),
        {"mode": mode, "parts": [p.as_dict() for p in parts]},
    )


# --------------------------------------------------------------------------------------
# Target resolution
# --------------------------------------------------------------------------------------


def resolve_target_root(explicit: str | os.PathLike | None = None) -> Path:
    """Locate the CredPilot implementation to validate.

    Priority: explicit argument, then ``CREDPILOT_ROOT``, then
    ``config/validation_config.json``, then the suite's parent directory.
    """
    if explicit:
        return Path(explicit).resolve()
    env = os.environ.get("CREDPILOT_ROOT")
    if env:
        return Path(env).resolve()
    cfg_path = SUITE_ROOT / "config" / "validation_config.json"
    if cfg_path.is_file():
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            cfg = {}
        configured = cfg.get("implementation_root")
        if configured:
            p = Path(configured)
            return (p if p.is_absolute() else (SUITE_ROOT / p)).resolve()
    return SUITE_ROOT.parent.resolve()


@lru_cache(maxsize=8)
def _load_config(suite_root: str) -> dict:
    cfg_path = Path(suite_root) / "config" / "validation_config.json"
    if not cfg_path.is_file():
        return {}
    try:
        return json.loads(cfg_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


class Context:
    """Everything a check needs to inspect one implementation tree."""

    def __init__(self, target_root: str | os.PathLike | None = None) -> None:
        self.root = resolve_target_root(target_root)
        self.suite_root = SUITE_ROOT
        self.config = _load_config(str(SUITE_ROOT))

    # -- listing -----------------------------------------------------------------

    @property
    def exists(self) -> bool:
        return self.root.is_dir()

    def _walk(self) -> Iterable[Path]:
        if not self.root.is_dir():
            return
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIR_NAMES]
            base = Path(dirpath)
            for name in filenames:
                yield base / name

    @lru_cache(maxsize=1)
    def all_files(self) -> tuple[Path, ...]:
        return tuple(sorted(self._walk()))

    def rel(self, path: Path) -> str:
        try:
            return path.relative_to(self.root).as_posix()
        except ValueError:  # pragma: no cover - path outside target
            return str(path)

    # -- git ---------------------------------------------------------------------

    @lru_cache(maxsize=1)
    def git_tracked(self) -> frozenset[str]:
        """Posix-style relative paths of git-tracked files, or empty if not a repo."""
        if not (self.root / ".git").exists():
            return frozenset()
        try:
            out = subprocess.run(
                ["git", "ls-files"],
                cwd=str(self.root),
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):  # pragma: no cover
            return frozenset()
        if out.returncode != 0:
            return frozenset()
        return frozenset(line.strip() for line in out.stdout.splitlines() if line.strip())

    @property
    def is_git_repo(self) -> bool:
        return (self.root / ".git").exists()

    def is_committed(self, path: Path) -> bool:
        return self.rel(path) in self.git_tracked()


# --------------------------------------------------------------------------------------
# Path location  ("at (or near) the path shown" - REQ-070)
# --------------------------------------------------------------------------------------


@dataclass
class Located:
    path: Path | None
    exact: bool
    searched: str
    candidates: list[str] = field(default_factory=list)


def locate_file(ctx: Context, relpath: str) -> Located:
    """Find a file at, or near, ``relpath``.

    The source document says artifacts must be "present at (or near) the path shown",
    so an exact hit is preferred but a same-basename hit elsewhere in the tree is
    accepted and reported as a near match with its real location.
    """
    exact = ctx.root / relpath
    if exact.is_file():
        return Located(exact, True, relpath)
    basename = Path(relpath).name
    near = [p for p in ctx.all_files() if p.name == basename]
    if near:
        return Located(near[0], False, relpath, [ctx.rel(p) for p in near])
    return Located(None, False, relpath)


def locate_dir(ctx: Context, relpath: str) -> Located:
    """Find a directory at, or near, ``relpath``."""
    exact = ctx.root / relpath
    if exact.is_dir():
        return Located(exact, True, relpath)
    wanted = Path(relpath.rstrip("/")).name
    seen: list[Path] = []
    if ctx.root.is_dir():
        for dirpath, dirnames, _ in os.walk(ctx.root):
            dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIR_NAMES]
            for d in dirnames:
                if d == wanted:
                    seen.append(Path(dirpath) / d)
    if seen:
        seen.sort()
        return Located(seen[0], False, relpath, [ctx.rel(p) for p in seen])
    return Located(None, False, relpath)


def _where(ctx: Context, loc: Located) -> str:
    assert loc.path is not None
    kind = "exact path" if loc.exact else f"near match for '{loc.searched}'"
    return f"{ctx.rel(loc.path)} ({kind})"


# --------------------------------------------------------------------------------------
# Existence primitives
# --------------------------------------------------------------------------------------


def file_exists(relpath: str) -> Callable[[Context], Evidence]:
    def check(ctx: Context) -> Evidence:
        loc = locate_file(ctx, relpath)
        if loc.path is None:
            return missing(f"No file at or near '{relpath}' under {ctx.root}")
        return found(
            f"File present: {_where(ctx, loc)}; size={loc.path.stat().st_size} bytes",
            path=ctx.rel(loc.path), exact=loc.exact, other_candidates=loc.candidates[1:],
        )

    return check


def any_file_exists(relpaths: Sequence[str], label: str = "") -> Callable[[Context], Evidence]:
    """Satisfied when at least one of the listed paths exists.

    Used only where the source document itself offers alternatives, e.g.
    "traces/phoenix_spans.parquet (or .jsonl)".
    """

    def check(ctx: Context) -> Evidence:
        for rel in relpaths:
            loc = locate_file(ctx, rel)
            if loc.path is not None:
                return found(
                    f"File present: {_where(ctx, loc)}; size={loc.path.stat().st_size} bytes",
                    path=ctx.rel(loc.path), exact=loc.exact, alternatives=list(relpaths),
                )
        return missing(
            f"None of the alternative paths exist{(' for ' + label) if label else ''}: "
            + ", ".join(relpaths)
        )

    return check


def dir_exists(relpath: str, require_nonempty: bool = True) -> Callable[[Context], Evidence]:
    def check(ctx: Context) -> Evidence:
        loc = locate_dir(ctx, relpath)
        if loc.path is None:
            return missing(f"No directory at or near '{relpath}' under {ctx.root}")
        entries = [p.name for p in sorted(loc.path.iterdir())] if loc.path.is_dir() else []
        if require_nonempty and not entries:
            return missing(f"Directory {_where(ctx, loc)} exists but is empty")
        return found(
            f"Directory present: {_where(ctx, loc)}; {len(entries)} entries: "
            + ", ".join(entries[:12]) + ("..." if len(entries) > 12 else ""),
            path=ctx.rel(loc.path), exact=loc.exact, entries=entries,
        )

    return check


def committed(relpath: str) -> Callable[[Context], Evidence]:
    """The artifact is tracked by git (Evidence-in-Repo Rule)."""

    def check(ctx: Context) -> Evidence:
        if not ctx.is_git_repo:
            return missing(
                f"Cannot verify '{relpath}' is committed: {ctx.root} is not a git repository, "
                "so no artifact in it can be shown to be committed evidence"
            )
        loc = locate_file(ctx, relpath)
        if loc.path is None:
            return missing(f"No file at or near '{relpath}' to check for commitment")
        rel = ctx.rel(loc.path)
        if rel in ctx.git_tracked():
            return found(f"git ls-files lists '{rel}' -> artifact is committed", path=rel)
        return missing(f"'{rel}' exists on disk but is NOT listed by git ls-files (uncommitted)")

    return check


def is_git_repository() -> Callable[[Context], Evidence]:
    def check(ctx: Context) -> Evidence:
        if not ctx.root.is_dir():
            return missing(f"Implementation root does not exist: {ctx.root}")
        if not ctx.is_git_repo:
            return missing(f"{ctx.root} contains no .git - it is not a Git repository")
        tracked = ctx.git_tracked()
        return found(
            f"{ctx.root} is a Git repository; git ls-files reports {len(tracked)} tracked files",
            tracked_count=len(tracked),
        )

    return check


def git_has_remote() -> Callable[[Context], Evidence]:
    def check(ctx: Context) -> Evidence:
        if not ctx.is_git_repo:
            return missing(f"{ctx.root} is not a Git repository, so it has no remote")
        try:
            out = subprocess.run(
                ["git", "remote", "-v"], cwd=str(ctx.root), capture_output=True,
                text=True, timeout=30, check=False,
            )
        except (OSError, subprocess.SubprocessError):  # pragma: no cover
            return missing("Unable to execute 'git remote -v'")
        remotes = [line for line in out.stdout.splitlines() if line.strip()]
        if not remotes:
            return missing("'git remote -v' returned no remotes - nothing has been pushed anywhere")
        return found("git remote -v:\n" + "\n".join(remotes), remotes=remotes)

    return check


# --------------------------------------------------------------------------------------
# Content primitives
# --------------------------------------------------------------------------------------


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:  # pragma: no cover
        return ""


def _first_match(text: str, pattern: str) -> tuple[int, str] | None:
    rx = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
    m = rx.search(text)
    if not m:
        return None
    line_no = text.count("\n", 0, m.start()) + 1
    line = text.splitlines()[line_no - 1].strip() if text.splitlines() else m.group(0)
    return line_no, line[:300]


def file_contains(
    relpath: str, patterns: Sequence[str], label: str, mode: str = "all"
) -> Callable[[Context], Evidence]:
    """Each regex in ``patterns`` must match (``all``) or at least one must (``any``)."""

    def check(ctx: Context) -> Evidence:
        loc = locate_file(ctx, relpath)
        if loc.path is None:
            return missing(f"Cannot check '{label}': no file at or near '{relpath}'")
        text = _read_text(loc.path)
        parts: list[Evidence] = []
        for pat in patterns:
            hit = _first_match(text, pat)
            if hit:
                parts.append(found(f"{ctx.rel(loc.path)}:{hit[0]}: {hit[1]}", pattern=pat))
            else:
                parts.append(missing(f"no match for /{pat}/ in {ctx.rel(loc.path)}", pattern=pat))
        return combine(f"{label} in {_where(ctx, loc)}", parts, mode)

    return check


def tree_contains(
    patterns: Sequence[str],
    label: str,
    suffixes: Sequence[str] = (".py",),
    mode: str = "all",
    under: str | None = None,
) -> Callable[[Context], Evidence]:
    """Each regex must match somewhere in the implementation tree.

    ``under`` restricts the search to a subtree (located at or near that path).
    """

    def check(ctx: Context) -> Evidence:
        scope_root = ctx.root
        scope_label = "implementation tree"
        if under:
            loc = locate_dir(ctx, under)
            if loc.path is None:
                return missing(f"Cannot check '{label}': no directory at or near '{under}'")
            scope_root = loc.path
            scope_label = f"'{ctx.rel(loc.path)}'"
        files = [
            p for p in ctx.all_files()
            if p.suffix.lower() in set(suffixes) and str(p).startswith(str(scope_root))
        ]
        if not files:
            return missing(f"Cannot check '{label}': no {list(suffixes)} files under {scope_label}")
        parts: list[Evidence] = []
        for pat in patterns:
            hit_ev: Evidence | None = None
            for p in files:
                hit = _first_match(_read_text(p), pat)
                if hit:
                    hit_ev = found(f"{ctx.rel(p)}:{hit[0]}: {hit[1]}", pattern=pat)
                    break
            parts.append(
                hit_ev or missing(f"no match for /{pat}/ in {len(files)} files under {scope_label}",
                                  pattern=pat)
            )
        return combine(f"{label} across {scope_label} ({len(files)} files)", parts, mode)

    return check


def tree_absent(
    patterns: Sequence[str], label: str, suffixes: Sequence[str] = (".py", ".md", ".txt", ".json")
) -> Callable[[Context], Evidence]:
    """NEGATIVE check: none of the regexes may match anywhere in the tree."""

    def check(ctx: Context) -> Evidence:
        files = [p for p in ctx.all_files() if p.suffix.lower() in set(suffixes)]
        hits: list[str] = []
        for pat in patterns:
            for p in files:
                hit = _first_match(_read_text(p), pat)
                if hit:
                    hits.append(f"/{pat}/ matched {ctx.rel(p)}:{hit[0]}: {hit[1]}")
        if hits:
            return missing(f"{label}: prohibited content found ({len(hits)} hit(s))\n" + "\n".join(hits[:20]))
        return found(f"{label}: no prohibited pattern matched across {len(files)} scanned files",
                     scanned=len(files), patterns=list(patterns))

    return check


def no_files_matching(globs: Sequence[str], label: str) -> Callable[[Context], Evidence]:
    """NEGATIVE check: no file in the tree may match these glob patterns."""

    def check(ctx: Context) -> Evidence:
        import fnmatch

        hits = [
            ctx.rel(p) for p in ctx.all_files()
            if any(fnmatch.fnmatch(ctx.rel(p), g) or fnmatch.fnmatch(p.name, g) for g in globs)
        ]
        if hits:
            return missing(f"{label}: found {len(hits)} matching file(s): " + ", ".join(hits[:20]))
        return found(f"{label}: no file matches {list(globs)} across {len(ctx.all_files())} files")

    return check


# --------------------------------------------------------------------------------------
# Structured-artifact primitives
# --------------------------------------------------------------------------------------


def read_jsonl(path: Path) -> tuple[list[dict], list[str]]:
    records: list[dict] = []
    errors: list[str] = []
    for i, line in enumerate(_read_text(path).splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {i}: {exc.msg}")
            continue
        if isinstance(obj, dict):
            records.append(obj)
        else:
            errors.append(f"line {i}: top-level value is {type(obj).__name__}, expected object")
    return records, errors


def jsonl_records(
    relpath: str, required_keys: Sequence[str], min_records: int = 1, label: str = ""
) -> Callable[[Context], Evidence]:
    """A JSONL artifact exists, parses, has >= ``min_records`` and carries the named keys."""

    def check(ctx: Context) -> Evidence:
        loc = locate_file(ctx, relpath)
        if loc.path is None:
            return missing(f"No JSONL artifact at or near '{relpath}'")
        records, errors = read_jsonl(loc.path)
        parts = [
            found(f"{ctx.rel(loc.path)} parsed: {len(records)} JSON object(s)")
            if not errors
            else missing(f"{ctx.rel(loc.path)} has malformed lines: " + "; ".join(errors[:5])),
            found(f"record count {len(records)} >= {min_records}")
            if len(records) >= min_records
            else missing(f"record count {len(records)} < required {min_records}"),
        ]
        present = set().union(*(r.keys() for r in records)) if records else set()
        for key in required_keys:
            if any(key in r for r in records):
                sample = next(r[key] for r in records if key in r)
                parts.append(found(f"key '{key}' present (sample value: {str(sample)[:90]!r})"))
            else:
                parts.append(
                    missing(f"key '{key}' absent from every record; keys seen: {sorted(present)}")
                )
        return combine(f"{label or relpath} at {_where(ctx, loc)}", parts, "all")

    return check


def json_keys(
    relpath: str, required_keys: Sequence[str], label: str = "", mode: str = "all"
) -> Callable[[Context], Evidence]:
    """A JSON artifact exists, parses, and contains the named keys at any depth."""

    def check(ctx: Context) -> Evidence:
        loc = locate_file(ctx, relpath)
        if loc.path is None:
            return missing(f"No JSON artifact at or near '{relpath}'")
        try:
            data = json.loads(_read_text(loc.path))
        except json.JSONDecodeError as exc:
            return missing(f"{ctx.rel(loc.path)} is not valid JSON: {exc}")

        seen: set[str] = set()

        def walk(node) -> None:
            if isinstance(node, dict):
                seen.update(node.keys())
                for v in node.values():
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)

        walk(data)
        parts = []
        for key in required_keys:
            rx = re.compile(key, re.IGNORECASE)
            hit = next((s for s in sorted(seen) if rx.search(s)), None)
            parts.append(
                found(f"key matching /{key}/ present as '{hit}'")
                if hit else missing(f"no key matching /{key}/; keys present: {sorted(seen)[:40]}")
            )
        return combine(f"{label or relpath} at {_where(ctx, loc)}", parts, mode)

    return check


def csv_has_rows(relpath: str, min_rows: int = 1, label: str = "") -> Callable[[Context], Evidence]:
    def check(ctx: Context) -> Evidence:
        loc = locate_file(ctx, relpath)
        if loc.path is None:
            return missing(f"No CSV artifact at or near '{relpath}'")
        try:
            with loc.path.open("r", encoding="utf-8", errors="replace", newline="") as fh:
                rows = list(csv.reader(fh))
        except OSError as exc:  # pragma: no cover
            return missing(f"Cannot read {ctx.rel(loc.path)}: {exc}")
        if not rows:
            return missing(f"{ctx.rel(loc.path)} is empty")
        header, data_rows = rows[0], rows[1:]
        if len(data_rows) < min_rows:
            return missing(
                f"{ctx.rel(loc.path)} has {len(data_rows)} data row(s), fewer than the "
                f"{min_rows} required; header={header}"
            )
        return found(
            f"{label or relpath}: {_where(ctx, loc)} header={header} with {len(data_rows)} data rows",
            header=header, rows=len(data_rows),
        )

    return check


def binary_artifact(
    relpath: str, min_bytes: int = 1, magic: bytes | None = None, label: str = ""
) -> Callable[[Context], Evidence]:
    """A non-text artifact (e.g. a PNG screenshot, a Parquet export) exists and is real."""

    def check(ctx: Context) -> Evidence:
        loc = locate_file(ctx, relpath)
        if loc.path is None:
            return missing(f"No artifact at or near '{relpath}'")
        size = loc.path.stat().st_size
        parts = [
            found(f"{ctx.rel(loc.path)} size={size} bytes (>= {min_bytes})")
            if size >= min_bytes
            else missing(f"{ctx.rel(loc.path)} size={size} bytes, below the {min_bytes}-byte floor")
        ]
        if magic is not None:
            head = loc.path.open("rb").read(len(magic))
            parts.append(
                found(f"file signature {head!r} matches expected {magic!r}")
                if head == magic
                else missing(f"file signature {head!r} does not match expected {magic!r}")
            )
        return combine(f"{label or relpath} at {_where(ctx, loc)}", parts, "all")

    return check


# --------------------------------------------------------------------------------------
# Python source analysis (AST-based, no import of implementation code)
# --------------------------------------------------------------------------------------


def _python_files(ctx: Context, under: str | None = None) -> list[Path]:
    files = [p for p in ctx.all_files() if p.suffix == ".py"]
    if under:
        loc = locate_dir(ctx, under)
        if loc.path is None:
            return []
        files = [p for p in files if str(p).startswith(str(loc.path))]
    return files


@lru_cache(maxsize=512)
def _parse(path_str: str) -> ast.AST | None:
    try:
        return ast.parse(Path(path_str).read_text(encoding="utf-8", errors="replace"))
    except (SyntaxError, OSError, ValueError):
        return None


def _call_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name):
                names.add(fn.id)
            elif isinstance(fn, ast.Attribute):
                names.add(fn.attr)
                parts: list[str] = [fn.attr]
                cur = fn.value
                while isinstance(cur, ast.Attribute):
                    parts.append(cur.attr)
                    cur = cur.value
                if isinstance(cur, ast.Name):
                    parts.append(cur.id)
                names.add(".".join(reversed(parts)))
    return names


def py_calls(
    call_names: Sequence[str], label: str, under: str | None = None, mode: str = "all"
) -> Callable[[Context], Evidence]:
    """The named callables are actually CALLED, not merely imported.

    Backs the source document's "called, not just imported" wording for the Phoenix
    tracer, and the "wired into" wording for guardrails and middleware.
    """

    def check(ctx: Context) -> Evidence:
        files = _python_files(ctx, under)
        if not files:
            where = f"'{under}'" if under else "the implementation tree"
            return missing(f"Cannot check '{label}': no Python files under {where}")
        parts: list[Evidence] = []
        for wanted in call_names:
            hit: Evidence | None = None
            for p in files:
                tree = _parse(str(p))
                if tree is None:
                    continue
                names = _call_names(tree)
                match = next((n for n in names if n == wanted or n.endswith("." + wanted)), None)
                if match:
                    hit = found(f"{ctx.rel(p)} contains a call to '{match}'", call=match)
                    break
            parts.append(hit or missing(f"no call to '{wanted}' in {len(files)} Python file(s)"))
        return combine(f"{label} (AST call analysis)", parts, mode)

    return check


def py_defines(
    symbols: Sequence[str], label: str, under: str | None = None, mode: str = "all"
) -> Callable[[Context], Evidence]:
    """The named functions/classes are DEFINED somewhere in scope."""

    def check(ctx: Context) -> Evidence:
        files = _python_files(ctx, under)
        if not files:
            where = f"'{under}'" if under else "the implementation tree"
            return missing(f"Cannot check '{label}': no Python files under {where}")
        parts: list[Evidence] = []
        for wanted in symbols:
            rx = re.compile(wanted, re.IGNORECASE)
            hit: Evidence | None = None
            for p in files:
                tree = _parse(str(p))
                if tree is None:
                    continue
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        if rx.search(node.name):
                            kind = "async def" if isinstance(node, ast.AsyncFunctionDef) else (
                                "class" if isinstance(node, ast.ClassDef) else "def")
                            hit = found(
                                f"{ctx.rel(p)}:{node.lineno}: {kind} {node.name}", symbol=node.name
                            )
                            break
                if hit:
                    break
            parts.append(hit or missing(f"no definition matching /{wanted}/ in {len(files)} file(s)"))
        return combine(f"{label} (AST definition analysis)", parts, mode)

    return check


def py_has_async(label: str, under: str | None = None, min_count: int = 1) -> Callable[[Context], Evidence]:
    """At least ``min_count`` ``async def`` definitions exist in scope."""

    def check(ctx: Context) -> Evidence:
        files = _python_files(ctx, under)
        if not files:
            where = f"'{under}'" if under else "the implementation tree"
            return missing(f"Cannot check '{label}': no Python files under {where}")
        hits: list[str] = []
        for p in files:
            tree = _parse(str(p))
            if tree is None:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.AsyncFunctionDef):
                    hits.append(f"{ctx.rel(p)}:{node.lineno}: async def {node.name}")
        if len(hits) < min_count:
            return missing(f"{label}: found {len(hits)} 'async def' definition(s), need >= {min_count}")
        return found(f"{label}: {len(hits)} async definition(s)\n" + "\n".join(hits[:12]))

    return check


def py_imports(
    modules: Sequence[str], label: str, under: str | None = None, mode: str = "all"
) -> Callable[[Context], Evidence]:
    """The named modules are imported somewhere in scope."""

    def check(ctx: Context) -> Evidence:
        files = _python_files(ctx, under)
        if not files:
            where = f"'{under}'" if under else "the implementation tree"
            return missing(f"Cannot check '{label}': no Python files under {where}")
        index: dict[str, str] = {}
        for p in files:
            tree = _parse(str(p))
            if tree is None:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for a in node.names:
                        index.setdefault(a.name, f"{ctx.rel(p)}:{node.lineno}: import {a.name}")
                elif isinstance(node, ast.ImportFrom) and node.module:
                    index.setdefault(
                        node.module, f"{ctx.rel(p)}:{node.lineno}: from {node.module} import ..."
                    )
        parts: list[Evidence] = []
        for wanted in modules:
            hit = next(
                (loc for mod, loc in sorted(index.items())
                 if mod == wanted or mod.startswith(wanted + ".")),
                None,
            )
            parts.append(found(hit) if hit else missing(f"module '{wanted}' is never imported"))
        return combine(f"{label} (import analysis)", parts, mode)

    return check


def py_counts_definitions(
    pattern: str, min_count: int, label: str, under: str | None = None
) -> Callable[[Context], Evidence]:
    """At least ``min_count`` DISTINCT definitions match ``pattern``.

    Used for the document's explicit counts, e.g. "supervisor + >=3 worker agents".
    """

    def check(ctx: Context) -> Evidence:
        files = _python_files(ctx, under)
        if not files:
            where = f"'{under}'" if under else "the implementation tree"
            return missing(f"Cannot check '{label}': no Python files under {where}")
        rx = re.compile(pattern, re.IGNORECASE)
        hits: dict[str, str] = {}
        for p in files:
            tree = _parse(str(p))
            if tree is None:
                continue
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    if rx.search(node.name):
                        hits.setdefault(node.name, f"{ctx.rel(p)}:{node.lineno}: {node.name}")
        if len(hits) < min_count:
            return missing(
                f"{label}: {len(hits)} distinct definition(s) match /{pattern}/, "
                f"need >= {min_count}. Found: {sorted(hits)}"
            )
        return found(
            f"{label}: {len(hits)} distinct definitions match /{pattern}/ (>= {min_count})\n"
            + "\n".join(list(hits.values())[:12]),
            names=sorted(hits),
        )

    return check


# --------------------------------------------------------------------------------------
# Dependency declaration
# --------------------------------------------------------------------------------------


DEP_FILES = ("requirements.txt", "requirements-dev.txt", "pyproject.toml", "setup.cfg",
             "setup.py", "Pipfile", "environment.yml", "constraints.txt")


def dependency_declared(
    packages: Sequence[str], label: str, mode: str = "all"
) -> Callable[[Context], Evidence]:
    """The named distributions are declared in a dependency manifest."""

    def check(ctx: Context) -> Evidence:
        blobs: list[tuple[str, str]] = []
        for name in DEP_FILES:
            loc = locate_file(ctx, name)
            if loc.path is not None:
                blobs.append((ctx.rel(loc.path), _read_text(loc.path)))
        if not blobs:
            return missing(
                f"Cannot check '{label}': no dependency manifest found "
                f"(looked for {', '.join(DEP_FILES)})"
            )
        parts: list[Evidence] = []
        for pkg in packages:
            rx = re.compile(rf"(?m)^[^#\n]*\b{re.escape(pkg)}\b")
            hit = None
            for rel, text in blobs:
                m = rx.search(text)
                if m:
                    line_no = text.count("\n", 0, m.start()) + 1
                    line = text.splitlines()[line_no - 1].strip()
                    hit = found(f"{rel}:{line_no}: {line}", package=pkg)
                    break
            parts.append(hit or missing(
                f"'{pkg}' not declared in any of: {', '.join(r for r, _ in blobs)}"))
        return combine(f"{label} (dependency manifests)", parts, mode)

    return check


def python_version_declared(minimum: str = "3.11") -> Callable[[Context], Evidence]:
    """A manifest or runbook states the required Python version."""

    def check(ctx: Context) -> Evidence:
        targets = ("pyproject.toml", "setup.cfg", "setup.py", ".python-version",
                   "runtime.txt", "README.md", "requirements.txt")
        pats = [
            rf"python[_\- ]?requires\s*[=:]\s*['\"]?>=\s*{re.escape(minimum)}",
            rf"requires-python\s*=\s*['\"]>=\s*{re.escape(minimum)}",
            rf"[Pp]ython\s*{re.escape(minimum)}\+",
            rf"^{re.escape(minimum)}(\.\d+)?$",
            rf"[Pp]ython\s*>=\s*{re.escape(minimum)}",
        ]
        for name in targets:
            loc = locate_file(ctx, name)
            if loc.path is None:
                continue
            text = _read_text(loc.path)
            for pat in pats:
                hit = _first_match(text, pat)
                if hit:
                    return found(
                        f"Python >= {minimum} declared at {ctx.rel(loc.path)}:{hit[0]}: {hit[1]}"
                    )
        return missing(
            f"No declaration of Python {minimum}+ found in any of: {', '.join(targets)}"
        )

    return check


# --------------------------------------------------------------------------------------
# Manual attestation channel
# --------------------------------------------------------------------------------------


MANUAL_ATTESTATIONS = SUITE_ROOT / "manual_evidence" / "manual_attestations.json"


def manual_attestation(test_id: str, what: str) -> Callable[[Context], Evidence]:
    """A statement that cannot be verified from the implementation tree at all.

    A human records concrete evidence in ``manual_evidence/manual_attestations.json``.
    Absent or empty evidence is a FAIL - no evidence is never a pass.
    """

    def check(_ctx: Context) -> Evidence:
        if not MANUAL_ATTESTATIONS.is_file():
            return missing(
                f"No manual evidence file at {MANUAL_ATTESTATIONS}; '{what}' is unattested -> FAIL"
            )
        try:
            data = json.loads(MANUAL_ATTESTATIONS.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return missing(f"manual_attestations.json is not valid JSON: {exc}")
        entry = (data.get("attestations") or {}).get(test_id)
        if not isinstance(entry, dict):
            return missing(f"No attestation recorded for {test_id} ('{what}') -> FAIL")
        ev = str(entry.get("evidence") or "").strip()
        attester = str(entry.get("attested_by") or "").strip()
        when = str(entry.get("attested_on") or "").strip()
        if not ev or not attester or not when:
            return missing(
                f"Attestation for {test_id} is incomplete "
                f"(evidence={ev!r}, attested_by={attester!r}, attested_on={when!r}) -> FAIL"
            )
        return found(f"Manual attestation for {test_id} by {attester} on {when}: {ev}")

    return check


def not_verifiable_from_artifact(what: str) -> Callable[[Context], Evidence]:
    """Records, with evidence, that the document specifies nothing testable here."""

    def check(_ctx: Context) -> Evidence:
        return Evidence(
            False,
            f"{UNSPECIFIED}: the source document states no value or artifact from which "
            f"'{what}' could be verified against an implementation.",
            {"unspecified": True, "subject": what},
        )

    return check


# --------------------------------------------------------------------------------------
# Combinators
# --------------------------------------------------------------------------------------


def all_of(label: str, *checks: Callable[[Context], Evidence]) -> Callable[[Context], Evidence]:
    """Every sub-check must produce satisfying evidence."""

    def check(ctx: Context) -> Evidence:
        return combine(label, [c(ctx) for c in checks], "all")

    return check


def any_of(label: str, *checks: Callable[[Context], Evidence]) -> Callable[[Context], Evidence]:
    """At least one sub-check must produce satisfying evidence.

    Only for alternatives the SOURCE DOCUMENT itself offers, e.g. "Chroma or FAISS",
    "parquet (or .jsonl)", "DeepEval (or equivalent)".
    """

    def check(ctx: Context) -> Evidence:
        return combine(label, [c(ctx) for c in checks], "any")

    return check
