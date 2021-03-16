
from datetime import datetime
import pandas as pd

def cleanDate(obj, dtFormat=r'%Y-%m-%d'):

    year = obj.apply(lambda x: '20'+x.split('/')[2][-2:]) 
    month = obj.apply(lambda x: x.split('/')[1])
    day = obj.apply(lambda x: x.split('/')[0]) 

    obj = year + '-' + month + '-' + day
    return obj.apply(lambda x: datetime.strptime(x, dtFormat))

def loadDf(fpath, shuffle_yn=False):

    df = pd.read_csv(fpath, engine='python')

    df.loc[:, 'Date'] = cleanDate(df.loc[:, 'Date'])
    df = df.loc[(df['T_GamesPlayed_H'] >= 3) & (df['T_GamesPlayed_A'] >= 3)]
    df = df.loc[(df['GoalsFor_H'] == df['GoalsFor_H']) & (df['GoalsFor_A'] == df['GoalsFor_A'])]
    df = df.fillna(0)

    if shuffle_yn:
        df = df.sample(frac=1.)

    cols = [
        'HomeOdds','DrawOdds','AwayOdds',
        'T_GoalsFor_H','T_GoalsAg_H',
        'T_GoalsFor_A','T_GoalsAg_A',
        'T_Conversion_H','T_Conversion_A',
        'T_Accuracy_H','T_Accuracy_A',
        'T_Points_H','T_Points_A',
        'T_TablePosition_H','T_TablePosition_A',
        'L3M_Points_H','L3M_Points_A',
        'T_Variance_H','T_Variance_A',
    ]

    X_train = df.loc[:,cols]
    y_train = df.loc[:, 'GoalsFor_H'] - df.loc[:, 'GoalsFor_A']

    return X_train, y_train, df

def printResults(df, league):

    games = {'T': 0, 'H': 0, 'D': 0, 'A': 0}
    correct_games = {'T': 0, 'H': 0, 'D': 0, 'A': 0}
    returns = {'T': 0, 'H': 0, 'D': 0, 'A': 0}

    for _, row in df.iterrows():

        if row['preds'] >= 0.05:
            predResult = 'H'
            oddsValue = row['HomeOdds']

        elif row['preds'] <= -0.05:
            predResult = 'A'
            oddsValue = row['AwayOdds']

        else:
            predResult = 'D'
            oddsValue = row['DrawOdds']

        games['T'] += 1
        games[predResult] += 1

        if predResult == row['FTR']:
            correct_games['T'] += 1
            correct_games[predResult] += 1

            returns['T'] += oddsValue * 20
            returns[predResult] += oddsValue * 20

    for k in games.keys():
        print( f'{league} Accuracy {k}', "{:.4f}".format(correct_games[k] / games[k]) )

    for k in games.keys():
        print( f'{league} ROI {k}', "{:.4f}".format((returns[k] / games[k]) - 1) )
