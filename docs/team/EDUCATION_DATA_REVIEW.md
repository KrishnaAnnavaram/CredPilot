# Education synthetic-data review record

| | |
|---|---|
| **Contributor / developer** | **Mahesh Rajendra** |
| **Internal reviewer** | **Krishna Annavaram** |
| Product line | Education loan — the second of CredPilot's two products |
| Data classification | **Synthetic only.** No real applicant, lender or account data. |

The two roles are deliberately separate: the person who generated the data is not
the person who reviewed it.

---

## Repository evidence

`REPOSITORY-VERIFIED`

```bash
git show f28a1fd --stat
```

| | |
|---|---|
| Commit | `f28a1fd6b4dcef675f318305045e94b71a8e1be7` |
| Author | Mahesh Rajendra `<rajendramahesh25@gmail.com>` |
| Authored | 2026-09-21 00:04:38 −0400 |
| Subject | *feat: add synthetic education loan origination dataset* |
| Size | **260 files, 39,470 insertions** |
| Branch | `syn-data-edu` |
| Merged by | Krishna Annavaram — pull request #2, merge commit `f5126c7` |

The commit message records the scope in the author's own words:

> Introduce a seeded generator, 200 applications, policy corpus, applicant
> document artifacts, and a 20-case golden evaluation set for origination copilot
> work. All records are fictional.

It also carries `Co-authored-by: Cursor <cursoragent@cursor.com>`. An assistant
was used during development; this project discloses that rather than hiding it.

The data was later relocated from `synthetic_data_education_loans/` to
`synthetic_data/education/` when both products were unified under one
product-partitioned root (`362355d`, Krishna Annavaram). The content is Mahesh's;
the move was a refactor.

---

## What was generated

`REPOSITORY-VERIFIED` — counts taken from the working tree.

| Artifact | Path | Count |
|---|---|---|
| Applications | `synthetic_data/education/applications/` | **200** |
| Policy corpus | `synthetic_data/education/policy_corpus/` | 12 documents |
| Golden evaluation set | `synthetic_data/education/golden_set/` | 22 files |
| Applicant document artifacts | `synthetic_data/education/applicant_documents/` | 18 |
| Applicant profiles | `synthetic_data/education/profiles/` | 2 |
| Scenario catalogue | `synthetic_data/education/scenarios/` | 1 |
| JSON schema | `synthetic_data/education/schemas/` | 1 |

### Generators

| Script | Purpose |
|---|---|
| [`generate_synthetic_data.py`](../../synthetic_data/education/generator/generate_synthetic_data.py) | Builds the applications. *"Deterministic, seeded, re-runnable."* |
| [`validate_synthetic_data.py`](../../synthetic_data/education/generator/validate_synthetic_data.py) | *"Asserts every internal-consistency rule and exits non-zero on violation."* |

### Reproducibility

`REPOSITORY-VERIFIED`

```python
# synthetic_data/education/generator/generate_synthetic_data.py:22
SEED = 20260901
random.seed(SEED)
```

The seed is fixed and written into each record's provenance block
(`generator_seed=SEED`, line 700), so a reader can tell which run produced a given
file. Re-running the generator reproduces the dataset.

### Consistency checking

`validate_synthetic_data.py` is a standalone checker that exits non-zero on any
violation — a generator that can produce an internally inconsistent record without
complaining is a generator whose output cannot be trusted as a fixture.

```bash
python synthetic_data/education/generator/validate_synthetic_data.py
```

---

## How the data is exercised downstream

`REPOSITORY-VERIFIED` — this dataset is not inert; the test suite depends on it.

| Concern | Test |
|---|---|
| Education policy chunking | [`tests/rag/test_chunking.py`](../../tests/rag/test_chunking.py) |
| Citations resolve to education documents | [`tests/rag/test_citations.py`](../../tests/rag/test_citations.py) |
| Golden set does not leak into the index | [`tests/rag/test_no_golden_leakage.py`](../../tests/rag/test_no_golden_leakage.py) |
| Education path through the graph | [`tests/rag/test_langgraph_rag_integration.py`](../../tests/rag/test_langgraph_rag_integration.py) |
| Education tools over MCP | [`tests/rag/test_mcp_rag_integration.py`](../../tests/rag/test_mcp_rag_integration.py) |
| Cross-product contamination | [`tests/rag/test_stack_boundaries.py`](../../tests/rag/test_stack_boundaries.py), retrieval evaluation |

The retrieval evaluation reports education metrics separately from mortgage in
[`eval/results/retrieval_eval.json`](../../eval/results/retrieval_eval.json) under
`per_product.EDUCATION_LOAN`, and cross-product contamination is measured at
**0.0000** — an education query never returns a mortgage rule, or the reverse.

---

## Synthetic-only confirmation

`REPOSITORY-VERIFIED`

* The commit message states *"All records are fictional."*
* [`tests/rag/test_pii_logging.py`](../../tests/rag/test_pii_logging.py) scans every
  committed data and documentation file under `logs/`, `traces/`, `reports/` and
  `eval/results/` for identifier- and account-shaped strings.
* A scan of the committed artifacts with the project's own
  `find_sensitive()` returns **zero** findings.
* No real lender, applicant, account or credit-bureau data is present.

---

## Known data-quality findings

Findings across both datasets are recorded in
[`docs/rag/DATA_QUALITY_FINDINGS.md`](../rag/DATA_QUALITY_FINDINGS.md). They are
kept as findings rather than quietly patched, so a reader can see what the
fixtures do and do not support.

One limitation is worth naming here because it bounds what the education product
can demonstrate: **the education corpus has no policy versions to select
between**, so the effective-date retrieval behaviour that the mortgage corpus
exercises has no education counterpart. This is recorded as deviation **D2** in
[`docs/rag/REQUIREMENTS_MAPPING.md`](../rag/REQUIREMENTS_MAPPING.md).

---

## Review

`TEAM-ATTESTED` — Krishna Annavaram reviewed and integrated this work. The merge
of pull request #2 (`f5126c7`) is the recorded integration action; the substance
of the review — reading the generator, the schema and a sample of records — is
attested rather than captured in Git.

### Reviewer confirmation

Reviewer: **Krishna Annavaram**

```
Confirmation: __________________________
Date:         __________________________
```

### Contributor acknowledgment

Contributor: **Mahesh Rajendra**

```
Confirmation: __________________________
Date:         __________________________
```

**Status: PENDING — unsigned.** Neither block is filled in on anyone's behalf.
