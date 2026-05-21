"""Move fresh Google Merchant CSVs from Downloads into shopify-price/.

Scans both machines' Downloads folders, moves any matching CSV into
shopify-price/, and deletes any older same-type CSV already there so we
only keep the latest of each kind.

Two file types are recognised:
- "Your most popular products with price benchmarks_*.csv"  (benchmark)
- "Sale price suggestions with highest performance impact_*.csv"  (sale price)
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

    if not moved:
        print("Nothing fresh in Downloads.")
        return
    for src, dst in moved:
        print(f"Moved: {src}")
        print(f"   -> {dst}")


if __name__ == "__main__":
    main()
