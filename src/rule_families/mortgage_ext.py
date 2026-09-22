"""Mortgage rule families the core engine did not evaluate.

Eight families, chosen by how many golden cases turn on them:
``DOC-REQ`` (4), ``EMP-CNT`` (4), ``AST-SRC`` (3), ``CRD-EVT`` (3),
``GEN-ELG`` (3), ``JMB-ELG`` (2), ``VAL-APR`` (2), ``CRD-DLQ`` (2).

The mortgage corpus publishes its numbers as backticked parameter tables, so
every threshold here comes from :func:`src.rules.parameters_of` applied to the
exact chunk that will be cited. That matters more than it looks: reading a
threshold from one version of a policy and citing another is the silent
wrong-answer this whole subsystem exists to prevent, and taking both from the
same chunk makes it impossible rather than merely unlikely.

Three families carry a severity that is not PASS/FAIL, and the distinction is
load-bearing:

* ``EMP-CNT-001`` states *"refer, not fail"* for a short history — a 22-month
  history with strong continuity can still support the income, and declining it
  would be wrong;
* ``DOC-REQ-004`` states that an incomplete file is **suspended**, never
  declined — the difference matters to the borrower, who can supply a document
  but cannot un-decline a file;
* ``CRD-EVT`` seasoning is a hard fail, because a seasoning period is a date
  arithmetic question with no judgement in it.

Where a rule says refer, this returns INDETERMINATE, which
:func:`src.rules.summarize` turns into a referral rather than a breach.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Mapping, Sequence

from src.rules import RuleEvaluation, Verdict, find_rule, parameters_of


def _as_date(value: Any) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(str(value).replace(",", "").replace("$", ""))
    except (TypeError, ValueError):
        return None


def _missing(rule_id: str, measure: str, observed: float | None = None) -> RuleEvaluation:
    """The only correct answer when the governing rule was not retrieved."""
    return RuleEvaluation(
        rule_id=rule_id,
        citation="",
        measure=measure,
        verdict=Verdict.INDETERMINATE,
        observed=observed,
        detail=(
            f"{rule_id} was not retrieved; absence of the rule is not permission "
            f"(POL-GEN-001 GEN-ELG-005)"
        ),
    )


def _note_date(packet: Mapping[str, Any]) -> date | None:
    """The date freshness is measured to (``DOC-REQ-002``: the note date)."""
    return _as_date(
        packet.get("underwriting_as_of_date") or packet.get("application_date")
    )


# ======================================================================================
# DOC-REQ — the document set and its freshness
# ======================================================================================

#: DOC-REQ-001's baseline set, as document types the packet uses. The rule names
#: the categories in prose; this maps each to the ``document_type`` values the
#: corpus actually files them under.
_BASELINE_DOCUMENTS: dict[str, tuple[str, ...]] = {
    "application": ("loan_application_summary",),
    "identity": ("identity_verification_summary",),
    "credit report": ("credit_report_summary",),
    "income evidence": ("paystub", "w2", "tax_return", "employment_verification",
                        "profit_and_loss", "income_verification"),
    "asset evidence": ("bank_statement", "asset_verification"),
    "valuation": ("appraisal_report", "valuation_report", "value_acceptance"),
}

_PURCHASE_ADDITIONAL = {"executed purchase contract": ("purchase_agreement",)}
_REFINANCE_ADDITIONAL = {"payoff statement": ("payoff_statement",)}

#: Which freshness parameter governs which document type. The window values come
#: out of DOC-REQ-002; only the mapping lives here.
_FRESHNESS_PARAMETER: dict[str, str] = {
    "paystub": "paystub_days",
    "bank_statement": "asset_statement_days",
    "asset_verification": "asset_statement_days",
    "employment_verification": "employment_verification_days",
    "tax_return": "tax_return_days",
}


def evaluate_documentation(
    calculations: Mapping[str, Any],
    packet: Mapping[str, Any],
    evidence: Sequence[Mapping[str, Any]],
) -> list[RuleEvaluation]:
    """Completeness and freshness of the document set."""
    out: list[RuleEvaluation] = []
    documents = list(packet.get("supplied_documents") or [])
    present = {str(d.get("document_type", "")).lower() for d in documents}
    purpose = str(packet.get("loan_purpose", "")).lower()

    # -- DOC-REQ-001: is the baseline set present? -----------------------------
    baseline_rule = find_rule(evidence, "DOC-REQ-001")
    if baseline_rule is None:
        out.append(_missing("DOC-REQ-001", "document_completeness"))
    else:
        required = dict(_BASELINE_DOCUMENTS)
        if purpose == "purchase":
            required.update(_PURCHASE_ADDITIONAL)
        elif "refinance" in purpose:
            required.update(_REFINANCE_ADDITIONAL)

        missing = [
            category
            for category, types in required.items()
            if not present & set(types)
        ]
        completeness = (len(required) - len(missing)) / len(required)
        # DOC-REQ-004: an incomplete file is suspended, not declined. That is
        # INDETERMINATE here — summarize() refers it, and a referral is a file
        # a borrower can still complete.
        out.append(
            RuleEvaluation(
                rule_id="DOC-REQ-001",
                citation=str(baseline_rule.get("citation") or ""),
                measure="document_completeness", unit="fraction_of_required",
                verdict=Verdict.PASS if not missing else Verdict.INDETERMINATE,
                observed=round(completeness, 4),
                threshold=1.0,
                comparator=">=",
                detail=(
                    f"all {len(required)} required document categories are on file"
                    if not missing
                    else (
                        f"missing: {', '.join(sorted(missing))}. DOC-REQ-004 makes an "
                        f"incomplete file SUSPENDED_INCOMPLETE, never a decline — the "
                        f"difference matters to the borrower, who can supply a "
                        f"document but cannot un-decline a file"
                    )
                ),
                factors=sorted(missing),
            )
        )

    # -- DOC-REQ-002: is what is on file current? ------------------------------
    freshness_rule = find_rule(evidence, "DOC-REQ-002")
    if freshness_rule is None:
        out.append(_missing("DOC-REQ-002", "document_freshness"))
        return out

    windows = parameters_of(freshness_rule)
    note_date = _note_date(packet)
    if note_date is None:
        out.append(
            RuleEvaluation(
                rule_id="DOC-REQ-002",
                citation=str(freshness_rule.get("citation") or ""),
                measure="document_freshness", unit="days",
                verdict=Verdict.INDETERMINATE,
                detail="no note date on the file to measure freshness against",
            )
        )
        return out

    stale: list[str] = []
    oldest_excess = 0.0
    for document in documents:
        kind = str(document.get("document_type", "")).lower()
        parameter = _FRESHNESS_PARAMETER.get(kind)
        if parameter is None:
            continue
        limit = _float(windows.get(parameter))
        document_date = _as_date(document.get("document_date"))
        if limit is None or document_date is None:
            continue
        age = (note_date - document_date).days
        if age > limit:
            stale.append(f"{kind} is {age} days old against a {limit:.0f}-day window")
            oldest_excess = max(oldest_excess, age - limit)

    out.append(
        RuleEvaluation(
            rule_id="DOC-REQ-002",
            citation=str(freshness_rule.get("citation") or ""),
            measure="document_freshness", unit="days",
            verdict=Verdict.PASS if not stale else Verdict.INDETERMINATE,
            observed=oldest_excess if stale else 0.0,
            threshold=0.0,
            comparator="<=",
            detail=(
                "every dated document is within its freshness window, measured to "
                "the note date"
                if not stale
                else (
                    "; ".join(stale)
                    + ". DOC-REQ-002 raises a refresh condition rather than treating "
                    "a stale document as a missing one"
                )
            ),
            factors=stale,
        )
    )
    return out


# ======================================================================================
# EMP-CNT — employment continuity
# ======================================================================================


def evaluate_employment_continuity(
    calculations: Mapping[str, Any],
    packet: Mapping[str, Any],
    evidence: Sequence[Mapping[str, Any]],
) -> list[RuleEvaluation]:
    """Two-year history, and employment that has not started yet."""
    out: list[RuleEvaluation] = []
    rule = find_rule(evidence, "EMP-CNT-001")
    as_of = _note_date(packet)
    history = _employment_history_months(packet, as_of)

    if rule is None:
        out.append(_missing("EMP-CNT-001", "employment_history_months", history))
    elif as_of is None or history is None:
        out.append(
            RuleEvaluation(
                rule_id="EMP-CNT-001",
                citation=str(rule.get("citation") or ""),
                measure="employment_history_months", unit="months",
                verdict=Verdict.INDETERMINATE,
                detail="no dated employment history on the file",
            )
        )
    else:
        params = parameters_of(rule)
        required = _float(params.get("required_history_months"))
        if required is None:
            out.append(
                RuleEvaluation(
                    rule_id="EMP-CNT-001",
                    citation=str(rule.get("citation") or ""),
                    measure="employment_history_months", unit="months",
                    verdict=Verdict.INDETERMINATE,
                    observed=history,
                    detail="EMP-CNT-001 was retrieved but publishes no required history",
                )
            )
        else:
            # "shortfall_treatment: refer, not fail". A short history with
            # strong continuity can still support the income, so this is
            # INDETERMINATE — which summarize() refers — and never a breach.
            out.append(
                RuleEvaluation(
                    rule_id="EMP-CNT-001",
                    citation=str(rule.get("citation") or ""),
                    measure="employment_history_months", unit="months",
                    verdict=Verdict.PASS if history >= required else Verdict.INDETERMINATE,
                    observed=history,
                    threshold=required,
                    comparator=">=",
                    detail=(
                        f"{history:.0f} months of combined employment history against "
                        f"the {required:.0f} required"
                        + (
                            ""
                            if history >= required
                            else "; EMP-CNT-001 states this refers the file rather than "
                                 "failing it"
                        )
                    ),
                )
            )

    # -- EMP-CNT-004: a job that has not started yet ---------------------------
    future_rule = find_rule(evidence, "EMP-CNT-004")
    pending = _pending_employment(packet, as_of)
    if future_rule is not None and pending is not None:
        params = parameters_of(future_rule)
        limit = _float(params.get("max_days_to_start"))
        if limit is None:
            out.append(
                RuleEvaluation(
                    rule_id="EMP-CNT-004",
                    citation=str(future_rule.get("citation") or ""),
                    measure="days_to_employment_start", unit="days",
                    verdict=Verdict.INDETERMINATE,
                    observed=pending,
                    detail="EMP-CNT-004 was retrieved but publishes no start-date window",
                )
            )
        else:
            out.append(
                RuleEvaluation(
                    rule_id="EMP-CNT-004",
                    citation=str(future_rule.get("citation") or ""),
                    measure="days_to_employment_start", unit="days",
                    verdict=Verdict.PASS if pending <= limit else Verdict.FAIL,
                    observed=pending,
                    threshold=limit,
                    comparator="<=",
                    detail=(
                        f"employment starts in {pending:.0f} days against a "
                        f"{limit:.0f}-day maximum; the offer must also be "
                        f"non-contingent and reserves must cover the gap"
                    ),
                )
            )
    return out


def _employment_history_months(
    packet: Mapping[str, Any], as_of: date | None
) -> float | None:
    """Combined months across every employment record, counted once per month.

    Overlapping records are a real shape in this corpus — a borrower who started
    a second job before leaving the first — and summing the spans would credit
    the overlap twice, turning 14 months of history into 26. Months are counted
    into a set instead.
    """
    if as_of is None:
        return None
    records = packet.get("employment") or []
    if not records:
        return None

    months: set[tuple[int, int]] = set()
    for record in records:
        start = _as_date(record.get("declared_start_date") or record.get("start_date"))
        if start is None:
            continue
        end = _as_date(record.get("end_date")) or (
            as_of if record.get("is_current") else as_of
        )
        if end < start:
            continue
        year, month = start.year, start.month
        while (year, month) <= (end.year, end.month):
            months.add((year, month))
            month += 1
            if month > 12:
                year, month = year + 1, 1
    return float(len(months)) if months else None


def _pending_employment(packet: Mapping[str, Any], as_of: date | None) -> float | None:
    """Days until a current job starts, when it has not started yet."""
    if as_of is None:
        return None
    for record in packet.get("employment") or []:
        if not record.get("is_current"):
            continue
        start = _as_date(record.get("declared_start_date") or record.get("start_date"))
        if start is not None and start > as_of:
            return float((start - as_of).days)
    return None


# ======================================================================================
# AST-SRC — source of funds
# ======================================================================================


def evaluate_asset_source(
    calculations: Mapping[str, Any],
    packet: Mapping[str, Any],
    evidence: Sequence[Mapping[str, Any]],
) -> list[RuleEvaluation]:
    """Large deposits must be sourced before their funds count."""
    rule = find_rule(evidence, "AST-SRC-002")
    transactions = list(packet.get("asset_transactions") or [])
    if rule is None:
        return [_missing("AST-SRC-002", "unsourced_large_deposits")]

    params = parameters_of(rule)
    share = _float(params.get("threshold_pct_of_qualifying_monthly_income"))
    income = _float((calculations.get("amounts") or {}).get("qualifying_monthly_income"))
    if share is None:
        return [
            RuleEvaluation(
                rule_id="AST-SRC-002",
                citation=str(rule.get("citation") or ""),
                measure="unsourced_large_deposits", unit="currency",
                verdict=Verdict.INDETERMINATE,
                detail="AST-SRC-002 was retrieved but publishes no deposit threshold",
            )
        ]
    if income is None or income <= 0:
        return [
            RuleEvaluation(
                rule_id="AST-SRC-002",
                citation=str(rule.get("citation") or ""),
                measure="unsourced_large_deposits", unit="currency",
                verdict=Verdict.INDETERMINATE,
                detail=(
                    "the deposit threshold is a share of qualifying monthly income, "
                    "which could not be computed"
                ),
            )
        ]

    threshold = income * share
    unsourced: list[str] = []
    total_unsourced = 0.0
    for transaction in transactions:
        if str(transaction.get("transaction_type", "")).lower() != "deposit":
            continue
        amount = _float(transaction.get("amount"))
        if amount is None or amount <= threshold:
            continue
        status = str(transaction.get("source_status", "")).upper()
        if status in ("SOURCED", "PAYROLL", "RECURRING"):
            continue
        total_unsourced += amount
        unsourced.append(
            f"${amount:,.0f} on {transaction.get('transaction_date')} "
            f"({status or 'no source status'})"
        )

    # "excluded and then the consequences are reported" — the rule is explicit
    # that an unsourced deposit is not counted and then flagged. Whether the
    # exclusion breaks funds-to-close or reserves is AST-FTC's and AST-RSV's
    # question; this reports the exclusion and refers.
    return [
        RuleEvaluation(
            rule_id="AST-SRC-002",
            citation=str(rule.get("citation") or ""),
            measure="unsourced_large_deposits", unit="currency",
            verdict=Verdict.PASS if not unsourced else Verdict.INDETERMINATE,
            observed=round(total_unsourced, 2),
            threshold=round(threshold, 2),
            comparator="<=",
            detail=(
                f"no deposit exceeds {share:.0%} of qualifying monthly income "
                f"(${threshold:,.0f}) without a documented source"
                if not unsourced
                else (
                    f"unsourced deposits above the ${threshold:,.0f} threshold: "
                    + "; ".join(unsourced)
                    + ". AST-SRC-002 excludes them from eligible assets and re-runs "
                    "funds-to-close and reserves without them"
                )
            ),
            factors=unsourced,
        )
    ]


# ======================================================================================
# CRD-EVT — credit event seasoning
# ======================================================================================

#: Event types as the corpus records them, mapped to the seasoning parameter
#: CRD-EVT-001 publishes for each. Only the mapping lives here; the months come
#: from the retrieved rule.
_SEASONING_PARAMETER: dict[str, str] = {
    "chapter_7_bankruptcy": "chapter_7_bankruptcy_months",
    "chapter_13_bankruptcy": "chapter_13_bankruptcy_discharged_months",
    "chapter_13_bankruptcy_discharged": "chapter_13_bankruptcy_discharged_months",
    "foreclosure": "foreclosure_months",
    "deed_in_lieu": "deed_in_lieu_months",
    "short_sale": "short_sale_months",
    "mortgage_charge_off": "mortgage_charge_off_months",
}


def evaluate_credit_events(
    calculations: Mapping[str, Any],
    packet: Mapping[str, Any],
    evidence: Sequence[Mapping[str, Any]],
) -> list[RuleEvaluation]:
    """Seasoning since a bankruptcy, foreclosure or short sale."""
    events = list(packet.get("credit_events") or [])
    rule = find_rule(evidence, "CRD-EVT-001")

    if not events:
        return [
            RuleEvaluation(
                rule_id="CRD-EVT-001",
                citation=str(rule.get("citation") or "") if rule else "",
                measure="credit_event_seasoning",
                verdict=Verdict.NOT_APPLICABLE,
                detail="no significant credit event on the file",
            )
        ]
    if rule is None:
        return [_missing("CRD-EVT-001", "credit_event_seasoning")]

    params = parameters_of(rule)
    as_of = _note_date(packet)
    out: list[RuleEvaluation] = []

    for event in events:
        kind = str(event.get("event_type", "")).lower()
        parameter = _SEASONING_PARAMETER.get(kind)
        required = _float(params.get(parameter)) if parameter else None
        # The extract records seasoning_months directly; the anchor date is the
        # authority and the recorded figure is the fallback when it is absent.
        anchor = _as_date(event.get("anchor_date"))
        elapsed = _float(event.get("seasoning_months"))
        if anchor is not None and as_of is not None:
            elapsed = (as_of.year - anchor.year) * 12 + (as_of.month - anchor.month)
            elapsed = float(max(elapsed, 0))

        if required is None:
            out.append(
                RuleEvaluation(
                    rule_id="CRD-EVT-001",
                    citation=str(rule.get("citation") or ""),
                    measure=f"seasoning_{kind}", unit="months",
                    verdict=Verdict.INDETERMINATE,
                    observed=elapsed,
                    detail=(
                        f"CRD-EVT-001 publishes no seasoning period for an event of "
                        f"type {kind!r}"
                    ),
                )
            )
            continue
        if elapsed is None:
            out.append(
                RuleEvaluation(
                    rule_id="CRD-EVT-001",
                    citation=str(rule.get("citation") or ""),
                    measure=f"seasoning_{kind}", unit="months",
                    verdict=Verdict.INDETERMINATE,
                    threshold=required,
                    detail=f"no anchor date recorded for the {kind} event",
                )
            )
            continue

        out.append(
            RuleEvaluation(
                rule_id="CRD-EVT-001",
                citation=str(rule.get("citation") or ""),
                measure=f"seasoning_{kind}", unit="months",
                verdict=Verdict.PASS if elapsed >= required else Verdict.FAIL,
                observed=elapsed,
                threshold=required,
                comparator=">=",
                detail=(
                    f"{elapsed:.0f} months since the {kind.replace('_', ' ')} "
                    f"anchor of {event.get('anchor_date')} against the "
                    f"{required:.0f} required"
                    + (
                        ""
                        if elapsed >= required
                        else "; CRD-EVT-002 permits 36 months with documented "
                             "extenuating circumstances and independent evidence, "
                             "which is a human's finding to make"
                    )
                ),
            )
        )
    return out


# ======================================================================================
# CRD-DLQ — delinquency
# ======================================================================================


def evaluate_delinquency(
    calculations: Mapping[str, Any],
    packet: Mapping[str, Any],
    evidence: Sequence[Mapping[str, Any]],
) -> list[RuleEvaluation]:
    """Housing and non-housing delinquency, weighed separately.

    ``CRD-DLQ-001`` weighs housing history on its own because a missed mortgage
    payment predicts a missed mortgage payment in a way a missed card payment
    does not. So a 60-day housing late fails where three 30-day non-housing
    lates only refer.
    """
    accounts = list(packet.get("credit_accounts") or [])
    housing_rule = find_rule(evidence, "CRD-DLQ-001")
    other_rule = find_rule(evidence, "CRD-DLQ-002")
    out: list[RuleEvaluation] = []

    if not accounts:
        return [
            RuleEvaluation(
                rule_id="CRD-DLQ-001",
                citation=str(housing_rule.get("citation") or "") if housing_rule else "",
                measure="delinquency",
                verdict=Verdict.INDETERMINATE,
                detail="no tradeline detail on the file to read a payment history from",
            )
        ]

    housing = [a for a in accounts if _is_housing(a)]
    other = [a for a in accounts if not _is_housing(a)]

    # -- CRD-DLQ-001: housing --------------------------------------------------
    if housing_rule is None:
        out.append(_missing("CRD-DLQ-001", "housing_delinquency"))
    else:
        params = parameters_of(housing_rule)
        refer_at = _float(params.get("housing_30d_refer_at"))
        fail_at = _float(params.get("housing_60d_fail_at"))
        lates_30 = sum(int(_float(a.get("lates_30d_24m")) or 0) for a in housing)
        lates_60 = sum(
            int(_float(a.get("lates_60d_24m")) or 0) + int(_float(a.get("lates_90d_24m")) or 0)
            for a in housing
        )
        if fail_at is not None and lates_60 >= fail_at:
            verdict, detail = Verdict.FAIL, (
                f"{lates_60} housing late(s) of 60 days or more in the lookback; "
                f"CRD-DLQ-001 fails at {fail_at:.0f}"
            )
        elif refer_at is not None and lates_30 >= refer_at:
            verdict, detail = Verdict.INDETERMINATE, (
                f"{lates_30} housing late(s) of 30 days in the lookback; "
                f"CRD-DLQ-001 refers at {refer_at:.0f} rather than failing"
            )
        elif refer_at is None and fail_at is None:
            verdict, detail = Verdict.INDETERMINATE, (
                "CRD-DLQ-001 was retrieved but publishes no delinquency counts"
            )
        else:
            verdict, detail = Verdict.PASS, (
                f"no housing delinquency in the lookback across "
                f"{len(housing)} housing tradeline(s)"
            )
        out.append(
            RuleEvaluation(
                rule_id="CRD-DLQ-001",
                citation=str(housing_rule.get("citation") or ""),
                measure="housing_delinquency", unit="count",
                verdict=verdict,
                observed=float(lates_60 or lates_30),
                threshold=fail_at,
                comparator="<",
                detail=detail,
            )
        )

    # -- CRD-DLQ-002: everything else -----------------------------------------
    if other_rule is None:
        out.append(_missing("CRD-DLQ-002", "non_housing_delinquency"))
    else:
        params = parameters_of(other_rule)
        refer_at = _float(params.get("accounts_30d_refer_at"))
        any_90 = params.get("any_90d_refer") is True
        accounts_30 = sum(
            1 for a in other if int(_float(a.get("lates_30d_24m")) or 0) > 0
        )
        accounts_90 = sum(
            1 for a in other if int(_float(a.get("lates_90d_24m")) or 0) > 0
        )
        if any_90 and accounts_90:
            verdict, detail = Verdict.INDETERMINATE, (
                f"{accounts_90} non-housing account(s) with a 90-day late; "
                f"CRD-DLQ-002 refers on any"
            )
        elif refer_at is not None and accounts_30 >= refer_at:
            verdict, detail = Verdict.INDETERMINATE, (
                f"{accounts_30} non-housing account(s) with a 30-day late against a "
                f"referral point of {refer_at:.0f}"
            )
        elif refer_at is None and not any_90:
            verdict, detail = Verdict.INDETERMINATE, (
                "CRD-DLQ-002 was retrieved but publishes no delinquency counts"
            )
        else:
            verdict, detail = Verdict.PASS, (
                f"non-housing delinquency is within the pattern CRD-DLQ-002 allows "
                f"across {len(other)} tradeline(s)"
            )
        out.append(
            RuleEvaluation(
                rule_id="CRD-DLQ-002",
                citation=str(other_rule.get("citation") or ""),
                measure="non_housing_delinquency", unit="count",
                verdict=verdict,
                observed=float(accounts_30),
                threshold=refer_at,
                comparator="<",
                detail=detail,
            )
        )
    return out


def _is_housing(account: Mapping[str, Any]) -> bool:
    kind = str(account.get("account_type", "")).lower()
    return any(token in kind for token in ("mortgage", "heloc", "home_equity", "rent"))


# ======================================================================================
# GEN-ELG — general eligibility
# ======================================================================================


def evaluate_general_eligibility(
    calculations: Mapping[str, Any],
    packet: Mapping[str, Any],
    evidence: Sequence[Mapping[str, Any]],
) -> list[RuleEvaluation]:
    """The programme limit, and whether ability to repay rests on verified facts.

    ``GEN-ELG-003`` is the one most easily got wrong: a loan above the conforming
    limit is **not ineligible**, it is *not conforming*. The rule says so in as
    many words. Failing it would decline every jumbo file in the book, so the
    test is conditional on the programme the file was actually offered under.
    """
    out: list[RuleEvaluation] = []
    rule = find_rule(evidence, "GEN-ELG-003")
    amount = _float(
        (packet.get("property_costs") or {}).get("note_amount")
    ) or _float((packet.get("requested_loan") or {}).get("base_loan_amount"))
    family = str(packet.get("product_family", "")).lower()

    if rule is None:
        out.append(_missing("GEN-ELG-003", "programme_loan_limit", amount))
    elif amount is None:
        out.append(
            RuleEvaluation(
                rule_id="GEN-ELG-003",
                citation=str(rule.get("citation") or ""),
                measure="programme_loan_limit", unit="currency",
                verdict=Verdict.INDETERMINATE,
                detail="no note amount on the file",
            )
        )
    else:
        params = parameters_of(rule)
        baseline = _float(params.get("conforming_baseline_one_unit_2026"))
        ceiling = _float(params.get("high_cost_ceiling_one_unit_2026"))
        if family == "conventional_conforming" and baseline is not None:
            within = amount <= (ceiling or baseline)
            out.append(
                RuleEvaluation(
                    rule_id="GEN-ELG-003",
                    citation=str(rule.get("citation") or ""),
                    measure="programme_loan_limit", unit="currency",
                    verdict=Verdict.PASS if within else Verdict.FAIL,
                    observed=amount,
                    threshold=ceiling or baseline,
                    comparator="<=",
                    detail=(
                        f"a conventional conforming loan must not exceed the "
                        f"applicable one-unit limit "
                        f"(baseline ${baseline:,.0f}, high-cost ceiling "
                        f"${ceiling or baseline:,.0f})"
                        + (
                            ""
                            if within
                            else "; above it the loan is not ineligible, it is not "
                                 "conforming, and must be executed under another "
                                 "programme"
                        )
                    ),
                )
            )
        else:
            out.append(
                RuleEvaluation(
                    rule_id="GEN-ELG-003",
                    citation=str(rule.get("citation") or ""),
                    measure="programme_loan_limit", unit="currency",
                    verdict=Verdict.NOT_APPLICABLE,
                    observed=amount,
                    detail=(
                        f"the conforming limit governs conventional conforming "
                        f"execution; this file is {family or 'an unstated programme'}"
                    ),
                )
            )

    # -- GEN-ELG-006: ability to repay rests on verified information ----------
    atr_rule = find_rule(evidence, "GEN-ELG-006")
    if atr_rule is not None:
        results = {
            str(v.get("category", "")).lower(): str(v.get("result", "")).upper()
            for v in (packet.get("verification_results") or [])
        }
        needed = ("income", "employment", "assets", "identity")
        unverified = [
            category
            for category in needed
            if results.get(category) not in ("VERIFIED", "PASS", "CLEAR")
        ]
        out.append(
            RuleEvaluation(
                rule_id="GEN-ELG-006",
                citation=str(atr_rule.get("citation") or ""),
                measure="verified_information", unit="count",
                verdict=Verdict.PASS if not unverified else Verdict.INDETERMINATE,
                observed=float(len(needed) - len(unverified)),
                threshold=float(len(needed)),
                comparator=">=",
                detail=(
                    "income, employment, assets and identity are all third-party "
                    "verified"
                    if not unverified
                    else (
                        f"not verified: {', '.join(unverified)}. Ability to repay must "
                        f"be established from verified information, so the file is "
                        f"referred rather than decided on declared figures"
                    )
                ),
                factors=unverified,
            )
        )
    return out


# ======================================================================================
# JMB-ELG — the jumbo overlay
# ======================================================================================


def evaluate_jumbo(
    calculations: Mapping[str, Any],
    packet: Mapping[str, Any],
    evidence: Sequence[Mapping[str, Any]],
) -> list[RuleEvaluation]:
    """The jumbo overlay's tighter leverage, credit and reserve bars.

    Only applies to a jumbo file. Applying it to a conforming loan would impose a
    720 score floor and a 75% LTV cap that conforming policy does not set, which
    would decline files that are perfectly eligible.
    """
    family = str(packet.get("product_family", "")).lower()
    if family != "jumbo":
        return [
            RuleEvaluation(
                rule_id="JMB-ELG-001",
                citation="",
                measure="jumbo_overlay",
                verdict=Verdict.NOT_APPLICABLE,
                detail=(
                    f"the jumbo overlay governs jumbo execution; this file is "
                    f"{family or 'an unstated programme'}"
                ),
            )
        ]

    out: list[RuleEvaluation] = []
    ratios = calculations.get("ratios") or {}
    occupancy = str(packet.get("occupancy_type", "")).lower()

    # -- JMB-ELG-002: leverage and credit floor --------------------------------
    rule = find_rule(evidence, "JMB-ELG-002")
    if rule is None:
        out.append(_missing("JMB-ELG-002", "jumbo_ltv"))
    else:
        params = parameters_of(rule)
        cap = _float(
            params.get(
                "max_ltv_primary_residence"
                if occupancy == "primary_residence"
                else "max_ltv_other_occupancy"
            )
        )
        ltv = _float(ratios.get("ltv"))
        if cap is None or ltv is None:
            out.append(
                RuleEvaluation(
                    rule_id="JMB-ELG-002",
                    citation=str(rule.get("citation") or ""),
                    measure="jumbo_ltv",
                    verdict=Verdict.INDETERMINATE,
                    observed=ltv,
                    detail=(
                        "the jumbo LTV cap for this occupancy was not published in the "
                        "retrieved rule" if cap is None else "LTV could not be computed"
                    ),
                )
            )
        else:
            out.append(
                RuleEvaluation(
                    rule_id="JMB-ELG-002",
                    citation=str(rule.get("citation") or ""),
                    measure="jumbo_ltv",
                    verdict=Verdict.PASS if ltv <= cap else Verdict.FAIL,
                    observed=ltv, threshold=cap, comparator="<=",
                    detail=f"jumbo LTV cap for {occupancy or 'this occupancy'} is {cap:.0%}",
                )
            )

        floor = _float(params.get("min_representative_score"))
        score = _float((packet.get("credit_summary") or {}).get("representative_score"))
        if floor is not None and score is not None:
            out.append(
                RuleEvaluation(
                    rule_id="JMB-ELG-002",
                    citation=str(rule.get("citation") or ""),
                    measure="jumbo_representative_score", unit="score",
                    verdict=Verdict.PASS if score >= floor else Verdict.FAIL,
                    observed=score, threshold=floor, comparator=">=",
                    detail=(
                        f"the jumbo overlay sets a {floor:.0f} representative-score "
                        f"floor, above the conventional one"
                    ),
                )
            )

    # -- JMB-ELG-003: reserves, tiered by loan amount --------------------------
    reserve_rule = find_rule(evidence, "JMB-ELG-003")
    if reserve_rule is not None:
        params = parameters_of(reserve_rule)
        amount = _float((packet.get("property_costs") or {}).get("note_amount"))
        tier = _float(params.get("loan_amount_tier_trigger"))
        required = _float(params.get("min_months_reserves"))
        if amount is not None and tier is not None and amount > tier:
            required = _float(params.get("min_months_reserves_above_1_5m")) or required
        observed = _float(
            (calculations.get("counts") or {}).get("months_of_reserves")
        ) or _float(calculations.get("months_of_reserves"))
        if required is None or observed is None:
            out.append(
                RuleEvaluation(
                    rule_id="JMB-ELG-003",
                    citation=str(reserve_rule.get("citation") or ""),
                    measure="jumbo_reserves", unit="months",
                    verdict=Verdict.INDETERMINATE,
                    observed=observed,
                    threshold=required,
                    detail=(
                        "the jumbo reserve requirement or the months of reserves "
                        "could not be established"
                    ),
                )
            )
        else:
            out.append(
                RuleEvaluation(
                    rule_id="JMB-ELG-003",
                    citation=str(reserve_rule.get("citation") or ""),
                    measure="jumbo_reserves", unit="months",
                    verdict=Verdict.PASS if observed >= required else Verdict.FAIL,
                    observed=observed, threshold=required, comparator=">=",
                    detail=(
                        f"jumbo requires {required:.0f} months of reserves"
                        + (
                            f", raised above the ${tier:,.0f} loan-amount tier"
                            if tier is not None and amount is not None and amount > tier
                            else ""
                        )
                    ),
                )
            )

    # -- JMB-ELG-004: every jumbo file is seen by a human ----------------------
    human_rule = find_rule(evidence, "JMB-ELG-004")
    if human_rule is not None:
        out.append(
            RuleEvaluation(
                rule_id="JMB-ELG-004",
                citation=str(human_rule.get("citation") or ""),
                measure="jumbo_human_review",
                verdict=Verdict.INDETERMINATE,
                detail=(
                    "every jumbo file is reviewed by a human underwriter "
                    "(reason code HR-JUMBO-EXPOSURE); this is a routing requirement, "
                    "not a test the file can pass"
                ),
            )
        )
    return out


# ======================================================================================
# VAL-APR — valuation
# ======================================================================================


def evaluate_valuation(
    calculations: Mapping[str, Any],
    packet: Mapping[str, Any],
    evidence: Sequence[Mapping[str, Any]],
) -> list[RuleEvaluation]:
    """Valuation age, and an appraisal that came in below the contract price."""
    out: list[RuleEvaluation] = []
    costs = packet.get("property_costs") or {}
    property_ = packet.get("subject_property") or {}

    # -- VAL-APR-002: appraised value below contract price ---------------------
    rule = find_rule(evidence, "VAL-APR-002")
    appraised = _float(costs.get("appraised_value"))
    contract = _float(property_.get("purchase_price"))
    used = _float(costs.get("value_used_for_ltv"))
    if rule is not None and appraised is not None and contract is not None:
        expected = min(appraised, contract)
        # The test is not "did it come in low" — that is allowed and common. It
        # is whether the *lower* of the two was used, which is what the rule
        # requires and what an upward adjustment would violate.
        correct = used is None or abs(used - expected) < 1.0
        out.append(
            RuleEvaluation(
                rule_id="VAL-APR-002",
                citation=str(rule.get("citation") or ""),
                measure="value_used_for_ltv", unit="currency",
                verdict=Verdict.PASS if correct else Verdict.FAIL,
                observed=used,
                threshold=expected,
                comparator="==",
                detail=(
                    f"the lower of contract (${contract:,.0f}) and appraised "
                    f"(${appraised:,.0f}) governs LTV"
                    + (
                        f"; ${used:,.0f} was used"
                        if used is not None and not correct
                        else ""
                    )
                    + (
                        ". The appraisal came in below contract, so the shortfall "
                        "needs additional borrower funds or a renegotiated price"
                        if appraised < contract
                        else ""
                    )
                ),
            )
        )
    elif rule is None:
        out.append(_missing("VAL-APR-002", "value_used_for_ltv", used))

    # -- VAL-APR-003: valuation age -------------------------------------------
    age_rule = find_rule(evidence, "VAL-APR-003")
    note_date = _note_date(packet)
    appraisal_date = _appraisal_date(packet)
    if age_rule is None:
        out.append(_missing("VAL-APR-003", "valuation_age_days"))
    elif note_date is None or appraisal_date is None:
        out.append(
            RuleEvaluation(
                rule_id="VAL-APR-003",
                citation=str(age_rule.get("citation") or ""),
                measure="valuation_age_days", unit="days",
                verdict=Verdict.INDETERMINATE,
                detail="no dated valuation on the file",
            )
        )
    else:
        params = parameters_of(age_rule)
        limit = _float(params.get("max_age_days"))
        update_window = _float(params.get("update_window_days"))
        age = float((note_date - appraisal_date).days)
        if limit is None:
            out.append(
                RuleEvaluation(
                    rule_id="VAL-APR-003",
                    citation=str(age_rule.get("citation") or ""),
                    measure="valuation_age_days", unit="days",
                    verdict=Verdict.INDETERMINATE,
                    observed=age,
                    detail="VAL-APR-003 was retrieved but publishes no age window",
                )
            )
        elif age <= limit:
            verdict = Verdict.PASS
            out.append(
                RuleEvaluation(
                    rule_id="VAL-APR-003",
                    citation=str(age_rule.get("citation") or ""),
                    measure="valuation_age_days", unit="days",
                    verdict=verdict, observed=age, threshold=limit, comparator="<=",
                    detail=f"the valuation is {age:.0f} days old against a {limit:.0f}-day window",
                )
            )
        else:
            # Between the window and the update window an update cures it; past
            # the update window a new valuation is required outright.
            curable = update_window is not None and age <= update_window
            out.append(
                RuleEvaluation(
                    rule_id="VAL-APR-003",
                    citation=str(age_rule.get("citation") or ""),
                    measure="valuation_age_days", unit="days",
                    verdict=Verdict.INDETERMINATE if curable else Verdict.FAIL,
                    observed=age, threshold=limit, comparator="<=",
                    detail=(
                        f"the valuation is {age:.0f} days old, past the {limit:.0f}-day "
                        f"window"
                        + (
                            f"; within the {update_window:.0f}-day update window, so an "
                            f"appraisal update cures it"
                            if curable
                            else "; past the update window, so a new valuation is required"
                        )
                    ),
                )
            )
    return out


def _appraisal_date(packet: Mapping[str, Any]) -> date | None:
    """The valuation date, from the appraisal document on the packet."""
    for document in packet.get("supplied_documents") or []:
        if str(document.get("document_type", "")).lower() in (
            "appraisal_report", "valuation_report", "value_acceptance",
        ):
            found = _as_date(document.get("document_date"))
            if found is not None:
                return found
    return None


# ======================================================================================
# Dispatch
# ======================================================================================


def evaluate_mortgage_families(
    calculations: Mapping[str, Any],
    packet: Mapping[str, Any],
    evidence: Sequence[Mapping[str, Any]],
) -> list[RuleEvaluation]:
    """Every extended mortgage family, in GEN-ELG-001's order of evaluation."""
    return [
        *evaluate_general_eligibility(calculations, packet, evidence),
        *evaluate_documentation(calculations, packet, evidence),
        *evaluate_employment_continuity(calculations, packet, evidence),
        *evaluate_credit_events(calculations, packet, evidence),
        *evaluate_delinquency(calculations, packet, evidence),
        *evaluate_asset_source(calculations, packet, evidence),
        *evaluate_valuation(calculations, packet, evidence),
        *evaluate_jumbo(calculations, packet, evidence),
    ]


__all__ = [
    "evaluate_asset_source",
    "evaluate_credit_events",
    "evaluate_delinquency",
    "evaluate_documentation",
    "evaluate_employment_continuity",
    "evaluate_general_eligibility",
    "evaluate_jumbo",
    "evaluate_mortgage_families",
    "evaluate_valuation",
]
