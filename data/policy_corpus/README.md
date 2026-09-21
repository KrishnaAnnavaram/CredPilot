# `data/policy_corpus/` — lending-policy corpus registry

This directory is the **registry** for the lending-policy corpora that the
CredPilot agentic-RAG tool retrieves from. The policy documents themselves
are committed under `synthetic_data/<product>/policy_corpus/` and are
deliberately not duplicated here — one copy of each policy means one
content hash, and the provenance chain from a citation back to a committed
source file cannot drift.

`corpus_registry.json` is written by `scripts/build_policy_indexes.py` on
every index build and records, for every source document: product domain,
policy id and version, effective window, declared rule ids, SHA-256 and its
canonical path.

| Product | Canonical corpus root | Documents | Declared rules | Chroma collection |
|---------|----------------------|-----------|----------------|-------------------|
| EDUCATION_LOAN | `synthetic_data/education/policy_corpus` | 12 | 72 | `credpilot_education_policies` |
| MORTGAGE | `synthetic_data/mortgage/policy_corpus` | 42 | 203 | `credpilot_mortgage_policies` |

**Total:** 54 policy documents, 275 declared rules.

Rebuild with:

```bash
python scripts/build_policy_indexes.py
```
