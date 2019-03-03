import pandas as pd
import argparse

ID_1 = 1  # Lowest player ID
    
def create_player_table(df) :
    ''' Create a DataFrame containg all player names and a generated player ID
    '''
    players = df.loc[:, 'no1team1':'no2team2'].stack().unique()
    
    player_table = pd.DataFrame({'playerId' : range(ID_1, len(players) + ID_1), 
                                 'name' : players })[['playerId', 'name']]
    
    return player_table


def result(row) :
    winner = ''
    if ((row['set1Team1GamesWon'] > row['set1Team2GamesWon']) & 
        (row['set2Team1GamesWon'] > row['set2Team2GamesWon'])) :
        winner = 'team1'
    elif ((row['set1Team1GamesWon'] < row['set1Team2GamesWon']) & 
          (row['set2Team1GamesWon'] < row['set2Team2GamesWon'])) :
        winner = 'team2'
    else :
        winner = 'draw'
        
    return winner 
      
    
def main(input_filepath, output_filepath) :
    ''' Creates Player table from input file
    '''
    players = create_player_table(pd.read_csv(input_filepath))
    players.to_csv(output_filepath, index=False)
    
    
if __name__ == '__main__' :
    
    parser = argparse.ArgumentParser()
    parser.add_argument('input_filepath', type=str,
                    help='the filepath for padel results data')
    parser.add_argument('output_filepath', type=str,
                    help='the filepath to save Player table')
    args = parser.parse_args()
   
    main(args.input_filepath, args.output_filepath)
    
    
    