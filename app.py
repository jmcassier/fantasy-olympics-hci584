# from flask import Flask
import csv
import pandas as pd
import sqlite3

tiers = {'A': [], 'B': [], 'C': [], 'D': [], 'E': []}
players = pd.DataFrame(columns = ['name', 'tier a', 'tier b', 'tier c', 'tier d', 'tier e', 'score'])

# app = Flask(__name__)

def database_creation():
    cxn = sqlite3.connect('olympic_stats.db')
    cxn.execute('DROP TABLE IF EXISTS olympic_stats')
    cxn.execute('''
        CREATE TABLE olympic_stats (
            Country text primary key
        );
    ''')

    read_medal_table('./medal-data/beijing-medal-table.csv', 'Beijing', cxn)
    read_medal_table('./medal-data/london-medal-table.csv', 'London', cxn)
    read_medal_table('./medal-data/rio-medal-table.csv', 'Rio', cxn)

    read_previous_results('./medal-data/archery/previous-archery.csv', 'Archery', cxn)
    read_previous_results('./medal-data/athletics/previous-athletics.csv', 'Athletics', cxn)
    read_previous_results('./medal-data/badminton/previous-badminton.csv', 'Badminton', cxn)
    read_previous_results('./medal-data/baseball/previous-baseball.csv', 'Baseball', cxn)
    read_previous_results('./medal-data/basketball/previous-basketball.csv', 'Basketball', cxn)
    read_previous_results('./medal-data/boxing/previous-boxing.csv', 'Boxing', cxn)
    read_previous_results('./medal-data/canoe/previous-canoe.csv', 'Canoe', cxn)
    read_previous_results('./medal-data/cycling/previous-cycling.csv', 'Cycling', cxn)
    read_previous_results('./medal-data/diving/previous-diving.csv', 'Diving', cxn)
    read_previous_results('./medal-data/equestrian/previous-equestrian.csv', 'Equestrian', cxn)
    read_previous_results('./medal-data/fencing/previous-fencing.csv', 'Fencing', cxn)
    read_previous_results('./medal-data/field-hockey/previous-field-hockey.csv', 'Field Hockey', cxn)
    read_previous_results('./medal-data/football/previous-football.csv', 'Football (Soccer)', cxn)
    read_previous_results('./medal-data/golf/previous-golf.csv', 'Golf', cxn)
    read_previous_results('./medal-data/gymnastics/previous-gymnastics.csv', 'Gymnastics', cxn)
    read_previous_results('./medal-data/handball/previous-handball.csv', 'Handball', cxn)
    read_previous_results('./medal-data/judo/previous-judo.csv', 'Judo', cxn)
    read_previous_results('./medal-data/modern-pentathlon/previous-modern-pentathlon.csv', 'Modern Pentathlon', cxn)
    read_previous_results('./medal-data/rowing/previous-rowing.csv', 'Rowing', cxn)
    read_previous_results('./medal-data/rugby/previous-rugby.csv', 'Rugby', cxn)
    read_previous_results('./medal-data/sailing/previous-sailing.csv', 'Sailing', cxn)
    read_previous_results('./medal-data/shooting/previous-shooting.csv', 'Shooting', cxn)
    read_previous_results('./medal-data/softball/previous-softball.csv', 'Softball', cxn)
    read_previous_results('./medal-data/swimming/previous-swimming.csv', 'Swimming', cxn)
    read_previous_results('./medal-data/table-tennis/previous-table-tennis.csv', 'Table Tennis', cxn)
    read_previous_results('./medal-data/taekwondo/previous-taekwondo.csv', 'Taekwondo', cxn)
    read_previous_results('./medal-data/tennis/previous-tennis.csv', 'Tennis', cxn)
    read_previous_results('./medal-data/triathlon/previous-triathlon.csv', 'Triathlon', cxn)
    read_previous_results('./medal-data/volleyball/previous-volleyball.csv', 'Volleyball', cxn)
    read_previous_results('./medal-data/water-polo/previous-water-polo.csv', 'Water Polo', cxn)
    read_previous_results('./medal-data/weightlifting/previous-weightlifting.csv', 'Weightlifting', cxn)
    read_previous_results('./medal-data/wrestling/previous-wrestling.csv', 'Wrestling', cxn)

    cxn.close()

def read_medal_table(file: str, column_name: str, cxn):
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

def read_previous_results(file: str, event_name: str, cxn):
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
            # print(columns)
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
    


                

database_creation()
