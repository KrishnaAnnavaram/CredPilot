# Where thresholds come from

Two acceptance criteria turn on a number:

> **AC-02** — *The copilot computes affordability (DTI / disposable income) from
> the application data and flags any policy breach **with the threshold it
> failed**.*

> **AC-03** — *…a decline or **high-value case** is routed for human review rather
> than auto-decided.*

**The requirements document states neither number.** It never gives a DTI
percentage and never gives a monetary boundary for "high-value" — a search of the
1,487-line hash-locked source finds no percentage at all.

This document records what CredPilot does instead, because the architecture is
the substantive answer to both criteria even though the validator cannot check a
number the source does not supply.

---

## The rule: thresholds are retrieved, never hard-coded

```
application data
      │
      ▼
retrieve the CURRENT applicable policy    ← effective-date aware, versioned
      │
      ▼
extract the threshold FROM THE CHUNK THAT WILL BE CITED
      │
      ▼
calculate the observed figure (DTI, disposable income)
      │
      ▼
compare observed against the retrieved threshold
      │
      ▼
report the breach, naming the threshold AND the rule it came from
```

No percentage and no dollar figure is written into the runtime. Both come from
the committed, versioned policy corpus at the application's effective date.

---

## Why not just hard-code 43% or 45%?

Three reasons, in order of how much they would cost:

1. **It would be fabricating a source value.** The requirements document does not
   state one. Writing `43` into the code and citing AC-02 for it would put a
   number in the repository that the specification never authorised.

2. **A cached threshold outlives the boundary that replaced it.** Lending policy
   is versioned and dated. `POL-DTI-001 v1.0` carries one ceiling and `v2.0`
   another; which applies depends on the application's effective date. A constant
   in code has no effective date and silently keeps applying after the rule that
   set it has been superseded.

3. **It breaks the audit trail.** The whole point of AC-02 is that a breach
   *names the threshold it failed*. A hard-coded number cannot cite anything. A
   retrieved one is reported alongside the rule id and version it came from, so a
   reviewer can go and read it.

---

## How it is implemented

### The threshold and its citation come from the same chunk

[`src/rules.py`](../src/rules.py):

```python
citation = dti_rule.get("citation", "")
# Read the thresholds from the chunk that will be cited, so the number and
# the citation can never come from different versions.
dti_params = parameters_of(dti_rule)
base     = dti_params.get("max_back_end_dti")
extended = dti_params.get("max_back_end_dti_with_factors")
```

The number and the citation are extracted from **one** retrieved object. They
cannot disagree, because there is no code path in which they come from different
places.

The breach then names what it failed:

```python
detail = f"ceiling {threshold:.2%} from {citation}"
```

### Absence is not permission

If the ceiling was not retrieved, the rule is **not** evaluated against a default:

```python
detail=(
    "the affordability ceiling was not retrieved; the rule cannot be "
    "applied and absence is not permission (GEN-ELG-005)"
)
```

The verdict becomes `INDETERMINATE` and the file routes to a human. A system that
falls back to a built-in number when retrieval fails is a system that quietly
decides against the wrong rule.

### High-value routing

[`src/review_triggers.py`](../src/review_triggers.py):

```python
if str(packet.get("product_family", "")).lower() == "jumbo":
    add("high_value_exposure", "a jumbo transaction is a mandatory human-review trigger")
```

`product_family` is a **classification carried in the policy corpus and the
application packet** — `conventional`, `jumbo`, `fha`, `va`, `usda`. The monetary
boundary that separates conforming from jumbo lives in the lending data, where it
can be versioned and dated, not as a constant in the routing code.

---

## What the validator can and cannot check

### AC-02 → `REQ-045` — 3 of 4 bound tests pass

| Test | Result | What it checks |
|---|---|---|
| `REQ-045-T01` | **PASS** | DTI / disposable-income computation exists in the implementation |
| `REQ-045-T02` | **PASS** | An affordability figure appears in observable CLI output |
| `REQ-045-T03` | **PASS** | The breach flag carries the threshold it failed |
| `REQ-045-T04` | **FAIL** | *The numeric DTI threshold the **source document** fixes* |

### AC-03 → `REQ-046` — 6 of 7 bound tests pass

| Test | Result | What it checks |
|---|---|---|
| `REQ-046-T01…T06` | **PASS** | approve / refer / decline vocabulary, written rationale, decline handling, high-value routing, human-review route |
| `REQ-046-T07` | **FAIL** | *The loan value above which a case is "high-value", **per the source document*** |

Both failing tests are registered through `not_verifiable_from_artifact(...)`,
which returns `Evidence(False, …)` and has no branch that can return `True`.

**The validator is not wrong.** It is reporting, accurately, that the
specification is silent. Turning either check green would claim the source
requirement had been verified when nothing verified it — so neither the checks
nor the thresholds were changed.

Recorded in
[`requirements_validation_tests/reports/unverifiable_requirements.md`](../requirements_validation_tests/reports/unverifiable_requirements.md),
which prints the regex searches proving the absence rather than asserting it.

---

## For a reviewer

The question worth asking is not *"what number did they use?"* but *"can the
system name the threshold it applied, and can I go and read the rule it came
from?"*

It can. Run:

```bash
python -m src.cli assess synthetic_data/mortgage/applications/APP-000056.json
```

and every affordability verdict reports its observed figure, the ceiling it was
judged against, and the versioned policy rule that ceiling came from.

The boundary triple `APP-000055` / `APP-000056` / `APP-000057` exercises the same
44% ratio passing, breaching, and passing-with-factors depending on the
application date and what the file documents — which is only possible because the
threshold is retrieved rather than fixed.
