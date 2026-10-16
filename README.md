# World Bank document scraper

Downloads project documents from the World Bank **Documents & Reports** API and counts
development-terminology keywords across the corpus.

Built to measure the rise of bottom-up and community-driven development language in World Bank
project documents between 1947 and 2023, for *Top Down or Bottom Up? Evidence from a Field
Experiment on Public Goods Provision*. It is generic enough to reuse for any keyword analysis
over the same corpus — change the `searches` dictionary in `scripts/04_count_keywords.py`.

---

## ⚠ When this was run, and why that matters

| | |
|---|---|
| Document lists fetched | **2025-03-15** |
| Document texts downloaded | **2023-10-06 to 2025-03-17** |
| Coverage | publication years **1947–2023** |
| Documents retrieved | **343,177** (~70 GB of text) |
| API endpoint | `https://search.worldbank.org/api/v2/wds` |
| Document-type filter | `majdocty_key=658102` (project documents) |

**The API may have changed since.** If stage 1 returns nothing or stage 2 cannot parse the
response, check the current API documentation before debugging this code.

Reruns will not reproduce the document count above either: the Bank adds and reclassifies
documents continuously, so treat the corpus as a dated snapshot.

---

## Pipeline

Run in order. Stages 1 and 3 hit the network; stage 4 is CPU and disk bound.

| | script | what it does | roughly |
|---|---|---|---|
| 1 | `01_fetch_document_lists.py` | queries the API year by year, 1,000 records per page, saving raw JSON | ~30 min |
| 2 | `02_build_document_table.py` | parses the JSON into one row per document with metadata and text URL | ~2 min |
| 3 | `03_download_documents.py` | downloads each document's plain text, skipping files already present | **hours to days** |
| 4 | `04_count_keywords.py` | regex keyword counts plus length statistics over every document | ~4 h |
| 5 | `05_flag_sample_procurement_plans.py` | flags boilerplate "sample procurement plan" documents for exclusion | ~1 min |
| 6 | `06_finalize_dataset.py` | merges the keyword counts onto the document table | ~1 min |

Stage 3 is restartable: it checks whether each file already exists, so an interrupted download
can simply be run again. It also sleeps 1–3 seconds between requests to stay polite to the API.

```bash
pip install -r requirements.txt
python scripts/01_fetch_document_lists.py
python scripts/02_build_document_table.py
python scripts/03_download_documents.py
python scripts/04_count_keywords.py
python scripts/05_flag_sample_procurement_plans.py
python scripts/06_finalize_dataset.py
```

## Where the data goes

Everything lands under `data/` in the repository by default:

```
data/01_document_lists/   raw API responses (JSON)        ~1.5 GB
data/02_document_texts/   downloaded document texts       ~70 GB
data/03_output/           the tables produced             ~230 MB
```

The corpus is large. To put it elsewhere, set `WB_DATA_DIR`:

```bash
set WB_DATA_DIR=D:\worldbank           # Windows
export WB_DATA_DIR=/mnt/big/worldbank  # Linux/macOS
```

`data/` is git-ignored — none of it belongs in version control, and the larger tables exceed
GitHub's 100 MB per-file limit anyway.

## Output

`06_finalize_dataset.py` writes `world_bank_reports.csv`: one row per document, with the API
metadata (id, project id, document type, region, country, date, language, URLs) plus, for each
search term, the number of matches in that document, and `nchar` / `nwords` / `ncwords` length
statistics for normalisation.

## Notes on the keyword counting

- Searches are **regular expressions**, not literal strings, and are counted with
  `re.findall`, so a term can match several times per document. See the `searches` dictionary
  at the top of `04_count_keywords.py`.
- Matching is deliberately loose in places: `"state"` matches `statement`, `"equal"` matches
  `equality` and `unequal`. If that matters for your use, add word boundaries (`\b`).
- Text is lower-cased, whitespace is collapsed, and everything outside `[0-9A-Za-z \t]` is
  stripped before matching.
- An earlier version of the cleaning step deleted newlines instead of replacing them with
  spaces, which welded the last word of each line onto the first word of the next. That is
  fixed here; the original line is kept as a comment with the measured impact (~12% of word
  boundaries, and a 10–15% undercount of rare multi-word phrases).
- `04_count_keywords.py` uses `dask.bag` with the threaded scheduler, behind an
  `if __name__ == "__main__"` guard. The guard is required: `dask.bag` defaults to the
  multiprocessing scheduler, and without it each worker re-imports the module and the script
  spawns recursively on Windows.

## Requirements

Python 3.11. See `requirements.txt`. Verified 2026-10-16 with pandas 3.0.2.

## License

MIT — see `LICENSE`.

Documents retrieved through this tool remain subject to the World Bank's own terms of use:
<https://www.worldbank.org/en/about/legal/terms-and-conditions>. This repository contains code
only; no World Bank documents are redistributed here.
