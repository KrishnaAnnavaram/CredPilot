"""Education-loan rule families: EDU-UW, EDU-RG, EDU-COS, EDU-INTL.

These four families decide 17 of the 20 education golden cases between them, and
until now none was evaluated against a threshold — the rules were retrieved and
cited, and then nothing compared them to anything.

Every number below is read out of the retrieved policy text at evaluation time.
The education corpus writes its parameters as prose tables with human-readable
row labels (``| Minimum loan amount | $1,000 per academic year |``) rather than
the backticked machine keys the mortgage corpus uses, so each family has a small
reader that pulls its own numbers out of its own rule. That is more parsing than
a shared extractor would need, and it is the right trade: a generic parser over
prose would silently pick up the wrong number from a neighbouring sentence, and
a wrong threshold is worse than an absent one.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Any, Mapping, Sequence

from src.rules import RuleEvaluation, Verdict, find_rule

#: Product codes the education corpus underwrites, and the EDU-UW rule that
#: publishes each one's criteria.
_UNDERWRITING_RULE_BY_PRODUCT = {
    "UG": "EDU-UW-001",
    "GR": "EDU-UW-002",
    "SP": "EDU-UW-003",
    "INTL": "EDU-UW-004",
    "REFI": "EDU-UW-005",
}


# ======================================================================================
# Reading numbers out of prose tables
# ======================================================================================


def _row(text: str, *labels: str) -> str | None:
    """The right-hand cell of the first table row whose label matches.

    Matching is on the label column only. Searching the whole rule for a pattern
    would find the same words in the paragraph underneath, which is how a
    "minimum 650" in an explanatory sentence ends up applied as the ceiling.
    """
    for line in (text or "").splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        label = cells[0].lower().replace("*", "")
        if any(l.lower() in label for l in labels):
            return cells[1]
    return None


_MONEY = re.compile(r"\$\s*([\d,]+(?:\.\d+)?)")
_PERCENT = re.compile(r"([\d.]+)\s*%")
_INT = re.compile(r"(?<![\d.])(\d{2,4})(?![\d.%])")


def _money_in(text: str | None) -> float | None:
    if not text:
        return None
    match = _MONEY.search(text)
    return float(match.group(1).replace(",", "")) if match else None


def _percent_in(text: str | None) -> float | None:
    if not text:
        return None
    match = _PERCENT.search(text)
    return float(match.group(1)) / 100.0 if match else None


def _score_in(text: str | None) -> float | None:
    """A FICO score in the 300-850 range, ignoring years, months and money."""
    if not text:
        return None
    for match in _INT.finditer(text.replace(",", "")):
        value = float(match.group(1))
        if 300 <= value <= 850:
            return value
    return None


def _indeterminate(
    rule_id: str, measure: str, detail: str, observed: float | None = None
) -> RuleEvaluation:
    return RuleEvaluation(
        rule_id=rule_id,
        citation="",
        measure=measure,
        verdict=Verdict.INDETERMINATE,
        observed=observed,
        detail=detail,
    )


def _missing(rule_id: str, measure: str, observed: float | None = None) -> RuleEvaluation:
    return _indeterminate(
        rule_id,
        measure,
        f"{rule_id} was not retrieved; absence of the rule is not permission "
        f"(POL-001 EDU-GOV, GEN-ELG-005)",
        observed,
    )


# ======================================================================================
# Facts off the packet
# ======================================================================================


def _bureau(packet: Mapping[str, Any], subject_type: str) -> dict[str, Any]:
    """The bureau pull for the borrower or the cosigner, whichever is asked for."""
    for row in packet.get("credit_bureau") or []:
        if str(row.get("subject_type", "")).lower() == subject_type:
            return dict(row)
    return {}


def _borrower_fico(packet: Mapping[str, Any]) -> float | None:
    score = _bureau(packet, "borrower").get("fico_score")
    return float(score) if score not in (None, "") else None


def _cosigner_fico(packet: Mapping[str, Any]) -> float | None:
    score = _bureau(packet, "cosigner").get("fico_score")
    return float(score) if score not in (None, "") else None


def _deciding_fico(packet: Mapping[str, Any]) -> tuple[float | None, str]:
    """The score the grade is assigned on.

    ``EDU-RG-001``: where a cosigner is present the stronger of the two profiles
    grades the file. Which one it was travels with the number, because "740"
    means something different depending on whose it is.
    """
    borrower, cosigner = _borrower_fico(packet), _cosigner_fico(packet)
    if cosigner is not None and (borrower is None or cosigner > borrower):
        return cosigner, "cosigner"
    return borrower, "borrower"


def _income_row(packet: Mapping[str, Any], subject_prefix: str) -> dict[str, Any]:
    for row in packet.get("income_verification") or []:
        if str(row.get("subject_id", "")).upper().startswith(subject_prefix):
            return dict(row)
    return {}


def _cosigner_dti(packet: Mapping[str, Any]) -> float | None:
    value = _income_row(packet, "COSIG").get("dti_pct")
    return float(value) if value not in (None, "") else None


def _file_status(packet: Mapping[str, Any]) -> str:
    return str(_bureau(packet, "borrower").get("file_status", "")).upper()


def _has_cosigner(packet: Mapping[str, Any]) -> bool:
    return bool(packet.get("has_cosigner")) or bool(packet.get("cosigner"))


def _borrower_age(packet: Mapping[str, Any]) -> int | None:
    age = (packet.get("borrower") or {}).get("age")
    return int(age) if age not in (None, "") else None


def _cosigner_age(packet: Mapping[str, Any]) -> int | None:
    """Cosigner age at application, from the date of birth on the packet."""
    cosigner = packet.get("cosigner") or {}
    dob = cosigner.get("dob")
    if not dob:
        return None
    try:
        born = date.fromisoformat(str(dob)[:10])
    except ValueError:
        return None
    reference = _as_of(packet) or date.today()
    return (
        reference.year - born.year
        - ((reference.month, reference.day) < (born.month, born.day))
    )


def _as_of(packet: Mapping[str, Any]) -> date | None:
    raw = packet.get("submitted_at") or packet.get("application_date")
    if not raw:
        return None
    try:
        return date.fromisoformat(str(raw)[:10])
    except ValueError:
        return None


# ======================================================================================
# EDU-UW — product underwriting criteria
# ======================================================================================


def evaluate_education_underwriting(
    calculations: Mapping[str, Any],
    packet: Mapping[str, Any],
    evidence: Sequence[Mapping[str, Any]],
) -> list[RuleEvaluation]:
    """Apply the EDU-UW rule for this file's product.

    Each product has exactly one EDU-UW rule and they are not
    interchangeable — a GR file judged against UG's criteria would be judged
    against a cosigner requirement it does not have and a loan cap three times
    too low. So the rule is selected by product code and a file whose product is
    unknown is INDETERMINATE rather than defaulted to anything.
    """
    product = str(packet.get("product_code", "")).upper()
    rule_id = _UNDERWRITING_RULE_BY_PRODUCT.get(product)
    if rule_id is None:
        return [
            _indeterminate(
                "EDU-UW-001",
                "product_underwriting",
                f"product code {product or '(absent)'!r} is not one this corpus "
                f"publishes underwriting criteria for",
            )
        ]

    rule = find_rule(evidence, rule_id)
    if rule is None:
        return [_missing(rule_id, "product_underwriting")]

    text = str(rule.get("text") or "")
    citation = str(rule.get("citation") or "")
    evaluations: list[RuleEvaluation] = []
    requested = _amount(calculations, packet)

    # -- loan amount within the product's per-year band ------------------------
    minimum = _money_in(_row(text, "minimum loan amount"))
    maximum = _money_in(_row(text, "maximum loan amount"))
    if requested is None:
        evaluations.append(
            _indeterminate(rule_id, "requested_amount", "no requested amount on the file")
        )
    elif minimum is None and maximum is None:
        evaluations.append(
            _indeterminate(
                rule_id, "requested_amount",
                f"{rule_id} was retrieved but publishes no loan amount band",
                requested,
            )
        )
    else:
        if minimum is not None and requested < minimum:
            evaluations.append(
                RuleEvaluation(
                    rule_id=rule_id, citation=citation, measure="requested_amount", unit="currency",
                    verdict=Verdict.FAIL, observed=requested, threshold=minimum,
                    comparator=">=",
                    detail=f"{product} minimum is ${minimum:,.0f} per academic year",
                )
            )
        elif maximum is not None and requested > maximum:
            evaluations.append(
                RuleEvaluation(
                    rule_id=rule_id, citation=citation, measure="requested_amount", unit="currency",
                    verdict=Verdict.FAIL, observed=requested, threshold=maximum,
                    comparator="<=",
                    detail=f"{product} maximum is ${maximum:,.0f} per academic year",
                )
            )
        else:
            evaluations.append(
                RuleEvaluation(
                    rule_id=rule_id, citation=citation, measure="requested_amount", unit="currency",
                    verdict=Verdict.PASS, observed=requested,
                    threshold=maximum if maximum is not None else minimum,
                    comparator="<=" if maximum is not None else ">=",
                    detail=(
                        f"within the {product} band "
                        f"${minimum or 0:,.0f}–${maximum or 0:,.0f} per academic year"
                    ),
                )
            )

    # -- solo credit floor, and whether a cosigner is required -----------------
    evaluations.extend(
        _underwriting_credit(rule_id, citation, text, product, packet)
    )

    # -- residency / enrolment knockouts the rule states -----------------------
    evaluations.extend(_underwriting_status(rule_id, citation, text, product, packet))

    return evaluations


def _amount(calculations: Mapping[str, Any], packet: Mapping[str, Any]) -> float | None:
    value = (calculations.get("amounts") or {}).get("requested_amount")
    if value in (None, ""):
        value = packet.get("requested_amount")
    return float(value) if value not in (None, "") else None


def _underwriting_credit(
    rule_id: str, citation: str, text: str, product: str, packet: Mapping[str, Any]
) -> list[RuleEvaluation]:
    """The product's credit floor and its cosigner rule.

    Two different tests, and conflating them is the common mistake: a file below
    the *no-cosigner* bar with a cosigner present passes, and a file below the
    *absolute* floor fails whatever it has attached.
    """
    borrower = _borrower_fico(packet)
    has_cosigner = _has_cosigner(packet)
    out: list[RuleEvaluation] = []

    floor = (
        _score_in(_row(text, "solo borrower fico minimum", "minimum fico",
                       "credit score minimum"))
    )
    if floor is not None:
        if borrower is None:
            out.append(
                _indeterminate(rule_id, "borrower_fico",
                               "no borrower bureau score on the file")
            )
        elif borrower >= floor:
            out.append(
                RuleEvaluation(
                    rule_id=rule_id, citation=citation, measure="borrower_fico", unit="score",
                    verdict=Verdict.PASS, observed=borrower, threshold=floor,
                    comparator=">=",
                    detail=f"{product} borrower score floor {floor:.0f}",
                )
            )
        elif has_cosigner and product != "REFI":
            # REFI publishes "no cosigner pathway available"; every other
            # product lets a cosigner cure a borrower below the floor.
            out.append(
                RuleEvaluation(
                    rule_id=rule_id, citation=citation, measure="borrower_fico", unit="score",
                    verdict=Verdict.PASS, observed=borrower, threshold=floor,
                    comparator=">=",
                    detail=(
                        f"borrower score {borrower:.0f} is below the {product} floor "
                        f"of {floor:.0f}, cured by a cosigner; the cosigner is tested "
                        f"separately under EDU-COS-001"
                    ),
                    factors=["cosigner_present"],
                )
            )
        else:
            out.append(
                RuleEvaluation(
                    rule_id=rule_id, citation=citation, measure="borrower_fico", unit="score",
                    verdict=Verdict.FAIL, observed=borrower, threshold=floor,
                    comparator=">=",
                    detail=(
                        f"{product} requires at least {floor:.0f} and "
                        + (
                            "this product has no cosigner pathway"
                            if product == "REFI"
                            else "no cosigner was provided"
                        )
                    ),
                )
            )

    # The UG/INTL cosigner requirement is conditional on the borrower's profile.
    requirement = _row(text, "cosigner requirement")
    if requirement:
        required_below = _score_in(requirement)
        thin = _file_status(packet) in ("THIN", "NO_FILE")
        needs = False
        why: list[str] = []
        if required_below is not None and borrower is not None and borrower < required_below:
            needs, _ = True, why.append(
                f"borrower FICO {borrower:.0f} is below {required_below:.0f}"
            )
        if thin:
            needs, _ = True, why.append(f"the borrower's file is {_file_status(packet)}")
        age = _borrower_age(packet)
        if age is not None and age < 18 and "under 18" in text.lower():
            needs, _ = True, why.append(f"the borrower is {age}")

        if needs:
            out.append(
                RuleEvaluation(
                    rule_id=rule_id, citation=citation, measure="cosigner_required", unit="boolean",
                    verdict=Verdict.PASS if has_cosigner else Verdict.FAIL,
                    observed=1.0 if has_cosigner else 0.0, threshold=1.0,
                    comparator=">=",
                    detail=(
                        f"{product} requires a cosigner here ({'; '.join(why)}); "
                        + ("one is present" if has_cosigner else "none was provided")
                    ),
                )
            )
        else:
            out.append(
                RuleEvaluation(
                    rule_id=rule_id, citation=citation, measure="cosigner_required", unit="boolean",
                    verdict=Verdict.NOT_APPLICABLE,
                    detail=f"{product} does not require a cosigner on this profile",
                )
            )
    return out


def _underwriting_status(
    rule_id: str, citation: str, text: str, product: str, packet: Mapping[str, Any]
) -> list[RuleEvaluation]:
    """Residency and enrolment conditions the product rule states as knockouts."""
    out: list[RuleEvaluation] = []
    lowered = text.lower()
    citizenship = str((packet.get("borrower") or {}).get("citizenship_status", "")).upper()
    certification = packet.get("school_certification") or {}
    intensity = str(certification.get("enrollment_intensity", "")).upper()

    # GR/SP: non-resident aliens must apply under INTL instead.
    if product in ("GR", "SP") and "non-resident alien" in lowered and citizenship:
        eligible = citizenship in ("US_CITIZEN", "PERM_RESIDENT", "DACA")
        out.append(
            RuleEvaluation(
                rule_id=rule_id, citation=citation, measure="residency_status",
                verdict=Verdict.PASS if eligible else Verdict.FAIL,
                detail=(
                    f"{product} requires a US citizen, permanent resident or DACA "
                    f"recipient; this borrower is {citizenship}"
                    + ("" if eligible else " and must apply under the INTL product")
                ),
            )
        )

    # INTL: half-time enrolment is not permitted.
    if product == "INTL" and "half-time not permitted" in lowered and intensity:
        full_time = intensity == "FULL_TIME"
        out.append(
            RuleEvaluation(
                rule_id=rule_id, citation=citation, measure="enrollment_intensity",
                verdict=Verdict.PASS if full_time else Verdict.FAIL,
                detail=(
                    f"INTL requires full-time enrolment; this file is {intensity}"
                ),
            )
        )

    # REFI: an active default is a knockout.
    if product == "REFI" and "active default" in lowered:
        statuses = {
            str(loan.get("status", "")).upper() for loan in (packet.get("existing_loans") or [])
        }
        in_default = bool(statuses & {"DEFAULT", "DEFAULTED", "CHARGE_OFF"})
        out.append(
            RuleEvaluation(
                rule_id=rule_id, citation=citation, measure="active_default",
                verdict=Verdict.FAIL if in_default else Verdict.PASS,
                detail=(
                    "an active default on any tradeline is a REFI knockout; "
                    + (f"statuses present: {sorted(statuses)}" if statuses
                       else "no existing-loan status indicates default")
                ),
            )
        )
    return out


# ======================================================================================
# EDU-RG — risk grading
# ======================================================================================

#: Grade bands are parsed from EDU-RG-001's table rather than written here. This
#: is only the set of grades that mean "decline", which the rule states in prose
#: beneath the table rather than in a cell.
_DECLINE_GRADES = frozenset({"E1", "E2", "E3"})


def evaluate_education_risk_grade(
    calculations: Mapping[str, Any],
    packet: Mapping[str, Any],
    evidence: Sequence[Mapping[str, Any]],
) -> list[RuleEvaluation]:
    """Assign the risk grade from EDU-RG-001's band table and apply its knockouts.

    Two conditions per band and the worse one governs: a 780 FICO at 44% DTI is
    not an A1, it is a C2. Getting that backwards would grade most thin files a
    grade or two better than policy allows, which is the direction that matters.
    """
    rule = find_rule(evidence, "EDU-RG-001")
    if rule is None:
        return [_missing("EDU-RG-001", "risk_grade")]

    text = str(rule.get("text") or "")
    citation = str(rule.get("citation") or "")
    bands = _grade_bands(text)
    if not bands:
        return [
            _indeterminate(
                "EDU-RG-001", "risk_grade",
                "EDU-RG-001 was retrieved but its grade-band table could not be read",
            )
        ]

    fico, whose = _deciding_fico(packet)
    dti = (calculations.get("ratios") or {}).get("education_dti")
    if fico is None:
        return [_indeterminate("EDU-RG-001", "risk_grade", "no bureau score on the file")]

    grade, band_dti = _assign_grade(bands, fico, dti)
    if grade is None:
        return [
            _indeterminate(
                "EDU-RG-001", "risk_grade",
                f"a {whose} score of {fico:.0f} falls outside every published band",
                fico,
            )
        ]

    out = [
        RuleEvaluation(
            rule_id="EDU-RG-001", citation=citation, measure="risk_grade", unit="score",
            verdict=Verdict.FAIL if grade in _DECLINE_GRADES else Verdict.PASS,
            observed=fico,
            threshold=band_dti,
            comparator="<=",
            detail=(
                f"graded {grade} on the {whose}'s FICO of {fico:.0f}"
                + (f" and a DTI of {dti:.2%}" if dti is not None else " (DTI unavailable)")
                + (
                    "; E-band is an automatic decline with no cosigner cure"
                    if grade in _DECLINE_GRADES
                    else ""
                )
            ),
            factors=[f"grade:{grade}", f"graded_on:{whose}"],
        )
    ]

    # D3 (580-599) is approvable only with a cosigner grading C3 or better.
    if grade == "D3" and "cosigner whose profile grades at c3 or above" in text.lower():
        cosigner = _cosigner_fico(packet)
        cosigner_grade = (
            _assign_grade(bands, cosigner, _cosigner_dti(packet))[0] if cosigner else None
        )
        acceptable = cosigner_grade is not None and _grade_rank(
            cosigner_grade
        ) <= _grade_rank("C3")
        out.append(
            RuleEvaluation(
                rule_id="EDU-RG-001", citation=citation, measure="d3_cosigner_cure", unit="score",
                verdict=Verdict.PASS if acceptable else Verdict.FAIL,
                observed=cosigner,
                detail=(
                    "a D3 file is approvable only with a cosigner grading C3 or "
                    "better; "
                    + (
                        f"the cosigner grades {cosigner_grade}"
                        if cosigner_grade
                        else "no qualifying cosigner is on the file"
                    )
                ),
            )
        )
    return out


def _grade_bands(text: str) -> list[tuple[str, float, float | None]]:
    """``[(grade, fico_minimum, dti_maximum)]``, read out of EDU-RG-001's table."""
    bands: list[tuple[str, float, float | None]] = []
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        grade = cells[0].replace("*", "").strip()
        if not re.fullmatch(r"[A-E][123]", grade):
            continue
        # "< 540" is the bottom band and states a *ceiling*, not a floor, so it
        # has to be recognised before the number is read as a minimum. Reading
        # it as a floor of 540 left every applicant below 540 matching no band
        # at all, and the hardest decline in the policy — "automatically
        # declined, no cosigner cure, no exception pathway" — came back as
        # INDETERMINATE, which refers. That is the wrong direction for the one
        # rule the corpus calls a hard knockout.
        if re.search(r"<\s*\d{3}", cells[1]):
            fico = 0.0
        else:
            fico = _score_in(cells[1])
        if fico is None:
            continue
        bands.append((grade, fico, _percent_in(cells[2])))
    return sorted(bands, key=lambda b: -b[1])


def _grade_rank(grade: str) -> int:
    """Lower is better. A1 is 0, E3 is 14."""
    letters = "ABCDE"
    if len(grade) != 2 or grade[0] not in letters:
        return 99
    return letters.index(grade[0]) * 3 + (int(grade[1]) - 1)


def _assign_grade(
    bands: Sequence[tuple[str, float, float | None]],
    fico: float | None,
    dti: float | None,
) -> tuple[str | None, float | None]:
    """The grade a profile earns. Where FICO and DTI disagree, the worse governs."""
    if fico is None:
        return None, None
    by_fico = next(((g, f, d) for g, f, d in bands if fico >= f), None)
    if by_fico is None:
        return None, None
    if dti is None:
        return by_fico[0], by_fico[2]

    # The best band whose DTI ceiling this file also clears. Bands with no
    # published ceiling (the E rows) are declines and do not constrain.
    by_dti = next(
        ((g, f, d) for g, f, d in bands if d is not None and dti <= d), None
    )
    if by_dti is None:
        # Worse than every published DTI ceiling — the bottom band governs.
        worst = min(bands, key=lambda b: b[1])
        return worst[0], worst[2]
    worse = by_fico if _grade_rank(by_fico[0]) >= _grade_rank(by_dti[0]) else by_dti
    return worse[0], worse[2]


# ======================================================================================
# EDU-COS — cosigner qualification
# ======================================================================================


def evaluate_education_cosigner(
    calculations: Mapping[str, Any],
    packet: Mapping[str, Any],
    evidence: Sequence[Mapping[str, Any]],
) -> list[RuleEvaluation]:
    """Qualify the cosigner against EDU-COS-001 to -003.

    Only runs where a cosigner exists. A file with no cosigner is not a cosigner
    failure — whether it *needed* one is EDU-UW's question, answered above — so
    this returns NOT_APPLICABLE rather than FAIL, which would decline every solo
    graduate borrower in the book.
    """
    if not _has_cosigner(packet):
        return [
            RuleEvaluation(
                rule_id="EDU-COS-001", citation="", measure="cosigner_eligibility",
                verdict=Verdict.NOT_APPLICABLE,
                detail="no cosigner on the file; whether one is required is EDU-UW's test",
            )
        ]

    rule = find_rule(evidence, "EDU-COS-001")
    if rule is None:
        return [_missing("EDU-COS-001", "cosigner_eligibility")]

    text = str(rule.get("text") or "")
    citation = str(rule.get("citation") or "")
    cosigner = packet.get("cosigner") or {}
    bureau = _bureau(packet, "cosigner")
    out: list[RuleEvaluation] = []

    # -- citizenship -----------------------------------------------------------
    status = str(cosigner.get("citizenship_status", "")).upper()
    if status:
        eligible = status in ("US_CITIZEN", "PERM_RESIDENT")
        out.append(
            RuleEvaluation(
                rule_id="EDU-COS-001", citation=citation, measure="cosigner_citizenship",
                verdict=Verdict.PASS if eligible else Verdict.FAIL,
                detail=(
                    f"a cosigner must be a US citizen or permanent resident; this "
                    f"one is {status}"
                ),
            )
        )

    # -- minimum age -----------------------------------------------------------
    min_age_cell = _row(text, "minimum age")
    min_age = None
    if min_age_cell:
        match = re.search(r"(\d{2})", min_age_cell)
        min_age = float(match.group(1)) if match else None
    age = _cosigner_age(packet)
    if min_age is not None:
        if age is None:
            out.append(
                _indeterminate("EDU-COS-001", "cosigner_age",
                               "the cosigner's date of birth is not on the file")
            )
        else:
            out.append(
                RuleEvaluation(
                    rule_id="EDU-COS-001", citation=citation, measure="cosigner_age", unit="years",
                    verdict=Verdict.PASS if age >= min_age else Verdict.FAIL,
                    observed=float(age), threshold=min_age, comparator=">=",
                    detail=f"a cosigner must be at least {min_age:.0f} at application",
                )
            )

    # -- FICO floor ------------------------------------------------------------
    floor = _score_in(_row(text, "fico score"))
    score = _cosigner_fico(packet)
    if floor is not None:
        if score is None:
            out.append(
                _indeterminate("EDU-COS-001", "cosigner_fico",
                               "no cosigner bureau score on the file")
            )
        else:
            out.append(
                RuleEvaluation(
                    rule_id="EDU-COS-001", citation=citation, measure="cosigner_fico", unit="score",
                    verdict=Verdict.PASS if score >= floor else Verdict.FAIL,
                    observed=score, threshold=floor, comparator=">=",
                    detail=f"the cosigner score floor is {floor:.0f}",
                )
            )

    # -- bankruptcy and sanctions knockouts ------------------------------------
    if bureau:
        bankrupt = bool(bureau.get("bankruptcy_flag"))
        out.append(
            RuleEvaluation(
                rule_id="EDU-COS-001", citation=citation, measure="cosigner_bankruptcy",
                verdict=Verdict.FAIL if bankrupt else Verdict.PASS,
                detail=(
                    "an active bankruptcy filing disqualifies a cosigner"
                    if bankrupt
                    else "no active bankruptcy on the cosigner's file"
                ),
            )
        )

    screening = packet.get("fraud_screening") or {}
    if "ofac" in text.lower() and screening:
        hit = bool(screening.get("ofac_hit"))
        out.append(
            RuleEvaluation(
                rule_id="EDU-COS-001", citation=citation, measure="sanctions_screening",
                verdict=Verdict.FAIL if hit else Verdict.PASS,
                detail="an OFAC match is a knockout with no exception",
            )
        )

    # -- cosigner DTI ceiling, EDU-COS-002 -------------------------------------
    dti_rule = find_rule(evidence, "EDU-COS-002")
    cosigner_dti = _cosigner_dti(packet)
    if dti_rule is None:
        out.append(_missing("EDU-COS-002", "cosigner_dti", cosigner_dti))
    elif cosigner_dti is None:
        out.append(
            _indeterminate("EDU-COS-002", "cosigner_dti",
                           "no verified cosigner income on the file")
        )
    else:
        ceiling = _percent_in(str(dti_rule.get("text") or ""))
        if ceiling is None:
            out.append(
                _indeterminate("EDU-COS-002", "cosigner_dti",
                               "EDU-COS-002 was retrieved but publishes no ceiling",
                               cosigner_dti)
            )
        else:
            out.append(
                RuleEvaluation(
                    rule_id="EDU-COS-002",
                    citation=str(dti_rule.get("citation") or ""),
                    measure="cosigner_dti",
                    verdict=Verdict.PASS if cosigner_dti <= ceiling else Verdict.FAIL,
                    observed=cosigner_dti, threshold=ceiling, comparator="<=",
                    detail=(
                        f"the cosigner ceiling is {ceiling:.0%}, higher than the "
                        f"borrower's because the obligation is contingent; a breach "
                        f"refers rather than declines"
                    ),
                )
            )

    # -- Reg Z notice, EDU-COS-003 ---------------------------------------------
    notice_rule = find_rule(evidence, "EDU-COS-003")
    if notice_rule is not None:
        acknowledged = bool(cosigner.get("cosigner_notice_acknowledged"))
        out.append(
            RuleEvaluation(
                rule_id="EDU-COS-003",
                citation=str(notice_rule.get("citation") or ""),
                measure="cosigner_notice_acknowledged",
                verdict=Verdict.PASS if acknowledged else Verdict.FAIL,
                detail=(
                    "Regulation Z requires the signed cosigner notice before "
                    "disbursement; missing acknowledgment is a compliance knockout"
                ),
            )
        )
    return out


# ======================================================================================
# EDU-INTL — international student lending
# ======================================================================================

_ELIGIBLE_VISAS = ("F-1", "J-1")


def evaluate_education_international(
    calculations: Mapping[str, Any],
    packet: Mapping[str, Any],
    evidence: Sequence[Mapping[str, Any]],
) -> list[RuleEvaluation]:
    """Apply the EDU-INTL family to an international file.

    Only runs on the INTL product. The corpus publishes these rules for INTL
    alone, and applying a visa test to a domestic undergraduate would fail every
    one of them for want of a visa nobody asked for.
    """
    product = str(packet.get("product_code", "")).upper()
    if product != "INTL":
        return [
            RuleEvaluation(
                rule_id="EDU-INTL-001", citation="", measure="international_eligibility",
                verdict=Verdict.NOT_APPLICABLE,
                detail=f"the EDU-INTL family governs the INTL product; this is {product or 'unknown'}",
            )
        ]

    details = packet.get("international_details") or {}
    out: list[RuleEvaluation] = []

    # -- EDU-INTL-001 visa class ----------------------------------------------
    visa_rule = find_rule(evidence, "EDU-INTL-001")
    visa = str(details.get("visa_type", "")).upper()
    if visa_rule is None:
        out.append(_missing("EDU-INTL-001", "visa_eligibility"))
    elif not visa:
        out.append(
            _indeterminate("EDU-INTL-001", "visa_eligibility",
                           "no visa classification on the file")
        )
    else:
        eligible = visa in _ELIGIBLE_VISAS
        out.append(
            RuleEvaluation(
                rule_id="EDU-INTL-001",
                citation=str(visa_rule.get("citation") or ""),
                measure="visa_eligibility",
                verdict=Verdict.PASS if eligible else Verdict.FAIL,
                detail=(
                    f"only F-1 and J-1 holders are eligible for the INTL product; "
                    f"this applicant holds {visa}"
                ),
            )
        )

    # -- EDU-INTL-003 I-94 verification ---------------------------------------
    # An unverifiable I-94 is explicitly REFER_MANUAL, not a decline: the record
    # may simply not be retrievable, and refusing the applicant for a CBP
    # outage is the wrong answer.
    i94_rule = find_rule(evidence, "EDU-INTL-003")
    if i94_rule is not None:
        verified = bool(details.get("i94_verified"))
        out.append(
            RuleEvaluation(
                rule_id="EDU-INTL-003",
                citation=str(i94_rule.get("citation") or ""),
                measure="i94_verification",
                verdict=Verdict.PASS if verified else Verdict.INDETERMINATE,
                detail=(
                    "the I-94 confirms lawful admission and current status"
                    if verified
                    else "the I-94 could not be verified; EDU-INTL-003 makes this "
                         "REFER_MANUAL for an underwriter to resolve, not a decline"
                ),
            )
        )

    # -- EDU-INTL-004 no-cosigner pathway --------------------------------------
    pathway_rule = find_rule(evidence, "EDU-INTL-004")
    if pathway_rule is not None and not _has_cosigner(packet):
        text = str(pathway_rule.get("text") or "")
        months_required = _months_in(text) or 12.0
        tier = str((packet.get("school") or {}).get("school_risk_tier", "")).upper()
        opt = bool(details.get("opt_eligible"))
        months = details.get("post_study_work_months")
        months = float(months) if months not in (None, "") else None

        unmet: list[str] = []
        if tier not in ("A", "B"):
            unmet.append(f"the school is Tier {tier or '?'}, not Tier A or B")
        if not opt:
            unmet.append("the applicant is not OPT-eligible")
        if months is None:
            unmet.append("post-study work authorization is not stated")
        elif months < months_required:
            unmet.append(
                f"{months:.0f} months of post-study work authorization, below the "
                f"{months_required:.0f} required"
            )

        out.append(
            RuleEvaluation(
                rule_id="EDU-INTL-004",
                citation=str(pathway_rule.get("citation") or ""),
                measure="no_cosigner_pathway", unit="months",
                verdict=Verdict.PASS if not unmet else Verdict.FAIL,
                observed=months,
                threshold=months_required,
                comparator=">=",
                detail=(
                    "the no-cosigner pathway is satisfied in full"
                    if not unmet
                    else "no cosigner was provided and the no-cosigner pathway is not "
                         "satisfied: " + "; ".join(unmet)
                ),
            )
        )
    elif pathway_rule is not None:
        out.append(
            RuleEvaluation(
                rule_id="EDU-INTL-004",
                citation=str(pathway_rule.get("citation") or ""),
                measure="no_cosigner_pathway", unit="months",
                verdict=Verdict.NOT_APPLICABLE,
                detail="a cosigner is present, so the no-cosigner pathway is not in play",
            )
        )

    # -- EDU-INTL-005 cosigner must be a US citizen or permanent resident ------
    cosigner_rule = find_rule(evidence, "EDU-INTL-005")
    if cosigner_rule is not None and _has_cosigner(packet):
        status = str((packet.get("cosigner") or {}).get("citizenship_status", "")).upper()
        ok = status in ("US_CITIZEN", "PERM_RESIDENT")
        out.append(
            RuleEvaluation(
                rule_id="EDU-INTL-005",
                citation=str(cosigner_rule.get("citation") or ""),
                measure="intl_cosigner_status",
                verdict=Verdict.PASS if ok else Verdict.FAIL,
                detail=(
                    f"an INTL cosigner must be a US citizen or permanent resident; "
                    f"this one is {status or 'unstated'}"
                ),
            )
        )
    return out


def _months_in(text: str) -> float | None:
    match = re.search(r"\*\*(\d{1,3})\*\*\s*months|(\d{1,3})\s*months", text)
    if not match:
        return None
    return float(match.group(1) or match.group(2))


# ======================================================================================
# Dispatch
# ======================================================================================


def evaluate_education_families(
    calculations: Mapping[str, Any],
    packet: Mapping[str, Any],
    evidence: Sequence[Mapping[str, Any]],
) -> list[RuleEvaluation]:
    """Every extended education family, in the order POL-001 evaluates them."""
    return [
        *evaluate_education_underwriting(calculations, packet, evidence),
        *evaluate_education_cosigner(calculations, packet, evidence),
        *evaluate_education_international(calculations, packet, evidence),
        *evaluate_education_risk_grade(calculations, packet, evidence),
    ]


__all__ = [
    "evaluate_education_cosigner",
    "evaluate_education_families",
    "evaluate_education_international",
    "evaluate_education_risk_grade",
    "evaluate_education_underwriting",
]
