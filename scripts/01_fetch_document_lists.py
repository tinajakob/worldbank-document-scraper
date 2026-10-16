import pandas as pd
import json
import requests
import math

# Paths come from config.py at the repository root (set WB_DATA_DIR to relocate the data).
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from config import LIST_DIR, DOCS_DIR, OUT_DIR


base_path = LIST_DIR
base_url = "https://search.worldbank.org/api/v2/wds?"

# Get number of documents per year
docs_per_year = {}

for year in range(1947, 2024):

    params = {"format": "json",
              "order": "desc",
              "majdocty_key": 658102,
              "rows": 1,
              "apilang": "en",
              "strdate": f"01-01-{year}",
              "enddate": f"12-31-{year}"}

    r = requests.get(base_url, params)
    try:
        nr_docs = json.loads(r.text)["total"]
        docs_per_year[year] = nr_docs
    except:
        print(f"error in year {year}")


docs_per_year # Improve: save this!!
docs_per_year_df = pd.DataFrame(list(docs_per_year.items()), columns=['Year', 'Documents'])
docs_per_year_df.to_csv(f"{base_path}/docs_per_year.csv")

# For each year: download 1000 at a time
for year, nr_docs in docs_per_year.items():
    print(year, nr_docs)

    end_i = math.floor(nr_docs/1000)*1000
    start_i = 0
    i = 0
    while start_i <= end_i:
        params = {"format": "json",
                  "order": "desc",
                  "majdocty_key": 658102,
                  "rows": 1000,
                  "os": start_i,
                  "apilang": "en",
                  "strdate": f"01-01-{year}",
                  "enddate": f"12-31-{year}"}

        start_i += 1000
        i += 1

        try:
            # Get page
            r = requests.get(base_url, params)

            # Save txt
            with open(fr"{base_path}\wb{year}-{i}.json", "w", encoding="utf8") as f:
                f.write(r.text)
        except:
            print(f"problem with {start_i} in {year}")
    print("done!")


# Check what happens in last group
with open(rf"{base_path}\wb2009-6.json", encoding="utf8") as f:
    wb6 = f.read()
wb6 = json.loads(wb6)
wb6 = wb6["documents"].keys()
len(wb6)

with open(fr"{base_path}\wb2009-5.json", encoding="utf8") as f:
    wb4 = f.read()
wb4 = json.loads(wb4)
wb4 = wb4["documents"].keys()
len(wb4)

with open(rf"{base_path}\wb2009-4.json", encoding="utf8") as f:
    wb5 = f.read()
wb5 = json.loads(wb5)
wb5 = wb5["documents"].keys()
len(wb5)

len(set(wb6).intersection(set(wb5)))
len(set(wb6).intersection(set(wb4)))