from __future__ import annotations

import contextlib
import io
import json
import os
import re
import sys
import tempfile
import unittest
from collections import defaultdict
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from unittest import mock
from urllib.parse import unquote, urljoin, urlsplit
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup, NavigableString


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

import generate_blog  # noqa: E402
from generate_blog import BlogGenerator  # noqa: E402


SITE_ORIGIN = "https://www.lucabol.com"
SITE_HOSTS = {"lucabol.com", "www.lucabol.com"}
FEED_URL = f"{SITE_ORIGIN}/feed.xml"
SITEMAP_NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"
XHTML_NAMESPACE = "http://www.w3.org/1999/xhtml"
FORBIDDEN_LINK_TEXT = {
    "here",
    "click here",
    "read more",
    "more",
    "this",
    "link",
}
GENERIC_ALT_TEXT = re.compile(
    r"^(?:alt text|figure|graphic|icon|image|img|logo|photo|picture|"
    r"placeholder|screenshot|thumbnail|untitled)(?:\s+\d+)?$",
    re.IGNORECASE,
)
SAFE_TAG_ROUTE = re.compile(r"^/tags(?:/[a-z0-9]+(?:-[a-z0-9]+)*)?$")
NEAR_TOP_PAGE_TEXT_LIMIT = 400


class GeneratedSiteStandardsTests(unittest.TestCase):
    """Regression tests for the public contract of the generated site."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._original_cwd = Path.cwd()
        os.chdir(ROOT)
        cls.addClassCleanup(os.chdir, cls._original_cwd)

        cls._has_api_key_patch = mock.patch.object(
            generate_blog,
            "has_api_key",
            return_value=False,
        )
        cls._api_info_patch = mock.patch.object(
            generate_blog,
            "print_api_key_info",
            return_value=None,
        )
        cls._has_api_key_patch.start()
        cls._api_info_patch.start()
        cls.addClassCleanup(cls._api_info_patch.stop)
        cls.addClassCleanup(cls._has_api_key_patch.stop)

        cls._temporary_directory = tempfile.TemporaryDirectory(
            prefix="generated-site-",
            dir=ROOT / "tests",
            ignore_cleanup_errors=True,
        )
        cls.addClassCleanup(cls._temporary_directory.cleanup)
        cls.dist = Path(cls._temporary_directory.name) / "dist"

        cls.generator = BlogGenerator(ROOT / "posts", cls.dist)
        with contextlib.redirect_stdout(io.StringIO()):
            cls.generator.generate_site()

        cls.html_files = sorted(cls.dist.rglob("*.html"))
        cls.generated_blog_html_files = [
            path for path in cls.html_files if not cls._is_schedule(path)
        ]
        cls.blog_html_files = cls.html_files
        cls.indexable_html_files = [
            path
            for path in cls.blog_html_files
            if not cls._is_schedule(path)
            and cls._relative(path).casefold() != "404.html"
        ]
        cls.post_html_files = sorted(
            [
                *cls.dist.joinpath("posts").glob("*.html"),
                *cls.dist.joinpath("en").glob("*.html"),
                *cls.dist.joinpath("it").glob("*.html"),
            ]
        )
        cls._soups = {}
        cls._html_routes = {
            cls._route_for_file(path).casefold(): (
                cls._route_for_file(path),
                path,
            )
            for path in cls.html_files
        }
        cls._output_files = {
            f"/{path.relative_to(cls.dist).as_posix()}".casefold(): path
            for path in cls.dist.rglob("*")
            if path.is_file()
        }

    @classmethod
    def _relative(cls, path):
        return path.relative_to(cls.dist).as_posix()

    @classmethod
    def _is_schedule(cls, path):
        relative = cls._relative(path).casefold()
        return relative in {"schedule.html", "schedule/index.html"}

    @classmethod
    def _route_for_file(cls, path):
        relative = cls._relative(path)
        if relative == "index.html":
            return "/"
        if not relative.endswith(".html"):
            raise ValueError(f"Not an HTML output: {relative}")
        return f"/{relative[:-5]}"

    @classmethod
    def _canonical_for_file(cls, path):
        return f"{SITE_ORIGIN}{cls._route_for_file(path)}"

    @classmethod
    def _soup(cls, path):
        if path not in cls._soups:
            cls._soups[path] = BeautifulSoup(
                path.read_text(encoding="utf-8"),
                "html.parser",
            )
        return cls._soups[path]

    @staticmethod
    def _rel_tokens(tag):
        value = tag.get("rel", [])
        if isinstance(value, str):
            value = value.split()
        return {str(token).casefold() for token in value}

    @classmethod
    def _links_with_rel(cls, soup, rel):
        rel = rel.casefold()
        return [
            link
            for link in soup.find_all("link")
            if rel in cls._rel_tokens(link)
        ]

    @staticmethod
    def _meta_tags(soup, attribute, value):
        value = value.casefold()
        return [
            tag
            for tag in soup.find_all("meta")
            if str(tag.get(attribute, "")).casefold() == value
        ]

    @staticmethod
    def _normalized_text(value):
        return re.sub(r"\s+", " ", value or "").strip()

    @classmethod
    def _resolve_output_path(cls, url_path):
        decoded_path = unquote(url_path or "/")
        if not decoded_path.startswith("/"):
            return None

        exact = cls._output_files.get(decoded_path.casefold())
        if exact is not None:
            return exact

        route = "/" if decoded_path == "/" else decoded_path.rstrip("/")
        route_entry = cls._html_routes.get(route.casefold())
        return route_entry[1] if route_entry is not None else None

    @classmethod
    def _actual_route_for_url_path(cls, url_path):
        decoded_path = unquote(url_path or "/")
        route = "/" if decoded_path == "/" else decoded_path.rstrip("/")
        route_entry = cls._html_routes.get(route.casefold())
        return route_entry[0] if route_entry is not None else None

    @classmethod
    def _absolute_url(cls, document, value):
        return urljoin(cls._canonical_for_file(document), value)

    @classmethod
    def _internal_url_parts(cls, document, value):
        value = (value or "").strip()
        if not value or value.startswith("#"):
            return None

        parsed = urlsplit(value)
        if parsed.scheme and parsed.scheme.casefold() not in {"http", "https"}:
            return None
        if parsed.hostname and parsed.hostname.casefold() not in SITE_HOSTS:
            return None

        absolute = cls._absolute_url(document, value)
        absolute_parts = urlsplit(absolute)
        if (
            absolute_parts.hostname
            and absolute_parts.hostname.casefold() not in SITE_HOSTS
        ):
            return None
        return absolute_parts

    @classmethod
    def _canonical_links(cls, soup):
        return cls._links_with_rel(soup, "canonical")

    @classmethod
    def _hreflang_map(cls, soup):
        alternates = defaultdict(list)
        for link in cls._links_with_rel(soup, "alternate"):
            language = cls._normalized_text(link.get("hreflang")).casefold()
            if language:
                alternates[language].append(
                    cls._normalized_text(link.get("href"))
                )
        return alternates

    @staticmethod
    def _assert_no_problems(problems):
        if not problems:
            return
        limit = 40
        displayed = problems[:limit]
        suffix = (
            f"\n... and {len(problems) - limit} more problem(s)"
            if len(problems) > limit
            else ""
        )
        raise AssertionError("\n" + "\n".join(displayed) + suffix)

    @staticmethod
    def _canonical_url_problems(url, context):
        problems = []
        parsed = urlsplit(url)
        if parsed.scheme != "https":
            problems.append(f"{context}: URL must use https: {url!r}")
        if parsed.netloc.casefold() != "www.lucabol.com":
            problems.append(
                f"{context}: URL must use www.lucabol.com: {url!r}"
            )
        decoded_path = unquote(parsed.path or "/")
        if decoded_path.casefold().endswith(".html"):
            problems.append(
                f"{context}: canonical URL must be extensionless: {url!r}"
            )
        if re.search(r"\s", decoded_path):
            problems.append(f"{context}: URL path contains whitespace: {url!r}")
        if parsed.query or parsed.fragment:
            problems.append(
                f"{context}: canonical URL has a query or fragment: {url!r}"
            )
        return problems

    def _parse_sitemap(self):
        root = ET.parse(self.dist / "sitemap.xml").getroot()
        entries = {}
        duplicates = []
        for url_element in root.findall(
            f"{{{SITEMAP_NAMESPACE}}}url"
        ):
            location_element = url_element.find(
                f"{{{SITEMAP_NAMESPACE}}}loc"
            )
            location = self._normalized_text(
                location_element.text if location_element is not None else ""
            )
            alternates = defaultdict(list)
            for link in url_element.findall(
                f"{{{XHTML_NAMESPACE}}}link"
            ):
                if str(link.get("rel", "")).casefold() != "alternate":
                    continue
                language = self._normalized_text(
                    link.get("hreflang")
                ).casefold()
                alternates[language].append(
                    self._normalized_text(link.get("href"))
                )
            if location in entries:
                duplicates.append(location)
            entries[location] = alternates
        return root, entries, duplicates

    def _parse_redirects(self):
        redirects = {}
        problems = []
        for line_number, raw_line in enumerate(
            (self.dist / "_redirects").read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            fields = line.split()
            if len(fields) != 3:
                problems.append(
                    f"_redirects:{line_number}: expected source, target, "
                    f"and status: {raw_line!r}"
                )
                continue
            source, target, status = fields
            if source in redirects:
                problems.append(
                    f"_redirects:{line_number}: duplicate source {source!r}"
                )
            redirects[source] = (target, status)
        self._assert_no_problems(problems)
        return redirects

    @staticmethod
    def _parse_headers(text):
        blocks = {}
        current_pattern = None
        for raw_line in text.splitlines():
            if not raw_line.strip() or raw_line.lstrip().startswith("#"):
                continue
            if not raw_line[:1].isspace():
                current_pattern = raw_line.strip()
                blocks.setdefault(current_pattern, {})
                continue
            if current_pattern is None or ":" not in raw_line:
                continue
            name, value = raw_line.strip().split(":", 1)
            blocks[current_pattern][name.casefold()] = value.strip()
        return blocks

    @staticmethod
    def _parse_css_declarations(body):
        declarations = {}
        for declaration in body.split(";"):
            if ":" not in declaration:
                continue
            name, value = declaration.split(":", 1)
            name = name.strip().casefold()
            if name:
                declarations[name] = value.strip()
        return declarations

    @classmethod
    def _parse_css_rules(cls, text):
        """Extract selectors/declarations without depending on a CSS parser."""
        text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
        rules = []

        def parse_region(region, media_queries=()):
            cursor = 0
            while cursor < len(region):
                opening = region.find("{", cursor)
                if opening == -1:
                    return

                prelude = region[cursor:opening].strip()
                depth = 1
                closing = opening + 1
                while closing < len(region) and depth:
                    if region[closing] == "{":
                        depth += 1
                    elif region[closing] == "}":
                        depth -= 1
                    closing += 1
                if depth:
                    return

                body = region[opening + 1 : closing - 1]
                lowered_prelude = prelude.casefold()
                if lowered_prelude.startswith("@media"):
                    query = prelude[len("@media") :].strip()
                    parse_region(body, (*media_queries, query))
                elif lowered_prelude.startswith(("@supports", "@layer")):
                    parse_region(body, media_queries)
                elif prelude:
                    selectors = tuple(
                        re.sub(r"\s+", " ", selector).strip()
                        for selector in prelude.split(",")
                        if selector.strip()
                    )
                    rules.append(
                        {
                            "selectors": selectors,
                            "declarations": cls._parse_css_declarations(body),
                            "media": media_queries,
                        }
                    )
                cursor = closing

        parse_region(text)
        return rules

    @staticmethod
    def _css_length_px(value, custom_properties):
        value = (value or "").strip().casefold()
        seen = set()
        while True:
            variable = re.fullmatch(
                r"var\(\s*(--[a-z0-9_-]+)\s*(?:,[^)]+)?\)",
                value,
            )
            if not variable:
                break
            name = variable.group(1)
            if name in seen or name not in custom_properties:
                return None
            seen.add(name)
            value = custom_properties[name].strip().casefold()

        length = re.fullmatch(r"(-?(?:\d+(?:\.\d+)?|\.\d+))(px|rem|em)", value)
        if not length:
            return None
        number = float(length.group(1))
        return number if length.group(2) == "px" else number * 16

    @staticmethod
    def _css_rules_for_selector(rules, selector):
        selector = re.sub(r"\s+", " ", selector).strip()
        return [rule for rule in rules if selector in rule["selectors"]]

    @staticmethod
    def _cache_max_age(value):
        match = re.search(r"(?:^|,)\s*max-age\s*=\s*(\d+)", value, re.IGNORECASE)
        return int(match.group(1)) if match else None

    def test_required_output_and_static_assets_exist(self):
        required_files = {
            "index.html",
            "404.html",
            "static/style.css",
            "sitemap.xml",
            "feed.xml",
            "_headers",
            "_redirects",
        }
        missing = [
            relative
            for relative in sorted(required_files)
            if not (self.dist / Path(*relative.split("/"))).is_file()
        ]

        for source_dir_name in ("img", "fonts"):
            source_dir = ROOT / source_dir_name
            if not source_dir.is_dir():
                continue
            for source_file in source_dir.rglob("*"):
                if not source_file.is_file():
                    continue
                destination = (
                    self.dist
                    / source_dir_name
                    / source_file.relative_to(source_dir)
                )
                if not destination.is_file():
                    missing.append(destination.relative_to(self.dist).as_posix())

        for source_file in [
            ROOT / "favicon.svg",
            ROOT / "favicon.ico",
            ROOT / "fluidicon.png",
            SRC / "story-language.js",
        ]:
            if not source_file.is_file():
                continue
            destination = (
                self.dist / "static" / source_file.name
                if source_file.parent == SRC
                else self.dist / source_file.name
            )
            if not destination.is_file():
                missing.append(destination.relative_to(self.dist).as_posix())

        self.assertFalse(missing, f"Missing generated files: {missing}")

    def test_source_posts_have_physical_html_outputs(self):
        expected = {
            source.stem.lower()
            for source in (ROOT / "posts").glob("*.md")
        }
        actual = {
            output.stem
            for output in (self.dist / "posts").glob("*.html")
        }
        self.assertTrue(expected, "Expected at least one source post")
        self.assertEqual(
            expected - actual,
            set(),
            "Every source post must produce posts/<lower-case-slug>.html",
        )

    def test_structured_project_links_render_as_links(self):
        path = self.dist / "code.html"
        soup = self._soup(path)
        link = soup.find(
            "a",
            href="http://followtheguru.azurewebsites.net/",
        )
        self.assertIsNotNone(link)
        self.assertEqual(
            self._normalized_text(link.get_text(" ", strip=True)),
            "Open the live FollowTheGuru app",
        )
        self.assertNotIn("&lt;a ", path.read_text(encoding="utf-8"))

    def test_indexable_pages_have_complete_page_specific_metadata(self):
        problems = []
        descriptions = defaultdict(list)

        for path in self.indexable_html_files:
            relative = self._relative(path)
            soup = self._soup(path)

            html_elements = soup.find_all("html")
            if len(html_elements) != 1:
                problems.append(
                    f"{relative}: expected one html element, found "
                    f"{len(html_elements)}"
                )
                continue
            language = self._normalized_text(
                html_elements[0].get("lang")
            ).casefold()
            if language not in {"en", "it"}:
                problems.append(
                    f"{relative}: html lang must be en or it, got {language!r}"
                )

            titles = soup.find_all("title")
            if len(titles) != 1 or not self._normalized_text(
                titles[0].get_text()
            ):
                problems.append(
                    f"{relative}: expected exactly one non-empty title"
                )
                title = ""
            else:
                title = self._normalized_text(titles[0].get_text())

            description_tags = self._meta_tags(
                soup,
                "name",
                "description",
            )
            if len(description_tags) != 1:
                problems.append(
                    f"{relative}: expected exactly one meta description, "
                    f"found {len(description_tags)}"
                )
                description = ""
            else:
                description = self._normalized_text(
                    description_tags[0].get("content")
                )
                if not description:
                    problems.append(
                        f"{relative}: meta description must not be empty"
                    )
                else:
                    descriptions[description.casefold()].append(relative)

            h1_elements = soup.find_all("h1")
            if len(h1_elements) != 1 or not self._normalized_text(
                h1_elements[0].get_text(" ", strip=True)
            ):
                problems.append(
                    f"{relative}: expected exactly one non-empty H1, found "
                    f"{len(h1_elements)}"
                )

            canonical_links = self._canonical_links(soup)
            if len(canonical_links) != 1:
                problems.append(
                    f"{relative}: expected exactly one canonical link, found "
                    f"{len(canonical_links)}"
                )
                canonical = ""
            else:
                canonical = self._normalized_text(
                    canonical_links[0].get("href")
                )
                expected_canonical = self._canonical_for_file(path)
                if canonical != expected_canonical:
                    problems.append(
                        f"{relative}: canonical must be self-referential; "
                        f"expected {expected_canonical!r}, got {canonical!r}"
                    )
                problems.extend(
                    self._canonical_url_problems(
                        canonical,
                        f"{relative} canonical",
                    )
                )

            robots_tags = self._meta_tags(soup, "name", "robots")
            if any(
                "noindex"
                in {
                    token.strip().casefold()
                    for token in str(tag.get("content", "")).split(",")
                }
                for tag in robots_tags
            ):
                problems.append(
                    f"{relative}: indexable page declares robots noindex"
                )

            rss_links = [
                link
                for link in self._links_with_rel(soup, "alternate")
                if str(link.get("type", "")).casefold()
                == "application/rss+xml"
            ]
            if len(rss_links) != 1:
                problems.append(
                    f"{relative}: expected one RSS discovery link, found "
                    f"{len(rss_links)}"
                )
            else:
                discovered_feed = self._absolute_url(
                    path,
                    self._normalized_text(rss_links[0].get("href")),
                )
                if discovered_feed != FEED_URL:
                    problems.append(
                        f"{relative}: RSS discovery must point to {FEED_URL}, "
                        f"got {discovered_feed!r}"
                    )

            open_graph = {}
            for property_name in (
                "og:title",
                "og:description",
                "og:type",
                "og:url",
                "og:image",
            ):
                tags = self._meta_tags(soup, "property", property_name)
                if len(tags) != 1:
                    problems.append(
                        f"{relative}: expected one {property_name} meta tag, "
                        f"found {len(tags)}"
                    )
                    continue
                value = self._normalized_text(tags[0].get("content"))
                if not value:
                    problems.append(
                        f"{relative}: {property_name} must not be empty"
                    )
                open_graph[property_name] = value

            twitter = {}
            for name in (
                "twitter:card",
                "twitter:title",
                "twitter:description",
                "twitter:image",
            ):
                tags = self._meta_tags(soup, "name", name)
                if len(tags) != 1:
                    problems.append(
                        f"{relative}: expected one {name} meta tag, found "
                        f"{len(tags)}"
                    )
                    continue
                value = self._normalized_text(tags[0].get("content"))
                if not value:
                    problems.append(f"{relative}: {name} must not be empty")
                twitter[name] = value

            expected_metadata = {
                "og:title": title,
                "og:description": description,
                "og:url": canonical,
                "twitter:title": title,
                "twitter:description": description,
            }
            for name, expected_value in expected_metadata.items():
                actual = (
                    open_graph.get(name)
                    if name.startswith("og:")
                    else twitter.get(name)
                )
                if actual is not None and actual != expected_value:
                    problems.append(
                        f"{relative}: {name} must match page metadata; "
                        f"expected {expected_value!r}, got {actual!r}"
                    )

            for name, value in (
                ("og:image", open_graph.get("og:image")),
                ("twitter:image", twitter.get("twitter:image")),
            ):
                if value:
                    parsed_image = urlsplit(value)
                    if parsed_image.scheme != "https" or not parsed_image.netloc:
                        problems.append(
                            f"{relative}: {name} must be an absolute HTTPS "
                            f"URL, got {value!r}"
                        )

            json_ld_scripts = [
                script
                for script in soup.find_all("script")
                if str(script.get("type", "")).casefold()
                == "application/ld+json"
            ]
            if not json_ld_scripts:
                problems.append(
                    f"{relative}: expected at least one JSON-LD script"
                )
            for index, script in enumerate(json_ld_scripts, start=1):
                payload = script.string or script.get_text()
                try:
                    parsed_payload = json.loads(payload)
                except (TypeError, json.JSONDecodeError) as error:
                    problems.append(
                        f"{relative}: JSON-LD script {index} is invalid: "
                        f"{error}"
                    )
                else:
                    if not isinstance(parsed_payload, (dict, list)):
                        problems.append(
                            f"{relative}: JSON-LD script {index} must contain "
                            "an object or array"
                        )

        for duplicate_paths in descriptions.values():
            if len(duplicate_paths) > 1:
                problems.append(
                    "Page-specific meta description is reused by: "
                    + ", ".join(sorted(duplicate_paths))
                )

        self._assert_no_problems(problems)

    def test_generated_blog_pages_have_a_working_skip_link(self):
        problems = []
        for path in self.generated_blog_html_files:
            relative = self._relative(path)
            soup = self._soup(path)
            skip_links = soup.select("a.skip-link")
            if len(skip_links) != 1:
                problems.append(
                    f"{relative}: expected exactly one skip link, found "
                    f"{len(skip_links)}"
                )
                continue

            skip_link = skip_links[0]
            if not self._normalized_text(
                skip_link.get_text(" ", strip=True)
            ):
                problems.append(f"{relative}: skip link text is empty")

            href = self._normalized_text(skip_link.get("href"))
            parsed_href = urlsplit(href)
            if parsed_href.path or parsed_href.query or not parsed_href.fragment:
                problems.append(
                    f"{relative}: skip link must be a same-page fragment, "
                    f"got {href!r}"
                )
                continue

            fragment = unquote(parsed_href.fragment)
            targets = soup.find_all(id=fragment)
            if len(targets) != 1:
                problems.append(
                    f"{relative}: skip-link fragment #{fragment} resolves to "
                    f"{len(targets)} elements"
                )
                continue

            target = targets[0]
            main_elements = soup.find_all("main")
            if len(main_elements) != 1 or target is not main_elements[0]:
                problems.append(
                    f"{relative}: skip link must target the page's one main "
                    "element"
                )
            if str(target.get("tabindex", "")).strip() != "-1":
                problems.append(
                    f"{relative}: skip target must use tabindex=-1 so focus "
                    "moves with the fragment"
                )
            if skip_link.find_next("main") is not target:
                problems.append(
                    f"{relative}: skip link must occur before its main target"
                )

        self._assert_no_problems(problems)

    def test_footer_site_search_is_accessible_and_scoped(self):
        problems = []
        for path in self.generated_blog_html_files:
            relative = self._relative(path)
            soup = self._soup(path)
            if not soup.find_all("footer"):
                problems.append(f"{relative}: missing footer")
                continue

            search_forms = [
                form
                for form in soup.find_all("form")
                if str(form.get("role", "")).casefold() == "search"
                and form.find_parent("footer") is not None
            ]
            if len(search_forms) != 1:
                problems.append(
                    f"{relative}: footer must contain exactly one role=search "
                    f"form, found {len(search_forms)}"
                )
                continue

            form = search_forms[0]
            if str(form.get("method", "")).casefold() != "get":
                problems.append(
                    f"{relative}: site search must submit with GET"
                )

            action = self._normalized_text(form.get("action"))
            action_parts = urlsplit(action)
            if (
                action_parts.scheme != "https"
                or (action_parts.hostname or "").casefold()
                not in {"duckduckgo.com", "www.duckduckgo.com"}
                or action_parts.path not in {"", "/"}
                or action_parts.query
                or action_parts.fragment
            ):
                problems.append(
                    f"{relative}: site search action must be the DuckDuckGo "
                    f"HTTPS endpoint, got {action!r}"
                )

            search_inputs = [
                field
                for field in form.find_all("input")
                if str(field.get("type", "")).casefold() == "search"
            ]
            if len(search_inputs) != 1:
                problems.append(
                    f"{relative}: search form needs exactly one type=search "
                    f"input, found {len(search_inputs)}"
                )
            else:
                search_input = search_inputs[0]
                if str(search_input.get("name", "")) != "q":
                    problems.append(
                        f"{relative}: DuckDuckGo search input must be named q"
                    )
                input_id = self._normalized_text(search_input.get("id"))
                labels = []
                if input_id:
                    labels.extend(
                        form.find_all("label", attrs={"for": input_id})
                    )
                    if len(soup.find_all(id=input_id)) != 1:
                        problems.append(
                            f"{relative}: search input id {input_id!r} is "
                            "not unique"
                        )
                wrapping_label = search_input.find_parent("label")
                if wrapping_label is not None:
                    labels.append(wrapping_label)
                if not input_id and wrapping_label is None:
                    problems.append(
                        f"{relative}: search input needs an id for its label "
                        "or must be wrapped by a label"
                    )
                unique_labels = []
                for label in labels:
                    if label not in unique_labels:
                        unique_labels.append(label)
                if len(unique_labels) != 1 or not self._normalized_text(
                    unique_labels[0].get_text(" ", strip=True)
                    if unique_labels
                    else ""
                ):
                    problems.append(
                        f"{relative}: search input needs exactly one real, "
                        "non-empty associated label"
                    )

            site_constraints = [
                field
                for field in form.find_all("input")
                if str(field.get("type", "")).casefold() == "hidden"
                and str(field.get("name", "")) == "sites"
                and str(field.get("value", "")) == "lucabol.com"
            ]
            if len(site_constraints) != 1:
                problems.append(
                    f"{relative}: search form needs one hidden "
                    "sites=lucabol.com constraint"
                )

            submit_buttons = [
                button
                for button in form.find_all("button")
                if str(button.get("type", "submit")).casefold() == "submit"
            ]
            if len(submit_buttons) != 1:
                problems.append(
                    f"{relative}: search form needs exactly one submit "
                    f"button, found {len(submit_buttons)}"
                )
            elif not (
                self._normalized_text(
                    submit_buttons[0].get_text(" ", strip=True)
                )
                or self._normalized_text(
                    submit_buttons[0].get("aria-label")
                )
            ):
                problems.append(
                    f"{relative}: search submit button needs an accessible "
                    "name"
                )

        self._assert_no_problems(problems)

    def test_404_is_noindex_and_not_required_to_be_indexable(self):
        path = self.dist / "404.html"
        soup = self._soup(path)
        robots = self._meta_tags(soup, "name", "robots")
        self.assertEqual(
            len(robots),
            1,
            "404.html must have exactly one robots meta tag",
        )
        directives = {
            directive.strip().casefold()
            for directive in str(robots[0].get("content", "")).split(",")
        }
        self.assertIn("noindex", directives)

        canonical_links = self._canonical_links(soup)
        self.assertLessEqual(
            len(canonical_links),
            1,
            "404.html may omit canonical metadata but must not duplicate it",
        )
        if canonical_links:
            canonical = self._normalized_text(canonical_links[0].get("href"))
            self.assertEqual(canonical, self._canonical_for_file(path))
            self._assert_no_problems(
                self._canonical_url_problems(canonical, "404.html canonical")
            )

        for script in [
            tag
            for tag in soup.find_all("script")
            if str(tag.get("type", "")).casefold()
            == "application/ld+json"
        ]:
            json.loads(script.string or script.get_text())

        titles = soup.find_all("title")
        self.assertEqual(len(titles), 1)
        self.assertIn(
            generate_blog.SITE_NAME.casefold(),
            self._normalized_text(titles[0].get_text()).casefold(),
            "404 title must retain the site's brand",
        )

        h1_elements = soup.find_all("h1")
        self.assertEqual(len(h1_elements), 1, "404 must have exactly one H1")
        self.assertRegex(
            self._normalized_text(
                h1_elements[0].get_text(" ", strip=True)
            ).casefold(),
            r"(?:404|not found)",
            "404 H1 must make the error recognizable",
        )

        main = soup.find("main")
        self.assertIsNotNone(main, "404 must contain a main landmark")
        explanation = self._normalized_text(
            " ".join(
                paragraph.get_text(" ", strip=True)
                for paragraph in main.find_all("p")
            )
        )
        self.assertGreaterEqual(
            len(explanation),
            30,
            "404 must explain what happened and help the visitor recover",
        )

        recovery_routes = set()
        for anchor in main.find_all("a", href=True):
            parts = self._internal_url_parts(path, anchor.get("href"))
            if parts is None:
                continue
            target = self._resolve_output_path(parts.path)
            if target is not None and target.suffix.casefold() == ".html":
                recovery_routes.add(unquote(parts.path or "/").rstrip("/") or "/")
        self.assertIn("/", recovery_routes, "404 must link back to the home page")
        self.assertGreaterEqual(
            len(recovery_routes),
            2,
            "404 must offer multiple working internal recovery destinations",
        )
        self.assertIsNotNone(
            soup.find(
                "form",
                attrs={"role": lambda value: str(value).casefold() == "search"},
            ),
            "404 must offer the site search",
        )

    def test_post_pages_use_one_semantic_article(self):
        problems = []
        self.assertTrue(self.post_html_files, "Expected generated post pages")

        for path in self.post_html_files:
            relative = self._relative(path)
            soup = self._soup(path)
            articles = soup.find_all("article")
            if len(articles) != 1:
                problems.append(
                    f"{relative}: expected exactly one article, found "
                    f"{len(articles)}"
                )
                continue

            article = articles[0]
            h1_elements = soup.find_all("h1")
            if len(h1_elements) != 1:
                problems.append(
                    f"{relative}: post must have exactly one H1, found "
                    f"{len(h1_elements)}"
                )
            elif h1_elements[0].find_parent("article") is not article:
                problems.append(f"{relative}: H1 must be inside the article")

            headers = article.find_all("header")
            if len(headers) != 1:
                problems.append(
                    f"{relative}: article must contain exactly one header, "
                    f"found {len(headers)}"
                )

            time_elements = article.find_all("time")
            if len(time_elements) != 1:
                problems.append(
                    f"{relative}: article must contain exactly one time, "
                    f"found {len(time_elements)}"
                )
            else:
                datetime_value = self._normalized_text(
                    time_elements[0].get("datetime")
                )
                if not datetime_value:
                    problems.append(
                        f"{relative}: time must have a datetime attribute"
                    )
                else:
                    try:
                        datetime.fromisoformat(
                            datetime_value.replace("Z", "+00:00")
                        )
                    except ValueError:
                        problems.append(
                            f"{relative}: invalid time datetime value "
                            f"{datetime_value!r}"
                        )
                if time_elements[0].find_parent("em") is None:
                    problems.append(
                        f"{relative}: article byline and date must retain "
                        "their editorial emphasis"
                    )

            content_elements = []
            for element in article.find_all(
                [
                    "p",
                    "ul",
                    "ol",
                    "blockquote",
                    "pre",
                    "table",
                    "img",
                    "h2",
                    "h3",
                    "h4",
                    "h5",
                    "h6",
                ]
            ):
                if element.find_parent("header") is not None:
                    continue
                if element.find_parent("footer") is not None:
                    continue
                content_elements.append(element)
            if not content_elements:
                problems.append(
                    f"{relative}: article has no content outside its header"
                )

        self._assert_no_problems(problems)

    def test_generated_tables_use_header_cell_semantics(self):
        problems = []
        table_count = 0
        for path in self.generated_blog_html_files:
            relative = self._relative(path)
            for table_number, table in enumerate(
                self._soup(path).find_all("table"),
                start=1,
            ):
                table_count += 1
                context = f"{relative} table {table_number}"
                if str(table.get("role", "")).casefold() in {
                    "none",
                    "presentation",
                }:
                    problems.append(
                        f"{context}: generated data table must retain table "
                        "semantics"
                    )

                rows = table.find_all("tr")
                if not rows:
                    problems.append(f"{context}: table has no rows")
                    continue
                for row_number, row in enumerate(rows, start=1):
                    direct_cells = row.find_all(
                        ["th", "td"],
                        recursive=False,
                    )
                    if not direct_cells:
                        problems.append(
                            f"{context}: row {row_number} has no th/td cells"
                        )

                header_cells = table.find_all("th")
                if not header_cells:
                    problems.append(
                        f"{context}: table needs semantic header cells"
                    )
                unscoped_body_headers = [
                    header
                    for header in header_cells
                    if header.find_parent("thead") is None
                    and str(header.get("scope", "")).casefold()
                    not in {"col", "colgroup", "row", "rowgroup"}
                ]
                if unscoped_body_headers:
                    problems.append(
                        f"{context}: th cells outside thead need an explicit "
                        "col/row scope"
                    )

        self.assertGreater(
            table_count,
            0,
            "The generated fixture must contain tables so this test is active",
        )
        self._assert_no_problems(problems)

    def test_heading_levels_do_not_jump(self):
        problems = []
        for path in self.blog_html_files:
            relative = self._relative(path)
            headings = self._soup(path).find_all(
                ["h1", "h2", "h3", "h4", "h5", "h6"]
            )
            levels = [int(heading.name[1]) for heading in headings]
            for index, (previous, current) in enumerate(
                zip(levels, levels[1:]),
                start=2,
            ):
                if current > previous + 1:
                    problems.append(
                        f"{relative}: heading {index} jumps from H{previous} "
                        f"to H{current}"
                    )
        self._assert_no_problems(problems)

    def test_internal_links_are_canonical_and_resolve(self):
        problems = []
        for path in self.blog_html_files:
            relative = self._relative(path)
            soup = self._soup(path)
            values = []
            for anchor in soup.find_all("a", href=True):
                values.append(("href", anchor.get("href")))
            for element in soup.find_all(attrs={"data-url-en": True}):
                values.append(("data-url-en", element.get("data-url-en")))
            for element in soup.find_all(attrs={"data-url-it": True}):
                values.append(("data-url-it", element.get("data-url-it")))

            for attribute, raw_value in values:
                value = str(raw_value or "")
                stripped = value.strip()
                if not stripped or stripped.startswith("#"):
                    continue

                raw_parts = urlsplit(stripped)
                if (
                    stripped.startswith("//")
                    and raw_parts.hostname
                    and "." not in raw_parts.hostname
                ):
                    problems.append(
                        f"{relative}: malformed protocol-relative internal "
                        f"{attribute} {stripped!r}"
                    )
                    continue

                parts = self._internal_url_parts(path, stripped)
                if parts is None:
                    continue

                if raw_parts.hostname:
                    if (
                        raw_parts.scheme.casefold() != "https"
                        or raw_parts.netloc.casefold() != "www.lucabol.com"
                    ):
                        problems.append(
                            f"{relative}: absolute internal {attribute} must "
                            f"use {SITE_ORIGIN}: {stripped!r}"
                        )

                decoded_path = unquote(parts.path or "/")
                if re.search(r"\s", decoded_path):
                    problems.append(
                        f"{relative}: internal {attribute} path contains "
                        f"whitespace: {stripped!r}"
                    )
                if decoded_path.casefold().endswith(".html"):
                    problems.append(
                        f"{relative}: internal {attribute} must use an "
                        f"extensionless HTML route: {stripped!r}"
                    )

                resolved = self._resolve_output_path(decoded_path)
                if resolved is None:
                    problems.append(
                        f"{relative}: internal {attribute} does not resolve: "
                        f"{stripped!r}"
                    )
                    continue

                if resolved.suffix.casefold() == ".html":
                    canonical_route = self._actual_route_for_url_path(
                        decoded_path
                    )
                    if canonical_route is None:
                        problems.append(
                            f"{relative}: cannot determine canonical route "
                            f"for {attribute} {stripped!r}"
                        )
                    elif decoded_path != canonical_route:
                        problems.append(
                            f"{relative}: internal {attribute} is not the "
                            f"canonical route; expected {canonical_route!r}, "
                            f"got {decoded_path!r}"
                        )

        self._assert_no_problems(problems)

    def test_visible_anchor_text_avoids_ambiguous_phrases(self):
        problems = []
        for path in self.blog_html_files:
            relative = self._relative(path)
            for anchor in self._soup(path).find_all("a"):
                text = self._normalized_text(
                    anchor.get_text(" ", strip=True)
                ).casefold()
                if text in FORBIDDEN_LINK_TEXT:
                    problems.append(
                        f"{relative}: ambiguous visible anchor text {text!r} "
                        f"for {anchor.get('href')!r}"
                    )
        self._assert_no_problems(problems)

    def test_tag_routes_are_safe_canonical_slugs(self):
        problems = []

        for path in (self.dist / "tags").glob("*.html"):
            route = self._route_for_file(path)
            if not SAFE_TAG_ROUTE.fullmatch(route):
                problems.append(
                    f"{self._relative(path)}: unsafe generated tag route "
                    f"{route!r}"
                )

        url_contexts = []
        for path in self.blog_html_files:
            soup = self._soup(path)
            for anchor in soup.find_all("a", href=True):
                parts = self._internal_url_parts(path, anchor.get("href"))
                if parts is not None:
                    url_contexts.append(
                        (
                            f"{self._relative(path)} href",
                            unquote(parts.path or "/"),
                        )
                    )
            for canonical in self._canonical_links(soup):
                value = self._normalized_text(canonical.get("href"))
                url_contexts.append(
                    (
                        f"{self._relative(path)} canonical",
                        unquote(urlsplit(value).path or "/"),
                    )
                )

        _, sitemap_entries, _ = self._parse_sitemap()
        for location in sitemap_entries:
            url_contexts.append(
                ("sitemap.xml", unquote(urlsplit(location).path or "/"))
            )

        for context, route in url_contexts:
            if route == "/tags" or route.startswith("/tags/"):
                if not SAFE_TAG_ROUTE.fullmatch(route):
                    problems.append(
                        f"{context}: tag URL is not a lower-case safe slug: "
                        f"{route!r}"
                    )
                if route.casefold().endswith(".html"):
                    problems.append(
                        f"{context}: legacy .html tag URL leaked: {route!r}"
                    )

        self._assert_no_problems(problems)

    def test_images_have_accessible_dimensions_and_loading_hints(self):
        problems = []
        for path in self.blog_html_files:
            relative = self._relative(path)
            soup = self._soup(path)
            for image_number, image in enumerate(
                soup.find_all("img"),
                start=1,
            ):
                context = f"{relative} image {image_number}"
                src = self._normalized_text(image.get("src"))
                if not src:
                    problems.append(f"{context}: missing src")
                    continue

                if str(image.get("decoding", "")).casefold() != "async":
                    problems.append(
                        f"{context}: decoding must be async ({src!r})"
                    )

                parts = self._internal_url_parts(path, src)
                is_local = parts is not None
                if is_local:
                    output_path = self._resolve_output_path(parts.path)
                    if output_path is None or not output_path.is_file():
                        problems.append(
                            f"{context}: local image does not resolve "
                            f"({src!r})"
                        )

                    alt = self._normalized_text(image.get("alt"))
                    if not alt:
                        problems.append(
                            f"{context}: local image needs non-empty alt text "
                            f"({src!r})"
                        )
                    elif GENERIC_ALT_TEXT.fullmatch(alt):
                        problems.append(
                            f"{context}: local image alt text is generic "
                            f"({alt!r})"
                        )

                    for dimension in ("width", "height"):
                        value = self._normalized_text(image.get(dimension))
                        if not value.isdigit() or int(value) <= 0:
                            problems.append(
                                f"{context}: local image needs a positive "
                                f"numeric {dimension} ({src!r})"
                            )

                article = image.find_parent("article")
                near_top_article_image = False
                near_top_template_image = False
                if article is not None and article.find("img") is image:
                    preceding_text = []
                    for node in article.descendants:
                        if node is image:
                            break
                        if not isinstance(node, NavigableString):
                            continue
                        if node.find_parent(
                            ["header", "script", "style", "noscript", "template"]
                        ):
                            continue
                        preceding_text.append(str(node))
                    normalized_prefix = self._normalized_text(
                        " ".join(preceding_text)
                    )
                    near_top_article_image = len(normalized_prefix) < 200
                elif article is None:
                    main = image.find_parent("main")
                    if main is not None:
                        preceding_text = []
                        for node in main.descendants:
                            if node is image:
                                break
                            if not isinstance(node, NavigableString):
                                continue
                            if node.find_parent(
                                ["script", "style", "noscript", "template"]
                            ):
                                continue
                            preceding_text.append(str(node))
                        near_top_template_image = (
                            len(
                                self._normalized_text(
                                    " ".join(preceding_text)
                                )
                            )
                            < NEAR_TOP_PAGE_TEXT_LIMIT
                        )

                loading = str(image.get("loading", "")).casefold()
                if (
                    near_top_article_image or near_top_template_image
                ) and loading == "lazy":
                    problems.append(
                        f"{context}: near-top image must not be lazy-loaded "
                        f"({src!r})"
                    )
                elif (
                    not near_top_article_image
                    and not near_top_template_image
                    and loading != "lazy"
                ):
                    problems.append(
                        f"{context}: image must use loading=lazy ({src!r})"
                    )
                if (
                    near_top_article_image
                    and str(image.get("fetchpriority", "")).casefold() != "high"
                ):
                    problems.append(
                        f"{context}: near-top article image must use "
                        f"fetchpriority=high ({src!r})"
                    )

                if article is None:
                    for dimension in ("width", "height"):
                        value = self._normalized_text(image.get(dimension))
                        if not value.isdigit() or int(value) <= 0:
                            problems.append(
                                f"{context}: template image needs a positive "
                                f"numeric {dimension} ({src!r})"
                            )

        self._assert_no_problems(problems)

    def test_translation_pages_have_reciprocal_hreflang(self):
        problems = []
        expected_pairs = []
        for language in ("en", "it"):
            translation_dir = ROOT / language
            if not translation_dir.is_dir():
                continue
            for source in translation_dir.glob("*.md"):
                slug = source.stem.lower()
                expected_pairs.append(
                    (
                        language,
                        self.dist / "posts" / f"{slug}.html",
                        self.dist / language / f"{slug}.html",
                    )
                )

        self.assertTrue(
            expected_pairs,
            "Expected checked-in story translations",
        )

        for translated_language, original_path, translated_path in expected_pairs:
            pair_context = (
                f"{translated_language}/{translated_path.stem}"
            )
            if not original_path.is_file():
                problems.append(
                    f"{pair_context}: missing original generated page "
                    f"{self._relative(original_path)}"
                )
                continue
            if not translated_path.is_file():
                problems.append(
                    f"{pair_context}: missing translated generated page "
                    f"{self._relative(translated_path)}"
                )
                continue

            original_soup = self._soup(original_path)
            translated_soup = self._soup(translated_path)
            original_alternates = self._hreflang_map(original_soup)
            translated_alternates = self._hreflang_map(translated_soup)

            for page_path, alternates in (
                (original_path, original_alternates),
                (translated_path, translated_alternates),
            ):
                relative = self._relative(page_path)
                if set(alternates) != {"en", "it", "x-default"}:
                    problems.append(
                        f"{relative}: hreflang set must be en, it, and "
                        f"x-default; got {sorted(alternates)}"
                    )
                for language, urls in alternates.items():
                    if len(urls) != 1:
                        problems.append(
                            f"{relative}: hreflang {language!r} must appear "
                            f"once, found {len(urls)}"
                        )
                        continue
                    url = urls[0]
                    problems.extend(
                        self._canonical_url_problems(
                            url,
                            f"{relative} hreflang {language}",
                        )
                    )
                    target = self._resolve_output_path(urlsplit(url).path)
                    if target is None:
                        problems.append(
                            f"{relative}: hreflang {language!r} does not "
                            f"resolve: {url!r}"
                        )
                    elif self._canonical_for_file(target) != url:
                        problems.append(
                            f"{relative}: hreflang {language!r} is not the "
                            f"target page's canonical URL: {url!r}"
                        )

            original_flat = {
                language: urls[0]
                for language, urls in original_alternates.items()
                if len(urls) == 1
            }
            translated_flat = {
                language: urls[0]
                for language, urls in translated_alternates.items()
                if len(urls) == 1
            }
            if original_flat != translated_flat:
                problems.append(
                    f"{pair_context}: original and translation do not expose "
                    "the same reciprocal hreflang URLs"
                )

            original_canonical = self._canonical_for_file(original_path)
            translated_canonical = self._canonical_for_file(translated_path)
            original_language = self._normalized_text(
                original_soup.html.get("lang") if original_soup.html else ""
            ).casefold()
            translated_page_language = self._normalized_text(
                translated_soup.html.get("lang")
                if translated_soup.html
                else ""
            ).casefold()
            if {original_language, translated_page_language} != {"en", "it"}:
                problems.append(
                    f"{pair_context}: paired page languages must be en and "
                    f"it, got {original_language!r} and "
                    f"{translated_page_language!r}"
                )
            if original_flat.get(original_language) != original_canonical:
                problems.append(
                    f"{pair_context}: original language alternate must match "
                    "the original self-canonical URL"
                )
            if (
                translated_flat.get(translated_page_language)
                != translated_canonical
            ):
                problems.append(
                    f"{pair_context}: translated language alternate must "
                    "match the translated self-canonical URL"
                )
            if original_flat.get("x-default") != original_canonical:
                problems.append(
                    f"{pair_context}: x-default must point to the original "
                    "story"
                )

        self._assert_no_problems(problems)

    def test_sitemap_is_valid_complete_and_matches_html_alternates(self):
        root, entries, duplicates = self._parse_sitemap()
        self.assertEqual(
            root.tag,
            f"{{{SITEMAP_NAMESPACE}}}urlset",
        )
        self.assertTrue(entries, "Sitemap must contain URL entries")
        self.assertFalse(duplicates, f"Duplicate sitemap URLs: {duplicates}")
        self.assertFalse(
            root.findall(f".//{{{SITEMAP_NAMESPACE}}}lastmod"),
            "Sitemap must omit lastmod until source content tracks updates",
        )

        problems = []
        expected_canonicals = {
            self._canonical_for_file(path)
            for path in self.indexable_html_files
        }
        actual_canonicals = set(entries)
        missing = expected_canonicals - actual_canonicals
        unexpected = actual_canonicals - expected_canonicals
        if missing:
            problems.append(
                "sitemap.xml: missing indexable canonical URLs: "
                + ", ".join(sorted(missing))
            )
        if unexpected:
            problems.append(
                "sitemap.xml: unexpected/non-indexable URLs: "
                + ", ".join(sorted(unexpected))
            )

        for location, sitemap_alternates in entries.items():
            problems.extend(
                self._canonical_url_problems(
                    location,
                    "sitemap.xml loc",
                )
            )
            route = unquote(urlsplit(location).path or "/")
            if route.casefold().rstrip("/") in {
                "/404",
                "/404.html",
                "/feed",
                "/feed.xml",
            }:
                problems.append(
                    f"sitemap.xml: excluded URL is present: {location!r}"
                )
            target = self._resolve_output_path(route)
            if target is None or target.suffix.casefold() != ".html":
                problems.append(
                    f"sitemap.xml: loc does not resolve to generated HTML: "
                    f"{location!r}"
                )
                continue

            html_alternates = self._hreflang_map(self._soup(target))
            normalized_sitemap_alternates = {
                language: urls
                for language, urls in sitemap_alternates.items()
            }
            normalized_html_alternates = {
                language: urls
                for language, urls in html_alternates.items()
            }
            if normalized_sitemap_alternates != normalized_html_alternates:
                problems.append(
                    f"sitemap.xml: alternates for {location!r} do not match "
                    "the HTML hreflang links"
                )

            for language, urls in sitemap_alternates.items():
                if not language:
                    problems.append(
                        f"sitemap.xml: {location!r} has an empty hreflang"
                    )
                if len(urls) != 1:
                    problems.append(
                        f"sitemap.xml: {location!r} has {len(urls)} "
                        f"{language!r} alternates"
                    )
                for alternate_url in urls:
                    problems.extend(
                        self._canonical_url_problems(
                            alternate_url,
                            f"sitemap.xml alternate for {location}",
                        )
                    )

        self._assert_no_problems(problems)

    def test_feed_is_valid_and_uses_canonical_item_urls(self):
        root = ET.parse(self.dist / "feed.xml").getroot()
        self.assertEqual(root.tag, "rss")
        channel = root.find("channel")
        self.assertIsNotNone(channel, "RSS feed must contain a channel")
        self.assertIn(
            self._normalized_text(channel.findtext("link")),
            {SITE_ORIGIN, f"{SITE_ORIGIN}/"},
        )
        last_build_date = parsedate_to_datetime(
            self._normalized_text(channel.findtext("lastBuildDate"))
        )
        self.assertLess(
            abs((datetime.now(timezone.utc) - last_build_date).total_seconds()),
            300,
            "RSS lastBuildDate must reflect the current build",
        )

        items = channel.findall("item")
        self.assertTrue(items, "RSS feed must contain items")
        problems = []
        for item_number, item in enumerate(items, start=1):
            link = self._normalized_text(item.findtext("link"))
            guid = self._normalized_text(item.findtext("guid"))
            context = f"feed.xml item {item_number}"
            problems.extend(
                self._canonical_url_problems(link, f"{context} link")
            )
            if guid != link:
                problems.append(
                    f"{context}: GUID must equal the canonical item URL; "
                    f"link={link!r}, guid={guid!r}"
                )
            target = self._resolve_output_path(urlsplit(link).path)
            if target is None or target.parent != self.dist / "posts":
                problems.append(
                    f"{context}: item URL does not resolve to an original "
                    f"generated post: {link!r}"
                )
            elif self._canonical_for_file(target) != link:
                problems.append(
                    f"{context}: item URL is not the target post's canonical "
                    f"URL: {link!r}"
                )

        self._assert_no_problems(problems)

    def test_redirects_cover_canonical_and_legacy_routes(self):
        redirects = self._parse_redirects()
        problems = []

        def require(source, target):
            actual = redirects.get(source)
            if actual is None:
                problems.append(
                    f"_redirects: missing {source!r} -> {target!r}"
                )
                return
            actual_target, status = actual
            if actual_target != target:
                problems.append(
                    f"_redirects: {source!r} targets {actual_target!r}, "
                    f"expected {target!r}"
                )
            if status != "301!":
                problems.append(
                    f"_redirects: {source!r} must be a forced 301, got "
                    f"{status!r}"
                )

        require("/index.html", f"{SITE_ORIGIN}/")
        for path in self.indexable_html_files:
            route = self._route_for_file(path)
            if route == "/":
                continue
            require(f"{route}.html", self._canonical_for_file(path))

        schedule = self.dist / "Schedule.html"
        if schedule.is_file():
            require("/Schedule.html", f"{SITE_ORIGIN}/Schedule")

        mixed_case_sources = []
        for source_post in (ROOT / "posts").glob("*.md"):
            source_slug = source_post.stem
            canonical_slug = source_slug.lower()
            target = f"{SITE_ORIGIN}/posts/{canonical_slug}"

            match = re.fullmatch(
                r"(\d{4})-(\d{2})-(\d{2})-(.+)",
                source_slug,
            )
            if match:
                year, month, day, legacy_slug = match.groups()
                date_route = f"/{year}/{month}/{day}/{legacy_slug}"
                for alias in (
                    date_route,
                    f"{date_route}/",
                    f"{date_route}.html",
                ):
                    require(alias, target)
                if date_route != date_route.lower():
                    lower_date_route = date_route.lower()
                    for alias in (
                        lower_date_route,
                        f"{lower_date_route}/",
                        f"{lower_date_route}.html",
                    ):
                        require(alias, target)

            if source_slug != canonical_slug:
                mixed_case_sources.append(source_slug)
                require(f"/posts/{source_slug}", target)
                require(f"/posts/{source_slug}.html", target)

        if not mixed_case_sources:
            problems.append(
                "Test fixture must include at least one mixed-case legacy slug"
            )

        for source in (
            "http://lucabol.com/*",
            "https://lucabol.com/*",
            "http://www.lucabol.com/*",
        ):
            require(source, f"{SITE_ORIGIN}/:splat")

        for source, (target, status) in redirects.items():
            if not target.startswith(f"{SITE_ORIGIN}/"):
                problems.append(
                    f"_redirects: target must be absolute canonical origin: "
                    f"{source!r} -> {target!r}"
                )
            if urlsplit(target).path.casefold().endswith(".html"):
                problems.append(
                    f"_redirects: target must be extensionless: "
                    f"{source!r} -> {target!r}"
                )
            if ":splat" not in target:
                resolved_target = self._resolve_output_path(
                    urlsplit(target).path
                )
                if resolved_target is None:
                    problems.append(
                        f"_redirects: target does not resolve to generated "
                        f"output: {source!r} -> {target!r}"
                    )
                elif (
                    resolved_target.suffix.casefold() == ".html"
                    and self._canonical_for_file(resolved_target) != target
                ):
                    problems.append(
                        f"_redirects: target is not the output's canonical "
                        f"URL: {source!r} -> {target!r}"
                    )
            if status != "301!":
                problems.append(
                    f"_redirects: redirect must use 301!: {source!r}"
                )

        self._assert_no_problems(problems)

    def test_css_has_required_responsive_and_readability_guards(self):
        css = (self.dist / "static" / "style.css").read_text(encoding="utf-8")
        rules = self._parse_css_rules(css)
        problems = []

        custom_properties = {}
        for rule in self._css_rules_for_selector(rules, ":root"):
            custom_properties.update(
                {
                    name: value
                    for name, value in rule["declarations"].items()
                    if name.startswith("--")
                }
            )

        responsive_rules = [
            rule
            for rule in rules
            if any(
                re.search(r"(?:min|max)-width", query, re.IGNORECASE)
                for query in rule["media"]
            )
        ]
        if not responsive_rules:
            problems.append(
                "static/style.css: expected responsive width media queries"
            )

        font_faces = self._css_rules_for_selector(rules, "@font-face")
        if not font_faces:
            problems.append("static/style.css: expected @font-face rules")
        for index, rule in enumerate(font_faces, start=1):
            if rule["declarations"].get("font-display", "").casefold() != "swap":
                problems.append(
                    f"static/style.css: @font-face {index} must use "
                    "font-display: swap"
                )

        pre_overflow = any(
            rule["declarations"].get("overflow-x", "").casefold()
            in {"auto", "scroll"}
            and any(re.search(r"(^|[^a-z-])pre([^a-z-]|$)", selector) for selector in rule["selectors"])
            for rule in rules
        )
        if not pre_overflow:
            problems.append(
                "static/style.css: pre/code blocks need horizontal overflow"
            )

        direct_table_overflow = any(
            rule["declarations"].get("overflow-x", "").casefold()
            in {"auto", "scroll"}
            and any(
                re.search(r"(^|[\s>+~])table(?:$|[:.\s>+~#])", selector)
                for selector in rule["selectors"]
            )
            for rule in rules
        )
        table_scroll_wrapper = any(
            ".table-scroll" in rule["selectors"]
            and rule["declarations"].get("overflow-x", "").casefold()
            in {"auto", "scroll"}
            for rule in rules
        )
        if not direct_table_overflow and not table_scroll_wrapper:
            problems.append(
                "static/style.css: narrow tables need horizontal overflow"
            )
        elif table_scroll_wrapper and not direct_table_overflow:
            for path in self.generated_blog_html_files:
                for table_number, table in enumerate(
                    self._soup(path).find_all("table"),
                    start=1,
                ):
                    if table.find_parent(class_="table-scroll") is None:
                        problems.append(
                            f"{self._relative(path)} table {table_number}: "
                            "table must use the CSS overflow wrapper"
                        )

        mobile_search_stacks = any(
            rule["media"]
            and (
                (
                    ".search-fields" in rule["selectors"]
                    and rule["declarations"].get(
                        "flex-direction",
                        "",
                    ).casefold()
                    == "column"
                )
                or (
                    ".search" in rule["selectors"]
                    and rule["declarations"].get("display", "").casefold()
                    == "grid"
                    and "1fr"
                    in rule["declarations"].get(
                        "grid-template-columns",
                        "",
                    ).casefold()
                )
            )
            for rule in responsive_rules
        )
        if not mobile_search_stacks:
            problems.append(
                "static/style.css: site-search controls must stack in a "
                "mobile media query"
            )

        skip_link_rules = self._css_rules_for_selector(rules, ".skip-link")
        if not skip_link_rules:
            problems.append(
                "static/style.css: missing base .skip-link styling"
            )
        else:
            if any(
                rule["declarations"].get("display", "").casefold() == "none"
                or rule["declarations"].get(
                    "visibility",
                    "",
                ).casefold()
                == "hidden"
                for rule in skip_link_rules
            ):
                problems.append(
                    "static/style.css: skip link must remain focusable while "
                    "visually hidden"
                )
            hidden_offscreen = any(
                rule["declarations"].get("top", "").lstrip().startswith("-")
                or re.search(
                    r"translate[xy]?\([^)]*-",
                    rule["declarations"].get("transform", ""),
                    re.IGNORECASE,
                )
                or "clip" in rule["declarations"]
                or "clip-path" in rule["declarations"]
                for rule in skip_link_rules
            )
            if not hidden_offscreen:
                problems.append(
                    "static/style.css: skip link needs a non-focus hidden "
                    "position"
                )

        skip_focus_rules = [
            rule
            for rule in rules
            if any(
                re.search(
                    r"\.skip-link:(?:focus|focus-visible)(?:\b|:)",
                    selector,
                )
                for selector in rule["selectors"]
            )
        ]
        focus_reveals_link = any(
            (
                "top" in rule["declarations"]
                and not rule["declarations"]["top"].lstrip().startswith("-")
            )
            or rule["declarations"].get("transform", "").casefold()
            in {"none", "translate(0)", "translatey(0)", "translatex(0)"}
            or rule["declarations"].get("clip", "").casefold() in {
                "auto",
                "none",
            }
            or rule["declarations"].get("clip-path", "").casefold() == "none"
            for rule in skip_focus_rules
        )
        if not focus_reveals_link:
            problems.append(
                "static/style.css: .skip-link needs a focus rule that brings "
                "it on screen"
            )

        def target_sizes(selector):
            matched = self._css_rules_for_selector(rules, selector)
            min_height_values = [
                rule["declarations"]["min-height"]
                for rule in matched
                if "min-height" in rule["declarations"]
            ]
            values = min_height_values or [
                rule["declarations"]["height"]
                for rule in matched
                if "height" in rule["declarations"]
            ]
            return [
                self._css_length_px(value, custom_properties)
                for value in values
            ]

        for selector in (".site-nav a", ".search input", ".search button"):
            sizes = target_sizes(selector)
            if not sizes or any(size is None or size < 44 for size in sizes):
                problems.append(
                    f"static/style.css: {selector} needs a mechanically "
                    "verifiable minimum 44px target height"
                )

        for selector in (
            ".posts-list > li > a",
            ".tags-list a",
            ".year-jump a",
        ):
            sizes = target_sizes(selector)
            if not sizes or any(size is None or size < 24 for size in sizes):
                problems.append(
                    f"static/style.css: {selector} archive links need a "
                    "minimum 24px target height"
                )

        footer_text_selectors = (
            ".site-footer",
            ".search label",
            ".public-domain",
            ".back-to-top",
        )
        for selector in footer_text_selectors:
            for rule in self._css_rules_for_selector(rules, selector):
                value = rule["declarations"].get("font-size")
                if value is None or value.casefold() in {
                    "inherit",
                    "initial",
                    "unset",
                }:
                    continue
                size = self._css_length_px(value, custom_properties)
                if size is None or size < 16:
                    problems.append(
                        f"static/style.css: {selector} font-size {value!r} "
                        "is below the 1rem base readable size"
                    )

        self._assert_no_problems(problems)

    def test_css_preserves_editorial_navigation_and_title_typography(self):
        css = (self.dist / "static" / "style.css").read_text(encoding="utf-8")
        rules = self._parse_css_rules(css)

        def base_declarations(selector):
            declarations = {}
            for rule in self._css_rules_for_selector(rules, selector):
                if not rule["media"]:
                    declarations.update(rule["declarations"])
            return declarations

        root = base_declarations(":root")
        self.assertEqual(
            root.get("--base-size"),
            "clamp(1rem, 2.2vw, 1.5rem)",
        )

        navigation = base_declarations(".site-nav a")
        self.assertEqual(navigation.get("font-family"), "var(--font-text)")
        self.assertNotIn("letter-spacing", navigation)
        self.assertIn(navigation.get("font-weight", "400"), {"400", "normal"})
        active_navigation = base_declarations(
            '.site-nav a[aria-current="page"]'
        )
        self.assertIn(
            active_navigation.get("font-weight", "400"),
            {"400", "normal"},
        )

        title = base_declarations("h1")
        self.assertEqual(title.get("font-family"), "var(--font-heading)")
        self.assertEqual(title.get("font-size"), "1.3em")
        self.assertEqual(title.get("font-weight"), "400")

        heading_font = next(
            rule["declarations"]
            for rule in self._css_rules_for_selector(rules, "@font-face")
            if rule["declarations"].get("font-family", "").strip("\"'")
            == "MyTrebuchet"
        )
        self.assertTrue(
            heading_font.get("src", "").startswith('local("Trebuchet MS")')
        )
        self.assertNotIn("Trebuchet MS Bold", heading_font.get("src", ""))
        self.assertEqual(heading_font.get("font-weight"), "400")

    def test_css_preserves_editorial_content_measure_and_list_inset(self):
        css = (self.dist / "static" / "style.css").read_text(encoding="utf-8")
        rules = self._parse_css_rules(css)

        def base_declarations(selector):
            declarations = {}
            for rule in self._css_rules_for_selector(rules, selector):
                if not rule["media"]:
                    declarations.update(rule["declarations"])
            return declarations

        def mobile_declarations(selector):
            declarations = {}
            for rule in self._css_rules_for_selector(rules, selector):
                if any(
                    "max-width: 36rem" in query
                    for query in rule["media"]
                ):
                    declarations.update(rule["declarations"])
            return declarations

        root = base_declarations(":root")
        self.assertEqual(root.get("--page-width"), "48rem")

        body = base_declarations("body")
        self.assertEqual(body.get("max-width"), "var(--page-width)")
        self.assertEqual(
            body.get("padding"),
            "var(--space-2) var(--space-8)",
        )
        self.assertEqual(body.get("line-height"), "1.3")
        for rule in self._css_rules_for_selector(rules, "body"):
            if rule["media"]:
                self.assertNotIn("padding-inline", rule["declarations"])

        posts_list = base_declarations(".posts-list")
        self.assertEqual(posts_list.get("padding-inline-start"), "2rem")
        self.assertEqual(posts_list.get("line-height"), "1.1")
        posts_list_link = base_declarations(".posts-list > li > a")
        self.assertEqual(posts_list_link.get("vertical-align"), "top")

        recent_posts_list = base_declarations(".recent-notes .posts-list")
        self.assertEqual(recent_posts_list.get("max-width"), "36rem")
        self.assertEqual(recent_posts_list.get("margin-inline"), "auto")
        self.assertEqual(recent_posts_list.get("text-align"), "left")

        post_meta = base_declarations(".post-meta")
        self.assertEqual(post_meta.get("font-size"), "1em")
        self.assertEqual(post_meta.get("line-height"), "1.3")
        self.assertEqual(post_meta.get("color"), "var(--color-text)")

        post_content = base_declarations(".post-content")
        self.assertEqual(post_content.get("line-height"), "1.4")
        post_paragraph = base_declarations(".post-content p")
        self.assertEqual(post_paragraph.get("margin-block"), "1lh")

        mobile_main = mobile_declarations("main")
        self.assertEqual(mobile_main.get("padding-block-start"), "0")

        mobile_year_jump = mobile_declarations(".year-jump")
        self.assertEqual(mobile_year_jump.get("display"), "block")
        self.assertEqual(
            mobile_year_jump.get("margin-bottom"),
            "var(--space-6)",
        )
        self.assertEqual(mobile_year_jump.get("text-align"), "center")

        mobile_year_jump_label = mobile_declarations(".year-jump-label")
        self.assertEqual(mobile_year_jump_label.get("display"), "block")
        self.assertEqual(
            mobile_year_jump_label.get("margin-bottom"),
            "var(--space-1)",
        )

        mobile_year_jump_list = mobile_declarations(".year-jump ol")
        self.assertEqual(
            mobile_year_jump_list.get("gap"),
            "0 var(--space-1)",
        )

        mobile_year_jump_link = mobile_declarations(".year-jump a")
        self.assertEqual(
            mobile_year_jump_link.get("min-width"),
            "var(--compact-target)",
        )
        self.assertEqual(
            mobile_year_jump_link.get("min-height"),
            "var(--compact-target)",
        )
        self.assertEqual(
            mobile_year_jump_link.get("padding-inline"),
            "0.125rem",
        )

    def test_headers_include_security_and_asset_cache_policies(self):
        blocks = self._parse_headers(
            (self.dist / "_headers").read_text(encoding="utf-8")
        )
        self.assertIn("/*", blocks, "_headers must define a site-wide block")
        site_headers = blocks["/*"]

        required_security_headers = {
            "content-security-policy",
            "permissions-policy",
            "referrer-policy",
            "strict-transport-security",
            "x-content-type-options",
            "x-frame-options",
        }
        self.assertEqual(
            required_security_headers - set(site_headers),
            set(),
            "Missing required security headers",
        )
        self.assertIn(
            "default-src",
            site_headers["content-security-policy"].casefold(),
        )
        self.assertIn(
            "frame-ancestors",
            site_headers["content-security-policy"].casefold(),
        )
        self.assertEqual(
            site_headers["x-content-type-options"].casefold(),
            "nosniff",
        )
        self.assertTrue(site_headers["permissions-policy"])
        self.assertTrue(site_headers["referrer-policy"])
        self.assertTrue(site_headers["x-frame-options"])

        stable_asset_patterns = ["/fonts/*", "/img/*"]
        for image_name in ("favicon.ico", "favicon.svg", "fluidicon.png"):
            if (self.dist / image_name).is_file():
                stable_asset_patterns.append(f"/{image_name}")

        stable_asset_ages = []
        for asset_pattern in stable_asset_patterns:
            self.assertIn(
                asset_pattern,
                blocks,
                f"_headers must define caching for {asset_pattern}",
            )
            cache_control = blocks[asset_pattern].get("cache-control", "")
            max_age = self._cache_max_age(cache_control)
            self.assertIsNotNone(
                max_age,
                f"{asset_pattern} must define max-age",
            )
            self.assertGreater(
                max_age,
                0,
                f"{asset_pattern} must define positive caching",
            )
            self.assertLessEqual(
                max_age,
                86_400,
                f"{asset_pattern} must remain safely revalidatable",
            )
            directives = {
                directive.strip().casefold()
                for directive in cache_control.split(",")
            }
            self.assertNotIn(
                "immutable",
                directives,
                f"{asset_pattern} has an unversioned URL and cannot be immutable",
            )
            self.assertIn(
                "public",
                directives,
                f"{asset_pattern} must be publicly cacheable",
            )
            stable_asset_ages.append(max_age)

        self.assertTrue(
            list((self.dist / "static").glob("*.css")),
            "The static policy must cover generated CSS",
        )
        self.assertTrue(
            list((self.dist / "static").glob("*.js")),
            "The static policy must cover generated JavaScript",
        )
        self.assertIn(
            "/static/*",
            blocks,
            "_headers must define a CSS/JS cache policy",
        )
        static_cache = blocks["/static/*"].get("cache-control", "")
        static_age = self._cache_max_age(static_cache)
        self.assertIsNotNone(static_age, "/static/* must define max-age")
        self.assertGreater(static_age, 0)
        self.assertLessEqual(
            static_age,
            min(stable_asset_ages),
            "CSS/JS caching must not outlive other stable asset URLs",
        )
        self.assertNotIn(
            "immutable",
            {
                directive.strip().casefold()
                for directive in static_cache.split(",")
            },
            "CSS/JS must remain revalidatable rather than immutable",
        )

        xml_ages = []
        for xml_path in ("/feed.xml", "/sitemap.xml"):
            self.assertIn(
                xml_path,
                blocks,
                f"_headers must define an explicit policy for {xml_path}",
            )
            xml_cache = blocks[xml_path].get("cache-control", "")
            xml_age = self._cache_max_age(xml_cache)
            self.assertIsNotNone(
                xml_age,
                f"{xml_path} must define max-age",
            )
            self.assertGreater(xml_age, 0)
            self.assertLess(
                xml_age,
                static_age,
                f"{xml_path} must refresh more often than CSS/JS",
            )
            xml_directives = {
                directive.strip().casefold()
                for directive in xml_cache.split(",")
            }
            self.assertIn(
                "must-revalidate",
                xml_directives,
                f"{xml_path} must require revalidation",
            )
            self.assertNotIn(
                "immutable",
                xml_directives,
                f"{xml_path} must not be immutable",
            )
            xml_ages.append(xml_age)

        self.assertEqual(
            len(xml_ages),
            2,
            "Both feed.xml and sitemap.xml need short cache policies",
        )

    def test_deploy_workflow_fails_on_invalid_netlify_responses(self):
        workflow = (ROOT / ".github" / "workflows" / "deploy.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("if: github.event_name != 'pull_request'", workflow)
        self.assertIn("curl --fail-with-body --silent --show-error", workflow)
        self.assertIn("jq -e '.id | strings | length > 0'", workflow)


if __name__ == "__main__":
    unittest.main()
