"""
CredPilot synthetic-data utilities.

Deterministic primitives shared by the generator and the validator:

* seeding and stable sub-RNG derivation
* synthetic identifier minting and masking (no real PII is ever produced)
* money arithmetic on Decimal so results are bit-stable
* the underwriting calculation library (amortisation, PITIA, DTI, LTV/CLTV/HCLTV,
  funds-to-close, reserves, utilisation, tenure, payment shock, seasoning)
* CSV / JSONL writers with a stable column order

Every calculation function is pure: same inputs -> same output, on every platform.
No calculation in this project is ever performed by a language model; the model's
role is to explain a value this module produced.

Formula versions are explicit so a stored result can be reproduced later.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import random
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP, getcontext
from pathlib import Path
from typing import Any, Iterable, Sequence

getcontext().prec = 28

# ---------------------------------------------------------------------------
# Repository layout
# ---------------------------------------------------------------------------

#: The generator lives inside the dataset it produces, so the producing code
#: and its evidence stay together in one folder.
SYNTH_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SYNTH_ROOT.parent
POLICY_CORPUS_DIR = SYNTH_ROOT / "policy_corpus"
APPLICATION_INPUT_DIR = SYNTH_ROOT / "applications"
STRUCTURED_DIR = SYNTH_ROOT / "structured"
PROFILE_DIR = SYNTH_ROOT / "profiles"
POLICY_META_DIR = SYNTH_ROOT / "policy_metadata"
DOCUMENT_DIR = SYNTH_ROOT / "applicant_documents"
SCENARIO_DIR = SYNTH_ROOT / "scenarios"
GOLDEN_DIR = SYNTH_ROOT / "golden_set"
SCHEMA_DIR = SYNTH_ROOT / "schemas"

# ---------------------------------------------------------------------------
# Seeding
# ---------------------------------------------------------------------------

DEFAULT_SEED = 20260920

#: The generation "today". Fixed so the dataset is reproducible regardless of
#: when the generator is run. Matches the research report's access date.
AS_OF_DATE = date(2026, 9, 20)

#: The single synthetic policy-version boundary used by the temporal-retrieval
#: scenarios. Applications either side of it must resolve different rule values.
POLICY_V1_EFFECTIVE = date(2026, 1, 1)
POLICY_V2_EFFECTIVE = date(2026, 7, 1)


def resolve_seed() -> int:
    """The active seed: SYNTHETIC_SEED from the environment, else the default."""
    raw = os.environ.get("SYNTHETIC_SEED", "").strip()
    if not raw:
        return DEFAULT_SEED
    try:
        return int(raw)
    except ValueError as exc:  # pragma: no cover - operator error
        raise SystemExit("SYNTHETIC_SEED must be an integer, got " + repr(raw)) from exc


def sub_rng(seed: int, label: str) -> random.Random:
    """A stable, independent RNG for `label`.

    Deriving from a hash rather than from a shared stream means adding a scenario
    never shifts the values of unrelated scenarios, so regeneration diffs stay
    small and reviewable.
    """
    digest = hashlib.sha256(f"{seed}:{label}".encode("utf-8")).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))


def stable_hash(*parts: Any) -> str:
    """A short deterministic hex digest used for synthetic document checksums."""
    joined = "|".join(str(p) for p in parts)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Synthetic identifiers and masking
#
# Nothing here can collide with a real identifier: every sensitive value is a
# token with a SYN- prefix, and its display form is masked.
# ---------------------------------------------------------------------------


def borrower_id(n: int) -> str:
    return f"BORR-{n:06d}"


def application_id(n: int) -> str:
    return f"APP-{n:06d}"


def syn_ssn_token(n: int) -> str:
    """Tokenised stand-in for a taxpayer identifier. Never a real SSN."""
    return f"SYN-SSN-{n:06d}"


def mask_ssn(token: str) -> str:
    """Display form of a tokenised taxpayer identifier: ***-**-0001."""
    tail = token.split("-")[-1][-4:]
    return f"***-**-{tail}"


def syn_account_token(n: int) -> str:
    return f"SYN-ACCT-{n:06d}"


def mask_account(token: str) -> str:
    """Display form of a tokenised deposit/brokerage account: ******0001."""
    tail = token.split("-")[-1][-4:]
    return f"******{tail}"


def syn_credit_token(n: int) -> str:
    return f"SYN-CRDT-{n:06d}"


def mask_credit(token: str) -> str:
    """Display form of a tokenised credit identifier: ****0001."""
    tail = token.split("-")[-1][-4:]
    return f"****{tail}"


def redact(_value: str) -> str:
    """Fully suppress a value that must never be rendered."""
    return "[REDACTED]"


def sanitize_for_log(value: str) -> str:
    """Belt-and-braces scrub applied to anything written to a log-like artifact."""
    if value.startswith("SYN-SSN-"):
        return mask_ssn(value)
    if value.startswith("SYN-ACCT-"):
        return mask_account(value)
    if value.startswith("SYN-CRDT-"):
        return mask_credit(value)
    return value


def syn_phone(area_code: str, n: int) -> str:
    """Reserved fictional telephone block (NANP 555-0100..555-0199) - never routable."""
    return f"({area_code}) 555-{100 + (n % 100):04d}"


def syn_email(first: str, last: str, n: int) -> str:
    """Addresses use the reserved example.com domain (RFC 2606)."""
    return f"{first.lower()}.{last.lower()}{n:03d}@example.com"


# ---------------------------------------------------------------------------
# Money
# ---------------------------------------------------------------------------

CENTS = Decimal("0.01")
PCT = Decimal("0.0001")


def money(value: Any) -> Decimal:
    """Coerce to a Decimal rounded to cents, half-up."""
    return Decimal(str(value)).quantize(CENTS, rounding=ROUND_HALF_UP)


def ratio(value: Any) -> Decimal:
    """Coerce to a Decimal ratio rounded to 4 dp (i.e. 2 dp as a percentage)."""
    return Decimal(str(value)).quantize(PCT, rounding=ROUND_HALF_UP)


def as_float(value: Decimal | None) -> float | None:
    return None if value is None else float(value)


# ---------------------------------------------------------------------------
# Dates
# ---------------------------------------------------------------------------


def months_between(start: date, end: date) -> int:
    """Whole months from `start` to `end` (0 if `end` precedes `start`)."""
    if end < start:
        return 0
    months = (end.year - start.year) * 12 + (end.month - start.month)
    if end.day < start.day:
        months -= 1
    return max(0, months)


def _days_in_month(year: int, month: int) -> int:
    if month == 12:
        return 31
    return (date(year, month + 1, 1) - timedelta(days=1)).day


def add_months(anchor: date, months: int) -> date:
    month_index = anchor.month - 1 + months
    year = anchor.year + month_index // 12
    month = month_index % 12 + 1
    day = min(anchor.day, _days_in_month(year, month))
    return date(year, month, day)


def iso(value: date | None) -> str | None:
    return None if value is None else value.isoformat()


# ---------------------------------------------------------------------------
# Underwriting calculations
#
# Each function is registered in FORMULA_VERSIONS so a persisted result can be
# tied to the exact expression that produced it.
# ---------------------------------------------------------------------------

FORMULA_VERSIONS: dict[str, str] = {
    "gross_monthly_income": "v1.0.0",
    "qualifying_monthly_income": "v1.0.0",
    "principal_and_interest": "v1.0.0",
    "housing_expense_pitia": "v1.0.0",
    "total_monthly_debt": "v1.0.0",
    "front_end_dti": "v1.0.0",
    "back_end_dti": "v1.0.0",
    "residual_income_monthly": "v1.0.0",
    "ltv": "v1.0.0",
    "cltv": "v1.0.0",
    "hcltv": "v1.0.0",
    "down_payment_amount": "v1.0.0",
    "down_payment_pct": "v1.0.0",
    "cash_to_close": "v1.0.0",
    "funds_to_close_available": "v1.0.0",
    "funds_shortfall": "v1.0.0",
    "post_close_reserves": "v1.0.0",
    "months_reserves": "v1.0.0",
    "credit_utilization": "v1.0.0",
    "employment_tenure_months": "v1.0.0",
    "payment_shock_pct": "v1.0.0",
    "loan_to_income": "v1.0.0",
    "derogatory_seasoning_months": "v1.0.0",
    "representative_credit_score": "v1.0.0",
}


def gross_monthly_income(annual_income: Decimal) -> Decimal:
    """Annual gross / 12. Research report, 'Underwriting calculations'."""
    return money(Decimal(annual_income) / Decimal(12))


def principal_and_interest(
    loan_amount: Decimal, annual_rate: Decimal, term_months: int
) -> Decimal:
    """Level-payment amortisation.

    P = L * i * (1+i)^n / ((1+i)^n - 1), with i the monthly rate.
    A zero rate degenerates to L / n.
    """
    loan = Decimal(loan_amount)
    if term_months <= 0:
        raise ValueError("term_months must be positive")
    i = Decimal(annual_rate) / Decimal(12)
    if i == 0:
        return money(loan / Decimal(term_months))
    growth = (Decimal(1) + i) ** term_months
    return money(loan * i * growth / (growth - Decimal(1)))


def housing_expense_pitia(
    principal_interest: Decimal,
    monthly_property_tax: Decimal,
    monthly_hazard_insurance: Decimal,
    monthly_hoa: Decimal = Decimal(0),
    monthly_mortgage_insurance: Decimal = Decimal(0),
    monthly_flood_insurance: Decimal = Decimal(0),
    monthly_subordinate_payment: Decimal = Decimal(0),
) -> Decimal:
    """Qualifying housing expense.

    Principal + interest + taxes + insurance + association dues, plus mortgage
    insurance, flood insurance and any subordinate-lien payment that qualifies as
    part of the housing obligation.
    """
    return money(
        Decimal(principal_interest)
        + Decimal(monthly_property_tax)
        + Decimal(monthly_hazard_insurance)
        + Decimal(monthly_hoa)
        + Decimal(monthly_mortgage_insurance)
        + Decimal(monthly_flood_insurance)
        + Decimal(monthly_subordinate_payment)
    )


def total_monthly_debt(
    pitia: Decimal, qualifying_liability_payments: Iterable[Decimal]
) -> Decimal:
    """PITIA plus every liability payment the policy engine marked include_in_dti."""
    return money(
        Decimal(pitia)
        + sum((Decimal(p) for p in qualifying_liability_payments), Decimal(0))
    )


def front_end_dti(pitia: Decimal, qualifying_monthly_income: Decimal) -> Decimal | None:
    """Housing ratio. None when qualifying income is zero (no silent divide)."""
    income = Decimal(qualifying_monthly_income)
    if income <= 0:
        return None
    return ratio(Decimal(pitia) / income)


def back_end_dti(
    monthly_debt: Decimal, qualifying_monthly_income: Decimal
) -> Decimal | None:
    """Total monthly obligations / qualifying monthly income."""
    income = Decimal(qualifying_monthly_income)
    if income <= 0:
        return None
    return ratio(Decimal(monthly_debt) / income)


def residual_income_monthly(
    qualifying_monthly_income: Decimal, monthly_debt: Decimal
) -> Decimal:
    """Disposable income after the proposed housing expense and recurring debt.

    AC-02 names 'DTI / disposable income'; both are produced so either can be cited.
    """
    return money(Decimal(qualifying_monthly_income) - Decimal(monthly_debt))


def value_for_ltv(
    loan_purpose: str, purchase_price: Decimal | None, appraised_value: Decimal | None
) -> Decimal:
    """The denominator the LTV rule uses.

    Purchase transactions use the lower of contract price and appraised value;
    refinances use the appraised/accepted value. Research report, 'Underwriting
    calculations' (Fannie Mae Selling Guide B2-1.2-01 is cited there for the
    purchase convention).
    """
    if loan_purpose == "purchase":
        if purchase_price is None or appraised_value is None:
            raise ValueError("purchase LTV needs both price and appraised value")
        return money(min(Decimal(purchase_price), Decimal(appraised_value)))
    if appraised_value is None:
        raise ValueError("refinance LTV needs an appraised value")
    return money(appraised_value)


def ltv(loan_amount: Decimal, value_denominator: Decimal) -> Decimal | None:
    denom = Decimal(value_denominator)
    if denom <= 0:
        return None
    return ratio(Decimal(loan_amount) / denom)


def cltv(
    loan_amount: Decimal,
    subordinate_balances: Iterable[Decimal],
    value_denominator: Decimal,
) -> Decimal | None:
    denom = Decimal(value_denominator)
    if denom <= 0:
        return None
    total = Decimal(loan_amount) + sum(
        (Decimal(b) for b in subordinate_balances), Decimal(0)
    )
    return ratio(total / denom)


def hcltv(
    loan_amount: Decimal,
    subordinate_closed_end_balances: Iterable[Decimal],
    heloc_credit_limits: Iterable[Decimal],
    value_denominator: Decimal,
) -> Decimal | None:
    """CLTV using the full HELOC credit line rather than its drawn balance."""
    denom = Decimal(value_denominator)
    if denom <= 0:
        return None
    total = (
        Decimal(loan_amount)
        + sum((Decimal(b) for b in subordinate_closed_end_balances), Decimal(0))
        + sum((Decimal(limit) for limit in heloc_credit_limits), Decimal(0))
    )
    return ratio(total / denom)


def down_payment_amount(purchase_price: Decimal, loan_amount: Decimal) -> Decimal:
    return money(Decimal(purchase_price) - Decimal(loan_amount))


def down_payment_pct(down_payment: Decimal, purchase_price: Decimal) -> Decimal | None:
    price = Decimal(purchase_price)
    if price <= 0:
        return None
    return ratio(Decimal(down_payment) / price)


def cash_to_close(
    down_payment: Decimal,
    closing_costs: Decimal,
    prepaids_and_escrow: Decimal,
    seller_credits: Decimal = Decimal(0),
    lender_credits: Decimal = Decimal(0),
    earnest_money_paid: Decimal = Decimal(0),
    payoff_amount: Decimal = Decimal(0),
    cash_out_proceeds: Decimal = Decimal(0),
) -> Decimal:
    """Borrower funds required at settlement.

    Purchase: down payment + costs + prepaids - credits - earnest money already paid.
    Refinance: the payoff is financed by the new loan, so it is added and then the
    new loan proceeds are recognised by the caller; cash-out proceeds reduce the
    borrower's required contribution.
    """
    total = (
        Decimal(down_payment)
        + Decimal(closing_costs)
        + Decimal(prepaids_and_escrow)
        + Decimal(payoff_amount)
        - Decimal(seller_credits)
        - Decimal(lender_credits)
        - Decimal(earnest_money_paid)
        - Decimal(cash_out_proceeds)
    )
    return money(total)


@dataclass(frozen=True)
class FundsDraw:
    """The deterministic order in which assets were consumed at closing."""

    required: Decimal
    available: Decimal
    shortfall: Decimal
    drawn: tuple[tuple[str, Decimal], ...]
    reserve_eligible_remaining: Decimal


def draw_funds_to_close(
    required: Decimal,
    assets: Sequence[dict[str, Any]],
) -> FundsDraw:
    """Consume closing funds from assets in a fixed, auditable order.

    Non-reserve-eligible sources (gift funds, earnest money already on deposit,
    sale proceeds) are consumed first so that reserve-eligible liquid assets are
    preserved for the reserve test wherever the policy permits. Within each tier
    assets are consumed in asset_id order, which makes the draw reproducible.

    `assets` rows use: asset_id, eligible_close_amount, eligible_reserve_amount.
    """
    need = Decimal(required)
    drawn: list[tuple[str, Decimal]] = []

    tier_one = sorted(
        (a for a in assets if Decimal(a["eligible_reserve_amount"]) == 0),
        key=lambda a: a["asset_id"],
    )
    tier_two = sorted(
        (a for a in assets if Decimal(a["eligible_reserve_amount"]) > 0),
        key=lambda a: a["asset_id"],
    )

    reserve_pool = sum(
        (Decimal(a["eligible_reserve_amount"]) for a in assets), Decimal(0)
    )
    available = sum((Decimal(a["eligible_close_amount"]) for a in assets), Decimal(0))
    reserve_consumed = Decimal(0)

    for tier, is_reserve_tier in ((tier_one, False), (tier_two, True)):
        for asset in tier:
            if need <= 0:
                break
            can_take = min(need, Decimal(asset["eligible_close_amount"]))
            if can_take <= 0:
                continue
            drawn.append((asset["asset_id"], money(can_take)))
            need -= can_take
            if is_reserve_tier:
                reserve_consumed += min(
                    can_take, Decimal(asset["eligible_reserve_amount"])
                )

    shortfall = money(max(Decimal(0), need))
    remaining = money(max(Decimal(0), reserve_pool - reserve_consumed))
    return FundsDraw(
        required=money(required),
        available=money(available),
        shortfall=shortfall,
        drawn=tuple(drawn),
        reserve_eligible_remaining=remaining,
    )


def months_reserves(post_close_reserves: Decimal, pitia: Decimal) -> Decimal | None:
    payment = Decimal(pitia)
    if payment <= 0:
        return None
    return (Decimal(post_close_reserves) / payment).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


def credit_utilization(
    revolving_balance: Decimal, revolving_limit: Decimal
) -> Decimal | None:
    """Revolving balance / revolving limit.

    Lines with no stated limit are excluded by the caller before summing, so a zero
    denominator means 'not measurable' rather than 'zero utilisation'.
    """
    limit = Decimal(revolving_limit)
    if limit <= 0:
        return None
    return ratio(Decimal(revolving_balance) / limit)


def employment_tenure_months(start: date, as_of: date) -> int:
    return months_between(start, as_of)


def payment_shock_pct(
    proposed_pitia: Decimal, current_housing_payment: Decimal | None
) -> Decimal | None:
    """Relative increase in housing payment.

    None when there is no prior payment: a borrower living rent-free has no
    meaningful denominator, and inventing one would fabricate a risk signal.
    """
    if current_housing_payment is None:
        return None
    current = Decimal(current_housing_payment)
    if current <= 0:
        return None
    return ratio((Decimal(proposed_pitia) - current) / current)


def loan_to_income(
    loan_amount: Decimal, annual_qualifying_income: Decimal
) -> Decimal | None:
    income = Decimal(annual_qualifying_income)
    if income <= 0:
        return None
    return (Decimal(loan_amount) / income).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


def derogatory_seasoning_months(event_date: date, as_of: date) -> int:
    return months_between(event_date, as_of)


def representative_credit_score(scores: Sequence[int]) -> int | None:
    """Middle of three scores; lower of two; the single score if only one exists.

    This is a SYNTHETIC_INTERNAL_POLICY methodology chosen because it mirrors the
    widely described public convention. It is documented as rule CRD-SCR-002.
    """
    clean = sorted(s for s in scores if s is not None)
    if not clean:
        return None
    if len(clean) >= 3:
        mid = len(clean) // 2
        return clean[mid] if len(clean) % 2 == 1 else clean[mid - 1]
    return clean[0]


def application_representative_score(
    per_borrower_scores: Sequence[int | None],
) -> int | None:
    """For a multi-borrower application, the lowest borrower representative score."""
    clean = [s for s in per_borrower_scores if s is not None]
    return min(clean) if clean else None


# ---------------------------------------------------------------------------
# Writers / readers
# ---------------------------------------------------------------------------


def _jsonable(value: Any) -> Any:
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    return value


def _csv_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, (list, tuple)):
        return "|".join(str(v) for v in value)
    return str(value)


def write_csv(path: Path, rows: Sequence[dict[str, Any]], columns: Sequence[str]) -> int:
    """Write `rows` with an explicit column order.

    The header is always written, so an empty table is still a well-formed,
    schema-bearing artifact rather than a zero-byte file.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns), extrasaction="raise")
        writer.writeheader()
        for row in rows:
            writer.writerow({c: _csv_cell(row.get(c)) for c in columns})
    return len(rows)


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(_jsonable(record), ensure_ascii=False))
            handle.write("\n")
            count += 1
    return count


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(_jsonable(payload), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + "\n", encoding="utf-8", newline="\n")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                out.append(json.loads(stripped))
    return out


def dec(value: Any, default: str = "0") -> Decimal:
    """Parse a CSV cell back to Decimal, treating blank as `default`."""
    if value is None or value == "":
        return Decimal(default)
    return Decimal(str(value))


def parse_date(value: Any) -> date | None:
    if value is None or value == "":
        return None
    return date.fromisoformat(str(value))


def parse_bool(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}
