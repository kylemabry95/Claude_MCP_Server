
# This repository is a MCP for GitHub which allows Claude Desktop to perform various actions related to Pull Requests


Add the following code to the `claude_desktop_config.json`
```
{
    "mcpServers": {
        "git-hub-server": {
            "command": "python3.11",
            "args": [
                "Users/kylemabry/Documents/MCP_Practice/main.py"
            ]
        }
    }
}
```

There is no need to locally run `main.py` - Claude will run this code in the background once it starts.