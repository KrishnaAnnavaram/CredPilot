"""The ``data/policy_corpus/`` registry.

The required-artifacts checklist names ``data/policy_corpus/`` as the agentic-RAG
tool's corpus location. CredPilot's policy documents are committed at
``synthetic_data/<product>/policy_corpus/``, one folder per lending product,
because the two corpora use incompatible identifier taxonomies and each ships
with its own generator, schemas and golden set.

Copying those documents into ``data/policy_corpus/`` would leave two copies of
every lending policy in the repository and two content hashes to keep in step —
exactly the drift the source-hash provenance chain exists to prevent. So
``data/policy_corpus/`` holds the **registry** instead: the machine-generated
inventory of every source document the indexes were built from, with its
product, policy id, version, effective window, rule ids, SHA-256 and canonical
path. It is written by committed code during every index build, and the
integrity validator checks it against the corpus.

See ``docs/rag/REQUIREMENTS_MAPPING.md`` for this deviation and its rationale.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

from src.config import REPO_ROOT, RagConfig, get_config
from src.domain import read_text_tolerant
from src.rag.models import sha256_file
from src.rag.parsers import get_parser
from src.rag.parsers.base import coerce_date, coerce_str_list, coerce_version, parse_front_matter

if TYPE_CHECKING:  # pragma: no cover
    from src.rag.indexer import BuildReport

REGISTRY_DIR = REPO_ROOT / "data" / "policy_corpus"
REGISTRY_PATH = REGISTRY_DIR / "corpus_registry.json"
REGISTRY_SCHEMA_VERSION = 1


def _iso(value: Any) -> str | None:
    d = coerce_date(value)
    return d.isoformat() if isinstance(d, date) else None


def scan_corpus(config: RagConfig | None = None) -> dict[str, Any]:
    """Scan both corpora and return the registry payload.

    Reads the committed documents directly, so the registry is a statement about
    the corpus rather than about whatever happens to be in the index.
    """
    config = config or get_config()
    products: dict[str, Any] = {}

    for key, product in sorted(config.products.items()):
        parser = get_parser(product.parser)
        documents = []
        for path in parser.corpus_files(product.corpus_root):
            text = read_text_tolerant(path)
            fm, _, _ = parse_front_matter(text, str(path))
            documents.append(
                {
                    "policy_id": str(fm.get("policy_id", "")),
                    "policy_version": coerce_version(fm.get("version")),
                    "policy_title": str(fm.get("title", "")),
                    "effective_date": _iso(fm.get("effective_date")),
                    "expiration_date": _iso(fm.get("expiration_date")),
                    "supersedes": fm.get("supersedes"),
                    "superseded_by": fm.get("superseded_by"),
                    "source_category": fm.get("source_category") or fm.get("classification"),
                    "product_scope": coerce_str_list(
                        fm.get("product_scope") or fm.get("products")
                    ),
                    "rule_ids": coerce_str_list(fm.get("rule_ids")),
                    "source_path": path.resolve().relative_to(REPO_ROOT).as_posix(),
                    "source_sha256": sha256_file(str(path)),
                    "bytes": path.stat().st_size,
                }
            )

        products[key] = {
            "product_domain": product.domain.value,
            "canonical_corpus_root": product.corpus_root.resolve()
            .relative_to(REPO_ROOT)
            .as_posix(),
            "collection": product.collection,
            "document_count": len(documents),
            "declared_rule_count": sum(len(d["rule_ids"]) for d in documents),
            "documents": documents,
        }

    return {
        "schema_version": REGISTRY_SCHEMA_VERSION,
        "description": (
            "Machine-generated inventory of the lending-policy corpora CredPilot's "
            "vector and lexical indexes are built from. The policy documents "
            "themselves are committed under synthetic_data/<product>/policy_corpus/ "
            "and are not duplicated here."
        ),
        "generated_by": "scripts/build_policy_indexes.py",
        "total_document_count": sum(p["document_count"] for p in products.values()),
        "total_declared_rule_count": sum(p["declared_rule_count"] for p in products.values()),
        "products": products,
    }


def write_registry(
    config: RagConfig | None = None, build_report: "BuildReport | None" = None
) -> Path:
    """Write ``data/policy_corpus/corpus_registry.json`` and its README."""
    config = config or get_config()
    payload = scan_corpus(config)

    if build_report is not None:
        payload["index_build"] = {
            "embedding_model": build_report.embedding.get("model"),
            "embedding_dimension": build_report.embedding.get("dimension"),
            "built_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "products": {
                key: {
                    "collection": rep.collection,
                    "source_document_count": rep.source_document_count,
                    "chunk_count": rep.chunk_count,
                }
                for key, rep in sorted(build_report.products.items())
            },
        }

    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    _write_readme(payload)
    return REGISTRY_PATH


def _write_readme(payload: dict[str, Any]) -> None:
    lines = [
        "# `data/policy_corpus/` — lending-policy corpus registry",
        "",
        "This directory is the **registry** for the lending-policy corpora that the",
        "CredPilot agentic-RAG tool retrieves from. The policy documents themselves",
        "are committed under `synthetic_data/<product>/policy_corpus/` and are",
        "deliberately not duplicated here — one copy of each policy means one",
        "content hash, and the provenance chain from a citation back to a committed",
        "source file cannot drift.",
        "",
        "`corpus_registry.json` is written by `scripts/build_policy_indexes.py` on",
        "every index build and records, for every source document: product domain,",
        "policy id and version, effective window, declared rule ids, SHA-256 and its",
        "canonical path.",
        "",
        "| Product | Canonical corpus root | Documents | Declared rules | Chroma collection |",
        "|---------|----------------------|-----------|----------------|-------------------|",
    ]
    for key, product in sorted(payload["products"].items()):
        lines.append(
            f"| {product['product_domain']} | `{product['canonical_corpus_root']}` | "
            f"{product['document_count']} | {product['declared_rule_count']} | "
            f"`{product['collection']}` |"
        )
    lines += [
        "",
        f"**Total:** {payload['total_document_count']} policy documents, "
        f"{payload['total_declared_rule_count']} declared rules.",
        "",
        "Rebuild with:",
        "",
        "```bash",
        "python scripts/build_policy_indexes.py",
        "```",
        "",
    ]
    (REGISTRY_DIR / "README.md").write_text("\n".join(lines), encoding="utf-8")


def load_registry() -> dict[str, Any]:
    if not REGISTRY_PATH.exists():
        raise FileNotFoundError(
            f"no corpus registry at {REGISTRY_PATH}; run "
            "'python scripts/build_policy_indexes.py'"
        )
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
