#!/usr/bin/env python3
import os
import sys
from datetime import datetime
import requests
import urllib.parse
import argparse
import re


def load_github_token():
    """Load GitHub token from ../.env (relative to this file), then environment."""
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')

    if os.path.exists(env_path):
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for raw_line in f:
                    line = raw_line.strip()
                    if not line or line.startswith('#') or '=' not in line:
                        continue

                    key, value = line.split('=', 1)
                    if key.strip() == 'GITHUB_TOKEN':
                        token = value.strip().strip('"').strip("'")
                        if token:
                            return token
        except OSError as e:
            print(f"Warning: Could not read {env_path}: {e}")

    return os.environ.get("GITHUB_TOKEN")

def get_latest_post():
    """Get the most recently modified .md file from the posts directory."""
    posts_dir = 'posts'
    if not os.path.exists(posts_dir):
        print(f"Error: {posts_dir} directory not found")
        sys.exit(1)
    
    md_files = []
    for file in os.listdir(posts_dir):
        if file.endswith('.md'):
            full_path = os.path.join(posts_dir, file)
            md_files.append((full_path, os.path.getmtime(full_path)))
    
    if not md_files:
        print(f"Error: No markdown files found in {posts_dir}")
        sys.exit(1)
    
    # Get the most recently modified file
    latest_file = max(md_files, key=lambda x: x[1])[0]
    
    # Extract date and title from filename
    filename = os.path.basename(latest_file)
    match = re.match(r'(\d{4}-\d{2}-\d{2})-(.+)\.md$', filename)
    if not match:
        print(f"Error: Invalid filename format: {filename}")
        sys.exit(1)
    
    date_str, slug = match.groups()
    
    # Read the file to get the title from frontmatter
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            content = f.read()
            title_match = re.search(r'title:\s*(.+)', content)
            if title_match:
                title = title_match.group(1).strip()
            else:
                # If no title in frontmatter, create one from slug
                title = ' '.join(word.capitalize() for word in slug.split('-'))
    except IOError as e:
        print(f"Error reading file {latest_file}: {str(e)}")
        sys.exit(1)
    
    return date_str, title

def create_github_issue(token, title):
    """Create a GitHub issue."""
    url = "https://api.github.com/repos/lucabol/MyBlog_Comments/issues"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "title": title,
        "body": "Comments for this blog post."
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["number"]
    except requests.exceptions.RequestException as e:
        print(f"Error creating GitHub issue: {str(e)}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        sys.exit(1)

def main():
    # Load GitHub token from ../.env first, then environment variables
    token = load_github_token()
    if not token:
        print("Error: GITHUB_TOKEN not found in ../.env or environment variables")
        sys.exit(1)
    
    # Get latest post info
    date_str, title = get_latest_post()
    
    # Format issue title (YYYY-MM-DD Title)
    issue_title = f"{date_str} {title}"
    
    # Create GitHub issue
    issue_number = create_github_issue(token, issue_title)
    
    # Generate the issue URL
    query = urllib.parse.quote(f"is:issue {date_str} {' '.join(title.split()[:3])}")
    issue_url = f"https://github.com/lucabol/MyBlog_Comments/issues?q={query}"
    
    print(f"\nSuccess!")
    print(f"Created GitHub issue for latest post: {issue_url}")

if __name__ == "__main__":
    main()
