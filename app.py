# from flask import Flask
import csv
import pandas as pd
import math

previous_scores = pd.DataFrame(columns = ["country"])
current_scores = pd.DataFrame(columns = ["country"])
tiers = {'A': [], 'B': [], 'C': [], 'D': [], 'E': []}
players = pd.DataFrame(columns = ["name", "tier a", "tier b", "tier c", "tier d", "tier e", "score"])

# app = Flask(__name__)

# @app.before_first_request
def determine_tiers():
    read_file('./medal-data/beijing-medal-table.csv', 'beijing', previous_scores)
    read_file('./medal-data/london-medal-table.csv', 'london', previous_scores)
    read_file('./medal-data/rio-medal-table.csv', 'rio', previous_scores)

    for index, row in previous_scores.iterrows():
        beijing = 0 if math.isnan(row[1]) else row[1]
        london = 0 if math.isnan(row[2]) else row[2]
        rio = 0 if math.isnan(row[3]) else row[3]
        avg = round((beijing + london + rio) / 3, 2)
        if avg >= 100:
            tiers['A'].append(previous_scores.at[index, 'country'])
        elif avg >= 60:
            tiers['B'].append(previous_scores.at[index, 'country'])
        elif avg >= 35:
            tiers['C'].append(previous_scores.at[index, 'country'])
        elif avg >= 30:
            tiers['D'].append(previous_scores.at[index, 'country'])
        elif avg >= 13:
            tiers['E'].append(previous_scores.at[index, 'country'])

def parse_current_scores():
    read_file('./medal-data/tokyo-medal-table.csv', 'tokyo', current_scores)

def read_file(file: str, olympic_cycle: str, table):
    with open(file, newline = '') as medal_table:
        table[olympic_cycle] = math.nan
        reader = csv.reader(medal_table, quotechar = '|')
        for row in reader:
            score = (int(row[1]) * 3) + (int(row[2]) * 2) + int(row[3])
            country = row[0]
            if (country in table['country'].unique()):
                country_idx = table.index[table['country'] == country][0]
                table.at[country_idx, olympic_cycle] = score
            else:
                table.loc[len(table)] = {'country': country, olympic_cycle: score}

                

determine_tiers()
parse_current_scores()

while(True):
    if (input("Do you have an new entry to make? (y/n): ") == "n"):
        break

    name = input("Enter your name: ")
    while (name in players['name'].unique()):
        name = input("This player already exists. Please enter a new name: ")
    
    score = 0

    print("Select 2 Tier A teams. They are as follows: ", tiers['A'])
    tier_a1 = input("First Tier A Team: ")
    while (tier_a1 not in tiers['A']):
        tier_a1 = input("This country is not in Tier A. Please select a different team: ")
    score += current_scores.loc[current_scores['country'] == tier_a1, 'tokyo'].tolist()[0]
    print(score)

    tier_a2 = input("Second Tier A Team: ")
    while ((tier_a2 == tier_a1) or (tier_a2 not in tiers['A'])):
        if tier_a2 == tier_a1:
            tier_a2 = input("You have already selected this country. Please select a different team: ")
        else:
            tier_a2 = input("This country is not in Tier A. Please select a different team: ")
    score += current_scores.loc[current_scores['country'] == tier_a2, 'tokyo'].tolist()[0]
    print(score)

    print("Select 1 Tier B teams. They are as follows: ", tiers['B'])
    tier_b = input("Tier B Team: ")
    while (tier_b not in tiers['B']):
        tier_b = input("This country is not in Tier B. Please select a different team: ")
    score += current_scores.loc[current_scores['country'] == tier_b, 'tokyo'].tolist()[0]
    print(score)

    print("Select 1 Tier C teams. They are as follows: ", tiers['C'])
    tier_c = input("Tier C Team: ")
    while (tier_c not in tiers['C']):
        tier_c = input("This country is not in Tier C. Please select a different team: ")
    score += current_scores.loc[current_scores['country'] == tier_c, 'tokyo'].tolist()[0]
    print(score)

    print("Select 1 Tier D teams. They are as follows: ", tiers['D'])
    tier_d = input("Tier D Team: ")
    while (tier_d not in tiers['D']):
        tier_d = input("This country is not in Tier D. Please select a different team: ")
    score += current_scores.loc[current_scores['country'] == tier_d, 'tokyo'].tolist()[0]
    print(score)

    print("Select 3 Tier E teams. They are as follows: ", tiers['E'])
    tier_e1 = input("First Tier E Team: ")
    while (tier_e1 not in tiers['E']):
        tier_e1 = input("This country is not in Tier E. Please select a different team: ")
    score += current_scores.loc[current_scores['country'] == tier_e1, 'tokyo'].tolist()[0]
    print(score)

    tier_e2 = input("Second Tier E Team: ")
    while ((tier_e2 == tier_e1) or (tier_e2 not in tiers['E'])):
        if tier_e2 == tier_e1:
            tier_e2 = input("You have already selected this country. Please select a different team: ")
        else:
            tier_e2 = input("This country is not in Tier E. Please select a different team: ")
    score += current_scores.loc[current_scores['country'] == tier_e2, 'tokyo'].tolist()[0]
    print(score)
    
    tier_e3 = input("Third Tier E Team: ")
    while ((tier_e3 == tier_e1) or (tier_e3 == tier_e2) or (tier_e3 not in tiers['E'])):
        if tier_e3 not in tiers['E']:
            tier_e3 = input("This country is not in Tier E. Please select a different team: ")
        else:
            tier_e3 = input("You have already selected this country. Please select a different team: ")
    score += current_scores.loc[current_scores['country'] == tier_e3, 'tokyo'].tolist()[0]
    print(score)
            
    
    players.loc[len(players)] = {'name': name, 'tier a': (tier_a1, tier_a2), 'tier b': tier_b, 'tier c': tier_c, 'tier d': tier_d, 'tier e': (tier_e1, tier_e2, tier_e3), 'score': score}
    players.sort_values(by = ['score'], inplace = True, ascending = False)
    print(players.to_string())
    
