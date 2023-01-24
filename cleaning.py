import pandas as pd
import os

# Discovering files in folder:
folder_path = "BD"
file_list = [
    f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))
]

# Select files based on last digits:
title_files = [f for f in file_list if f[-10:] == "titles.csv"]
# credit_files = [f for f in file_list if f[-11:] == "credits.csv"]


#  Creating functions:
def extract_items(database_name, column_name):
    column_copy = database_name[column_name].str.strip("[]")
    column_copy = column_copy.str.split(", ")  # Transforms str into list

    items = []

    for i in column_copy:
        items.extend(i)

    items = list(set(items))

    for i in range(0, len(items)):
        items[i] = items[i].strip("'")

    return items


def column_creator(database, column_name):
    items_list = extract_items(database, column_name)
    columns_dict = {}

    for item in items_list:

        database[column_name + " " + item] = 0

        # Populates the column
        for i in range(0, len(database)):
            if item in database[column_name][i]:
                database[column_name + " " + item][i] = 1

        # Do not add "outros" to columns_dict
        if column_name + " " + item != column_name + " outros":
            columns_dict[column_name + " " + item] = database[
                column_name + " " + item
            ].sum()

        # Check if "outros" is in database, if not, add it!
        if len(columns_dict) == 9:
            if (column_name + " outros") not in database:
                database[column_name + " outros"] = 0

        # Remove excessive columns by condensing them!
        if len(columns_dict) > 9:
            to_remove = min(columns_dict, key=columns_dict.get)
            database[column_name + " outros"] = +database[to_remove]
            database.drop(to_remove, axis=1, inplace=True)
            del columns_dict[to_remove]


# Passing functions through files:
for file in title_files:
    database = pd.read_csv("BD/" + file)
    column_creator(database, "genres")
    column_creator(database, "production_countries")
    database.to_csv("Cleaned_BD/cleaned_" + file)
