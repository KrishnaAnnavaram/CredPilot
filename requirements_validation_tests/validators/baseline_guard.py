"""
Baseline protection.

The requirements baseline (``source_requirements/requirements_verbatim.md``) is
hashed at generation time. Every validation run re-hashes it and compares.

If the hash does not match, validation STOPS and reports
``REQUIREMENTS_BASELINE_MODIFIED``. This exists so that a failing implementation can
never be made to "pass" by quietly editing the requirements.

Legitimately changing the baseline (e.g. a genuinely revised source document) is done
by re-running ``python traceability/build_traceability.py --rewrite-hash`` and saying
so in the commit — never by editing the stored hash on its own.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

SUITE_ROOT = Path(__file__).resolve().parent.parent
BASELINE_PATH = SUITE_ROOT / "source_requirements" / "requirements_verbatim.md"
HASH_PATH = SUITE_ROOT / "traceability" / "source_requirements_hash.txt"

BASELINE_MODIFIED = "REQUIREMENTS_BASELINE_MODIFIED"
BASELINE_MISSING = "REQUIREMENTS_BASELINE_MISSING"
HASH_MISSING = "REQUIREMENTS_BASELINE_HASH_MISSING"
BASELINE_OK = "REQUIREMENTS_BASELINE_VERIFIED"


class BaselineIntegrityError(RuntimeError):
    """Raised when the requirements baseline fails its integrity check."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


@dataclass(frozen=True)
class BaselineStatus:
    code: str
    expected_sha256: str | None
    actual_sha256: str | None
    baseline_path: str
    hash_path: str

    @property
    def ok(self) -> bool:
        return self.code == BASELINE_OK


def sha256_of(path: Path) -> str:
    """SHA-256 of the file's raw bytes (no newline or encoding normalisation)."""
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_stored_hash() -> str | None:
    if not HASH_PATH.is_file():
        return None
    for line in HASH_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Accept "<sha256>" or the sha256sum style "<sha256>  <filename>".
        return line.split()[0]
    return None


def check_baseline() -> BaselineStatus:
    """Verify the baseline against its recorded hash. Does not raise."""
    if not BASELINE_PATH.is_file():
        return BaselineStatus(BASELINE_MISSING, None, None, str(BASELINE_PATH), str(HASH_PATH))

    actual = sha256_of(BASELINE_PATH)
    expected = _read_stored_hash()
    if expected is None:
        return BaselineStatus(HASH_MISSING, None, actual, str(BASELINE_PATH), str(HASH_PATH))
    code = BASELINE_OK if expected == actual else BASELINE_MODIFIED
    return BaselineStatus(code, expected, actual, str(BASELINE_PATH), str(HASH_PATH))


def require_baseline() -> BaselineStatus:
    """Verify the baseline and raise ``BaselineIntegrityError`` if it is not intact."""
    status = check_baseline()
    if status.ok:
        return status
    messages = {
        BASELINE_MISSING: f"requirements baseline not found at {status.baseline_path}",
        HASH_MISSING: f"no recorded hash at {status.hash_path}",
        BASELINE_MODIFIED: (
            f"requirements baseline hash mismatch. "
            f"expected={status.expected_sha256} actual={status.actual_sha256}. "
            "STOP VALIDATION - the requirement baseline has been altered since it was generated "
            "from the source document."
        ),
    }
    raise BaselineIntegrityError(status.code, messages[status.code])


def write_hash() -> str:
    """(Re)write the recorded hash. Only called by the traceability builder."""
    digest = sha256_of(BASELINE_PATH)
    HASH_PATH.parent.mkdir(parents=True, exist_ok=True)
    HASH_PATH.write_text(
        "# SHA-256 of source_requirements/requirements_verbatim.md\n"
        "# Verified before every validation run by validators/baseline_guard.py.\n"
        "# A mismatch halts validation with REQUIREMENTS_BASELINE_MODIFIED.\n"
        f"{digest}  requirements_verbatim.md\n",
        encoding="utf-8",
    )
    return digest


if __name__ == "__main__":  # pragma: no cover - CLI helper
    import sys

    from console import use_utf8_console

    use_utf8_console()
    st = check_baseline()
    print(f"baseline : {st.baseline_path}")
    print(f"expected : {st.expected_sha256}")
    print(f"actual   : {st.actual_sha256}")
    print(f"status   : {st.code}")
    sys.exit(0 if st.ok else 1)
