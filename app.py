# from flask import Flask
import csv
import pandas as pd
import math
import sqlite3

previous_scores = pd.DataFrame(columns = ["country"])
current_scores = pd.DataFrame(columns = ["country"])
tiers = {'A': [], 'B': [], 'C': [], 'D': [], 'E': []}
players = pd.DataFrame(columns = ["name", "tier a", "tier b", "tier c", "tier d", "tier e", "score"])

# app = Flask(__name__)

# @app.before_first_request
def determine_tiers():
    cxn = sqlite3.connect('olympic_stats.db')
    cxn.execute('DROP TABLE IF EXISTS olympic_stats')
    cxn.execute('DROP TABLE IF EXISTS duplicate')
    cxn.execute('''
        CREATE TABLE olympic_stats (
            country text primary key
        );
    ''')

    read_medal_table('./medal-data/beijing-medal-table.csv', 'beijing', cxn)
    read_medal_table('./medal-data/london-medal-table.csv', 'london', cxn)
    read_medal_table('./medal-data/rio-medal-table.csv', 'rio', cxn)

def read_medal_table(file: str, column_name: str, connect):
    with open(file, newline = '') as medal_table:
        connect.execute('''
            ALTER TABLE olympic_stats ADD COLUMN %s int DEFAULT 0
            ''' % (column_name)
        )
        connect.commit()
        reader = csv.reader(medal_table, quotechar = '|')
        for row in reader:
            score = (int(row[1]) * 3) + (int(row[2]) * 2) + int(row[3])
            country = row[0]
            
            in_table = connect.execute('''
                SELECT COUNT(*)
                FROM olympic_stats
                WHERE country = ?
                ''',
                (country,)
            ).fetchone()[0]

            if (in_table != 0):
                connect.execute('''
                    UPDATE olympic_stats
                    SET %s = ?
                    WHERE country = ?
                    ''' % (column_name),
                    (score, country)
                )
                connect.commit()
            else:
                connect.execute('''
                    INSERT INTO olympic_stats (country, %s)
                    VALUES (?, ?)
                    ''' % (column_name),
                    (country, score)
                )
                connect.commit()


                

determine_tiers()
