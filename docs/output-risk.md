# CredPilot — Output Risk Classification

Not every sentence the system produces carries the same consequence. A retrieved policy excerpt that is wrong wastes an underwriter's minute; a decline recommendation that is wrong denies someone credit and starts an adverse-action clock.

This document sorts what CredPilot emits into three tiers, states what gates each tier, and shows a worked sample of each.

**Audience:** credit risk, compliance and the engineers who maintain the gating.

---

## The tiers at a glance

| Tier | What it covers | Who may see it unreviewed | Gate |
|---|---|---|---|
| **Low** | Retrieved policy text, citations, computed figures, retrieval diagnostics, answers to general questions about what CredPilot is | Underwriter or applicant, directly | Citation must resolve; figures carry their formula version |
| **Medium** | Eligibility status, risk level, approve and refer recommendations, the written rationale, answers to policy questions | Underwriter, as a recommendation to act on | Rule-engine verdict + deterministic narrative check + evidence sufficiency + response validation |
| **High** | Decline recommendations, adverse-action reason codes, anything on a file where applicant text attempted instruction, anything on a request that asked for an override or disputed a decision | **Nobody** — human review is mandatory before the output leaves the system | Hard routing to `human_review`; no auto-issue path exists |

The tier is a property of the **output**, not of the applicant or the file. The same application can produce Low-tier retrieval and a High-tier recommendation in one run.

### Two outputs the conversational surface added

**A general answer** — "hello", "what can you do" — is Tier 1, and is the only
output in the system produced with neither retrieval nor a model. It comes from
a fixed capability statement in `src/supervisor.py`. It cannot cite a policy
because it never reads one, and it cannot be wrong about lending because it says
nothing about a file.

**A policy answer** — "what is the maximum back-end DTI on a jumbo mortgage?" —
is Tier 2, and is gated more tightly than the assessment rationale rather than
less. There is no application, no computed figure and no decided outcome, so the
retrieved policy text is the *only* ground truth and the model has correspondingly
more room to go wrong. Three gates:

* the answer is generated only from retrieved evidence, and the prompt forbids
  stating a number that is not in it;
* the same deterministic check runs afterwards — every citation and every figure
  in the prose must trace to the evidence it was given;
* a failed check **replaces the prose with the quoted rules**. Verbose to read,
  and incapable of being wrong about what the policy says.

A policy answer also refuses to decide anything about a particular file. That is
not a matter of prompt discipline alone: there is no application on the state, so
the rule engine never runs and there is no outcome for the answer to leak.

**An escalation** — an override request, a dispute, a detected injection — is
Tier 3 and produces no retrieval, no figures and no citations at all. The output
is a statement that a person has it.

---

## Tier 1 — Low risk

### What it covers

- Policy text returned by retrieval, with its citation, version and effective date
- Computed figures: DTI, LTV, reserves, residual income, funds to close
- Retrieval diagnostics: which rules were retrieved, fusion ranks, applicability status
- Memory recall of prior-session context (documents outstanding, stated preferences)

### Why it is low

None of it is a conclusion. It is material an underwriter reads and judges. The worst realistic failure is irrelevance — a retrieved rule that does not bear on the file — which costs attention, not a wrong outcome.

### Gate

1. **Every citation must resolve** to a real rule in the indexed corpus at the file's as-of date. `citation_resolves` is carried on every piece of evidence and aggregated to `all_citations_resolve`.
2. **Every figure carries its formula version** (`POL-DTI-001` DTI-CALC-002), so a reader can tell which definition produced it.
3. **Product isolation holds** — evidence comes from the file's own product collection, structurally, with no combined collection to leak from.

### Sample

```
POL-DTI-001 v2.0 rule DTI-CONV-001  (effective 2026-01-01, applicable)
  "Back-end debt-to-income must not exceed 43%. The ceiling extends to 45%
   where at least two compensating factors from DTI-CONV-003 are documented
   and named in the file."

Computed (formula DTI-CALC-002):
  qualifying_monthly_income      8,858.33
  total_monthly_obligations      3,897.67
  back_end_dti                      0.4400
```

An underwriter who disagrees with any line here can open the cited rule and check. That is the whole safety property of this tier.

---

## Tier 2 — Medium risk

### What it covers

- `ELIGIBLE` / `INELIGIBLE` / `INDETERMINATE` eligibility status
- Risk level and risk flags
- `APPROVE_RECOMMENDATION` and `REFER_RECOMMENDATION`
- The written rationale — the only model-generated prose in the system

### Why it is medium

These are conclusions, and an underwriter may reasonably act on them. But none of them closes a file adversely: an approve recommendation still passes through a human credit decision, and a refer explicitly asks for one. The reversible direction.

### Gate

1. **The verdict comes from the rule engine**, not a model. Thresholds come from retrieved policy; figures from `src.calculations`; the comparison is deterministic code.
2. **Missing evidence never becomes a negative result.** Absent evidence returns `INDETERMINATE`, which routes to referral (`GEN-ELG-005`). This was not free — failure F-8 had the engine reading "0 of 2 compensating factors documented" from evidence it had simply failed to retrieve, and declining a file it should have referred.
3. **The rationale is checked against its own evidence after generation.** `src.narrative.verify_narrative` extracts every citation and every figure from the prose and confirms each appears in the evidence supplied. A rationale that fails is **kept, marked `rationale_is_faithful: false`, and escalated to Tier 3.** It is not dropped — that would hide the failure — and not shipped unmarked, which would be worse.
4. **The model cannot reach the outcome.** It receives the decision as a fact in its prompt. There is no code path by which its text changes `recommendation["outcome"]`.
5. **The assembled response is validated before it is published.** The Final Response Agent re-checks, on the exact prose it is about to publish rather than on some earlier draft: every cited rule resolves, every figure is one the calculators produced, and the prose does not read as an approval under a decline (or the reverse). A failure substitutes the deterministic summary, is recorded in `validation.failures`, and escalates the output to Tier 3.
6. **The output guardrail is the last thing that runs.** It scans for PII and redacts in place, and it *adds* the human-review notice when the flag is set and the text does not already carry one — rather than trusting the writer above it to have remembered.

### Sample

```
Recommendation : APPROVE_RECOMMENDATION
Eligibility    : ELIGIBLE      Risk: LOW
Citations      : POL-DTI-001 v2.0 rule DTI-CONV-001
                 POL-DTI-001 v2.0 rule DTI-CONV-003
Rationale faithful: true   (0 unsupported citations, 0 unsupported figures)

"...Because the computed back_end_dti of 0.44 exceeds the baseline threshold
 of 43 percent, the transaction requires the compensating-factor extension
 under POL-DTI-001 v2.0 rule DTI-CONV-001..."
```

Note what the rationale does *not* do: it does not conclude, soften, or recompute. It narrates a decision already made and names the rule that made it.

---

## Tier 3 — High risk

### What it covers

- `DECLINE_RECOMMENDATION` — any of them, without exception
- Adverse-action reason codes and disclosure content
- Any output on a file where applicant-supplied text attempted to alter policy, thresholds or data access
- Any output from a run that **halted** on its step budget without reaching a decision
- Any rationale that failed the deterministic faithfulness check

### Why it is high

This is the irreversible direction. A wrong decline denies credit, starts a regulatory clock, and is the outcome an applicant is least able to challenge — precisely because it arrives with citations attached and looks authoritative.

### Gate

**Human review is mandatory and there is no path around it.**

| Trigger | Where it is enforced |
|---|---|
| Eligibility `INELIGIBLE` → decline | `{product}_recommendation`: sets `requires_human_review = True` unconditionally, citing `POL-DEC-001` DEC-REC-002 |
| Eligibility `INDETERMINATE` | `{product}_eligibility` and `{product}_recommendation`: outcome becomes `REFER_RECOMMENDATION` |
| Risk level `HIGH` | `{product}_recommendation` |
| Injection attempt in applicant text | `input_guardrails_node` sets the flag; `{product}_risk` raises the level to HIGH and adds `APPLICANT_TEXT_INSTRUCTION_ATTEMPT`. The file is **still assessed** — refusing to underwrite it would let a hostile attachment stop an applicant's file from being read |
| Injection attempt in the **request itself** | `supervisor_node` routes to `HUMAN_REVIEW` before any specialist runs, so the attack reaches no corpus, no rule engine and no model |
| An override, dispute or complaint | `supervisor_node`: a request that asks for a decision to be changed is a person's to own (`POL-UWR-001` UWR-HRV-001) |
| The product cannot be resolved after two clarification rounds | `supervisor_node` + `MAX_CLARIFICATION_ROUNDS` |
| An application routed to the wrong specialist | `{product}_agent` refuses rather than assessing it against the other product's policy |
| No policy evidence retrieved | `{product}_policy_retrieval` routes straight to `human_review` |
| Unfaithful rationale | `narrative_node` |
| The assembled response fails validation | `final_response_node` |
| Step budget exhausted | `_guard()` in every node — halts with a reason a human can read, rather than raising |

No graph edge carries a decline to `END`. Every terminal path for one runs
through `human_review`, and `output_guardrails` adds the review notice to the
published text if the writer above it did not.

### Sample

```
Recommendation : DECLINE_RECOMMENDATION
Eligibility    : INELIGIBLE     Risk: ELEVATED
Requires human review: TRUE
Reasons:
  - a decline recommendation is always routed to a human (DEC-REC-002)
  - breach of back_end_dti: observed 0.4812 against 0.4500
    [POL-DTI-001 v2.0 rule DTI-CONV-001]

Route: recommendation -> narrative -> human_review
```

The rationale is still written for this file — a reviewer picking up a decline needs the reasoning more than an auto-approval does, which is why the narrative node sits *before* the handoff rather than being skipped when a human is going to look anyway.

---

## What is deliberately not gated

**Retrieval breadth.** The system retrieves more than it uses and lets the reranker and the dedupe budgets narrow it. Gating retrieval on relevance would reintroduce the F-1 failure, where overview chunks starved rule chunks out of the final slate.

**The rationale's style.** It is checked for *provenance* — did every citation and figure come from the evidence — and not for tone, length or persuasiveness. A dull accurate rationale passes; a fluent one with an invented threshold does not.

**Model availability.** An outage degrades the narrative to a deterministic summary rather than blocking the file. A recommendation without prose is still a recommendation.

---

## Known gap

The system cannot express `APPROVE_WITH_CONDITIONS`. Six golden cases expect it; `recommendation_node` emits approve, refer or decline and nothing else. Today those files land in Tier 2 as a refer, which is the safe direction but not the right answer. Adding the outcome would require a conditions vocabulary the rule engine does not yet have, and it is named in `reports/eval_report.json` as `cases_with_inexpressible_expectation` rather than absorbed into the accuracy figure.
