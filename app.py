# from flask import Flask
import csv
import pandas as pd
import sqlite3

tiers = {'A': [], 'B': [], 'C': [], 'D': [], 'E': []}
players = pd.DataFrame(columns = ['name', 'tier a', 'tier b', 'tier c', 'tier d', 'tier e', 'score'])
cxn = sqlite3.connect('olympic_stats.db')

# app = Flask(__name__)

def database_creation():
    table_exists = cxn.execute('''
        SELECT tbl_name FROM sqlite_master WHERE type='table' AND tbl_name='olympic_stats'
    ''').fetchall()
    if table_exists == []:
        cxn.execute('''
            CREATE TABLE olympic_stats (
                Country text primary key
            );
        ''')
        cxn.commit()

        read_medal_table('./medal-data/beijing-medal-table.csv', 'Beijing')
        read_medal_table('./medal-data/london-medal-table.csv', 'London')
        read_medal_table('./medal-data/rio-medal-table.csv', 'Rio')

        read_previous_results('./medal-data/archery/previous-archery.csv', 'Archery')
        read_previous_results('./medal-data/athletics/previous-athletics.csv', 'Athletics')
        read_previous_results('./medal-data/badminton/previous-badminton.csv', 'Badminton')
        read_previous_results('./medal-data/baseball/previous-baseball.csv', 'Baseball')
        read_previous_results('./medal-data/basketball/previous-basketball.csv', 'Basketball')
        read_previous_results('./medal-data/boxing/previous-boxing.csv', 'Boxing')
        read_previous_results('./medal-data/canoe/previous-canoe.csv', 'Canoe')
        read_previous_results('./medal-data/cycling/previous-cycling.csv', 'Cycling')
        read_previous_results('./medal-data/diving/previous-diving.csv', 'Diving')
        read_previous_results('./medal-data/equestrian/previous-equestrian.csv', 'Equestrian')
        read_previous_results('./medal-data/fencing/previous-fencing.csv', 'Fencing')
        read_previous_results('./medal-data/field-hockey/previous-field-hockey.csv', 'Field Hockey')
        read_previous_results('./medal-data/football/previous-football.csv', 'Football (Soccer)')
        read_previous_results('./medal-data/golf/previous-golf.csv', 'Golf')
        read_previous_results('./medal-data/gymnastics/previous-gymnastics.csv', 'Gymnastics')
        read_previous_results('./medal-data/handball/previous-handball.csv', 'Handball')
        read_previous_results('./medal-data/judo/previous-judo.csv', 'Judo')
        read_previous_results('./medal-data/modern-pentathlon/previous-modern-pentathlon.csv', 'Modern Pentathlon')
        read_previous_results('./medal-data/rowing/previous-rowing.csv', 'Rowing')
        read_previous_results('./medal-data/rugby/previous-rugby.csv', 'Rugby')
        read_previous_results('./medal-data/sailing/previous-sailing.csv', 'Sailing')
        read_previous_results('./medal-data/shooting/previous-shooting.csv', 'Shooting')
        read_previous_results('./medal-data/softball/previous-softball.csv', 'Softball')
        read_previous_results('./medal-data/swimming/previous-swimming.csv', 'Swimming')
        read_previous_results('./medal-data/table-tennis/previous-table-tennis.csv', 'Table Tennis')
        read_previous_results('./medal-data/taekwondo/previous-taekwondo.csv', 'Taekwondo')
        read_previous_results('./medal-data/tennis/previous-tennis.csv', 'Tennis')
        read_previous_results('./medal-data/triathlon/previous-triathlon.csv', 'Triathlon')
        read_previous_results('./medal-data/volleyball/previous-volleyball.csv', 'Volleyball')
        read_previous_results('./medal-data/water-polo/previous-water-polo.csv', 'Water Polo')
        read_previous_results('./medal-data/weightlifting/previous-weightlifting.csv', 'Weightlifting')
        read_previous_results('./medal-data/wrestling/previous-wrestling.csv', 'Wrestling')

    rows = cxn.execute('''
        SELECT * FROM olympic_stats
    ''').fetchall()

    for row in rows:
        beijing = row[1]
        london = row[2]
        rio = row[3]
        avg = (beijing + london + rio) / 3
        if (avg >= 100):
            tiers['A'].append(row[0])
        elif (avg >= 60):
            tiers['B'].append(row[0])
        elif (avg >= 35):
            tiers['C'].append(row[0])
        elif (avg >= 30):
            tiers['D'].append(row[0])
        elif (avg >= 13):
            tiers['E'].append(row[0])

    cxn.close()

def read_medal_table(file: str, column_name: str):
    with open(file, newline = '') as medal_table:
        cxn.execute('''
            ALTER TABLE olympic_stats ADD COLUMN %s int DEFAULT 0
            ''' % (column_name)
        )
        cxn.commit()
        reader = csv.reader(medal_table, quotechar = '|')
        for row in reader:
            score = (int(row[1]) * 3) + (int(row[2]) * 2) + int(row[3])
            country = row[0]
            
            in_table = cxn.execute('''
                SELECT COUNT(*)
                FROM olympic_stats
                WHERE country = ?
                ''',
                (country,)
            ).fetchone()[0]

            if (in_table != 0):
                cxn.execute('''
                    UPDATE olympic_stats
                    SET %s = ?
                    WHERE country = ?
                    ''' % (column_name),
                    (score, country)
                )
                cxn.commit()
            else:
                cxn.execute('''
                    INSERT INTO olympic_stats (country, %s)
                    VALUES (?, ?)
                    ''' % (column_name),
                    (country, score)
                )
                cxn.commit()

def read_previous_results(file: str, event_name: str):
    with open(file, newline = '') as prev_data:
        reader = csv.reader(prev_data, quotechar = '|')
        for row in reader:
            column_name = event_name + ' - ' + row[0]
            medal = row[1]
            countries = row[2:]

            cursor = cxn.execute('''
                SELECT * FROM olympic_stats
            ''')
            columns = list(map(lambda x: x[0], cursor.description))
            if (column_name not in columns):
                cxn.execute('''
                    ALTER TABLE olympic_stats ADD COLUMN `%s` int DEFAULT 0
                    ''' % column_name
                )
                cxn.commit()

            for country in countries:
                to_add = 1
                if (medal == 'Gold'):
                    to_add = 3
                elif (medal == 'Silver'):
                    to_add = 2
                
                cxn.execute('''
                    UPDATE olympic_stats SET `%s` = `%s` + ? WHERE country = ?
                    ''' % (column_name, column_name),
                    (to_add, country)
                )
                cxn.commit()

def pick_league():
    name = input("Enter your name: ")

    print("Select 2 Tier A teams. They are as follows: ", tiers['A'])
    tier_a1 = input("First Tier A Team: ")
    while (tier_a1 not in tiers['A']):
        tier_a1 = input("This country is not in Tier A. Please select a different team: ")
    
    tier_a2 = input("Second Tier A Team: ")
    while ((tier_a2 == tier_a1) or (tier_a2 not in tiers['A'])):
        if tier_a2 == tier_a1:
            tier_a2 = input("You have already selected this country. Please select a different team: ")
        else:
            tier_a2 = input("This country is not in Tier A. Please select a different team: ")
    
    print("Select 1 Tier B teams. They are as follows: ", tiers['B'])
    tier_b = input("Tier B Team: ")
    while (tier_b not in tiers['B']):
        tier_b = input("This country is not in Tier B. Please select a different team: ")

    print("Select 1 Tier C teams. They are as follows: ", tiers['C'])
    tier_c = input("Tier C Team: ")
    while (tier_c not in tiers['C']):
        tier_c = input("This country is not in Tier C. Please select a different team: ")
    
    print("Select 1 Tier D teams. They are as follows: ", tiers['D'])
    tier_d = input("Tier D Team: ")
    while (tier_d not in tiers['D']):
        tier_d = input("This country is not in Tier D. Please select a different team: ")

    print("Select 3 Tier E teams. They are as follows: ", tiers['E'])
    tier_e1 = input("First Tier E Team: ")
    while (tier_e1 not in tiers['E']):
        tier_e1 = input("This country is not in Tier E. Please select a different team: ")
    
    tier_e2 = input("Second Tier E Team: ")
    while ((tier_e2 == tier_e1) or (tier_e2 not in tiers['E'])):
        if tier_e2 == tier_e1:
            tier_e2 = input("You have already selected this country. Please select a different team: ")
        else:
            tier_e2 = input("This country is not in Tier E. Please select a different team: ")
    
    tier_e3 = input("Third Tier E Team: ")
    while ((tier_e3 == tier_e1) or (tier_e3 == tier_e2) or (tier_e3 not in tiers['E'])):
        if tier_e3 not in tiers['E']:
            tier_e3 = input("This country is not in Tier E. Please select a different team: ")
        else:
            tier_e3 = input("You have already selected this country. Please select a different team: ")
    
    players.loc[len(players)] = {
        'name': name,
        'tier a': (tier_a1, tier_a2),
        'tier b': tier_b,
        'tier c': tier_c,
        'tier d': tier_d,
        'tier e': (tier_e1, tier_e2, tier_e3),
        'score': 0
    }
    print(players.to_string())

def end_game():
    cxn.close()

database_creation()
pick_league()
end_game()
