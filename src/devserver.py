#!/usr/bin/env python
# This file should be run with `uv run src/devserver.py` from the project root

import os
import sys
import shutil
import time
from livereload import Server
from generate_blog import main as generate_blog


def main():
    # Kill any running processes started with 'uv run'
    os.system('wmic process where "commandline like \'%uv run%\'" call terminate 2>nul')
    
    # Delete dist directory if it exists
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    # Generate the blog
    generate_blog()
    
    # Set the directory to serve
    DIRECTORY = "dist"
    PORT = 8000
    
    # Get the project root directory (one level up from src)
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Create a LiveReload server
    server = Server()
    
    # Define regeneration function - make filepath parameter optional
    def regenerate(filepath=None):
        if filepath:
            print(f"File changed: {filepath}")
        print("Regenerating blog...")
        # Delete and recreate dist directory to ensure clean state
        if os.path.exists('dist'):
            shutil.rmtree('dist')
            # Small delay to ensure file system operations complete
            time.sleep(0.5)
        
        # Regenerate the blog
        generate_blog()
        print("Blog regenerated successfully!")
        return True
    
    # Use absolute paths for watching directories to ensure they're detected properly
    posts_dir = os.path.join(root_dir, 'posts')
    src_dir = os.path.join(root_dir, 'src')
    img_dir = os.path.join(root_dir, 'img')
    
    # Watch for changes with absolute paths
    server.watch(posts_dir, regenerate)
    server.watch(src_dir, regenerate)
    server.watch(os.path.join(root_dir, '*.html'), regenerate)
    server.watch(img_dir, regenerate)
    
    print(f"Starting development server with auto-refresh at http://localhost:{PORT}")
    print(f"Watching for changes in:")
    print(f"  - {posts_dir}")
    print(f"  - {src_dir}")
    print(f"  - {img_dir}")
    print(f"  - HTML files in {root_dir}")
    print("Press Ctrl+C to quit")
    
    # Important: serve from the dist directory that will be regenerated
    # Use absolute path for the root directory
    dist_dir = os.path.join(root_dir, DIRECTORY)
    server.serve(root=dist_dir, port=PORT, host='localhost', open_url_delay=1, restart_delay=0, debug=True)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        sys.exit(0)
