# PowerBuilder PBL Files & Git

## The Problem

PowerBuilder rewrites PBL file internals (timestamps, page ordering) every time you open the IDE, even if you don't change any code. This makes `git status` show every PBL as modified, cluttering commits with meaningless changes.

## The Solution

PBL files are marked as "assume-unchanged" in git. This means:

- **Git ignores local changes** to PBL files — opening PowerBuilder won't dirty your git status
- **The files stay in the repo** — both machines can pull them
- **You control when to commit** — turn tracking on only when you've made real code changes

## Day-to-Day Workflow

1. `git pull` to get latest
2. Open PowerBuilder, run your app, close it
3. `git status` stays clean — nothing to do

## When You Make Real Code Changes

1. Run `bash powerbuilder/track.sh` — turns tracking back on
2. `git add powerbuilder/` — stage your changes
3. `git commit -m "your message"` and `git push`
4. Run `bash powerbuilder/untrack.sh` — turns tracking back off

## Setting Up a New Machine

After cloning the repo, run `untrack.sh` once to mark the PBL files as assume-unchanged:

```
bash powerbuilder/untrack.sh
```

This only needs to be done once per machine — the setting is local to each git repo clone.
