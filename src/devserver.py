#!/usr/bin/env python
# Run this file with `python src/devserver.py` from the project root.

import os
import shutil
import sys
import time
from pathlib import Path
from urllib.parse import unquote, urlsplit, urlunsplit

from livereload import Server
from livereload.handlers import StaticFileHandler
from tornado.web import HTTPError

from generate_blog import main as generate_blog


class ExtensionlessStaticFileHandler(StaticFileHandler):
    _redirect_cache = {}
    _site_hosts = {"lucabol.com", "www.lucabol.com"}

    @classmethod
    def _redirects_for_root(cls, root):
        redirects_file = Path(root) / "_redirects"
        try:
            modified_at = redirects_file.stat().st_mtime_ns
        except FileNotFoundError:
            return {}

        cache_key = str(redirects_file.resolve())
        cached = cls._redirect_cache.get(cache_key)
        if cached and cached[0] == modified_at:
            return cached[1]

        redirects = {}
        for raw_line in redirects_file.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            fields = line.split()
            if len(fields) != 3:
                continue

            source, target, raw_status = fields
            source_parts = urlsplit(source)
            if source_parts.scheme or source_parts.netloc or "*" in source:
                continue

            try:
                status = int(raw_status.rstrip("!"))
            except ValueError:
                continue
            if status not in {301, 302, 303, 307, 308}:
                continue

            redirects[unquote(source_parts.path)] = (target, status)

        cls._redirect_cache[cache_key] = (modified_at, redirects)
        return redirects

    def _redirect_for_path(self, url_path):
        requested_path = unquote(f"/{url_path}") if url_path else "/"
        redirect = self._redirects_for_root(self.root).get(requested_path)
        if redirect is None:
            return None

        target, status = redirect
        target_parts = urlsplit(target)
        if (
            target_parts.scheme in {"http", "https"}
            and target_parts.hostname in self._site_hosts
        ):
            target_parts = target_parts._replace(
                scheme="",
                netloc="",
                path=target_parts.path or "/",
            )
        if self.request.query and not target_parts.query:
            target_parts = target_parts._replace(query=self.request.query)

        return urlunsplit(target_parts), status

    async def get(self, path, include_body=True):
        redirect = self._redirect_for_path(path)
        if redirect is not None:
            target, status = redirect
            self.redirect(target, status=status)
            return

        try:
            await super().get(path, include_body)
        except HTTPError as error:
            if error.status_code != 404 or path == "404.html":
                raise

            self.clear()
            self.set_status(404)
            await super().get("404.html", include_body)

    def parse_url_path(self, url_path):
        path = super().parse_url_path(url_path)
        if not path or Path(path).suffix:
            return path

        root = Path(self.root).resolve()
        candidate = (root / f"{path}.html").resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            return path

        return f"{path}.html" if candidate.is_file() else path


def main():
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
    server.SFH = ExtensionlessStaticFileHandler
    
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
