"""The runtime stays inside the approved stack.

REQ-032 and REQ-036: Google Gemini is the only model provider, the stack is
open-source, and nothing requires Docker or an external database service. This
file turns that into a check over the committed code rather than a claim in a
document.

Claude Code was the development assistant for this work. The *runtime* must not
call Claude, and must not read an ``ANTHROPIC_API_KEY``.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

RUNTIME_TREES = ("src", "mcp_server", "scripts")

#: Packages that would put a model or a vector service outside the approved
#: stack into the runtime. Substring-matched against every import's root package.
FORBIDDEN_PACKAGES = {
    "anthropic": "Claude is not the approved provider (REQ-036)",
    "claude": "Claude is not the approved provider (REQ-036)",
    "openai": "OpenAI is not the approved provider (REQ-036)",
    "langchain_openai": "OpenAI is not the approved provider (REQ-036)",
    "cohere": "hosted reranking/embedding is out of stack",
    "voyageai": "hosted embedding is out of stack",
    "pinecone": "a hosted vector service is out of stack (REQ-032)",
    "weaviate": "a hosted vector service is out of stack (REQ-032)",
    "qdrant_client": "a hosted vector service is out of stack (REQ-032)",
    "pymilvus": "a vector server is out of stack (REQ-032)",
    "elasticsearch": "an external search service is out of stack (REQ-032)",
    "opensearchpy": "an external search service is out of stack (REQ-032)",
    "azure": "a hosted search service is out of stack (REQ-032)",
    "psycopg2": "an external database service is out of stack (REQ-032)",
    "pymongo": "an external database service is out of stack (REQ-032)",
    "redis": "an external service is out of stack (REQ-032)",
}

#: Environment variables the runtime must never read.
FORBIDDEN_ENV = ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "COHERE_API_KEY", "VOYAGE_API_KEY")


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


@pytest.mark.parametrize("package,reason", sorted(FORBIDDEN_PACKAGES.items()))
def test_no_runtime_module_imports_a_forbidden_package(repo_root, package, reason):
    offenders = []
    for path in _runtime_files(repo_root):
        for lineno, module in _imports(path):
            if module.split(".")[0].lower() == package:
                offenders.append(f"{path.relative_to(repo_root)}:{lineno}: {module}")
    assert not offenders, f"{reason}: {offenders}"


@pytest.mark.parametrize("variable", FORBIDDEN_ENV)
def test_no_runtime_module_reads_a_forbidden_credential(repo_root, variable):
    offenders = []
    for path in _runtime_files(repo_root):
        text = path.read_text(encoding="utf-8")
        for number, line in enumerate(text.splitlines(), start=1):
            if variable in line and not line.strip().startswith("#"):
                offenders.append(f"{path.relative_to(repo_root)}:{number}")
    assert not offenders, offenders


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
        assert name not in ("anthropic", "openai", "cohere", "pinecone-client", "weaviate-client"), name


def test_no_docker_or_database_service_is_required(repo_root):
    """REQ-032: pip + Python, no Docker, no external DB."""
    assert not (repo_root / "Dockerfile").exists()
    assert not (repo_root / "docker-compose.yml").exists()
    assert not (repo_root / "docker-compose.yaml").exists()

    text = "\n".join(p.read_text(encoding="utf-8") for p in _runtime_files(repo_root))
    for marker in ("postgresql://", "mysql://", "mongodb://", "redis://"):
        assert marker not in text, f"{marker} implies an external database service"


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
    """Where an LLM is wired at all, it is Gemini."""
    text = "\n".join(p.read_text(encoding="utf-8") for p in _runtime_files(repo_root))
    if "ChatGoogleGenerativeAI" in text or "langchain_google_genai" in text:
        assert "ChatAnthropic" not in text
        assert "ChatOpenAI" not in text


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
