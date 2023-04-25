import pandas as pd

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
    print(input_df.columns)
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


def main():

    # Read input
    input_df = pd.read_csv(input_loc + "Rugbycology_dataset_v2.csv")

    # Create summary
    output_df, summary = summarise(input_df)

    # Export
    summary.to_csv(output_loc + "basic_summary.csv", index=False)
    output_df.to_csv(output_loc + "attached_game_id.csv", index=False)


main()