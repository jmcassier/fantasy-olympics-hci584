# Fantasy Olympics - Developer's Documenation - HCI 584X

## Project Overview

Fantasy Olympics is a game of chance created to simulate the selection of a fantasy sports league for the 2020 Summer Olympic Games and uses historical data to determine a potential outcome for each event (note: this outcome is not necessarily what happened in the actual 2020 Tokyo games). This historical data was pulled from the 2008 - 2016 Summer Olympics and the teams are categorized into 5 tiers - A, B, C, D, E - with A-tier being teams with historically highest medal scores and E-tier being teams with historically lowest medal scores from the Summer Olympics. A countries medal score is calculated as follows: 3 points for each gold medal, 2 points for each silver medal, 1 point for each bronze medal. To ensure that each player selects a range of teams (and not just powerhouse teams that historically sweep the medal tables), the teams. In order to play, a player selects a league of 8 countries that will earn them points based on the medals that team earns in game. From there, the game is kicked off and the in game simulation begins for each event. Before each event is played, each player has the opportunity to bet on who they think will win the event as well. The rules of the game can be found in the User's Guide.

## How To Run & Packages
Refer to "Set Up, How To Run & Packages" in the User's Guide. No additional install/deployment/admin issues to add here.

## User Activity Flow

&nbsp; &nbsp; &nbsp; &nbsp;The first task is to select the number of people playing the game and entering their names.

&nbsp; &nbsp; &nbsp; &nbsp;The first task will be the user drafting the 8 countries they want to form their league. John wants to go ahead and do this to participate in the single-player game. He does this by clicking the play game to start the game. He then inputs his name and selects the teams he wants in his league based on the rules defined above in the project description. Once he has finalized his selections, he clicks the submit button. Once the button is clicked and his response successfully submitted, the game is launched.

&nbsp; &nbsp; &nbsp; &nbsp;Now, let's say John and Sarah are playing this as a multiplayer game. They similarly click the play game to start the game. John first starts by entering his name, followed by Sarah. They each proceed to select their leagues based on the rules defined above in the project description. Once they have finalized their selections, they click the submit button and the game is launched.

### Task 2
&nbsp; &nbsp; &nbsp; &nbsp;The second user activity is viewing the scoreboard and game progression. This task is launched after the form is submitted. As each event is played, he is to view the scoreboard and see how he places amongst other players (if multiplayer game). As the game progresses, he realizes that his bracket isn’t as strong as his competitors and is now heavily relying on two of his D-tier teams to get him some extra points. He also is curious as to how these other players are doing so much better. In looking at the other players' bracket, he realizes he selected a B-tier team that isn’t performing as well as they usually do and it’s causing him to miss out on a lot of points.

&nbsp; &nbsp; &nbsp; &nbsp;Details/Ideas for further consideration:
* If possible, can there be a toggle for a more detailed table so that the default view is just a player’s name and score and a more detailed table also has each player’s league ? Or does all information show by default ?

## Technical Flow
&nbsp; &nbsp; &nbsp; &nbsp;From a technical perspective, I want to create the main GUI using Flask, with the landing page either rendering a play game button with rules of the game. During start up as well, the app would use the data either parsed or already stored in its backend (depending on if the tables exist) to determine which Olympic teams are in each tier to have that ready to go during a player’s selection process, the weights a team has for each event, and the participants competing in each event. This data is stored as follows:

1) 3 tables in a SQL database for easy access.
   * scores_by_olympic cycle stores each country's score at each individual Summer Olympics from 2008 to 2016.
      * Scores are calculated as follows: 3 points for each gold medal, 2 points for each silver medal, 1 point for each bronze medal. 
      * This data comes from parsing the csv medal tables from the Olympic Games. Each row is formatted as follows: <Country_Name>, <Gold_Medal_Count>, <Silver_Medal_Count>, <Bronze_Medal_Count>
   * scores_by_event stores each country's weights for each event based on how they previously performed in the events in Summer Olympic Games from 2008 to 2016.
      * Scores are calculated as follows: 3 points for each gold medal, 2 points for each silver medal, 1 point for each bronze medal.
      * This data comes from parsing the csv event tables from the Olympic Games. Each row is formatted as follows: <Event_Name>, <Medal_Color>, <Country_Name>, <Country_Name>, ..., <Country_Name>. So, for example, if a row looks like 
      
            Singles Men,Gold,Spain,Great Britain,Great Britain
         It means that the for the Men's Singles, the Gold Medal was won by Spain once and Great Britain twice from 2008 to 2016.
   * event_athletes stores the participants for the event in the game.
      * There are 8 participants per event that were determined by taking the actual top 8 finishers of each event at the 2020 Tokyo Olympics for simplicity. Events with less than 8 participants had less than 8 participants competing (note: this was commonly seen in Team events and had 6 participants or in event finals with less than 8 participants).
      * This data comes from the csv event list. Each row is formatted as follows: <Event_Name>, <Country_Name>, <Country_Name>, <Country_Name>, ..., <Country_Name>
2) A dictionary that stores which countries are in which tiers
3) A list that stores events that will be played in the game
4) A list that stores which events have been played at prior Olympics
   * This informs whether or not a weighted random selection will be used for determining medals.

&nbsp; &nbsp; &nbsp; &nbsp;Upon clicking the play button, the drafting page would render on the screen. Here, the players would enter their name and select the teams for their league using the form and the application would use this as the input for the system. Ideally, team selection would make use of dropdowns or buttons to avoid potential issues I foresee with error handling (e.g. misspellings). Because of this, I would have to render the data about each team on the screen for the user to see. Once the players go through the drafting process, the application would take that data and add it to a pandas database storing the players name, league and scores. Once all of that work on the backend is complete, the main game play would be launched.

&nbsp; &nbsp; &nbsp; &nbsp;Once the drafting process has been completed and the main game play has been launched, the scoreboard page would render the data from each person’s league in order of their current ranking in the game and the players would be able to launch the medal tabulation of the first event. Before each event is run, the players will be allowed to bet on the winner of the event. When the medalists have been determined for an event, they will appear on the screen and the scoreboard will be updated to reflect the outcome. Once the players are ready for the game to continue, they will click the continue button for the next event to occur. This process will repeat itself until all events have been completed and the game has concluded. For the scoreboard, I would also want to have a switch view function on the backend that determines which information to show since I want to do a general view and a detailed view for each player’s league (though this is still subject to change). 

## Sources for Data

* 2008 Beijing Olympics: https://olympics.com/en/olympic-games/beijing-2008/

* 2012 London Olympics: https://olympics.com/en/olympic-games/london-2012/

* 2016 Rio Olympics: https://olympics.com/en/olympic-games/rio-2016/
   * Kuwaiti athletes competed as "Independent Olympic Athletes" in 2016 as a result of Kuwait's suspension. For simplicity, they are referred to as Kuwait in this project.

* 2020 Tokyo Olympics: https://olympics.com/en/olympic-games/tokyo-2020/
   * Russian athletes competed as "ROC" in 2020 as a result of Russia's suspension. For simplicity, they are referred to as Russia in this project.
