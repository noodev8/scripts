# pb-deploy — PowerBuilder release packaging

Packages a fresh PowerBuilder build into `BrookfieldUpdate.zip` and publishes it
as a new release on [brookfielduser1/BrookfieldApp](https://github.com/brookfielduser1/BrookfieldApp/releases).

## Run it

Compile in PowerBuilder first, then double-click one of these (or run it from
cmd, from any folder):

| Front door | Does |
|---|---|
| `release.bat` | **The full deploy** — builds the zip, then publishes the GitHub release |
| `build_update.bat` | Builds the zip only, no upload |

Both anchor on their own location, so the working directory doesn't matter, and
both pause at the end so you can read the result. The `.ps1` files alongside
hold the logic (`env_util.ps1` holds the bits both share) — don't invoke those
directly, cmd hands `.ps1` files to the default editor rather than running them.

### What `release.bat` does

1. Collects `brookfieldcomfort.exe` + every `*.pbd` from the compile output folder
   (`My Drive (noodev8@gmail.com)\Business\Brookfield Comfort\Powerbuilder`).
2. Checks each PBD against its matching PBL and **stops** if any PBD is older.
3. Writes `BrookfieldUpdate.zip` into that same folder.
4. Reads the existing releases, works out the next tag, and shows you what it's
   about to publish.
5. **Waits for you to confirm (y/N)**, then creates the release and uploads the zip.
6. Reads the release back from GitHub and prints a pass/fail table.

## How you know it worked

You don't need to go and check the releases page. After uploading, the script
re-reads the release **from GitHub** — not from the upload response — and
confirms the release exists, isn't a draft, has the asset attached, that the
asset finished uploading, and that its size matches the local zip byte for byte.

- All pass → `v2.18 published and verified.` plus the URL, exit code 0.
- Anything fails → `PUBLISH INCOMPLETE`, which line failed, the URL to go and
  look at, and exit code 1.

Checking GitHub yourself is then a belt-and-braces confirmation, not the test.

## Running it on the other machine

The scripts are machine-agnostic — nothing is hardcoded to the laptop. On a new
machine they work out both folders themselves:

The **PowerBuilder output folder** is searched for under your user profile and
on every drive letter, as `<root>\My Drive [(noodev8@gmail.com)]\Business\
Brookfield Comfort\Powerbuilder`. A candidate only counts if
`brookfieldcomfort.exe` is actually in it, so a stale or empty copy of the tree
won't match. It's the only machine-dependent path — the zip is built and
uploaded from there, nothing else on disk is touched.

So try it with no `.env` change first. If auto-detection misses, the script
stops and tells you exactly what to add:

```
PB_SOURCE_DIR=G:\My Drive\Business\Brookfield Comfort\Powerbuilder
```

Optional, and overrides auto-detection when present.

**`.env` is gitignored, so `git pull` won't bring it across.** Each machine
needs its own copy, and `GITHUB_TOKEN` must be in the one on the machine you're
publishing from — the same token string works on both.

## One-time setup: the token

Publishing needs a GitHub token in the repo-root `.env`. Without it the script
stops harmlessly and prints these instructions.

1. Sign in to GitHub as **brookfielduser1** (not your usual `noodev8` account).
2. Go to Settings → Developer settings →
   [Fine-grained personal access tokens](https://github.com/settings/personal-access-tokens)
   → Generate new token.
3. Repository access: **Only select repositories** → `BrookfieldApp`.
   Permissions: **Contents = Read and write**.
4. Add the token to `C:\scripts\.env` as its own line:

```
GITHUB_TOKEN=github_pat_...
```

`.env` is gitignored, so the token never reaches the repo. Note fine-grained
tokens expire — when publishing starts failing with an auth error, regenerate
and replace this line.

## Versioning

Tags follow the existing convention: `v2.14`, `v2.15`, `v2.16` — major, then a
**zero-padded two-digit** minor. The script reads the latest release and adds
one to the minor, so after `v2.16` it publishes `v2.17`. Release title matches
the tag, body is left empty, exactly as the previous releases were done by hand.

To override: `release.bat -Version v3.00`. You must do this manually once the
minor reaches 99, since a major bump is a judgement call — the script refuses
rather than guessing.

## Flags

Pass these to `release.bat` (they reach the publish step) or `build_update.bat`:

| Flag | Purpose |
|---|---|
| `-Version v3.00` | Override the auto-computed tag |
| `-Yes` | Skip the confirm prompt — unattended publish |
| `-Force` | Build anyway when the staleness check fails |
| `-Source <path>` | Point at a different compile output folder, this run only |
| `-Zip <path>` | Publish a specific zip instead of the freshly built one |

## Gotchas

**The staleness check is the point of the build script.** PowerBuilder will
happily leave a PBD untouched if that library failed to regenerate, and the zip
then ships last version's code for it — silently, only surfacing on a client PC.
If the script reports a library as behind, go back and rebuild it rather than
reaching for `-Force`.

**The asset name is fixed at `BrookfieldUpdate.zip`** and must stay that way.
Every previous release uses exactly that name, so anything fetching
`/releases/latest/download/BrookfieldUpdate.zip` keeps working. Don't add a
version number to the filename.

**PBLs are not shipped.** The last hand-built zip contained a stray
`birkenstock.pbl` (~1 MB); it was accidental and clients don't need it. Payload
is exe + PBDs only. The runtime DLLs (`pbvm100.dll` etc.) also aren't in the
zip — they're install-time files that don't change between versions.

**A failed asset upload deletes its own release.** Otherwise you'd be left with
a release that looks valid but has nothing to download, which a client would
fetch and fail on. If the cleanup itself fails, the script prints the release
URL so you can delete it by hand.

**The zip is built via a temp folder** and moved into place, so a failure
part-way through can't leave a half-written `BrookfieldUpdate.zip` in the Drive
folder where Drive would sync it out. The temp folder is deleted whether the
build succeeds or fails.

**Nothing accumulates on disk.** Exactly one zip is kept — the
`BrookfieldUpdate.zip` in the PowerBuilder folder — and it's overwritten on
every build. Old versions live on GitHub as releases, which is the point. The
script never copies the zip anywhere else.
