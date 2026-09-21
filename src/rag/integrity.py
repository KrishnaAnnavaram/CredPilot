"""Index integrity validation.

The build is only trustworthy if it can prove three things, from the artifacts
themselves rather than from the build log:

1. **Nothing was skipped.** Every policy document in each corpus is represented
   in that product's collection, and every rule the front matter declares has a
   chunk.
2. **Nothing crossed over.** No education policy sits in the mortgage collection
   and no mortgage policy sits in the education collection — measured as
   ``cross_product_contamination_rate``, which must be 0.00.
3. **Nothing is stale.** The SHA-256 of every source file still matches the hash
   recorded in the index, so an edited policy cannot leave old embeddings in
   place unnoticed.

Every check runs against the live Chroma collections and the live corpus.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.config import REPO_ROOT, RagConfig, get_config
from src.domain import LendingProductDomain
from src.rag.citations import CitationResolver
from src.rag.lexical import BM25Index
from src.rag.models import sha256_file
from src.rag.parsers import get_parser
from src.rag.parsers.base import coerce_str_list, parse_front_matter
from src.domain import read_text_tolerant
from src.rag.vectorstore import PolicyVectorStore

def rel_to_repo(path: Path) -> str:
    """Repo-relative, forward-slashed — the same form chunk metadata records."""
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:  # pragma: no cover - only if a corpus moves outside the repo
        return path.as_posix()


@dataclass
class Check:
    name: str
    passed: bool
    detail: str
    measured: Any = None
    expected: Any = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "check": self.name,
            "status": "PASS" if self.passed else "FAIL",
            "detail": self.detail,
            "measured": self.measured,
            "expected": self.expected,
        }


@dataclass
class IntegrityReport:
    checks: list[Check] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks)

    @property
    def failures(self) -> list[Check]:
        return [c for c in self.checks if not c.passed]

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": "PASS" if self.passed else "FAIL",
            "check_count": len(self.checks),
            "failed_count": len(self.failures),
            "metrics": self.metrics,
            "checks": [c.as_dict() for c in self.checks],
        }

    def write(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return path


def _declared_rules(path: Path) -> set[str]:
    text = read_text_tolerant(path)
    fm, _, _ = parse_front_matter(text, str(path))
    return set(coerce_str_list(fm.get("rule_ids")))


def validate_product(config: RagConfig, product_key: str) -> tuple[list[Check], dict[str, Any]]:
    """Validate one product's index against its corpus."""
    product = config.products[product_key]
    domain = product.domain
    label = domain.value
    checks: list[Check] = []

    parser = get_parser(product.parser)
    source_files = parser.corpus_files(product.corpus_root)
    source_count = len(source_files)

    store = PolicyVectorStore(config, domain)
    records = store.get_all()
    metadatas = [r["metadata"] for r in records]

    indexed_sources = {m.get("source_path") for m in metadatas if m.get("source_path")}
    indexed_source_count = len(indexed_sources)

    # 1. every source document is represented
    expected_sources = {rel_to_repo(p) for p in source_files}
    missing_sources = sorted(expected_sources - indexed_sources)
    checks.append(
        Check(
            f"{label}: every source document is indexed",
            passed=not missing_sources and indexed_source_count == source_count,
            detail=(
                f"{indexed_source_count}/{source_count} documents indexed"
                + (f"; missing {missing_sources[:5]}" if missing_sources else "")
            ),
            measured=indexed_source_count,
            expected=source_count,
        )
    )

    # 2. every declared rule has a chunk
    declared: set[str] = set()
    for path in source_files:
        declared |= _declared_rules(path)
    indexed_rules = {m.get("rule_id") for m in metadatas if m.get("rule_id")}
    missing_rules = sorted(declared - indexed_rules)
    checks.append(
        Check(
            f"{label}: every declared rule is indexed",
            passed=not missing_rules,
            detail=(
                f"{len(indexed_rules)}/{len(declared)} declared rules indexed"
                + (f"; missing {missing_rules[:5]}" if missing_rules else "")
            ),
            measured=len(indexed_rules),
            expected=len(declared),
        )
    )

    # 3. no foreign product in this collection
    foreign = [
        m.get("chunk_id")
        for m in metadatas
        if m.get("product_domain") != domain.value
        or not str(m.get("chunk_id", "")).startswith(domain.chunk_prefix + "__")
    ]
    contamination_rate = len(foreign) / len(metadatas) if metadatas else 0.0
    checks.append(
        Check(
            f"{label}: collection contains only {label} policy",
            passed=not foreign,
            detail=(
                f"cross_product_contamination_rate={contamination_rate:.4f}"
                + (f"; foreign chunks {foreign[:5]}" if foreign else "")
            ),
            measured=round(contamination_rate, 6),
            expected=0.0,
        )
    )

    # 4. every source path lies under this product's corpus root, and none under another's
    own_prefix = rel_to_repo(product.corpus_root) + "/"
    other_prefixes = [
        rel_to_repo(p.corpus_root) + "/" for k, p in config.products.items() if k != product_key
    ]
    foreign_paths = sorted(
        {
            str(m.get("source_path", ""))
            for m in metadatas
            if not str(m.get("source_path", "")).startswith(own_prefix)
            or any(str(m.get("source_path", "")).startswith(op) for op in other_prefixes)
        }
    )
    checks.append(
        Check(
            f"{label}: every source path lies under {own_prefix}",
            passed=not foreign_paths,
            detail=(
                f"{len(foreign_paths)} foreign source path(s): {foreign_paths[:5]}"
                if foreign_paths
                else f"all {len(indexed_sources)} source paths are under {own_prefix}"
            ),
            measured=len(foreign_paths),
            expected=0,
        )
    )

    # 5. source hashes still match the committed files
    recorded: dict[str, set[str]] = {}
    for meta in metadatas:
        sp, sha = meta.get("source_path"), meta.get("source_sha256")
        if sp and sha:
            recorded.setdefault(sp, set()).add(sha)
    stale: list[str] = []
    for path in source_files:
        rel = rel_to_repo(path)
        if rel not in recorded:
            continue
        if recorded[rel] != {sha256_file(str(path))}:
            stale.append(rel)
    checks.append(
        Check(
            f"{label}: indexed content hashes match the committed corpus",
            passed=not stale,
            detail=(f"{len(stale)} stale document(s): {stale[:5]}" if stale else "all hashes match"),
            measured=len(stale),
            expected=0,
        )
    )

    # 6. lexical index agrees with the vector collection
    lexical_path = BM25Index.path_for(config, domain)
    if lexical_path.exists():
        lexical = BM25Index.load(lexical_path)
        aligned = set(lexical.chunk_ids) == {r["chunk_id"] for r in records}
        checks.append(
            Check(
                f"{label}: lexical and vector indexes cover the same chunks",
                passed=aligned,
                detail=f"bm25={len(lexical.chunk_ids)} chroma={len(records)}",
                measured=len(lexical.chunk_ids),
                expected=len(records),
            )
        )
    else:
        checks.append(
            Check(
                f"{label}: lexical index exists",
                passed=False,
                detail=f"missing {lexical_path}",
                measured=0,
                expected=1,
            )
        )

    # 7. every chunk's citation resolves to a committed artifact
    resolver = CitationResolver(config)
    unresolved = [
        m.get("citation")
        for m in metadatas
        if not resolver.citation_exists(str(m.get("citation", "")))
    ]
    validity = 1.0 - (len(unresolved) / len(metadatas)) if metadatas else 0.0
    checks.append(
        Check(
            f"{label}: every indexed citation resolves",
            passed=not unresolved,
            detail=(
                f"citation_validity={validity:.4f}"
                + (f"; unresolved {unresolved[:5]}" if unresolved else "")
            ),
            measured=round(validity, 6),
            expected=1.0,
        )
    )

    metrics = {
        "source_document_count": source_count,
        "indexed_source_count": indexed_source_count,
        "chunk_count": len(records),
        "declared_rule_count": len(declared),
        "indexed_rule_count": len(indexed_rules),
        "cross_product_contamination_rate": round(contamination_rate, 6),
        "citation_validity": round(validity, 6),
        "stale_documents": len(stale),
    }
    return checks, metrics


def cross_product_checks(config: RagConfig) -> list[Check]:
    """Checks that only make sense across both collections at once."""
    checks: list[Check] = []
    by_domain: dict[LendingProductDomain, set[str]] = {}
    for key, product in config.products.items():
        store = PolicyVectorStore(config, product.domain)
        by_domain[product.domain] = {
            str(r["metadata"].get("policy_id")) for r in store.get_all()
        }

    mortgage_ids = by_domain.get(LendingProductDomain.MORTGAGE, set())
    education_ids = by_domain.get(LendingProductDomain.EDUCATION_LOAN, set())
    overlap = sorted(mortgage_ids & education_ids)
    checks.append(
        Check(
            "cross-product: no policy id appears in both collections",
            passed=not overlap,
            detail=f"{len(overlap)} shared policy id(s): {overlap[:5]}",
            measured=len(overlap),
            expected=0,
        )
    )

    collections = [p.collection for p in config.products.values()]
    checks.append(
        Check(
            "cross-product: each product has its own collection",
            passed=len(set(collections)) == len(collections),
            detail=f"collections={collections}",
            measured=len(set(collections)),
            expected=len(collections),
        )
    )
    return checks


def validate_indexes(config: RagConfig | None = None) -> IntegrityReport:
    """Run every integrity check across every product."""
    config = config or get_config()
    report = IntegrityReport()
    per_product: dict[str, Any] = {}
    for key in config.products:
        checks, metrics = validate_product(config, key)
        report.checks.extend(checks)
        per_product[key] = metrics
    report.checks.extend(cross_product_checks(config))

    total_chunks = sum(m["chunk_count"] for m in per_product.values()) or 1
    report.metrics = {
        "products": per_product,
        "cross_product_contamination_rate": round(
            sum(
                m["cross_product_contamination_rate"] * m["chunk_count"]
                for m in per_product.values()
            )
            / total_chunks,
            6,
        ),
        "citation_validity": round(
            sum(m["citation_validity"] * m["chunk_count"] for m in per_product.values())
            / total_chunks,
            6,
        ),
    }
    return report
