"""Funds to close, and the reserves that are what remains after it.

``AST-FTC-001`` defines the calculation, ``AST-FTC-004`` the draw order, and
``AST-RSV-001`` says reserves are measured on what is left once the draw has
happened. The three are one arithmetic chain, and two links in it were wrong
when this system was first run end to end:

* reserves were measured on the balance **before** closing, overstating them by
  the entire down payment — 40.7 months where the truth was 9.6;
* the whole lien payoff was counted as cash the borrower must bring, ignoring
  ``AST-FTC-001``'s "not financed by the new loan". That made every refinance
  look like the borrower had to arrive with the existing balance in cash, and
  **declined files that should have approved** — the worst direction to be wrong
  in.

Both are covered here against the committed packets, so neither can come back.
"""

from __future__ import annotations

import pytest

from src.application_context import build_underwriting_input
from src.calculations import compute_affordability
from src.domain import LendingProductDomain

MORTGAGE = LendingProductDomain.MORTGAGE


@pytest.fixture(scope="module")
def figures(repo_root):
    def _for(application_id: str) -> dict:
        packet = build_underwriting_input(
            repo_root / f"synthetic_data/mortgage/applications/{application_id}.json"
        )
        return compute_affordability(MORTGAGE, packet)

    return _for


# ------------------------------------------------------------------ the payoff


def test_a_refinance_payoff_covered_by_the_new_loan_costs_the_borrower_nothing():
    """The qualifier that matters: 'not financed by the new loan'.

    APP-000022 is a rate-and-term refinance with a $313,148 payoff against a
    $381,888 new loan. The loan retires the lien — that is what a refinance is —
    so the borrower brings closing costs and prepaids, not the balance.
    """
    from src.application_context import build_underwriting_input
    from src.config import REPO_ROOT

    packet = build_underwriting_input(
        REPO_ROOT / "synthetic_data/mortgage/applications/APP-000022.json"
    )
    amounts = compute_affordability(MORTGAGE, packet)["amounts"]

    assert amounts["lien_payoff_total"] == pytest.approx(313148.16)
    assert amounts["lien_payoff_financed_by_new_loan"] == pytest.approx(313148.16)
    assert amounts["funds_to_close_required"] == pytest.approx(10168.29)
    assert amounts["funds_to_close_required"] < amounts["funds_to_close_available"]


def test_a_purchase_has_no_payoff_and_keeps_its_down_payment(figures):
    amounts = figures("APP-000001")["amounts"]
    assert amounts["lien_payoff_total"] == pytest.approx(0.0)
    assert amounts["lien_payoff_financed_by_new_loan"] == pytest.approx(0.0)
    # 80,000 down plus costs, less credits.
    assert amounts["funds_to_close_required"] == pytest.approx(75687.85)


def test_cash_out_proceeds_reduce_what_the_borrower_brings(figures):
    """On a cash-out refinance the borrower receives money at the table."""
    amounts = figures("APP-000023")["amounts"]
    assert amounts["funds_to_close_required"] < 0, (
        "a borrower taking cash out should not be required to bring cash"
    )


def test_a_genuine_shortfall_still_fails(figures):
    """The fix must not make the sufficiency test toothless.

    APP-000006 is a purchase whose verified assets fall $23,080 short. No
    compensating factor cures it (AST-FTC-003), and nothing above should have
    made it pass.
    """
    amounts = figures("APP-000006")["amounts"]
    assert amounts["funds_to_close_available"] < amounts["funds_to_close_required"]
    assert amounts["funds_to_close_surplus"] == pytest.approx(-23080.86)


# ---------------------------------------------------------------- the components


def test_every_component_is_stored_separately(figures):
    """AST-FTC-001: 'a single net figure with no components cannot be reconciled'."""
    components = figures("APP-000001")["funds_to_close_components"]
    assert set(components) == {
        "down_payment_amount", "closing_costs", "prepaids_and_escrow",
        "unfinanced_payoff", "seller_credits", "lender_credits",
        "earnest_money_paid", "cash_out_proceeds",
    }


def test_the_components_sum_to_the_required_figure(figures):
    """The headline number has to reconcile to its own parts."""
    calculations = figures("APP-000022")
    total = sum(calculations["funds_to_close_components"].values())
    assert total == pytest.approx(calculations["amounts"]["funds_to_close_required"])


@pytest.mark.parametrize("application_id", ["APP-000001", "APP-000006", "APP-000022", "APP-000023"])
def test_credits_are_carried_as_negatives_not_silently_dropped(figures, application_id):
    components = figures(application_id)["funds_to_close_components"]
    for credit in ("seller_credits", "lender_credits", "earnest_money_paid", "cash_out_proceeds"):
        assert components[credit] <= 0, f"{credit} should reduce required funds"


# -------------------------------------------------------------------- reserves


def test_reserves_are_measured_after_the_draw_not_before(figures):
    """AST-RSV-001, and the bug it caught.

    APP-000003 holds $132,711 liquid and must bring $101,531 to closing. Measured
    before the draw it looks like 40.7 months of reserves; measured after, as the
    rule requires, it is 9.6.
    """
    calculations = figures("APP-000003")
    amounts = calculations["amounts"]

    before_the_draw = amounts["funds_to_close_available"] / amounts["housing_expense_pitia"]
    assert before_the_draw > 40, "fixture no longer reproduces the overstatement"

    assert calculations["months_of_reserves"] == pytest.approx(9.5667, abs=0.01)
    assert amounts["reserve_eligible_assets_after_closing"] == pytest.approx(
        amounts["funds_to_close_available"] - amounts["funds_to_close_required"]
    )


def test_reserves_never_go_negative(figures):
    """A file that cannot close has no reserves; it does not have negative ones."""
    calculations = figures("APP-000006")
    assert calculations["amounts"]["funds_to_close_surplus"] < 0
    assert calculations["months_of_reserves"] == pytest.approx(0.0)
    assert calculations["amounts"]["reserve_eligible_assets_after_closing"] == pytest.approx(0.0)


def test_reserves_use_the_full_housing_expense_as_the_denominator(figures):
    """AST-RSV-001 is explicit: PITIA, not principal and interest alone.

    The smaller denominator overstates months of reserves by a wide margin on a
    high-leverage file.
    """
    calculations = figures("APP-000003")
    amounts = calculations["amounts"]
    assert amounts["housing_expense_pitia"] > amounts["principal_and_interest"]

    expected = (
        amounts["reserve_eligible_assets_after_closing"] / amounts["housing_expense_pitia"]
    )
    assert calculations["months_of_reserves"] == pytest.approx(expected, abs=0.01)


def test_the_formula_version_moved_with_the_formula(figures):
    """A changed calculation under an unchanged version is an unauditable figure."""
    assert figures("APP-000001")["formula_version"] == "mortgage-affordability-2.1"
