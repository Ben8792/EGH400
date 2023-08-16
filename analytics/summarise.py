import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from regression import get_osws, get_mean_stats

input_loc = "../data/inputs/"
output_loc = "../data/outputs/"


def get_zones(data):
    data["retainedPosession"] = 0
    retain_list = ["Retain NEG", "Retain Static", "Retain Gain 1", "Retain Gain +1",
        "Retain Score", "Retain HR neg", "Retain HR Static", "Retain HR Gain 1",
        "Retain HR Gain +1"]
    for col in retain_list:
        data["retainedPosession"] = data["retainedPosession"] + data[col]
    
    this_summary = data.groupby(["teamAttack", "teamDefense", "game_id"])[""].sum().reset_index()
    



def summarise(input_df: pd.DataFrame) -> list[pd.DataFrame, pd.DataFrame]:
    """
    Summarises a defined list of statistics per game

    :param input_df: Input df, play by play
    :returns input_df: input df with game ids added
    :returns overall: Summarised stats, per game
    """

    # Change to nicer column names
    input_df = (input_df
        .reset_index()
        .rename(columns={
            "Attack Team": "teamAttack",
            "Defense team": "teamDefense",
            "Date": "date",
            "index": "row_id"
        })
    )
    
    # Ask pandas to interpret as datetime instead of string
    input_df.date = pd.to_datetime(input_df.date, dayfirst=False)

    # Get list of each game (reduced from list of each play)
    game_ids = (
        input_df[["teamAttack", "teamDefense", "date"]]
        .loc[input_df.teamAttack > input_df.teamDefense]
        .drop_duplicates()
        .sort_values(by=["date", "teamAttack", "teamDefense"], ignore_index=True)
        .reset_index(drop=False)
        .rename(columns={"index": "game_id"})
    )

    # Allow game_id to seam teamA vs teamB AND teamB vs teamA
    game_ids2 = game_ids.copy()
    game_ids2.teamAttack = game_ids.teamDefense
    game_ids2.teamDefense = game_ids.teamAttack

    game_ids = (
        pd.concat([game_ids, game_ids2], ignore_index=True)
        .sort_values(by="game_id")
    )

    # Don't need this anymore
    del game_ids2

    # Merge game ids
    input_df = pd.merge(input_df, game_ids).sort_values(by=["game_id", "row_id"])

    # Initilase summary df
    overall = game_ids

    # Sum total retain of posession
    input_df["retainedPosession"] = 0
    retain_list = ["Retain NEG", "Retain Static", "Retain Gain 1", "Retain Gain +1",
        "Retain Score", "Retain HR neg", "Retain HR Static", "Retain HR Gain 1",
        "Retain HR Gain +1"]
    
    for col in retain_list:
        input_df["retainedPosession"] = input_df["retainedPosession"] + input_df[col]
    
    # Sum total loss of posession
    input_df["lostPosession"] = 0
    lose_list = ["Lose gain neg", "Lose Static", "Lose Gain 1", "Lose Gain +1",
        "Lose HR neg", "Lose HR Static", "Lose HR Gain 1", "Lose HR Gain +1"]
    for col in lose_list:
        input_df["lostPosession"] = input_df["lostPosession"] + input_df[col]

    # Define list of stats to sum
    stats_to_sum = ["Pass", "Ruck", "Clear", "retainedPosession", "lostPosession", "Score"]

    # Generate sums
    for stat in stats_to_sum:
        this_summary = input_df.groupby(["teamAttack", "teamDefense", "game_id"])[stat].sum().reset_index()
        overall = pd.merge(overall, this_summary)
    


    return input_df, overall


def add_exp_decay(input_data):
    input_data = input_data.reset_index(drop=True)
   
    scoring_plays = input_data.loc[input_data.Score > 0]

    games = input_data.game_id.drop_duplicates().to_list()
    
    
    input_data["outcome_score"] = 0
    input_data["related_score"] = ""
    input_data["team_scored"] = ""


    for game in games:
       
        this_game = input_data.loc[input_data.game_id == game]
       
        game_sum = input_data.Score.sum()
       
        if game_sum == 0:
            input_data[this_game.index,"related_score"] = "No_score"
        else:
            scoring_plays = this_game.loc[this_game.Score > 0]

            for play in scoring_plays.index:
                if play == scoring_plays.index.min():
                    input_data.loc[(input_data.game_id == game) & (input_data.index <= play),"related_score"] = play
                else:
                    input_data.loc[
                        (input_data.game_id == game) &
                        (input_data.index <= play) &
                        (input_data.index > prev_play), "related_score"
                    ] = play

                prev_play = play

    scoring_list = input_data.related_score.drop_duplicates().to_list()

    
    for play in scoring_list:
        if play == "":
            continue
        
        events = input_data.loc[input_data.related_score == play]

        length = len(events)
        
        A_coef = input_data.loc[play, "Score"]
        team_scored = input_data.loc[play, "teamAttack"]
        
        B_coef = 0.5
        

        add_df = pd.DataFrame({"position":[*range(length)]})
        add_df["outcome_score"] = A_coef*np.exp((-1)*B_coef*add_df.position)

        add_df = add_df.iloc[::-1]

        input_data.loc[input_data.related_score == play, "outcome_score"] = add_df.outcome_score.to_list()
        input_data.loc[input_data.related_score == play, "team_scored"] = team_scored
    
    input_data.loc[
        input_data.teamDefense == input_data.team_scored,
        "outcome_score"
    ] = -1 * (input_data.
        loc[
            input_data.teamDefense == input_data.team_scored,
            "outcome_score"
        ]
    )
            
    
    return input_data


def attach_play_type(input_df):

    input_df["passRuckRatio"] = input_df.Pass / input_df.Ruck
    input_df["nextOrigin"] = input_df.Origin.shift(1)
    input_df["play"] = ""
    
    
    ruleset = pd.read_csv("../data/inputs/ruleset.csv")

    play_list = ruleset.play.drop_duplicates().to_list()

    for i in ruleset.index:
        this_play = ruleset.loc[i,"play"]
        filter_string = ruleset.loc[i, "filter"]
        execute_line = "df.loc[" + filter_string + ", \"play\"] = this_play"
        
        execute_line = execute_line.replace("df", "input_df")

        exec(execute_line)

    return input_df


# def get_osws(input_df):



    # return osw_df


def main():

    # Read input
    input_df = pd.read_csv(input_loc + "Rugbycology_dataset_v2.csv")

    # Create summary
    output_df, summary = summarise(input_df)

    # Attach play type
    output_df = add_exp_decay(output_df)
    output_df = attach_play_type(output_df)

    x_set = ["Start", "Pass", "Ruck", "Clear", "Contest", "Score", "Retain NEG",
        "Retain Static", "Retain Gain 1", "Retain Gain +1", "Retain Score",
        "Retain HR neg", "Retain HR Static", "Retain HR Gain 1", "Retain HR Gain +1",
        "Lose gain neg", "Lose Static", "Lose Gain 1", "Lose Gain +1", "Lose HR neg",
        "Lose HR Static", "Lose HR Gain 1", "Lose HR Gain +1"
    ]
    y_set = "outcome_score"

    osw_set = get_osws(output_df, x_set, y_set).tolist()
    print(osw_set)

    mean_set = get_mean_stats(output_df, x_set, "Pick and Go").to_list()
    print(mean_set)

    cp_df = pd.DataFrame({"weight": osw_set, "value": mean_set})

    cp_df["weighted_value"] = cp_df.weight * cp_df.value

    outcome_score = cp_df.weighted_value.sum()

    print(outcome_score)

    # Export
    summary.to_csv(output_loc + "basic_summary.csv", index=False)
    output_df.to_csv(output_loc + "attached_game_id.csv", index=False)


main()