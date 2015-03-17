#!/usr/bin/env python3
#-*- coding: utf-8 -*-

""" Merge data from raw_data/stockfish.csv and raw_data/data.pgn into base_data.csv """

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import pandas as pd
import numpy as np
import os
import scipy as sp


def main():

    # Datafile has 50000 games
    event_list = [None] * 50000
    result_list = [None] * 50000
    WhiteElo_list = [None] * 50000
    BlackElo_list = [None] * 50000

    with open("../raw_data/data.pgn") as f:
        for line in f:
            if (line.startswith('[Event')):
                gamenum = int(line.split('"')[1])
                event_list[gamenum-1] = gamenum
            if (line.startswith('[Result')):
                result_list[gamenum-1] = line.split('"')[1]
            if (line.startswith('[WhiteElo')):
                WhiteElo_list[gamenum-1] = line.split('"')[1]
            if (line.startswith('[BlackElo')):
                BlackElo_list[gamenum-1] = line.split('"')[1]

    df_data = list(zip(event_list, result_list, WhiteElo_list, BlackElo_list))
    df_game = pd.DataFrame(df_data, columns=["Event", "Result", "WhiteElo", "BlackElo"])
    df_stockfish = pd.read_csv("../raw_data/stockfish.csv")
    df = df_game.merge(df_stockfish)
    df.to_csv("../derived_data/base_data.csv", index=False)

    df_stockfish = pd.read_csv("../derived_data/stockfish_trunc_null.csv")
    df = df.update(df_stockfish, overwrite=False)
    
    zeros = pd.DataFrame(columns = ["White Wins", "Black Wins"])
    df = df.append(zeros)
    columns = df.columns.tolist()
    columns = [columns[i] for i in [2, 1, -1, 4, 5, 0, 3]]
    df = df[columns]

    for i,x in enumerate(df['Result']):
        if (x == "1/2-1/2"):
            df['White Wins'][i] = 1
            df['Black Wins'][i] = 1
        elif (x == "1-0"):
            df['White Wins'][i] = 1
        else:
            df['Black Wins'][i] = 1
        df.update(df[["White Wins", "Black Wins"]].fillna(0, inplace=False), overwrite=False)
        df = df.drop("Result", axis=1)
        for i,x in enumerate(df["MoveScores"]):
            df["MoveScores"][i] = np.array([int(j) for j in x.split(" ") if j != ''])

    df.to_csv("../derived_data/base_data_v1.csv", index=False)


    for i,x in enumerate(df["MoveScores"]):
        white_moves = x[::2]
        black_moves = x[1::2]

        # Calculate White Deltas
        if len(black_moves) < len(white_moves):
            black_moves = np.insert(black_moves,0,0)
        else:
            black_moves = np.insert(black_moves,0,0)
        white_moves = np.append(white_moves, black_moves[-1])
        df["White Avg"][i] = np.mean(np.subtract(white_moves, black_moves))
        df["White Std Dev"][i] = np.std(np.subtract(white_moves, black_moves))

        #Calculate Black Deltas
        white_moves = x[::2]
        if len(x) % 2 == 0:
            black_moves = x[1::2]
        else:
            black_moves = np.append(x[1::2], white_moves[-1])
        df["Black Avg"][i] = - np.mean(black_moves - white_moves)
        df["Black Std Dev"][i] = np.std(black_moves - white_moves)

        # Data for first model
        df.to_csv("../derived_data/data_trunc_null.csv", index=False)

if __name__ == '__main__':
    main()




