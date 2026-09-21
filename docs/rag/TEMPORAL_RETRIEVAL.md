# Temporal retrieval — the version that governed, not the newest one

Retrieval has to return the policy that governed a file **on the day it was
underwritten**. Returning the newest published document instead is the kind of
bug that produces a confidently wrong decision with a real citation attached to
it, which is worse than no answer.

---

## 1. The case this is built around

The mortgage corpus was written with a boundary in it. `POL-DTI-001` exists at
two versions:

| Version | Effective | Back-end DTI ceiling |
|---------|-----------|----------------------|
| v1.0 | 2026-01-01 | **45%**, unconditionally |
| v2.0 | 2026-07-01 | **43%**, extending to 45% with ≥ 2 documented compensating factors (DTI-CONV-003) |

Three committed applications sit around that boundary. All three compute to
**exactly 44.00% back-end DTI**:

| Application | As-of | Governing version | Ceiling applied | Eligibility | Recommendation |
|-------------|-------|-------------------|-----------------|-------------|----------------|
| `APP-000055` | 2026-06-25 | **v1.0** | 45% | ELIGIBLE | APPROVE |
| `APP-000056` | 2026-07-08 | **v2.0** | 43% | **INELIGIBLE** | **DECLINE** → human review |
| `APP-000057` | 2026-07-08 | **v2.0** | 45% *(3 factors documented)* | ELIGIBLE | APPROVE |

Same ratio, three outcomes. The difference is entirely which version retrieval
returned and what the file documents. `APP-000056`'s breach cites
`POL-DTI-001 v2.0 rule DTI-CONV-001`, observed 0.4400 against threshold 0.4300;
`APP-000057`'s pass names each factor it relied on:

```
verified reserves of 61.1 months (>= 6.0)
representative credit score 744 (>= 720)
loan-to-value 72.00% (<= 75%)
```

Reproduce:

```bash
python -m src.cli assess synthetic_data/mortgage/applications/APP-000055.json
python -m src.cli assess synthetic_data/mortgage/applications/APP-000056.json
python -m src.cli assess synthetic_data/mortgage/applications/APP-000057.json
```

---

## 2. How the version is selected

Two mechanisms in [`src/rag/applicability.py`](../../src/rag/applicability.py),
applied in order, both **hard**:

### Effective window

A document is eligible when

```
effective_date <= as_of_date
AND (expiration_date is null OR as_of_date <= expiration_date)
```

Both bounds are inclusive: a policy effective 2026-07-01 governs *on*
2026-07-01. A document with no published expiry is open-ended — absence of an
expiry is not an expiry to invent.

### Latest eligible version per policy id

Where several versions of one policy id are eligible, the one with the newest
effective date on or before the as-of date governs. Everything older is marked
`SUPERSEDED` and removed before ranking. A single retrieval therefore **never
returns two versions of the same policy** — asserted over a 15-result retrieval
in [`test_temporal_retrieval.py`](../../tests/rag/test_temporal_retrieval.py).

Version ordering is numeric, not lexical: `10.0` sorts after `2.0`.

### Filtering happens before search, and again after

The allow-list is computed before BM25 and the dense query run, so ineligible
chunks never enter the candidate pool and never consume a slot. The survivors
are re-validated after reranking, so a chunk that reached the top by some other
path still cannot get through.

---

## 3. Every versioned mortgage policy, both sides

Six policies are published at two versions, all switching on 2026-07-01. Each is
tested at 2026-06-25 and 2026-07-08:

| Policy | What changed at v2.0 |
|--------|----------------------|
| `POL-DTI-001` | 45% unconditional → 43% with a compensating-factor extension |
| `POL-CRD-001` | flat minimum score → graduated by leverage, plus a new inquiries rule |
| `POL-AST-003` | flat reserve requirement → adjusted for leverage and affordability, plus a curable-shortfall rule |
| `POL-INC-004` | fixed variable-income history → shorter-history allowance with positive factors |
| `POL-JUMBO-001` | added a second-valuation threshold |
| `POL-VAL-001` | full appraisal mandatory → value acceptance available, plus a data-standard rule |

Measured: **12/12** correct (6 policies × 2 dates), `version_accuracy` 1.0000,
`wrong_version_rate` 0.0000.

---

## 4. What happens when nothing applies

An as-of date before any policy existed returns `NO_APPLICABLE_POLICY` with an
empty evidence list — not the oldest document, not the newest, and not a
fabricated answer:

```
2020-01-01, mortgage   -> NO_APPLICABLE_POLICY
2024-01-01, education  -> NO_APPLICABLE_POLICY
```

`POL-GEN-001` GEN-ELG-005 governs what the rule engine does next: missing
evidence yields INDETERMINATE, never a negative result. The file is referred, not
declined, and the absence of a retrieved ceiling is never read as "no ceiling" —
[`test_langgraph_rag_integration.py`](../../tests/rag/test_langgraph_rag_integration.py)
checks that by removing the retrieved rule and asserting the engine reports
INDETERMINATE rather than falling back to a hardcoded 43%.

---

## 5. Education: a documented limitation

The education corpus publishes **one version per policy document**, each with an
`effective_date` (2026-01-01 for `POL-001`..`POL-006`, 2025-01-15 for
`POL-007`..`POL-012`) and **no** `expiration_date`, `supersedes` or
`superseded_by`.

So:

* **Effective-date filtering is applied**, and works — a 2024 as-of date returns
  `NO_APPLICABLE_POLICY` rather than the newest document.
* **Version selection has nothing to select between.** There is no second version
  of any education policy to prefer or supersede.

No fake version history was added to make the two products look symmetrical. The
`PolicyChunk` model carries `policy_version`, `expiration_date`, `supersedes` and
`superseded_by` for education too — they are simply `None` where the corpus does
not publish them — so the day the education corpus gains a v2.0, the same
selection code applies with no change.

[`test_temporal_retrieval.py`](../../tests/rag/test_temporal_retrieval.py) pins
the limitation explicitly: `test_education_has_a_single_version_per_policy`
fails the moment a second version appears, which is the signal to revisit this
section rather than discover the gap in a decision.

---

## 6. What is *not* time-filtered

Product scope — `product_scope`, `purpose_scope`, `occupancy_scope` — is a
**soft** ranking boost in `[0, 1]`, not a filter. Scope metadata is incomplete
across the corpus, and an overlay that omits a scope list still governs;
hard-filtering on it would silently drop valid evidence. Only the product domain
and the effective-date window are hard.

---

## 7. Tests

| Test | What it proves |
|------|----------------|
| `test_effective_window_inclusion` | the boundary day is inclusive on both ends |
| `test_expiry_is_inclusive_and_open_ended_when_absent` | a missing expiry is open-ended |
| `test_version_selection_picks_the_latest_eligible` | the newest *eligible* version wins |
| `test_superseded_versions_are_classified_as_such` | older versions are marked, not silently dropped |
| `test_version_ordering_is_numeric_not_lexical` | `10.0` > `2.0` |
| `test_before_the_boundary_returns_v1` (×6) | every versioned policy resolves to v1.0 before |
| `test_after_the_boundary_returns_v2` (×6) | every versioned policy resolves to v2.0 after |
| `test_no_superseded_version_ever_appears` | one retrieval never mixes versions |
| `test_the_boundary_pair_retrieves_different_dti_ceilings` | 45% vs 43% text, correct citations |
| `test_a_date_before_any_policy_yields_no_applicable_policy` | no silent fallback |
| `test_education_effective_dates_are_honoured` | education filtering is real |
| `test_education_before_its_first_policy_returns_nothing` | and it refuses when nothing applies |
| `test_education_has_a_single_version_per_policy` | the limitation, pinned |
| `test_the_same_ratio_decides_three_ways` | the boundary triple, end to end through the graph |
| `test_temporal_selection_and_clarification_hold_over_mcp` | and across the MCP boundary |
