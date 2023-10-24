import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

input_loc = "../data/inputs/"
output_loc = "../data/outputs/"
figure_loc = output_loc + "figures/"


# Import data
results_df = pd.read_csv(output_loc + "filtered_results.csv")
n_values = pd.read_csv(output_loc + "n_values.csv")
filters = pd.read_csv(input_loc + "filters.csv")

# Extract special scenarios
results_df = pd.merge(results_df, filters, how="left", left_on="filter", right_on="filter")
n_values = pd.merge(n_values, filters, how="left", left_on="filter", right_on="filter")
# print(results_df)

# Create time graphs
def create_time_graphs():
    time_df = results_df.loc[(results_df["filter"].str.contains("time")) & (results_df.special_scenario == "FALSE")]
    time_df["time_column"] = time_df["filter"].str.replace("time_bin == ","").astype(float) + 2.5

    play_list = ["Penalty Goal Attempt", "Kick for Position", "Kick for Touch",
        "Pick and Go Short", "Passing Play", "Pick and Go Long"]
    
    graph = go.Figure()
    graph_title = f"Outcome Score vs. Time for Different Offensive Plays"

    for play in play_list:
        graph.add_trace(go.Scatter(x=time_df.time_column,y=time_df[play],mode="lines",name=play))

    graph.update_layout(
        title=graph_title,
        xaxis_title="Time (minutes)",
        yaxis_title="Expected Outcome Score",
    )

    graph.write_image(figure_loc + f"{graph_title}.png")


def create_zone_graphs():
    """
    Create graphs of offensive play results in specific field positions.
    """
    # Grab teamDefense results
    zones_df = results_df.loc[(results_df["filter"].str.contains("Zone")) & (results_df.special_scenario == "FALSE")].drop(columns=["No Play Set"])

    # Extract team
    zones_df["zone"] = zones_df["filter"].str.replace("Zone == \"","").str.rstrip("\"")

    # Transpose and clean up
    trans_df = zones_df.drop(columns="filter").transpose()
    trans_df.columns = trans_df.loc["zone"]
    trans_df = trans_df.loc[trans_df.index != "zone"].reset_index(drop=False).rename(columns={"index": "play"})

    # Same thing as above, for no. data points
    this_values_df = n_values.loc[(n_values["filter"].str.contains("Zone")) & ~(n_values.special_scenario)].drop(columns=["No Play Set"])
    this_values_df["zone"] = this_values_df["filter"].str.replace("Zone == \"","").str.rstrip("\"")

    # Transposing
    n_trans_df = this_values_df.drop(columns="filter").transpose()
    n_trans_df.columns = n_trans_df.loc["zone"]
    n_trans_df = n_trans_df.loc[n_trans_df.index != "zone"].reset_index(drop=False).rename(columns={"index": "play"})

    # Get list of teams available
    zone_list = trans_df.drop(columns="play").columns.to_list()

    # Create a graph for each team
    for zone in zone_list:
        graph_title = f"Expected Outcome Score of Offensive Plays in {zone}"
        # Initialise plotly figure object
        fig = go.Figure()
        # Add bar chart
        fig.add_trace(go.Bar(
            x=trans_df.play,
            y=trans_df[zone],
            text=n_trans_df[zone], # Add number of data points
            textposition='auto',
        ))
        # Add titles, labels, etc
        fig.update_layout(
            title=graph_title,
            xaxis_title="Offensive Play",
            yaxis_title="Expected Outcome Score",
        )
        # Write to png
        fig.write_image(figure_loc + f"{graph_title}.png")


def create_team_attack_graphs():
    """
    Create graphs of defensive team offensive play results.
    """
    # Grab teamDefense results
    zones_df = results_df.loc[(results_df["filter"].str.contains("teamAttack")) & (results_df.special_scenario == "FALSE")].drop(columns=["No Play Set"])

    # Extract team
    zones_df["team"] = zones_df["filter"].str.replace("teamAttack == \"", "").str.rstrip("\"")
    

    # Transpose and clean up
    trans_df = zones_df.drop(columns="filter").transpose()
    trans_df.columns = trans_df.loc["team"]
    trans_df = trans_df.loc[trans_df.index != "team"].reset_index(drop=False).rename(columns={"index": "play"})

    # Same thing as above, for no. data points
    this_values_df = n_values.loc[(n_values["filter"].str.contains("teamAttack")) & ~(n_values.special_scenario)].drop(columns=["No Play Set"])
    this_values_df["team"] = this_values_df["filter"].str.replace("teamAttack == \"", "").str.rstrip("\"")

    # Transposing
    n_trans_df = this_values_df.drop(columns="filter").transpose()
    n_trans_df.columns = n_trans_df.loc["team"]
    n_trans_df = n_trans_df.loc[n_trans_df.index != "team"].reset_index(drop=False).rename(columns={"index": "play"})

    # Get list of teams available
    team_list = trans_df.drop(columns="play").columns.to_list()

    # Create a graph for each team
    for team in team_list:
        graph_title = f"Expected Outcome Score of Offensive Plays by {team}"
        # Initialise plotly figure object
        fig = go.Figure()
        # Add bar chart
        fig.add_trace(go.Bar(
            x=trans_df.play,
            y=trans_df[team],
            text=n_trans_df[team], # Add number of data points
            textposition='auto',
        ))
        # Add titles, labels, etc
        fig.update_layout(
            title=graph_title,
            xaxis_title="Offensive Play",
            yaxis_title="Expected Outcome Score",
        )
        # Write to png
        fig.write_image(figure_loc + f"{graph_title}.png")


def create_team_defense_graphs():
    """
    Create graphs of defensive team offensive play results.
    """
    # Grab teamDefense results
    zones_df = results_df.loc[(results_df["filter"].str.contains("teamDefense")) & (results_df.special_scenario == "FALSE")].drop(columns=["No Play Set"])

    # Extract team
    zones_df["team"] = zones_df["filter"].str.replace("teamDefense == \"", "").str.rstrip("\"")

    # Transpose and clean up
    trans_df = zones_df.drop(columns="filter").transpose()
    trans_df.columns = trans_df.loc["team"]
    trans_df = trans_df.loc[trans_df.index != "team"].reset_index(drop=False).rename(columns={"index": "play"})

    # Same thing as above, for no. data points
    this_values_df = n_values.loc[(n_values["filter"].str.contains("teamDefense")) & ~(n_values.special_scenario)].drop(columns=["No Play Set"])
    this_values_df["team"] = this_values_df["filter"].str.replace("teamDefense == \"", "").str.rstrip("\"")

    # Transposing
    n_trans_df = this_values_df.drop(columns="filter").transpose()
    n_trans_df.columns = n_trans_df.loc["team"]
    n_trans_df = n_trans_df.loc[n_trans_df.index != "team"].reset_index(drop=False).rename(columns={"index": "play"})

    # Get list of teams available
    team_list = trans_df.drop(columns="play").columns.to_list()

    # Create a graph for each team
    for team in team_list:
        graph_title = f"Expected Outcome Score of Offensive Plays Against {team}"
        # Initialise plotly figure object
        fig = go.Figure()
        # Add bar chart
        fig.add_trace(go.Bar(
            x=trans_df.play,
            y=trans_df[team],
            text=n_trans_df[team], # Add number of data points
            textposition='auto',
        ))
        # Add titles, labels, etc
        fig.update_layout(
            title=graph_title,
            xaxis_title="Offensive Play",
            yaxis_title="Expected Outcome Score",
        )
        # Write to png
        fig.write_image(figure_loc + f"{graph_title}.png")


def create_origin_graphs():
    """
    Create graphs of offensive play results per origin type.
    """
    # Grab teamDefense results
    origin_df = results_df.loc[(results_df["filter"].str.contains("Origin")) & (results_df.special_scenario == "FALSE")].drop(columns=["No Play Set"])

    # Extract team
    origin_df["origin"] = origin_df["filter"].str.replace("Origin == \"","").str.rstrip("\"")

    # Transpose and clean up
    trans_df = origin_df.drop(columns="filter").transpose()
    trans_df.columns = trans_df.loc["origin"]
    trans_df = trans_df.loc[trans_df.index != "origin"].reset_index(drop=False).rename(columns={"index": "play"})

    # Same thing as above, for no. data points
    this_values_df = n_values.loc[(n_values["filter"].str.contains("Origin")) & ~(n_values.special_scenario)].drop(columns=["No Play Set"])
    this_values_df["origin"] = this_values_df["filter"].str.replace("Origin == \"","").str.rstrip("\"")

    # Transposing
    n_trans_df = this_values_df.drop(columns="filter").transpose()
    n_trans_df.columns = n_trans_df.loc["origin"]
    n_trans_df = n_trans_df.loc[n_trans_df.index != "origin"].reset_index(drop=False).rename(columns={"index": "play"})

    # Get list of teams available
    origin_list = trans_df.drop(columns="play").columns.to_list()

    # Create a graph for each team
    for origin in origin_list:
        graph_title = f"Expected Outcome Score of Offensive Plays After {origin}"
        # Initialise plotly figure object
        fig = go.Figure()
        # Add bar chart
        fig.add_trace(go.Bar(
            x=trans_df.play,
            y=trans_df[origin],
            text=n_trans_df[origin], # Add number of data points
            textposition='auto',
        ))
        # Add titles, labels, etc
        fig.update_layout(
            title=graph_title,
            xaxis_title="Offensive Play",
            yaxis_title="Expected Outcome Score",
        )
        # Write to png
        fig.write_image(figure_loc + f"{graph_title}.png")


def create_special_graphs():
    """
    Create graphs of offensive play results per origin type.
    """
    # Grab teamDefense results
    scenarios_df = results_df.loc[(results_df.special_scenario != "FALSE")].drop(columns=["No Play Set"])

    # Extract team
    # scenarios_df["origin"] = scenarios_df["filter"].str.replace("Origin == \"","").str.rstrip("\"")

    # Transpose and clean up
    trans_df = scenarios_df.drop(columns=["filter", "no."]).transpose()
    trans_df.columns = trans_df.loc["special_scenario"]
    trans_df = trans_df.loc[trans_df.index != "special_scenario"].reset_index(drop=False).rename(columns={"index": "play"})

    # Same thing as above, for no. data points
    this_values_df = n_values.loc[(n_values.special_scenario != "FALSE")].drop(columns=["No Play Set"])
    # this_values_df["origin"] = this_values_df["filter"].str.replace("Origin == \"","").str.rstrip("\"")

    # Transposing
    n_trans_df = this_values_df.drop(columns=["filter", "no."]).transpose()
    n_trans_df.columns = n_trans_df.loc["special_scenario"]
    n_trans_df = n_trans_df.loc[n_trans_df.index != "special_scenario"].reset_index(drop=False).rename(columns={"index": "play"})

    # Get list of teams available
    scenario_list = trans_df.drop(columns="play").columns.to_list()

    # Create a graph for each team
    for scenario in scenario_list:
        graph_title = f"Expected Outcome Score of Offensive Plays in {scenario}"
        # Initialise plotly figure object
        fig = go.Figure()
        # Add bar chart
        fig.add_trace(go.Bar(
            x=trans_df.play,
            y=trans_df[scenario],
            text=n_trans_df[scenario], # Add number of data points
            textposition='auto',
        ))
        # Add titles, labels, etc
        fig.update_layout(
            title=graph_title,
            xaxis_title="Offensive Play",
            yaxis_title="Expected Outcome Score",
        )
        # Write to png
        fig.write_image(figure_loc + f"{graph_title}.png")


# create_time_graphs()
# create_team_attack_graphs()
# create_team_defense_graphs()
# create_origin_graphs()
# create_zone_graphs()
create_special_graphs()
