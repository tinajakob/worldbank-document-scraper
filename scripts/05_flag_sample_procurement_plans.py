import pandas as pd
import os

# Paths come from config.py at the repository root (set WB_DATA_DIR to relocate the data).
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from config import LIST_DIR, DOCS_DIR, OUT_DIR


# Directory paths

in_dir = LIST_DIR
txt_dir = DOCS_DIR
out_dir = OUT_DIR
os.chdir(in_dir)
os.chdir(in_dir)

# Import and prepare project list
df = pd.read_csv(os.path.join(out_dir, "project_list.csv"))
df["year"] = df.file_name.str[2:6].astype(int)  # Assuming format is wbYYYY_nr.json
df["txt_name"] = "doc_" + df.year.astype(str) + "_" + df.id.astype(str) + ".txt"

# Filter documents in the problematic ID range
mask = (df.id >= 33211820) & (df.id <= 33218910)
selected_df = df[mask]

# Identify non-sample procurement plans
def is_sample_plan(file_name, txt_dir):
    """Check if a document is a sample procurement plan."""
    try:
        with open(os.path.join(txt_dir, file_name), 'r', encoding='utf-8') as f:
            start = f.read(200).lower()
            return 'sample procurement plan' in start
    except:
        print(f"Error reading file: {file_name}")
        return False

non_sample_ids = []
for _, row in selected_df.iterrows():
    if not is_sample_plan(row.txt_name, txt_dir):
        non_sample_ids.append(row.id)

# Save results
sample_plans_df = selected_df[~selected_df.id.isin(non_sample_ids)]
sample_plans_df.to_csv(os.path.join(out_dir, "sample_procurement_plans.csv"), index=False)

# Print summary
print(f"Found {len(sample_plans_df)} sample procurement plans out of {len(selected_df)} documents")