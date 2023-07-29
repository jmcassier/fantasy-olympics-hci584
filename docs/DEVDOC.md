# Fantasy Olympics - Developer's Documenation - HCI 584X

## Project Overview

Fantasy Olympics is a game of chance created to simulate the selection of a fantasy sports league for the 2020 Summer Olympic Games and uses historical data to determine a potential outcome for each event (note: this outcome is not necessarily what happened in the actual 2020 Tokyo games). This historical data was pulled from the 2008 - 2016 Summer Olympics and the teams are categorized into 5 tiers - A, B, C, D, E - with A-tier being teams with historically highest medal scores and E-tier being teams with historically lowest medal scores from the Summer Olympics. A countries medal score is calculated as follows: 3 points for each gold medal, 2 points for each silver medal, 1 point for each bronze medal. To ensure that each player selects a range of teams (and not just powerhouse teams that historically sweep the medal tables), the teams. In order to play, a player selects a league of 8 countries that will earn them points based on the medals that team earns in game. From there, the game is kicked off and the in game simulation begins for each event. Before each event is played, each player has the opportunity to bet on who they think will win the event as well. The rules of the game can be found in the User's Guide.

## Install / Deployment / Admin Issues
Refer to "Set Up, How To Run & Packages" in the User's Guide (README.md). No additional install/deployment/admin issues to add here.

## The User Flow
See the step-by-step process and gifs defined in the "User Walkthrough" section of the User's Guide (README.md).

## Code Walkthrough & Technical Flow
&nbsp; &nbsp; &nbsp; &nbsp;From a technical perspective, the main GUI was created using Flask. During start up, the app either uses the data stored in the olympic_stats.db. If this SQL database doesn't exist or any of the 3 required tables (as defined below) are missing from it, the data in the medal-data folder is parsed and added to the olympic_stats.db. The data in the database is used to determine which Olympic teams are in each tier to have that ready to go during a player’s selection process, the weights a team has for each event, and the participants competing in each event. The table and data olympic_stats.db is described as follows:

1. scores_by_olympic_cycle stores each country's score at each individual Summer Olympics from 2008 to 2016.
    * Scores are calculated as follows: 3 points for each gold medal, 2 points for each silver medal, 1 point for each bronze medal.
    * This data comes from parsing the csv medal tables from the Olympic Games. Each row is formatted as follows: <Country_Name>, <Gold_Medal_Count>, <Silver_Medal_Count>, <Bronze_Medal_Count>
    * The columns in the SQL table are <Country\>, <Beijing\>, <London\> and <Rio\>, with the Country column storing the country name and the <Beijing\>, <London\> and <Rio\> storing the scores won at each Olympic Games, respectively.
###
2. scores_by_event stores each country's weights for each event based on how they previously performed in the events in Summer Olympic Games from 2008 to 2016.
    * Scores are calculated as follows: 3 points for each gold medal, 2 points for each silver medal, 1 point for each bronze medal.
    * This data comes from parsing the csv event tables from the Olympic Games. Each row is formatted as follows: <Event_Name>, <Medal_Color>, <Country_Name>, <Country_Name>, ..., <Country_Name>. So, for example, if a row looks like 
      
          Singles Men,Gold,Spain,Great Britain,Great Britain

      It means that the for the Men's Singles, the Gold Medal was won by Spain once and Great Britain twice from 2008 to 2016.
    * The columns in the SQL table are <Country\> and 1 further column for each event. <Country\> stores the country name and each event stores the score for the event.
###
3. event_athletes stores the participants for the event in the game.
    * There are 8 participants per event that were determined by taking the actual top 8 finishers of each event at the 2020 Tokyo Olympics for simplicity. Events with less than 8 participants had less than 8 participants competing (note: this was commonly seen in Team events and had 6 participants or in event finals with less than 8 participants).
    * This data comes from the csv event list. Each row is formatted as follows: <Event_Name>, <Country_Name>, <Country_Name>, <Country_Name>, ... , <Country_Name>
    * The columns in the SQL table are <Event\>, <Athlete1\>, <Athlete2\>, <Athlete3\>, ... , <Athlete7\>, <Athelete8\>. <Event\> stores the name of the event and the competitors for the event are held <AthleteX\> columns (one per column).
###

Once the database is completed in its entirety, the following data structures are initialized during database creation:
1. tiers: A dictionary that stores which countries are in which tiers. The tiers are determined by the data in scores_by_olympic_cycle
###
2. unplayed_events: A list that stores events that haven't been played in the game yet. Upon initialization, this will include all events that will be played.
###
3. previously_played_events: A list that stores which events have been played at prior Olympics
   * This informs whether or not a weighted random selection will be used for determining medals.
###
4. country_codes: A dictionary that stores the country codes for the flags that will be rendered on the frontend.
###

Other data structures that are initialized on start to be empty or hold static data are the following:
1. players: A dataframe that stores the information related to each player, including their name, league, score, rank, which team they are betting on, how much they are betting, and their net bet score. Initalized to be empty, but updates as the players' names are confirmed and teams are selected in the frontend. It is further updated in the main game play as scores are updated and bets are made.
###
2. dual_bronze: A list of events that always award 2 bronze medals due to no bronze medal match. This data remains static.
###
3. game_medal_table: A dataframe that will store the scores of each country in the game. Initialized as an empty dataframe with the columns Country and Score
###
4. draft_order: A list of the players name stored in the order in which they can choose teams during the draft. Initialized to be empty and fills with all the player names once they are confirmed and validated.
###
5. current_draft_pick: An integer value that determines which person is up to select a team during the draft process from the draft_order list. Initalized to 0 and increments during the draft process.
###
6. draft_round: A list that contains the draft round at index 0 and which tier teams are being selected from at index 1. Initialized to [1, 'A'].
###
7. session: A dictionary that mocks establishing session data to send messages during a POST-redirect-GET.
###
8. master_draft: A list of all teams that were drafted by at least one player. This is used to help filter through the game_medal_table to retrieve only the relevant data for the front end during the main game play.
###
Once all of the set up has been completed on start up, the home page will be rendered on screen. At this point, the user will click the number of people playing and the number of name fields will be populated, which is entirely handled in the home.html file. Once the names are entered, they will be able to click the "Confirm Players" button. However, if any of the names are blank or do not conform to the standards defined in the game rules (see: "Game Rules" in User's Guide), there is a validation method in the home.html file as well. Once a list of valid players is submitted, the values in each field are passed to the backend, where each player is added to the players dataframe with an empty league, score of 0, rank of 0, bet amount of 0, net bet score of 0 and a bet on value of none. The names are also all added to the draft_order list where it is then shuffled to create the first draft order. Since there are a finite number of teams in each tier, all or a subset of the tiers will be filled with duplicate values to ensure everyone has the ability to get 8 teams following the rules of the game. If there are 3 players, each A-tier team is available 2 times; if there are 4 players, each B-tier team is availabe 3 times; if there are 5 players, each A-tier team is available 3 times, and each B-tier, C-tier and E-tier team are available 2 times; if there are 6 players, each A-tier team is available 4 times, and each B-tier, C-tier, D-tier and E-tier team are available 2 times. The number of times each team was made available was determined by analyzing the worst case scenario for the last person choosing a team from that tier.

Upon clicking the Confirm Players button with valid player names, the drafting page would render on the screen. Here, the players select teams for their league by clicking on the "select" button under their team of choice on the screen. To avoid issues related to reloading the screen, the draft_page code makes use of a POST-redirect-GET strategy. Each player chooses their team one-by-one following the rules of the draft. As mention previously, the first round is randomly created using the random.shuffle; in each succeeding round, the order is flipped (i.e. rounds 1, 3, 5, 7 have the same order; rounds 2, 4, 6, 8 have the same order). When a team is selected by a user on the UI, the selection is passed to the backend and an attempt to add it to the player's league is made. If that attempt is successful, the team is added to the master_draft list to keep track of which teams have been selected at least once, the team is removed from the available teams list and the draft_round and draft_order is updated if necessary. During the draft process, each player's league is also currently rendered on the left sidebar.

Once the drafting process has been completed and the main game play has been launched, the scoreboard page would render in the left sidebar using the data from players dataframe. Before each event is run, the players will be allowed to bet on the winner of the event. First, the form is validated to ensure a team is selected and a valid amount was entered. The team selection is largely handled on the frontend, however the amount validation is largely handled through an AJAX call that is sent to the set_bet function on the backend where it is checked that this amount meets the requirements set by the rules. Any validation errors are passed through as session data and passed through to the frontend to alert the user. Once the form is fully validated, the bet is added to and stored in the players database using an AJAX call on the frontend that is sent to the backend in the set_bet function. Once all players have placed a bet, the continue button is enabled and the player can run the event simulation. Once run, a POST-redirect-GET request is run, during which the play_game function is called. In this function, a weighted selection (for events previously played at the Olympic Games) or a random selection (for events new to this Olympic Games) to determine the medalists. The participants are retrieved from the event_athletes table and, if a previously weighted event, the weights are retrieved from the scores_by_event table. Once the medalists have been determined, each player's score is updated and game_medal_table is updated. The event medalists are then sent to the frontend, along with the next event to be displayed on the screen in a podium visualization. This process repeats itself until all events have been completed and the game has concluded.

## Known Issues
Refer to "Known Issues" in the User's Guide (README.md) for the minor issues described there. 

Beyond those issues, a UX Issue I suspect exists and wanted to eliminate (but didn't have time to) was the constant clicking of the continue button in the main game play section. I was trying to research ways to automate that process a bit more such that when every player had submitted their bet, it would automatically play the event. For a single player, this would have been easy to figure out, but the multiplayer aspect caused some issues. Unfortunately, due to time constraints, this was unable to be remediated and would have been a major win for the UX if it could have been accomplished.

Another issue is the overall structure of the code. Due to time limitations near the end of this project, particularly with my work schedule and going to a major conference, I just ran out of time to make my code more modular using packages. This would have really helped clean up my code and make it more readable for any person trying to use it.

No other minor or major issues of note that are known or suspected.

Inefficiencies: Due to my lack of experience with creating frontends using Python and Flask, I didn't quite figure out how to create the frontend using a more refined framework, such as React, which would have made it so that I wouldn't have had to do as much script injection in the HMTL file. That would be a major win to get implemented for the future of this project.

## Future Work
Future work includes the following 2 features that were on my wish-list of items if I had time that I didn't quite get to:

1. Ties: A very real occurence at the Olympic Games are ties for medals. This is something this game does not accomodate for and takes the very simiplistic approach of 1 athlete per medal (except for those events where multiple bronze events are awards because they don't do bronze medal matches). This feature would add more complexity to the game and more depth to the experience.
###
2. Disqualifications: Sometimes medalists are disqualified after winning a medal for breaking rules (e.g. using banned substances, etc.) and the medal table and an athlete just off the podium may be elevated to the podium. Similar to ties, this is something that this game does not accomodate for and would add more complexity to the game and more depth to the experience.

## Ongoing Deployment/Development
I do not intend to continue development on this project following the end of this course.

## Sources for Data

* 2008 Beijing Olympics: https://olympics.com/en/olympic-games/beijing-2008/
###
* 2012 London Olympics: https://olympics.com/en/olympic-games/london-2012/
###
* 2016 Rio Olympics: https://olympics.com/en/olympic-games/rio-2016/
   * Kuwaiti athletes competed as "Independent Olympic Athletes" in 2016 as a result of Kuwait's suspension. For simplicity, they are referred to as Kuwait in this project.
###
* 2020 Tokyo Olympics: https://olympics.com/en/olympic-games/tokyo-2020/
   * Russian athletes competed as "ROC" in 2020 as a result of Russia's suspension. For simplicity, they are referred to as Russia in this project.
