import pandas as pd
import numpy as np
import elo
import argparse


def results_columns(df) :
    ''' Add three dummy columns columns for the match outcome '''
    
    def matchResult(row) :
        ''' Return result dummies'''
        if ((row['set1Team1GamesWon'] > row['set1Team2GamesWon']) &
            (row['set2Team1GamesWon'] > row['set2Team2GamesWon'])):
            return 1, 0, 0
        elif ((row['set1Team1GamesWon'] < row['set1Team2GamesWon']) &
              (row['set2Team1GamesWon'] < row['set2Team2GamesWon'])) :
            return 0, 0, 1
        else :
            return 0, 1, 0
    
    df[['team1WinMatch', 'drawMatch', 'team2WinMatch']] = pd.DataFrame(
         df.apply(matchResult, axis=1).tolist()) 
    
    return df
    

def rating_columns(data) :
    
    results = data.copy()
    
    # All new players enter at this rating
    START_RATING = 1200
    
    # Create list of unique player names
    NAME_COLS = ['no1team1', 'no2team1', 'no1team2', 'no2team2']
    players = results.loc[:, NAME_COLS].stack().unique()
    
    # Create df to keep track of rating
    rating = pd.DataFrame(players, columns=['playerName'])
    rating['elo'] = START_RATING
    
      
    def player_rating(playerName) :
        ''' Returns rating of player stored in ratings df '''
        playerRating = rating[rating['playerName'] == playerName]['elo'].values[0]
        return playerRating
    
    
    def team_rating(player1Name, player2Name) :
        ''' Team rating is sum of team's players rankings divided by two '''
        teamRating = (player_rating(player1Name) + 
                      player_rating(player2Name)) / 2
        return teamRating
    
        
    def post_match_rating(row) :
        ''' Calculate ratings for each player based on the match result '''
        
        # Player names and pre match ratings
        p1 = row['no1team1']
        p2 = row['no2team1']
        p3 = row['no1team2']
        p4 = row['no2team2']
        
        p1PreRating = player_rating(p1)
        p2PreRating = player_rating(p2)
        p3PreRating = player_rating(p3)
        p4PreRating = player_rating(p4)
        
        # Team ratings is used for calculating player ratings only
        t1PreRating = team_rating(p1, p2)
        t2PreRating = team_rating(p3, p4)
        t1PostRating = np.NaN
        t2PostRating = np.NaN
        
        # Elo rater takes winning team rating as first argument    
        if row['team1WinMatch'] == 1 :
            t1PostRating, t2PostRating = elo.rate_1vs1(
                    t1PreRating, t2PreRating)     
        elif row['drawMatch'] == 1 :
            t1PostRating, t2PostRating = elo.rate_1vs1(
                    t1PreRating, t2PreRating, drawn=True) 
        elif row['team2WinMatch'] == 1 :
             t2PostRating, t1PostRating = elo.rate_1vs1(
                    t2PreRating, t1PreRating) 
        
        # Calculate new player rating
        p1PostRating = p1PreRating + (t1PostRating - t1PreRating)
        p2PostRating = p2PreRating + (t1PostRating - t1PreRating)
        p3PostRating = p3PreRating + (t2PostRating - t2PreRating)
        p4PostRating = p4PreRating + (t2PostRating - t2PreRating)
    
        # Update ratings df
        for name, newRating in [(p1, p1PostRating), 
                                (p2, p2PostRating),
                                (p3, p3PostRating), 
                                (p4, p4PostRating)] :
            rating.loc[rating['playerName'] == name, 'elo'] = newRating
            
        return p1PostRating, p2PostRating, p3PostRating, p4PostRating
        
    # Add player post match rating columns to df
    results[['no1team1PostRating', 'no2team1PostRating', 'no1team2PostRating',
            'no2team2PostRating']] = pd.DataFrame(
             results.apply(post_match_rating, axis=1).tolist())

    return results

def main(input_filepath, output_filepath) :
    ''' Adds result and rating columns to df and writes to csv file
    '''
    data = pd.read_csv(input_filepath)
    df = results_columns(data)
    df = rating_columns(df)
    df.to_csv(output_filepath, index=False)

if __name__ == '__main__' :
    
    parser = argparse.ArgumentParser()
    parser.add_argument('input_filepath', type=str,
                    help='the filepath for clean data')
    parser.add_argument('output_filepath', type=str,
                    help='the filepath to save the updated data')
    args = parser.parse_args()
   
    main(args.input_filepath, args.output_filepath)

