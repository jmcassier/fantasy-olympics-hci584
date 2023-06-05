import csv
import pandas as pd
import math

previous_scores = pd.DataFrame(columns = ["country"])
current_scores = pd.DataFrame(columns = ["country"])

# app = Flask(__name__)

# @app.before_first_request
def determine_tiers():
    read_file('./medal-data/beijing-medal-table.csv', 'beijing', previous_scores)
    read_file('./medal-data/london-medal-table.csv', 'london', previous_scores)
    read_file('./medal-data/rio-medal-table.csv', 'rio', previous_scores)

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

print(previous_scores)
print(current_scores)
