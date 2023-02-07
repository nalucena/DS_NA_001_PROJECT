import pandas as pd
import os

# Discovering files in folder:
folder_path = "BD"
file_list = [
    f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))
]

# Select files based on last digits:
title_files = [f for f in file_list if f[-10:] == "titles.csv"]
credit_files = [f for f in file_list if f[-11:] == "credits.csv"]


#  Creating functions:
def extract_items(database_name, column_name):
    """Extrair os varios atributos existentes em uma coluna"""
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


def streamer_column(database, file):
    """Criar uma coluna para identificar a plataforma de stream"""
    database["streamer"] = file[:-11]
    return database


def column_creator(database, column_name):
    """Cria uma coluna para cada atributo identificado"""
    items_list = extract_items(database, column_name)

    for item in items_list:
        # Add new columns
        database[column_name + " " + item] = 0

        for i in range(0, len(database)):
            if item in database[column_name][i]:
                database[column_name + " " + item][i] = 1


def column_trimmer(database, column_name):
    """Reduz a quantidade de colunas a 10, para facilitar a analise"""
    columns_dict = {}
    for item in database.columns:
        if item == column_name + " outros":
            continue
        elif item[: len(column_name) + 1] == column_name + " ":
            columns_dict[item] = database[item].sum()

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
title_base = pd.DataFrame()

for file in title_files:
    database = pd.read_csv("BD/" + file)
    database.drop("description", axis=1, inplace=True)
    database = streamer_column(database, file)
    column_creator(database, "genres")
    column_creator(database, "production_countries")

    title_base = pd.concat([title_base, database], axis=0)

column_trimmer(title_base, "genres")
column_trimmer(title_base, "production_countries")

title_base.to_csv("Cleaned_BD/cleaned_base.csv")

credits_base = pd.DataFrame()

for file in credit_files:
    database = pd.read_csv("BD/" + file)
    credits_base = pd.concat([credits_base, database], axis=0)

credits_base.to_csv("Cleaned_BD/cleaned_credits.csv")
