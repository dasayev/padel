# -*- coding: utf-8 -*-
"""
Created on Sun Mar 17 11:12:35 2019

@author: Erik
"""
import pandas as pd
import elo

DATA = '../output/data.csv'
ID_1 = 1 # Lowest integer for ID column
START_RATING = 1200

def dimTeam_table(df) :
    COLS = ['player1', 'player2']
    teams = pd.DataFrame(columns=COLS)
    
    # Locate player columns in input df
    team1 = df[['no1team1', 'no2team1']]
    team2 = df[['no1team2', 'no2team2']]
    
    # Fill teams table with player pairs from both team 1 and team 2
    for df in [team1, team2] :
        df.columns = COLS
        teams = pd.concat([teams, df]).drop_duplicates(
                COLS).reset_index(drop=True)
      
    teams['teamName'] = teams['player1'] + ' & ' + teams['player2']
    # Create team ID column 
    teams.insert(0, 'teamId', range(ID_1 , len(teams) + ID_1))
    
    return teams

def dimPlayer_table(df) :
    # Create list of unique player names
    players = df.loc[:, 'no1team1':'no2team2'].stack().unique() 
    
    player_df = pd.DataFrame({'playerId' : range(ID_1, len(players) + ID_1),
                              'playerName' : players })
    return player_df


def dimDate_table(df) :
    dates = df.copy()[['date']].drop_duplicates()
    # Create team ID column 
    dates.insert(0, 'dateId', range(ID_1 , len(dates) + ID_1))
    
    return dates

def dimMatch_table(df) :
    matches = df.copy()[['matchId', 'date', 'matchNo']]

    return matches

def factResult_table(data, dimPlayer, dimTeam, dimDate, dimMatch) :
    
    results = data.copy().drop(columns=['date', 'matchNo'])
    # Create df to keep track of rankings
    ratings = dimPlayer.copy()[['playerId']]
    ratings['elo'] = START_RATING
    
    
    def common_team(row) :
        teamID = team_dict[row[0], row[1]]
        return teamID
    
    def set_win(row) :
        if row[0] > row[1] :
            return 1
        else :
            return 0
    
    def matchResult(row) :
        ''' Return result string, win, draw, loss dummies and point '''
        if (row['set1Win'] + row['set2Win']) == 2 :
            return 'Win', 1, 0, 0, 3
        elif (row['set1Win'] + row['set2Win']) == 1 :
            return 'Draw', 0, 1, 0, 1
        elif (row['set1Win'] + row['set2Win']) == 0 :
            return 'Loss', 0, 0, 1, 0

    def tiebreak(row) :
        if row[0] + row[1] == 13 :
            return 1
        else :
            return 0
        
    def players_in_team(teamId) :
        ''' Return player ID for each player in team '''
        playerName = dimTeam[dimTeam['teamId'] == teamId]['player1'].values[0]
        player1Id = dimPlayer[dimPlayer['playerName'] == playerName][
                'playerId'].values[0]
        playerName = dimTeam[dimTeam['teamId'] == teamId]['player2'].values[0]
        player2Id = dimPlayer[dimPlayer['playerName'] == playerName][
                'playerId'].values[0]
        return player1Id, player2Id
        
    def player_rating(playerId) :
        ''' Returns rating of player stored in ratings df '''
        rating = ratings[ratings['playerId'] == playerId]['elo'].values[0]
        return rating
    
    def team_rating(teamId) :
        ''' Team raning is sum of team's players rankings divided by two '''
        playerIds = players_in_team(teamId)
        teamRating = ((player_rating(playerIds[0]) + 
                       player_rating(playerIds[1])) / 2)
        return teamRating
     
        
    def post_match_rating(row) :
        
        # Read player and team rating before the game is played
        preTeamR = team_rating(row['teamId'])
        prePlayerR = player_rating(row['playerId'])
        
        if row['matchWin'] == 1 :
            postTeamR = elo.rate_1vs1(preTeamR,
                                      team_rating(row['opponentTeamId']))[0]
            postPlayerR = prePlayerR + (postTeamR - preTeamR)
        elif row['matchDraw'] == 1 :
            postTeamR = elo.rate_1vs1(preTeamR,
                                      team_rating(row['opponentTeamId']),
                                      drawn=True)[0]
            postPlayerR = prePlayerR + (postTeamR - preTeamR)
        elif row['matchLoss'] == 1 :
            postTeamR = elo.rate_1vs1(team_rating(row['opponentTeamId']),
                                      preTeamR)[1]
            postPlayerR = prePlayerR + (postTeamR - preTeamR)
        
        # Update ratings df
        ratings.loc[ratings['playerId'] == row['playerId'], 'elo'] = postPlayerR
        
        return postPlayerR
           
     
    # Create dictionary for mapping players to team
    team_players = zip(dimTeam['player1'], dimTeam['player2'])
    team_dict = dict(zip(team_players, dimTeam['teamId']))
    # Create players dictionary for mapping ID to name
    player_dict = dict(zip(dimPlayer['playerName'], dimPlayer['playerId']))

    # Create team ID columns
    results['team1'] = results[['no1team1', 'no2team1']].apply(
            common_team, axis=1).apply(pd.Series)
    results['team2'] = results[['no1team2', 'no2team2']].apply(
            common_team, axis=1).apply(pd.Series)
    
    # Replace player names with played IDs
    player_cols = ['no1team1', 'no2team1', 'no1team2', 'no2team2']
    results.loc[:, player_cols] = results.loc[:, player_cols].replace(
            player_dict)
    
    # Create one df for each team
    team1results = results[['matchId', 'no1team1', 'no2team1',
                            'set1Team1GamesWon', 'set1Team2GamesWon',
                            'set2Team1GamesWon', 'set2Team2GamesWon',
                            'team1', 'team2']]
    team2results = results[['matchId', 'no1team2', 'no2team2',
                            'set1Team2GamesWon', 'set1Team1GamesWon',
                            'set2Team2GamesWon', 'set2Team1GamesWon',
                            'team2', 'team1']]
    TEAM_RESULT_COLS =  ['matchId', 'player1', 'player2', 'set1Games',
                         'opponentSet1Games', 'set2Games', 'opponentSet2Games',
                         'teamId', 'opponentTeamId']
    team1results.columns = team2results.columns = TEAM_RESULT_COLS
    
    # Concat the team dfs
    results = pd.concat([team1results, team2results]).reset_index(drop=True)
    
    # Go from 4 to 1 player per row
    results = results.melt(id_vars=['matchId', 'set1Games',
                                    'opponentSet1Games', 'set2Games', 
                                    'opponentSet2Games', 'teamId', 
                                    'opponentTeamId'],
                            value_vars=['player1', 'player2'],
                            value_name='playerId').drop(columns=['variable'])
    
    # Add columns for set and match results
    results['set1Win'] = results[['set1Games', 'opponentSet1Games']].apply(
            set_win, axis=1)
    results['set2Win'] = results[['set2Games', 'opponentSet2Games']].apply(
            set_win, axis=1) 
    results[['matchResult', 'matchWin', 
             'matchDraw', 'matchLoss', 'points']] = pd.DataFrame(
             results.apply(matchResult, axis=1).tolist())  
    
    # Add dummies to show if sets had tiebreaker
    results['set1Tiebreak'] = results[['set1Games', 
           'opponentSet1Games']].apply(tiebreak, axis=1)
    results['set2Tiebreak'] = results[['set2Games', 
           'opponentSet2Games']].apply(tiebreak, axis=1)
    
    # Sort df by match ID to apply rating in chronological order
    results.sort_values(by='matchId', inplace=True)
    # Add pre and post match rating columns
    results['playerPostMatchRating'] = results.apply(post_match_rating, axis=1)
    
    # Add ID column
    results.insert(0, 'resultId', range(ID_1 , len(results) + ID_1))
    
    # Re-order columns
    results = results[['resultId', 'matchId', 'playerId', 'teamId',
                       'opponentTeamId', 'set1Games', 'opponentSet1Games',
                       'set1Tiebreak', 'set1Win', 'set2Games', 
                       'opponentSet2Games', 'set2Tiebreak', 'set2Win',
                       'matchResult', 'matchWin', 'matchDraw', 'matchLoss',
                       'points', 'playerPostMatchRating']]   
    
    return results


data = pd.read_csv(DATA)
dimPlayer = dimPlayer_table(data)
dimTeam = dimTeam_table(data)
dimDate = dimDate_table(data)
dimMatch = dimMatch_table(data)
factResult = factResult_table(data, dimPlayer, dimTeam, dimDate, dimMatch)

dimPlayer.to_csv('../output/dimPlayer.csv', index=False)
dimTeam.to_csv('../output/dimTeam.csv', index=False)
dimMatch.to_csv('../output/dimMatch.csv', index=False)
dimDate.to_csv('../output/dimDate.csv', index=False)
factResult.to_csv('../output/factResult.csv', index=False)