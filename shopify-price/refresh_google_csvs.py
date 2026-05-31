"""Move fresh Google Merchant CSVs from Downloads into shopify-price/.

Scans both machines' Downloads folders, moves any matching CSV into
shopify-price/, and deletes any older same-type CSV already there so we
only keep the latest of each kind.

Three file types are recognised:
- "Your most popular products with price benchmarks_*.csv"  (benchmark)
- "Sale price suggestions with highest performance impact_*.csv"  (sale price)
- "adcost30.csv"  (Google Ads 30-day per-item performance: impr/clicks/cost/conv)

The first two are timestamped Merchant Center exports — the newest of each is
kept. adcost30.csv is a fixed-name Google Ads export and is OPTIONAL: the user
drops a fresh copy in Downloads only sometimes. When present it overwrites the
existing copy; when absent the script just skips it (no error). Its `Item ID`
column joins to `skumap.googleid` (lowercase, leading zeros stripped) — NOT to
groupid. A SKU/size absent from the report had zero ad activity in the window:
treat as zero, not as missing data.
"""
import os
import shutil
import glob

DOWNLOAD_DIRS = [
    r"C:\Users\aandr\Downloads",
    r"C:\Users\UserPC\Downloads",
]
DEST = os.path.dirname(os.path.abspath(__file__))

PREFIXES = [
    "Your most popular products with price benchmarks_",
    "Sale price suggestions with highest performance impact_",
]

# Fixed-name exports (not timestamped). Optional — skipped silently if absent.
EXACT_FILES = [
    "adcost30.csv",
]


def latest_in(directory, prefix):
    """Return the newest matching file in `directory`, or None."""
    matches = glob.glob(os.path.join(directory, prefix + "*.csv"))
    if not matches:
        return None
    return max(matches, key=os.path.getmtime)


def main():
    moved = []
    for prefix in PREFIXES:
        # Find newest candidate across both Downloads folders
        candidates = []
        for d in DOWNLOAD_DIRS:
            if not os.path.isdir(d):
                continue
            f = latest_in(d, prefix)
            if f:
                candidates.append(f)
        if not candidates:
            continue
        src = max(candidates, key=os.path.getmtime)

        # If an existing dest copy is newer or same, skip
        existing = latest_in(DEST, prefix)
        if existing and os.path.getmtime(existing) >= os.path.getmtime(src):
            continue

        dest_path = os.path.join(DEST, os.path.basename(src))

        # Remove old same-type files in dest (only keep latest)
        for old in glob.glob(os.path.join(DEST, prefix + "*.csv")):
            if os.path.abspath(old) != os.path.abspath(dest_path):
                os.remove(old)

        shutil.move(src, dest_path)
        moved.append((src, dest_path))

    # Fixed-name exports: move newest match across Downloads, overwriting dest.
    for name in EXACT_FILES:
        candidates = [os.path.join(d, name) for d in DOWNLOAD_DIRS
                      if os.path.isfile(os.path.join(d, name))]
        if not candidates:
            continue
        src = max(candidates, key=os.path.getmtime)

        existing = os.path.join(DEST, name)
        # Skip if the dest copy is already as new as the Download.
        if os.path.isfile(existing) and os.path.getmtime(existing) >= os.path.getmtime(src):
            continue
        if os.path.isfile(existing):
            os.remove(existing)
        shutil.move(src, existing)
        moved.append((src, existing))

    if not moved:
        print("Nothing fresh in Downloads.")
        return
    for src, dst in moved:
        print(f"Moved: {src}")
        print(f"   -> {dst}")


if __name__ == "__main__":
    main()
