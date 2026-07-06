"""
Synthetic Olympic Games dataset generator.
Produces representative (not real) data mirroring the structure of
public Olympic datasets: Athletes, Coaches, Teams, EntriesGender, Medals.
Used as sample input for the Databricks/Synapse/Power BI pipeline.
"""

import pandas as pd
import numpy as np
import random

random.seed(42)
np.random.seed(42)

countries = [
    ("USA", "United States"), ("CHN", "China"), ("JPN", "Japan"),
    ("GBR", "Great Britain"), ("ROC", "ROC"), ("AUS", "Australia"),
    ("NED", "Netherlands"), ("FRA", "France"), ("GER", "Germany"),
    ("ITA", "Italy"), ("CAN", "Canada"), ("BRA", "Brazil"),
    ("NZL", "New Zealand"), ("CUB", "Cuba"), ("HUN", "Hungary"),
    ("KOR", "South Korea"), ("POL", "Poland"), ("CZE", "Czech Republic"),
    ("KEN", "Kenya"), ("NOR", "Norway"), ("JAM", "Jamaica"),
    ("ESP", "Spain"), ("SWE", "Sweden"), ("SUI", "Switzerland"),
    ("DEN", "Denmark"), ("IND", "India"),
]

disciplines = [
    "Athletics", "Swimming", "Gymnastics", "Rowing", "Cycling Road",
    "Boxing", "Judo", "Wrestling", "Weightlifting", "Fencing",
    "Table Tennis", "Badminton", "Volleyball", "Basketball",
    "Football", "Hockey", "Archery", "Shooting", "Sailing",
    "Taekwondo", "Diving", "Canoe Sprint", "Triathlon", "Golf",
]

first_names_m = ["James", "Liam", "Noah", "Oliver", "Ethan", "Lucas", "Mason", "Kenji", "Wei", "Ivan",
                 "Carlos", "Marco", "Sven", "Raj", "Kofi", "Diego", "Hiroshi", "Andrei", "Tom", "Ben"]
first_names_f = ["Emma", "Olivia", "Ava", "Sophia", "Mia", "Yuki", "Li", "Elena", "Maria", "Anna",
                  "Priya", "Aisha", "Sofia", "Nadia", "Ingrid", "Clara", "Julia", "Sara", "Nina", "Lea"]
last_names = ["Smith", "Johnson", "Wang", "Tanaka", "Kowalski", "Silva", "Muller", "Dubois", "Rossi",
              "Kim", "Nguyen", "Patel", "Andersson", "Novak", "Garcia", "Kovac", "Fischer", "Hansen",
              "Yamamoto", "Ivanov"]

n_athletes = 600
athletes = []
for i in range(1, n_athletes + 1):
    gender = random.choice(["Male", "Female"])
    fname = random.choice(first_names_m if gender == "Male" else first_names_f)
    lname = random.choice(last_names)
    noc_code, noc_name = random.choice(countries)
    athletes.append({
        "athlete_id": i,
        "name": f"{fname} {lname}",
        "gender": gender,
        "country_code": noc_code,
        "country": noc_name,
        "discipline": random.choice(disciplines),
        "birth_year": random.randint(1985, 2006),
    })
athletes_df = pd.DataFrame(athletes)

n_coaches = 120
coaches = []
for i in range(1, n_coaches + 1):
    gender = random.choice(["Male", "Female"])
    fname = random.choice(first_names_m if gender == "Male" else first_names_f)
    lname = random.choice(last_names)
    noc_code, noc_name = random.choice(countries)
    coaches.append({
        "coach_id": i,
        "name": f"{fname} {lname}",
        "country_code": noc_code,
        "country": noc_name,
        "discipline": random.choice(disciplines),
        "event": random.choice(["Team", "Individual"]),
    })
coaches_df = pd.DataFrame(coaches)

teams = []
team_id = 1
for noc_code, noc_name in countries:
    for disc in random.sample(disciplines, k=random.randint(2, 6)):
        teams.append({
            "team_id": team_id,
            "team_name": f"{noc_name} {disc}",
            "discipline": disc,
            "country_code": noc_code,
            "country": noc_name,
            "num_athletes": random.randint(1, 12),
        })
        team_id += 1
teams_df = pd.DataFrame(teams)

entries_gender = []
for disc in disciplines:
    female = random.randint(10, 150)
    male = random.randint(10, 150)
    entries_gender.append({
        "discipline": disc,
        "female": female,
        "male": male,
        "total": female + male,
    })
entries_gender_df = pd.DataFrame(entries_gender)

medals = []
for noc_code, noc_name in countries:
    gold = np.random.poisson(4)
    silver = np.random.poisson(4)
    bronze = np.random.poisson(4)
    medals.append({
        "country_code": noc_code,
        "country": noc_name,
        "gold": gold,
        "silver": silver,
        "bronze": bronze,
        "total": gold + silver + bronze,
    })
medals_df = pd.DataFrame(medals).sort_values("total", ascending=False).reset_index(drop=True)
medals_df["rank"] = medals_df.index + 1

# introduce a few realistic data quality issues for the cleaning step to handle
athletes_df.loc[athletes_df.sample(15, random_state=1).index, "birth_year"] = np.nan
athletes_df.loc[athletes_df.sample(10, random_state=2).index, "country"] = None
coaches_df.loc[coaches_df.sample(5, random_state=3).index, "event"] = None
dupe_rows = athletes_df.sample(8, random_state=4)
athletes_df = pd.concat([athletes_df, dupe_rows], ignore_index=True)

athletes_df.to_csv("Athletes.csv", index=False)
coaches_df.to_csv("Coaches.csv", index=False)
teams_df.to_csv("Teams.csv", index=False)
entries_gender_df.to_csv("EntriesGender.csv", index=False)
medals_df.to_csv("Medals.csv", index=False)

print("Generated: Athletes.csv, Coaches.csv, Teams.csv, EntriesGender.csv, Medals.csv")
print(f"Athletes: {len(athletes_df)} rows (includes injected nulls/duplicates for cleaning demo)")
print(f"Coaches: {len(coaches_df)} rows")
print(f"Teams: {len(teams_df)} rows")
print(f"EntriesGender: {len(entries_gender_df)} rows")
print(f"Medals: {len(medals_df)} rows")
