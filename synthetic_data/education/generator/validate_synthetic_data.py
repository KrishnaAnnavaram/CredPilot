#!/usr/bin/env python3
"""
Consistency checker for Education Loan synthetic dataset.
Asserts every internal-consistency rule and exits non-zero on violation.

Usage:
    python validate_synthetic_data.py
"""

import json, sys, os
from pathlib import Path
from collections import Counter

BASE = Path(__file__).resolve().parent.parent
APP_DIR = BASE / "applications"
POLICY_DIR = BASE / "policy_corpus"

passed = 0
failed = 0
warnings = 0

def check(condition, msg):
    global passed, failed
    if condition:
        passed += 1
    else:
        failed += 1
        print(f"  FAIL: {msg}")

def warn(condition, msg):
    global warnings
    if not condition:
        warnings += 1
        print(f"  WARN: {msg}")

def main():
    global passed, failed, warnings

    # Load all applications
    app_files = sorted(APP_DIR.glob("APP-2026-*.json"))
    check(len(app_files) == 200, f"Expected 200 applications, found {len(app_files)}")

    apps = []
    for f in app_files:
        with open(f) as fh:
            apps.append(json.load(fh))

    print(f"Loaded {len(apps)} applications\n")

    # ── 1. Product mix ──
    print("1. Product mix")
    pmix = Counter(a["product_code"] for a in apps)
    check(pmix["UG"] == 80, f"UG count: {pmix['UG']} (expected 80)")
    check(pmix["GR"] == 50, f"GR count: {pmix['GR']} (expected 50)")
    check(pmix["SP"] == 30, f"SP count: {pmix['SP']} (expected 30)")
    check(pmix["INTL"] == 25, f"INTL count: {pmix['INTL']} (expected 25)")
    check(pmix["REFI"] == 15, f"REFI count: {pmix['REFI']} (expected 15)")

    # ── 2. Application ID uniqueness ──
    print("2. Application ID uniqueness")
    ids = [a["application_id"] for a in apps]
    check(len(ids) == len(set(ids)), "Duplicate application IDs found")

    # ── 3. Borrower ID uniqueness ──
    print("3. Borrower ID uniqueness")
    bids = [a["borrower"]["borrower_id"] for a in apps]
    check(len(bids) == len(set(bids)), "Duplicate borrower IDs found")

    # ── 4. Decision consistency ──
    print("4. Decision consistency")
    for a in apps:
        d = a["decision"]
        aid = a["application_id"]

        # DECLINE must have reason codes
        if d["decision"] == "DECLINE":
            check(len(d["decline_reason_codes"]) > 0,
                  f"{aid}: DECLINE with no reason codes")
            check(d["approved_amount"] is None,
                  f"{aid}: DECLINE with non-null approved_amount")

        # APPROVE must have no decline reason codes
        if d["decision"] == "APPROVE":
            check(len(d["decline_reason_codes"]) == 0,
                  f"{aid}: APPROVE with decline reason codes: {d['decline_reason_codes']}")

        # APPROVE_WITH_CONDITIONS must have conditions
        if d["decision"] == "APPROVE_WITH_CONDITIONS":
            check(len(d["conditions"]) > 0,
                  f"{aid}: APPROVE_WITH_CONDITIONS with no conditions")

        # Adverse action
        if d["decision"] in ("DECLINE", "APPROVE_WITH_CONDITIONS"):
            check(d["adverse_action_required"],
                  f"{aid}: {d['decision']} but adverse_action_required=false")
        if d["decision"] == "APPROVE":
            check(not d["adverse_action_required"],
                  f"{aid}: APPROVE but adverse_action_required=true")

    # ── 5. School certification math ──
    print("5. School certification consistency")
    for a in apps:
        cert = a.get("school_certification")
        if cert and cert["certification_status"] == "RECEIVED":
            coa = cert["cost_of_attendance"]
            aid_ = cert["other_financial_aid"]
            fed = cert["federal_loans_amount"]
            cme = cert["certified_max_eligible"]
            expected = round(coa - aid_ - fed, 2)
            check(abs(cme - expected) < 0.02,
                  f"{a['application_id']}: cert_max {cme} != COA({coa}) - aid({aid_}) - fed({fed}) = {expected}")

    # ── 6. Approved amount ≤ certified max (non-REFI) ──
    print("6. Approved amount <= certified max")
    for a in apps:
        if a["product_code"] == "REFI":
            continue
        d = a["decision"]
        cert = a.get("school_certification")
        if d["decision"] != "DECLINE" and d["approved_amount"] is not None and cert and cert["certification_status"] == "RECEIVED":
            check(d["approved_amount"] <= cert["certified_max_eligible"] + 0.01,
                  f"{a['application_id']}: approved {d['approved_amount']} > cert_max {cert['certified_max_eligible']}")

    # ── 7. DTI computation ──
    print("7. DTI computation")
    for a in apps:
        for inc in a.get("income_verification", []):
            if inc["gross_annual_income"] > 0:
                expected_dti = round(inc["monthly_debt_service"] / ((inc["gross_annual_income"] + inc["other_income"]) / 12), 4)
                check(abs(inc["dti_pct"] - expected_dti) < 0.005,
                      f"{a['application_id']} {inc['subject_id']}: DTI {inc['dti_pct']} != computed {expected_dti}")

    # ── 8. Cosigner consistency ──
    print("8. Cosigner consistency")
    for a in apps:
        if a["has_cosigner"]:
            check(a["cosigner"] is not None,
                  f"{a['application_id']}: has_cosigner=true but no cosigner record")
        else:
            check(a["cosigner"] is None,
                  f"{a['application_id']}: has_cosigner=false but cosigner record present")

    # ── 9. INTL must have international_details ──
    print("9. International details")
    for a in apps:
        if a["product_code"] == "INTL":
            check(a["international_details"] is not None,
                  f"{a['application_id']}: INTL product missing international_details")
        else:
            check(a["international_details"] is None,
                  f"{a['application_id']}: non-INTL product has international_details")

    # ── 10. REFI must have existing_loans ──
    print("10. REFI existing loans")
    for a in apps:
        if a["product_code"] == "REFI":
            check(a["existing_loans"] is not None and len(a["existing_loans"]) > 0,
                  f"{a['application_id']}: REFI product missing existing_loans")
        else:
            check(a["existing_loans"] is None,
                  f"{a['application_id']}: non-REFI product has existing_loans")

    # ── 11. REFI has no school ──
    print("11. REFI school exclusion")
    for a in apps:
        if a["product_code"] == "REFI":
            check(a["school"] is None,
                  f"{a['application_id']}: REFI has school record")

    # ── 12. Non-REFI must have school ──
    print("12. Non-REFI school requirement")
    for a in apps:
        if a["product_code"] != "REFI":
            check(a["school"] is not None,
                  f"{a['application_id']}: non-REFI missing school")

    # ── 13. FICO distribution checks ──
    print("13. FICO distributions")
    cosigner_ficos = []
    refi_ficos = []
    for a in apps:
        for cb in a.get("credit_bureau", []):
            if cb["subject_type"] == "cosigner" and cb["fico_score"] is not None:
                cosigner_ficos.append(cb["fico_score"])
            if cb["subject_type"] == "borrower" and cb["fico_score"] is not None and a["product_code"] == "REFI":
                refi_ficos.append(cb["fico_score"])

    if cosigner_ficos:
        avg_cos = sum(cosigner_ficos) / len(cosigner_ficos)
        warn(660 < avg_cos < 780, f"Cosigner FICO avg {avg_cos:.0f} outside expected range 660-780")
    if refi_ficos:
        avg_refi = sum(refi_ficos) / len(refi_ficos)
        warn(650 < avg_refi < 770, f"REFI FICO avg {avg_refi:.0f} outside expected range 650-770")

    # ── 14. Masked SSN format ──
    print("14. SSN masking format")
    for a in apps:
        ssn = a["borrower"]["ssn_itin_masked"]
        check(ssn.startswith("XXX-XX-") and len(ssn) == 11,
              f"{a['application_id']}: bad SSN format: {ssn}")

    # ── 15. Risk grade validity ──
    print("15. Risk grade validity")
    valid_grades = {"A1","A2","A3","B1","B2","B3","C1","C2","C3","D1","D2","D3","E1","E2","E3"}
    for a in apps:
        check(a["decision"]["risk_grade"] in valid_grades,
              f"{a['application_id']}: invalid grade {a['decision']['risk_grade']}")

    # ── 16. Aggregate exposure math ──
    print("16. Aggregate exposure consistency")
    for a in apps:
        agg = a.get("aggregate_exposure", {})
        if agg.get("projected_starting_salary", 0) > 0:
            expected_ratio = round(agg["projected_debt_at_graduation"] / agg["projected_starting_salary"], 4)
            check(abs(agg["debt_to_projected_income_ratio"] - expected_ratio) < 0.005,
                  f"{a['application_id']}: debt_to_income ratio {agg['debt_to_projected_income_ratio']} != {expected_ratio}")

    # ── 17. Policy docs exist ──
    print("17. Policy documents")
    expected_policies = [f"POL-{i:03d}" for i in range(1, 13)]
    policy_files = list(POLICY_DIR.glob("POL-*.md"))
    check(len(policy_files) >= 12, f"Expected 12 policy files, found {len(policy_files)}")

    # ── Summary ──
    print("\n" + "=" * 60)
    print(f"VALIDATION COMPLETE: {passed} passed, {failed} failed, {warnings} warnings")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)
    else:
        print("All checks passed.")
        sys.exit(0)

if __name__ == "__main__":
    main()
