import pandas as pd


def summarise(input_df: pd.DataFrame) -> list[pd.DataFrame, pd.DataFrame]:
    """
    Summarises a defined list of statistics per game

    :param input_df: Input df, play by play
    :returns input_df: input df with game ids added
    :returns overall: Summarised stats, per game
    """

    # Change to nicer column names
    input_df = input_df.rename(columns={
        "Attack Team": "teamAttack",
        "Defense team": "teamDefense",
        "Date": "date"
    })

    # Ask pandas to interpret as datetime instead of string
    input_df.date = pd.to_datetime(input_df.date, dayfirst=True)

    # Get list of each game (reduced from list of each play)
    game_ids = (
        input_df[["teamAttack", "teamDefense", "date"]]
        .loc[input_df.teamAttack > input_df.teamDefense]
        .drop_duplicates()
        .sort_values(by=["date", "teamAttack", "teamDefense"], ignore_index=True)
        .reset_index(drop=False)
        .rename(columns={"index": "game_id"})
    )

    # Allow game_d to seam teamA vs teamB AND teamB vs teamA
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
    input_df = pd.merge(input_df, game_ids)

    # Initilase summary df
    overall = game_ids

    # Define lis of stats to sum
    stats_to_sum = ["Pass", "Ruck", "Clear"]

    # Generate sums
    for stat in stats_to_sum:
        this_summary = input_df.groupby(["teamAttack", "teamDefense", "game_id"])[stat].sum().reset_index()
        overall = pd.merge(overall, this_summary)

    return input_df, overall


def main():

    # Read input
    input_df = pd.read_csv("Rugbycology_dataset_v2.csv")

    # Create summary
    output_df, summary = summarise(input_df)

    # Export
    summary.to_csv("basic_summary.csv", index=False)


main()