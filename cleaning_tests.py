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


def table_creator(database, column_name):
    items_list = extract_items(database, column_name)
    columns_dict = {}
    new_table = pd.DataFrame(index=range(len(database)))

    for item in items_list:
        if item != "outros":
            # Add new columns
            new_table[column_name + " " + item] = 0

            for i in range(len(database)):
                if item in database[column_name][i]:
                    new_table[column_name + " " + item][i] = 1

            # Track new columns in columns_dict
            columns_dict[column_name + " " + item] = new_table[
                column_name + " " + item
            ].sum()

        elif item == "outros":
            # Check if "outros" column in database
            if (column_name + " outros") not in new_table:
                new_table[column_name + " outros"] = 0
                for i in range(len(database)):
                    if item in database[column_name][i]:
                        new_table[column_name + " outros"][i] = 1

            elif (column_name + " outros") in new_table:
                for i in range(len(database)):
                    if item in database[column_name][i]:
                        new_table[column_name + " outros"][i] += 1

        # Limit the creation of new columns to 10!
        if len(columns_dict) > 9:
            # Check if "outros" column is in database:
            if (column_name + " outros") not in new_table:
                new_table[column_name + " outros"] = 0

            # Remove excessive columns by condensing them in "outros"
            to_remove = min(columns_dict, key=columns_dict.get)
            new_table[column_name + " outros"] += new_table[to_remove]
            new_table.drop(to_remove, axis=1, inplace=True)
            del columns_dict[to_remove]
        
        results_table = pd.DataFrame()
        for column in new_table.columns:
            results_table[column] = new_table[column].sum()

    return results_table


def export_table(file, table_name, column_name):
    table_name.to_csv("BD/" + file[:-10] + column_name + ".csv")


# Passing functions through files:
for file in title_files:
    database = pd.read_csv("BD/" + file)
    genres_table = table_creator(database, "genres")
    export_table(file, genres_table, "genres")
    countries_table = table_creator(database, "production_countries")
    export_table(file, countries_table, "production_countries")
