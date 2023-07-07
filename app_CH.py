from flask import Flask, render_template, redirect, url_for, request
from flask_cachecontrol import dont_cache
import csv
import pandas as pd
import sqlite3
import random
import numpy as np

tiers = {'A': [], 'B': [], 'C': [], 'D': [], 'E': []}
players = pd.DataFrame(
    columns = [
        'Name', 
        'Tier A', 
        'Tier B', 
        'Tier C', 
        'Tier D', 
        'Tier E', 
        'Score'
    ]
)
cxn = sqlite3.connect('olympic_stats.db', check_same_thread=False)
unplayed_events = []
previously_played_events = []

# these events always give 2 bronze medals
dual_bronze = ['Boxing', 'Judo', 'Karate', 'Taekwondo', 'Wrestling']

game_medal_table = pd.DataFrame(
    columns = ['Country', 'Gold', 'Silver', 'Bronze', 'Score']
)
draft_order = []
current_draft_pick = 0
draft_round = [1, 'A']
country_codes = {} # used to determine flag icons in UI
error_msg = None # any error message to be displayed on the UI.

app = Flask(__name__)

@app.route('/')
@dont_cache()
def home_page():
    '''
    Creates the home page of the UI that has a description of the game,
    the rules of the game, and the player name inputs
    '''

    # if the home page loads with players or teams in the medal table,
    # reset the game
    if (len(players.index) > 0) or (len(game_medal_table) > 0):
        reset_game()
    
    return render_template('home.html')

@app.route('/draft', methods = ["POST", "GET"])
def draft_page():
    '''
    Creates the draft page of the UI which allows for players to draft
    which available teams to their league and connects the front-end
    with the back-end
    '''

    # ensure global variables are used
    global draft_order, current_draft_pick, draft_round, error_msg

    # actions to take if Confirm Players button was clicked
    if (request.method == "POST") and \
        (request.form.get("submit") is not None) and \
        (request.form["submit"] == "Confirm Players"):
        if len(players) == 0:
            set_players(request.form.to_dict(flat=False))
        error_msg = None
        return redirect(url_for('draft_page'), 302)
    
    # actions to take if a team was selected by a players
    if request.method == "POST":
        # actions to take if the team is not already in the player's
        # league
        if draft_team(list(request.form.keys())[0], draft_round[1]):
            # redirect to the main game play page if draft round is 9,
            # which indicates the draft is over.
            if draft_round[0] == 9:
                return redirect(url_for('play_game'))
            error_msg = None

            # redirect for POST-redirect-GET to ensure form isn't 
            # submitted multiple times if reloaded
            return redirect(url_for('draft_page'), 302) 

        error_msg = '''You have already selected this country. 
            Please select a different country'''
        # redirect for POST-redirect-GET to ensure form isn't submitted
        # multiple times if reloaded        
        return redirect(url_for('draft_page'), 302)
    
    # actions to take if the page is rendered for a GET request.
    else:
        avail_country_codes = []
        for country in tiers[draft_round[1]]:
            if country_codes[country] not in avail_country_codes:
                avail_country_codes.append(country_codes[country])

        if error_msg is not None:
            return render_template('draft.html',
                                   player=draft_order[current_draft_pick], 
                                   available_countries=tiers[draft_round[1]], 
                                   country_codes=avail_country_codes,
                                   round=draft_round[0],
                                   error=error_msg)
        
        return render_template('draft.html', 
                               player=draft_order[current_draft_pick],
                               available_countries=tiers[draft_round[1]],
                               country_codes=avail_country_codes,
                               round=draft_round[0])

"""
@app.route('/play-game', methods = ["GET", "POST"])
def play_game():
    '''
    Creates the game play page of the UI which allows for players to
    see how the game is unfolding and their rank amongst other players.
    '''
    
    if len(unplayed_events) == 0:
        print(players)
        return render_template('game.html', game_over="game over")
    
    game_play()
    scoreboard_data = []
    for player in players.iterrows():
        scoreboard_data.append(
            players.loc[player[0], :].values.flatten().tolist()
        )
    return render_template('game.html', scoreboard=scoreboard_data)
"""
import time
from flask import Response, stream_with_context
@app.route('/play-game', methods = ["GET", "POST"])
def play_game():
    '''demo for streaming html'''

    # def a generator that
    def game_generator():
        for round in range(5):  # hard coding 5 rounds
            html = "Round " + str(round) + "<br>"   # or use render_template into a html string
            yield html # "prints" html string into browser
            time.sleep(2) # wait 2 secs

    r =  Response(stream_with_context(game_generator()), mimetype='text/html')
    return r

def set_players(players_dict: dict):
    '''
    Add the players to the players dataframe and determine the number
    of times each country is available for the draft.
    '''

    global draft_order, current_draft_pick, draft_round
    draft_order = []
    draft_round = [1, 'A']
    for player in players_dict:
        name = players_dict[player][0]
        if name == 'Confirm Players':
            continue
        draft_order.append(name)
        players.loc[len(players.index)] = {
                'Name': name,
                'Tier A': [],
                'Tier B': None,
                'Tier C': None,
                'Tier D': None,
                'Tier E': [],
                'Score': 0
        }
    current_draft_pick = 0
    random.shuffle(draft_order)

    player_count = len(draft_order)
    
    if player_count == 3:
        tiers['A'] = np.repeat(tiers['A'][:], 2).tolist()
    elif player_count == 4:
        tiers['A'] = np.repeat(tiers['A'][:], 3).tolist()
    elif player_count == 5:
        tiers['A'] = np.repeat(tiers['A'][:], 3).tolist()
        tiers['B'] = np.repeat(tiers['B'][:], 2).tolist()
        tiers['C'] = np.repeat(tiers['C'][:], 2).tolist()
        tiers['E'] = np.repeat(tiers['E'][:], 2).tolist()
    elif player_count == 6:
        tiers['A'] = np.repeat(tiers['A'][:], 4).tolist()
        tiers['B'] = np.repeat(tiers['B'][:], 2).tolist()
        tiers['C'] = np.repeat(tiers['C'][:], 2).tolist()
        tiers['D'] = np.repeat(tiers['D'][:], 2).tolist()
        tiers['E'] = np.repeat(tiers['E'][:], 2).tolist()

def draft_team(drafted_team: str, tier: str):
    '''
    Add team to each players draft if possible

    :return: if the team was successfully added. should only return
             false if the team is already in a player's league
    '''
    
    global current_draft_pick, draft_order, draft_round
    player_index = players.index[
        players['Name'] == draft_order[current_draft_pick]
    ][0]

    if (tier == 'A' or tier == 'E') and \
        (drafted_team in players.at[player_index, 'Tier ' + tier]):
        return False
    
    if tier == 'A' or tier == 'E':
        players.at[player_index, 'Tier ' + tier].append(drafted_team)
    else:
        players.at[player_index, 'Tier ' + tier] = drafted_team
    
    tiers[tier].remove(drafted_team)
    current_draft_pick = (current_draft_pick + 1) % len(draft_order)
    if current_draft_pick == 0:
        draft_order.reverse()
        draft_round[0] += 1
        if draft_round[0] == 3:
            draft_round[1] = 'B'
        if draft_round[0] == 4:
            draft_round[1] = 'C'
        if draft_round[0] == 5:
            draft_round[1] = 'D'
        if draft_round[0] == 6:
            draft_round[1] = 'E'
    return True

def database_creation():
    '''
    This function completes the following preprocessing steps required
    for the game to be played:

        1) creates the following tables in the database:
            a) score_by_olympic_cycle, which holds the scores a country
            earned in the olympics from 2008 - 2016.
            b) score_by_event, which holds the weights a country has
            for each event for weight random selection when medalists 
            are determined
            c) event_athletes, which holds the participants for each
            event played in game

        2) determines which countries are in each tier for player
           drafting

        3) sets which events have been previously played to know which
        events will use weighted selection (new events do not have 
        historical data to create weights from)
    '''

    # uncomment any of the following 3 lines to remove any of the
    # tables in the database to recreate them
    # cxn.execute('DROP TABLE IF EXISTS scores_by_olympic_cycle')
    # cxn.execute('DROP TABLE IF EXISTS scores_by_event')
    # cxn.execute('DROP TABLE IF EXISTS event_athletes')

    # check if the required tables exist
    table_by_cycle_exists = cxn.execute('''
        SELECT tbl_name FROM sqlite_master 
        WHERE type='table' 
        AND (tbl_name='scores_by_olympic_cycle')
    ''').fetchall()
    table_by_event_exists = cxn.execute('''
        SELECT tbl_name FROM sqlite_master 
        WHERE type='table' 
        AND (tbl_name='scores_by_event')
    ''').fetchall()
    event_athletes_exists = cxn.execute('''
        SELECT tbl_name FROM sqlite_master 
        WHERE type='table' 
        AND (tbl_name='event_athletes')
    ''').fetchall()

    # create scores_by_olympic_cycle if not in the database
    if table_by_cycle_exists == []:
        cxn.execute('''
            CREATE TABLE scores_by_olympic_cycle (
                Country text primary key
            );
        ''')
        cxn.commit()

        read_medal_table('./medal-data/beijing-medal-table.csv', 'Beijing')
        read_medal_table('./medal-data/london-medal-table.csv', 'London')
        read_medal_table('./medal-data/rio-medal-table.csv', 'Rio')

    # create scores_by_event if not in the database
    if table_by_event_exists == []:
        cxn.execute('''
            CREATE TABLE scores_by_event (
                Country text primary key
            );
        ''')
        cxn.commit()

        read_previous_results('./medal-data/archery/previous-archery.csv',
                               'Archery')
        read_previous_results('./medal-data/athletics/previous-athletics.csv', 
                              'Athletics')
        read_previous_results('./medal-data/badminton/previous-badminton.csv', 
                              'Badminton')
        read_previous_results('./medal-data/baseball/previous-baseball.csv', 
                              'Baseball')
        read_previous_results(
            './medal-data/basketball/previous-basketball.csv', 
            'Basketball'
        )
        read_previous_results('./medal-data/boxing/previous-boxing.csv', 
                              'Boxing')
        read_previous_results('./medal-data/canoe/previous-canoe.csv',
                              'Canoe')
        read_previous_results('./medal-data/cycling/previous-cycling.csv', 
                              'Cycling')
        read_previous_results('./medal-data/diving/previous-diving.csv', 
                              'Diving')
        read_previous_results(
            './medal-data/equestrian/previous-equestrian.csv', 
            'Equestrian'
        )
        read_previous_results('./medal-data/fencing/previous-fencing.csv', 
                              'Fencing')
        read_previous_results(
            './medal-data/field-hockey/previous-field-hockey.csv', 
            'Field Hockey'
        )
        read_previous_results('./medal-data/football/previous-football.csv', 
                              'Football (Soccer)')
        read_previous_results('./medal-data/golf/previous-golf.csv', 'Golf')
        read_previous_results(
            './medal-data/gymnastics/previous-gymnastics.csv', 
            'Gymnastics'
        )
        read_previous_results('./medal-data/handball/previous-handball.csv', 
                              'Handball')
        read_previous_results('./medal-data/judo/previous-judo.csv', 'Judo')
        read_previous_results(
            './medal-data/modern-pentathlon/previous-modern-pentathlon.csv', 
            'Modern Pentathlon'
        )
        read_previous_results('./medal-data/rowing/previous-rowing.csv', 
                              'Rowing')
        read_previous_results('./medal-data/rugby/previous-rugby.csv', 
                              'Rugby')
        read_previous_results('./medal-data/sailing/previous-sailing.csv', 
                              'Sailing')
        read_previous_results('./medal-data/shooting/previous-shooting.csv', 
                              'Shooting')
        read_previous_results('./medal-data/softball/previous-softball.csv', 
                              'Softball')
        read_previous_results('./medal-data/swimming/previous-swimming.csv', 
                              'Swimming')
        read_previous_results(
            './medal-data/table-tennis/previous-table-tennis.csv', 
            'Table Tennis'
        )
        read_previous_results('./medal-data/taekwondo/previous-taekwondo.csv', 
                              'Taekwondo')
        read_previous_results('./medal-data/tennis/previous-tennis.csv', 
                              'Tennis')
        read_previous_results('./medal-data/triathlon/previous-triathlon.csv', 
                              'Triathlon')
        read_previous_results(
            './medal-data/volleyball/previous-volleyball.csv', 
            'Volleyball'
        )
        read_previous_results(
            './medal-data/water-polo/previous-water-polo.csv', 
            'Water Polo'
        )
        read_previous_results(
            './medal-data/weightlifting/previous-weightlifting.csv', 
            'Weightlifting'
        )
        read_previous_results('./medal-data/wrestling/previous-wrestling.csv', 
                              'Wrestling')

    rows = cxn.execute('''
        SELECT * FROM scores_by_olympic_cycle
    ''').fetchall()

    # determine which tier a country is in based on average score. if
    # average score is less than 13, it will not be available for 
    # drafting
    for row in rows:
        # handle North Korea not participating in the 2020 Olympics
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

    # create event_athletes if not in the database
    if event_athletes_exists == []:
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
        # set unplayed events which is completed in 
        # read_event_athletes() if that table doesn't exist
        events = cxn.execute('''
            SELECT Event
            FROM event_athletes
        ''').fetchall()
        for event in events:
            unplayed_events.append(event[0])
    
    # set previously played events for game play
    cursor = cxn.execute('''
        SELECT * FROM scores_by_event
    ''')
    global previously_played_events
    previously_played_events = list(map(lambda x: x[0], cursor.description))

    read_country_codes('./medal-data/country-codes.csv')

def read_medal_table(file: str, column: str):
    '''
    This function parses through a medal table and places the data into
    score_by_olympic_cycle. The value in each score represents the
    score a country earned at the olympic games

    :param file: the file storing the data
    :param column_name: the name of the column to add to table
    '''

    with open(file, newline = '') as medal_table:
        cxn.execute(f'''
            ALTER TABLE scores_by_olympic_cycle 
            ADD COLUMN {column} int DEFAULT 0
            '''
        )
        cxn.commit()
        reader = csv.reader(medal_table, quotechar = '|')
        
        # iterate through each country, tabulate the score and add it
        # to the table
        for row in reader:
            # determine score (3 points for each gold; 2 for each
            # silver; 1 for each bronze)
            score = (int(row[1]) * 3) + (int(row[2]) * 2) + int(row[3])
            country = row[0]
            
            # check if country is in table
            country_in_table = cxn.execute('''
                SELECT COUNT(*)
                FROM scores_by_olympic_cycle
                WHERE Country = ?
                ''',
                (country,)
            ).fetchone()[0]

            # add score to table for the associated country
            if country_in_table != 0:
                cxn.execute(f'''
                    UPDATE scores_by_olympic_cycle
                    SET {column} = ?
                    WHERE Country = ?
                    ''',
                    (score, country)
                )
                cxn.commit()
            else:
                cxn.execute(f'''
                    INSERT INTO scores_by_olympic_cycle (Country, {column})
                    VALUES (?, ?)
                    ''',
                    (country, score)
                )
                cxn.commit()

def read_previous_results(file: str, event_name: str):
    '''
    This function parses the previous medalists for each event and
    places the data into scores_by_event. The value placed in each
    column represents the weight that country will receive if they are
    participating in that event

    :param file: the file storing the data
    :param event_name: the event category (e.g. Swimming, Diving,
                       Athletics, etc.)
    '''

    with open(file, newline = '') as prev_data:
        reader = csv.reader(prev_data, quotechar = '|')
        for row in reader:
            # creates the column name in format <event category> - 
            # <event name> (e.g. Swimming - 100m Freestyle Men)
            column_name = event_name + ' - ' + row[0] 
            medal = row[1]
            countries = row[2:]

            # add event to table if it hasn't already been added
            cursor = cxn.execute('''
                SELECT * FROM scores_by_event
            ''')
            columns = list(map(lambda x: x[0], cursor.description))
            if column_name not in columns:
                cxn.execute(f'''
                    ALTER TABLE scores_by_event ADD COLUMN `{column_name}` int
                    DEFAULT 0
                    '''
                )
                cxn.commit()

            # determines how many points a country will add to its
            # weight in the event (3 for gold, 2 for silver, 1 for
            # bronze)
            for country in countries:
                if country == '':
                    continue
                to_add = 1
                if medal == 'Gold':
                    to_add = 3
                elif medal == 'Silver':
                    to_add = 2
                
                # check if country is already in the table
                country_in_table = cxn.execute('''
                    SELECT COUNT(*)
                    FROM scores_by_event
                    WHERE Country = ?
                    ''',
                    (country,)
                ).fetchone()[0]

                # update table with data
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
    '''
    This function parses the event participants per event and places
    them into event_athletes

    :param file: the file storing the event participants
    '''

    with open(file, newline = '') as event_list:
        reader = csv.reader(event_list, quotechar = '|')
        for event in reader:
            unplayed_events.append(event[0])
            cxn.execute('''
                INSERT INTO event_athletes
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (event[0], 
                 event[1], 
                 event[2], 
                 event[3], 
                 event[4], 
                 event[5], 
                 event[6], 
                 event[7], 
                 event[8])
            )
            cxn.commit()

def read_country_codes(file: str):
    '''
    This function parses through the country

    :param file: the file storing the country codes for the flag icons
                 for the UI
    '''
    with open(file, newline = '') as codes:
        reader = csv.reader(codes, quotechar = '|')
        for code in reader:
            country_codes[code[0]] = code[1]

def game_play():
    '''
    This function performs the majority of the game play operations
    following league selection.
    '''

    curr_event = random.choice(unplayed_events)
    unplayed_events.remove(curr_event)
    athletes = cxn.execute('''
        SELECT *
        FROM event_athletes
        WHERE Event = ?
        ''',
        (curr_event,)
    ).fetchone()

    # removes blank entries if there are only 6 participants
    if athletes[7] == '' and athletes[8] == '':
        athletes = list(athletes[1:7])
    else:
        athletes = list(athletes[1:])

    
    previously_played = True if curr_event in previously_played_events \
        else False
    event_medalists = []
    weighted_athletes = []
    num_medals = 4 if curr_event.split(' ')[0] in dual_bronze else 3

    # use a weighted random selection if previously played.
    if previously_played:
        # get the weights for each country
        for athlete in athletes:
            weight = cxn.execute(f'''
                SELECT `{curr_event}`
                FROM scores_by_event
                WHERE country = ?
                ''',
                (athlete,)
            ).fetchone()
            if weight is not None:
                # add one to offset the default being 1
                weighted_athletes.append(weight[0]+1)
            else:
                weighted_athletes.append(1)

    # determine the medalists
    for index in range(0, num_medals):
        medalist = random.choices(athletes, weights = weighted_athletes)[0] \
            if previously_played \
            else random.choice(athletes)
        event_medalists.append(medalist)

        # remove weight from weights if previously played
        if previously_played:
            medalist_index = athletes.index(medalist)
            del weighted_athletes[medalist_index]
        
        # remove medalist from participants to avoid duplicate winners
        athletes.remove(medalist)

    print(curr_event)
    print(f'gold medalist: {event_medalists[0]}' )
    print(f'silver medalist: {event_medalists[1]}' )
    if num_medals == 4:
        print(f'bronze medalists: {event_medalists[2]} and {event_medalists[3]}' )
    else:
        print(f'bronze medalist: {event_medalists[2]}' )
        
        # update medal table
        if index == 0:
            update_game_medals(medalist, 'Gold')
        elif index == 1:
            update_game_medals(medalist, 'Silver')
        else:
            update_game_medals(medalist)
    
    # update scoreboard
    update_player_scores(event_medalists)

def update_game_medals(country: str, medal: str = 'Bronze'):
    '''
    This function updates the medal table for the game throughout the
    game

    :param country: the medalist for the event
    :param medal: the color of the medal the country won
    '''

    country_idx = None
    if country in game_medal_table['Country'].unique():
        country_idx = game_medal_table.index[
            game_medal_table['Country'] == country
        ][0]
    else:
        country_idx = len(game_medal_table)
        game_medal_table.loc[country_idx] = {
            'Country': country, 
            'Gold': 0, 
            'Silver': 0, 
            'Bronze': 0, 
            'Score': 0
        }
    
    game_medal_table.at[country_idx, medal] += 1
    if medal == 'Gold':
        game_medal_table.at[country_idx, 'Score'] += 3
    elif medal == 'Silver':
        game_medal_table.at[country_idx, 'Score'] += 2
    elif medal == 'Bronze':
        game_medal_table.at[country_idx, 'Score'] += 1

def update_player_scores(medalists: list):
    '''
    This function updates the players score after an event has been
    played.

    :param medalists: a list of the medalists for the event.
    '''

    for index, player in players.iterrows():
        # aggregates a persons league into a single list
        league = [
            player[1][0], 
            player[1][1], 
            player[2], 
            player[3], 
            player[4], 
            player[5][0], 
            player[5][1], 
            player[5][2]
        ]
        
        # increase score by 3 if the gold medalist is in their league
        if medalists[0] in league:
            players.at[index, 'Score'] += 3
        # increase score by 2 if the silver medalist is in their league
        if medalists[1] in league:
            players.at[index, 'Score'] += 2
        # increase score by 1 if the bronze medalist is in their league
        if medalists[2] in league:
            players.at[index, 'Score'] += 1
        # increase score by 1 if the bronze medalist is in their league
        if (len(medalists) == 4) and (medalists[3] in league):
            players.at[index, 'Score'] += 1
    
    players.sort_values(by='Score', ascending=False, inplace=True)
    print(players)

def reset_game():
    '''
    Resets game and all necessary variables for whenever the game is 
    reset to ensure there are no issues with the game play.
    '''
    global players, game_medal_table, cxn, unplayed_events
    global previously_played_events, tiers, country_codes, error_msg
    players = pd.DataFrame(
        columns = [
            'Name', 
            'Tier A', 
            'Tier B', 
            'Tier C', 
            'Tier D', 
            'Tier E', 
            'Score'
        ]
    )
    game_medal_table = pd.DataFrame(
        columns = ['Country', 'Gold', 'Silver', 'Bronze', 'Score']
    )
    unplayed_events = []
    previously_played_events = []
    tiers = {'A': [], 'B': [], 'C': [], 'D': [], 'E': []}
    country_codes = {}
    error_msg = None
    database_creation()

def end_game():
    '''
    This function goes through required operations to end the game
    '''

    # currently just closes the connection to the database; function is
    # a placeholder just in case needed in the future.
    cxn.close()

with app.app_context():
    database_creation()


if __name__ == '__main__':
    # run on the local ip at the port number
    app.run(debug=True, port=5001)
