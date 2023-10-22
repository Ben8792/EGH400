import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
# import kaleido

output_loc = "../data/outputs/"
figure_loc = output_loc + "figures/"


# Import data
results_df = pd.read_csv(output_loc + "filtered_results.csv")
n_values = pd.read_csv(output_loc + "n_values.csv")

# Create time graphs
def create_time_graphs():
    time_df = results_df.loc[results_df["filter"].str.contains("time")]
    time_df["time_column"] = time_df["filter"].str.lstrip("time_bin == ").astype(float) + 2.5

    play_list = ["Penalty Goal Attempt", "Kick for Position", "Kick for Touch",
        "Pick and Go Short", "Passing Play", "Pick and Go Long"]
    
    graph = go.Figure()
    graph_title = f"Outcome Score vs. Time for Different Offensive Plays"

    for play in play_list:
        graph.add_trace(go.Scatter(x=time_df.time_column,y=time_df[play],mode="lines",name=play))

    graph.update_layout(
        title=graph_title,
        xaxis_title="Time (seconds)",
        yaxis_title="Expected Outcome Score",
    )

    graph.write_image(figure_loc + f"{graph_title}.png")


# Create Zone graphs
def create_zone_graphs():
    zones_df = results_df.loc[results_df["filter"].str.contains("Zone")]

    zones_df["zone"] = zones_df["filter"].str.lstrip("Zone == \"").str.rstrip("\"")

    trans_df = zones_df.drop(columns="filter").transpose()
    trans_df.columns = trans_df.loc["zone"]
    trans_df = trans_df.loc[trans_df.index != "zone"].reset_index(drop=False)

    for position in ["Own 22", "Own 50", "Opp 50", "Opp 22"]:
        graph_title = f"Expected Outcome Score of Offensive Plays in {position}"
        fig = px.bar(trans_df, x="index", y=position, title=graph_title, labels={
                     "index": "Offensive Play",
                     position: "Outcome Score",
                 },)
        fig.write_image(figure_loc + f"{graph_title}.png")

    print(trans_df)


# Create team attack graphs
def create_team_attack_graphs():
    zones_df = results_df.loc[results_df["filter"].str.contains("teamAttack")]

    zones_df["team"] = zones_df["filter"].str.lstrip("teamAttack == \"").str.rstrip("\"")

    trans_df = zones_df.drop(columns="filter").transpose()
    trans_df.columns = trans_df.loc["team"]
    trans_df = trans_df.loc[trans_df.index != "team"].reset_index(drop=False)

    for team in trans_df.columns.to_list():
        graph_title = f"Expected Outcome Score of {team}'s Offensive Plays"
        fig = px.bar(trans_df, x="index", y=team, title=graph_title, labels={
                     "index": "Offensive Play",
                     team: "Outcome Score",
                 },)
        fig.write_image(figure_loc + f"{graph_title}.png")

    print(trans_df)


def create_team_defense_graphs():
    zones_df = results_df.loc[results_df["filter"].str.contains("teamDefense")]

    zones_df["team"] = zones_df["filter"].str.lstrip("teamDefense == \"").str.rstrip("\"")

    trans_df = zones_df.drop(columns="filter").transpose()
    trans_df.columns = trans_df.loc["team"]
    trans_df = trans_df.loc[trans_df.index != "team"].reset_index(drop=False).rename(columns={"index": "play"})

    this_values_df = n_values.loc[n_values["filter"].str.contains("teamDefense")]

    this_values_df["team"] = this_values_df["filter"].str.lstrip("teamDefense == \"").str.rstrip("\"")

    n_trans_df = this_values_df.drop(columns="filter").transpose()
    n_trans_df.columns = n_trans_df.loc["team"]
    n_trans_df = n_trans_df.loc[n_trans_df.index != "team"].reset_index(drop=False).rename(columns={"index": "play"})

    # data_points_list = trans_df["n_values"].to_list()

    for team in trans_df.columns.to_list()[2:]:
        graph_title = f"Expected Outcome Score of Offensive Plays Against {team}"
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=trans_df.play,
            y=trans_df[team],
            text=n_trans_df[team],
            textposition='auto',
        ))
        # fig = px.bar(trans_df, x="index", y=team, title=graph_title, labels={
        #              "index": "Offensive Play",
        #              team: "Outcome Score",
        #          },)
        fig.write_image(figure_loc + f"{graph_title}.png")

    print(trans_df)


# def create_team_defense_graphs():
#     zones_df = results_df.loc[results_df["filter"].str.contains("teamDefense")]

#     zones_df["team"] = zones_df["filter"].str.lstrip("teamDefense == \"").str.rstrip("\"")

#     trans_df = zones_df.drop(columns="filter").transpose()
#     trans_df.columns = trans_df.loc["team"]
#     trans_df = trans_df.loc[trans_df.index != "team"].reset_index(drop=False)

#     for team in trans_df.team.to_list():
#         graph_title = f"Expected Outcome Score of Offensive Plays Against {team}"
#         fig = px.bar(trans_df, x="index", y=team, title=graph_title, labels={
#                      "index": "Offensive Play",
#                      team: "Defending Team",
#                  },)
#         fig.write_image(figure_loc + f"{graph_title}.png")

#     print(trans_df)


# create_time_graphs()
# create_team_attack_graphs()
create_team_defense_graphs()

