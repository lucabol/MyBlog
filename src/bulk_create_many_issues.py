import os
import json
import time
import requests
import sys
from pathlib import Path
from datetime import datetime
from typing import Union

# Flag to control whether to actually create GitHub issues
ToGithub = True

# Constants
MAX_BODY_LENGTH = 65534  # GitHub's issue body length limit
START_YEAR = 2022       # Only process posts from this year onwards

def github_request(method, url, token, params=None, data=None, etag=None, retries=10):
    """
    Make a GitHub API request with rate limit handling.
    Returns tuple of (response_data, status_code, new_etag).
    """
    if not ToGithub:
        return None, 200, None

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Add If-None-Match header for conditional request if etag provided
    if etag:
        headers["If-None-Match"] = etag

    base_wait_time = 60  # Start with 1 minute wait for secondary rate limits
    
    for attempt in range(retries):
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data
            )

            # Handle rate limits
            remaining = int(response.headers.get('x-ratelimit-remaining', 0))
            reset_time = int(response.headers.get('x-ratelimit-reset', 0))
            new_etag = response.headers.get('etag')

            # Secondary rate limit (403 or 429)
            if response.status_code in [403, 429]:
                if "secondary rate limit" in response.text.lower():
                    # Check retry-after header first
                    if 'retry-after' in response.headers:
                        wait_time = int(response.headers['retry-after'])
                        print(f"Secondary rate limit hit. Waiting {wait_time} seconds (retry-after)...")
                        time.sleep(wait_time)
                    # Then check rate limit headers
                    elif remaining == 0 and reset_time:
                        now = datetime.now().timestamp()
                        wait_time = reset_time - now
                        if wait_time > 0:
                            print(f"Rate limit exceeded. Waiting {wait_time:.0f} seconds until {datetime.fromtimestamp(reset_time)}")
                            time.sleep(wait_time)
                    # If no headers, use exponential backoff
                    else:
                        wait_time = base_wait_time * (2 ** attempt)  # Exponential backoff
                        print(f"Secondary rate limit hit. Using exponential backoff: waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                    continue
                # Primary rate limit
                elif remaining == 0 and reset_time:
                    now = datetime.now().timestamp()
                    wait_time = reset_time - now
                    if wait_time > 0:
                        print(f"Rate limit exceeded. Waiting {wait_time:.0f} seconds until {datetime.fromtimestamp(reset_time)}")
                        time.sleep(wait_time)
                        continue

            # Not modified (304) is success for conditional requests
            if response.status_code in [200, 201, 304]:
                return response.json() if response.status_code != 304 else None, response.status_code, new_etag

            # Other errors
            print(f"GitHub API error: {response.status_code} - {response.text}")
            if attempt == retries - 1:
                print("Maximum retries reached. Exiting script.")
                sys.exit(1)

        except Exception as e:
            print(f"Request failed: {str(e)}")
            if attempt == retries - 1:
                print("Maximum retries reached. Exiting script.")
                sys.exit(1)
            wait_time = base_wait_time * (2 ** attempt)  # Use exponential backoff for errors too
            time.sleep(wait_time)
            continue

    return None, None, None

def get_existing_issue(token, title):
    """Check if an issue with the given title already exists and return its number"""
    if not ToGithub:
        return None
        
    url = "https://api.github.com/repos/lucabol/MyBlog_Comments/issues"
    params = {"state": "all"}
    
    data, status, _ = github_request("GET", url, token, params=params)
    if status == 200 and data:
        for issue in data:
            if issue["title"] == title:
                return issue["number"]
    return None

def get_markdown_content(md_path):
    """Get markdown content excluding YAML header"""
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Find the second --- marker
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = parts[2].strip()
                if len(content) > MAX_BODY_LENGTH:
                    print(f"Warning: Content length ({len(content)}) exceeds GitHub's limit. Truncating to {MAX_BODY_LENGTH} characters.")
                    content = content[:MAX_BODY_LENGTH]
                return content
            return content[:MAX_BODY_LENGTH]  # Just in case
    except Exception as e:
        print(f"Error reading markdown file {md_path}: {str(e)}")
        return ""

def create_github_issue(token, title, md_path) -> Union[int, str, None]:
    """
    Create a GitHub issue using the REST API or get existing issue number.
    Returns:
    - int: Issue number for new issues
    - 'exists': For existing issues (to skip comments)
    - None: On error
    - 999: For dry run
    """
    if not ToGithub:
        print(f"Would create GitHub issue: {title}")
        return 999  # Return dummy issue number
        
    # Check if issue already exists
    existing_number = get_existing_issue(token, title)
    if existing_number is not None:
        print(f"Issue already exists: {title} (#{existing_number}), skipping comments")
        return 'exists'
        
    url = "https://api.github.com/repos/lucabol/MyBlog_Comments/issues"
    
    # Get markdown content for issue body
    body = get_markdown_content(md_path)
    data = {
        "title": title,
        "body": body
    }
    
    response_data, status, _ = github_request("POST", url, token, data=data)
    if status == 201 and response_data:
        return response_data["number"]
    return None

def create_github_comment(token, issue_number, comment_data):
    """Create a comment on a GitHub issue"""
    if not ToGithub:
        print(f"Would add comment to issue #{issue_number}: {comment_data['author']} says: {comment_data['message']}")
        return True
        
    url = f"https://api.github.com/repos/lucabol/MyBlog_Comments/issues/{issue_number}/comments"
    data = {
        "body": f"{comment_data['author']} says: {comment_data['message']}"
    }
    
    response_data, status, _ = github_request("POST", url, token, data=data)
    return status == 201

def import_comments_from_json(json_path):
    """Import comments from a JSON file with author names"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'disqus' in data and 'comments' in data['disqus']:
                comments = []
                for comment in data['disqus']['comments']:
                    # Add main comment
                    comments.append({
                        'author': comment['author'],
                        'message': comment['message']
                    })
                    # Add replies if any exist
                    if 'replies' in comment:
                        for reply in comment['replies']:
                            comments.append({
                                'author': reply['author'],
                                'message': reply['message']
                            })
                return comments
            return []
    except Exception as e:
        print(f"Error reading JSON file {json_path}: {str(e)}")
        return []

def is_post_from_year_or_later(filename: str, year: int) -> bool:
    """Check if post is from specified year or later"""
    try:
        post_date = filename[:10]  # YYYY-MM-DD
        post_year = int(post_date[:4])
        return post_year >= year
    except (ValueError, IndexError):
        return False

def main():
    # Get GitHub token from environment variable if we're posting to GitHub
    token = None
    if ToGithub:
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            print("Error: GITHUB_TOKEN environment variable not set")
            return

    # Get all markdown files from posts directory
    posts_dir = Path("posts")
    if not posts_dir.exists():
        print("Error: posts directory not found")
        return

    # Track processed posts to avoid duplicates
    processed_posts = set()
    
    # Get markdown files from 2022 onwards
    md_files = [f for f in posts_dir.glob("*.md") if is_post_from_year_or_later(f.stem, START_YEAR)]
    total_files = len(md_files)
    print(f"Found {total_files} markdown files from {START_YEAR} onwards to process")
    
    # Process each markdown file
    for i, post_file in enumerate(md_files, 1):
        # Skip if we've already processed this post
        if post_file.stem in processed_posts:
            continue
            
        try:
            # Format the title according to requirements
            filename = post_file.stem
            # Split into date and rest
            date_part = filename[:10]  # YYYY-MM-DD
            content_part = filename[11:]  # Skip the date and the following hyphen
            
            # Replace hyphens with spaces in content part and capitalize words
            words = content_part.split('-')
            capitalized_words = [word.capitalize() for word in words]
            content_part = ' '.join(capitalized_words)
            
            # Combine date and formatted content
            title = f"{date_part} {content_part}"
            
            # Create issue or get existing issue number
            print(f"[{i}/{total_files}] Processing: {title}")
            result = create_github_issue(token, title, post_file)
            
            if result == 'exists':
                # Issue exists, skip comments
                processed_posts.add(post_file.stem)
                continue
            elif isinstance(result, int):
                # New issue created or dry run
                processed_posts.add(post_file.stem)
                if not ToGithub:
                    print(f"Would create/use issue #{result} for {title}")
                else:
                    print(f"Successfully created issue #{result} for {title}")
                
                # Check for corresponding JSON file
                json_file = post_file.with_suffix('.json')
                print(f"Looking for JSON file: {json_file}")
                if json_file.exists():
                    print(f"Found JSON file: {json_file}")
                    comments = import_comments_from_json(json_file)
                    print(f"Found {len(comments)} comments")
                    for comment in comments:
                        if create_github_comment(token, result, comment):
                            print(f"Added comment to issue #{result}")
                else:
                    print(f"No JSON file found at: {json_file}")
            
        except Exception as e:
            print(f"Error processing {post_file}: {str(e)}")

if __name__ == "__main__":
    main()
