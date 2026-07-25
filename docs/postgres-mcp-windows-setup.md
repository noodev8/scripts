# PostgreSQL MCP Server Setup for Windows

This guide shows how to properly configure the PostgreSQL MCP server for Claude Code on Windows.

## Configuration

Add the following configuration to your `.claude.json` file in the project-specific section:

```json
{
  "mcpServers": {
    "postgres": {
      "command": "cmd",
      "args": [
        "/c",
        "npx",
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://brookfield_prod_user:YOUR_PASSWORD@217.154.35.5:5432/brookfield_prod"
      ]
    }
  }
}
```

## Example Configuration

```json
{
  "mcpServers": {
    "postgres": {
      "command": "cmd",
      "args": [
        "/c",
        "npx",
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://myuser:mypassword@localhost:5432/mydatabase"
      ]
    }
  }
}
```

## Important Notes for Windows

- **Always use `"command": "cmd"`** - Never use `"command": "npx"` directly on Windows
- **First argument must be `"/c"`** - This tells cmd to execute the command and exit
- **No need for `"type": "stdio"` or `"env": {}`** - These are optional and not required

## Common Mistakes

❌ **Wrong (will cause warnings):**
```json
{
  "postgres": {
    "type": "stdio",
    "command": "npx",
    "args": [
      "-y",
      "@modelcontextprotocol/server-postgres",
      "connection-string"
    ],
    "env": {}
  }
}
```

✅ **Correct:**
```json
{
  "postgres": {
    "command": "cmd",
    "args": [
      "/c",
      "npx",
      "-y",
      "@modelcontextprotocol/server-postgres",
      "connection-string"
    ]
  }
}
```

## Connection String Format

```
postgresql://username:password@host:port/database
```

For your setup:
- `username`: brookfield_prod_user
- `password`: Replace YOUR_PASSWORD with actual password
- `host`: 217.154.35.5
- `port`: 5432
- `database`: brookfield_prod

## Verification

After adding the configuration, run `/doctor` in Claude Code to verify the setup is correct. You should see no warnings about the PostgreSQL MCP server.