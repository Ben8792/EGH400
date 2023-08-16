from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd

def get_osws(input_df, x_set, y_set):

    x_array = input_df[x_set].fillna(0).to_numpy()
    y_array = input_df[y_set].to_numpy()

    reg = LinearRegression().fit(x_array, y_array)

    osws = reg.coef_

    return osws


def get_mean_stats(input_df, x_set, play):

    input_df = input_df.loc[input_df.play == play]

    x_df = input_df[x_set].copy()

    mean_set = x_df.mean(axis=0)

    return mean_set

# def determine_play_signs():
