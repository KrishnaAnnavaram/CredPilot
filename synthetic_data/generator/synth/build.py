"""
Application builder.

Turns a :class:`ScenarioSpec` into a fully reconciled set of entity rows.

The method is: pick the transaction shape, compute the housing expense from it,
then *solve backwards* for the borrower facts that hit the scenario's targets
exactly, then run the deterministic rules engine over the result. Nothing is drawn
at random and then labelled after the fact: the liabilities are solved so the
debt-to-income ratio lands on its target to the cent, the assets are solved so the
post-closing reserve figure lands on its target, and the documents are rendered from
the same values the tables carry.

Where a scenario calls for a discrepancy, exactly one value is moved and the
intended mismatch is recorded in the scenario's ground truth. Everything else still
reconciles.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from random import Random
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import synthetic_data_utils as u  # noqa: E402
from synthetic_data_utils import money, ratio  # noqa: E402

from .people import BANKS, BROKERAGES, CREDITORS, Person, account_identifiers  # noqa: E402
from .policies import param  # noqa: E402
from .rules_engine import (  # noqa: E402
    Engine,
    Facts,
    eligibility_result,
    recommendation,
    requires_human_review,
    risk_level,
)
from .scenarios import ScenarioSpec  # noqa: E402

ZERO = Decimal("0")

PRICE_BANDS = {
    "low": (180_000, 290_000),
    "mid": (380_000, 560_000),
    "high": (620_000, 790_000),
    "jumbo": (1_300_000, 1_700_000),
    "jumbo_xl": (1_900_000, 2_400_000),
}

#: Effective annual property-tax rate by state. Public geography-level reference
#: points chosen for spread, applied as a synthetic modelling assumption.
TAX_RATES = {
    "TX": Decimal("0.0181"), "IL": Decimal("0.0208"), "AZ": Decimal("0.0063"),
    "NC": Decimal("0.0078"), "WA": Decimal("0.0092"), "KS": Decimal("0.0141"),
    "TN": Decimal("0.0066"), "OR": Decimal("0.0097"), "GA": Decimal("0.0092"),
    "CO": Decimal("0.0055"), "NH": Decimal("0.0209"), "RI": Decimal("0.0140"),
    "MI": Decimal("0.0154"), "CA": Decimal("0.0073"), "FL": Decimal("0.0089"),
}
DEFAULT_TAX_RATE = Decimal("0.0110")

HAZARD_RATE = Decimal("0.0035")        # annual premium as a share of value
FLOOD_RATE = Decimal("0.0012")
REVOLVING_MIN_PAYMENT_RATE = Decimal("0.03")
CONSUMER_DEBT_RATE = Decimal("0.0699")  # rate used to price a liability balance


@dataclass
class BuiltApplication:
    """Every row produced for one scenario, ready to be written out."""

    scenario: ScenarioSpec
    application: dict[str, Any]
    borrowers: list[Person]
    application_borrowers: list[dict[str, Any]]
    loan: dict[str, Any]
    prop: dict[str, Any]
    appraisal: dict[str, Any] | None
    employments: list[dict[str, Any]] = field(default_factory=list)
    income_sources: list[dict[str, Any]] = field(default_factory=list)
    income_history: list[dict[str, Any]] = field(default_factory=list)
    assets: list[dict[str, Any]] = field(default_factory=list)
    asset_transactions: list[dict[str, Any]] = field(default_factory=list)
    liabilities: list[dict[str, Any]] = field(default_factory=list)
    credit_profiles: list[dict[str, Any]] = field(default_factory=list)
    credit_accounts: list[dict[str, Any]] = field(default_factory=list)
    credit_events: list[dict[str, Any]] = field(default_factory=list)
    verifications: list[dict[str, Any]] = field(default_factory=list)
    title_records: list[dict[str, Any]] = field(default_factory=list)
    insurance_records: list[dict[str, Any]] = field(default_factory=list)
    calculations: list[dict[str, Any]] = field(default_factory=list)
    facts: Facts | None = None
    engine_result: Any = None
    derived: dict[str, Any] = field(default_factory=dict)


class ApplicationBuilder:
    def __init__(self, engine: Engine, registry: dict[str, Any], seed: int) -> None:
        self.engine = engine
        self.registry = registry
        self.seed = seed
        self._asset_seq = 0
        self._account_seq = 0

    # -- entry point ------------------------------------------------------

    def build(
        self,
        spec: ScenarioSpec,
        app_number: int,
        primary: Person,
        co_borrower: Person | None,
    ) -> BuiltApplication:
        rng = u.sub_rng(self.seed, f"app:{spec.scenario_id}")
        app_id = u.application_id(app_number)
        as_of = spec.as_of

        shape = self._transaction_shape(spec, rng, primary)
        housing = self._housing_expense(spec, shape, as_of)
        income = self._solve_income(spec, housing["pitia"], primary, co_borrower)
        liabilities = self._solve_liabilities(
            spec, rng, income["qualifying_monthly_income"], housing["pitia"], app_id
        )
        settlement = self._settlement(spec, shape, housing, rng)
        assets = self._solve_assets(
            spec, rng, settlement, housing["pitia"], income["qualifying_monthly_income"],
            app_id, primary,
        )
        credit = self._credit(spec, rng, primary, co_borrower, liabilities, as_of, app_id)

        derived = self._derive(
            spec, shape, housing, income, liabilities, settlement, assets, credit, as_of
        )
        facts = self._facts(
            spec, app_id, shape, housing, income, liabilities, settlement, assets,
            credit, derived, as_of,
        )
        result = self.engine.evaluate(facts)

        built = BuiltApplication(
            scenario=spec,
            application=self._application_row(spec, app_id, as_of, primary, co_borrower),
            borrowers=[p for p in (primary, co_borrower) if p is not None],
            application_borrowers=self._application_borrowers(app_id, primary, co_borrower),
            loan=self._loan_row(spec, app_id, shape, housing, settlement),
            prop=self._property_row(spec, app_id, shape, housing, primary),
            appraisal=self._appraisal_row(spec, app_id, shape, as_of),
            employments=self._employment_rows(spec, app_id, primary, co_borrower, as_of),
            income_sources=income["sources"],
            income_history=income["history"],
            assets=assets["rows"],
            asset_transactions=assets["transactions"],
            liabilities=liabilities["rows"],
            credit_profiles=credit["profiles"],
            credit_accounts=credit["accounts"],
            credit_events=credit["events"],
            verifications=self._verification_rows(spec, app_id, primary, as_of),
            title_records=self._title_rows(spec, app_id, as_of),
            insurance_records=self._insurance_rows(spec, app_id, shape, housing, as_of),
            facts=facts,
            engine_result=result,
            derived=derived,
        )
        built.calculations = self._calculation_rows(app_id, as_of, derived, facts)
        return built

    # -- transaction shape ------------------------------------------------

    def _transaction_shape(
        self, spec: ScenarioSpec, rng: Random, primary: Person
    ) -> dict[str, Any]:
        if spec.price_override:
            price = money(spec.price_override)
        else:
            low, high = PRICE_BANDS[spec.price_band]
            price = money(rng.randrange(low, high + 1, 10_000))

        target_ltv = spec.as_decimal("target_ltv")
        appraised = money(price * spec.as_decimal("appraised_value_factor"))

        if spec.purpose == "purchase":
            value_used = money(min(price, appraised))
            purchase_price: Decimal | None = price
        else:
            value_used = appraised
            purchase_price = None

        base_loan = money(value_used * target_ltv)

        # Government programmes finance an up-front premium on top of the base loan.
        financed_premium = ZERO
        if spec.product == "fha":
            pct = Decimal(str(param(
                self.registry, "FHA-OVL-003", "upfront_premium_pct_of_base_loan", spec.as_of
            )))
            financed_premium = money(base_loan * pct)
        elif spec.product == "va":
            pct = Decimal(str(param(
                self.registry, "VA-OVL-002", "funding_fee_pct_financed", spec.as_of
            )))
            financed_premium = money(base_loan * pct)
        elif spec.product == "usda":
            pct = Decimal(str(param(
                self.registry, "USD-OVL-003", "upfront_guarantee_fee_pct", spec.as_of
            )))
            financed_premium = money(base_loan * pct)

        note_amount = money(base_loan + financed_premium)
        return {
            "purchase_price": purchase_price,
            "appraised_value": appraised,
            "value_used": value_used,
            "base_loan_amount": base_loan,
            "financed_premium": financed_premium,
            "note_amount": note_amount,
            "ltv": u.ltv(base_loan, value_used),
            "state": primary.state,
            "rate": spec.as_decimal("rate"),
            "term_months": spec.term_months,
        }

    # -- housing expense --------------------------------------------------

    def _housing_expense(
        self, spec: ScenarioSpec, shape: dict[str, Any], as_of: date
    ) -> dict[str, Any]:
        pi = u.principal_and_interest(
            shape["note_amount"], shape["rate"], shape["term_months"]
        )
        tax_rate = TAX_RATES.get(shape["state"], DEFAULT_TAX_RATE)
        monthly_tax = money(shape["value_used"] * tax_rate / 12)
        monthly_hazard = money(shape["value_used"] * HAZARD_RATE / 12)
        monthly_hoa = (
            money(Decimal("285"))
            if spec.property_type in ("condominium", "planned_unit_development")
            else ZERO
        )
        monthly_flood = (
            money(shape["value_used"] * FLOOD_RATE / 12) if spec.flood_zone_sfha else ZERO
        )
        monthly_mi = self._mortgage_insurance(spec, shape, as_of)

        pitia = u.housing_expense_pitia(
            pi, monthly_tax, monthly_hazard, monthly_hoa, monthly_mi, monthly_flood
        )
        return {
            "principal_interest": pi,
            "monthly_property_tax": monthly_tax,
            "monthly_hazard_insurance": monthly_hazard,
            "monthly_hoa": monthly_hoa,
            "monthly_flood_insurance": monthly_flood,
            "monthly_mortgage_insurance": monthly_mi,
            "pitia": pitia,
            "annual_tax_rate": tax_rate,
        }

    def _mortgage_insurance(
        self, spec: ScenarioSpec, shape: dict[str, Any], as_of: date
    ) -> Decimal:
        ltv = shape["ltv"] or ZERO
        if spec.product == "va":
            return ZERO  # VA-OVL-002: no monthly mortgage insurance.
        if spec.product == "fha":
            pct = Decimal(str(param(
                self.registry, "FHA-OVL-003", "annual_premium_pct_of_loan", as_of
            )))
            return money(shape["note_amount"] * pct / 12)
        if spec.product == "usda":
            pct = Decimal(str(param(
                self.registry, "USD-OVL-003", "annual_fee_pct_of_loan", as_of
            )))
            return money(shape["note_amount"] * pct / 12)
        if ltv <= Decimal("0.80"):
            return ZERO
        if ltv <= Decimal("0.85"):
            key = "annual_factor_ltv_80_to_85"
        elif ltv <= Decimal("0.90"):
            key = "annual_factor_ltv_85_to_90"
        elif ltv <= Decimal("0.95"):
            key = "annual_factor_ltv_90_to_95"
        else:
            key = "annual_factor_ltv_above_95"
        factor = Decimal(str(param(self.registry, "CONV-PUR-003", key, as_of)))
        return money(shape["base_loan_amount"] * factor / 12)

    # -- income -----------------------------------------------------------

    def _solve_income(
        self, spec: ScenarioSpec, pitia: Decimal, primary: Person,
        co: Person | None,
    ) -> dict[str, Any]:
        """Solve qualifying monthly income from the housing-ratio target.

        The housing ratio is clamped so it always leaves room for the non-housing
        debt the DTI target implies; otherwise a scenario asking for a low DTI and a
        high housing ratio would need negative liabilities.
        """
        target_dti = spec.as_decimal("target_back_end_dti")
        housing_ratio = min(
            spec.as_decimal("housing_ratio_target"), target_dti - Decimal("0.02")
        )
        if housing_ratio <= 0:
            housing_ratio = target_dti * Decimal("0.80")

        qmi_raw = pitia / housing_ratio
        # Round the annual figure to a realistic salary-like number, then take the
        # exact monthly value back off it so income and salary always reconcile.
        annual = (qmi_raw * 12).quantize(Decimal("1"))
        annual = (annual / Decimal(100)).quantize(Decimal("1")) * Decimal(100)
        qmi = money(annual / 12)

        sources: list[dict[str, Any]] = []
        history: list[dict[str, Any]] = []
        profile = spec.income_profile
        shares = self._income_shares(profile)
        allocated = ZERO
        for idx, (kind, share) in enumerate(zip(profile, shares)):
            last = idx == len(profile) - 1
            amount = money(qmi - allocated) if last else money(qmi * share)
            allocated = money(allocated + amount)
            sources.append(
                {
                    "borrower_id": primary.borrower_id,
                    "income_type": kind,
                    "qualifying_monthly_amount": amount,
                    "verified_monthly_amount": amount,
                    "declared_monthly_amount": amount,
                    "annual_amount": money(amount * 12),
                }
            )

        if co is not None:
            # A joint application has two earners. The largest component is split
            # between them rather than being recorded as one borrower's income, so
            # the income table, the employment table and the paystubs all agree on
            # who earns what. The split is exact to the cent: the co-borrower's row
            # takes the remainder so the two still sum to qualifying income.
            sources.sort(key=lambda s: s["qualifying_monthly_amount"], reverse=True)
            largest = sources[0]
            total = largest["qualifying_monthly_amount"]
            primary_share = money(total * Decimal("0.58"))
            co_share = money(total - primary_share)
            largest["qualifying_monthly_amount"] = primary_share
            largest["verified_monthly_amount"] = primary_share
            largest["declared_monthly_amount"] = primary_share
            largest["annual_amount"] = money(primary_share * 12)
            sources.append(
                {
                    "borrower_id": co.borrower_id,
                    "income_type": largest["income_type"],
                    "qualifying_monthly_amount": co_share,
                    "verified_monthly_amount": co_share,
                    "declared_monthly_amount": co_share,
                    "annual_amount": money(co_share * 12),
                }
            )
        # One controlled discrepancy: the application overstates income.
        if spec.income_conflict_variance:
            variance = spec.as_decimal("income_conflict_variance")
            target = next(
                s for s in sources if s["borrower_id"] == primary.borrower_id
            )
            target["declared_monthly_amount"] = money(
                target["verified_monthly_amount"] * (Decimal(1) + variance)
            )
        return {
            "qualifying_monthly_income": qmi,
            "qualifying_annual_income": money(qmi * 12),
            "sources": sources,
            "history": history,
            "housing_ratio_used": housing_ratio,
        }

    @staticmethod
    def _income_shares(profile: tuple[str, ...]) -> list[Decimal]:
        weights = {
            "salaried": Decimal("1.00"), "hourly_variable": Decimal("1.00"),
            "self_employed": Decimal("1.00"), "bonus": Decimal("0.12"),
            "overtime": Decimal("0.10"), "commission": Decimal("0.30"),
            "rental": Decimal("0.18"), "rental_negative": Decimal("-0.12"),
            "retirement": Decimal("0.60"), "social_security": Decimal("0.40"),
        }
        raw = [weights.get(k, Decimal("0.20")) for k in profile]
        total = sum(raw)
        if total <= 0:
            return [Decimal(1) / Decimal(len(profile))] * len(profile)
        return [w / total for w in raw]

    # -- liabilities ------------------------------------------------------

    def _solve_liabilities(
        self, spec: ScenarioSpec, rng: Random, qmi: Decimal, pitia: Decimal, app_id: str
    ) -> dict[str, Any]:
        """Solve the recurring obligations that land back-end DTI on its target."""
        target_dti = spec.as_decimal("target_back_end_dti")
        total_other = money(target_dti * qmi - pitia)
        if total_other < 0:
            total_other = ZERO

        plan = [
            ("auto_loan", Decimal("0.34"), 48),
            ("student_loan", Decimal("0.26"), 96),
            ("revolving_credit_card", Decimal("0.24"), 0),
            ("installment_personal", Decimal("0.16"), 36),
        ]
        rows: list[dict[str, Any]] = []
        allocated = ZERO
        util_target = spec.as_decimal("revolving_utilization")
        for idx, (kind, share, term) in enumerate(plan):
            last = idx == len(plan) - 1
            payment = money(total_other - allocated) if last else money(total_other * share)
            if payment <= 0:
                continue
            allocated = money(allocated + payment)
            if kind == "revolving_credit_card":
                balance = money(payment / REVOLVING_MIN_PAYMENT_RATE)
                limit = money(balance / util_target) if util_target > 0 else ZERO
                remaining_term = None
            else:
                balance = _present_value(payment, CONSUMER_DEBT_RATE, term)
                limit = ZERO
                remaining_term = term
            rows.append(
                {
                    "liability_id": f"{app_id}-LIA-{len(rows) + 1:02d}",
                    "application_id": app_id,
                    "liability_type": kind,
                    "creditor": CREDITORS[rng.randrange(len(CREDITORS))],
                    "balance": balance,
                    "monthly_payment": payment,
                    "remaining_term_months": remaining_term,
                    "credit_limit": limit,
                    "include_in_dti": True,
                    "inclusion_rule_id": (
                        "LIA-INC-003" if kind == "revolving_credit_card" else "LIA-INC-001"
                    ),
                    "source": "credit_report",
                }
            )
        # An obligation the credit report shows but the application omitted.
        if spec.undeclared_liability and rows:
            rows[-1]["source"] = "credit_report_only"
            rows[-1]["inclusion_rule_id"] = "LIA-INC-006"
        return {
            "rows": rows,
            "total_monthly_payments": allocated,
        }

    # -- settlement -------------------------------------------------------

    def _settlement(
        self, spec: ScenarioSpec, shape: dict[str, Any], housing: dict[str, Any],
        rng: Random,
    ) -> dict[str, Any]:
        as_of = spec.as_of
        origination = Decimal(str(param(
            self.registry, "AST-FTC-002", "origination_fixed_component", as_of
        )))
        third_party_pct = Decimal(str(param(
            self.registry, "AST-FTC-002", "third_party_cost_pct_of_loan", as_of
        )))
        tax_months = int(param(self.registry, "AST-FTC-002", "tax_escrow_months", as_of))
        hazard_months = int(param(
            self.registry, "AST-FTC-002", "hazard_escrow_months", as_of
        ))
        interest_days = int(param(
            self.registry, "AST-FTC-002", "prepaid_interest_days", as_of
        ))

        closing_costs = money(origination + shape["note_amount"] * third_party_pct)
        prepaids = money(
            housing["monthly_property_tax"] * tax_months
            + housing["monthly_hazard_insurance"] * hazard_months
            + shape["note_amount"] * shape["rate"] / Decimal(365) * interest_days
        )

        if spec.purpose == "purchase":
            down_payment = u.down_payment_amount(
                shape["purchase_price"], shape["base_loan_amount"]
            )
            earnest_money = money(shape["purchase_price"] * Decimal("0.01"))
            seller_credits = (
                money(shape["purchase_price"] * Decimal("0.02"))
                if rng.random() < 0.3
                else ZERO
            )
            required = u.cash_to_close(
                down_payment=down_payment,
                closing_costs=closing_costs,
                prepaids_and_escrow=prepaids,
                seller_credits=seller_credits,
                earnest_money_paid=earnest_money,
            )
            payoff = ZERO
            cash_out = ZERO
        else:
            down_payment = ZERO
            earnest_money = ZERO
            seller_credits = ZERO
            payoff = money(shape["base_loan_amount"] * Decimal("0.82"))
            if spec.purpose == "cash_out_refinance":
                cash_out = money(
                    shape["base_loan_amount"] - payoff - closing_costs - prepaids
                )
                required = ZERO
            else:
                cash_out = ZERO
                required = u.cash_to_close(
                    down_payment=ZERO,
                    closing_costs=closing_costs,
                    prepaids_and_escrow=prepaids,
                )
        return {
            "down_payment": down_payment,
            "closing_costs": closing_costs,
            "prepaids": prepaids,
            "seller_credits": seller_credits,
            "lender_credits": ZERO,
            "earnest_money": earnest_money,
            "payoff_amount": payoff,
            "cash_out_proceeds": cash_out,
            "funds_required": money(max(ZERO, required)),
        }

    # -- assets -----------------------------------------------------------

    def _solve_assets(
        self, spec: ScenarioSpec, rng: Random, settlement: dict[str, Any],
        pitia: Decimal, qmi: Decimal, app_id: str, primary: Person,
    ) -> dict[str, Any]:
        """Solve the asset ledger so the post-closing reserve figure hits its target."""
        required = settlement["funds_required"]
        gift = money(spec.gift_amount)
        target_reserves = money(spec.as_decimal("target_reserves_months") * pitia)

        needed_from_reserve_tier = money(max(ZERO, required - gift))
        if spec.assets_posture == "short":
            # Deliberately leave the file unable to close.
            needed_from_reserve_tier = money(needed_from_reserve_tier * Decimal("0.72"))
            target_reserves = ZERO
        reserve_pool = money(needed_from_reserve_tier + target_reserves)

        brokerage_reserve = ZERO
        retirement_reserve = ZERO
        if spec.assets_posture == "ample" and target_reserves > 0:
            brokerage_reserve = money(target_reserves * Decimal("0.25"))
            retirement_reserve = money(target_reserves * Decimal("0.20"))
        liquid_reserve = money(reserve_pool - brokerage_reserve - retirement_reserve)
        checking = money(liquid_reserve * Decimal("0.35"))
        savings = money(liquid_reserve - checking)

        rows: list[dict[str, Any]] = []
        transactions: list[dict[str, Any]] = []

        def add(
            asset_type: str, institution: str, verified: Decimal,
            close_amt: Decimal, reserve_amt: Decimal, haircut: Decimal,
        ) -> dict[str, Any]:
            self._asset_seq += 1
            self._account_seq += 1
            token, masked = account_identifiers(self._account_seq)
            row = {
                "asset_id": f"{app_id}-AST-{len(rows) + 1:02d}",
                "application_id": app_id,
                "borrower_id": primary.borrower_id,
                "asset_type": asset_type,
                "institution": institution,
                "account_token": token,
                "account_masked": masked,
                "declared_balance": verified,
                "verified_balance": verified,
                "eligible_close_amount": close_amt,
                "eligible_reserve_amount": reserve_amt,
                "liquidity_haircut": haircut,
                "eligibility_rule_id": "AST-ELG-001",
            }
            rows.append(row)
            return row

        bank = BANKS[rng.randrange(len(BANKS))]
        checking_row = add(
            "checking", bank, checking, checking, checking, Decimal("0.00")
        )
        add("savings", bank, savings, savings, savings, Decimal("0.00"))
        if brokerage_reserve > 0:
            bal = money(brokerage_reserve / Decimal("0.80"))
            add(
                "brokerage", BROKERAGES[rng.randrange(len(BROKERAGES))], bal,
                brokerage_reserve, brokerage_reserve, Decimal("0.20"),
            )
        if retirement_reserve > 0:
            bal = money(retirement_reserve / Decimal("0.60"))
            # Retirement is reserve-eligible but not available at closing.
            add("retirement", "Meridian Retirement Trust", bal, ZERO,
                retirement_reserve, Decimal("0.40"))
        if gift > 0:
            # AST-SRC-001 bars gifts on investment property. An ineligible gift is not
            # "a gift with a warning" - it is money that cannot be brought to
            # settlement, so it contributes nothing to available funds and the
            # shortfall that follows is the real consequence.
            gift_eligible = spec.occupancy != "investment"
            add(
                "gift_funds", bank, gift, gift if gift_eligible else ZERO, ZERO,
                Decimal("0.00"),
            )
            if not gift_eligible:
                rows[-1]["eligibility_rule_id"] = "AST-SRC-001"

        # Earnest money already paid leaves the checking account.
        if settlement["earnest_money"] > 0:
            transactions.append(
                {
                    "transaction_id": f"{app_id}-TXN-EMD",
                    "application_id": app_id,
                    "asset_id": checking_row["asset_id"],
                    "transaction_type": "withdrawal",
                    "amount": settlement["earnest_money"],
                    "transaction_date": spec.as_of - timedelta(days=21),
                    "description": "Earnest money deposit to settlement agent",
                    "source_status": "SOURCED",
                    "large_deposit_flag": False,
                }
            )

        # An unsourced deposit inflates the stated balance but not the eligible amount.
        unsourced = money(spec.as_decimal("unsourced_deposit_factor") * qmi)
        if unsourced > 0:
            checking_row["declared_balance"] = money(
                checking_row["declared_balance"] + unsourced
            )
            checking_row["verified_balance"] = money(
                checking_row["verified_balance"] + unsourced
            )
            transactions.append(
                {
                    "transaction_id": f"{app_id}-TXN-DEP",
                    "application_id": app_id,
                    "asset_id": checking_row["asset_id"],
                    "transaction_type": "deposit",
                    "amount": unsourced,
                    "transaction_date": spec.as_of - timedelta(days=17),
                    "description": "Incoming transfer, originator not identified",
                    "source_status": "UNSOURCED",
                    "large_deposit_flag": True,
                }
            )

        draw = u.draw_funds_to_close(required, rows)
        return {
            "rows": rows,
            "transactions": transactions,
            "draw": draw,
            "gift_amount": gift,
            "unsourced_deposit": unsourced,
        }

    # -- credit -----------------------------------------------------------

    def _credit(
        self, spec: ScenarioSpec, rng: Random, primary: Person, co: Person | None,
        liabilities: dict[str, Any], as_of: date, app_id: str,
    ) -> dict[str, Any]:
        report_date = as_of - timedelta(days=spec.credit_report_age_days)
        profiles: list[dict[str, Any]] = []
        for person, target in ((primary, spec.credit_score), (co, spec.co_borrower_score)):
            if person is None:
                continue
            score = target if target is not None else spec.credit_score
            # Three bureau-style scores whose middle value is the target, so the
            # representative-score methodology is actually exercised.
            scores = sorted([score - rng.randint(4, 14), score, score + rng.randint(3, 12)])
            rep = u.representative_credit_score(scores)
            profiles.append(
                {
                    "credit_profile_id": f"{app_id}-CRP-{len(profiles) + 1}",
                    "application_id": app_id,
                    "borrower_id": person.borrower_id,
                    "credit_file_token": person.credit_file_token,
                    "credit_file_masked": person.credit_file_masked,
                    "report_date": report_date,
                    "report_age_days": spec.credit_report_age_days,
                    "bureau_vendor": "SYNTH-TRIMERGE",
                    "score_model": "SYNTH-SCORE-4",
                    "score_1": scores[0],
                    "score_2": scores[1],
                    "score_3": scores[2],
                    "representative_score": rep,
                    "representative_score_rule_id": "CRD-SCR-002",
                    "scoreable_tradelines": spec.scoreable_tradelines,
                    "recent_inquiries_90d": spec.recent_inquiries_90d,
                }
            )

        accounts: list[dict[str, Any]] = []
        for lia in liabilities["rows"]:
            accounts.append(
                {
                    "credit_account_id": lia["liability_id"].replace("LIA", "TRD"),
                    "application_id": app_id,
                    "borrower_id": primary.borrower_id,
                    "liability_id": lia["liability_id"],
                    "account_type": lia["liability_type"],
                    "creditor": lia["creditor"],
                    "balance": lia["balance"],
                    "credit_limit": lia["credit_limit"],
                    "monthly_payment": lia["monthly_payment"],
                    "opened_date": as_of - timedelta(days=rng.randint(400, 3200)),
                    "account_status": "open",
                    "lates_30d_24m": 0,
                    "lates_60d_24m": 0,
                    "lates_90d_24m": 0,
                    "dispute_flag": False,
                }
            )
        # Spread the declared delinquency pattern across the real tradelines.
        for i in range(min(spec.nonhousing_accounts_30d_24m, len(accounts))):
            accounts[i]["lates_30d_24m"] = 1
        if spec.any_90d_24m and accounts:
            accounts[0]["lates_90d_24m"] = 1

        if spec.collection_total and money(spec.collection_total) > 0:
            accounts.append(
                {
                    "credit_account_id": f"{app_id}-TRD-COL",
                    "application_id": app_id,
                    "borrower_id": primary.borrower_id,
                    "liability_id": None,
                    "account_type": "collection",
                    "creditor": CREDITORS[rng.randrange(len(CREDITORS))],
                    "balance": money(spec.collection_total),
                    "credit_limit": ZERO,
                    "monthly_payment": ZERO,
                    "opened_date": as_of - timedelta(days=rng.randint(500, 1400)),
                    "account_status": "collection",
                    "lates_30d_24m": 0,
                    "lates_60d_24m": 0,
                    "lates_90d_24m": 0,
                    "dispute_flag": False,
                }
            )

        events: list[dict[str, Any]] = []
        for idx, ev in enumerate(spec.credit_events):
            anchor = u.add_months(as_of, -int(ev["months_ago"]))
            events.append(
                {
                    "credit_event_id": f"{app_id}-EVT-{idx + 1}",
                    "application_id": app_id,
                    "borrower_id": primary.borrower_id,
                    "event_type": ev["event_type"],
                    "anchor_date": anchor,
                    "anchor_basis": (
                        "discharge or dismissal date"
                        if "bankruptcy" in ev["event_type"]
                        else "completion or title transfer date"
                    ),
                    "seasoning_months": u.derogatory_seasoning_months(anchor, as_of),
                    "status": "resolved",
                }
            )

        revolving_balance = sum(
            (a["balance"] for a in accounts if a["account_type"] == "revolving_credit_card"),
            ZERO,
        )
        revolving_limit = sum(
            (
                a["credit_limit"]
                for a in accounts
                if a["account_type"] == "revolving_credit_card" and a["credit_limit"] > 0
            ),
            ZERO,
        )
        return {
            "profiles": profiles,
            "accounts": accounts,
            "events": events,
            "report_date": report_date,
            "revolving_balance": money(revolving_balance),
            "revolving_limit": money(revolving_limit),
            "representative_score": u.application_representative_score(
                [p["representative_score"] for p in profiles]
            ),
        }

    # -- derived values ---------------------------------------------------

    def _derive(
        self, spec: ScenarioSpec, shape: dict[str, Any], housing: dict[str, Any],
        income: dict[str, Any], liabilities: dict[str, Any], settlement: dict[str, Any],
        assets: dict[str, Any], credit: dict[str, Any], as_of: date,
    ) -> dict[str, Any]:
        qmi = income["qualifying_monthly_income"]
        pitia = housing["pitia"]
        total_debt = u.total_monthly_debt(
            pitia, [row["monthly_payment"] for row in liabilities["rows"]]
        )
        draw = assets["draw"]
        reserves = draw.reserve_eligible_remaining
        current_housing = self._current_housing_payment(spec, pitia)
        return {
            "qualifying_monthly_income": qmi,
            "qualifying_annual_income": income["qualifying_annual_income"],
            "gross_monthly_income": u.gross_monthly_income(
                income["qualifying_annual_income"]
            ),
            "housing_expense_pitia": pitia,
            "total_monthly_debt": total_debt,
            "front_end_dti": u.front_end_dti(pitia, qmi),
            "back_end_dti": u.back_end_dti(total_debt, qmi),
            "residual_income_monthly": u.residual_income_monthly(qmi, total_debt),
            "ltv": shape["ltv"],
            "cltv": u.cltv(shape["base_loan_amount"], [], shape["value_used"]),
            "hcltv": u.hcltv(shape["base_loan_amount"], [], [], shape["value_used"]),
            "down_payment_amount": settlement["down_payment"],
            "down_payment_pct": (
                u.down_payment_pct(settlement["down_payment"], shape["purchase_price"])
                if shape["purchase_price"]
                else None
            ),
            "cash_to_close": settlement["funds_required"],
            "funds_to_close_required": draw.required,
            "funds_to_close_available": draw.available,
            "funds_shortfall": draw.shortfall,
            "post_close_reserves": reserves,
            "months_reserves": u.months_reserves(reserves, pitia),
            "credit_utilization": u.credit_utilization(
                credit["revolving_balance"], credit["revolving_limit"]
            ),
            "employment_tenure_months": spec.employment_tenure_months,
            "payment_shock_pct": u.payment_shock_pct(pitia, current_housing),
            "current_housing_payment": current_housing,
            "loan_to_income": u.loan_to_income(
                shape["base_loan_amount"], income["qualifying_annual_income"]
            ),
            "representative_credit_score": credit["representative_score"],
            "draw": draw,
        }

    def _current_housing_payment(
        self, spec: ScenarioSpec, pitia: Decimal
    ) -> Decimal | None:
        """The borrower's present housing cost, or None where there is none.

        A refinancing borrower already owns the home, so payment shock against a
        'current rent' is meaningless for them. For a purchase, the prior payment is
        drawn deterministically per scenario so the payment-shock distribution across
        the dataset is a spread rather than a single repeated value.
        """
        if spec.purpose != "purchase":
            return None
        if spec.current_housing_factor is not None:
            factor = spec.as_decimal("current_housing_factor")
        else:
            rng = u.sub_rng(self.seed, f"shock:{spec.scenario_id}")
            factor = Decimal(str(rng.randrange(52, 96))) / Decimal(100)
        return money(pitia * factor)

    # -- facts ------------------------------------------------------------

    def _facts(
        self, spec: ScenarioSpec, app_id: str, shape: dict[str, Any],
        housing: dict[str, Any], income: dict[str, Any], liabilities: dict[str, Any],
        settlement: dict[str, Any], assets: dict[str, Any], credit: dict[str, Any],
        derived: dict[str, Any], as_of: date,
    ) -> Facts:
        conforming = int(param(
            self.registry, "GEN-ELG-003", "conforming_baseline_one_unit_2026", as_of
        ))
        compensating = self._compensating_factors(spec, derived, as_of)
        household_income = (
            money(spec.household_annual_income_override)
            if spec.household_annual_income_override
            else money(income["qualifying_annual_income"] * Decimal("1.15"))
        )
        return Facts(
            application_id=app_id,
            as_of=as_of,
            application_date=as_of,
            product=spec.product,
            purpose=spec.purpose,
            occupancy=spec.occupancy,
            units=spec.units,
            property_type=spec.property_type,
            loan_amount=shape["note_amount"],
            base_loan_amount=shape["base_loan_amount"],
            term_months=shape["term_months"],
            interest_rate=shape["rate"],
            purchase_price=shape["purchase_price"],
            appraised_value=shape["appraised_value"],
            value_used=shape["value_used"],
            ltv=derived["ltv"],
            cltv=derived["cltv"],
            hcltv=derived["hcltv"],
            qualifying_monthly_income=derived["qualifying_monthly_income"],
            pitia=derived["housing_expense_pitia"],
            total_monthly_debt=derived["total_monthly_debt"],
            back_end_dti=derived["back_end_dti"],
            front_end_dti=derived["front_end_dti"],
            residual_income=derived["residual_income_monthly"],
            representative_score=credit["representative_score"],
            credit_report_age_days=spec.credit_report_age_days,
            scoreable_tradelines=spec.scoreable_tradelines,
            recent_inquiries_90d=spec.recent_inquiries_90d,
            revolving_utilization=derived["credit_utilization"],
            housing_lates_30d_12m=spec.housing_lates_30d_12m,
            housing_lates_60d_12m=spec.housing_lates_60d_12m,
            nonhousing_accounts_30d_24m=spec.nonhousing_accounts_30d_24m,
            any_90d_24m=spec.any_90d_24m,
            collection_total=money(spec.collection_total),
            credit_events=tuple(
                {
                    "event_type": e["event_type"],
                    "anchor_date": e["anchor_date"].isoformat(),
                    "seasoning_months": e["seasoning_months"],
                }
                for e in credit["events"]
            ),
            undeclared_liability_found=spec.undeclared_liability,
            funds_required=derived["funds_to_close_required"],
            funds_available=derived["funds_to_close_available"],
            funds_shortfall=derived["funds_shortfall"],
            reserves_months=derived["months_reserves"],
            own_funds_pct=self._own_funds_pct(spec, shape, settlement, assets),
            gift_amount=assets["gift_amount"],
            gift_documented=spec.gift_documented,
            other_financed_properties=spec.other_financed_properties,
            ownership_months=spec.ownership_months,
            unsourced_deposit_amount=assets["unsourced_deposit"],
            unsourced_deposit_date=(
                as_of - timedelta(days=17) if assets["unsourced_deposit"] > 0 else None
            ),
            employment_tenure_months=spec.employment_tenure_months,
            employment_history_months=spec.employment_history_months,
            job_change_recent=spec.job_change_recent,
            job_change_field_or_structure=spec.job_change_field_or_structure,
            future_employment_start=(
                u.add_months(as_of, spec.future_employment_months_ahead)
                if spec.future_employment_months_ahead is not None
                else None
            ),
            employment_verification_conflict=spec.employment_verification_conflict,
            self_employed=spec.self_employed,
            variable_income_history_months=spec.variable_income_history_months,
            variable_income_positive_factors=spec.variable_income_positive_factors,
            income_conflict_variance=(
                spec.as_decimal("income_conflict_variance")
                if spec.income_conflict_variance
                else None
            ),
            ytd_reconciliation_variance=(
                spec.as_decimal("ytd_reconciliation_variance")
                if spec.ytd_reconciliation_variance
                else None
            ),
            household_size=spec.household_size,
            household_annual_income=household_income,
            valuation_method=spec.valuation_method,
            valuation_age_days=spec.valuation_age_days,
            appraisal_below_contract=spec.appraisal_below_contract,
            property_condition_finding=spec.property_condition_finding,
            flood_zone_sfha=spec.flood_zone_sfha,
            flood_insurance_evidenced=spec.flood_insurance_evidenced,
            occupancy_contradiction=spec.occupancy_contradiction,
            title_exception_blocking=spec.title_exception_blocking,
            identity_status=spec.identity_status,
            fraud_indicators=spec.fraud_indicators,
            document_tampering=spec.document_tampering,
            documents_required=0,
            documents_received_current=0,
            missing_document_types=spec.missing_document_types,
            stale_document_types=spec.stale_document_types,
            security_event_types=spec.security_event_types,
            conforming_limit=conforming,
            compensating_factors=compensating,
        )

    def _compensating_factors(
        self, spec: ScenarioSpec, derived: dict[str, Any], as_of: date
    ) -> tuple[str, ...]:
        """Only factors DTI-CONV-003 recognises, and only where documented."""
        try:
            rule_params = {
                key: param(self.registry, "DTI-CONV-003", key, as_of)
                for key in (
                    "factor_reserves_months", "factor_min_credit_score",
                    "factor_max_payment_shock", "factor_min_employment_months",
                    "factor_max_ltv",
                )
            }
        except KeyError:
            return ()
        found: list[str] = []
        months = derived.get("months_reserves")
        if months is not None and months >= Decimal(str(rule_params["factor_reserves_months"])):
            found.append(f"post-closing reserves of {months} months")
        score = derived.get("representative_credit_score")
        if score is not None and score >= int(rule_params["factor_min_credit_score"]):
            found.append(f"representative credit score {score}")
        shock = derived.get("payment_shock_pct")
        if shock is not None and shock <= Decimal(str(rule_params["factor_max_payment_shock"])):
            found.append(f"payment shock {shock}")
        if spec.employment_tenure_months >= int(rule_params["factor_min_employment_months"]):
            found.append(
                f"continuous employment {spec.employment_tenure_months} months"
            )
        ltv = derived.get("ltv")
        if ltv is not None and ltv <= Decimal(str(rule_params["factor_max_ltv"])):
            found.append(f"loan-to-value {ltv}")
        return tuple(found)

    @staticmethod
    def _own_funds_pct(
        spec: ScenarioSpec, shape: dict[str, Any], settlement: dict[str, Any],
        assets: dict[str, Any],
    ) -> Decimal:
        if not shape["purchase_price"] or shape["purchase_price"] <= 0:
            return ZERO
        own = money(max(ZERO, settlement["down_payment"] - assets["gift_amount"]))
        return ratio(own / shape["purchase_price"])

    # -- row builders -----------------------------------------------------

    def _application_row(
        self, spec: ScenarioSpec, app_id: str, as_of: date, primary: Person,
        co: Person | None,
    ) -> dict[str, Any]:
        return {
            "application_id": app_id,
            "scenario_id": spec.scenario_id,
            "application_date": as_of,
            "underwriting_as_of_date": as_of,
            "received_date": as_of - timedelta(days=9),
            "channel": "retail",
            "loan_purpose": spec.purpose,
            "product_family": spec.product,
            "occupancy_type": spec.occupancy,
            "borrower_count": 2 if co else 1,
            "primary_borrower_id": primary.borrower_id,
            "application_status": "in_underwriting",
            "loan_officer_id": "MLO-0417",
            "loan_officer_identifier_type": "synthetic unique identifier",
            "household_size": spec.household_size,
        }

    @staticmethod
    def _application_borrowers(
        app_id: str, primary: Person, co: Person | None
    ) -> list[dict[str, Any]]:
        rows = [
            {
                "application_id": app_id,
                "borrower_id": primary.borrower_id,
                "borrower_role": "primary",
                "borrower_order": 1,
                "joint_credit_intent": bool(co),
            }
        ]
        if co:
            rows.append(
                {
                    "application_id": app_id,
                    "borrower_id": co.borrower_id,
                    "borrower_role": "co_borrower",
                    "borrower_order": 2,
                    "joint_credit_intent": True,
                }
            )
        return rows

    def _loan_row(
        self, spec: ScenarioSpec, app_id: str, shape: dict[str, Any],
        housing: dict[str, Any], settlement: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "loan_id": f"{app_id}-LOAN",
            "application_id": app_id,
            "product_family": spec.product,
            "loan_purpose": spec.purpose,
            "base_loan_amount": shape["base_loan_amount"],
            "financed_premium_amount": shape["financed_premium"],
            "note_amount": shape["note_amount"],
            "term_months": shape["term_months"],
            "interest_rate": shape["rate"],
            "rate_type": "fixed",
            "lien_position": 1,
            "amortisation_type": "fully_amortising",
            "principal_and_interest": housing["principal_interest"],
            "monthly_mortgage_insurance": housing["monthly_mortgage_insurance"],
            "down_payment_amount": settlement["down_payment"],
            "seller_credits": settlement["seller_credits"],
            "lender_credits": settlement["lender_credits"],
            "closing_costs": settlement["closing_costs"],
            "prepaids_and_escrow": settlement["prepaids"],
            "earnest_money_paid": settlement["earnest_money"],
            "payoff_amount": settlement["payoff_amount"],
            "cash_out_proceeds": settlement["cash_out_proceeds"],
        }

    def _property_row(
        self, spec: ScenarioSpec, app_id: str, shape: dict[str, Any],
        housing: dict[str, Any], primary: Person,
    ) -> dict[str, Any]:
        return {
            "property_id": f"{app_id}-PROP",
            "application_id": app_id,
            # Python's built-in hash() is salted per process, so it must never
            # appear in generated data. stable_hash is a fixed digest.
            "street": self._property_street(app_id),
            "city": primary.city,
            "state": primary.state,
            "postal_code": primary.postal_code,
            "property_type": spec.property_type,
            "units": spec.units,
            "occupancy_type": spec.occupancy,
            "purchase_price": shape["purchase_price"],
            "appraised_value": shape["appraised_value"],
            "value_used_for_ltv": shape["value_used"],
            "valuation_method": spec.valuation_method,
            "annual_property_tax": money(housing["monthly_property_tax"] * 12),
            "annual_hazard_premium": money(housing["monthly_hazard_insurance"] * 12),
            "monthly_hoa": housing["monthly_hoa"],
            "flood_zone": "AE" if spec.flood_zone_sfha else "X",
            "flood_zone_sfha": spec.flood_zone_sfha,
            "ownership_months": spec.ownership_months,
        }

    @staticmethod
    def _property_street(app_id: str) -> str:
        digest = int(u.stable_hash("street", app_id), 16)
        streets = (
            "Wrenfield Way", "Copperbeech Drive", "Marlowe Crossing", "Hazeldene Court",
            "Ambersley Road", "Foxglove Terrace", "Kingsmere Lane", "Sablecrest Drive",
        )
        return f"{2200 + digest % 700} {streets[digest % len(streets)]}"

    def _appraisal_row(
        self, spec: ScenarioSpec, app_id: str, shape: dict[str, Any], as_of: date
    ) -> dict[str, Any] | None:
        if spec.valuation_method == "value_acceptance":
            return None
        return {
            "appraisal_id": f"{app_id}-APR",
            "application_id": app_id,
            "property_id": f"{app_id}-PROP",
            "appraisal_date": as_of - timedelta(days=spec.valuation_age_days),
            "valuation_method": spec.valuation_method,
            "appraised_value": shape["appraised_value"],
            "appraiser_licence": "SYN-APPR-00418",
            "condition_rating": "C4" if spec.property_condition_finding else "C3",
            "condition_finding": spec.property_condition_finding,
            "dataset_version": "SYNTH-UAD-3.6",
            "below_contract_price": spec.appraisal_below_contract,
        }

    def _employment_rows(
        self, spec: ScenarioSpec, app_id: str, primary: Person, co: Person | None,
        as_of: date,
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for idx, person in enumerate([p for p in (primary, co) if p]):
            tenure = spec.employment_tenure_months if idx == 0 else max(
                24, spec.employment_tenure_months - 7
            )
            start = u.add_months(as_of, -tenure)
            declared_start = start
            if spec.employment_verification_conflict and idx == 0:
                declared_start = u.add_months(start, -4)
            rows.append(
                {
                    "employment_id": f"{app_id}-EMP-{idx + 1}",
                    "application_id": app_id,
                    "borrower_id": person.borrower_id,
                    "employer_name": person.employer,
                    "occupation": person.occupation,
                    "employment_type": (
                        "self_employed" if spec.self_employed and idx == 0 else "employed"
                    ),
                    "self_employed_flag": spec.self_employed and idx == 0,
                    "business_ownership_pct": (
                        Decimal("100") if spec.self_employed and idx == 0 else ZERO
                    ),
                    "declared_start_date": declared_start,
                    "verified_start_date": start,
                    "end_date": None,
                    "is_current": True,
                    "tenure_months": u.employment_tenure_months(start, as_of),
                    "pay_frequency": "bi_weekly",
                }
            )
            if spec.employment_history_months > tenure and tenure < 60:
                prior_end = u.add_months(start, -1)
                prior_start = u.add_months(
                    prior_end, -(spec.employment_history_months - tenure)
                )
                rows.append(
                    {
                        "employment_id": f"{app_id}-EMP-{idx + 1}P",
                        "application_id": app_id,
                        "borrower_id": person.borrower_id,
                        "employer_name": "Kestrel Freight Services",
                        "occupation": "Operations Associate",
                        "employment_type": "employed",
                        "self_employed_flag": False,
                        "business_ownership_pct": ZERO,
                        "declared_start_date": prior_start,
                        "verified_start_date": prior_start,
                        "end_date": prior_end,
                        "is_current": False,
                        "tenure_months": u.months_between(prior_start, prior_end),
                        "pay_frequency": "bi_weekly",
                    }
                )
        return rows

    def _verification_rows(
        self, spec: ScenarioSpec, app_id: str, primary: Person, as_of: date
    ) -> list[dict[str, Any]]:
        def row(idx: int, category: str, result: str, rule: str) -> dict[str, Any]:
            return {
                "verification_id": f"{app_id}-VER-{idx}",
                "application_id": app_id,
                "borrower_id": primary.borrower_id,
                "category": category,
                "provider": "SYNTH-VERIFY",
                "requested_date": as_of - timedelta(days=12),
                "completed_date": as_of - timedelta(days=8),
                "result": result,
                "rule_id": rule,
            }

        return [
            row(1, "identity", spec.identity_status, "KYC-IDV-001"),
            row(
                2, "employment",
                "CONFLICT" if spec.employment_verification_conflict else "VERIFIED",
                "EMP-VER-001",
            ),
            row(3, "income", "VERIFIED", "INC-GEN-001"),
            row(4, "assets", "VERIFIED", "AST-ELG-001"),
            row(5, "flood_determination", "AE" if spec.flood_zone_sfha else "X",
                "PRP-ELG-004"),
        ]

    def _title_rows(
        self, spec: ScenarioSpec, app_id: str, as_of: date
    ) -> list[dict[str, Any]]:
        return [
            {
                "title_record_id": f"{app_id}-TTL",
                "application_id": app_id,
                "commitment_date": as_of - timedelta(days=6),
                "required_lien_position": 1,
                "vesting_matches_borrowers": True,
                "exception_count": 2 if spec.title_exception_blocking else 1,
                "blocking_exception": spec.title_exception_blocking,
                "exception_summary": (
                    "Recorded judgment taking priority over the new lien"
                    if spec.title_exception_blocking
                    else "Standard utility easement"
                ),
                "rule_id": "TTL-LIE-002",
            }
        ]

    def _insurance_rows(
        self, spec: ScenarioSpec, app_id: str, shape: dict[str, Any],
        housing: dict[str, Any], as_of: date,
    ) -> list[dict[str, Any]]:
        rows = [
            {
                "insurance_record_id": f"{app_id}-INS-HAZ",
                "application_id": app_id,
                "coverage_type": "hazard",
                "carrier": "Thornhill Insurance Brokers",
                "annual_premium": money(housing["monthly_hazard_insurance"] * 12),
                "coverage_amount": shape["base_loan_amount"],
                "effective_date": as_of + timedelta(days=21),
                "evidenced": True,
                "rule_id": "TTL-INS-001",
            }
        ]
        if spec.flood_zone_sfha:
            rows.append(
                {
                    "insurance_record_id": f"{app_id}-INS-FLD",
                    "application_id": app_id,
                    "coverage_type": "flood",
                    "carrier": "Thornhill Insurance Brokers",
                    "annual_premium": money(housing["monthly_flood_insurance"] * 12),
                    "coverage_amount": shape["base_loan_amount"],
                    "effective_date": as_of + timedelta(days=21),
                    "evidenced": spec.flood_insurance_evidenced,
                    "rule_id": "PRP-ELG-004",
                }
            )
        return rows

    @staticmethod
    def _calculation_rows(
        app_id: str, as_of: date, derived: dict[str, Any], facts: Facts
    ) -> list[dict[str, Any]]:
        spec_map: list[tuple[str, str, tuple[str, ...], str, str]] = [
            ("gross_monthly_income", "gross_monthly_income",
             ("income.annual_amount",), "USD_PER_MONTH",
             "Gross eligible earnings before tax, before policy adjustment."),
            ("qualifying_monthly_income", "qualifying_monthly_income",
             ("income.qualifying_monthly_amount",), "USD_PER_MONTH",
             "The income figure the affordability rules are permitted to use."),
            ("housing_expense_pitia", "housing_expense_pitia",
             ("loans.principal_and_interest", "properties.annual_property_tax",
              "properties.annual_hazard_premium", "properties.monthly_hoa",
              "loans.monthly_mortgage_insurance"),
             "USD_PER_MONTH",
             "Full qualifying housing expense; the reserve denominator."),
            ("total_monthly_debt", "total_monthly_debt",
             ("underwriting_calculations.housing_expense_pitia",
              "liabilities.monthly_payment"),
             "USD_PER_MONTH", "DTI numerator."),
            ("front_end_dti", "front_end_dti",
             ("underwriting_calculations.housing_expense_pitia",
              "underwriting_calculations.qualifying_monthly_income"),
             "RATIO", "Housing ratio; advisory except on the USDA overlay."),
            ("back_end_dti", "back_end_dti",
             ("underwriting_calculations.total_monthly_debt",
              "underwriting_calculations.qualifying_monthly_income"),
             "RATIO", "Principal affordability measure (AC-02)."),
            ("residual_income_monthly", "residual_income_monthly",
             ("underwriting_calculations.qualifying_monthly_income",
              "underwriting_calculations.total_monthly_debt"),
             "USD_PER_MONTH", "Disposable income (AC-02 alternative measure)."),
            ("ltv", "ltv",
             ("loans.base_loan_amount", "properties.value_used_for_ltv"),
             "RATIO", "Leverage against the value the rule uses."),
            ("cltv", "cltv",
             ("loans.base_loan_amount", "properties.value_used_for_ltv"),
             "RATIO", "Leverage including every subordinate lien."),
            ("hcltv", "hcltv",
             ("loans.base_loan_amount", "properties.value_used_for_ltv"),
             "RATIO", "Leverage counting HELOC credit lines in full."),
            ("down_payment_amount", "down_payment_amount",
             ("properties.purchase_price", "loans.base_loan_amount"),
             "USD", "Borrower equity contribution at purchase."),
            ("down_payment_pct", "down_payment_pct",
             ("underwriting_calculations.down_payment_amount",
              "properties.purchase_price"),
             "RATIO", "Contribution as a share of price."),
            ("cash_to_close", "cash_to_close",
             ("underwriting_calculations.down_payment_amount", "loans.closing_costs",
              "loans.prepaids_and_escrow", "loans.seller_credits",
              "loans.earnest_money_paid"),
             "USD", "Borrower funds required at settlement."),
            ("funds_to_close_available", "funds_to_close_available",
             ("assets.eligible_close_amount",), "USD",
             "Eligible assets available at settlement."),
            ("funds_shortfall", "funds_shortfall",
             ("underwriting_calculations.cash_to_close",
              "underwriting_calculations.funds_to_close_available"),
             "USD", "Positive value means the file cannot close as structured."),
            ("post_close_reserves", "post_close_reserves",
             ("assets.eligible_reserve_amount",
              "underwriting_calculations.cash_to_close"),
             "USD", "Reserve-eligible assets surviving the settlement draw."),
            ("months_reserves", "months_reserves",
             ("underwriting_calculations.post_close_reserves",
              "underwriting_calculations.housing_expense_pitia"),
             "MONTHS", "Reserves expressed in months of housing expense."),
            ("credit_utilization", "credit_utilization",
             ("credit_accounts.balance", "credit_accounts.credit_limit"),
             "RATIO", "Risk context only; never a policy breach on its own."),
            ("employment_tenure_months", "employment_tenure_months",
             ("employment.verified_start_date", "applications.application_date"),
             "MONTHS", "Computed from the verified start date, not the declared one."),
            ("payment_shock_pct", "payment_shock_pct",
             ("underwriting_calculations.housing_expense_pitia",
              "applications.current_housing_payment"),
             "RATIO", "Not applicable where there is no prior housing payment."),
            ("loan_to_income", "loan_to_income",
             ("loans.base_loan_amount",
              "underwriting_calculations.qualifying_annual_income"),
             "MULTIPLE", "Supplemental analytical measure, not an eligibility rule."),
            ("representative_credit_score", "representative_credit_score",
             ("credit_profiles.score_1", "credit_profiles.score_2",
              "credit_profiles.score_3"),
             "SCORE", "Middle of three per borrower; lowest across borrowers."),
        ]
        rows: list[dict[str, Any]] = []
        for idx, (name, formula_key, inputs, units, interpretation) in enumerate(spec_map, 1):
            value = derived.get(name)
            rows.append(
                {
                    "calculation_id": f"{app_id}-CALC-{idx:02d}",
                    "application_id": app_id,
                    "calculation_name": name,
                    "input_fields": "|".join(inputs),
                    "formula_version": u.FORMULA_VERSIONS.get(formula_key, "v1.0.0"),
                    "result": value,
                    "units": units,
                    "calculated_at": as_of,
                    "policy_context": _policy_context(name),
                    "expected_interpretation": interpretation,
                }
            )
        _ = facts
        return rows


def _policy_context(name: str) -> str:
    return {
        "qualifying_monthly_income": "POL-INC-001",
        "gross_monthly_income": "POL-INC-001",
        "housing_expense_pitia": "POL-DTI-001",
        "total_monthly_debt": "POL-LIA-001",
        "front_end_dti": "POL-DTI-001",
        "back_end_dti": "POL-DTI-001",
        "residual_income_monthly": "POL-DTI-001",
        "ltv": "POL-CONV-001",
        "cltv": "POL-CONV-001",
        "hcltv": "POL-CONV-001",
        "down_payment_amount": "POL-AST-002",
        "down_payment_pct": "POL-AST-002",
        "cash_to_close": "POL-AST-002",
        "funds_to_close_available": "POL-AST-001",
        "funds_shortfall": "POL-AST-002",
        "post_close_reserves": "POL-AST-003",
        "months_reserves": "POL-AST-003",
        "credit_utilization": "POL-CRD-003",
        "employment_tenure_months": "POL-EMP-002",
        "payment_shock_pct": "POL-DTI-001",
        "loan_to_income": "POL-DTI-001",
        "representative_credit_score": "POL-CRD-001",
    }.get(name, "POL-GEN-001")


def _present_value(payment: Decimal, annual_rate: Decimal, months: int) -> Decimal:
    """Balance implied by a level payment over a remaining term."""
    if months <= 0:
        return ZERO
    i = annual_rate / Decimal(12)
    if i == 0:
        return money(payment * months)
    growth = (Decimal(1) + i) ** months
    return money(payment * (growth - Decimal(1)) / (i * growth))


def summarise(built: BuiltApplication) -> dict[str, Any]:
    """Engine-derived outcome summary used by the golden set and the reports."""
    result = built.engine_result
    facts = built.facts
    rec = recommendation(result, facts)
    return {
        "eligibility_result": eligibility_result(result),
        "risk_level": risk_level(result),
        "recommendation": rec,
        "requires_human_review": requires_human_review(result, rec),
    }
