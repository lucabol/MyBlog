import hashlib
import html
import os
import re
import shutil
import unicodedata
import urllib.parse
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

import frontmatter
import markdown
import yaml
from bs4 import BeautifulSoup, NavigableString
from jinja2 import Environment, FileSystemLoader, select_autoescape
from PIL import Image

from translate import (
    has_api_key,
    load_translation,
    print_api_key_info,
    save_translation,
    translate_story,
    translation_exists,
)


SITE_URL = "https://www.lucabol.com"
SITE_NAME = "Luca Bolognese"
SITE_AUTHOR = "Luca Bolognese"
SITE_DESCRIPTION = (
    "Writing by Luca Bolognese about software, books, investing, "
    "short stories, and other interests."
)
DEFAULT_SOCIAL_IMAGE = "/fluidicon.png"


class BlogGenerator:
    def __init__(self, posts_dir, output_dir):
        self.posts_dir = Path(posts_dir)
        self.output_dir = Path(output_dir)
        self.root_dir = Path.cwd()
        self.posts = []
        self.translated_posts = []
        self.tags = defaultdict(list)
        self.sitemap_pages = []
        self.redirects = []
        self.env = Environment(
            loader=FileSystemLoader("src/templates"),
            autoescape=select_autoescape(enabled_extensions=("html", "xml")),
        )
        self.site = {
            "name": SITE_NAME,
            "url": SITE_URL,
            "author": SITE_AUTHOR,
            "feed_url": f"{SITE_URL}/feed.xml",
            "default_image_url": f"{SITE_URL}{DEFAULT_SOCIAL_IMAGE}",
            "stylesheet_url": self._versioned_asset_url(
                "src/style.css",
                "/static/style.css",
            ),
            "story_language_script_url": self._versioned_asset_url(
                "src/story-language.js",
                "/static/story-language.js",
            ),
        }

    def _versioned_asset_url(self, source_path, public_path):
        source = self.root_dir / source_path
        digest = hashlib.sha256(source.read_bytes()).hexdigest()[:12]
        return f"{public_path}?v={digest}"

    def _ensure_dir(self, path):
        Path(path).mkdir(parents=True, exist_ok=True)

    def _write_file(self, path, content):
        path = Path(path)
        self._ensure_dir(path.parent)
        path.write_text(content, encoding="utf-8")

    def _absolute_url(self, path):
        if not path:
            return None
        if path.startswith(("http://", "https://")):
            return path
        return f"{SITE_URL}/{path.lstrip('/')}" if path != "/" else f"{SITE_URL}/"

    def _page_context(
        self,
        *,
        title,
        description,
        path=None,
        lang="en",
        alternates=None,
        og_type="website",
        image_url=None,
        twitter_card=None,
        robots=None,
        json_ld=None,
        current_section=None,
    ):
        canonical_url = self._absolute_url(path) if path is not None else None
        social_image = self._absolute_url(image_url or DEFAULT_SOCIAL_IMAGE)
        return {
            "title": title,
            "description": description,
            "lang": lang,
            "og_locale": "it_IT" if lang == "it" else "en_US",
            "canonical_path": path,
            "canonical_url": canonical_url,
            "alternates": alternates or [],
            "og_type": og_type,
            "image_url": social_image,
            "twitter_card": twitter_card
            or ("summary_large_image" if image_url else "summary"),
            "robots": robots,
            "json_ld": json_ld,
            "current_section": current_section,
        }

    def _render_and_write(
        self,
        template_name,
        output_path,
        *,
        page=None,
        register=True,
        lastmod=None,
        **kwargs,
    ):
        template = self.env.get_template(template_name)
        content = template.render(
            site=self.site,
            page=page or {},
            year=datetime.now().year,
            **kwargs,
        )
        self._write_file(self.output_dir / output_path, content)

        if (
            register
            and page
            and page.get("canonical_url")
            and page.get("robots") != "noindex"
        ):
            self._register_sitemap_page(
                page["canonical_url"],
                lastmod=lastmod,
                alternates=page.get("alternates", []),
            )

    def _register_sitemap_page(self, url, *, lastmod=None, alternates=None):
        if any(page["url"] == url for page in self.sitemap_pages):
            return
        self.sitemap_pages.append(
            {
                "url": url,
                "lastmod": lastmod,
                "alternates": alternates or [],
            }
        )

    def _encode_redirect_source(self, source):
        if source.startswith(("http://", "https://")):
            parsed = urllib.parse.urlsplit(source)
            path = urllib.parse.quote(
                urllib.parse.unquote(parsed.path),
                safe="/:._~-*",
            )
            return urllib.parse.urlunsplit(
                (parsed.scheme, parsed.netloc, path, parsed.query, parsed.fragment)
            )
        return urllib.parse.quote(
            urllib.parse.unquote(source),
            safe="/:._~-*",
        )

    def _register_redirect(self, source, target):
        source = self._encode_redirect_source(source)
        target = self._absolute_url(target)
        if not source or not target or source == target:
            return
        redirect = (source, target)
        if redirect not in self.redirects:
            self.redirects.append(redirect)

    def _register_html_redirect(self, canonical_path):
        if canonical_path and canonical_path != "/":
            self._register_redirect(f"{canonical_path}.html", canonical_path)

    def _process_post_date(self, post_date):
        if post_date:
            if isinstance(post_date, date) and not isinstance(post_date, datetime):
                post_date = datetime.combine(post_date, datetime.min.time())
            if getattr(post_date, "tzinfo", None) is not None:
                post_date = post_date.replace(tzinfo=None)
        return post_date

    def _process_post_author(self, author):
        return SITE_AUTHOR if author == "lucabol" else (author or "Anonymous")

    def _convert_markdown(self, content):
        return markdown.markdown(
            content,
            extensions=[
                "fenced_code",
                "tables",
                "sane_lists",
                "smarty",
                "attr_list",
            ],
        )

    def _local_asset_path(self, src):
        parsed = urllib.parse.urlsplit(src)
        if parsed.scheme or parsed.netloc:
            if parsed.netloc.lower() not in {"lucabol.com", "www.lucabol.com"}:
                return None
        relative = urllib.parse.unquote(parsed.path).lstrip("/")
        if not relative:
            return None
        candidate = (self.root_dir / relative).resolve()
        try:
            candidate.relative_to(self.root_dir.resolve())
        except ValueError:
            return None
        return candidate if candidate.is_file() else None

    def _image_dimensions(self, src):
        asset_path = self._local_asset_path(src)
        if not asset_path:
            return None
        try:
            with Image.open(asset_path) as image:
                return image.size
        except (OSError, ValueError):
            return None

    def _resolve_internal_url(self, url, base_path=None):
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme or parsed.netloc:
            if parsed.scheme not in {"http", "https"}:
                return url, False
            if parsed.netloc.lower() not in {"lucabol.com", "www.lucabol.com"}:
                return url, False
        elif not parsed.path.startswith("/"):
            if not base_path:
                return url, False
            parsed = urllib.parse.urlsplit(
                urllib.parse.urljoin(self._absolute_url(base_path), url)
            )

        resolved_path = urllib.parse.unquote(parsed.path or "/")
        resolved_url = urllib.parse.urlunsplit(
            ("", "", resolved_path, parsed.query, parsed.fragment)
        )
        return resolved_url, True

    def _canonicalize_internal_href(self, href, base_path=None):
        if not href or href.startswith(("#", "mailto:", "tel:", "data:")):
            return href

        resolved_href, is_internal = self._resolve_internal_url(href, base_path)
        if not is_internal:
            return href
        parsed = urllib.parse.urlsplit(resolved_href)
        path = parsed.path
        if path.endswith(".html"):
            path = path[:-5]

        legacy_match = re.fullmatch(
            r"/(\d{4})/(\d{2})/(\d{2})/([^/]+)/?",
            path,
        )
        if legacy_match:
            year, month, day, slug = legacy_match.groups()
            path = f"/posts/{year}-{month}-{day}-{slug.lower()}"
        elif path.startswith("/posts/"):
            path = f"/posts/{path.removeprefix('/posts/').rstrip('/').lower()}"
        elif path.startswith("/tags/"):
            tag = path.removeprefix("/tags/").rstrip("/")
            path = f"/tags/{self._slugify_tag(tag)}"
        elif path != "/":
            path = path.rstrip("/")

        return urllib.parse.urlunsplit(
            ("", "", path or "/", parsed.query, parsed.fragment)
        )

    def _enrich_content_images(self, content, page_path=None):
        soup = BeautifulSoup(content, "html.parser")
        for link in soup.find_all("a", href=True):
            link["href"] = self._canonicalize_internal_href(
                link["href"].strip(),
                page_path,
            )

        for table in soup.find_all("table"):
            wrapper = soup.new_tag(
                "div",
                attrs={
                    "class": "table-scroll",
                    "role": "region",
                    "aria-label": "Scrollable table",
                    "tabindex": "0",
                },
            )
            table.wrap(wrapper)

        images = soup.find_all("img")
        if not images:
            return str(soup), None

        first_image = images[0]
        text_before_first_image = []
        for node in soup.descendants:
            if node is first_image:
                break
            if isinstance(node, NavigableString):
                if node.find_parent(["style", "script", "noscript", "template"]):
                    continue
                text_before_first_image.append(str(node))
        leading_text = re.sub(r"\s+", " ", " ".join(text_before_first_image)).strip()
        first_image_is_likely_above_fold = len(leading_text) < 200

        for index, image in enumerate(images):
            src = image.get("src", "").strip()
            resolved_src, is_internal = self._resolve_internal_url(src, page_path)
            if is_internal:
                src = resolved_src
                image["src"] = src
            dimensions = self._image_dimensions(src)
            if dimensions:
                image["width"], image["height"] = map(str, dimensions)

            image["decoding"] = "async"
            if index == 0 and first_image_is_likely_above_fold:
                image.attrs.pop("loading", None)
                image["fetchpriority"] = "high"
            else:
                image["loading"] = "lazy"
                image.attrs.pop("fetchpriority", None)

        lead_src = first_image.get("src", "").strip()
        lead_image = self._absolute_url(lead_src) if lead_src else None
        return str(soup), lead_image

    def _description_from_html(self, content, fallback):
        soup = BeautifulSoup(content, "html.parser")
        for element in soup.find_all(["p", "li"]):
            if element.find_parent(["pre", "code"]):
                continue
            text = html.unescape(element.get_text(" ", strip=True))
            text = re.sub(r"\s+", " ", text).strip()
            if len(text) >= 40:
                return self._truncate_description(text)
        return self._truncate_description(fallback)

    def _post_description(self, title, content, explicit=None):
        if explicit:
            return self._truncate_description(explicit)
        excerpt = self._description_from_html(content, title)
        if title.lower() in excerpt.lower():
            return excerpt
        return self._truncate_description(f"{title}. {excerpt}")

    def _truncate_description(self, text, limit=160):
        text = re.sub(r"\s+", " ", str(text)).strip()
        if len(text) <= limit:
            return text
        shortened = text[: limit + 1].rsplit(" ", 1)[0].rstrip(" ,;:-")
        return f"{shortened}..."

    def _get_comments_url(self, post_date, title):
        date_str = post_date.strftime("%Y-%m-%d")
        title_words = " ".join(title.split()[:3])
        query = urllib.parse.quote(f"is:issue {date_str} {title_words}")
        return f"https://github.com/lucabol/MyBlog_Comments/issues?q={query}"

    def _slugify_tag(self, tag):
        if tag.strip().lower() == "c++":
            return "c-plus-plus"
        normalized = unicodedata.normalize("NFKD", tag)
        ascii_tag = normalized.encode("ascii", "ignore").decode("ascii").lower()
        return re.sub(r"[^a-z0-9]+", "-", ascii_tag).strip("-")

    def _tag_link(self, tag):
        slug = self._slugify_tag(tag)
        return {
            "name": tag,
            "slug": slug,
            "url": f"/tags/{slug}",
        }

    def _process_post_file(self, filename):
        filepath = self.posts_dir / filename
        post = frontmatter.load(filepath)

        post_date = self._process_post_date(post.get("date"))
        post_title = post.get("title", "Untitled")
        post_tags = [str(tag) for tag in (post.get("tags", []) or [])]
        source_slug = filepath.stem
        slug = source_slug.lower()
        canonical_path = f"/posts/{slug}"
        language = str(post.get("language", "en")).lower()
        converted_content = self._convert_markdown(post.content)
        enriched_content, image_url = self._enrich_content_images(
            converted_content,
            canonical_path,
        )
        description = self._post_description(
            post_title,
            enriched_content,
            explicit=post.get("description"),
        )
        post_data = {
            "title": post_title,
            "date": post_date,
            "author": self._process_post_author(post.get("author")),
            "tags": post_tags,
            "tag_links": [self._tag_link(tag) for tag in post_tags],
            "content": enriched_content,
            "raw_content": post.content,
            "url": canonical_path,
            "output_path": f"posts/{slug}.html",
            "slug": slug,
            "source_slug": source_slug,
            "comments_url": self._get_comments_url(post_date, post_title),
            "description": description,
            "image_url": image_url,
            "is_story": "story" in post_tags,
            "is_translation": False,
            "language": language,
            "has_translation": False,
            "translation": None,
            "translation_url": None,
            "original_url": canonical_path,
            "original_language": language,
            "title_en": post_title if language == "en" else None,
            "title_it": post_title if language == "it" else None,
            "url_en": canonical_path if language == "en" else None,
            "url_it": canonical_path if language == "it" else None,
        }

        self._register_html_redirect(canonical_path)
        if source_slug != slug:
            self._register_redirect(f"/posts/{source_slug}", canonical_path)
            self._register_redirect(f"/posts/{source_slug}.html", canonical_path)

        legacy_match = re.fullmatch(
            r"(\d{4})-(\d{2})-(\d{2})-(.+)",
            source_slug,
        )
        if legacy_match:
            year, month, day, legacy_slug = legacy_match.groups()
            legacy_date_path = f"/{year}/{month}/{day}/{legacy_slug}"
            legacy_date_variants = {
                legacy_date_path,
                f"{legacy_date_path}/",
                f"{legacy_date_path}.html",
            }
            lowercase_date_path = legacy_date_path.lower()
            if lowercase_date_path != legacy_date_path:
                legacy_date_variants.update(
                    {
                        lowercase_date_path,
                        f"{lowercase_date_path}/",
                        f"{lowercase_date_path}.html",
                    }
                )
            for legacy_route in sorted(legacy_date_variants):
                self._register_redirect(legacy_route, canonical_path)

        return post_data

    def read_posts(self):
        for filename in sorted(os.listdir(self.posts_dir)):
            if filename.endswith(".md"):
                post_data = self._process_post_file(filename)
                self.posts.append(post_data)
                for tag in post_data["tags"]:
                    self.tags[tag].append(post_data)

        self.posts.sort(
            key=lambda item: (item["date"], item["slug"]),
            reverse=True,
        )

    def _post_alternates(self, post):
        if not post.get("has_translation"):
            return []
        return [
            {"lang": "en", "url": self._absolute_url(post["url_en"])},
            {"lang": "it", "url": self._absolute_url(post["url_it"])},
            {
                "lang": "x-default",
                "url": self._absolute_url(post["original_url"]),
            },
        ]

    def _post_json_ld(self, post):
        canonical_url = self._absolute_url(post["url"])
        data = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": post["title"],
            "description": post["description"],
            "datePublished": post["date"].date().isoformat(),
            "author": {
                "@type": "Person",
                "name": post["author"],
                "url": f"{SITE_URL}/about",
            },
            "publisher": {
                "@type": "Person",
                "name": SITE_AUTHOR,
                "url": f"{SITE_URL}/about",
            },
            "mainEntityOfPage": canonical_url,
            "url": canonical_url,
            "inLanguage": post["language"],
            "keywords": post["tags"],
            "isPartOf": {
                "@type": "Blog",
                "name": f"{SITE_NAME}'s Blog",
                "url": f"{SITE_URL}/",
            },
        }
        if post.get("image_url"):
            data["image"] = post["image_url"]
        return data

    def _post_page(self, post):
        page = self._page_context(
            title=f"{post['title']} - {SITE_NAME}",
            description=post["description"],
            path=post["url"],
            lang=post["language"],
            alternates=self._post_alternates(post),
            og_type="article",
            image_url=post.get("image_url"),
            json_ld=self._post_json_ld(post),
            current_section="notes",
        )
        page["published_time"] = post["date"].date().isoformat()
        page["article_tags"] = post["tags"]
        return page

    def _web_page_json_ld(self, page_type, title, description, path, lang="en"):
        return {
            "@context": "https://schema.org",
            "@type": page_type,
            "name": title,
            "description": description,
            "url": self._absolute_url(path),
            "inLanguage": lang,
            "isPartOf": {
                "@type": "WebSite",
                "name": SITE_NAME,
                "url": f"{SITE_URL}/",
            },
        }

    def generate_home_page(self):
        page = self._page_context(
            title=SITE_NAME,
            description=SITE_DESCRIPTION,
            path="/",
            current_section="home",
            json_ld={
                "@context": "https://schema.org",
                "@graph": [
                    {
                        "@type": "WebSite",
                        "name": SITE_NAME,
                        "url": f"{SITE_URL}/",
                        "description": SITE_DESCRIPTION,
                        "inLanguage": "en",
                    },
                    {
                        "@type": "ProfilePage",
                        "name": SITE_NAME,
                        "url": f"{SITE_URL}/",
                        "mainEntity": {
                            "@type": "Person",
                            "name": SITE_AUTHOR,
                            "url": f"{SITE_URL}/about",
                        },
                    },
                ],
            },
        )
        self._register_redirect("/index.html", "/")
        self._register_redirect("/index", "/")
        self._render_and_write(
            "home.html",
            "index.html",
            page=page,
            recent_posts=self.posts[:5],
        )

    def _group_posts_by_year(self, posts):
        posts_by_year = defaultdict(list)
        for post in posts:
            if post["date"]:
                year = post["date"].strftime("%Y")
                posts_by_year[year].append(post)

        sorted_years = sorted(posts_by_year.keys(), reverse=True)
        for year in sorted_years:
            posts_by_year[year].sort(
                key=lambda item: item["date"],
                reverse=True,
            )
        return posts_by_year, sorted_years

    def generate_notes_page(self):
        description = "Browse Luca Bolognese's complete archive of notes and essays."
        page = self._page_context(
            title=f"Notes - {SITE_NAME}",
            description=description,
            path="/notes",
            current_section="notes",
            json_ld=self._web_page_json_ld(
                "CollectionPage",
                "Notes",
                description,
                "/notes",
            ),
        )
        posts_by_year, sorted_years = self._group_posts_by_year(self.posts)
        self._register_html_redirect("/notes")
        self._render_and_write(
            "notes.html",
            "notes.html",
            page=page,
            posts=self.posts,
            posts_by_year=posts_by_year,
            sorted_years=sorted_years,
        )

    def generate_tags_page(self):
        sorted_tags = sorted(self.tags.items(), key=lambda item: item[0].lower())
        tag_items = [
            {
                **self._tag_link(tag),
                "count": len(posts),
            }
            for tag, posts in sorted_tags
        ]
        description = "Browse Luca Bolognese's writing by topic."
        page = self._page_context(
            title=f"Tags - {SITE_NAME}",
            description=description,
            path="/tags",
            current_section="tags",
            json_ld=self._web_page_json_ld(
                "CollectionPage",
                "Tags",
                description,
                "/tags",
            ),
        )
        self._register_html_redirect("/tags")
        self._render_and_write(
            "tags.html",
            "tags.html",
            page=page,
            tags=dict(sorted_tags),
            tag_items=tag_items,
        )

        for tag, posts in sorted_tags:
            tag_info = {
                **self._tag_link(tag),
                "count": len(posts),
            }
            posts_by_year, sorted_years = self._group_posts_by_year(posts)
            description = (
                f"Browse {len(posts)} "
                f"{'post' if len(posts) == 1 else 'posts'} tagged {tag}."
            )
            tag_page = self._page_context(
                title=f"{tag} - {SITE_NAME}",
                description=description,
                path=tag_info["url"],
                current_section="tags",
                json_ld=self._web_page_json_ld(
                    "CollectionPage",
                    f"Posts tagged {tag}",
                    description,
                    tag_info["url"],
                ),
            )
            self._register_html_redirect(tag_info["url"])

            legacy_tag_path = f"/tags/{tag}"
            if legacy_tag_path != tag_info["url"]:
                self._register_redirect(legacy_tag_path, tag_info["url"])
                self._register_redirect(
                    f"{legacy_tag_path}.html",
                    tag_info["url"],
                )

            template_name = "tag_story.html" if tag == "story" else "tag.html"
            self._render_and_write(
                template_name,
                f"tags/{tag_info['slug']}.html",
                page=tag_page,
                tag=tag_info,
                posts_by_year=posts_by_year,
                sorted_years=sorted_years,
            )

    def generate_post_pages(self):
        for post in self.posts:
            self._render_and_write(
                "post.html",
                post["output_path"],
                page=self._post_page(post),
                post=post,
            )

    def _copy_static_asset(self, source, destination):
        source = Path(source)
        destination = Path(destination)
        if destination.exists():
            if destination.is_dir():
                shutil.rmtree(destination)
            else:
                destination.unlink()
        if not source.exists():
            return
        self._ensure_dir(destination.parent)
        if source.is_dir():
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)

    def copy_static_files(self):
        static_dir = self.output_dir / "static"
        self._ensure_dir(static_dir)

        self._copy_static_asset("src/style.css", static_dir / "style.css")
        self._copy_static_asset(
            "src/story-language.js",
            static_dir / "story-language.js",
        )

        for directory in ["img", "fonts"]:
            self._copy_static_asset(directory, self.output_dir / directory)

        for filename in ["favicon.svg", "favicon.ico", "fluidicon.png"]:
            self._copy_static_asset(filename, self.output_dir / filename)

        self._copy_static_asset("src/_headers", self.output_dir / "_headers")

        if Path("Schedule.html").exists():
            self._copy_static_asset(
                "Schedule.html",
                self.output_dir / "Schedule.html",
            )
            self._register_redirect("/Schedule.html", "/Schedule")

    def generate_feed(self):
        self._render_and_write(
            "feed.xml",
            "feed.xml",
            register=False,
            posts=self.posts,
            now=datetime.now(timezone.utc),
        )

    def generate_code_page(self):
        projects_path = Path("src/projects.yaml")
        if not projects_path.exists():
            return

        projects = yaml.safe_load(projects_path.read_text(encoding="utf-8"))
        description = "Software projects and experiments by Luca Bolognese."
        page = self._page_context(
            title=f"Code - {SITE_NAME}",
            description=description,
            path="/code",
            current_section="code",
            json_ld=self._web_page_json_ld(
                "CollectionPage",
                "Code",
                description,
                "/code",
            ),
        )
        self._register_html_redirect("/code")
        self._render_and_write(
            "code.html",
            "code.html",
            page=page,
            projects=projects,
        )

    def generate_about_page(self):
        description = (
            "About Luca Bolognese, a software developer, manager, writer, "
            "and sports enthusiast living in Italy."
        )
        page = self._page_context(
            title=f"About - {SITE_NAME}",
            description=description,
            path="/about",
            current_section="about",
            json_ld={
                "@context": "https://schema.org",
                "@type": "ProfilePage",
                "name": f"About {SITE_NAME}",
                "description": description,
                "url": f"{SITE_URL}/about",
                "inLanguage": "en",
                "mainEntity": {
                    "@type": "Person",
                    "name": SITE_AUTHOR,
                    "url": f"{SITE_URL}/about",
                },
            },
        )
        self._register_html_redirect("/about")
        self._render_and_write(
            "about.html",
            "about.html",
            page=page,
        )

    def generate_404_page(self):
        description = (
            "The requested page could not be found. Browse the latest notes "
            "or search lucabol.com."
        )
        page = self._page_context(
            title=f"Page not found - {SITE_NAME}",
            description=description,
            path=None,
            robots="noindex",
            current_section=None,
        )
        self._render_and_write(
            "404.html",
            "404.html",
            page=page,
            register=False,
            recent_posts=self.posts[:3],
        )

    def generate_translations(self):
        story_posts = [post for post in self.posts if post["is_story"]]
        if not story_posts:
            return

        print_api_key_info()
        print(f"\n[Translation] Processing {len(story_posts)} story posts...")

        for post in story_posts:
            slug = post["slug"]
            source_language = post["language"]
            target_language = "en" if source_language == "it" else "it"

            print(f"\n  [{slug}] ({source_language} -> {target_language})")
            translated_title = None
            translated_markdown = None

            if translation_exists(slug, target_language):
                print(
                    "    Translation exists - loading from "
                    f"{target_language}/{slug}.md"
                )
                translated_title, translated_markdown = load_translation(
                    slug,
                    target_language,
                )
            elif has_api_key():
                print(f"    Translating to {target_language}...")
                translated_title, translated_markdown = translate_story(
                    post["raw_content"],
                    post["title"],
                    target_language,
                )
                if translated_title and translated_markdown:
                    save_translation(
                        slug,
                        translated_title,
                        translated_markdown,
                        target_language,
                    )
                    print(
                        "    [OK] Translation saved to "
                        f"{target_language}/{slug}.md"
                    )
            else:
                print("    [Skip] No API key")
                continue

            if not translated_markdown:
                continue

            translated_url = f"/{target_language}/{slug}"
            translated_content = self._convert_markdown(translated_markdown)
            translated_content, translated_image = self._enrich_content_images(
                translated_content,
                translated_url,
            )
            translated_title = translated_title or post["title"]

            post["has_translation"] = True
            post["translation_url"] = translated_url
            post["translation"] = {
                "lang": target_language,
                "url": translated_url,
                "label": f"{target_language.upper()} (AI)",
            }
            post[f"title_{target_language}"] = translated_title
            post[f"url_{target_language}"] = translated_url

            translated_post = post.copy()
            translated_post.update(
                {
                    "title": translated_title,
                    "content": translated_content,
                    "raw_content": translated_markdown,
                    "url": translated_url,
                    "output_path": f"{target_language}/{slug}.html",
                    "description": self._post_description(
                        translated_title,
                        translated_content,
                    ),
                    "image_url": translated_image or post.get("image_url"),
                    "is_translation": True,
                    "language": target_language,
                    "translation": {
                        "lang": source_language,
                        "url": post["url"],
                        "label": source_language.upper(),
                    },
                    "translation_url": post["url"],
                }
            )

            self.translated_posts.append(translated_post)
            self._register_html_redirect(translated_url)
            self._render_and_write(
                "post.html",
                translated_post["output_path"],
                page=self._post_page(translated_post),
                post=translated_post,
            )

    def generate_sitemap(self):
        sitemap_namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
        xhtml_namespace = "http://www.w3.org/1999/xhtml"
        ET.register_namespace("", sitemap_namespace)
        ET.register_namespace("xhtml", xhtml_namespace)

        urlset = ET.Element(ET.QName(sitemap_namespace, "urlset"))
        for page in self.sitemap_pages:
            url_element = ET.SubElement(
                urlset,
                ET.QName(sitemap_namespace, "url"),
            )
            ET.SubElement(
                url_element,
                ET.QName(sitemap_namespace, "loc"),
            ).text = page["url"]
            if page["lastmod"]:
                ET.SubElement(
                    url_element,
                    ET.QName(sitemap_namespace, "lastmod"),
                ).text = page["lastmod"]
            for alternate in page["alternates"]:
                ET.SubElement(
                    url_element,
                    ET.QName(xhtml_namespace, "link"),
                    {
                        "rel": "alternate",
                        "hreflang": alternate["lang"],
                        "href": alternate["url"],
                    },
                )

        tree = ET.ElementTree(urlset)
        ET.indent(tree, space="  ")
        sitemap_path = self.output_dir / "sitemap.xml"
        self._ensure_dir(sitemap_path.parent)
        tree.write(
            sitemap_path,
            encoding="utf-8",
            xml_declaration=True,
        )

    def generate_redirects(self):
        domain_redirects = [
            (
                "http://lucabol.com/*",
                f"{SITE_URL}/:splat",
            ),
            (
                "https://lucabol.com/*",
                f"{SITE_URL}/:splat",
            ),
            (
                "http://www.lucabol.com/*",
                f"{SITE_URL}/:splat",
            ),
        ]

        lines = [
            "# Generated by src/generate_blog.py. Specific routes must come first."
        ]
        for source, target in self.redirects + domain_redirects:
            lines.append(f"{source} {target} 301!")
        self._write_file(
            self.output_dir / "_redirects",
            "\n".join(lines) + "\n",
        )

    def generate_site(self):
        self.posts = []
        self.tags = defaultdict(list)
        self.translated_posts = []
        self.redirects = []
        self.sitemap_pages = []
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self._ensure_dir(self.output_dir)

        self.read_posts()
        self.copy_static_files()
        self.generate_translations()
        self.generate_home_page()
        self.generate_notes_page()
        self.generate_tags_page()
        self.generate_post_pages()
        self.generate_code_page()
        self.generate_about_page()
        self.generate_404_page()
        self.generate_feed()
        self.generate_sitemap()
        self.generate_redirects()


def main():
    BlogGenerator("posts", "dist").generate_site()


if __name__ == "__main__":
    main()
