
# Model Context Protocol (MCP) Server for GitHub using Claude Desktop


Add the following code to the `./Library/Application\ Support/Claude/claude_desktop_config.json`
```
{
    "mcpServers": {
        "git-hub-server": {
            "command": "python3.11",
            "args": [
                "Users/{your_username}/Documents/MCP_Practice/main.py"
            ]
        }
    }
}
```

There is no need to locally run `main.py` - Claude will run this code in the background once it starts.

# GitHub PR Server

A Model Context Protocol (MCP) server that provides tools for interacting with GitHub repositories. This server enables you to retrieve pull requests, issues, README files, and other repository content through a standardized interface.

## Features

### Pull Request Management
- **List Pull Requests**: Get all pull requests for a repository
- **Get Specific PR**: Retrieve detailed information about a specific pull request or the latest PR
- **PR Details**: Access comprehensive PR information including changes, commits, and metadata

### Repository Content Access
- **README Retrieval**: Automatically fetch README files (supports .md, .rst, .txt formats)
- **File Content**: Access any file content from a repository
- **Issue Management**: Retrieve repository issues with filtering options

### Issue Tracking
- **List Issues**: Get repository issues with state filtering (open/closed/all)
- **Pagination**: Control the number of issues returned per request

## Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `list_pull_requests` | List all pull requests for a repository | `owner`, `repo` |
| `get_specified_pr` | Get detailed information about a specific PR | `owner`, `repo`, `pr_number` (optional) |
| `get_repository_issues` | Fetch repository issues with filtering | `owner`, `repo`, `state`, `per_page` |
| `get_repository_readme` | Get README file content | `owner`, `repo`, `branch` |
| `get_repository_file` | Access any file from the repository | `owner`, `repo`, `file_path`, `branch` |

## Setup

### Prerequisites
- Python 3.11.9
- Required packages: `fastmcp`, `httpx`, `requests`, `urllib3`, `mcp`, `typing`

### Installation

```bash
pip install fastmcp httpx requests urllib3 mcp typing
```

### Configuration

#### GitHub Token (Optional but Recommended)
Set your GitHub personal access token as an environment variable for higher rate limits:

```bash
export GITHUB_TOKEN=your_github_token_here
```

Without a token, you'll be limited to GitHub's unauthenticated API rate limits.

## Usage Examples

### List Pull Requests
```python
# Get all pull requests for a repository
prs = list_pull_requests("owner_name", "repo_name")
```

### Get Specific Pull Request
```python
# Get the latest pull request
latest_pr = get_specified_pr("owner_name", "repo_name")

# Get a specific pull request by number
specific_pr = get_specified_pr("owner_name", "repo_name", pr_number=5)
```

### Fetch Repository Issues
```python
# Get open issues (default)
issues = get_repository_issues("owner_name", "repo_name")

# Get closed issues
closed_issues = get_repository_issues("owner_name", "repo_name", state="closed")

# Get all issues with custom pagination
all_issues = get_repository_issues("owner_name", "repo_name", state="all", per_page=50)
```

### Access Repository Content
```python
# Get README content
readme = get_repository_readme("owner_name", "repo_name")

# Get specific file content
file_content = get_repository_file("owner_name", "repo_name", "src/main.py")

# Get file from specific branch
file_content = get_repository_file("owner_name", "repo_name", "config.json", branch="development")
```

## Error Handling

The server includes comprehensive error handling:
- Network timeouts and connection errors
- API rate limiting
- Invalid repository or file paths
- Authentication failures
- SSL certificate verification bypass (with warnings disabled)

## API Response Format

### Pull Request Response
```json
{
  "success": true,
  "latest_pr": {
    "number": 1,
    "title": "Feature implementation",
    "state": "open",
    "author": "username",
    "url": "https://github.com/owner/repo/pull/1",
    "created_at": "2025-06-02T14:05:28Z",
    "commits": 1,
    "additions": 42,
    "deletions": 4,
    "changed_files": 2
  },
  "method_used": "default_ssl",
  "all_prs": [...]
}
```

### Issues Response
```json
[
  {
    "number": 1,
    "title": "Bug report",
    "state": "open",
    "user": {"login": "username"},
    "created_at": "2025-06-01T10:00:00Z",
    "body": "Issue description..."
  }
]
```

## Security Notes

- SSL warnings are disabled for cases where certificate verification is bypassed
- GitHub tokens should be kept secure and not committed to version control
- The server respects GitHub's API rate limits
- File content is decoded from base64 when retrieved through the GitHub API

## Contributing

When contributing to this project:
1. Ensure all new tools follow the MCP tool decoration pattern
2. Include proper error handling and timeouts
3. Add appropriate type hints
4. Test with both authenticated and unauthenticated GitHub API access

## License

[Add your license information here]