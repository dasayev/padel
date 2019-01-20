# -*- coding: utf-8 -*-
"""
Created on Sat Jan 19 15:44:19 2019

@author: Erik
"""
import pandas as pd
import argparse

COL_NAMES = ['submitTime', 'date', 'matchNo', 'team1', 'team2', 
             'set1Team1GamesWon', 'set1Team2GamesWon', 'set2Team1GamesWon', 
             'set2Team2GamesWon']

def splitCols(df, cols, splitChar) :
    ''' Creates two separate columns from one column. Deletes original column.  
    '''
    for col in cols:
        df[['no1' + col, 'no2' + col]] = df[col].str.split(splitChar, 
          expand=True)
        df.drop(col, axis=1, inplace=True)
    return df

def validateDuplPlayers(df):
    ''' Validate players data, making sure each player is only names once 
    '''
    error_list = []
    transp = df[['no1team1', 'no2team1', 'no1team2', 'no2team2']].transpose()
    for col in transp.columns :
        if len(transp[col].unique()) != 4 :
            error_list.append(col)
    if len(error_list) != 0 :        
        print('Duplicate player names in row ' + str(error_list))
    else : 
        return df
         
    
def main(input_filepath, output_filepath) :
    ''' Loads the data and performs basic cleaning and validating
    '''
    df = pd.read_csv(input_filepath, names=COL_NAMES, header=0, 
                     parse_dates=['date']).sort_values(['date', 'matchNo']
                     ).drop('submitTime', axis=1).reset_index(drop=True)
    df['matchId'] = df.index + 1
    df = splitCols(df, ['team1', 'team2'], ',')  
    df = validateDuplPlayers(df)
    df[['matchId', 'date', 'no1team1', 'no2team1', 'no1team2', 'no2team2',
        'set1Team1GamesWon', 'set1Team2GamesWon', 'set2Team1GamesWon', 
        'set2Team2GamesWon']].to_csv(output_filepath, index=False)
    
if __name__ == '__main__' :
    
    parser = argparse.ArgumentParser()
    parser.add_argument('input_filepath', type=str,
                    help='the filepath for padel results data')
    parser.add_argument('output_filepath', type=str,
                    help='the filepath to save the cleaned data')
    args = parser.parse_args()
   
    main(args.input_filepath, args.output_filepath)