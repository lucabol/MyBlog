import os
import sys
import tempfile
import unittest
from pathlib import Path

from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from devserver import ExtensionlessStaticFileHandler  # noqa: E402


class ExtensionlessStaticFileHandlerTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)
        (self.root / "notes.html").write_text("notes", encoding="utf-8")
        (self.root / "Schedule.html").write_text("schedule", encoding="utf-8")
        (self.root / "tags").mkdir()
        (self.root / "tags" / "story.html").write_text(
            "stories",
            encoding="utf-8",
        )
        (self.root / "static").mkdir()
        (self.root / "static" / "style.css").write_text(
            "body {}",
            encoding="utf-8",
        )

        self.handler = object.__new__(ExtensionlessStaticFileHandler)
        self.handler.root = str(self.root)
        ExtensionlessStaticFileHandler._redirect_cache.clear()

    def test_resolves_extensionless_routes_to_html_files(self):
        self.assertEqual(
            self.handler.parse_url_path("notes"),
            "notes.html",
        )
        self.assertEqual(
            self.handler.parse_url_path("tags/story"),
            os.path.join("tags", "story.html"),
        )
        self.assertEqual(
            self.handler.parse_url_path("Schedule"),
            "Schedule.html",
        )

    def test_leaves_assets_and_unknown_routes_unchanged(self):
        self.assertEqual(
            self.handler.parse_url_path("static/style.css"),
            os.path.join("static", "style.css"),
        )
        self.assertEqual(
            self.handler.parse_url_path("missing"),
            "missing",
        )


class ExtensionlessStaticFileHandlerHttpTests(AsyncHTTPTestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        (self.root / "404.html").write_text(
            "<title>Page not found | lucabol.com</title><main>Not found</main>",
            encoding="utf-8",
        )
        (self.root / "notes.html").write_text("notes", encoding="utf-8")
        (self.root / "_redirects").write_text(
            "/notes.html https://www.lucabol.com/notes 301!\n",
            encoding="utf-8",
        )
        ExtensionlessStaticFileHandler._redirect_cache.clear()
        super().setUp()

    def tearDown(self):
        try:
            super().tearDown()
        finally:
            self.temporary_directory.cleanup()

    def get_app(self):
        return Application(
            [
                (
                    r"/(.*)",
                    ExtensionlessStaticFileHandler,
                    {
                        "path": str(self.root),
                        "default_filename": "index.html",
                    },
                )
            ]
        )

    def test_redirects_html_aliases_to_local_canonical_routes(self):
        response = self.fetch(
            "/notes.html?source=preview",
            follow_redirects=False,
        )

        self.assertEqual(response.code, 301)
        self.assertEqual(response.headers["Location"], "/notes?source=preview")

    def test_serves_custom_404_with_not_found_status(self):
        response = self.fetch("/missing-audit-route")

        self.assertEqual(response.code, 404)
        self.assertIn(b"Page not found | lucabol.com", response.body)


if __name__ == "__main__":
    unittest.main()
