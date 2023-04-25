import pandas as pd

input_loc = "../data/inputs/"
output_loc = "../data/inputs/"

game_data = pd.read_csv(input_loc + "attached_game_id.csv")

game_ids = game_data.game_id.drop_duplicates.to_list()

# for game in game