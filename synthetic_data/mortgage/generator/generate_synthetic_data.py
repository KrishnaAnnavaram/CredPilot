#!/usr/bin/env python3
"""
CredPilot synthetic-data generator.

    python synthetic_data/mortgage/generator/generate_synthetic_data.py

Reproducible: the seed comes from SYNTHETIC_SEED (default 20260920) and every
random draw is derived from a hash of that seed plus a stable label, so running
twice produces byte-identical output and adding a scenario never shifts the values
of the ones already there.

The generator asserts each scenario against the rules engine as it builds. If a
scenario stops producing the outcome it declares, generation fails loudly rather
than emitting mislabelled ground truth.

Writes:
    synthetic_data/mortgage/policy_corpus/        42 versioned policy documents
    synthetic_data/mortgage/applications/         the input packets the copilot reads
    synthetic_data/mortgage/structured/           32 relational tables
    synthetic_data/mortgage/profiles/             borrower and application profiles
    synthetic_data/mortgage/policy_metadata/      policy and rule catalogues
    synthetic_data/mortgage/applicant_documents/  one folder per application
    synthetic_data/mortgage/scenarios/            scenario_catalog.json
    synthetic_data/mortgage/golden_set/           evaluation cases and expected results
    synthetic_data/mortgage/schemas/              JSON Schemas
"""

from __future__ import annotations

import argparse
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import synthetic_data_utils as u
from synth.build import ApplicationBuilder, BuiltApplication
from synth.corpus import ALL_POLICIES, REGISTRY
from synth.documents import DocumentBuilder
from synth.emit import (
    application_input_packet,
    golden_case,
    json_schemas,
    policy_rule_rows,
    write_documents,
    write_policy_corpus,
    write_tables,
)
from synth.people import make_demographics, make_person
from synth.rules_engine import (
    Engine,
    eligibility_result,
    recommendation,
    requires_human_review,
    risk_level,
)
from synth.scenarios import SCENARIOS

ZERO = Decimal("0")


class ScenarioAssertionError(RuntimeError):
    """A scenario no longer produces the ground truth it declares."""


def assert_scenario(built: BuiltApplication) -> None:
    spec = built.scenario
    result = built.engine_result
    rec = recommendation(result, built.facts)
    problems: list[str] = []

    if rec != spec.expect_recommendation:
        problems.append(f"recommendation {rec} != declared {spec.expect_recommendation}")
    elig = eligibility_result(result)
    if elig != spec.expect_eligibility:
        problems.append(f"eligibility {elig} != declared {spec.expect_eligibility}")
    hr = requires_human_review(result, rec)
    if hr != spec.expect_human_review:
        problems.append(f"human_review {hr} != declared {spec.expect_human_review}")

    fails = {e.rule_id for e in result.breaches}
    missing = sorted(set(spec.expect_breach_rules) - fails)
    if missing:
        problems.append(f"declared breaches not produced: {missing} (actual {sorted(fails)})")
    refers = {e.rule_id for e in result.refers}
    missing_r = sorted(set(spec.expect_refer_rules) - refers)
    if missing_r:
        problems.append(f"declared refers not produced: {missing_r} (actual {sorted(refers)})")
    categories = {f["category"] for f in result.risk_flags}
    missing_c = sorted(set(spec.expect_risk_categories) - categories)
    if missing_c:
        problems.append(
            f"declared risk categories not produced: {missing_c} (actual {sorted(categories)})"
        )
    if spec.security_test_type and not spec.security_event_types:
        problems.append("security scenario produced no security event")

    if problems:
        raise ScenarioAssertionError(
            f"{spec.scenario_id} ({spec.name}):\n  - " + "\n  - ".join(problems)
        )


def build_all(seed: int) -> dict[str, Any]:
    engine = Engine(REGISTRY)
    builder = ApplicationBuilder(engine, REGISTRY, seed)
    doc_builder = DocumentBuilder(seed)

    people_by_scenario: dict[str, Any] = {}
    person_index = 0
    all_people: list[Any] = []
    demographics: list[Any] = []
    built_apps: list[BuiltApplication] = []

    for number, spec in enumerate(SCENARIOS, start=1):
        if spec.returning_borrower_of:
            primary = people_by_scenario[spec.returning_borrower_of]
        else:
            person_index += 1
            primary = make_person(
                u.sub_rng(seed, f"person:{spec.scenario_id}:p"), person_index, spec.as_of
            )
            all_people.append(primary)
            demographics.append(
                make_demographics(
                    u.sub_rng(seed, f"demo:{primary.borrower_id}"), primary, spec.as_of
                )
            )
            people_by_scenario[spec.scenario_id] = primary

        co = None
        if spec.co_borrower:
            person_index += 1
            co = make_person(
                u.sub_rng(seed, f"person:{spec.scenario_id}:c"), person_index, spec.as_of
            )
            all_people.append(co)
            demographics.append(
                make_demographics(
                    u.sub_rng(seed, f"demo:{co.borrower_id}"), co, spec.as_of
                )
            )

        built = builder.build(spec, number, primary, co)
        assert_scenario(built)
        built_apps.append(built)

    return {
        "applications": built_apps,
        "people": all_people,
        "demographics": demographics,
        "doc_builder": doc_builder,
    }


def to_rows(state: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Flatten the built applications into the committed relational tables."""
    apps: list[BuiltApplication] = state["applications"]
    tables: dict[str, list[dict[str, Any]]] = {name: [] for name in (
        "borrowers", "borrower_demographics", "applications", "application_borrowers",
        "loans", "properties", "employment", "income", "assets", "asset_transactions",
        "liabilities", "credit_profiles", "credit_accounts", "credit_events",
        "documents", "document_extractions", "appraisals", "title_records",
        "insurance_records", "verifications", "fraud_checks", "rule_evaluations",
        "risk_flags", "underwriting_calculations", "eligibility_results", "conditions",
        "decisions", "decision_reasons", "human_reviews", "security_events",
        "audit_events", "scenario_assignments",
    )}

    for person in state["people"]:
        tables["borrowers"].append(
            {
                "borrower_id": person.borrower_id,
                "first_name": person.first_name,
                "last_name": person.last_name,
                "date_of_birth": person.date_of_birth,
                "age_band_note": (
                    "Age is never a credit factor (CRD-SCR-006); date of birth is held "
                    "for identity verification only."
                ),
                "ssn_token": person.ssn_token,
                "ssn_masked": person.ssn_masked,
                "email": person.email,
                "phone": person.phone,
                "street": person.street,
                "city": person.city,
                "state": person.state,
                "postal_code": person.postal_code,
                "prior_street": person.prior_street,
                "prior_city": person.prior_city,
                "prior_state": person.prior_state,
                "prior_postal_code": person.prior_postal_code,
                "years_at_current_address": person.years_at_current_address,
                "marital_status": person.marital_status,
                "dependents": person.dependents,
                "citizenship_status": person.citizenship_status,
                "credit_file_token": person.credit_file_token,
                "credit_file_masked": person.credit_file_masked,
                "employer": person.employer,
                "employer_sector": person.employer_sector,
                "occupation": person.occupation,
            }
        )
    for demo in state["demographics"]:
        tables["borrower_demographics"].append(
            {
                "borrower_id": demo.borrower_id,
                "ethnicity": demo.ethnicity,
                "race": demo.race,
                "sex": demo.sex,
                "age_band": demo.age_band,
                "collection_method": demo.collection_method,
                "use_restriction": (
                    "MONITORING_ONLY - must never reach an eligibility, affordability, "
                    "risk or recommendation component (SEC-PII-002, CRD-SCR-006, "
                    "DEC-ADV-003)"
                ),
            }
        )

    doc_builder = state["doc_builder"]
    packets: list[dict[str, Any]] = []
    golden_cases: list[dict[str, Any]] = []
    golden_expected: list[dict[str, Any]] = []
    borrower_profiles: dict[str, dict[str, Any]] = {}
    application_profiles: list[dict[str, Any]] = []

    for built in apps:
        app_id = built.application["application_id"]
        spec = built.scenario
        result = built.engine_result
        as_of = built.application["underwriting_as_of_date"]
        rec = recommendation(result, built.facts)
        needs_human = requires_human_review(result, rec)

        tables["applications"].append(built.application)
        tables["application_borrowers"].extend(built.application_borrowers)
        tables["loans"].append(built.loan)
        tables["properties"].append(built.prop)
        tables["employment"].extend(built.employments)
        tables["title_records"].extend(built.title_records)
        tables["insurance_records"].extend(built.insurance_records)
        tables["verifications"].extend(built.verifications)
        tables["credit_profiles"].extend(built.credit_profiles)
        tables["credit_accounts"].extend(built.credit_accounts)
        tables["credit_events"].extend(built.credit_events)
        tables["assets"].extend(built.assets)
        tables["asset_transactions"].extend(built.asset_transactions)
        tables["liabilities"].extend(built.liabilities)
        tables["underwriting_calculations"].extend(built.calculations)
        if built.appraisal:
            tables["appraisals"].append(built.appraisal)

        primary_id = built.borrowers[0].borrower_id
        for idx, src in enumerate(built.income_sources, 1):
            tables["income"].append(
                {
                    "income_id": f"{app_id}-INC-{idx:02d}",
                    "application_id": app_id,
                    "borrower_id": src.get("borrower_id", primary_id),
                    "income_type": src["income_type"],
                    "declared_monthly_amount": src["declared_monthly_amount"],
                    "verified_monthly_amount": src["verified_monthly_amount"],
                    "qualifying_monthly_amount": src["qualifying_monthly_amount"],
                    "annual_amount": src["annual_amount"],
                    "qualifying_rule_id": _income_rule(src["income_type"]),
                    "evidence_document_types": _income_evidence(src["income_type"]),
                }
            )

        docs = doc_builder.build(built)
        meta, extractions = write_documents(built, docs, u.DOCUMENT_DIR)
        tables["documents"].extend(meta)
        tables["document_extractions"].extend(extractions)

        for idx, ev in enumerate(result.evaluations, 1):
            tables["rule_evaluations"].append(
                {
                    "evaluation_id": f"{app_id}-EVAL-{idx:03d}",
                    "application_id": app_id,
                    "rule_id": ev.rule_id,
                    "policy_id": ev.policy_id,
                    "policy_version": ev.policy_version,
                    "policy_effective_date": ev.policy_effective_date,
                    "source_category": ev.source_category,
                    "severity": ev.severity,
                    "outcome": ev.outcome,
                    "observed_value": ev.observed_value,
                    "comparator": ev.comparator,
                    "threshold_value": ev.threshold_value,
                    "input_fields": "|".join(ev.input_fields),
                    "requires_human_review": ev.requires_human_review,
                    "reason": ev.reason,
                }
            )
        for idx, flag in enumerate(result.risk_flags, 1):
            tables["risk_flags"].append(
                {
                    "risk_flag_id": f"{app_id}-RSK-{idx:02d}",
                    "application_id": app_id,
                    "category": flag["category"],
                    "severity": flag["severity"],
                    "detail": flag["detail"],
                    "evidence": flag["evidence"],
                    "rule_id": flag["rule_id"],
                    "status": flag["status"],
                }
            )
        for idx, cond in enumerate(result.conditions, 1):
            tables["conditions"].append(
                {
                    "condition_id": f"{app_id}-CND-{idx:02d}",
                    "application_id": app_id,
                    "category": cond["category"],
                    "text": cond["text"],
                    "required_evidence": cond["required_evidence"],
                    "timing": cond["timing"],
                    "status": cond["status"],
                    "rule_id": cond["rule_id"],
                    "created_date": as_of,
                }
            )
        for idx, indicator in enumerate(spec.fraud_indicators, 1):
            tables["fraud_checks"].append(
                {
                    "fraud_check_id": f"{app_id}-FRD-{idx:02d}",
                    "application_id": app_id,
                    "check_type": "cross_source_consistency",
                    "result": "INDICATOR_RAISED",
                    "indicator": indicator,
                    "evidence_source_a": "document_extractions",
                    "evidence_source_b": "income / employment tables",
                    "rule_id": "FRD-IND-001",
                    "requires_human_review": True,
                }
            )
        if spec.document_tampering:
            tables["fraud_checks"].append(
                {
                    "fraud_check_id": f"{app_id}-FRD-TMP",
                    "application_id": app_id,
                    "check_type": "document_integrity",
                    "result": "TAMPERING_INDICATOR",
                    "indicator": "Stated year-to-date gross does not sum from line items",
                    "evidence_source_a": "documents.tampering_indicator",
                    "evidence_source_b": "document_extractions.ytd_gross",
                    "rule_id": "FRD-IND-002",
                    "requires_human_review": True,
                }
            )

        determining = sorted(
            {
                e.rule_id
                for e in result.evaluations
                if e.outcome in ("FAIL", "INDETERMINATE")
            }
        )
        tables["eligibility_results"].append(
            {
                "eligibility_result_id": f"{app_id}-ELIG",
                "application_id": app_id,
                "programme": built.application["product_family"],
                "result": eligibility_result(result),
                "determining_rule_ids": "|".join(determining),
                "as_of_date": as_of,
            }
        )

        decision_id = f"{app_id}-DEC-01"
        tables["decisions"].append(
            {
                "decision_id": decision_id,
                "application_id": app_id,
                "decision_stage": "underwriting_recommendation",
                "decision_type": "COPILOT_RECOMMENDATION",
                "result": rec,
                "actor_type": "AUTOMATED_COMPONENT",
                "actor_id": "credpilot-underwriting-copilot",
                "decision_date": as_of,
                "risk_level": risk_level(result),
                "eligibility_result": eligibility_result(result),
                "requires_human_review": needs_human,
            }
        )
        if needs_human:
            tables["decisions"].append(
                {
                    "decision_id": f"{app_id}-DEC-02",
                    "application_id": app_id,
                    "decision_stage": "credit_decision",
                    "decision_type": "HUMAN_CREDIT_DECISION",
                    "result": "PENDING_HUMAN_REVIEW",
                    "actor_type": "HUMAN",
                    "actor_id": "unassigned",
                    "decision_date": None,
                    "risk_level": risk_level(result),
                    "eligibility_result": eligibility_result(result),
                    "requires_human_review": True,
                }
            )
        for idx, ev in enumerate(result.breaches + result.refers, 1):
            tables["decision_reasons"].append(
                {
                    "decision_reason_id": f"{app_id}-RSN-{idx:02d}",
                    "decision_id": decision_id,
                    "application_id": app_id,
                    "reason_code": "RSN-" + ev.rule_id.replace("-", ""),
                    "reason_text": ev.reason,
                    "rule_id": ev.rule_id,
                    "policy_id": ev.policy_id,
                    "policy_version": ev.policy_version,
                    "evidence_reference": "|".join(ev.input_fields),
                }
            )
        if needs_human:
            triggers = sorted({r.split(":")[0] for r in result.human_review_reasons})
            tables["human_reviews"].append(
                {
                    "human_review_id": f"{app_id}-HRV",
                    "application_id": app_id,
                    "queue": _queue(spec, rec),
                    "trigger_rule_ids": "|".join(triggers) if triggers else rec,
                    "reason_code": _hr_reason_code(spec, rec),
                    "reason_text": (
                        result.human_review_reasons[0]
                        if result.human_review_reasons
                        else f"{rec} is never auto-decided (DEC-REC-002)."
                    ),
                    "reviewer_role": _reviewer_role(spec, rec),
                    "status": "OPEN",
                    "opened_date": as_of,
                }
            )
        for idx, event in enumerate(spec.security_event_types, 1):
            tables["security_events"].append(
                {
                    "security_event_id": f"{app_id}-SEC-{idx:02d}",
                    "application_id": app_id,
                    "event_type": event,
                    "detected_in": (
                        "bank_statement memo line"
                        if event == "INSTRUCTION_SMUGGLING"
                        else "applicant free-text submission"
                    ),
                    "masked_excerpt": _mask_excerpt(spec.untrusted_text),
                    "action_taken": "QUARANTINED_AND_ESCALATED",
                    "rule_id": _security_rule(event),
                    "detected_at": as_of,
                }
            )

        tables["audit_events"].extend(_audit_trail(built, rec, needs_human))
        tables["scenario_assignments"].append(
            {
                "application_id": app_id,
                "scenario_id": spec.scenario_id,
                "scenario_name": spec.name,
                "security_test_type": spec.security_test_type,
                "expected_recommendation": rec,
                "expected_human_review": needs_human,
            }
        )

        packet = application_input_packet(built, docs)
        packets.append(packet)
        case, expected = golden_case(built, docs)
        golden_cases.append(case)
        golden_expected.append(expected)

        for person in built.borrowers:
            profile = borrower_profiles.setdefault(
                person.borrower_id,
                {
                    "borrower_id": person.borrower_id,
                    "name": person.full_name,
                    "date_of_birth": person.date_of_birth,
                    "taxpayer_id_masked": person.ssn_masked,
                    "email": person.email,
                    "phone": person.phone,
                    "current_address": {
                        "street": person.street, "city": person.city,
                        "state": person.state, "postal_code": person.postal_code,
                    },
                    "previous_address": (
                        {
                            "street": person.prior_street, "city": person.prior_city,
                            "state": person.prior_state,
                            "postal_code": person.prior_postal_code,
                        }
                        if person.prior_street
                        else None
                    ),
                    "years_at_current_address": person.years_at_current_address,
                    "household": {
                        "marital_status": person.marital_status,
                        "dependents": person.dependents,
                    },
                    "citizenship_status": person.citizenship_status,
                    "employer": person.employer,
                    "employer_sector": person.employer_sector,
                    "occupation": person.occupation,
                    "credit_file_masked": person.credit_file_masked,
                    "applications": [],
                },
            )
            profile["applications"].append(app_id)

        application_profiles.append(
            {
                "application_id": app_id,
                "scenario_id": spec.scenario_id,
                "as_of_date": as_of,
                "product_family": built.application["product_family"],
                "loan_purpose": built.application["loan_purpose"],
                "occupancy_type": built.application["occupancy_type"],
                "borrower_ids": [p.borrower_id for p in built.borrowers],
                "base_loan_amount": built.loan["base_loan_amount"],
                "value_used_for_ltv": built.prop["value_used_for_ltv"],
                "qualifying_monthly_income": built.derived["qualifying_monthly_income"],
                "housing_expense_pitia": built.derived["housing_expense_pitia"],
                "total_monthly_debt": built.derived["total_monthly_debt"],
                "back_end_dti": built.derived["back_end_dti"],
                "ltv": built.derived["ltv"],
                "months_reserves": built.derived["months_reserves"],
                "representative_credit_score": built.derived[
                    "representative_credit_score"
                ],
                "document_count": len(docs),
            }
        )

    state["packets"] = packets
    state["golden_cases"] = golden_cases
    state["golden_expected"] = golden_expected
    state["borrower_profiles"] = list(borrower_profiles.values())
    state["application_profiles"] = application_profiles
    return tables


def _income_rule(income_type: str) -> str:
    return {
        "salaried": "INC-SAL-001", "hourly_variable": "INC-HRL-002",
        "self_employed": "INC-SEB-003", "bonus": "INC-VAR-002",
        "overtime": "INC-VAR-002", "commission": "INC-VAR-002",
        "rental": "INC-RNT-002", "rental_negative": "INC-RNT-002",
        "retirement": "INC-OTH-001", "social_security": "INC-OTH-001",
    }.get(income_type, "INC-GEN-001")


def _income_evidence(income_type: str) -> str:
    return {
        "salaried": "paystub|w2|employment_verification",
        "hourly_variable": "paystub|w2|employment_verification",
        "self_employed": "tax_return|profit_and_loss",
        "bonus": "paystub|w2", "overtime": "paystub|w2",
        "commission": "paystub|w2|tax_return",
        "rental": "lease_agreement|tax_return",
        "rental_negative": "lease_agreement|tax_return",
        "retirement": "award_letter", "social_security": "award_letter",
    }.get(income_type, "paystub")


def _queue(spec: Any, rec: str) -> str:
    if spec.security_test_type:
        return "SECURITY_REVIEW"
    if spec.identity_status != "VERIFIED" or spec.document_tampering:
        return "FRAUD_AND_FINANCIAL_CRIME"
    if spec.product == "jumbo":
        return "HIGH_VALUE_UNDERWRITING"
    if rec == "DECLINE_RECOMMENDATION":
        return "CREDIT_DECISION"
    return "UNDERWRITING"


def _hr_reason_code(spec: Any, rec: str) -> str:
    if spec.security_test_type:
        return f"HR-SECURITY-{spec.security_test_type}"
    if spec.identity_status != "VERIFIED":
        return "HR-IDENTITY-MISMATCH"
    if spec.document_tampering:
        return "HR-DOCUMENT-INTEGRITY"
    if spec.product == "jumbo":
        return "HR-JUMBO-EXPOSURE"
    if spec.self_employed:
        return "HR-SELF-EMPLOYED-COMPLEXITY"
    if rec == "DECLINE_RECOMMENDATION":
        return "HR-DECLINE-RECOMMENDATION"
    return "HR-POLICY-TRIGGER"


def _reviewer_role(spec: Any, rec: str) -> str:
    if spec.security_test_type or spec.identity_status != "VERIFIED":
        return "financial_crime_analyst"
    if rec == "DECLINE_RECOMMENDATION":
        return "credit_underwriter_authorised_decision_maker"
    if spec.product == "jumbo":
        return "senior_underwriter"
    return "underwriter"


def _security_rule(event: str) -> str:
    return {
        "PROMPT_INJECTION": "SEC-INJ-001",
        "POLICY_OVERRIDE_ATTEMPT": "SEC-INJ-001",
        "INSTRUCTION_SMUGGLING": "SEC-INJ-001",
        "CROSS_CUSTOMER_ACCESS": "SEC-INJ-002",
        "PII_EXTRACTION": "SEC-INJ-003",
        "OUT_OF_SCOPE_REQUEST": "SEC-INJ-004",
    }.get(event, "SEC-INJ-001")


def _mask_excerpt(text: str | None) -> str:
    if not text:
        return ""
    excerpt = text if len(text) <= 90 else text[:87] + "..."
    return excerpt.replace("\n", " ")


def _audit_trail(
    built: BuiltApplication, rec: str, needs_human: bool
) -> list[dict[str, Any]]:
    app_id = built.application["application_id"]
    as_of = built.application["underwriting_as_of_date"]
    correlation = f"RUN-{app_id}"
    steps = [
        ("AUTOMATED_COMPONENT", "authorise_case_access", "authorisation",
         "applications", app_id, "GRANTED"),
        ("AUTOMATED_COMPONENT", "classify_request", "intent_classifier",
         "applications", app_id, "MORTGAGE_UNDERWRITING"),
        ("AUTOMATED_COMPONENT", "select_policy_versions", "policy_retrieval",
         "policy_documents", "as_of=" + as_of.isoformat(), "RESOLVED"),
        ("AUTOMATED_COMPONENT", "extract_document_fields", "document_extraction",
         "documents", app_id, "COMPLETED"),
        ("AUTOMATED_COMPONENT", "run_calculations", "calculation_engine",
         "underwriting_calculations", app_id, "COMPLETED"),
        ("AUTOMATED_COMPONENT", "evaluate_rules", "rules_engine",
         "rule_evaluations", app_id, f"{len(built.engine_result.evaluations)} evaluated"),
        ("AUTOMATED_COMPONENT", "screen_risk", "risk_screening",
         "risk_flags", app_id, f"{len(built.engine_result.risk_flags)} flags"),
        ("AUTOMATED_COMPONENT", "produce_recommendation", "decision_composer",
         "decisions", app_id, rec),
    ]
    if built.scenario.security_event_types:
        steps.insert(
            3,
            ("AUTOMATED_COMPONENT", "quarantine_untrusted_text", "guardrail",
             "security_events", app_id, "QUARANTINED"),
        )
    if needs_human:
        steps.append(
            ("AUTOMATED_COMPONENT", "route_to_human_review", "router",
             "human_reviews", app_id, "QUEUED"),
        )
    rows = []
    for idx, (actor_type, action, tool, obj_type, obj_id, outcome) in enumerate(steps, 1):
        rows.append(
            {
                "audit_event_id": f"{app_id}-AUD-{idx:02d}",
                "application_id": app_id,
                "sequence": idx,
                "actor_type": actor_type,
                "actor_id": "credpilot-underwriting-copilot",
                "action": action,
                "tool": tool,
                "object_type": obj_type,
                "object_id": obj_id,
                "outcome": outcome,
                "correlation_id": correlation,
                "timestamp": as_of,
            }
        )
    return rows


def scenario_catalog(state: dict[str, Any]) -> list[dict[str, Any]]:
    entries = []
    by_scenario = {b.scenario.scenario_id: b for b in state["applications"]}
    for spec in SCENARIOS:
        built = by_scenario[spec.scenario_id]
        result = built.engine_result
        rec = recommendation(result, built.facts)
        entries.append(
            {
                "scenario_id": spec.scenario_id,
                "scenario_name": spec.name,
                "description": spec.description,
                "application_id": built.application["application_id"],
                "as_of_date": built.application["underwriting_as_of_date"],
                "features_being_tested": list(spec.features_tested),
                "expected_policy_rules": sorted(
                    {e.rule_id for e in result.evaluations}
                ),
                "expected_calculations": {
                    row["calculation_name"]: (
                        None if row["result"] is None else str(row["result"])
                    )
                    for row in built.calculations
                    if row["calculation_name"]
                    in (
                        "qualifying_monthly_income", "housing_expense_pitia",
                        "total_monthly_debt", "back_end_dti", "front_end_dti", "ltv",
                        "cash_to_close", "funds_shortfall", "months_reserves",
                        "representative_credit_score",
                    )
                },
                "expected_risk_flags": [
                    {"category": f["category"], "severity": f["severity"]}
                    for f in result.risk_flags
                ],
                "expected_routing": (
                    "HUMAN_REVIEW_QUEUE"
                    if requires_human_review(result, rec)
                    else "AUTOMATED_RECOMMENDATION"
                ),
                "expected_human_review": requires_human_review(result, rec),
                "expected_recommendation": rec,
                "expected_eligibility": eligibility_result(result),
                "security_test_type": spec.security_test_type,
                "expected_discrepancies": [dict(d) for d in spec.expected_discrepancies],
                "notes": spec.notes,
            }
        )
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--seed", type=int, default=None,
        help="override SYNTHETIC_SEED for this run",
    )
    args = parser.parse_args()
    seed = args.seed if args.seed is not None else u.resolve_seed()

    print(f"CredPilot synthetic data generator - seed {seed}")
    print("-" * 70)

    print("1/8  policy corpus")
    policy_rows = write_policy_corpus(ALL_POLICIES, u.POLICY_CORPUS_DIR)
    rule_rows = policy_rule_rows(ALL_POLICIES)
    u.write_csv(
        u.POLICY_META_DIR / "policies.csv", policy_rows,
        [c for c in (
            "policy_document_id", "policy_id", "version", "title", "family",
            "effective_date", "expiration_date", "source_category", "priority",
            "supersedes", "superseded_by", "requires_human_review", "jurisdiction",
            "product_scope", "occupancy_scope", "purpose_scope", "rule_count",
            "relative_path", "document_hash",
        )],
    )
    u.write_csv(
        u.POLICY_META_DIR / "policy_rules.csv", rule_rows,
        [c for c in (
            "rule_id", "policy_id", "policy_version", "policy_effective_date",
            "policy_expiration_date", "title", "source_category", "severity",
            "outcome_type", "requires_human_review", "parameters",
            "has_research_reference", "cross_refs",
        )],
    )
    print(f"     {len(policy_rows)} documents, {len(rule_rows)} rule versions")

    print("2/8  building applications (asserting each scenario)")
    state = build_all(seed)
    print(f"     {len(state['applications'])} applications, {len(state['people'])} people")

    print("3/8  structured tables and documents")
    tables = to_rows(state)
    counts = write_tables(tables, u.STRUCTURED_DIR)
    print(f"     {sum(counts.values())} rows across {len(counts)} tables")

    print("4/8  profiles")
    u.write_jsonl(u.PROFILE_DIR / "borrower_profiles.jsonl", state["borrower_profiles"])
    u.write_jsonl(
        u.PROFILE_DIR / "application_profiles.jsonl", state["application_profiles"]
    )

    print("5/8  application input packets")
    for packet in state["packets"]:
        u.write_json(
            u.APPLICATION_INPUT_DIR / f"{packet['application_id']}.json", packet
        )
    u.write_json(
        u.APPLICATION_INPUT_DIR / "index.json",
        {
            "generated_with_seed": seed,
            "count": len(state["packets"]),
            "note": (
                "Model inputs only. No expected decision, rule or risk flag appears in "
                "these files; ground truth lives in synthetic_data/mortgage/golden_set/."
            ),
            "applications": [p["application_id"] for p in state["packets"]],
        },
    )

    print("6/8  scenarios and golden set")
    catalog = scenario_catalog(state)
    u.write_json(
        u.SCENARIO_DIR / "scenario_catalog.json",
        {
            "generated_with_seed": seed,
            "scenario_count": len(catalog),
            "scenarios": catalog,
        },
    )
    u.write_jsonl(u.GOLDEN_DIR / "evaluation_cases.jsonl", state["golden_cases"])
    u.write_jsonl(u.GOLDEN_DIR / "expected_results.jsonl", state["golden_expected"])

    print("7/8  schemas")
    for name, schema in json_schemas().items():
        u.write_json(u.SCHEMA_DIR / name, schema)

    print("8/8  generated documentation")
    from synth import reports

    u.write_text(u.SYNTH_ROOT / "DATA_DICTIONARY.md", reports.data_dictionary())
    u.write_text(
        u.SYNTH_ROOT / "POLICY_TEST_COVERAGE.md", reports.policy_test_coverage()
    )
    u.write_text(
        u.SYNTH_ROOT / "SCENARIO_COVERAGE.md", reports.scenario_coverage(catalog)
    )
    u.write_text(
        u.SYNTH_ROOT / "SYNTHETIC_DATA_REPORT.md", reports.final_report(seed, catalog)
    )

    print("-" * 70)
    print("Generation complete.")
    print(f"  policy documents      {len(policy_rows)}")
    print(f"  policy rule versions  {len(rule_rows)}")
    print(f"  applications          {len(tables['applications'])}")
    print(f"  borrowers             {len(tables['borrowers'])}")
    print(f"  applicant documents   {len(tables['documents'])}")
    print(f"  rule evaluations      {len(tables['rule_evaluations'])}")
    print(f"  golden cases          {len(state['golden_cases'])}")
    print()
    print("Next: python synthetic_data/mortgage/generator/validate_synthetic_data.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
