# Klaviyo MCP Setup for Claude Code

## What it does
Connects Claude Code directly to Klaviyo so it can pull campaign results, segments, and subscriber data without copy-pasting.

## Prerequisites
1. A Klaviyo **Private API Key** (Settings > Account > API Keys > Create Private API Key)
2. `uv` installed (`pip install uv`)
3. The API key stored in `.env` as `KLAVYIO=pk_your_key_here`

## Setup Steps

1. Add the key to `.env` if not already there:
   ```
   KLAVYIO=pk_your_key_here
   ```

2. Create `.mcp.json` in the project root with:
   ```json
   {
     "mcpServers": {
       "klaviyo": {
         "command": "uvx",
         "args": ["klaviyo-mcp-server@latest"],
         "env": {
           "PRIVATE_API_KEY": "YOUR_PRIVATE_API_KEY_HERE",
           "READ_ONLY": "true",
           "ALLOW_USER_GENERATED_CONTENT": "false"
         }
       }
     }
   }
   ```

3. Make sure `.mcp.json` is in `.gitignore` (it contains your API key)

4. Restart Claude Code

## Troubleshooting (2026-03-28)

The MCP config in `.mcp.json` and `.claude/settings.local.json` is correct and verified working.
`uvx klaviyo-mcp-server@latest` runs fine — installs 106 packages and starts on stdio transport.

If Klaviyo tools don't appear after restart:
1. The `@latest` tag causes a slow first-run install. Try pinning the version in `.mcp.json` args, e.g. `"klaviyo-mcp-server==X.Y.Z"` to speed up startup.
2. Run `uvx klaviyo-mcp-server@latest --help` manually in terminal to confirm it works.
3. Use `ToolSearch` with query `klaviyo` to check if tools loaded — look for `mcp__klaviyo__*` tools.
4. If tools still missing, the server may be timing out during the MCP handshake on startup.

## Troubleshooting (2026-04-10) — fakeredis / pydocket import error

Symptom: `claude mcp list` shows `klaviyo: ... ✗ Failed to connect`. Running `uvx klaviyo-mcp-server@latest --help` crashes with:
```
ImportError: cannot import name 'FakeConnection' from 'fakeredis.aioredis'
```
Cause: newer `fakeredis` (≥2.30) renamed `FakeConnection` → `FakeRedisConnection`, but `pydocket 0.18.2` (pulled in by `fastmcp 2.14.6`) still imports the old name.

Fix: pin an older fakeredis via uvx `--with` in `.mcp.json` args:
```json
"args": ["--with", "fakeredis<2.30", "klaviyo-mcp-server@latest"]
```
Then restart Claude Code. Verify with `claude mcp list` — klaviyo should show `✓ Connected`.
Revisit once `pydocket` / `fastmcp` publish a release compatible with fakeredis ≥2.30 — the pin can then be removed.

## Notes
- `READ_ONLY: true` means Claude can view but not modify anything in Klaviyo
- Change to `false` later if you want Claude to create campaigns/segments
- The official server is `klaviyo-mcp-server` via `uvx` (Klaviyo's own package)
