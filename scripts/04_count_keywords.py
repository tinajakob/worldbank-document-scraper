import pandas as pd
import os
import time
import re
import string
import english_words
import time


from english_words import get_english_words_set

# Paths come from config.py at the repository root (set WB_DATA_DIR to relocate the data).
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from config import LIST_DIR, DOCS_DIR, OUT_DIR

all_words = {word.lower() for word in get_english_words_set(['web2'])}
#print(len(all_words))

pd.options.display.max_columns = 6


in_dir = LIST_DIR
files_dir = DOCS_DIR
out_dir = OUT_DIR
os.chdir(in_dir)

# NOTE: this module used to read project_list.csv (hundreds of MB) here into a frame
# that was never used again. Each pool worker re-imports this module, so that cost
# seconds and a lot of memory per worker. 06_finalize_dataset.py is where the project
# list is actually joined onto these counts.

# Change to file directory
os.chdir(files_dir)

# Inspect project list
# df.columns
# df["year"].value_counts().sort_index().plot()
# plt.show()
# df["year"].value_counts().sort_index().head(50).plot()
# plt.show()
#
# df.lang.value_counts(normalize=True)
# df.majdocty.value_counts(normalize=True)  # Not relevant
# df.loc[df.year > 2010, "count"].value_counts(normalize=True).head(20)
# df.admreg.value_counts(normalize=True).head(10)
# df.majtheme.value_counts(normalize=True).head(10)
# df.projectid.isna().mean()
# df.projectid.nunique()

# test document search
filename = "doc_1947_18171749.txt"

# Define search terms
searches = {
    "development": "development",
    "state": "state",
    "national": "national",
    "local": "local",
    "community": "communit(y|ies)",
    "gender": "gender",
    "education": "education",
    "women": "wom(a|e)n",
    "infrastructure": "infrastructure",
    "microfinance": "micro ?(finance|credit)",
    "equality": "equal",
    "communitydriven": "community ?driven",
    "communitybased": "community ?based",
    "communitydrivendevelopment": "community ?driven development",
    "communitybaseddevelopment": "community ?based development",
    "localdevelopment": "local [a-z]* ?development",
    "participatorydevelopment": "participatory [a-z]* ?development",
    "cdd_all": "(community ?(driven|based))|((participatory|local) [a-z]* ?development)",
    "bottomup": "bottom ?up",
    "empowerment": "empowerment",  # Additional terms added after this
    "counterpart": "counterpart ?(contribution|fund|financing)",
    "matching": "match(ing)? ?(grant|contribution|fund)",
    "co_finance": "co ?(financ|fund)|cost ?sharing",
    "local_contribution": "(local|community|communities|village|villages) ?(contribut|financ)",
    "capacity_building": "(capacity|capability) ?(building|strengthening)|(build(ing)?|strengthen(ing)?) ?([a-z]+)? ?(capacit|capabilit)",
    "volunteer": "volunteer|voluntary|labor contribution|contribute labor|unpaid|sweat equity",
    "local_capacity": "(local|village|community) ?(capacity|capabilit)",
    "local_governance": "(local|village|community) ?governance",
    "training": "(training)|(facilitation)",
    "facilitator": "facilitator",
    "facilitate": "facilitate",
    "workshop": "workshop",
    "awareness": "awareness",
    "collective_action": "collective action",
    "sustainability": "sustainab",
    "public_goods": "public good",
    "participatory": "participatory"  # Moved this to the end so that code does not need to me adapted
}


#wb = "community-driven development and local development or community based economic development local economic development "


# Function to clean string
def get_counts(wb_string, searches, all_words=all_words):
    # ORIGINAL LINE AS USED FOR THE SHIPPED DATA (kept for reference -- do not delete):
    #     wb_string = wb_string.lower().replace("(\n)|(\t)|(\xa0)", " ")
    # str.replace is literal, so that call searched for the 18-character string
    # "(\n)|(\t)|(\xa0)" and matched nothing. The re.sub on the next line then DELETED
    # newlines instead of turning them into spaces, welding the last word of each line onto
    # the first word of the next ("community\ndriven" -> "communitydriven"). Measured over
    # 400-500 documents: ~12% of word boundaries lost, so nwords/ncwords are understated by
    # ~12%, and multi-word patterns with a MANDATORY internal space are undercounted
    # (e.g. "community ?driven development": 25 vs 29 hits).
    #
    # IMPORTANT: the keyword shares reported in the paper are almost unaffected, because the
    # patterns behind them use OPTIONAL space matching ("community ?based",
    # "(capacity|capability) ?(building|...)") which still matches welded text, or are single
    # tokens ("sustainab", "state"). Measured document shares, shipped vs fixed:
    #     capacity_building 38.2% -> 37.0% | sustainability 41.0% -> 41.0%
    #     communitybased     8.2% ->  8.2% | cdd_all        14.6% -> 14.4%
    #     state             58.4% -> 58.4% | counterpart/matching/co_finance unchanged
    #
    # The line below is the corrected version. As of 2026-10-15 it has NOT been run: the
    # shipped keyword_finds.csv / 99_world_bank_reports.csv still come from the original line
    # above (a re-run means re-reading 343,177 files / 70 GB, ~4 h, for sub-1pp changes).
    # See 04_Data_Cleaning/CHANGELOG_2026-10-15_cleaning-corrections.md.
    # Collapse all whitespace to single spaces FIRST, then strip unwanted characters.
    wb_string = re.sub(r"\s+", " ", wb_string.lower())
    wb_string = re.sub(r"(@\[A-Za-z]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^rt|http.+?", "", wb_string)
    wb_string = re.sub('[0-9]', '', wb_string).strip()
    wb_string = re.sub(' +', ' ', wb_string)

    # Get length
    nchar = len(wb_string)
    if nchar > 0:

        nwords = len(wb_string.split(" "))
        newords = len([word for word in wb_string.split(" ") if word in all_words])
        stats = [nchar, nwords, newords]

        # Define search patterns
        finds = []
        for skey, svalue in searches.items():
            finds.append(len(re.findall(svalue, wb_string)))
        return stats + finds

    else:
        return [0]*(3+len(searches))

# complete function
def read_and_count(filename, searches, all_words=all_words):

    try:
        try:
            with open(filename, encoding="utf8") as f:
                wb = f.read()
        except:
            with open(filename, encoding="latin") as f:
                wb = f.read()
        wb_counts = get_counts(wb, searches, all_words=all_words)
        wb_counts = [filename] + wb_counts
    except:
        print(filename)
    return wb_counts



# Get counts for all files, one worker process per core.
# NOTE: the work is CPU-bound in `re`, not I/O-bound, so threads gain nothing -- the GIL
# serialises them. Measured on the full corpus (66.8 GB, 343,177 documents): one core gives
# 14-19 hours, ten processes bring it to about an hour. A process pool needs the
# `if __name__ == "__main__"` guard below, because on Windows every worker re-imports this
# module and would otherwise spawn recursively.
N_WORKERS = max(1, min(10, (os.cpu_count() or 2) - 2))
CHECKPOINT_EVERY = 20000


def _count_one(filename):
    """Pool target: a module-level function, so it can be pickled to the workers."""
    return read_and_count(filename, searches=searches)


if __name__ == "__main__":
    import multiprocessing as mp

    # Listed here rather than at module level: every pool worker re-imports this module, and
    # listing hundreds of thousands of filenames once per worker is pure overhead.
    all_files = os.listdir()
    print("%s documents found" % format(len(all_files), ","), flush=True)

    # Windows sleeps after an idle timeout even while busy, which would freeze a long run.
    # The request is released when this process exits. Closing a laptop lid still sleeps.
    if os.name == "nt":
        try:
            import ctypes
            ES_CONTINUOUS, ES_SYSTEM_REQUIRED = 0x80000000, 0x00000001
            ctypes.windll.kernel32.SetThreadExecutionState(
                ES_CONTINUOUS | ES_SYSTEM_REQUIRED)
            print("keeping the machine awake for the duration", flush=True)
        except Exception as exc:
            print("could not request a wake lock (%s)" % exc, flush=True)

    columns = ["filename", "nchar", "nwords", "ncwords"] + list(searches.keys())
    partial_path = os.path.join(out_dir, "keyword_finds_partial.csv")
    starttime = time.time()
    all_counts = []

    print("%s documents, %d worker processes" % (format(len(all_files), ","), N_WORKERS),
          flush=True)
    with mp.Pool(N_WORKERS) as pool:
        for i, row in enumerate(pool.imap_unordered(_count_one, all_files, chunksize=64), 1):
            all_counts.append(row)
            if i % 2000 == 0:
                el = time.time() - starttime
                rate = i / el
                print("  %s/%s  %4.1f%%  %.0f docs/s  elapsed %.0f min  eta %.0f min"
                      % (format(i, ","), format(len(all_files), ","),
                         100.0 * i / len(all_files), rate, el / 60,
                         (len(all_files) - i) / rate / 60), flush=True)
            if i % CHECKPOINT_EVERY == 0:
                pd.DataFrame.from_records(all_counts, columns=columns).to_csv(
                    partial_path, index=False)
                print("  checkpoint written at %s documents" % format(i, ","), flush=True)

    duration = (time.time() - starttime) / 60
    print("done in %.1f min" % duration, flush=True)


    # Convert to dataframe
    search_df = pd.DataFrame.from_records(all_counts,
                              columns=["filename", "nchar", "nwords", "ncwords"] + list(searches.keys()))

    # Drop cases with "PDF not found" error message or 0 characters
    search_df = search_df.loc[~((search_df.nchar == 76) & (search_df.nwords == 2) & (search_df.ncwords == 0)), :]
    search_df = search_df[search_df.nchar > 0]


    # Inspect dataframe
    search_df.nchar.describe()
    (search_df.nchar == 0).mean()

    search_df.nwords.describe()
    search_df.ncwords.describe()
    (search_df.cdd_all == search_df.communitydriven + search_df.communitybased +
     search_df.participatorydevelopment + search_df.localdevelopment).mean()  # Should be 1

    for col in search_df.loc[:, "development":"participatory"].columns:
        print(col)
        print(search_df[col].value_counts(normalize=True).head(5))

    # Save csv
    search_df.to_csv(os.path.join(out_dir, "keyword_finds.csv"), index=False)

