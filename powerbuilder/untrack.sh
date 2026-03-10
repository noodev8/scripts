#!/bin/bash
# Turn OFF git tracking for PBL files (run this after committing your changes)
cd "$(dirname "$0")/.."
git update-index --assume-unchanged powerbuilder/*.pbl
echo "PBL files are now IGNORED by git (assume-unchanged)."
echo "PowerBuilder can open/run without dirtying git status."
