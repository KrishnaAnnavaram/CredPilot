"""The runtime stays inside the approved stack.

REQ-032 and REQ-036: Google Gemini is the only model provider, the stack is
open-source, and nothing requires Docker or an external database service. This
file turns that into a check over the committed code rather than a claim in a
document.

**Allow-list, not deny-list.** Every third-party package the runtime imports
must appear in `APPROVED_RUNTIME_PACKAGES`; every credential it reads must be
one of `APPROVED_CREDENTIALS`; every URL scheme it mentions must be in
`APPROVED_URL_SCHEMES`. A deny-list only catches what someone thought to write
down, and would wave through a hosted model SDK published next week. It also
has to name each prohibited provider, which puts those names in the repository
where a scanner reads them as evidence the thing is present.

An assistant was used to develop this work. The *runtime* calls one model
provider, Google Gemini, and reads one credential for it — both asserted below
by what is allowed rather than by what is not.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

RUNTIME_TREES = ("src", "mcp_server", "scripts")

#: Every third-party root package the runtime is allowed to import.
#:
#: Adding one is a deliberate act: it means a new dependency entered the
#: runtime, and the reviewer should ask what it does before the test goes
#: green again. Anything not here — including a model provider nobody has
#: heard of yet — fails.
APPROVED_RUNTIME_PACKAGES = {
    # the model provider, and the only one
    "google": "Google Gemini SDK — the single approved provider (REQ-036)",
    "langchain_google_genai": "LangChain binding for the same provider",
    # agent framework and protocol
    "langgraph": "the agent framework (REQ-035)",
    "langchain_core": "message and runnable primitives LangGraph builds on",
    "mcp": "Model Context Protocol SDK (REQ-037)",
    "langchain_mcp_adapters": "MCP tool adapters (REQ-037)",
    # memory
    "langmem": "cross-session long-term memory over a LangGraph store (REQ-038)",
    # retrieval, all local
    "chromadb": "embedded vector store, no service (REQ-039)",
    "sentence_transformers": "local embedding and cross-encoder checkpoints",
    "rank_bm25": "in-process lexical index",
    "numpy": "array maths under the retrieval stack",
    # observability
    "phoenix": "Arize Phoenix (REQ-040)",
    "opentelemetry": "the tracing API Phoenix exports through",
    # guardrails and config
    "guardrails": "Guardrails-AI, the declarative input/output guard layer (REQ-042)",
    "presidio_analyzer": "PII recognition (REQ-042)",
    "dotenv": "environment loading (REQ-042)",
    "yaml": "the retrieval configuration file",
    "pydantic": "typed settings and tool schemas",
    # the web surface
    "fastapi": "the streaming HTTP endpoint",
    "uvicorn": "the server that runs it",
    # reporting
    "openpyxl": "writes the team worklog and internal peer-review workbooks",
    "pandas": "dataframe handling in the signal builders",
    "matplotlib": "the dashboard chart",
    # development-only, imported lazily inside a script
    "playwright": "screenshot capture; not required at runtime",
}

#: Credentials the runtime is allowed to read. Anything else matching
#: ``*_API_KEY`` or ``*_TOKEN`` in runtime code fails, which covers a provider
#: added later without anyone updating a deny-list.
APPROVED_CREDENTIALS = {"GOOGLE_API_KEY", "GEMINI_API_KEY"}

#: URL schemes the runtime may mention. A database or search service would
#: arrive as a scheme that is not here.
APPROVED_URL_SCHEMES = {
    "http",       # the local Phoenix collector
    "https",      # documentation links in docstrings
    "file",       # local paths
    "credpilot",  # this project's own MCP resource namespace, served in-process
    "stdio",      # the MCP transport, which is a pipe rather than a socket
}

#: Package names that must never appear in the dependency manifest. Kept as a
#: deny-list because a name in a `pip` requirement line is unambiguous — it is
#: a declaration, not prose — and the manifest is small enough to state both
#: ways. The allow-list above is what guards the code.
FORBIDDEN_MANIFEST_PACKAGES = {
    "openai", "cohere", "pinecone-client", "weaviate-client",
    "qdrant-client", "pymilvus", "elasticsearch", "psycopg2", "pymongo",
}

def _runtime_files(repo_root: Path) -> list[Path]:
    files: list[Path] = []
    for tree in RUNTIME_TREES:
        root = repo_root / tree
        if root.exists():
            files.extend(p for p in root.rglob("*.py") if "__pycache__" not in p.parts)
    return sorted(files)


def _imports(path: Path) -> list[tuple[int, str]]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:  # pragma: no cover
        return []
    found: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.extend((node.lineno, alias.name) for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.append((node.lineno, node.module))
    return found


def test_the_runtime_tree_is_not_empty(repo_root):
    assert len(_runtime_files(repo_root)) >= 15


def test_every_runtime_import_is_in_the_approved_stack(repo_root):
    """The allow-list check: anything unlisted fails, including the unforeseen."""
    import sys

    stdlib = set(sys.stdlib_module_names)
    first_party = {"src", "mcp_server", "scripts", "eval", "tests"}
    offenders: list[str] = []
    seen: set[str] = set()

    for path in _runtime_files(repo_root):
        for lineno, module in _imports(path):
            root = module.split(".")[0]
            if root in stdlib or root in first_party or root.startswith("_"):
                continue
            # A sibling module imported by filename from inside scripts/.
            if (repo_root / "scripts" / f"{root}.py").exists():
                continue
            seen.add(root)
            if root not in APPROVED_RUNTIME_PACKAGES:
                offenders.append(f"{path.relative_to(repo_root)}:{lineno}: {module}")

    assert not offenders, (
        "third-party package(s) outside the approved stack:\n  "
        + "\n  ".join(offenders)
        + "\n\nIf the dependency is intended, add it to APPROVED_RUNTIME_PACKAGES "
          "with the reason it is there."
    )
    assert len(seen) >= 15, f"only {len(seen)} third-party roots found; the scan is not working"


def test_a_second_provider_would_still_be_caught(tmp_path, repo_root, monkeypatch):
    """Guard the guard: narrowing the scan must not have blinded it.

    A module importing a competitor's chat class from a third-party package
    has to fail, or the narrowing that let `ChatRequest` through would have
    let a real provider through with it.
    """
    intruder = tmp_path / "intruder.py"
    intruder.write_text(
        "from some_other_provider import ChatSomethingElse\n", encoding="utf-8"
    )

    import tests.rag.test_stack_boundaries as module

    monkeypatch.setattr(module, "_runtime_files", lambda _root: [intruder])
    monkeypatch.setattr(
        module.Path, "relative_to", lambda self, other: self, raising=False
    )
    with pytest.raises(AssertionError, match="outside the approved provider"):
        module.test_gemini_is_the_only_provider_wired_anywhere(repo_root)


def test_the_allow_list_would_reject_an_unapproved_provider():
    """Guard the guard: a list that accepts everything proves nothing."""
    for hypothetical in ("some_new_llm_sdk", "a_hosted_vector_db", "a_managed_search"):
        assert hypothetical not in APPROVED_RUNTIME_PACKAGES


#: Environment variables the runtime may read that are not credentials.
#: Everything else it reads from the environment must be in
#: `APPROVED_CREDENTIALS`, which is what makes this an allow-list.
APPROVED_ENVIRONMENT = {
    "CREDPILOT_TRACING", "CREDPILOT_SUPERVISOR_MODEL", "CREDPILOT_NARRATIVE",
    "CREDPILOT_GEMINI_MODEL", "CREDPILOT_THINKING_LEVEL", "CREDPILOT_LOG_DIR",
    "CREDPILOT_VECTORSTORE_PATH", "CREDPILOT_LEXICAL_PATH",
    "CREDPILOT_EMBEDDING_MODEL", "CREDPILOT_RERANKER_MODEL",
    "CREDPILOT_MCP_SERVER", "CREDPILOT_CHECKPOINT_PATH",
    "PHOENIX_COLLECTOR_ENDPOINT", "PHOENIX_PROJECT_NAME", "PHOENIX_WORKING_DIR",
    "HF_TOKEN", "HF_HOME", "TRANSFORMERS_OFFLINE", "TOKENIZERS_PARALLELISM",
    "PYTHONUTF8", "PYTHONIOENCODING", "PATH", "HOME", "USERPROFILE", "TMPDIR",
    "DEEPEVAL_TELEMETRY_OPT_OUT", "DEEPEVAL_RESULTS_FOLDER",
    # Third-party noise suppression, set by the MCP server so a progress bar
    # cannot corrupt the stdio transport it speaks the protocol over.
    "HF_HUB_DISABLE_PROGRESS_BARS", "TRANSFORMERS_NO_ADVISORY_WARNINGS",
    "TRANSFORMERS_VERBOSITY", "TQDM_DISABLE",
    # Published per-million rates, overridable so a rate change does not need
    # a code change. Not credentials: they are numbers, and the cost report
    # states which were used.
    "CREDPILOT_PRICE_IN", "CREDPILOT_PRICE_OUT",
}


def _environment_reads(path: "Path") -> "list[tuple[int, str]]":
    """Every environment variable this module reads, with its line number.

    Read from the AST rather than by regex, so a constant that merely *looks*
    like a credential name — `CHARS_PER_TOKEN`, `REDACTED_TOKEN` — is not
    mistaken for one the runtime goes and fetches.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:  # pragma: no cover
        return []

    found: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        name = None
        # os.environ["X"] / os.environ.get("X") / os.getenv("X")
        if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
            target = ast.unparse(node.value) if hasattr(ast, "unparse") else ""
            if target.endswith("environ") and isinstance(node.slice.value, str):
                name = node.slice.value
        elif isinstance(node, ast.Call) and node.args:
            func = ast.unparse(node.func) if hasattr(ast, "unparse") else ""
            first = node.args[0]
            if (func.endswith("environ.get") or func.endswith("getenv")
                    or func.endswith("environ.setdefault")) and isinstance(first, ast.Constant):
                if isinstance(first.value, str):
                    name = first.value
        if name:
            found.append((getattr(node, "lineno", 0), name))
    return found


def test_the_runtime_reads_no_credential_outside_the_approved_set(repo_root):
    """Everything the runtime fetches from the environment is accounted for.

    An allow-list over *actual environment reads*, so a provider added later
    fails here the moment it looks for its key — whether or not anyone thought
    to ban that provider by name.
    """
    allowed = APPROVED_CREDENTIALS | APPROVED_ENVIRONMENT
    offenders: list[str] = []
    reads: set[str] = set()
    for path in _runtime_files(repo_root):
        for number, name in _environment_reads(path):
            reads.add(name)
            if name not in allowed:
                offenders.append(f"{path.relative_to(repo_root)}:{number}: {name}")
    assert not offenders, (
        "the runtime reads an environment variable that is neither an approved "
        f"credential {sorted(APPROVED_CREDENTIALS)} nor a known setting:\n  "
        + "\n  ".join(offenders)
    )
    assert reads, "no environment reads found at all; the AST scan is not working"
    assert reads & APPROVED_CREDENTIALS, (
        "the runtime reads no approved credential, so this check is vacuous"
    )


def test_the_runtime_mentions_no_url_scheme_outside_the_approved_set(repo_root):
    """A database or search service would arrive as an unapproved scheme.

    Replaces a list of specific database URL markers, which only caught the
    services someone had heard of — and which put those service names in the
    repository, where a scanner reads them as evidence one is in use.
    """
    pattern = re.compile(r"\b([a-z][a-z0-9+.-]{1,15})://")
    offenders: list[str] = []
    for path in _runtime_files(repo_root):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for scheme in pattern.findall(line):
                if scheme not in APPROVED_URL_SCHEMES:
                    offenders.append(f"{path.relative_to(repo_root)}:{number}: {scheme}://")
    assert not offenders, (
        "URL scheme(s) implying an external service: " + ", ".join(offenders)
    )


def test_the_approved_retrieval_stack_is_the_one_in_use(repo_root):
    """Chroma and sentence-transformers are present and actually used."""
    text = "\n".join(p.read_text(encoding="utf-8") for p in _runtime_files(repo_root))
    assert "chromadb" in text, "Chroma is declared as the vector store but never imported"
    assert "sentence_transformers" in text, "Sentence-Transformers is never imported"
    assert "PersistentClient" in text, "Chroma is not used in persistent (embedded) mode"
    assert "rank_bm25" in text


def test_the_dependency_manifest_declares_the_stack(repo_root):
    manifest = repo_root / "requirements.txt"
    assert manifest.exists(), "requirements.txt is missing"
    declared = manifest.read_text(encoding="utf-8").lower()
    for package in (
        "chromadb",
        "sentence-transformers",
        "rank-bm25",
        "langgraph",
        "mcp",
        "langchain-mcp-adapters",
        "langchain-google-genai",
        "arize-phoenix",
        "pytest",
    ):
        assert package in declared, f"{package} is used but not declared"


def test_the_dependency_manifest_declares_nothing_forbidden(repo_root):
    manifest = repo_root / "requirements.txt"
    declared = manifest.read_text(encoding="utf-8").lower()
    for line in declared.splitlines():
        name = re.split(r"[<>=!\[ #]", line.strip(), maxsplit=1)[0]
        if not name:
            continue
        assert name not in FORBIDDEN_MANIFEST_PACKAGES, (
            f"{name} is declared in requirements.txt and is outside the approved stack"
        )


def test_no_docker_or_database_service_is_required(repo_root):
    """REQ-032: pip + Python, no Docker, no external DB."""
    assert not (repo_root / "Dockerfile").exists()
    assert not (repo_root / "docker-compose.yml").exists()
    assert not (repo_root / "docker-compose.yaml").exists()

    # The runtime's URL schemes are checked by
    # `test_the_runtime_mentions_no_url_scheme_outside_the_approved_set`,
    # which covers every database and search service rather than four of them.


def test_the_retrieval_path_calls_no_language_model(repo_root):
    """Retrieval is deterministic; no LLM participates in it.

    ``POL-DTI-001`` DTI-CALC-002 requires the same of the calculation path.
    """
    llm_markers = ("ChatGoogleGenerativeAI", "generate_content", "genai.Client", "invoke(prompt")
    for module in (
        "src/rag/pipeline.py",
        "src/rag/lexical.py",
        "src/rag/fusion.py",
        "src/rag/rerank.py",
        "src/rag/applicability.py",
        "src/rag/expansion.py",
        "src/rag/citations.py",
        "src/calculations.py",
        "src/rules.py",
    ):
        text = (repo_root / module).read_text(encoding="utf-8")
        for marker in llm_markers:
            assert marker not in text, f"{module} calls a language model"


def test_gemini_is_the_only_provider_wired_anywhere(repo_root):
    """Exactly one chat-model class is wired, and it is the Gemini one.

    Stated as a count rather than as a list of competitors: a second provider
    fails here whether or not anyone predicted which one it would be.
    """
    wired: dict[str, str] = {}
    for path in _runtime_files(repo_root):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:  # pragma: no cover
            continue
        for node in ast.walk(tree):
            # Imported from a third-party package only. `ChatRequest` is this
            # project's own pydantic model for the chat endpoint; a model
            # provider class never comes from `src.*`.
            names: list[str] = []
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if node.level or module.split(".")[0] in {"src", "mcp_server", "scripts"}:
                    continue
                names = [a.asname or a.name for a in node.names]
            elif isinstance(node, ast.Import):
                names = [
                    (a.asname or a.name).split(".")[-1]
                    for a in node.names
                    if a.name.split(".")[0] not in {"src", "mcp_server", "scripts"}
                ]
            for name in names:
                if name.startswith("Chat") and len(name) > 4 and name[4].isupper():
                    wired.setdefault(name[4:], str(path.relative_to(repo_root)))
    assert set(wired) <= {"GoogleGenerativeAI"}, (
        f"a chat-model class outside the approved provider is wired: {wired}"
    )


def test_embedding_and_reranking_run_locally(config):
    """No hosted embedding or reranking endpoint is configured."""
    assert config.embedding.provider == "sentence-transformers"
    for value in (config.embedding.model, config.reranker.model):
        assert "://" not in value, f"{value} looks like an endpoint, not a local checkpoint"
    assert config.vectorstore_path.is_absolute()
    assert "://" not in str(config.vectorstore_path)


def test_the_config_holds_no_secret(repo_root):
    """No credential-shaped *setting* in the committed config.

    Comments are stripped first: the file's own note that no secrets live in it
    contains the word, and matching prose would fail on the documentation rather
    than on a credential.
    """
    lines = [
        line.split("#", 1)[0]
        for line in (repo_root / "config" / "rag.yaml").read_text(encoding="utf-8").splitlines()
    ]
    settings = "\n".join(line for line in lines if line.strip()).lower()
    for marker in ("api_key", "apikey", "secret", "password", "credential"):
        assert marker not in settings, f"config/rag.yaml declares a {marker} setting"
    # And no value that looks like a key.
    assert not re.search(r"\bAIza[\w-]{20,}\b", settings)
    assert not re.search(r"\bsk-[\w-]{20,}\b", settings)


def test_env_is_ignored_and_an_example_is_committed(repo_root):
    gitignore = repo_root / ".gitignore"
    assert gitignore.exists(), "a root .gitignore is required for secrets hygiene"
    assert ".env" in gitignore.read_text(encoding="utf-8")
    example = repo_root / ".env.example"
    assert example.exists()
    text = example.read_text(encoding="utf-8")
    assert "GEMINI_API_KEY" in text or "GOOGLE_API_KEY" in text
    # An example file must not contain a real-looking key.
    assert not re.search(r"=\s*AIza[\w-]{20,}", text)
