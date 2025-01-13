#!/usr/bin/env python3
import os
import sys
from datetime import datetime
import argparse

def slugify(text):
    """Convert text to URL-friendly slug."""
    # Convert spaces and special chars to hyphens
    text = text.lower()
    text = text.replace(' ', '-')
    # Remove any character that's not alphanumeric or hyphen
    text = ''.join(c for c in text if c.isalnum() or c == '-')
    # Remove multiple consecutive hyphens
    while '--' in text:
        text = text.replace('--', '-')
    # Remove leading/trailing hyphens
    return text.strip('-')

def create_post_file(title, date):
    """Create a new blog post markdown file."""
    slug = slugify(title)
    filename = f"{date.strftime('%Y-%m-%d')}-{slug}.md"
    filepath = os.path.join('posts', filename)
    
    # Create posts directory if it doesn't exist
    os.makedirs('posts', exist_ok=True)
    
    # Create post content with YAML frontmatter
    content = f"""---
title: {title}
date: {date.strftime('%Y-%m-%d')}
author: lucabol
tags: []
---

"""
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created post file: {filepath}")
        return filepath
    except IOError as e:
        print(f"Error creating post file: {str(e)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Create a new blog post.')
    parser.add_argument('title', help='Title of the blog post')
    args = parser.parse_args()
    
    # Get current date
    date = datetime.now()
    
    # Create the post file
    filepath = create_post_file(args.title, date)
    
    print(f"\nSuccess!")
    print(f"Post file: {filepath}")
    print("\nNext steps:")
    print("1. Edit the post file to add your content")
    print("2. Add relevant tags in the frontmatter")
    print("3. Run the blog generator to update the site")

if __name__ == "__main__":
    main()
