import numpy as np
import pandas as pd
import json
import requests
import math
import os

# Paths come from config.py at the repository root (set WB_DATA_DIR to relocate the data).
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from config import LIST_DIR, DOCS_DIR, OUT_DIR


pd.options.display.max_columns = 6


in_dir = LIST_DIR
out_dir = OUT_DIR
os.chdir(in_dir)

# Get all files
all_files = os.listdir(in_dir)


# Function to retrieve information
keys_to_retrieve = ["id",
                    "projectid",
                    "docty",
                    "majdocty",
                    "admreg",
                    "count",
                    "projn",
                    "subsc",
                    "theme",
                    "majtheme",
                    "docdt",
                    "lang",
                    "txturl",
                    "pdfurl"]

def create_data_row(json_entry, keys_to_retrieve):
    data_row = []

    for dict_key in keys_to_retrieve:
        if dict_key in json_entry:
            data_row.append(json_entry[dict_key])
        else:
            data_row.append(np.nan)
    return data_row


# Extract information from all files

all_dfs = []

for json_file in all_files:
    try:
        with open(json_file, encoding="utf8") as f:
            wb = f.read()

        wb = json.loads(wb)

        allrows = []
        for key, json_entry in wb["documents"].items():
            if key != "facets":
                new_row = create_data_row(json_entry, keys_to_retrieve)
                allrows.append(new_row)

        df = pd.DataFrame.from_records(allrows, columns=keys_to_retrieve)
        df["file_name"] = json_file

        all_dfs.append(df)
    except Exception as e:
        print(f"FILE {json_file}")
        print(e)



project_list = pd.concat(all_dfs)
project_list.to_csv(os.path.join(out_dir, "project_list.csv"), index=False)

# # Inspect table
# len(project_list)
# project_list.columns
# project_list.docty.value_counts().head(10)
#
#
# ## Check probelm cases -- two server errors (deal with them later!!)
#
# with open("wb2001-2.json", encoding="utf8") as f:
#     wb = f.read() #
#     print(wb)
#
# with open("wb2020-10.json", encoding="utf8") as f:
#     wb = f.read()
#     print(wb)