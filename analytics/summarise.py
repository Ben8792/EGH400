import pandas as pd
import numpy as np
# from sklearn.linear_model import LinearRegression
from regression import get_osws, get_mean_stats
from time_stamps import add_time_stamps

input_loc = "../data/inputs/"
output_loc = "../data/outputs/"

input_file = "Rugbycology_dataset_v2.csv"


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
        final_time = max(events.time)
        # print("new event!\n",events)

        length = len(events)
        
        A_coef = input_data.loc[play, "Score"]
        team_scored = input_data.loc[play, "teamAttack"]
        
        B_coef = 0.3
        

        # add_df = pd.DataFrame({"position":[*range(length)]})
        add_df = pd.DataFrame({"position": events.time})
        add_df.position = final_time - add_df.position
        add_df["outcome_score"] = A_coef*np.exp((-1)*B_coef*add_df.position)

        # add_df = add_df.iloc[::-1]

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
    input_df["nextOrigin"] = input_df.Origin.shift(-1)
    input_df["play"] = ""
    
    
    ruleset = pd.read_csv("../data/inputs/ruleset.csv")

    play_list = ruleset.play.drop_duplicates().to_list()

    for i in ruleset.index:
        this_play = ruleset.loc[i,"play"]
        filter_string = ruleset.loc[i, "filter"] + " & (df.play == \"\")"
        execute_line = "df.loc[" + filter_string + ", \"play\"] = this_play"
        
        execute_line = execute_line.replace("df", "input_df")

        exec(execute_line)

    return input_df


def bin_time(input_df): 

    input_df["time_bin"] = 5 * (input_df.time / 5).round()

    return input_df


def pre_process(filename, x_set, y_set):
    print("pre-processing...")
    # Read input
    # print(input_loc + input_file)
    input_df = pd.read_csv(input_loc + input_file)

    # Create summary
    print("creating summary...")
    output_df, summary = summarise(input_df)

    # Attach play type, exp decay, time and time bins
    print("attaching time...")
    output_df = add_time_stamps(output_df)
    print(len(output_df.columns))
    print("adding exp decay...")
    output_df = add_exp_decay(output_df)
    print(len(output_df.columns))
    print("attaching play type...")
    output_df = attach_play_type(output_df)
    print(len(output_df.columns))
    
    
    print("binning time...")
    output_df = bin_time(output_df)
    print(len(output_df.columns))
    print("getting osws...")
    osw_set = get_osws(output_df, x_set, y_set).tolist()

    return output_df, summary, osw_set

def get_top_three(data_df, x_set, possible_plays, osw_set, filters=None): # Continue this later

    scores = list()

    for play in possible_plays:
        mean_set = get_mean_stats(data_df, x_set, play)

        cp_df = pd.DataFrame({"weight": osw_set, "value": mean_set})

        cp_df["weighted_value"] = cp_df.weight * cp_df.value

        scores.append(cp_df.weighted_value.sum())
    
    optimal_plays = pd.DataFrame({
        "play": possible_plays,
        "score": scores,
    }).sort_values(by=[scores], ascending=[True])

    return optimal_plays


def rank_plays_with_filter(df, filter):

    df = df.query(filter)

    # print(len(df))

    ranked_plays = (df
        .groupby("play")
        .outcome_score
        .mean()
        .reset_index()
        .transpose()
        .reset_index(drop=True)
    )

    n_values = (df
        .groupby("play")
        .outcome_score
        .count()
        .reset_index()
        .transpose()
        .reset_index(drop=True)
    )

    # ranked_plays = ranked_plays.drop(columns=[0])

    # print(ranked_plays)

    ranked_plays.columns = ranked_plays.loc[0]
    ranked_plays = ranked_plays.drop(0)
    ranked_plays["filter"] = filter

    n_values.columns = n_values.loc[0]
    n_values = n_values.drop(0)
    n_values["filter"] = filter

    return ranked_plays, n_values


def rank_all_filters(df, plays):
    
    
    filter_set = pd.read_csv("../data/inputs/filters.csv")

    output_df = pd.DataFrame(columns=plays)
    output_df_n = pd.DataFrame(columns=plays)
    # output_df.columns = plays

    for i in range(len(filter_set)):
        filter = filter_set.loc[i, "filter"]

        this_output_df, this_output_df_n = rank_plays_with_filter(df, filter)
        output_df = pd.concat([output_df,this_output_df])
        output_df_n = pd.concat([output_df_n,this_output_df_n])

    output_df = output_df.rename(columns={"":"No Play Set"})
    
    return output_df, output_df_n



def main():

    filename = "Rugbycology_dataset_v2.csv"
    x_set = ["Start", "Pass", "Ruck", "Clear", "Contest", "Score", "Retain NEG",
        "Retain Gain 1", "Retain Gain +1", "Retain Score",
        "Retain HR neg", "Retain HR Static", "Retain HR Gain 1", "Retain HR Gain +1",
        "Lose gain neg", "Lose Static", "Lose Gain 1", "Lose Gain +1", "Lose HR neg",
        "Lose HR Static", "Lose HR Gain 1", "Lose HR Gain +1"
    ]
    y_set = "outcome_score"
    # "Retain Static", 

    output_df, summary, osw_set = pre_process(filename, x_set, y_set)

    # mean_set = get_mean_stats(output_df, x_set, "Pick and Go").to_list()
    # print(mean_set)

    # cp_df = pd.DataFrame({"weight": osw_set, "value": mean_set})

    # cp_df["weighted_value"] = cp_df.weight * cp_df.value

    # outcome_score = cp_df.weighted_value.sum()

    ruleset = pd.read_csv("../data/inputs/ruleset.csv")
    plays = ruleset.play.drop_duplicates().to_list()

    # Export
    summary.to_csv(output_loc + "basic_summary.csv", index=False)
    output_df.to_csv(output_loc + "attached_game_id.csv", index=False)

    filtered_results, n_values = rank_all_filters(output_df, plays)
    filtered_results = filtered_results.reset_index(drop=True)
    n_values = n_values.reset_index(drop=True)

    # print(n_values)

    filtered_results.to_csv(output_loc + "filtered_results.csv", index=False)
    n_values.to_csv(output_loc + "n_values.csv", index=False)



if __name__ == "__main__":
    main()