# Data-quality findings in the committed synthetic datasets

Found while building and evaluating the retrieval subsystem. Each is a defect in
the committed data rather than in retrieval, and each is handled explicitly —
worked around in code with the reason recorded, rather than silently absorbed
into a metric.

None of these were introduced by this work. None of the underlying data files
were modified: the datasets are generated from committed generators and fixing
them belongs with those generators, not with a consumer.

---

## F-1 — 36% of education golden citations are broken

**Severity: high** — it makes education golden-set scores read worse than
retrieval actually is.

`synthetic_data/education/golden_set/evaluation_cases.jsonl` contains 20 cases
with **59** `expected_policy_citations` between them. **21 are defective.**

### 9 citations name a rule that does not exist anywhere in the corpus

| Rule id cited | Cases | In the corpus? |
|---------------|-------|----------------|
| `EDU-CERT-001` | GOLD-06, GOLD-14, GOLD-19 | **no** |
| `EDU-REFI-001` | GOLD-12, GOLD-13, GOLD-14, GOLD-16 | **no** |
| `EDU-AGG-001` | GOLD-07 | **no** |
| `EDU-FRAUD-001` | GOLD-18 | **no** |

The twelve education policy documents declare 72 rules in their front matter, and
all 72 are present in their bodies and indexed. These four ids are in none of
them. They look like rules that were planned — certification, refinancing,
aggregate exposure, fraud — and whose content ended up inside other rules
(`EDU-SCH-005`, `EDU-UW-005`, `EDU-FRD-001`) under different ids.

**Effect.** No retriever can return a rule that was never written. Scoring
against these measures the corpus, not the retriever.

**Handling.** `eval/retrieval/dataset.py` drops them from ground truth and counts
them in `UNRESOLVABLE_EDUCATION_RULES`, so the exclusion is visible rather than
silent.

### 12 citations pair a real rule with the wrong policy document

| Citation as written | Where the rule actually lives |
|---------------------|-------------------------------|
| `POL-005 EDU-RG-001` | `POL-003` (Risk Grading and Pricing Matrix) |
| `POL-010 EDU-INTL-001` | `POL-012` (International Student Lending Policy) |

`POL-005` is the Income Verification and DTI policy; it has no `EDU-RG-*` rule.
`POL-010` is the Reg Z disclosure policy; it has no `EDU-INTL-*` rule.

**Handling.** The rule id is the reliable half of the pair, so ground truth
resolves the rule to its policy from the corpus front matter instead of trusting
the citation's policy component.

### Verifying

```bash
python - <<'PY'
import json, io, sys; sys.path.insert(0, '.')
from src.config import get_config
from src.rag.parsers import get_parser
from src.rag.parsers.base import parse_front_matter, coerce_str_list
from src.domain import read_text_tolerant

cfg = get_config()
rule_to_policy = {}
for path in get_parser('education').corpus_files(cfg.products['education'].corpus_root):
    fm, _, _ = parse_front_matter(read_text_tolerant(path), str(path))
    for rule in coerce_str_list(fm.get('rule_ids')):
        rule_to_policy[rule] = fm['policy_id']

for row in (json.loads(l) for l in io.open(
        'synthetic_data/education/golden_set/evaluation_cases.jsonl', encoding='utf-8')):
    for citation in row.get('expected_policy_citations', []):
        parts = citation.split()
        policy = next((p for p in parts if p.startswith('POL-')), None)
        rule = next((p for p in parts if p.startswith('EDU-')), None)
        if rule and rule not in rule_to_policy:
            print(f"{row['case_id']}: {citation}  -- rule not in corpus")
        elif rule and policy and rule_to_policy[rule] != policy:
            print(f"{row['case_id']}: {citation}  -- rule lives in {rule_to_policy[rule]}")
PY
```

**Suggested fix, upstream:** the education generator should build
`expected_policy_citations` from the rule ids it actually emitted, resolving the
policy from the same front matter the documents are written from.

---

## F-2 — five education application packets are not UTF-8

**Severity: medium** — a plain `json.load` raises on them.

| File | Failing byte |
|------|-------------|
| `APP-2026-00023.json` | `0x97` at offset 3949 |
| `APP-2026-00030.json` | `0x97` at offset 5335 |
| `APP-2026-00085.json` | `0x97` at offset 5467 |
| `APP-2026-00097.json` | `0x97` at offset 4967 |
| `APP-2026-00177.json` | `0x97` at offset 4971 |

`0x97` is an em dash in cp1252. The remaining 195 packets are clean UTF-8, so the
generator writes free-text fields with the platform default encoding on some
paths and UTF-8 on others.

```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0x97 in position 3949
```

**Handling.** `src.domain.read_text_tolerant` decodes UTF-8 first and falls back
to cp1252, then to lossy UTF-8. Every loader in the subsystem uses it, so the
five files load correctly rather than crashing a batch run partway through.

**Suggested fix, upstream:** the generator should pass `encoding="utf-8"`
explicitly on every write.

---

## F-3 — `index.json` sits among the application packets

**Severity: low.**

`synthetic_data/mortgage/applications/` holds 76 files: 75 applications and an
`index.json` manifest. A naive `glob("*.json")` picks up the manifest and tries to
route `index` as an application id.

**Handling.** Application loading globs `APP-*.json`. The manifest is a useful
artifact — it states plainly that the packets are model inputs only — so it is
not something to remove.

---

## F-4 — mortgage escrow inputs are not on the application packet

**Severity: medium** — not a defect, but it shapes the design.

A mortgage packet carries the loan amount, the rate and the purchase price. It
does **not** carry the property tax, the hazard premium, the association dues or
the mortgage insurance — all of which enter the qualifying housing expense and
therefore the DTI. Without them, `APP-000056`'s back-end DTI computes to 0.34
instead of the golden 0.44, and the DTI-CONV-001 breach never fires.

Those figures live in `synthetic_data/mortgage/structured/properties.csv` and
`loans.csv` — which is realistic: an underwriter reads them off the appraisal,
the insurance evidence and the rate sheet, not off the application form.

**Handling.** `src/application_context.py` assembles the underwriting input from
the packet plus those tables, and enforces an explicit allowlist:
`INPUT_TABLES` may be read; `OUTCOME_TABLES` — `underwriting_calculations`,
`eligibility_results`, `rule_evaluations`, `decisions`, `decision_reasons`,
`conditions`, `risk_flags`, `borrower_demographics` — raise `OutcomeAccessError`.
Reading the answer is not underwriting.

With the real inputs, `APP-000056` reproduces the golden figures exactly:
`housing_expense_pitia` 3902.92, `total_monthly_debt` 5540.33,
`back_end_dti` 0.4400, `front_end_dti` 0.3100, `ltv` 0.9200.

---

## F-5 — `dti_pct` is a fraction, not a percentage

**Severity: low.**

`income_verification[].dti_pct` in education packets holds `0.1618` for a DTI of
16.18%. The field name says percent; the value is a fraction. Treating it as a
percentage produces a DTI of 0.16%, which passes every ceiling trivially and
makes the capacity rule useless.

**Handling.** `src/calculations.py` reads it as a fraction and divides by 100 only
when the value exceeds 1, so it stays correct if the convention is ever fixed.

---

## What was *not* found

Worth recording, because these were checked:

* **The mortgage corpus is internally consistent.** All 42 documents declare
  rule ids in front matter that exactly match the `### RULE-ID` headings in their
  bodies — 203 rules, zero mismatches. The parser raises on a mismatch, so this
  is enforced on every build.
* **The education corpus is internally consistent.** All 12 documents' declared
  rule ids match their bold rule markers — 72 rules, zero mismatches.
* **Every mortgage golden citation resolves.** All `expected_citations` across
  the 75 mortgage golden cases name a real policy, version and rule.
* **No policy id is shared between the two corpora.**
* **No golden content appears in any policy document**, so nothing leaks into the
  index.
