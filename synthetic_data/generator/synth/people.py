"""
Synthetic person construction.

No third-party name generator is used. The pools below are deliberately small,
ordinary and committed, so the same seed produces the same people on any machine
with no network access and no extra dependency - which is what the Reproducibility
Rule (REQ-033) actually requires.

Every person is fictional. Sensitive identifiers are minted as SYN- tokens and are
only ever rendered in masked form. Telephone numbers use the reserved 555-0100 to
555-0199 block and e-mail uses the reserved example.com domain, so nothing generated
here can reach a real person.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from random import Random

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from synthetic_data_utils import (  # noqa: E402
    borrower_id,
    mask_account,
    mask_credit,
    mask_ssn,
    syn_account_token,
    syn_credit_token,
    syn_email,
    syn_phone,
    syn_ssn_token,
)

GIVEN_NAMES = (
    "Alex", "Jordan", "Priya", "Marcus", "Elena", "Devon", "Nadia", "Tobias",
    "Camille", "Rashid", "Ingrid", "Felix", "Yara", "Oscar", "Lena", "Mateo",
    "Sofia", "Isaac", "Ruth", "Kenji", "Amara", "Victor", "Noor", "Gregor",
    "Iris", "Malik", "Bianca", "Theo", "Salma", "Hugo", "Delia", "Anton",
    "Freya", "Omar", "Junie", "Caleb", "Rosa", "Niall", "Mira", "Vincent",
    "Talia", "Emeka", "Greta", "Silas", "Winona", "Andre", "Paloma", "Everett",
)

FAMILY_NAMES = (
    "Whitfield", "Okafor", "Lindqvist", "Marchetti", "Delacroix", "Abernathy",
    "Castellanos", "Nakamura", "Thornbury", "Vasquez", "Ellingsworth", "Baptiste",
    "Kowalczyk", "Ferreira", "Hollingsworth", "Adeyemi", "Sorensen", "Mbeki",
    "Ravenscroft", "Quintero", "Brennerman", "Fairbanks", "Ivanova", "Solberg",
    "Pemberton", "Achterberg", "Guerrero", "Lindstrom", "Waverly", "Osei",
    "Chandrasekar", "Moreau", "Ashworth", "Kirilenko", "Underhill", "Nakagawa",
    "Saldivar", "Blackwood", "Petrosyan", "Hargrave",
)

STREET_NAMES = (
    "Alderwood Lane", "Bramblewood Court", "Cedarhollow Drive", "Draycott Way",
    "Elmridge Terrace", "Fennimore Street", "Gullwing Road", "Havenbrook Lane",
    "Innisfree Court", "Juniper Bend", "Kestrel Ridge", "Larkspur Avenue",
    "Meadowvane Drive", "Nightingale Close", "Orchardstone Way", "Pemberly Road",
    "Quarrystone Lane", "Rosslyn Terrace", "Stonebriar Court", "Thistledown Drive",
    "Umberwood Place", "Verdigris Lane", "Windermere Court", "Yarrowfield Road",
)

#: City / state / ZIP-style value / area code. Place names are public geography, not
#: personal data; the street addresses attached to them are fictional.
LOCALES = (
    ("Plano", "TX", "75024", "972"),
    ("Naperville", "IL", "60540", "630"),
    ("Chandler", "AZ", "85224", "480"),
    ("Cary", "NC", "27513", "919"),
    ("Bellevue", "WA", "98004", "425"),
    ("Overland Park", "KS", "66210", "913"),
    ("Franklin", "TN", "37067", "615"),
    ("Beaverton", "OR", "97006", "503"),
    ("Sandy Springs", "GA", "30328", "770"),
    ("Broomfield", "CO", "80020", "303"),
    ("Nashua", "NH", "03062", "603"),
    ("Cranston", "RI", "02910", "401"),
    ("Sugar Land", "TX", "77479", "281"),
    ("Rochester Hills", "MI", "48307", "248"),
    ("Yorba Linda", "CA", "92886", "714"),
    ("Coral Springs", "FL", "33071", "954"),
)

#: Fictional employers. Named so no real company's payroll appears in the data.
EMPLOYERS = (
    ("Harborline Logistics", "logistics"),
    ("Meridian Civic Health", "healthcare"),
    ("Blue Larkspur Manufacturing", "manufacturing"),
    ("Cartwright & Vale Advisory", "professional_services"),
    ("Northgate Public Schools", "education"),
    ("Sable Ridge Software", "technology"),
    ("Pinewater Utilities District", "utilities"),
    ("Kestrel Freight Services", "transport"),
    ("Aldermill Retail Group", "retail"),
    ("Orchard Point Hospitality", "hospitality"),
    ("Fenwick Structural Engineering", "engineering"),
    ("Grayson Municipal Authority", "public_sector"),
    ("Thornhill Insurance Brokers", "insurance"),
    ("Silverbrook Diagnostics", "healthcare"),
    ("Latchford Construction", "construction"),
    ("Verity Loom Textiles", "manufacturing"),
)

OCCUPATIONS = {
    "logistics": ("Operations Supervisor", "Warehouse Planner", "Fleet Coordinator"),
    "healthcare": ("Registered Nurse", "Clinical Technologist", "Practice Manager"),
    "manufacturing": ("Production Lead", "Quality Engineer", "Maintenance Technician"),
    "professional_services": ("Senior Consultant", "Account Director", "Analyst"),
    "education": ("Classroom Teacher", "Curriculum Coordinator", "School Counsellor"),
    "technology": ("Software Engineer", "Systems Analyst", "Product Manager"),
    "utilities": ("Field Supervisor", "Grid Technician", "Compliance Officer"),
    "transport": ("Route Manager", "Dispatch Lead", "Logistics Planner"),
    "retail": ("Store Manager", "Merchandise Planner", "District Supervisor"),
    "hospitality": ("Operations Manager", "Events Director", "Front Office Manager"),
    "engineering": ("Structural Engineer", "Project Engineer", "Design Lead"),
    "public_sector": ("Programme Officer", "Records Administrator", "Inspector"),
    "insurance": ("Claims Adjuster", "Underwriting Assistant", "Broker"),
    "construction": ("Site Supervisor", "Estimator", "Project Coordinator"),
    "textiles": ("Production Planner", "Quality Lead", "Line Supervisor"),
}

BANKS = (
    "Northwind Community Bank",
    "Harbor Point Savings",
    "Cascade Mutual Credit Union",
    "Sablefield Trust",
)

BROKERAGES = ("Ravenscourt Securities", "Tidewater Investment Services")

CREDITORS = (
    "Northwind Card Services",
    "Pinnacle Auto Finance",
    "Summit Education Lending",
    "Harborline Retail Credit",
    "Cascade Personal Loans",
    "Sablefield Mortgage Servicing",
)


@dataclass
class Person:
    """One synthetic applicant."""

    borrower_id: str
    first_name: str
    last_name: str
    date_of_birth: date
    ssn_token: str
    ssn_masked: str
    email: str
    phone: str
    street: str
    city: str
    state: str
    postal_code: str
    prior_street: str | None
    prior_city: str | None
    prior_state: str | None
    prior_postal_code: str | None
    years_at_current_address: int
    marital_status: str
    dependents: int
    citizenship_status: str
    credit_file_token: str
    credit_file_masked: str
    employer: str
    employer_sector: str
    occupation: str

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def age_at(self, as_of: date) -> int:
        years = as_of.year - self.date_of_birth.year
        if (as_of.month, as_of.day) < (self.date_of_birth.month, self.date_of_birth.day):
            years -= 1
        return years


@dataclass
class Demographics:
    """Statutory monitoring attributes.

    Held on a separate record, written to a separate file, and deliberately NOT a
    field on :class:`Person`, so no code path that builds underwriting facts can
    reach them. See SEC-PII-002 and CRD-SCR-006.
    """

    borrower_id: str
    ethnicity: str
    race: str
    sex: str
    age_band: str
    collection_method: str


ETHNICITIES = ("Hispanic or Latino", "Not Hispanic or Latino", "Information not provided")
RACES = (
    "American Indian or Alaska Native",
    "Asian",
    "Black or African American",
    "Native Hawaiian or Other Pacific Islander",
    "White",
    "Information not provided",
)
SEXES = ("Female", "Male", "Information not provided")
COLLECTION_METHODS = ("Applicant provided", "Visual observation or surname", "Not provided")


def make_person(rng: Random, index: int, as_of: date, min_age: int = 24) -> Person:
    """Build one fictional applicant deterministically from `rng`."""
    first = GIVEN_NAMES[rng.randrange(len(GIVEN_NAMES))]
    last = FAMILY_NAMES[rng.randrange(len(FAMILY_NAMES))]
    age = rng.randint(min_age, 66)
    dob = date(
        as_of.year - age,
        rng.randint(1, 12),
        rng.randint(1, 28),
    )
    city, state, postal, area = LOCALES[rng.randrange(len(LOCALES))]
    years_here = rng.randint(1, 12)
    has_prior = years_here < 3
    prior = LOCALES[rng.randrange(len(LOCALES))] if has_prior else None
    employer, sector = EMPLOYERS[rng.randrange(len(EMPLOYERS))]
    occupations = OCCUPATIONS.get(sector, ("Specialist",))
    ssn = syn_ssn_token(index)
    credit_token = syn_credit_token(index)
    return Person(
        borrower_id=borrower_id(index),
        first_name=first,
        last_name=last,
        date_of_birth=dob,
        ssn_token=ssn,
        ssn_masked=mask_ssn(ssn),
        email=syn_email(first, last, index),
        phone=syn_phone(area, index),
        street=f"{rng.randint(100, 9899)} {STREET_NAMES[rng.randrange(len(STREET_NAMES))]}",
        city=city,
        state=state,
        postal_code=postal,
        prior_street=(
            f"{rng.randint(100, 9899)} {STREET_NAMES[rng.randrange(len(STREET_NAMES))]}"
            if prior
            else None
        ),
        prior_city=prior[0] if prior else None,
        prior_state=prior[1] if prior else None,
        prior_postal_code=prior[2] if prior else None,
        years_at_current_address=years_here,
        marital_status=rng.choice(["Married", "Unmarried", "Separated"]),
        dependents=rng.choice([0, 0, 1, 1, 2, 3]),
        citizenship_status=rng.choice(
            ["US Citizen", "US Citizen", "US Citizen", "Permanent Resident"]
        ),
        credit_file_token=credit_token,
        credit_file_masked=mask_credit(credit_token),
        employer=employer,
        employer_sector=sector,
        occupation=occupations[rng.randrange(len(occupations))],
    )


def make_demographics(rng: Random, person: Person, as_of: date) -> Demographics:
    """Monitoring attributes, generated independently of every underwriting fact.

    The generator draws these from their own RNG stream with no reference to the
    person's credit, income or outcome, so no statistical relationship exists between
    a monitoring attribute and a decision in this dataset. That is the property a
    fair-lending test on this data should be able to confirm.
    """
    age = person.age_at(as_of)
    if age < 25:
        band = "Under 25"
    elif age < 35:
        band = "25-34"
    elif age < 45:
        band = "35-44"
    elif age < 55:
        band = "45-54"
    elif age < 65:
        band = "55-64"
    else:
        band = "65 and over"
    return Demographics(
        borrower_id=person.borrower_id,
        ethnicity=ETHNICITIES[rng.randrange(len(ETHNICITIES))],
        race=RACES[rng.randrange(len(RACES))],
        sex=SEXES[rng.randrange(len(SEXES))],
        age_band=band,
        collection_method=COLLECTION_METHODS[rng.randrange(len(COLLECTION_METHODS))],
    )


def account_identifiers(index: int) -> tuple[str, str]:
    """A tokenised deposit account and its masked display form."""
    token = syn_account_token(index)
    return token, mask_account(token)
