#!/bin/bash
# Turn ON git tracking for PBL files (run this when you've made real code changes)
cd "$(dirname "$0")/.."
git update-index --no-assume-unchanged powerbuilder/*.pbl
echo "PBL files are now TRACKED by git."
echo "Run 'git add powerbuilder/' then commit and push as normal."
echo "When done, run untrack.sh to turn tracking back off."
