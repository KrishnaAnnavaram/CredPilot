#!/usr/bin/env python3
"""
Synthetic Data Generator for Education Loan Origination Copilot.
Deterministic, seeded, re-runnable.  Produces JSON application files.
Lender: Edgemont Education Lending (fictional).

Usage:
    python generate_synthetic_data.py

Output:
    ../applications/APP-2026-XXXXX.json   (200 files)
    ../profiles/school_profiles.jsonl
    ../profiles/borrower_profiles.jsonl
    ../scenarios/scenario_catalog.json
"""

import json, os, random, math
from datetime import datetime, timedelta, date
from pathlib import Path
from collections import Counter

SEED = 20260901
random.seed(SEED)

BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "applications"
PROFILE_DIR = BASE_DIR / "profiles"
SCENARIO_DIR = BASE_DIR / "scenarios"
for d in [APP_DIR, PROFILE_DIR, SCENARIO_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── name pools ──────────────────────────────────────────────────────
FIRST = [
    "Aiden","Brielle","Carlos","Dina","Ethan","Fatima","Gavin","Hana",
    "Ivan","Jaya","Kenji","Lina","Marco","Noor","Oscar","Priya",
    "Quinn","Ravi","Sofia","Tariq","Uma","Victor","Wendy","Xander",
    "Yuki","Zara","Amara","Benicio","Celeste","Dmitri","Elena","Felix",
    "Gia","Hassan","Isla","Jamal","Kira","Leon","Mei","Nico",
    "Olivia","Pavel","Rosa","Sanjay","Tessa","Umar","Violet","Wesley",
    "Xiomara","Yosef","Ada","Blake","Camille","Derek","Esme","Farhan",
    "Grace","Hugo","Iris","Julian","Kaya","Lorenzo","Mina","Nathan",
    "Ophelia","Petra","Rafael","Sage","Theo","Ursula",
]
LAST = [
    "Aldridge","Bhatti","Castillo","Delacroix","Erikson","Fujimoto",
    "Gonzalez","Hartwell","Inoue","Johansson","Kowalski","Lambert",
    "Morales","Nakamura","Okafor","Petrov","Quintero","Ramirez",
    "Sato","Thornton","Ueda","Vasquez","Whitfield","Xu","Yamamoto",
    "Zhou","Andersen","Brennan","Cortez","Duval","Espinoza","Ferro",
    "Gutierrez","Holt","Ivanov","Jensen","Kaur","Leclerc","Mendoza",
    "Novak","Ortega","Park","Reyes","Singh","Tanaka","Underwood",
    "Volkov","Walsh","Yang","Zamora",
]
EMPLOYERS = [
    "Pinnacle Ridge Technologies","Silverlake Data Systems","Coastline Financial",
    "Redwood Consulting","Horizon Cloud Services","Ironbridge Manufacturing",
    "Crestview Medical Group","Bluewater Engineering","Summit Legal Associates",
    "Maple Street Capital","Northwind Analytics","Greenfield Solar Corp",
    "Cascade Supply Chain","Birchwood Retail","Ironforge Defense Systems",
    "Coral Bay Hospitality","Ashford Media Group","Stonebridge Construction",
    "Lakeside Pharmaceuticals","Prairie Wind Energy",
]
JOBS = [
    "Software Engineer","Marketing Manager","Registered Nurse","Financial Analyst",
    "Operations Manager","Sales Representative","Project Manager","Accountant",
    "HR Coordinator","Mechanical Engineer","Teacher","Pharmacist",
    "Admin Assistant","Research Scientist","Data Analyst","Physical Therapist",
]
SERVICERS = [
    "Clearpath Student Services","Horizon Loan Management",
    "National Education Servicing","Ridgeview Financial","Summit Student Lending",
]
STATES = [
    "CA","TX","NY","FL","IL","PA","OH","GA","NC","MI",
    "NJ","VA","WA","AZ","MA","TN","IN","MO","MD","WI",
    "CO","MN","SC","AL","LA","KY","OR","OK","CT","UT",
]
CITIES = {
    "CA":["Los Angeles","San Francisco","San Diego"],"TX":["Houston","Dallas","Austin"],
    "NY":["New York","Buffalo","Albany"],"FL":["Miami","Orlando","Tampa"],
    "IL":["Chicago","Springfield","Naperville"],"PA":["Philadelphia","Pittsburgh"],
    "OH":["Columbus","Cleveland","Cincinnati"],"GA":["Atlanta","Savannah"],
    "NC":["Charlotte","Raleigh","Durham"],"MI":["Detroit","Ann Arbor"],
    "MA":["Boston","Cambridge","Worcester"],"VA":["Richmond","Arlington"],
    "WA":["Seattle","Tacoma"],"AZ":["Phoenix","Tucson"],
}
PASSPORT_COUNTRIES = [
    "India","China","South Korea","Brazil","Nigeria","Japan","Mexico",
    "Germany","France","United Kingdom","Canada","Turkey","Vietnam",
    "Pakistan","Bangladesh","Thailand","Colombia","Kenya",
]

# ── 40 fictional schools ───────────────────────────────────────────
def _build_schools():
    raw = [
        ("Crestmont University","PUBLIC_4YR",True,"REGIONAL",True,3.2,85,58000,"A","US"),
        ("Harborview State University","PUBLIC_4YR",True,"REGIONAL",True,4.1,82,55000,"A","US"),
        ("Ridgeline College","PRIVATE_4YR",True,"REGIONAL",True,2.8,88,62000,"A","US"),
        ("Silverlake University","PRIVATE_4YR",True,"REGIONAL",True,4.5,80,56000,"A","US"),
        ("Pacific Crest University","PUBLIC_4YR",True,"REGIONAL",True,3.9,83,57000,"A","US"),
        ("Ironwood Institute of Technology","PRIVATE_4YR",True,"REGIONAL",True,5.0,81,60000,"A","US"),
        ("Westbridge University","PUBLIC_4YR",True,"REGIONAL",True,6.2,76,48000,"B","US"),
        ("Maplewood College","PRIVATE_4YR",True,"REGIONAL",True,7.1,72,45000,"B","US"),
        ("Cedar Falls University","PUBLIC_4YR",True,"REGIONAL",True,8.0,68,42000,"B","US"),
        ("Ashford State University","PUBLIC_4YR",True,"REGIONAL",True,6.8,74,47000,"B","US"),
        ("Thornfield College","PRIVATE_4YR",True,"REGIONAL",True,9.0,66,41000,"B","US"),
        ("Stonewall University","PUBLIC_4YR",True,"REGIONAL",True,7.5,70,44000,"B","US"),
        ("Birchwood Community College","COMMUNITY",True,"REGIONAL",True,11.0,55,32000,"C","US"),
        ("Valley View College","COMMUNITY",True,"REGIONAL",True,12.5,52,30000,"C","US"),
        ("Sunridge Technical Institute","PUBLIC_4YR",True,"NATIONAL",True,13.0,54,35000,"C","US"),
        ("Lakeside State College","PUBLIC_4YR",True,"REGIONAL",True,14.0,51,31000,"C","US"),
        ("Prairie Heights University","PUBLIC_4YR",True,"REGIONAL",True,11.5,58,34000,"C","US"),
        ("Greenfield Community College","COMMUNITY",True,"REGIONAL",True,13.5,53,33000,"C","US"),
        ("Desert Springs College","COMMUNITY",True,"REGIONAL",True,18.0,42,27000,"D","US"),
        ("Riverbend Career Institute","COMMUNITY",True,"NATIONAL",True,22.0,38,25000,"D","US"),
        ("Southgate Technical School","COMMUNITY",True,"REGIONAL",True,19.5,45,28000,"D","US"),
        ("Bayshore Academy","COMMUNITY",False,"NATIONAL",False,28.0,35,22000,"D","US"),
        ("Edgewater School of Medicine","PROFESSIONAL",True,"LCME",True,1.5,95,180000,"A","US"),
        ("Summit Law School","PROFESSIONAL",True,"ABA",True,3.0,88,95000,"A","US"),
        ("Crestmont School of Dentistry","PROFESSIONAL",True,"CODA",True,2.0,92,160000,"A","US"),
        ("Bridgeport MBA School","PROFESSIONAL",True,"AACSB",True,3.5,90,110000,"A","US"),
        ("Oakridge School of Pharmacy","PROFESSIONAL",True,"ACPE",True,4.0,85,120000,"A","US"),
        ("Northland School of Law","PROFESSIONAL",True,"ABA",True,8.5,72,68000,"B","US"),
        ("Prairie Medical College","PROFESSIONAL",True,"LCME",True,7.0,78,150000,"B","US"),
        ("Westfield School of Nursing","PROFESSIONAL",True,"CCNE",True,6.0,80,72000,"B","US"),
        ("Bayview Osteopathic School","PROFESSIONAL",True,"AOA",True,9.0,75,140000,"B","US"),
        ("Royal Kensington University","INTERNATIONAL_ELIGIBLE",False,"UK_QAA",True,3.0,90,65000,"A","United Kingdom"),
        ("Heidelberg Technical University","INTERNATIONAL_ELIGIBLE",False,"EUR_ECTS",True,4.0,85,58000,"A","Germany"),
        ("Maple Leaf University","INTERNATIONAL_ELIGIBLE",False,"CAN_AUCC",True,3.5,87,55000,"A","Canada"),
        ("Pacific Rim Business School","INTERNATIONAL_ELIGIBLE",False,"AACSB",True,6.5,78,52000,"B","Singapore"),
        ("Southern Cross University","INTERNATIONAL_ELIGIBLE",False,"AUS_TEQSA",True,7.0,75,48000,"B","Australia"),
        ("Pinnacle Online University","PRIVATE_4YR",True,"DEAC",True,16.0,48,29000,"D","US"),
        ("Harbor City State College","PUBLIC_4YR",True,"REGIONAL",True,10.0,62,38000,"B","US"),
        ("Summit Ridge Polytechnic","PUBLIC_4YR",True,"REGIONAL",True,5.5,79,51000,"A","US"),
        ("Clearwater Bible College","PRIVATE_4YR",True,"REGIONAL",False,14.5,60,30000,"C","US"),
    ]
    out = []
    for i, s in enumerate(raw):
        out.append(dict(
            school_id=f"SCH-{i+1:03d}", school_name=s[0], school_type=s[1],
            title_iv_eligible=s[2], accreditation_status=s[3], on_approved_list=s[4],
            cohort_default_rate_pct=s[5], completion_rate_pct=s[6],
            median_earnings_3yr_post=s[7], school_risk_tier=s[8], country=s[9]))
    return out

SCHOOLS = _build_schools()

# ── helpers ─────────────────────────────────────────────────────────
def rand_date(s, e):
    return s + timedelta(days=random.randint(0, max(0, (e - s).days)))

def rand_dt(s, e):
    d = rand_date(s, e)
    return datetime(d.year, d.month, d.day, random.randint(8, 17), random.randint(0, 59))

def masked_ssn(n): return f"XXX-XX-{n:04d}"
def rand_phone(): return f"({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}"

def rand_zip(st):
    ranges = {"CA":(90000,96199),"TX":(73301,79999),"NY":(10001,14999),"FL":(32004,34997),
              "IL":(60001,62999),"PA":(15001,19699),"OH":(43001,45999),"GA":(30001,31999)}
    lo, hi = ranges.get(st, (10000, 99999))
    return str(random.randint(lo, hi))

def rand_street():
    n = random.randint(100, 9999)
    st = random.choice(["Oak","Maple","Cedar","Pine","Elm","Willow","Birch","Spruce","Walnut","Cherry"])
    tp = random.choice(["St","Ave","Dr","Ln","Blvd","Way","Ct","Rd"])
    return f"{n} {st} {tp}"

def gauss_clamp(mu, sigma, lo, hi):
    return max(lo, min(hi, round(random.gauss(mu, sigma))))

# ── FICO generators ────────────────────────────────────────────────
def fico_cosigner():       return gauss_clamp(720, 50, 650, 850)
def fico_ug_borrower():
    r = random.random()
    if   r < 0.55: return None,  "NO_FILE"
    elif r < 0.75: return gauss_clamp(650, 30, 580, 710), "THIN"
    else:          return gauss_clamp(690, 35, 620, 780), "ESTABLISHED"
def fico_gr_borrower():
    if random.random() < 0.5: return gauss_clamp(695, 30, 630, 780), "ESTABLISHED"
    else:                     return gauss_clamp(740, 25, 680, 820), "ESTABLISHED"
def fico_sp_borrower():
    r = random.random()
    if   r < 0.08: return None, "THIN"
    elif r < 0.25: return gauss_clamp(685, 25, 640, 750), "THIN"
    else:          return gauss_clamp(725, 35, 650, 810), "ESTABLISHED"
def fico_intl():           return None, "NO_FILE"
def fico_refi():           return gauss_clamp(705, 45, 600, 820), "ESTABLISHED"

# ── risk grade matrix (must match POL-003) ──────────────────────────
GRADES = [
    ("A1",780,0.25,4.99),("A2",760,0.30,5.49),("A3",740,0.35,5.99),
    ("B1",720,0.38,6.49),("B2",700,0.40,6.99),("B3",680,0.42,7.49),
    ("C1",660,0.43,7.99),("C2",650,0.44,8.49),("C3",640,0.45,8.99),
    ("D1",620,0.46,9.99),("D2",600,0.48,10.99),("D3",580,0.50,11.99),
]
TIER_ADJ = {"A":0.0,"B":0.0,"C":0.50,"D":1.00}
DTI_CEIL = {"UG":0.45,"GR":0.43,"SP":0.45,"INTL":0.40,"REFI":0.45}
AMT_RANGE = {"UG":(1000,75000),"GR":(5000,100000),"SP":(10000,150000),"INTL":(5000,80000),"REFI":(5000,300000)}

def assign_grade(fico, dti, tier):
    if fico is None: return "E1", None
    for g, mf, md, r in GRADES:
        if fico >= mf and dti <= md:
            return g, round(r + TIER_ADJ.get(tier, 0), 2)
    if fico >= 580: return "D3", round(11.99 + TIER_ADJ.get(tier, 0), 2)
    return "E1", None

# ── entity generators ──────────────────────────────────────────────
def gen_borrower(seq, product, cit=None):
    fn, ln = random.choice(FIRST), random.choice(LAST)
    ages = {"UG":(17,22),"GR":(22,35),"SP":(23,38),"INTL":(18,30),"REFI":(24,45)}
    lo, hi = ages[product]
    age = random.randint(lo, hi)
    dob = date(2026 - age, random.randint(1,12), random.randint(1,28))
    st = random.choice(STATES)
    city = random.choice(CITIES.get(st, ["Springfield"]))
    if cit is None:
        cit = random.choice(["F1_VISA","F1_VISA","F1_VISA","J1_VISA"]) if product == "INTL" \
              else random.choice(["US_CITIZEN","US_CITIZEN","US_CITIZEN","PERM_RESIDENT"])
    return dict(
        borrower_id=f"BORR-{seq:05d}", first_name=fn, last_name=ln,
        dob=dob.isoformat(), age=age, ssn_itin_masked=masked_ssn(seq),
        email=f"{fn.lower()}.{ln.lower()}{seq}@example.com", phone=rand_phone(),
        address_line1=rand_street(), city=city, state=st, zip=rand_zip(st),
        citizenship_status=cit, years_at_address=random.randint(0, min(age-17, 10)),
        references_provided=random.randint(0, 3))

def gen_cosigner(seq, bid):
    fn, ln = random.choice(FIRST), random.choice(LAST)
    age = random.randint(35, 65)
    dob = date(2026 - age, random.randint(1,12), random.randint(1,28))
    st = random.choice(STATES); city = random.choice(CITIES.get(st, ["Springfield"]))
    return dict(
        cosigner_id=f"COSIG-{seq:05d}", borrower_id=bid,
        relationship=random.choice(["parent","parent","parent","spouse","relative","other"]),
        first_name=fn, last_name=ln, dob=dob.isoformat(),
        citizenship_status=random.choice(["US_CITIZEN","US_CITIZEN","PERM_RESIDENT"]),
        ssn_masked=masked_ssn(seq+5000),
        address=f"{rand_street()}, {city}, {st} {rand_zip(st)}",
        cosigner_notice_acknowledged=random.random() > 0.05)

def gen_credit(sid, stype, fico, fstatus):
    pull = rand_date(date(2026,7,1), date(2026,8,15))
    if fstatus == "NO_FILE":
        return dict(subject_id=sid, subject_type=stype, pull_date=pull.isoformat(),
                     pull_type="HARD", fico_score=None, file_status="NO_FILE",
                     oldest_tradeline_months=None, open_tradelines=None,
                     total_debt=None, revolving_utilization_pct=None,
                     inquiries_6mo=0, delinq_30_24mo=0, delinq_60_24mo=0, delinq_90_24mo=0,
                     collections_count=0, charge_offs_count=0,
                     bankruptcy_flag=False, bankruptcy_discharge_date=None,
                     student_loan_delinquency_flag=False)
    oldest = random.randint(6,360) if fstatus=="ESTABLISHED" else random.randint(3,36)
    opn = random.randint(1,15) if fstatus=="ESTABLISHED" else random.randint(0,3)
    debt = round(random.uniform(0,120000),2) if fstatus=="ESTABLISHED" else round(random.uniform(0,5000),2)
    util = round(random.uniform(0,0.75),2) if opn>0 else 0
    bad = fico is not None and fico < 640
    bk = bad and random.random() < 0.05
    d30 = random.randint(0,3) if bad else random.randint(0,1)
    d60 = random.randint(0,2) if bad else 0
    d90 = random.randint(0,1) if bad else 0
    coll = random.randint(0,2) if bad else 0
    co = random.randint(0,1) if bad else 0
    bk_dt = rand_date(date(2020,1,1),date(2025,6,30)).isoformat() if bk else None
    return dict(subject_id=sid, subject_type=stype, pull_date=pull.isoformat(),
                pull_type="HARD", fico_score=fico, file_status=fstatus,
                oldest_tradeline_months=oldest, open_tradelines=opn,
                total_debt=debt, revolving_utilization_pct=util,
                inquiries_6mo=random.randint(0,5), delinq_30_24mo=d30,
                delinq_60_24mo=d60, delinq_90_24mo=d90,
                collections_count=coll, charge_offs_count=co,
                bankruptcy_flag=bk, bankruptcy_discharge_date=bk_dt,
                student_loan_delinquency_flag=bad and random.random()<0.10)

def gen_income(sid, product, is_cosigner, req_amt):
    is_student = product in ("UG","GR","SP","INTL") and not is_cosigner
    if is_student and product == "UG":
        emp = random.choice(["Part-time Campus Job","Summer Internship","None"])
        etype = "W2" if emp != "None" else "UNEMPLOYED"
        gross = round(random.uniform(0,15000),2) if etype != "UNEMPLOYED" else 0
        tenure = random.randint(0,24) if etype != "UNEMPLOYED" else 0
        meth = "PAYSTUB" if etype != "UNEMPLOYED" else "VOE"
        job = "Student Worker" if etype != "UNEMPLOYED" else "Student"
    elif is_cosigner:
        emp = random.choice(EMPLOYERS); etype = random.choice(["W2","W2","W2","SELF_EMPLOYED"])
        gross = round(random.uniform(60000,250000),2)
        tenure = random.randint(24,360)
        meth = random.choice(["PAYSTUB","W2","TAX_RETURN"]); job = random.choice(JOBS)
    elif product == "REFI":
        emp = random.choice(EMPLOYERS); etype = random.choice(["W2","W2","SELF_EMPLOYED","CONTRACT"])
        gross = round(random.uniform(50000,200000),2)
        tenure = random.randint(12,180)
        meth = random.choice(["PAYSTUB","W2","TAX_RETURN"]); job = random.choice(JOBS)
    else:
        emp = random.choice(EMPLOYERS); etype = random.choice(["W2","W2","SELF_EMPLOYED","CONTRACT","W2"])
        gross = round(random.uniform(35000,130000),2)
        tenure = random.randint(6,120)
        meth = random.choice(["PAYSTUB","W2","TAX_RETURN","VOE"]); job = random.choice(JOBS)

    monthly = gross / 12 if gross > 0 else 1
    other = round(random.uniform(0,12000),2) if random.random()<0.15 else 0
    osrc = random.choice(["Investment income","Rental income","Alimony",None]) if other>0 else None
    housing = round(random.uniform(700,2500),2) if (is_cosigner or product=="REFI") else round(random.uniform(0,1200),2)

    if req_amt > 0:
        ep = (req_amt * 0.07/12) / (1 - (1+0.07/12)**(-120))
    else:
        ep = 0

    # Keep other debts proportional to income so DTI stays reasonable
    other_debts = round(random.uniform(0, monthly * 0.10), 2)
    ds = round(housing + ep + other_debts, 2)
    tot_m = (gross + other) / 12
    dti = round(ds / tot_m, 4) if tot_m > 0 else 9.99
    dti = min(dti, 0.99)
    res = round(tot_m - ds, 2)
    dc = random.random() > 0.05

    return dict(subject_id=sid, verification_method=meth, employer_name=emp,
                employment_type=etype, job_title=job, tenure_months=tenure,
                gross_annual_income=gross, other_income=other, other_income_source=osrc,
                monthly_housing_expense=housing, monthly_debt_service=round(ds,2),
                dti_pct=round(dti,4), residual_income=res, docs_complete=dc)

def gen_cert(school, product, req_amt):
    if product == "REFI": return None
    coa = round(random.uniform(15000,85000),2)
    if school["school_type"] == "PROFESSIONAL": coa = round(random.uniform(50000,95000),2)
    elif school["school_type"] == "COMMUNITY": coa = round(random.uniform(8000,25000),2)
    aid = round(random.uniform(0, coa*0.4),2)
    gap = max(0, coa - aid)
    if product == "UG":   fed = min(round(random.uniform(3500,7500),2), gap * 0.8)
    elif product == "GR": fed = min(20500, round(random.uniform(5000,20500),2), gap * 0.7)
    elif product == "SP": fed = min(50000, round(random.uniform(10000,50000),2), gap * 0.7)
    else:                 fed = 0
    fed = round(fed, 2)
    cme = round(max(0, coa - aid - fed), 2)
    status = "PENDING" if random.random() < 0.04 else "RECEIVED"
    cat = rand_date(date(2026,6,1),date(2026,8,15)).isoformat() if status=="RECEIVED" else None
    start = date(2026,8,15) if random.random()>0.3 else date(2027,1,10)
    end = date(start.year+1, start.month, min(start.day,28))
    deg = {"UG":random.choice(["BS","BA","AS"]),"GR":random.choice(["MS","MA","MEng"]),
           "SP":random.choice(["MD","JD","DDS","MBA","PharmD"]),
           "INTL":random.choice(["MS","BS","MBA"])}.get(product,"BS")
    prog = {"UG":random.choice(["Computer Science","Biology","Business","Nursing","Engineering","Psychology"]),
            "GR":random.choice(["Data Science","Computer Engineering","Public Health","Finance","Biomedical Eng"]),
            "SP":random.choice(["Medicine","Law","Dentistry","Business Admin","Pharmacy"]),
            "INTL":random.choice(["Computer Science","Electrical Eng","Data Science","Business Analytics","Biotech"]),
            }.get(product,"General Studies")
    return dict(certification_status=status, certified_at=cat, cost_of_attendance=coa,
                other_financial_aid=aid, federal_loans_amount=fed, certified_max_eligible=cme,
                enrollment_period_start=start.isoformat(), enrollment_period_end=end.isoformat(),
                enrollment_intensity=random.choice(["FULL_TIME","FULL_TIME","FULL_TIME","HALF_TIME"]),
                degree_level=deg, program_name=prog,
                expected_graduation_date=date(start.year+random.randint(1,4),5,15).isoformat(),
                year_in_program=random.randint(1,4))

def gen_intl(product, borrower):
    if product != "INTL": return None
    visa = "F-1" if borrower["citizenship_status"]=="F1_VISA" else "J-1"
    stem = random.random() < 0.65
    opt = (visa=="F-1") and random.random() < 0.75
    psw = 36 if stem and opt else (12 if opt else random.randint(0,12))
    return dict(visa_type=visa, i20_ds2019_number=f"N{random.randint(1000000000,9999999999)}",
                i94_verified=random.random()>0.10,
                passport_country=random.choice(PASSPORT_COUNTRIES),
                home_country_credit_available=random.random()<0.3,
                home_country_reference_provided=random.random()<0.7,
                sponsor_funds_documented=random.random()<0.5,
                opt_eligible=opt, stem_opt_eligible=stem and opt,
                post_study_work_months=psw)

def gen_existing(product):
    if product != "REFI": return None
    loans = []
    for i in range(random.randint(1,5)):
        bal = round(random.uniform(5000,80000),2)
        rate = round(random.uniform(4.0,12.0),2)
        pay = round(bal*(rate/100/12)/(1-(1+rate/100/12)**(-120)),2)
        r = random.random()
        st = "CURRENT" if r<0.85 else ("30DPD" if r<0.93 else ("60DPD" if r<0.97 else "DEFAULT"))
        loans.append(dict(loan_seq=i+1, servicer_name=random.choice(SERVICERS),
                          loan_type=random.choice(["FEDERAL_DIRECT","FEDERAL_DIRECT","PRIVATE","FEDERAL_PLUS"]),
                          current_balance=bal, current_rate_pct=rate, monthly_payment=pay,
                          status=st, payoff_statement_received=random.random()>0.12))
    return loans

def gen_fraud(product, school):
    kyc = "PASS"; ofac = False; eflag = False
    drs = random.randint(5,35); vel = False; sis = random.randint(5,25); amf = random.random()<0.08
    if random.random() < 0.02: kyc = random.choice(["FAIL","REVIEW"])
    if random.random() < 0.005: ofac = True
    if school and school["school_risk_tier"]=="D" and random.random()<0.08: eflag = True
    elif random.random() < 0.01: eflag = True
    if random.random() < 0.04: drs = random.randint(70,95); vel = random.random()<0.5
    if random.random() < 0.02: sis = random.randint(65,90)
    return dict(kyc_status=kyc, cip_documents_verified=kyc!="FAIL", ofac_hit=ofac,
                device_risk_score=drs, velocity_flag=vel, synthetic_identity_score=sis,
                enrollment_fraud_flag=eflag, address_mismatch_flag=amf)

def gen_exposure(bid, product, req, school):
    pl = random.randint(0,3)
    pb = round(random.uniform(0,50000),2) if pl>0 else 0
    fb = round(random.uniform(0,57500),2) if product!="INTL" else 0
    op = round(random.uniform(0,30000),2) if random.random()<0.3 else 0
    td = round(pb+fb+op+req, 2)
    if product == "REFI":
        pd_ = td; ps = round(random.uniform(45000,180000),2)
    else:
        yl = random.randint(1,4)
        pd_ = round(td + req*(yl-1)*0.3, 2)
        ps = round(school["median_earnings_3yr_post"]*random.uniform(0.7,1.3),2) if school else round(random.uniform(35000,90000),2)
    return dict(prior_loans_with_us=pl, prior_balance_with_us=pb,
                federal_loan_balance=fb, other_private_balance=op,
                total_education_debt=td, projected_debt_at_graduation=pd_,
                projected_starting_salary=ps,
                debt_to_projected_income_ratio=round(pd_/ps,4) if ps>0 else 9.99)

# ── decision engine ─────────────────────────────────────────────────
def decide(app):
    product = app["product_code"]
    borrower = app["borrower"]
    cosigner = app.get("cosigner")
    cbs = app.get("credit_bureau",[])
    incs = app.get("income_verification",[])
    school = app.get("school")
    cert = app.get("school_certification")
    intl = app.get("international_details")
    existing = app.get("existing_loans")
    fraud = app["fraud_screening"]

    dec_r, cond, ref_r = [], [], []

    # Extract scores
    b_fico, c_fico = None, None
    for cb in cbs:
        if cb["subject_type"]=="borrower":  b_fico = cb["fico_score"]
        elif cb["subject_type"]=="cosigner": c_fico = cb["fico_score"]
    eff_fico = b_fico if b_fico is not None else c_fico

    # Extract DTI/residual from best income record
    dti, residual, inc_subj = 0, 99999, None
    for inc in incs:
        if inc["gross_annual_income"] > 0:
            if inc_subj is None or (not inc["subject_id"].startswith("COSIG") and inc["gross_annual_income"] > 0):
                dti = inc["dti_pct"]; residual = inc["residual_income"]; inc_subj = inc
    # For UG with cosigner only, prefer cosigner income
    if product == "UG" and cosigner:
        for inc in incs:
            if inc["subject_id"].startswith("COSIG"):
                dti = inc["dti_pct"]; residual = inc["residual_income"]; inc_subj = inc; break

    tier = school["school_risk_tier"] if school else "B"

    # Stage 0: Intake knockouts
    if fraud.get("enrollment_fraud_flag"): dec_r.append("RC-016")
    if school and not school["on_approved_list"]: dec_r.append("RC-009")
    if product=="INTL" and borrower["citizenship_status"] not in ("F1_VISA","J1_VISA"): dec_r.append("RC-014")

    # Stage 1: Identity & fraud
    if fraud.get("ofac_hit"): dec_r.append("RC-018")
    if fraud["kyc_status"]=="FAIL": dec_r.append("RC-017")
    if fraud.get("synthetic_identity_score",0) > 70: ref_r.append("RC-019")
    if fraud.get("velocity_flag"): ref_r.append("RC-024")

    # Stage 2: Credit
    if eff_fico is not None and eff_fico < 580:
        dec_r.append("RC-001")
    elif eff_fico is None and cosigner is None and product not in ("INTL","SP"):
        dec_r.append("RC-002"); dec_r.append("RC-011")
    elif eff_fico is None and cosigner is None and product == "SP":
        ref_r.append("RC-002")  # SP projected income path
    # Bankruptcy check: only on the effective underwriting subject
    for cb in cbs:
        if cb.get("bankruptcy_flag"):
            # For UG/INTL with cosigner, borrower bankruptcy matters less
            if cb["subject_type"] == "cosigner":
                dec_r.append("RC-005"); break
            elif cb["subject_type"] == "borrower" and cosigner is None:
                dec_r.append("RC-005"); break
            elif cb["subject_type"] == "borrower" and product in ("GR","SP","REFI"):
                dec_r.append("RC-005"); break
    if any(cb.get("collections_count",0) >= 4 for cb in cbs): dec_r.append("RC-006")

    # Stage 3: Capacity
    ceil = DTI_CEIL.get(product, 0.45)
    if not dec_r:
        if dti > ceil + 0.05:
            dec_r.append("RC-003")
        elif dti > ceil:
            ref_r.append("RC-003")
    if product == "REFI" and residual < 800 and inc_subj and not dec_r:
        dec_r.append("RC-023")

    # Stage 4: School risk
    if school and school["completion_rate_pct"] < 40 and not dec_r:
        dec_r.append("RC-010")

    # Stage 5: Amount & certification
    approved_amt = app["requested_amount"]
    if cert and cert["certification_status"]=="RECEIVED":
        if approved_amt > cert["certified_max_eligible"]:
            approved_amt = cert["certified_max_eligible"]
            cond.append("Amount capped at certified maximum eligible")
    elif cert and cert["certification_status"]=="PENDING" and product != "REFI":
        ref_r.append("RC-022")
        cond.append("Pending school certification — obtain before disbursement")

    # Stage 6: Grade & pricing
    grade, rate = assign_grade(eff_fico, dti, tier)

    # INTL no-cosigner
    if product=="INTL" and cosigner is None and intl and not dec_r:
        ok = (school and tier in ("A","B") and intl.get("opt_eligible") and intl.get("post_study_work_months",0)>=12)
        if not ok: dec_r.append("RC-015")
        if not intl.get("i94_verified"):
            ref_r.append("RC-022"); cond.append("I-94 verification required")

    if product=="INTL" and intl and not dec_r:
        if intl.get("post_study_work_months",0) < 6 and not intl.get("opt_eligible"):
            dec_r.append("RC-015")

    # REFI loan status
    if product=="REFI" and existing and not dec_r:
        for ln in existing:
            if ln["status"] in ("60DPD","DEFAULT"):
                dec_r.append("RC-021"); break
        if not all(ln.get("payoff_statement_received") for ln in existing):
            ref_r.append("RC-022"); cond.append("Missing payoff statement(s)")

    # Cosigner credit
    if cosigner and c_fico is not None and c_fico < 650 and not dec_r:
        dec_r.append("RC-012")

    # Deduplicate
    dec_r = list(dict.fromkeys(dec_r))
    ref_r = list(dict.fromkeys(ref_r))
    cond  = list(dict.fromkeys(cond))

    if dec_r:
        decision = "DECLINE"
    elif ref_r:
        decision = "REFER_MANUAL"
    elif cond:
        decision = "APPROVE_WITH_CONDITIONS"
    else:
        decision = "APPROVE"

    # Inject messiness → promote APPROVE to APPROVE_WITH_CONDITIONS
    if decision == "APPROVE" and inc_subj and not inc_subj.get("docs_complete", True):
        decision = "APPROVE_WITH_CONDITIONS"
        cond.append("Complete income documentation required")

    # Address mismatch is tracked in fraud_screening; no separate condition needed

    cos_release = True if cosigner and decision in ("APPROVE","APPROVE_WITH_CONDITIONS") else None
    rtype = random.choice(["FIXED","FIXED","FIXED","VARIABLE"]) if rate else None
    term = None
    if decision != "DECLINE":
        if product=="REFI":    term = random.choice([60,84,120,180])
        elif product=="SP":    term = random.choice([120,180,240])
        else:                  term = random.choice([60,84,120,180])
    repay = None
    if decision in ("APPROVE","APPROVE_WITH_CONDITIONS"):
        if product in ("UG","GR","SP"):  repay = random.choice(["DEFERRED","INTEREST_ONLY","FLAT_25"])
        elif product=="INTL":            repay = random.choice(["DEFERRED","INTEREST_ONLY"])
        else:                            repay = "IMMEDIATE"

    d_at = rand_dt(date(2026,8,1), date(2026,9,15))

    app["decision"] = dict(
        risk_grade=grade, decision=decision,
        approved_amount=approved_amt if decision!="DECLINE" else None,
        offered_rate_pct=rate,
        rate_type=rtype, term_months=term, repayment_option=repay,
        cosigner_release_eligible=cos_release,
        conditions=cond if decision!="DECLINE" else [],
        decline_reason_codes=dec_r if decision=="DECLINE" else [],
        adverse_action_required=decision in ("DECLINE","APPROVE_WITH_CONDITIONS"),
        decisioned_at=d_at.isoformat(),
        decisioned_by="AUTO" if decision in ("APPROVE","DECLINE") else f"ANALYST-{random.randint(100,999)}")
    return app

# ── build one application ──────────────────────────────────────────
def gen_app(seq, product):
    app_id = f"APP-2026-{seq:05d}"
    borrower = gen_borrower(seq, product)
    submitted = rand_dt(date(2026,7,1), date(2026,9,1))

    has_cos = (product=="UG" and random.random()<0.95) or \
              (product=="GR" and random.random()<0.55) or \
              (product=="SP" and random.random()<0.40) or \
              (product=="INTL" and random.random()<0.60) or \
              False
    cosigner = gen_cosigner(seq, borrower["borrower_id"]) if has_cos else None

    # School
    school = None
    if product=="UG":
        pool = [s for s in SCHOOLS if s["school_type"] in ("PUBLIC_4YR","PRIVATE_4YR","COMMUNITY") and s["on_approved_list"]]
        school = random.choice(pool)
    elif product=="GR":
        pool = [s for s in SCHOOLS if s["school_type"] in ("PUBLIC_4YR","PRIVATE_4YR") and s["on_approved_list"]]
        school = random.choice(pool)
    elif product=="SP":
        pool = [s for s in SCHOOLS if s["school_type"]=="PROFESSIONAL" and s["on_approved_list"]]
        school = random.choice(pool)
    elif product=="INTL":
        if random.random()<0.5:
            pool = [s for s in SCHOOLS if s["school_type"]=="INTERNATIONAL_ELIGIBLE" and s["on_approved_list"]]
        else:
            pool = [s for s in SCHOOLS if s["school_type"] in ("PUBLIC_4YR","PRIVATE_4YR") and s["on_approved_list"]]
        school = random.choice(pool)

    lo, hi = AMT_RANGE[product]
    req = round(random.uniform(lo, hi), 2)

    # For non-REFI: if we have a school, pre-estimate cert max so most requests are within it
    # This gets refined after cert is generated, but keeps amounts realistic
    if product != "REFI" and school:
        est_coa = 50000 if school["school_type"]=="PROFESSIONAL" else (12000 if school["school_type"]=="COMMUNITY" else 35000)
        est_max = est_coa * 0.6  # rough cert max
        if req > est_max and random.random() < 0.85:
            req = round(random.uniform(lo, max(lo, est_max)), 2)

    # Credit
    if product=="UG":     fico, fs = fico_ug_borrower()
    elif product=="GR":   fico, fs = fico_gr_borrower()
    elif product=="SP":   fico, fs = fico_sp_borrower()
    elif product=="INTL": fico, fs = fico_intl()
    else:                 fico, fs = fico_refi()

    cbs = [gen_credit(borrower["borrower_id"], "borrower", fico, fs)]
    if has_cos and cosigner:
        cbs.append(gen_credit(cosigner["cosigner_id"], "cosigner", fico_cosigner(), "ESTABLISHED"))

    # Income
    incs = []
    if product=="UG" and has_cos:
        incs.append(gen_income(cosigner["cosigner_id"], product, True, req))
    elif product in ("GR","SP") and not has_cos:
        incs.append(gen_income(borrower["borrower_id"], product, False, req))
    elif product in ("GR","SP") and has_cos:
        incs.append(gen_income(borrower["borrower_id"], product, False, req))
        incs.append(gen_income(cosigner["cosigner_id"], product, True, req))
    elif product=="INTL":
        if has_cos: incs.append(gen_income(cosigner["cosigner_id"], product, True, req))
    elif product=="REFI":
        incs.append(gen_income(borrower["borrower_id"], product, False, req))

    cert = gen_cert(school, product, req) if school else None
    intl_ = gen_intl(product, borrower)
    exist = gen_existing(product)
    fraud_ = gen_fraud(product, school)
    agg = gen_exposure(borrower["borrower_id"], product, req, school)

    ch = random.choice(["direct","school_referral","partner"]) if product!="REFI" else random.choice(["direct","partner"])
    purp = {"UG":"undergraduate_tuition","GR":"graduate_tuition","SP":"professional_program_tuition",
            "INTL":"international_education","REFI":"refinance_existing_education_loans"}

    app = dict(
        application_id=app_id, product_code=product, submitted_at=submitted.isoformat(),
        channel=ch, requested_amount=req, loan_purpose=purp[product],
        state_of_residence=borrower["state"], has_cosigner=has_cos, status="DECISIONED",
        borrower=borrower, cosigner=cosigner, credit_bureau=cbs,
        income_verification=incs, school=school, school_certification=cert,
        international_details=intl_, existing_loans=exist,
        fraud_screening=fraud_, aggregate_exposure=agg,
        decision={}, supplied_documents=[], untrusted_applicant_text=None)

    return decide(app)

# ── main ────────────────────────────────────────────────────────────
def main():
    products = ["UG"]*80 + ["GR"]*50 + ["SP"]*30 + ["INTL"]*25 + ["REFI"]*15
    random.shuffle(products)
    apps = []
    for i, p in enumerate(products, 1):
        a = gen_app(i, p)
        apps.append(a)
        with open(APP_DIR / f"{a['application_id']}.json", "w") as f:
            json.dump(a, f, indent=2, ensure_ascii=False)

    with open(PROFILE_DIR / "school_profiles.jsonl", "w") as f:
        for s in SCHOOLS: f.write(json.dumps(s)+"\n")
    with open(PROFILE_DIR / "borrower_profiles.jsonl", "w") as f:
        for a in apps:
            f.write(json.dumps(dict(
                borrower_id=a["borrower"]["borrower_id"], application_id=a["application_id"],
                product_code=a["product_code"],
                name=f"{a['borrower']['first_name']} {a['borrower']['last_name']}",
                age=a["borrower"]["age"], citizenship=a["borrower"]["citizenship_status"],
                has_cosigner=a["has_cosigner"],
                decision=a["decision"]["decision"], risk_grade=a["decision"]["risk_grade"]))+"\n")
    with open(SCENARIO_DIR / "scenario_catalog.json", "w") as f:
        json.dump(dict(
            generator_seed=SEED, generated_at=datetime.now().isoformat(),
            total_applications=len(apps),
            product_mix=dict(Counter(a["product_code"] for a in apps)),
            decision_mix=dict(Counter(a["decision"]["decision"] for a in apps)),
            grade_distribution=dict(Counter(a["decision"]["risk_grade"] for a in apps)),
            cosigner_rate=sum(1 for a in apps if a["has_cosigner"])/len(apps)), f, indent=2)

    # Summary
    print("="*60)
    print("EDUCATION LOAN SYNTHETIC DATA — GENERATION COMPLETE")
    print("="*60)
    print(f"Applications: {len(apps)}")
    print(f"Output:       {APP_DIR}\n")
    for label, counter in [
        ("Product mix", Counter(a["product_code"] for a in apps)),
        ("Decision mix", Counter(a["decision"]["decision"] for a in apps)),
        ("Risk grades", Counter(a["decision"]["risk_grade"] for a in apps)),
    ]:
        print(f"{label}:")
        for k, v in sorted(counter.items()):
            pct = v/len(apps)*100
            print(f"  {k:30s}: {v:4d} ({pct:5.1f}%)")
        print()
    print(f"Cosigner rate: {sum(1 for a in apps if a['has_cosigner'])/len(apps):.1%}\n")
    di = sum(1 for a in apps for inc in a.get("income_verification",[]) if not inc.get("docs_complete",True))
    pc = sum(1 for a in apps if a.get("school_certification") and a["school_certification"]["certification_status"]=="PENDING")
    iv = sum(1 for a in apps if a.get("international_details") and not a["international_details"].get("i94_verified",True))
    am = sum(1 for a in apps if a["fraud_screening"].get("address_mismatch_flag"))
    print(f"Deliberate messiness: incomplete_docs={di}, pending_certs={pc}, unverified_i94={iv}, addr_mismatch={am}")

if __name__ == "__main__":
    main()
