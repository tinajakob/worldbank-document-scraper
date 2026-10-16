import numpy as np
import pandas as pd
import json
import requests
import os
from urllib.request import urlretrieve
import time
import dask
import dask.dataframe
import random

# Paths come from config.py at the repository root (set WB_DATA_DIR to relocate the data).
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from config import LIST_DIR, DOCS_DIR, OUT_DIR


pd.options.display.max_columns = 6


temp_dir = OUT_DIR
out_dir = DOCS_DIR

# Import project list
df = pd.read_csv(fr"{temp_dir}/project_list.csv")
len(df.id)
len(df.id.unique()) # 3 dups, deal with them later
df.columns
df["txturl"][0]
df["year"] = df.file_name.str[2:6]

# Drop if no lin available
len(df)
df = df[df["txturl"].notna()]
print(len(df))


# # Function to retrieve file
# def retrieve_file(row):
#     year = row["year"]
#     url = row["txturl"]
#     doc_id = row['id']
#     filename = out_dir + f"\doc_{year}_{doc_id}.txt"
#     try:
#         # Check if file exists, else retrieve and save
#         if not os.path.isfile(filename):
#             urlretrieve(url, filename)
#     except Exception as e:
#         print(f"row {doc_id}, link {url}")
#         print(e)

def retrieve_file(row):
    year = row["year"]
    url = row["txturl"]
    doc_id = row['id']
    filename = out_dir + f"\doc_{year}_{doc_id}.txt"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }

    session = requests.Session()

    try:
        if not os.path.isfile(filename):
            response = session.get(url, headers=headers)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded {filename}")
            else:
                print(f"Failed to download {url}, status code: {response.status_code}")

            # Add a short, random delay (between 1–3 seconds) to avoid rate limits
            time.sleep(random.uniform(1, 3))

    except Exception as e:
        print(f"row {doc_id}, link {url}")
        print(e)


# Use dask to retrieve all files
start_time = time.time()
ddf = dask.dataframe.from_pandas(df, npartitions=21)

ddf.apply(retrieve_file, axis=1).compute()
duration = (time.time()-start_time)/60
#duration/60*340


