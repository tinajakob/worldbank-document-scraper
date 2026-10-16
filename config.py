"""
Where the pipeline reads and writes.

By default everything lives under `data/` inside the repository. Point WB_DATA_DIR somewhere
else if you want the corpus on another drive -- the downloaded documents alone are ~70 GB, so
that is usually what you want.

    set WB_DATA_DIR=D:\worldbank            (Windows)
    export WB_DATA_DIR=/mnt/big/worldbank   (Linux/macOS)

Nothing else in the pipeline hard-codes a path.
"""

import os

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.environ.get("WB_DATA_DIR", "").strip() or os.path.join(REPO_ROOT, "data")

# Stage 1: raw JSON responses from the WDS API, one file per year and page.
LIST_DIR = os.path.join(DATA_DIR, "01_document_lists")

# Stage 3: the downloaded document texts, one .txt per document. This is the big one.
DOCS_DIR = os.path.join(DATA_DIR, "02_document_texts")

# Stages 2, 4, 5, 6: tables produced along the way.
OUT_DIR = os.path.join(DATA_DIR, "03_output")

for _d in (LIST_DIR, DOCS_DIR, OUT_DIR):
    os.makedirs(_d, exist_ok=True)

__all__ = ["REPO_ROOT", "DATA_DIR", "LIST_DIR", "DOCS_DIR", "OUT_DIR"]

if __name__ == "__main__":
    for k in ("REPO_ROOT", "DATA_DIR", "LIST_DIR", "DOCS_DIR", "OUT_DIR"):
        print(f"{k:11s} {globals()[k]}")
