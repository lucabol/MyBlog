import os
import frontmatter
from datetime import datetime, date, timezone
from collections import defaultdict
from jinja2 import Environment, FileSystemLoader
import markdown
import urllib.parse
import yaml
from translate import translate_story, translation_exists, has_api_key, print_api_key_info, save_translation, load_translation

class BlogGenerator:
    def generate_sitemap(self):
        """Generate sitemap.xml with all site URLs."""
        base_url = "https://lucabol.com"  # Change to your actual domain if needed
        urls = [
            f"{base_url}/",
            f"{base_url}/notes.html",
            f"{base_url}/tags.html",
            f"{base_url}/about.html",
            f"{base_url}/code.html",
            f"{base_url}/feed.xml",
        ]

        # Add post URLs
        for post in self.posts:
            urls.append(f"{base_url}/{post['url']}")

        # Add tag pages
        for tag in self.tags:
            urls.append(f"{base_url}/tags/{tag}.html")

        # Build XML
        urlset = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        ]
        for url in urls:
            urlset.append(f"  <url><loc>{url}</loc></url>")
        urlset.append('</urlset>')

        sitemap_content = "\n".join(urlset)
        self._write_file(os.path.join(self.output_dir, "sitemap.xml"), sitemap_content)

    def __init__(self, posts_dir, output_dir):
        self.posts_dir = posts_dir
        self.output_dir = output_dir
        self.posts = []
        self.tags = defaultdict(list)
        self.env = Environment(loader=FileSystemLoader('src/templates'))
        
    def _ensure_dir(self, path):
        """Create directory if it doesn't exist."""
        os.makedirs(path, exist_ok=True)
        
    def _write_file(self, path, content):
        """Write content to file, ensuring directory exists."""
        self._ensure_dir(os.path.dirname(path))
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    def _render_and_write(self, template_name, output_path, **kwargs):
        """Render template and write to file."""
        template = self.env.get_template(template_name)
        kwargs['year'] = datetime.now().year
        content = template.render(**kwargs)
        self._write_file(output_path, content)
        
    def _process_post_date(self, post_date):
        """Process post date to consistent format."""
        if post_date:
            if isinstance(post_date, date) and not isinstance(post_date, datetime):
                post_date = datetime.combine(post_date, datetime.min.time())
            if hasattr(post_date, 'tzinfo') and post_date.tzinfo is not None:
                post_date = post_date.replace(tzinfo=None)
        return post_date
        
    def _process_post_author(self, author):
        """Process author name to consistent format."""
        if author == 'lucabol':
            return 'Luca Bolognese'
        return author or 'Anonymous'
        
    def _convert_markdown(self, content):
        """Convert markdown to HTML with extended features."""
        return markdown.markdown(
            content,
            extensions=[
                'fenced_code',
                'tables',
                'sane_lists',
                'smarty',
                'attr_list'
            ]
        )

    def _get_comments_url(self, post_date, title):
        """Generate GitHub issues search URL for comments."""
        # Get date in YYYY-MM-DD format
        date_str = post_date.strftime('%Y-%m-%d')
        
        # Get first few words of title (up to 3)
        title_words = ' '.join(title.split()[:3])
        
        # Create search query
        query = f"is:issue {date_str} {title_words}"
        
        # URL encode the query
        encoded_query = urllib.parse.quote(query)
        
        # Return full URL
        return f"https://github.com/lucabol/MyBlog_Comments/issues?q={encoded_query}"
        
    def _process_post_file(self, filename):
        """Process a single post file and return post data."""
        filepath = os.path.join(self.posts_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
            
        post_date = self._process_post_date(post.get('date'))
        post_title = post.get('title', 'Untitled')
        post_tags = post.get('tags', [])
        slug = os.path.splitext(filename)[0]
        language = post.get('language', 'en')
        
        # Check if this is a story
        is_story = 'story' in post_tags
            
        return {
            'title': post_title,
            'date': post_date,
            'author': self._process_post_author(post.get('author')),
            'tags': post_tags,
            'content': self._convert_markdown(post.content),
            'raw_content': post.content,
            'url': f'posts/{slug}.html',
            'slug': slug,
            'comments_url': self._get_comments_url(post_date, post_title),
            'description': post.get('description'),
            'is_story': is_story,
            'language': language,
            'has_translation': False,
            'translation_url': None
        }
        
    def read_posts(self):
        """Read all posts from posts directory."""
        for filename in os.listdir(self.posts_dir):
            if filename.endswith('.md'):
                post_data = self._process_post_file(filename)
                self.posts.append(post_data)
                for tag in post_data['tags']:
                    self.tags[tag].append(post_data)
        
        self.posts.sort(key=lambda x: x['date'], reverse=True)
    
    def generate_home_page(self):
        """Generate the home page with recent posts."""
        self._render_and_write('home.html', 
                             os.path.join(self.output_dir, 'index.html'),
                             recent_posts=self.posts[:5])
    
    def generate_notes_page(self):
        """Generate the notes page with all posts."""
        self._render_and_write('notes.html',
                             os.path.join(self.output_dir, 'notes.html'),
                             posts=self.posts)
    
    def _group_posts_by_year(self, posts):
        """Group posts by year and sort them."""
        posts_by_year = defaultdict(list)
        for post in posts:
            if post['date']:
                year = post['date'].strftime('%Y')
                posts_by_year[year].append(post)
        
        # Sort years and posts within years
        sorted_years = sorted(posts_by_year.keys(), reverse=True)
        for year in sorted_years:
            posts_by_year[year].sort(key=lambda x: x['date'], reverse=True)
            
        return posts_by_year, sorted_years
    
    def generate_tags_page(self):
        """Generate tag index and individual tag pages."""
        # Generate main tags index
        sorted_tags = dict(sorted(self.tags.items(), key=lambda x: x[0].lower()))
        self._render_and_write('tags.html',
                             os.path.join(self.output_dir, 'tags.html'),
                             tags=sorted_tags)
            
        # Generate individual tag pages
        tags_dir = os.path.join(self.output_dir, 'tags')
        self._ensure_dir(tags_dir)
        
        for tag, posts in self.tags.items():
            posts_by_year, sorted_years = self._group_posts_by_year(posts)
            
            # Special handling for 'story' tag - generate EN and IT versions
            if tag == 'story':
                self._generate_story_tag_pages(posts, posts_by_year, sorted_years, tags_dir)
            else:
                self._render_and_write('tag.html',
                                     os.path.join(tags_dir, f'{tag}.html'),
                                     tag=tag,
                                     posts_by_year=posts_by_year,
                                     sorted_years=sorted_years)
    
    def _generate_story_tag_pages(self, posts, posts_by_year, sorted_years, tags_dir):
        """Generate the story tag page with inline language links."""
        # Just render the single story tag page - posts already have translation_url
        self._render_and_write('tag_story.html',
                             os.path.join(tags_dir, 'story.html'),
                             tag='story',
                             posts_by_year=posts_by_year,
                             sorted_years=sorted_years)
    
    def generate_post_pages(self):
        """Generate individual post pages."""
        posts_dir = os.path.join(self.output_dir, 'posts')
        self._ensure_dir(posts_dir)
        
        for post in self.posts:
            self._render_and_write('post.html',
                                 os.path.join(self.output_dir, post['url']),
                                 post=post)
    
    def _copy_static_asset(self, src, dest):
        """Copy a static asset, removing destination if it exists."""
        import shutil
        if os.path.exists(dest):
            if os.path.isdir(dest):
                shutil.rmtree(dest)
            else:
                os.remove(dest)
        if os.path.exists(src):
            if os.path.isdir(src):
                shutil.copytree(src, dest)
            else:
                shutil.copy2(src, dest)
    
    def copy_static_files(self):
        """Copy static assets to output directory."""
        static_dir = os.path.join(self.output_dir, 'static')
        self._ensure_dir(static_dir)
        
        # Copy CSS file
        self._copy_static_asset('src/style.css', os.path.join(static_dir, 'style.css'))
        
        # Copy static assets
        for dir_name in ['img', 'fonts']:
            self._copy_static_asset(
                dir_name,
                os.path.join(self.output_dir, dir_name)
            )
            
        # Copy favicon files
        for favicon in ['favicon.svg', 'favicon.ico']:
            self._copy_static_asset(
                favicon,
                os.path.join(self.output_dir, favicon)
            )
    
    def generate_feed(self):
        """Generate RSS feed."""
        self._render_and_write('feed.xml',
                             os.path.join(self.output_dir, 'feed.xml'),
                             posts=self.posts,
                             now=datetime.now(timezone.utc))
    
    def generate_code_page(self):
        """Generate code page from projects.yaml."""
        # Skip code page generation if projects.yaml doesn't exist
        if not os.path.exists('src/projects.yaml'):
            return
            
        with open('src/projects.yaml', 'r', encoding='utf-8') as f:
            projects = yaml.safe_load(f)
            
        self._render_and_write('code.html',
                             os.path.join(self.output_dir, 'code.html'),
                             projects=projects)
    
    def generate_about_page(self):
        """Generate the about page."""
        self._render_and_write('about.html',
                             os.path.join(self.output_dir, 'about.html'))

    def generate_italian_translations(self):
        """Generate Italian translations for story posts."""
        story_posts = [p for p in self.posts if p.get('is_story')]
        
        if not story_posts:
            return
        
        # Print API key info
        print_api_key_info()
        
        print(f"\n[Translation] Processing {len(story_posts)} story posts...")
        
        it_dir = os.path.join(self.output_dir, 'it')
        en_dir = os.path.join(self.output_dir, 'en')
        self._ensure_dir(it_dir)
        self._ensure_dir(en_dir)
        
        for post in story_posts:
            slug = post['slug']
            source_lang = post['language']
            target_lang = 'en' if source_lang == 'it' else 'it'
            target_dir = en_dir if target_lang == 'en' else it_dir
            
            print(f"\n  [{slug}] ({source_lang} -> {target_lang})")
            
            # Check if translation already exists in source folder
            if translation_exists(slug, target_lang):
                print(f"    Translation exists - loading from {target_lang}/{slug}.md")
                translated_title, translated_md = load_translation(slug, target_lang)
            elif has_api_key():
                # Translate the content and title
                print(f"    Translating to {target_lang}...")
                translated_title, translated_md = translate_story(post['raw_content'], post['title'], target_lang)
                
                if translated_title and translated_md:
                    # Save to source folder
                    save_translation(slug, translated_title, translated_md, target_lang)
                    print(f"    [OK] Translation saved to {target_lang}/{slug}.md")
            else:
                print(f"    [Skip] No API key")
                continue
            
            if translated_md:
                # Convert translated markdown to HTML
                translated_html = self._convert_markdown(translated_md)
                
                # Create translated post data
                translated_post = post.copy()
                translated_post['content'] = translated_html
                translated_post['title'] = translated_title or post['title']
                translated_post['original_url'] = f'/{post["url"]}'
                translated_post['target_language'] = target_lang
                
                # Write the translated page
                template = 'post_en.html' if target_lang == 'en' else 'post_it.html'
                self._render_and_write(template,
                                     os.path.join(target_dir, f'{slug}.html'),
                                     post=translated_post)
                
                # Update post to indicate it has a translation
                post['has_translation'] = True
                post['translation_url'] = f'/{target_lang}/{slug}.html'

    def generate_site(self):
        """Generate the complete site."""
        self.read_posts()
        self.copy_static_files()
        
        # Generate translations first (updates post data with has_translation)
        self.generate_italian_translations()
        
        self.generate_home_page()
        self.generate_notes_page()
        self.generate_tags_page()
        self.generate_post_pages()
        self.generate_code_page()
        self.generate_about_page()
        self.generate_feed()

        # Dynamically generate sitemap.xml every time
        self.generate_sitemap()

def main():
    generator = BlogGenerator('posts', 'dist')
    generator.generate_site()

if __name__ == '__main__':
    main()
