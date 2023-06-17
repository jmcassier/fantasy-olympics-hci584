# from flask import Flask
import csv
import pandas as pd
import sqlite3
import random

tiers = {'A': [], 'B': [], 'C': [], 'D': [], 'E': []}
players = pd.DataFrame(columns = ['Name', 'Tier A', 'Tier B', 'Tier C', 'Tier D', 'Tier E', 'Score'])
cxn = sqlite3.connect('olympic_stats.db')
unplayed_events = []
new_events = []
dual_bronze = ['Boxing', 'Judo', 'Karate', 'Taekwondo', 'Wrestling'] # these events always give 2 bronze medals
game_medal_table = pd.DataFrame(columns = ['Country', 'Gold', 'Silver', 'Bronze', 'Score'])

# app = Flask(__name__)

def database_creation():
    # cxn.execute('DROP TABLE IF EXISTS scores_by_olympic_cycle')
    # cxn.execute('DROP TABLE IF EXISTS scores_by_event')
    # cxn.execute('DROP TABLE IF EXISTS event_athletes')
    table_by_cycle_exists = cxn.execute('''
        SELECT tbl_name FROM sqlite_master WHERE type='table' AND (tbl_name='scores_by_olympic_cycle')
    ''').fetchall()
    table_by_event_exists = cxn.execute('''
        SELECT tbl_name FROM sqlite_master WHERE type='table' AND (tbl_name='scores_by_event')
    ''').fetchall()
    event_athletes_exists = cxn.execute('''
        SELECT tbl_name FROM sqlite_master WHERE type='table' AND (tbl_name='event_athletes')
    ''').fetchall()

    if table_by_cycle_exists == []:
        print("creating by cycle")
        cxn.execute('''
            CREATE TABLE scores_by_olympic_cycle (
                Country text primary key
            );
        ''')
        cxn.commit()

        read_medal_table('./medal-data/beijing-medal-table.csv', 'Beijing')
        read_medal_table('./medal-data/london-medal-table.csv', 'London')
        read_medal_table('./medal-data/rio-medal-table.csv', 'Rio')

    if table_by_event_exists == []:
        print("creating by event")
        cxn.execute('''
            CREATE TABLE scores_by_event (
                Country text primary key
            );
        ''')
        cxn.commit()

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
        SELECT * FROM scores_by_olympic_cycle
    ''').fetchall()

    for row in rows:
        # handle North Korea not participating in the 2020 Olympic Games
        if row[0] == 'North Korea':
            continue
        beijing = row[1]
        london = row[2]
        rio = row[3]
        avg = (beijing + london + rio) / 3
        if avg >= 100:
            tiers['A'].append(row[0])
        elif avg >= 60:
            tiers['B'].append(row[0])
        elif avg >= 35:
            tiers['C'].append(row[0])
        elif avg >= 30:
            tiers['D'].append(row[0])
        elif avg >= 13:
            tiers['E'].append(row[0])

    if event_athletes_exists == []:
        print("creating by athletes table")
        cxn.execute('''
            CREATE TABLE event_athletes (
                Event text primary key,
                Athlete1 text DEFAULT NULL,
                Athlete2 text DEFAULT NULL,
                Athlete3 text DEFAULT NULL,
                Athlete4 text DEFAULT NULL,
                Athlete5 text DEFAULT NULL,
                Athlete6 text DEFAULT NULL,
                Athlete7 text DEFAULT NULL,
                Athlete8 text DEFAULT NULL
            );
        ''')
        cxn.commit()
        read_event_athletes('./medal-data/tokyo-event-list.csv')
    else:
        events = cxn.execute('''
            SELECT Event
            FROM event_athletes
        ''').fetchall()
        for event in events:
            unplayed_events.append(event[0])
    
    
    cursor = cxn.execute('''
        SELECT * FROM scores_by_event
    ''')
    previously_played = list(map(lambda x: x[0], cursor.description))
    for unplayed in unplayed_events:
        if unplayed not in previously_played:
            new_events.append(unplayed)


def read_medal_table(file: str, column_name: str):
    with open(file, newline = '') as medal_table:
        cxn.execute(f'''
            ALTER TABLE scores_by_olympic_cycle ADD COLUMN {column_name} int DEFAULT 0
            '''
        )
        cxn.commit()
        reader = csv.reader(medal_table, quotechar = '|')
        for row in reader:
            score = (int(row[1]) * 3) + (int(row[2]) * 2) + int(row[3])
            country = row[0]
            
            country_in_table = cxn.execute('''
                SELECT COUNT(*)
                FROM scores_by_olympic_cycle
                WHERE Country = ?
                ''',
                (country,)
            ).fetchone()[0]

            if country_in_table != 0:
                cxn.execute(f'''
                    UPDATE scores_by_olympic_cycle
                    SET {column_name} = ?
                    WHERE Country = ?
                    ''',
                    (score, country)
                )
                cxn.commit()
            else:
                cxn.execute(f'''
                    INSERT INTO scores_by_olympic_cycle (Country, {column_name})
                    VALUES (?, ?)
                    ''',
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
                SELECT * FROM scores_by_event
            ''')
            columns = list(map(lambda x: x[0], cursor.description))
            if column_name not in columns:
                cxn.execute(f'''
                    ALTER TABLE scores_by_event ADD COLUMN `{column_name}` int DEFAULT 0
                    '''
                )
                cxn.commit()

            for country in countries:
                if country == '':
                    continue
                to_add = 1
                if medal == 'Gold':
                    to_add = 3
                elif medal == 'Silver':
                    to_add = 2
                
                country_in_table = cxn.execute('''
                    SELECT COUNT(*)
                    FROM scores_by_event
                    WHERE Country = ?
                    ''',
                    (country,)
                ).fetchone()[0]

                if country_in_table != 0:
                    cxn.execute(f'''
                        UPDATE scores_by_event 
                        SET `{column_name}` = `{column_name}` + ? 
                        WHERE Country = ?
                        ''',
                        (to_add, country)
                    )
                    cxn.commit()
                else:
                    cxn.execute(f'''
                        INSERT INTO scores_by_event (Country, `{column_name}`)
                        VALUES (?, ?)
                        ''',
                        (country, to_add)
                    )
                    cxn.commit()

def read_event_athletes(file: str):
    with open(file, newline = '') as event_list:
        reader = csv.reader(event_list, quotechar = '|')
        for event in reader:
            unplayed_events.append(event[0])
            cxn.execute('''
                INSERT INTO event_athletes
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (event[0], event[1], event[2], event[3], event[4], event[5], event[6], event[7], event[8])
            )
            cxn.commit()

def pick_league():
    name = input("Enter your name: ")

    print("Select 2 Tier A teams. They are as follows: ", tiers['A'])
    tier_a1 = input("First Tier A Team: ")
    while tier_a1 not in tiers['A']:
        tier_a1 = input("This country is not in Tier A. Please select a different team: ")
    
    tier_a2 = input("Second Tier A Team: ")
    while (tier_a2 == tier_a1) or (tier_a2 not in tiers['A']):
        if tier_a2 == tier_a1:
            tier_a2 = input("You have already selected this country. Please select a different team: ")
        else:
            tier_a2 = input("This country is not in Tier A. Please select a different team: ")
    
    print("Select 1 Tier B teams. They are as follows: ", tiers['B'])
    tier_b = input("Tier B Team: ")
    while tier_b not in tiers['B']:
        tier_b = input("This country is not in Tier B. Please select a different team: ")

    print("Select 1 Tier C teams. They are as follows: ", tiers['C'])
    tier_c = input("Tier C Team: ")
    while tier_c not in tiers['C']:
        tier_c = input("This country is not in Tier C. Please select a different team: ")
    
    print("Select 1 Tier D teams. They are as follows: ", tiers['D'])
    tier_d = input("Tier D Team: ")
    while tier_d not in tiers['D']:
        tier_d = input("This country is not in Tier D. Please select a different team: ")

    print("Select 3 Tier E teams. They are as follows: ", tiers['E'])
    tier_e1 = input("First Tier E Team: ")
    while tier_e1 not in tiers['E']:
        tier_e1 = input("This country is not in Tier E. Please select a different team: ")
    
    tier_e2 = input("Second Tier E Team: ")
    while (tier_e2 == tier_e1) or (tier_e2 not in tiers['E']):
        if tier_e2 == tier_e1:
            tier_e2 = input("You have already selected this country. Please select a different team: ")
        else:
            tier_e2 = input("This country is not in Tier E. Please select a different team: ")
    
    tier_e3 = input("Third Tier E Team: ")
    while (tier_e3 == tier_e1) or (tier_e3 == tier_e2) or (tier_e3 not in tiers['E']):
        if tier_e3 not in tiers['E']:
            tier_e3 = input("This country is not in Tier E. Please select a different team: ")
        else:
            tier_e3 = input("You have already selected this country. Please select a different team: ")
    
    players.loc[len(players)] = {
        'Name': name,
        'Tier A': [tier_a1, tier_a2],
        'Tier B': tier_b,
        'Tier C': tier_c,
        'Tier D': tier_d,
        'Tier E': [tier_e1, tier_e2, tier_e3],
        'Score': 0
    }
    print(players.to_string())

def game_play():
    while len(unplayed_events) > 0:
        curr_event = random.choice(unplayed_events)
        unplayed_events.remove(curr_event)
        athletes = cxn.execute('''
            SELECT *
            FROM event_athletes
            WHERE Event = ?
            ''',
            (curr_event,)
        ).fetchone()

        if athletes[7] == '' and athletes[8] == '':
            athletes = list(athletes[1:7])
        else:
            athletes = list(athletes[1:])

        
        previously_played = False if curr_event in new_events else True
        event_medalists = []
        num_medals = 4 if curr_event.split(' ')[0] in dual_bronze else 3
        print(f'{curr_event}: {num_medals} medals')

        if previously_played:
            weighted_athletes = []
            for athlete in athletes:
                weight = cxn.execute(f'''
                    SELECT `{curr_event}`
                    FROM scores_by_event
                    WHERE country = ?
                    ''',
                    (athlete,)
                ).fetchone()
                if weight is not None:
                    weighted_athletes.append(weight[0]+1)
                else:
                    weighted_athletes.append(1)
            for index in range(0, num_medals):
                medalist = random.choices(athletes, weights = weighted_athletes)[0]
                print(medalist)
                medalist_index = athletes.index(medalist)
                athletes.remove(medalist)
                del weighted_athletes[medalist_index]
                event_medalists.append(medalist)
                if index == 0:
                    update_game_medals(medalist, 'Gold')
                elif index == 1:
                    update_game_medals(medalist, 'Silver')
                else:
                    update_game_medals(medalist)   
        else:
            for index in range(0, num_medals):
                medalist = random.choice(athletes)
                athletes.remove(medalist)
                event_medalists.append(medalist)
                if index == 0:
                    update_game_medals(medalist, 'Gold')
                elif index == 1:
                    update_game_medals(medalist, 'Silver')
                else:
                    update_game_medals(medalist)
        
        print(f'gold medalist: {event_medalists[0]}' )
        print(f'silver medalist: {event_medalists[1]}' )
        if num_medals == 4:
            print(f'bronze medalists: {event_medalists[2]} and {event_medalists[3]}' )
        else:
            print(f'bronze medalist: {event_medalists[2]}' )
        update_player_scores(event_medalists)
        
        input('continue? ')   

def update_game_medals(country: str, medal: str = 'Bronze'):
    country_idx = None
    if country in game_medal_table['Country'].unique():
        country_idx = game_medal_table.index[game_medal_table['Country'] == country][0]
    else:
        country_idx = len(game_medal_table)
        game_medal_table.loc[country_idx] = {'Country': country, 'Gold': 0, 'Silver': 0, 'Bronze': 0, 'Score': 0}
    
    game_medal_table.at[country_idx, medal] += 1
    if medal == 'Gold':
        game_medal_table.at[country_idx, 'Score'] += 3
    elif medal == 'Silver':
        game_medal_table.at[country_idx, 'Score'] += 2
    elif medal == 'Bronze':
        game_medal_table.at[country_idx, 'Score'] += 1

def update_player_scores(medalists: list):
    for index, player in players.iterrows():
        league = [player[1][0], player[1][1], player[2], player[3], player[4], player[5][0], player[5][1], player[5][2]]
        if medalists[0] in league:
            players.at[index, 'Score'] += 3
        if medalists[1] in league:
            players.at[index, 'Score'] += 2
        if medalists[2] in league:
            players.at[index, 'Score'] += 1
        if (len(medalists) == 4) and (medalists[3] in league):
            players.at[index, 'Score'] += 1

    print(players)

def end_game():
    cxn.close()

database_creation()
pick_league()
game_play()
end_game()
