import pandas as pd
import os

# Paths come from config.py at the repository root (set WB_DATA_DIR to relocate the data).
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from config import LIST_DIR, DOCS_DIR, OUT_DIR


# Directory paths

in_dir = OUT_DIR
out_dir = OUT_DIR
os.chdir(in_dir)
os.chdir(in_dir)

# Import and prepare project list
df = pd.read_csv(os.path.join(in_dir, "project_list.csv"))
df["year"] = df.file_name.str[2:6].astype(int)
df["txt_name"] = "doc_" + df.year.astype(str) + "_" + df.id.astype(str) + ".txt"

# Remove sample procurement plans (problem in 2021)
sample_df = pd.read_csv(in_dir + r"\sample_procurement_plans.csv")
sample_df["txt_name"] = "doc_" + sample_df.year.astype(str) + "_" + sample_df.id.astype(str) + ".txt"
df = df[~df.txt_name.isin(sample_df.txt_name)]

# Import keyword finds
search_df = pd.read_csv(in_dir + r"\keyword_finds.csv")

# Merge
df = df.merge(search_df, left_on="txt_name", right_on="filename", how="outer", indicator=True)
df["_merge"].value_counts()
df["no_doc"] = df["_merge"] == "left_only"

# Inspect cases that were not merged
df.groupby("year")["no_doc"].mean().head(60)

# Keep only merged cases
df = df[df["_merge"] == "both"].drop(columns=["_merge", "no_doc"])

# Save cleaned dataset
df.drop(columns="txt_name", inplace=True)
df.to_csv(fr"{out_dir}/99_world_bank_reports.csv", index=False)