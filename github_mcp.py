import arxiv
import json
import os
import requests
from typing import List
from fastmcp import FastMCP
from dotenv import load_dotenv
from fastmcp.prompts.prompt import Message, PromptMessage, TextContent


load_dotenv()

mcp = FastMCP("Demo Github")
github_pat = os.getenv("PAT")  


@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def list_all_members_in_organization(org: str) -> List[str]:
    """
    List all members in a GitHub organization.
    
    Args:
        org: The name of the GitHub organization
    Returns:
        List of member usernames
    """
    url = f"https://api.github.com/orgs/{org}/members"
    headers = {"Authorization": f"token {github_pat}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        members = response.json()
        return [member['login'] for member in members]
    else:
        raise Exception(f"Failed to fetch members: {response.status_code} {response.text}")

@mcp.tool()
def list_issues(org: str = None) -> List[str]:
    """List all issues in a GitHub organization or globally.
    Args:
        org: The name of the GitHub organization
    Returns:
        List of issue titles
    """
    if org is None:
        url = "https://api.github.com/issues"
    else:
        url = f"https://api.github.com/orgs/{org}/issues"

    headers = {"Authorization": f"token {github_pat}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        issues = response.json()
        return [issue['title'] for issue in issues if 'title' in issue]
    else:
        raise Exception(f"Failed to fetch issues: {response.status_code} {response.text}")
    
@mcp.resource("resource://greeting")
def get_config() -> dict:
    """Provides application configuration as JSON."""
    return {
        "theme": "dark",
        "version": "1.2.0",
        "features": ["tools", "resources"],
    }

@mcp.prompt
def generate_code_request(language: str, task_description: str) -> PromptMessage:
    """Generates a user message requesting code generation."""
    content = f"Write a {language} function that performs the following task: {task_description}" 
    return PromptMessage(role="user", content=TextContent(type="text", text=content))



if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')