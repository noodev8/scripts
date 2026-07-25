#!/usr/bin/env python3
"""
Catalogue checker -- keeps INDEX.md honest.

Report only. This script never moves, edits or deletes anything; it prints what
looks wrong and exits 1 so it can be wired into a check later.

Checks:
  1. Every script path in crontab.txt exists on disk.
  2. Every capability folder has a front-door .md.
  3. Every .py at root or in a capability folder is mentioned in INDEX.md.
  4. Nothing unexpected is sitting at root.

    python catalogue.py
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

# Folders that aren't capabilities and are never indexed.
SKIP_DIRS = {
    ".git", ".claude", ".idea", "__pycache__", "venv", ".venv",
    "logs", "archive_logs", "archive", "sandpit", "node_modules",
}

# Files allowed to live at root regardless of INDEX.md.
ALLOWED_ROOT_FILES = {
    "CLAUDE.md", "INDEX.md", "crontab.txt",
    "logging_utils.py", "catalogue.py",
    ".env", ".gitignore", ".gitattributes", ".mcp.json",
}

# Root file patterns that are credentials or config, not clutter.
ALLOWED_ROOT_PATTERNS = [
    re.compile(r"^.*\.json$"),      # service accounts, OAuth tokens
    re.compile(r"^\..+$"),          # any dotfile
]

# The VPS path prefix used in crontab.txt, mapped onto this checkout.
CRON_PREFIX = "/apps/scripts/"


def read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def capability_folders():
    """Top-level folders that should behave like capabilities."""
    out = []
    for name in sorted(os.listdir(ROOT)):
        full = os.path.join(ROOT, name)
        if os.path.isdir(full) and name not in SKIP_DIRS and not name.startswith("."):
            out.append(name)
    return out


def check_crontab_paths(problems):
    """Every script the crontab invokes must exist on disk."""
    crontab = os.path.join(ROOT, "crontab.txt")
    if not os.path.exists(crontab):
        problems.append(("crontab", "crontab.txt not found"))
        return 0

    seen = set()
    for line in read(crontab).splitlines():
        if line.strip().startswith("#"):
            continue
        for match in re.finditer(re.escape(CRON_PREFIX) + r"(\S+\.(?:py|sh))", line):
            seen.add(match.group(1))

    for rel in sorted(seen):
        if not os.path.exists(os.path.join(ROOT, rel.replace("/", os.sep))):
            problems.append(("crontab", f"{rel} is scheduled but not on disk"))
    return len(seen)


def check_front_doors(problems, folders):
    """Every capability folder needs a .md someone can open cold."""
    for folder in folders:
        full = os.path.join(ROOT, folder)
        has_md = any(f.lower().endswith(".md") for f in os.listdir(full)
                     if os.path.isfile(os.path.join(full, f)))
        if not has_md:
            problems.append(("front-door", f"{folder}/ has no .md"))


def folder_docs(folder):
    """All .md text inside a capability folder, concatenated."""
    chunks = []
    for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, folder)):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.lower().endswith(".md"):
                chunks.append(read(os.path.join(dirpath, name)))
    return "\n".join(chunks)


def check_indexed(problems, folders, index_text):
    """
    Every script should be documented somewhere a person would look.

    Two tiers, deliberately: INDEX.md carries the one-liner per capability, the
    folder's own .md carries the detail. A script inside a capability folder is
    covered by either -- requiring every one in INDEX.md would defeat the
    one-row-per-capability point of the index. Root scripts have no folder doc
    to fall back on, so they must be in INDEX.md.
    """
    count = 0

    for name in sorted(os.listdir(ROOT)):
        if os.path.isfile(os.path.join(ROOT, name)) and name.endswith((".py", ".sh")):
            if name == "catalogue.py":
                continue
            count += 1
            if name not in index_text:
                problems.append(("unindexed", f"{name} (root) is not in INDEX.md"))

    for folder in folders:
        docs = folder_docs(folder)
        for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, folder)):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for name in sorted(filenames):
                if not name.endswith(".py"):
                    continue
                count += 1
                rel = os.path.relpath(os.path.join(dirpath, name), ROOT).replace(os.sep, "/")
                if rel in index_text or name in index_text or name in docs:
                    continue
                problems.append(
                    ("undocumented", f"{rel} is in neither INDEX.md nor {folder}/*.md")
                )
    return count


def check_root_clutter(problems, index_text):
    """Root is for shared infrastructure and top-level docs, not working files."""
    for name in sorted(os.listdir(ROOT)):
        full = os.path.join(ROOT, name)
        if not os.path.isfile(full):
            continue
        if name in ALLOWED_ROOT_FILES:
            continue
        if any(p.match(name) for p in ALLOWED_ROOT_PATTERNS):
            continue
        # Live cron scripts still at root are fine while they're indexed.
        if name in index_text:
            continue
        problems.append(("root", f"{name} sits at root and isn't in INDEX.md"))


def main():
    index_path = os.path.join(ROOT, "INDEX.md")
    if not os.path.exists(index_path):
        print("INDEX.md not found -- nothing to check against.")
        return 1
    index_text = read(index_path)

    folders = capability_folders()
    problems = []

    cron_count = check_crontab_paths(problems)
    check_front_doors(problems, folders)
    script_count = check_indexed(problems, folders, index_text)
    check_root_clutter(problems, index_text)

    print(f"Checked {len(folders)} folders, {script_count} scripts, "
          f"{cron_count} crontab entries.\n")

    if not problems:
        print("All clear.")
        return 0

    current = None
    for kind, message in problems:
        if kind != current:
            print(f"[{kind}]")
            current = kind
        print(f"  {message}")

    print(f"\n{len(problems)} issue(s). Report only -- nothing was changed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
