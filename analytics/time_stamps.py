
import pandas as pd
import csv
import numpy as np

def add_time_stamps(df):

    # df = pd.read_csv("Rugbycology_dataset_v2.csv")

    ### Time 1 Variable

    # initialize variables
    tally = []
    curr_val = df.iloc[0, 0]
    count = 0

    # iterate over the rows of the DataFrame
    for i, row in df.iterrows():
        # check if the current value in the first column is different from the previous one
        if row['game_id'] != curr_val:
            # store the tally and reset the count
            tally.append(count)
            count = 0
            curr_val = row['game_id']
        count += 1

    # add the final tally to the list
    tally.append(count)

    # Initialise the game end time as 83 minutes
    game_end = 83

    ## Time Variable

    # Create empty arrays for sums
    sums_pass = []
    sums_ruck = []
    sums_clear = []

    # Initialise
    start_index = 0

    # Calculate sums of rucks, passes and clearances
    for t in tally:
        end_index = start_index + t
        s_ruck = df.iloc[start_index:end_index, 10].sum()
        s_pass = df.iloc[start_index:end_index, 9].sum()
        s_clear = df.iloc[start_index:end_index, 11].sum()
        sums_ruck.append(s_ruck)
        sums_pass.append(s_pass)
        sums_clear.append(s_clear)
        start_index = end_index

    # Apply scaling factors
    ruck_scale = 4
    pass_scale = 1
    clear_scale = 6

    # Scale the sums
    sums_ruck = [x * ruck_scale for x in sums_ruck]
    sums_pass = [x * pass_scale for x in sums_pass]
    sums_clear = [x * clear_scale for x in sums_clear]

    # Create a mapping dictionary
    string_to_number = {
        "Restart": 1, 
        "Kick fielded": 2,
        "Turnover": 3,
        "Scrum": 4,
        "Free-kick": 5,
        "Lineout": 6,
        "Penalty": 7
    }

    # Convert the strings to numbers
    map_dic = df['Origin'].map(string_to_number)

    # Display column of mapped numbers
    df["map_dic"] = map_dic

    # Initialise
    start_index = 0
    game_sums = []
    score_counts = []

    # Create a Series with all possible values (1 through 7)
    all_possible_values = pd.Series(range(1, 8))

    # Calculate sums
    for t in tally:
        end_index = start_index + t

        # Count the occurrences of each number in the 'numbers' column
        number_counts = df.iloc[start_index:end_index, 15].value_counts(sort=False)

        # Reindex the number_counts Series with all possible values (1 through 7)
        number_counts = number_counts.reindex(all_possible_values, fill_value=0)

        # Store just the occurrences (counts) in a list or NumPy array
        occurrences_list = number_counts.values.tolist()
        game_sums.append(occurrences_list)

        # Count the number of times a team scores
        times_scored = (df.iloc[start_index:end_index, 13] > 3).sum()
        score_counts.append(times_scored)

        start_index = end_index

    # Apply scaling factors
    restart_scale = 23
    scrum_scale = 65
    free_kick_scale = 37
    lineout_scale = 25
    penalty_scale = 37

    # Create new variable
    scaled_times = game_sums

    # Columns to remove (No addition to time)
    columns_to_remove = [1, 2]  # Remove the second and third columns (indices 1 and 2)

    # Remove the specified columns using list comprehension
    scaled_times = [[row[i] for i in range(len(row)) if i not in columns_to_remove] for row in scaled_times]

    # Scale the times
    for row in scaled_times:
        row[0] *= restart_scale
        row[1] *= scrum_scale
        row[2] *= free_kick_scale
        row[3] *= lineout_scale
        row[4] *= penalty_scale

    # Calculate the sum of entries in each row using list comprehension
    scaled_sums = [sum(row) for row in scaled_times]

    # Calculate time wasted for tries
    try_scale = 80

    # Perform element-wise multiplication
    sums_tries = [try_scale * count for count in score_counts]

    # Calculate a total sum
    df.fillna(0, inplace=True)
    total_sums = [sum(x) for x in zip(sums_ruck, sums_pass, sums_clear, scaled_sums, sums_tries)]

    # Create a time column variable
    time_col = []

    # Initialise
    start_index = 0
    counter = 0
    scale = 0
    scale2 = 0

    # Create a loop to iterate through tally and total sums simultaneously
    for t, s in zip(tally, total_sums):

        # Identify last row in a match
        end_index = start_index + t

        # Iterate over each row
        for index, row in df.iloc[start_index:end_index].iterrows():

            # Determine scaling
            if row[15] == 1:
                scale = restart_scale
            if row[15] == 4:
                scale = scrum_scale
            if row[15] == 5:
                scale = free_kick_scale
            if row[15] == 6:
                scale = lineout_scale
            if row[15] == 7:
                scale = penalty_scale
            if row[13] > 3:
                scale2 = try_scale

            # Calculate the weighted time
            value = (pass_scale*row[9] + ruck_scale*row[10] + clear_scale*row[11] + scale + scale2)/ s * game_end

            # Check if new game, if not new game, add to previous
            if counter > 0:
                value += time_col[-1]

            # Increment counter
            counter += 1

            # Reset counter at end of game
            if counter == t:
                counter = 0

            # Append value to time_col4
            time_col.append(value)

            # Reset scaling indexes
            scale = 0
            scale2 = 0

        # Assign index to start of new game
        start_index = end_index

    # Remove reference column
    df = df.drop(df.columns[15], axis=1)

    # add the "time" column to the DataFrame
    df['time'] = time_col

    # convert to integer time values
    df['time'] = df['time'].round(2)

    # Initialise
    start_index = 0
    diff = 0

    # Create a loop to iterate through tally
    for t in tally:

        # Identify last row in a match
        end_index = start_index + t

        # Iterate over each row
        for index, row in df.iloc[start_index:end_index].iterrows():

            # Check if empirical time is recorded
            if df.iloc[index, 14] > 0:

                # Calculate discrepancy between actual and recorded time
                diff = df.iloc[index, 15] - df.iloc[index, 14]

            # Adjust estimate
            df.iloc[index, 15] = df.iloc[index, 15] - diff

        # Set difference to 0
        diff = 0

        # Assign index to start of new game
        start_index = end_index   

    return df
