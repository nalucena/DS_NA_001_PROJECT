import pandas as pd
import os

# Discovering files in folder:
folder_path = "BD"
file_list = [
    f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))
]

# Select files based on last digits:
title_files = [f for f in file_list if f[-10:] == "titles.csv"]

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

        if items[i] == "":
            items[i] = "outros"

    return items


def column_creator(database, column_name):
    items_list = extract_items(database, column_name)
    columns_dict = {}

    for item in items_list:

        if item != "outros":
            # Add new columns
            database[column_name + " " + item] = 0

            for i in range(0, len(database)):
                if item in database[column_name][i]:
                    database[column_name + " " + item][i] = 1

            # Track new columns in columns_dict
            columns_dict[column_name + " " + item] = database[
                column_name + " " + item
            ].sum()

        elif item == "outros":
            # Check if "outros" column in database
            if (column_name + " outros") not in database:
                database[column_name + " outros"] = 0
                for i in range(0, len(database)):
                    if item in database[column_name][i]:
                        database[column_name + " outros"][i] = 1

            elif (column_name + " outros") in database:
                for i in range(0, len(database)):
                    if item in database[column_name][i]:
                        database[column_name + " outros"][i] += 1

        # Limit the creation of new columns to 10!
        if len(columns_dict) > 9:
            # Check if "outros" column is in database:
            if (column_name + " outros") not in database:
                database[column_name + " outros"] = 0

            # Remove excessive columns by condensing them in "outros"
            to_remove = min(columns_dict, key=columns_dict.get)
            database[column_name + " outros"] += database[to_remove]
            database.drop(to_remove, axis=1, inplace=True)
            del columns_dict[to_remove]


# Passing functions through files:
for file in title_files:
    database = pd.read_csv("BD/" + file)
    column_creator(database, "genres")
    column_creator(database, "production_countries")
    database.to_csv("Cleaned_BD/cleaned_" + file)
