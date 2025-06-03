# GitHub Pull Request MCP Server
# This server provides tools to list pull requests and get their content
# using the Model Context Protocol (MCP) with GitHub's API.
# It uses the FastMCP framework for easy server creation and management.
import json
import os
import sys
import base64
from typing import List, Dict, Any, Optional
import httpx
import requests
import urllib3
from mcp.server.fastmcp import FastMCP
from git_hub_pr_fetcher import GitHubPRFetcher

mcp = FastMCP("GitHub PR Server")

@mcp.tool()
def list_pull_requests(repo: str, owner: str) -> str:
    """List all pull requests for a GitHub repository.
    
    Args:
        repo: Repository name
        owner: Repository owner
    """
    try:
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        response = httpx.get(url)
        response.raise_for_status()

        prs = response.json()
        result = []
        for pr in prs:
            result.append({
                "number": pr["number"],
                "title": pr["title"],
                "state": pr["state"],
                "author": pr["user"]["login"],
                "url": pr["html_url"]
            })
        return json.dumps(result, indent=2)
    except Exception as e:
        print('There was an error in the code: ' +  str(e), file=sys.stderr)
        return f"Error: {str(e)}"


#Disable SSL warnings for when we bypass verification
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

@mcp.tool()
def get_specified_pr(owner: str, repo: str, pr_number: int = 0) -> Dict[str, Any]:
    """
    Convenience function to get the latest PR from a repository.
    
    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: Pull request number (optional, defaults to latest)
        
    Returns:
        Dictionary with latest PR details
    """
    # Get access token from environment variable or use default
    token = os.getenv("GITHUB_TOKEN")
    fetcher = GitHubPRFetcher(token) # type: ignore

    # First get the list of PRs
    pr_list = fetcher.list_pull_requests(owner, repo)

    if not pr_list['success'] or not pr_list['data']:
        return pr_list

    # Get the latest PR (first in the sorted list)
    latest_pr_number = pr_list['data'][pr_number-1]['number']

    # Fetch detailed information about the latest PR
    pr_details = fetcher.fetch_pr_details(owner, repo, latest_pr_number)

    if pr_details['success']:
        return {
            'success': True,
            'latest_pr': pr_details['data'],
            'method_used': pr_details['method'],
            'all_prs': pr_list['data']
        }
    else:
        return pr_details

@mcp.tool()
def get_repository_issues(owner: str, repo: str, state: str = "open", per_page: int = 30) -> List[Dict[str, Any]]:
    """
    Get issues from a GitHub repository.
    
    Args:
        owner: Repository owner username
        repo: Repository name
        state: Issue state ('open', 'closed', 'all')
        per_page: Number of issues per page (max 100)
    
    Returns:
        List of issue dictionaries
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    params = {"state": state, "per_page": min(per_page, 100)}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": f"Failed to fetch issues: {str(e)}"} # type: ignore

@mcp.tool()
def get_repository_readme(owner: str, repo: str, branch: str = "main") -> Optional[str]:
    """
    Get README file content from a GitHub repository.
    
    Args:
        owner: Repository owner username
        repo: Repository name
        branch: Branch name (defaults to 'main')
        
    Returns:
        README content as string, or None if not found
    """
    # Try common README filenames 
    filenames = ["README.md", "README.rst", "README.txt", "README"]

    for filename in filenames:
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{filename}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.text
        except requests.RequestException:
            continue

@mcp.tool()
def get_repository_file(owner: str, repo: str, file_path: str, branch: str = "main") -> Optional[str]:
    """
    MCP function to access code files from a GitHub repository.
    
    Args:
        owner: Repository owner username
        repo: Repository name
        file_path: Path to the file in the repository
        branch: Branch name (defaults to 'main')
        
    Returns:
        File content as string, or None if not found
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    params = {"ref": branch}

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("encoding") == "base64":
                return base64.b64decode(data["content"]).decode('utf-8')
        return None
    except Exception:
        return None

if __name__ == "__main__":
    mcp.run()
