<!-- GENERATED FILE - do not edit by hand.
     Regenerate with:  python synthetic_data/mortgage/generator/generate_synthetic_data.py -->

# CredPilot Synthetic Data Dictionary

Every committed table, its grain, what it is for, and every column with its inferred type. Row counts and types are read from the generated files, so this document describes what actually exists rather than what was intended.

Three column pairs recur and are the heart of the model. `declared_*` is what the applicant said, `verified_*` is what the evidence established, and `qualifying_*` is what policy permits underwriting to use. They are stored separately on purpose: collapsing them into one number destroys the ability to show which document supported which figure.

## `synthetic_data/mortgage/structured/`

### `application_borrowers.csv`

- **Rows:** 92
- **Grain:** One applicant's participation in one application.
- **Sensitivity:** Moderate.

The many-to-many bridge. Carries borrower role, order and joint-credit intent, which is what makes a returning applicant expressible.

| Column | Type | Description |
| --- | --- | --- |
| `application_id` | string | Application surrogate key, format APP-nnnnnn. |
| `borrower_id` | string | Person surrogate key, format BORR-nnnnnn. |
| `borrower_role` | string |  |
| `borrower_order` | integer |  |
| `joint_credit_intent` | boolean |  |

### `applications.csv`

- **Rows:** 75
- **Grain:** One application.
- **Sensitivity:** Moderate.

The operational record: dates, channel, product, purpose, occupancy and the underwriting as-of date that selects which policy versions apply.

| Column | Type | Description |
| --- | --- | --- |
| `application_id` | string | Application surrogate key, format APP-nnnnnn. |
| `scenario_id` | string | The scenario that produced this row. |
| `application_date` | date | Date the application became sufficiently complete. |
| `underwriting_as_of_date` | date | The date that selects which policy versions apply. |
| `received_date` | date | Date the item reached the lender. |
| `channel` | string | Origination channel. |
| `loan_purpose` | string | purchase | rate_term_refinance | cash_out_refinance. |
| `product_family` | string | conventional_conforming | jumbo | fha | va | usda. |
| `occupancy_type` | string | primary_residence | second_home | investment. |
| `borrower_count` | integer | Number of applicants; must match application_borrowers. |
| `primary_borrower_id` | string | Must match the borrower with role 'primary'. |
| `application_status` | string | Workflow state. |
| `loan_officer_id` | string | Surrogate key. |
| `loan_officer_identifier_type` | string |  |
| `household_size` | integer | Used by the residual-income and programme-income tests only. |

### `appraisals.csv`

- **Rows:** 73
- **Grain:** One valuation event.
- **Sensitivity:** Moderate.

Value, method, condition and dataset version. Absent where the transaction used value acceptance, which is why the valuation method lives on the property row too.

| Column | Type | Description |
| --- | --- | --- |
| `appraisal_id` | string | Surrogate key. |
| `application_id` | string | Application surrogate key, format APP-nnnnnn. |
| `property_id` | string | Surrogate key. |
| `appraisal_date` | date |  |
| `valuation_method` | string | full_appraisal | value_acceptance. Not every loan has a report. |
| `appraised_value` | decimal | Appraised or otherwise accepted value. |
| `appraiser_licence` | string |  |
| `condition_rating` | string |  |
| `condition_finding` | boolean |  |
| `dataset_version` | string |  |
| `below_contract_price` | boolean |  |

### `asset_transactions.csv`

- **Rows:** 73
- **Grain:** One relevant account movement.
- **Sensitivity:** Extreme.

Deposits and withdrawals that bear on source of funds, including the unsourced large deposits the risk rules act on.

| Column | Type | Description |
| --- | --- | --- |
| `transaction_id` | string | Surrogate key. |
| `application_id` | string | Application surrogate key, format APP-nnnnnn. |
| `asset_id` | string | Surrogate key. |
| `transaction_type` | string |  |
| `amount` | decimal |  |
| `transaction_date` | date |  |
| `description` | string |  |
| `source_status` | string |  |
| `large_deposit_flag` | boolean |  |

### `assets.csv`

- **Rows:** 296
- **Grain:** One asset account or source.
- **Sensitivity:** Extreme. Financial account data, tokenised.

Verified balance plus two independent eligibility amounts: what can be brought to closing and what counts as a reserve. They are frequently different, which is why one 'balance' column would not do.

| Column | Type | Description |
| --- | --- | --- |
| `asset_id` | string | Surrogate key. |
| `application_id` | string | Application surrogate key, format APP-nnnnnn. |
| `borrower_id` | string | Person surrogate key, format BORR-nnnnnn. |
| `asset_type` | string |  |
| `institution` | string |  |
| `account_token` | string | Tokenised deposit or brokerage account identifier. |
| `account_masked` | string | Display form, ******nnnn. |
| `declared_balance` | decimal | What the applicant stated. |
| `verified_balance` | decimal | What the statement or verification established. |
| `eligible_close_amount` | decimal | Portion usable at settlement after any haircut. |
| `eligible_reserve_amount` | decimal | Portion countable as a reserve. Gifts are always zero. |
| `liquidity_haircut` | decimal | Reduction applied for conversion cost or uncertainty. |
| `eligibility_rule_id` | string | Surrogate key. |

### `audit_events.csv`

- **Rows:** 653
- **Grain:** One recorded action.
- **Sensitivity:** Moderate.

The ordered trail from authorisation through policy selection, extraction, calculation, rule evaluation, risk screening and recommendation.

| Column | Type | Description |
| --- | --- | --- |
| `audit_event_id` | string | Surrogate key. |
| `application_id` | string | Application surrogate key, format APP-nnnnnn. |
| `sequence` | integer | Position in the run, contiguous from 1. |
| `actor_type` | string | AUTOMATED_COMPONENT | HUMAN. |
| `actor_id` | string | Surrogate key. |
| `action` | string |  |
| `tool` | string |  |
| `object_type` | string |  |
| `object_id` | string | Surrogate key. |
| `outcome` | string | PASS | FAIL | REFER | NOT_APPLICABLE | INDETERMINATE. |
| `correlation_id` | string | Ties one run's audit events together. |
| `timestamp` | date |  |

### `borrower_demographics.csv`

- **Rows:** 90
- **Grain:** One synthetic person.
- **Sensitivity:** Restricted. Monitoring use only; never a credit factor.

Statutory monitoring attributes, held in their own table with an explicit use restriction on every row. Never joined into any decision surface.

| Column | Type | Description |
| --- | --- | --- |
| `borrower_id` | string | Person surrogate key, format BORR-nnnnnn. |
| `ethnicity` | string |  |
| `race` | string |  |
| `sex` | string |  |
| `age_band` | string |  |
| `collection_method` | string |  |
| `use_restriction` | string | States that the row is monitoring-only. |

### `borrowers.csv`

- **Rows:** 90
- **Grain:** One synthetic person.
- **Sensitivity:** High. Contains name, address and tokenised identifiers.

Identity and contact attributes for every applicant. Every person here is fictional; identifiers are SYN- tokens and are displayed masked.

| Column | Type | Description |
| --- | --- | --- |
| `borrower_id` | string | Person surrogate key, format BORR-nnnnnn. |
| `first_name` | string |  |
| `last_name` | string |  |
| `date_of_birth` | date |  |
| `age_band_note` | string |  |
| `ssn_token` | string | Tokenised taxpayer identifier. Never a real SSN. |
| `ssn_masked` | string | Display form, ***-**-nnnn. |
| `email` | string | Reserved example.com domain (RFC 2606). |
| `phone` | string | Reserved fictional 555-0100..555-0199 block. |
| `street` | string |  |
| `city` | string |  |
| `state` | string |  |
| `postal_code` | integer |  |
| `prior_street` | string |  |
| `prior_city` | string |  |
| `prior_state` | string |  |
| `prior_postal_code` | integer |  |
| `years_at_current_address` | integer |  |
| `marital_status` | string |  |
| `dependents` | integer |  |
| `citizenship_status` | string |  |
| `credit_file_token` | string | Tokenised credit-file identifier. |
| `credit_file_masked` | string | Display form, ****nnnn. |
| `employer` | string |  |
| `employer_sector` | string |  |
| `occupation` | string |  |

### `conditions.csv`

- **Rows:** 25
- **Grain:** One outstanding item.
- **Sensitivity:** High.

What is required, what evidence satisfies it, when it is due and its status.

| Column | Type | Description |
| --- | --- | --- |
| `condition_id` | string | Surrogate key. |
| `application_id` | string | Application surrogate key, format APP-nnnnnn. |
| `category` | string |  |
| `text` | string |  |
| `required_evidence` | string |  |
| `timing` | string |  |
| `status` | string |  |
| `rule_id` | string | Stable rule identifier, citable in a decision. |
| `created_date` | date |  |

### `credit_accounts.csv`

- **Rows:** 301
- **Grain:** One tradeline.
- **Sensitivity:** Extreme.

Balances, limits, payments and late history. Links back to the liability it supports so the DTI numerator is traceable to the report.

| Column | Type | Description |
| --- | --- | --- |
| `credit_account_id` | string | Surrogate key. |
| `application_id` | string | Application surrogate key, format APP-nnnnnn. |
| `borrower_id` | string | Person surrogate key, format BORR-nnnnnn. |
| `liability_id` | string | Surrogate key. |
| `account_type` | string |  |
| `creditor` | string |  |
| `balance` | decimal |  |
| `credit_limit` | decimal | Revolving limit; zero means no stated limit. |
| `monthly_payment` | decimal | The payment the DTI numerator uses. |
| `opened_date` | date |  |
| `account_status` | string |  |
| `lates_30d_24m` | integer |  |
| `lates_60d_24m` | integer |  |
| `lates_90d_24m` | integer |  |
| `dispute_flag` | boolean |  |

### `credit_events.csv`

- **Rows:** 3
- **Grain:** One significant derogatory event.
- **Sensitivity:** Extreme.

Event type, anchor date, the basis for that anchor, and seasoning in months. The anchor basis is recorded because using the wrong one is the classic error.

| Column | Type | Description |
| --- | --- | --- |
| `credit_event_id` | string | Surrogate key. |
| `application_id` | string | Application surrogate key, format APP-nnnnnn. |
| `borrower_id` | string | Person surrogate key, format BORR-nnnnnn. |
| `event_type` | string | Significant derogatory event type. |
| `anchor_date` | date | The date seasoning is measured from. |
| `anchor_basis` | string | Which date that is for this event type. |
| `seasoning_months` | integer | Whole months from the anchor to the as-of date. |
| `status` | string |  |

### `credit_profiles.csv`

- **Rows:** 92
- **Grain:** One credit report snapshot per borrower.
- **Sensitivity:** Extreme.

Report metadata, all three scores, the representative score and the methodology rule. A score without its model is not comparable to a threshold.

| Column | Type | Description |
| --- | --- | --- |
| `credit_profile_id` | string | Surrogate key. |
| `application_id` | string | Application surrogate key, format APP-nnnnnn. |
| `borrower_id` | string | Person surrogate key, format BORR-nnnnnn. |
| `credit_file_token` | string | Tokenised credit-file identifier. |
| `credit_file_masked` | string | Display form, ****nnnn. |
| `report_date` | date |  |
| `report_age_days` | integer | Days from report date to the as-of date. |
| `bureau_vendor` | string |  |
| `score_model` | string | Required metadata: a score without its model is not comparable. |
| `score_1` | integer |  |
| `score_2` | integer |  |
| `score_3` | integer |  |
| `representative_score` | integer | Middle of three per borrower; lowest across borrowers. |
| `representative_score_rule_id` | string | Surrogate key. |
| `scoreable_tradelines` | integer | Below three routes to manual credit review. |
| `recent_inquiries_90d` | integer | Context for an explanation condition, never an adverse basis. |

### `decision_reasons.csv`

- **Rows:** 91
- **Grain:** One specific reason.
- **Sensitivity:** High.

The reason code, the rule, the policy version and the evidence reference. Adverse-action reasons must be specific and accurate, so a generic category is not acceptable here.

| Column | Type | Description |
| --- | --- | --- |
| `decision_reason_id` | string | Surrogate key. |
| `decision_id` | string | Surrogate key. |
| `application_id` | string | Application surrogate key, format APP-nnnnnn. |
| `reason_code` | string | Controlled adverse-action reason code. |
| `reason_text` | string | The specific reason, not a generic category. |
| `rule_id` | string | Stable rule identifier, citable in a decision. |
| `policy_id` | string | Policy family identifier. |
| `policy_version` | decimal | The version applied, selected by the as-of date. |
| `evidence_reference` | string | The fields the reason rests on. |

### `decisions.csv`

- **Rows:** 122
- **Grain:** One decision at one stage.
- **Sensitivity:** High.

The copilot's recommendation and, where human review is required, the pending human credit decision. An automated actor never appears on the credit-decision stage.

| Column | Type | Description |
| --- | --- | --- |
| `decision_id` | string | Surrogate key. |
| `application_id` | string | Application surrogate key, format APP-nnnnnn. |
| `decision_stage` | string | underwriting_recommendation | credit_decision. |
| `decision_type` | string | COPILOT_RECOMMENDATION | HUMAN_CREDIT_DECISION. |
| `result` | string | The computed value. |
| `actor_type` | string | AUTOMATED_COMPONENT | HUMAN. |
| `actor_id` | string | Surrogate key. |
| `decision_date` | date |  |
| `risk_level` | string |  |
| `eligibility_result` | string |  |
| `requires_human_review` | boolean | True where policy routes the file to a person. |

### `document_extractions.csv`

- **Rows:** 3898
- **Grain:** One extracted field.
- **Sensitivity:** High.

Field-level provenance: which document supplied which value, at what confidence. This is what makes lineage queryable below the record level.

| Column | Type | Description |
| --- | --- | --- |
| `extraction_id` | string | Surrogate key. |
| `document_id` | string | Surrogate key. |
| `application_id` | string | Application surrogate key, format APP-nnnnnn. |
| `field_name` | string |  |
| `extracted_value` | string |  |
| `page` | integer |  |
| `extraction_confidence` | decimal | Extraction confidence, 0 to 1. |

### `documents.csv`

- **Rows:** 1140
- **Grain:** One document instance.
- **Sensitivity:** High.

Metadata for every applicant document, including its trust class and whether it carries untrusted free text.

| Column | Type | Description |
| --- | --- | --- |
| `document_id` | string | Surrogate key. |
| `application_id` | string | Application surrogate key, format APP-nnnnnn. |
| `borrower_id` | string | Person surrogate key, format BORR-nnnnnn. |
| `document_type` | string | Document category. |
| `document_date` | date |  |
| `received_date` | date | Date the item reached the lender. |
| `issuer_type` | string |  |
| `source` | string |  |
| `verification_status` | string |  |
| `contains_pii` | boolean | True where the document carries personal data. |
| `masked` | boolean | True where sensitive values are rendered masked. |
| `tampering_indicator` | boolean | True where integrity signals were detected. |
| `trust_class` | string | customer_evidence | authoritative_evidence | internal_record. |
| `contains_untrusted_text` | boolean | True where the document carries applicant free text. |
| `is_stale` | boolean | True where the document sits outside its freshness window. |
| `relative_path` | string | Repository-relative path to the rendered artifact. |
| `expected_extracted_fields` | string | Fields an extraction component should recover. |
| `related_entities` | string |  |

### `eligibility_results.csv`

- **Rows:** 75
- **Grain:** One programme eligibility determination.
- **Sensitivity:** Decision.

Kept separate from the recommendation and from the credit decision, because eligible is not a synonym for approved.

| Column | Type | Description |
| --- | --- | --- |
| `eligibility_result_id` | string | Surrogate key. |
| `application_id` | string | Application surrogate key, format APP-nnnnnn. |
| `programme` | string |  |
| `result` | string | The computed value. |
| `determining_rule_ids` | string |  |
| `as_of_date` | date |  |

### `employment.csv`

- **Rows:** 181
- **Grain:** One employment episode.
- **Sensitivity:** High.

Employer, occupation, dates and tenure. Declared and verified start dates are separate columns so a verification conflict is expressible.

| Column | Type | Description |
| --- | --- | --- |
| `employment_id` | string | Surrogate key. |
| `application_id` | string | Application surrogate key, format APP-nnnnnn. |
| `borrower_id` | string | Person surrogate key, format BORR-nnnnnn. |
| `employer_name` | string |  |
| `occupation` | string |  |
| `employment_type` | string |  |
| `self_employed_flag` | boolean | True at 25 percent ownership or above. |
| `business_ownership_pct` | integer |  |
| `declared_start_date` | date | What the application stated. |
| `verified_start_date` | date | What the employer confirmed. Tenure is computed from this. |
| `end_date` | date |  |
| `is_current` | boolean |  |
| `tenure_months` | integer | Whole months from the verified start to the as-of date. |
| `pay_frequency` | string |  |

### `fraud_checks.csv`

- **Rows:** 2
- **Grain:** One integrity finding.
- **Sensitivity:** High.

Cross-source inconsistencies and document-integrity findings, each naming the two sources that disagree rather than asserting a score.

| Column | Type | Description |
| --- | --- | --- |
| `fraud_check_id` | string | Surrogate key. |
| `application_id` | string | Application surrogate key, format APP-nnnnnn. |
| `check_type` | string |  |
| `result` | string | The computed value. |
| `indicator` | string |  |
| `evidence_source_a` | string |  |
| `evidence_source_b` | string |  |
| `rule_id` | string | Stable rule identifier, citable in a decision. |
| `requires_human_review` | boolean | True where policy routes the file to a person. |

### `human_reviews.csv`

- **Rows:** 47
- **Grain:** One review event.
- **Sensitivity:** High.

Queue, trigger rules, reason code and reviewer role for every file that policy routes to a person.

| Column | Type | Description |
| --- | --- | --- |
| `human_review_id` | string | Surrogate key. |
| `application_id` | string | Application surrogate key, format APP-nnnnnn. |
| `queue` | string | Which human queue owns the file. |
| `trigger_rule_ids` | string |  |
| `reason_code` | string | Controlled adverse-action reason code. |
| `reason_text` | string | The specific reason, not a generic category. |
| `reviewer_role` | string | The role authorised to act on it. |
| `status` | string |  |
| `opened_date` | date |  |

### `income.csv`

- **Rows:** 99
- **Grain:** One income stream for one borrower.
- **Sensitivity:** High.

Declared, verified and qualifying amounts held separately, with the rule that produced the qualifying figure and the evidence types that support it.

| Column | Type | Description |
| --- | --- | --- |
| `income_id` | string | Surrogate key. |
| `application_id` | string | Application surrogate key, format APP-nnnnnn. |
| `borrower_id` | string | Person surrogate key, format BORR-nnnnnn. |
| `income_type` | string |  |
| `declared_monthly_amount` | decimal | What the applicant stated. Never used to qualify. |
| `verified_monthly_amount` | decimal | What the evidence established. |
| `qualifying_monthly_amount` | decimal | What policy permits. Never exceeds verified. |
| `annual_amount` | decimal |  |
| `qualifying_rule_id` | string | Surrogate key. |
| `evidence_document_types` | string |  |

### `insurance_records.csv`

- **Rows:** 77
- **Grain:** One policy or binder.
- **Sensitivity:** High.

Hazard and flood coverage with premiums that feed the housing expense.

| Column | Type | Description |
| --- | --- | --- |
| `insurance_record_id` | string | Surrogate key. |
| `application_id` | string | Application surrogate key, format APP-nnnnnn. |
| `coverage_type` | string |  |
| `carrier` | string |  |
| `annual_premium` | decimal |  |
| `coverage_amount` | decimal |  |
| `effective_date` | date |  |
| `evidenced` | boolean |  |
| `rule_id` | string | Stable rule identifier, citable in a decision. |

### `liabilities.csv`

- **Rows:** 300
- **Grain:** One obligation.
- **Sensitivity:** Extreme.

Every recurring obligation with its own inclusion decision and the rule id behind it. A single aggregated debt total would make the DTI unauditable.

| Column | Type | Description |
| --- | --- | --- |
| `liability_id` | string | Surrogate key. |
| `application_id` | string | Application surrogate key, format APP-nnnnnn. |
| `liability_type` | string |  |
| `creditor` | string |  |
| `balance` | decimal |  |
| `monthly_payment` | decimal | The payment the DTI numerator uses. |
| `remaining_term_months` | integer | Drives the ten-payment exclusion test. |
| `credit_limit` | decimal | Revolving limit; zero means no stated limit. |
| `include_in_dti` | boolean | The inclusion decision, with its rule in inclusion_rule_id. |
| `inclusion_rule_id` | string | Surrogate key. |
| `source` | string |  |

### `loans.csv`

- **Rows:** 75
- **Grain:** One requested loan.
- **Sensitivity:** Financial.

Product, amount, term, rate and every settlement component. The base loan amount and the note amount are separate because a financed programme premium changes the payment but not the leverage test.

| Column | Type | Description |
| --- | --- | --- |
| `loan_id` | string | Surrogate key. |
| `application_id` | string | Application surrogate key, format APP-nnnnnn. |
| `product_family` | string | conventional_conforming | jumbo | fha | va | usda. |
| `loan_purpose` | string | purchase | rate_term_refinance | cash_out_refinance. |
| `base_loan_amount` | decimal | The amount the leverage test measures. |
| `financed_premium_amount` | decimal | Programme premium financed into the note. |
| `note_amount` | decimal | Base loan plus financed premium; the amount that amortises. |
| `term_months` | integer | Loan term. |
| `interest_rate` | decimal | Annual nominal rate as a decimal. |
| `rate_type` | string |  |
| `lien_position` | integer |  |
| `amortisation_type` | string |  |
| `principal_and_interest` | decimal | Level payment from the note amount, rate and term. |
| `monthly_mortgage_insurance` | decimal | Enters the qualifying housing expense. |
| `down_payment_amount` | decimal | Purchase price less base loan amount. |
| `seller_credits` | decimal |  |
| `lender_credits` | integer |  |
| `closing_costs` | decimal | Borrower-paid costs; synthetic basis in AST-FTC-002. |
| `prepaids_and_escrow` | decimal | Tax and insurance escrow plus per-diem interest. |
| `earnest_money_paid` | decimal | Reduces funds required; sourced from a verified account. |
| `payoff_amount` | decimal | Lien retired by the new loan on a refinance. |
| `cash_out_proceeds` | decimal | Equity returned to the borrower. |

### `properties.csv`

- **Rows:** 75
- **Grain:** One collateral property.
- **Sensitivity:** High. Address data.

Address, type, units, occupancy, price, value and the value actually used for leverage - which is a different column on purpose.

| Column | Type | Description |
| --- | --- | --- |
| `property_id` | string | Surrogate key. |
| `application_id` | string | Application surrogate key, format APP-nnnnnn. |
| `street` | string |  |
| `city` | string |  |
| `state` | string |  |
| `postal_code` | integer |  |
| `property_type` | string |  |
| `units` | integer | USD | USD_PER_MONTH | RATIO | MONTHS | SCORE | MULTIPLE. |
| `occupancy_type` | string | primary_residence | second_home | investment. |
| `purchase_price` | decimal | Contract price; null on a refinance. |
| `appraised_value` | decimal | Appraised or otherwise accepted value. |
| `value_used_for_ltv` | decimal | Lower of price and value on a purchase; value on a refinance. |
| `valuation_method` | string | full_appraisal | value_acceptance. Not every loan has a report. |
| `annual_property_tax` | decimal | Annual amount; the housing expense uses one twelfth. |
| `annual_hazard_premium` | decimal | Annual amount; the housing expense uses one twelfth. |
| `monthly_hoa` | integer | Association dues. |
| `flood_zone` | string | Determination result. |
| `flood_zone_sfha` | boolean | True where the property sits in a special flood hazard area. |
| `ownership_months` | integer | Months since acquisition; drives cash-out seasoning. |

### `risk_flags.csv`

- **Rows:** 38
- **Grain:** One risk finding.
- **Sensitivity:** High.

Category, severity, the evidence behind it and the rule that raised it.

| Column | Type | Description |
| --- | --- | --- |
| `risk_flag_id` | string | Surrogate key. |
| `application_id` | string | Application surrogate key, format APP-nnnnnn. |
| `category` | string |  |
| `severity` | string | HARD_FAIL | CONDITIONAL | REFER | ADVISORY. |
| `detail` | string |  |
| `evidence` | string |  |
| `rule_id` | string | Stable rule identifier, citable in a decision. |
| `status` | string |  |

### `rule_evaluations.csv`

- **Rows:** 1827
- **Grain:** One rule applied to one application.
- **Sensitivity:** Decision.

The outcome, the observed value, the threshold it was compared against, the policy version in force, and the input fields consumed. This table is the spine of the audit trail.

| Column | Type | Description |
| --- | --- | --- |
| `evaluation_id` | string | Surrogate key. |
| `application_id` | string | Application surrogate key, format APP-nnnnnn. |
| `rule_id` | string | Stable rule identifier, citable in a decision. |
| `policy_id` | string | Policy family identifier. |
| `policy_version` | decimal | The version applied, selected by the as-of date. |
| `policy_effective_date` | date | Start of that version's effective window. |
| `source_category` | string | Authority layer for the rule. |
| `severity` | string | HARD_FAIL | CONDITIONAL | REFER | ADVISORY. |
| `outcome` | string | PASS | FAIL | REFER | NOT_APPLICABLE | INDETERMINATE. |
| `observed_value` | string | The value measured. |
| `comparator` | string | The comparison applied. |
| `threshold_value` | string | The value it was measured against. |
| `input_fields` | string | The fields consumed, for lineage. |
| `requires_human_review` | boolean | True where policy routes the file to a person. |
| `reason` | string | Why the rule produced this outcome, in full. |

### `scenario_assignments.csv`

- **Rows:** 75
- **Grain:** One application's scenario mapping.
- **Sensitivity:** Low.

Which scenario produced this application and what it is meant to exercise.

| Column | Type | Description |
| --- | --- | --- |
| `application_id` | string | Application surrogate key, format APP-nnnnnn. |
| `scenario_id` | string | The scenario that produced this row. |
| `scenario_name` | string |  |
| `security_test_type` | string |  |
| `expected_recommendation` | string |  |
| `expected_human_review` | boolean |  |

### `security_events.csv`

- **Rows:** 6
- **Grain:** One security detection.
- **Sensitivity:** High.

Injection, extraction, cross-customer and out-of-scope attempts, with a masked excerpt and the action taken. Blocked attempts are recorded exactly as successful ones would be.

| Column | Type | Description |
| --- | --- | --- |
| `security_event_id` | string | Surrogate key. |
| `application_id` | string | Application surrogate key, format APP-nnnnnn. |
| `event_type` | string | Significant derogatory event type. |
| `detected_in` | string |  |
| `masked_excerpt` | string | Triggering content, masked. |
| `action_taken` | string | What the control did. |
| `rule_id` | string | Stable rule identifier, citable in a decision. |
| `detected_at` | date |  |

### `title_records.csv`

- **Rows:** 75
- **Grain:** One title commitment.
- **Sensitivity:** High.

Lien position, vesting and exceptions, with the blocking flag the clear-to-close gate reads.

| Column | Type | Description |
| --- | --- | --- |
| `title_record_id` | string | Surrogate key. |
| `application_id` | string | Application surrogate key, format APP-nnnnnn. |
| `commitment_date` | date |  |
| `required_lien_position` | integer |  |
| `vesting_matches_borrowers` | boolean |  |
| `exception_count` | integer |  |
| `blocking_exception` | boolean |  |
| `exception_summary` | string |  |
| `rule_id` | string | Stable rule identifier, citable in a decision. |

### `underwriting_calculations.csv`

- **Rows:** 1650
- **Grain:** One calculated feature per application.
- **Sensitivity:** Derived.

Every derived number with its inputs, formula version, units and expected interpretation. Nothing here was produced by a language model.

| Column | Type | Description |
| --- | --- | --- |
| `calculation_id` | string | Surrogate key. |
| `application_id` | string | Application surrogate key, format APP-nnnnnn. |
| `calculation_name` | string | The derived feature. |
| `input_fields` | string | The fields consumed, for lineage. |
| `formula_version` | string | Version of the expression that produced the result. |
| `result` | decimal | The computed value. |
| `units` | string | USD | USD_PER_MONTH | RATIO | MONTHS | SCORE | MULTIPLE. |
| `calculated_at` | date |  |
| `policy_context` | string | The policy this calculation feeds. |
| `expected_interpretation` | string | How the value should be read. |

### `verifications.csv`

- **Rows:** 375
- **Grain:** One third-party check.
- **Sensitivity:** High.

Identity, employment, income, asset and flood verifications with provider, dates and result.

| Column | Type | Description |
| --- | --- | --- |
| `verification_id` | string | Surrogate key. |
| `application_id` | string | Application surrogate key, format APP-nnnnnn. |
| `borrower_id` | string | Person surrogate key, format BORR-nnnnnn. |
| `category` | string |  |
| `provider` | string |  |
| `requested_date` | date |  |
| `completed_date` | date |  |
| `result` | string | The computed value. |
| `rule_id` | string | Stable rule identifier, citable in a decision. |

## `synthetic_data/mortgage/policy_metadata/`

### `policies.csv`

- **Rows:** 42
- **Grain:** One policy version.
- **Sensitivity:** None. No customer data.

Front-matter metadata for every document in the corpus, including its effective window and its content hash.

| Column | Type | Description |
| --- | --- | --- |
| `policy_document_id` | string | Surrogate key. |
| `policy_id` | string | Policy family identifier. |
| `version` | decimal |  |
| `title` | string |  |
| `family` | string |  |
| `effective_date` | date |  |
| `expiration_date` | date |  |
| `source_category` | string | Authority layer for the rule. |
| `priority` | integer |  |
| `supersedes` | string |  |
| `superseded_by` | string |  |
| `requires_human_review` | boolean | True where policy routes the file to a person. |
| `jurisdiction` | string |  |
| `product_scope` | string |  |
| `occupancy_scope` | string |  |
| `purpose_scope` | string |  |
| `rule_count` | integer |  |
| `relative_path` | string | Repository-relative path to the rendered artifact. |
| `document_hash` | string |  |

### `policy_rules.csv`

- **Rows:** 203
- **Grain:** One rule in one policy version.
- **Sensitivity:** None.

The addressable rule catalogue: identifier, authority, severity, outcome type and parameters, per version.

| Column | Type | Description |
| --- | --- | --- |
| `rule_id` | string | Stable rule identifier, citable in a decision. |
| `policy_id` | string | Policy family identifier. |
| `policy_version` | decimal | The version applied, selected by the as-of date. |
| `policy_effective_date` | date | Start of that version's effective window. |
| `policy_expiration_date` | date |  |
| `title` | string |  |
| `source_category` | string | Authority layer for the rule. |
| `severity` | string | HARD_FAIL | CONDITIONAL | REFER | ADVISORY. |
| `outcome_type` | string |  |
| `requires_human_review` | boolean | True where policy routes the file to a person. |
| `parameters` | string |  |
| `has_research_reference` | boolean |  |
| `cross_refs` | string |  |

## Totals

- **Tables:** 34
- **Rows:** 12336
