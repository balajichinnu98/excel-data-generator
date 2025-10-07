from flask import Flask, render_template, request, send_file
import pandas as pd
import random
import os
from faker import Faker

app = Flask(__name__)
faker = Faker()


job_titles = [faker.job() for _ in range(500)]
grades = [f"{random.choice(['A','B','C','D'])}{random.randint(1,5)}" for _ in range(50)]

team_name_part1 = [
    "Alpha", "Beta", "Summit", "Crest", "Nova", "Aspen", "Everest", "Iron", "Blue", "Silver",
    "Golden", "Titan", "Falcon", "Orion", "Phoenix", "Stonegate", "Maple", "Redwood", "Aurora", "Canyon"
]

team_name_part2 = [
    "Fund", "Capital", "Partners", "Equity", "Group", "Associates", "Advisors", "Investments",
    "Strategies", "Ventures", "Management", "Holdings", "Global", "Solutions", "Advisory"
]

team_structure_part1 = [
    "Investment", "Portfolio", "Risk", "Fund", "Corporate", "Deal", "Financial", "Strategy",
    "Market", "Capital", "Transaction", "Growth", "Exit", "Liquidity", "Valuation", "Governance"
]

team_structure_part2 = [
    "Committee", "Management", "Team", "Operations", "Relations", "Support", "Analysis",
    "Development", "Execution", "Planning", "Research", "Oversight", "Advisory", "Optimization"
]

investment_names = [
    "BlueSky Energy", "Aurora Biotech", "Crestline Retail", "Titan Infrastructure", "SilverLake Tech",
    "Summit Healthcare", "Redwood Real Estate", "Orion Logistics", "NorthStar Manufacturing",
    "Vanguard Media", "Evergreen Foods", "Canyon Mining", "Falcon Automotive", "IronBridge Financial",
    "Maplewood Education", "Lighthouse Pharma", "Granite Hospitality", "Skyline Entertainment",
    "Aspen Telecom", "Stonegate Energy"
]



carry_types = ["Cash", "Carry", "Shares"]
pfcv_types = ["PFCV Mid", "PFCV Low", "PFCV High", "Current Value"]



def generate_user_emp_id(first, middle, last):
    parts = [first.lower(), middle.lower() if middle else "", last.lower()]
    chosen = random.sample([p for p in parts if p], 2)
    sep = random.choice([".", "-", "_"])
    base = sep.join(chosen)
    if random.random() > 0.5:
        base += str(random.randint(10, 999))
    return base

def generate_team_name():
    return random.choice(team_name_part1) + " " + random.choice(team_name_part2)

def generate_structure_name():
    return random.choice(team_structure_part1) + " " + random.choice(team_structure_part2)

def random_id(base):
    sep = random.choice([".", "-", "_"])
    return f"{base}{sep}{random.randint(100,999)}"

def generate_postcode():

    styles = [
        lambda: str(random.randint(100000, 999999)),            
        lambda: f"{random.randint(100,999)} {random.randint(100,999)}",  
        lambda: faker.postcode(),                              
        lambda: ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=7)) 
    ]
    return random.choice(styles)()


def fill_random_value(col_name):
    col = col_name.lower()

    
    if col_name.startswith("BN_"):
        return "#CLICK"

    
    first, middle, last = faker.first_name(), faker.first_name(), faker.last_name()

    
    if "first" in col:
        return first
    if "middle" in col:
        return middle
    if "last" in col or "surname" in col:
        return last
    if "name" in col and "team" not in col and "structure" not in col:
        return f"{first} {middle} {last}"

    
    if "userid" in col or "empid" in col:
        return generate_user_emp_id(first, middle, last)

    
    if "risk" in col and "flag" in col:
        return random.choice(["Y", "N"])
    if "comp" in col and "flag" in col:
        return random.choice(["Y", "N"])

    
    if "agreement" in col:
        return random.choice(["Permanent", "Independency Agreement"])


    if "teamid" in col:
        return random_id("team" + random.choice([".", "-", "_"]) + random.choice(team_name_part1).lower())
    if "team" in col and "structure" not in col:
        return generate_team_name()
    if "structure" in col:
        return generate_structure_name().title()

    
    if "job" in col and "title" in col:
        return random.choice(job_titles)


    if "grade" in col:
        return random.choice(grades)

    
    if "carry" in col:
        return random.choice(carry_types)

    
    if "pfcv" in col:
        return random.choice(pfcv_types)

    
    if "code" in col or (("id" in col) and "empid" not in col and "userid" not in col):
        return random_id(faker.word())

    
    if "country" in col or "location" in col or "work" in col:
        return faker.country()

    
    if "email" in col:
        return faker.email()
    if "address" in col:
        return faker.address().replace("\n", ", ")


    if "postcode" in col or "zip" in col:
        return generate_postcode()


    if "salary" in col:
        return random.randint(40000, 150000)


    if "date" in col:
        return faker.date(pattern="%d-%b-%Y")

    
    if "check" in col:
        return "#CHECK"

    return "#NULL"


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if not file:
        return "No file uploaded", 400

    ext = file.filename.split('.')[-1].lower()
    if ext == "csv":
        df = pd.read_csv(file)
    elif ext in ["xls", "xlsx", "ods"]:
        df = pd.read_excel(file, engine="odf" if ext == "ods" else None)
    else:
        return "Unsupported file type", 400

    for col in df.columns:
        df[col] = df[col].apply(lambda x: fill_random_value(col) if pd.isna(x) or str(x).strip() == "" else x)

    out_file = "output." + ext
    if ext == "csv":
        df.to_csv(out_file, index=False)
    elif ext == "ods":
        df.to_excel(out_file, index=False, engine="odf")
    else:
        df.to_excel(out_file, index=False)

    return send_file(out_file, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
