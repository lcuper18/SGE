# MCP Server Configuration

## GitHub MCP Server

The Model Context Protocol (MCP) server for GitHub has been installed and configured.

### Installation Details

**Installed:** February 13, 2026

**Components:**
- Node.js: v24.13.1
- npm: v11.8.0
- MCP Server: @modelcontextprotocol/server-github (global installation)
- Server Binary: `/usr/bin/mcp-server-github`

### Configuration

**Location:** `~/.config/Code/User/globalStorage/github.copilot-chat/mcpServers.json`

```json
{
  "mcpServers": {
    "github": {
      "command": "mcp-server-github",
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_************************************"
      }
    }
  }
}
```

### Capabilities

The GitHub MCP server enables GitHub Copilot Chat to:
- Search repositories and code on GitHub
- Create, read, and update GitHub Issues
- Manage Pull Requests
- Navigate GitHub repository structure
- Access repository metadata
- Perform GitHub API operations directly from chat

### Usage

After reloading VS Code, the MCP server runs automatically when using GitHub Copilot Chat.

**Activation:**
1. Open GitHub Copilot Chat (Ctrl+Alt+I)
2. Use natural language to interact with GitHub
3. Example: "Create an issue for Epic 1: Authentication"

### Troubleshooting

**If the server doesn't start:**
1. Check that Node.js is installed: `node --version`
2. Verify server binary exists: `which mcp-server-github`
3. Check VS Code Developer Tools (Help > Toggle Developer Tools) for errors
4. Ensure the GitHub token has correct scopes: repo, project, workflow, read:org

**Reload VS Code:** Ctrl+Shift+P > "Developer: Reload Window"

### Token Permissions

The configured GitHub Personal Access Token has these scopes:
- `admin:org` - Organization administration
- `delete:packages` - Delete packages
- `project` - Full control of projects
- `repo` - Full control of repositories
- `workflow` - Update GitHub Actions workflows
- `write:packages` - Write packages

### Security Note

The GitHub token is stored in the VS Code configuration directory. Ensure proper file permissions are set:
```bash
chmod 600 ~/.config/Code/User/globalStorage/github.copilot-chat/mcpServers.json
```

### Maintenance

**Updating the Server:**
```bash
sudo npm update -g @modelcontextprotocol/server-github
```

**Uninstalling:**
```bash
sudo npm uninstall -g @modelcontextprotocol/server-github
rm ~/.config/Code/User/globalStorage/github.copilot-chat/mcpServers.json
```

### Alternative MCP Servers

Other useful MCP servers for development:
- `@modelcontextprotocol/server-filesystem` - Local file operations
- `@modelcontextprotocol/server-postgres` - PostgreSQL database access
- `@modelcontextprotocol/server-git` - Git operations

---

**Note:** The package `@modelcontextprotocol/server-github` is marked as deprecated. This may indicate a migration to a newer package in the future. Monitor the [Model Context Protocol repository](https://github.com/modelcontextprotocol) for updates.
