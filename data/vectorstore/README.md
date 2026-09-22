# `data/vectorstore/`

Build products of `python scripts/build_policy_indexes.py`.

| Path | Committed | What |
|------|-----------|------|
| `index_manifest.json` | yes | embedding model and revision, dimension, distance metric, per-product chunk counts, and every source document's SHA-256 and chunk ids |
| `index_integrity.json` | yes | all 16 integrity checks with pass/fail and detail, including `cross_product_contamination_rate` and `citation_validity` |
| `lexical/bm25_mortgage.json and lexical/bm25_education.json` | yes | the BM25 indexes — readable JSON, one record per chunk |
| `credpilot/` | **no** | the Chroma binary store (~8 MB), regenerated deterministically in ~30 s |

The Chroma directory is a build product. The committed artifacts are the evidence
*about* it: a reviewer can check that every policy document was indexed, that no
source has drifted from its recorded hash, and that neither collection contains
the other product's policy — all without running anything.

Rebuild:

```bash
python scripts/build_policy_indexes.py
```

The build exits non-zero if any integrity check fails.
