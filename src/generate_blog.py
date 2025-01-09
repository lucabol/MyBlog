import os
import frontmatter
from datetime import datetime, date, timezone
from collections import defaultdict
from jinja2 import Environment, FileSystemLoader
import markdown

class BlogGenerator:
    def __init__(self, posts_dir, output_dir):
        self.posts_dir = posts_dir
        self.output_dir = output_dir
        self.posts = []
        self.tags = defaultdict(list)
        self.env = Environment(loader=FileSystemLoader('src/templates'))
        
    def read_posts(self):
        for filename in os.listdir(self.posts_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(self.posts_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)
                    
                # Convert markdown to HTML with extended features
                html_content = markdown.markdown(
                    post.content,
                    extensions=[
                        'fenced_code',
                        'tables',
                        'sane_lists',
                        'smarty',
                        'attr_list'
                    ]
                )
                
                post_date = post.get('date')
                if post_date:
                    if isinstance(post_date, date) and not isinstance(post_date, datetime):
                        post_date = datetime.combine(post_date, datetime.min.time())
                    if hasattr(post_date, 'tzinfo') and post_date.tzinfo is not None:
                        post_date = post_date.replace(tzinfo=None)
                
                author = post.get('author', 'Anonymous')
                if author == 'lucabol':
                    author = 'Luca Bolognese'
                    
                post_data = {
                    'title': post.get('title', 'Untitled'),
                    'date': post_date,
                    'author': author,
                    'tags': post.get('tags', []),
                    'content': html_content,
                    'url': f'posts/{os.path.splitext(filename)[0]}.html'
                }
                
                self.posts.append(post_data)
                for tag in post_data['tags']:
                    self.tags[tag].append(post_data)
        
        self.posts.sort(key=lambda x: x['date'], reverse=True)
    
    def generate_home_page(self):
        template = self.env.get_template('home.html')
        content = template.render(
            recent_posts=self.posts[:5],
            year=datetime.now().year
        )
        
        os.makedirs(self.output_dir, exist_ok=True)
        with open(os.path.join(self.output_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(content)
    
    def generate_notes_page(self):
        template = self.env.get_template('notes.html')
        content = template.render(
            posts=self.posts,
            year=datetime.now().year
        )
        
        with open(os.path.join(self.output_dir, 'notes.html'), 'w', encoding='utf-8') as f:
            f.write(content)
    
    def generate_tags_page(self):
        # Generate main tags index
        # Sort tags alphabetically
        sorted_tags = dict(sorted(self.tags.items(), key=lambda x: x[0].lower()))
        template = self.env.get_template('tags.html')
        content = template.render(
            tags=sorted_tags,
            year=datetime.now().year
        )
        with open(os.path.join(self.output_dir, 'tags.html'), 'w', encoding='utf-8') as f:
            f.write(content)
            
        # Generate individual tag pages
        tag_template = self.env.get_template('tag.html')
        tags_dir = os.path.join(self.output_dir, 'tags')
        os.makedirs(tags_dir, exist_ok=True)
        
        for tag, posts in self.tags.items():
            # Group posts by year
            posts_by_year = defaultdict(list)
            for post in posts:
                if post['date']:  # Check if date exists
                    year = post['date'].strftime('%Y')
                    posts_by_year[year].append(post)
            
            # Sort years and posts within years
            sorted_years = sorted(posts_by_year.keys(), reverse=True)
            for year in sorted_years:
                posts_by_year[year].sort(key=lambda x: x['date'], reverse=True)
            
            content = tag_template.render(
                tag=tag,
                posts_by_year=posts_by_year,
                sorted_years=sorted_years,
                year=datetime.now().year
            )
            tag_path = os.path.join(tags_dir, f'{tag}.html')
            with open(tag_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def generate_post_pages(self):
        template = self.env.get_template('post.html')
        posts_dir = os.path.join(self.output_dir, 'posts')
        os.makedirs(posts_dir, exist_ok=True)
        
        for post in self.posts:
            content = template.render(
                post=post,
                year=datetime.now().year
            )
            post_path = os.path.join(self.output_dir, post['url'])
            with open(post_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def copy_static_files(self):
        static_dir = os.path.join(self.output_dir, 'static')
        os.makedirs(static_dir, exist_ok=True)
        css_dir = os.path.join(static_dir, 'css')
        os.makedirs(css_dir, exist_ok=True)
        with open(os.path.join(css_dir, 'style.css'), 'w', encoding='utf-8') as f:
            f.write("""
                @font-face {
                    font-family: 'MyGeorgia';
                    src: local('Georgia'),
                         url('/fonts/georgiasubset.eot') format('embedded-opentype'),
                         url('/fonts/georgiasubset.woff2') format('woff2'),
                         url('/fonts/georgiasubset.woff') format('woff'),
                         url('/fonts/georgiasubset.ttf') format('truetype'),
                         url('/fonts/georgiasubset.svg#georgiasubset') format('svg');
                }

                @font-face {
                    font-family: 'MyTrebuchet';
                    src: local('Trebuchet MS'),
                         url('/fonts/trebucbdsubset.eot') format('embedded-opentype'),
                         url('/fonts/trebucbdsubset.woff2') format('woff2'),
                         url('/fonts/trebucbdsubset.woff') format('woff'),
                         url('/fonts/trebucbdsubset.ttf') format('truetype'),
                         url('/fonts/trebucbdsubset.svg#trebucbdsubset') format('svg');
                }

                :root {
                    font-size: 16px;
                    --base-size: clamp(15px, 2.2vw, 24px);
                }
                html, body {
                    font-family: MyGeorgia, serif;
                    font-size: var(--base-size);
                    line-height: 1.3;
                    max-width: 75ch;
                    font-variant-ligatures: discretionary-ligatures;
                    margin: 0 auto;
                    padding: 0.5rem 1rem;
                }
                nav {
                    text-align: center;
                    margin: 2rem 0 1rem;
                }
                nav a {
                    margin: 0 1rem;
                    text-decoration: none;
                    color: #000;
                    font-size: calc(var(--base-size) * 1.1);
                }
                h1, .year {
                    font-family: MyTrebuchet, sans-serif;
                }
                h1 {
                    text-align: center;
                    font-size: calc(var(--base-size) * 1.3);
                    margin-bottom: 1rem;
                    font-weight: normal;
                }
                .year {
                    font-size: calc(var(--base-size) * 1.2);
                    margin: 2rem 0 1rem;
                    font-weight: normal;
                }
                article h1 {
                    font-size: calc(var(--base-size) * 1.3);
                    font-weight: normal;
                }
                .posts-list {
                    list-style-type: circle;
                    margin: 0;
                    padding-left: 2rem;
                    line-height: 1.1;
                    font-size: var(--base-size);
                }
                .posts-list li {
                    margin: 0.3rem 0;
                }
                .post-meta {
                    text-align: center;
                    margin-bottom: 1rem;
                }
                .post-content {
                    font-size: var(--base-size);
                    line-height: 1.4;
                    margin-bottom: 3rem;
                }
                .post-content p {
                    text-align: left;
                }
                .post-tags {
                    list-style-type: circle;
                    padding-left: 2rem;
                    margin: 1rem 0 2rem;
                    font-size: var(--base-size);
                }
                .post-tags li {
                    margin: 0.5rem 0;
                }
                .post-tags a {
                    color: #000;
                    text-decoration: none;
                    text-transform: uppercase;
                }
                .post-tags a:hover {
                    text-decoration: underline;
                }
                .post-content + h2 {
                    font-family: "Trebuchet MS", sans-serif;
                    font-weight: normal;
                    font-size: calc(var(--base-size) * 1.2);
                    margin: 3rem 0 1rem;
                }
                .avatar {
                    text-align: center;
                    margin: 3rem 0;
                }
                .avatar img {
                    width: 200px;
                    height: 200px;
                }
                .social-links {
                    text-align: center;
                    margin: 3rem 0;
                }
                .social-link {
                    display: inline-block;
                    margin: 0 1rem;
                }
                .social-link img {
                    width: 32px;
                    height: 32px;
                }
                .search {
                    text-align: center;
                    margin: 3rem 0;
                }
                .search input {
                    font-family: Georgia, serif;
                    font-size: var(--base-size);
                    padding: 0.5rem;
                    width: 300px;
                    margin-right: 0.5rem;
                }
                .search button {
                    font-family: Georgia, serif;
                    font-size: var(--base-size);
                    padding: 0.5rem 1rem;
                    cursor: pointer;
                }
                .post-footer {
                    text-align: center;
                    margin: 2rem 0;
                }
                .post-footer a {
                    color: #000;
                    text-decoration: none;
                }
                .posts-list a {
                    color: #000;
                    text-decoration: none;
                }
                .posts-list a:hover {
                    text-decoration: underline;
                }
                .tags-list {
                    list-style-type: circle;
                    padding-left: 2rem;
                    margin: 2rem 0;
                    font-size: var(--base-size);
                }
                .tags-list li {
                    margin: 0.2rem 0;
                }
                .tags-list a {
                    color: #000;
                    text-decoration: none;
                    text-transform: uppercase;
                }
                .tags-list a:hover {
                    text-decoration: underline;
                }
                pre {
                    background-color: #fbfbff;
                    padding: 0.5rem 1rem 0.5rem 0.5rem;
                    margin: 0;
                    overflow-x: auto;
                    font-family: ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, Consolas, 'DejaVu Sans Mono', monospace;
                    font-size: 1rem;
                    line-height: normal;
                }
                code {
                    font-family: ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, Consolas, 'DejaVu Sans Mono', monospace;
                    font-size: 1rem;
                }
                table {
                    background-color: #fbfbff;
                    padding: 0.5rem;
                    margin: 1rem 0;
                    width: 100%;
                    border-collapse: collapse;
                    font-family: ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, Consolas, 'DejaVu Sans Mono', monospace;
                    font-size: 1rem;
                    line-height: normal;
                }
                th, td {
                    padding: 0.5rem;
                    text-align: left;
                    border: 1px solid #e0e0e0;
                }
                th {
                    background-color: #f5f5ff;
                    font-weight: normal;
                }
                .submit {
                    background: transparent;
                    border: 1px solid #000;
                    cursor: pointer;
                    font-family: MyGeorgia, serif;
                    font-size: var(--base-size);
                    padding: 0.5rem 1rem;
                }
                .public-domain {
                    font-size: calc(var(--base-size) * 0.7);
                    text-align: center;
                    color: #666;
                    margin: 0.5rem 0;
                }
                .back-to-top {
                    display: block;
                    text-align: center;
                    margin-top: 2rem;
                    color: #000;
                    text-decoration: none;
                    font-family: MyGeorgia, serif;
                    font-size: var(--base-size);
                }
                .back-to-top:hover {
                    text-decoration: underline;
                }
            """)
            
        # Copy static assets
        import shutil
        for dir_name in ['img', 'fonts']:
            if os.path.exists(dir_name):
                dest = os.path.join(self.output_dir, dir_name)
                if os.path.exists(dest):
                    shutil.rmtree(dest)
                shutil.copytree(dir_name, dest)
    
    def generate_feed(self):
        template = self.env.get_template('feed.xml')
        content = template.render(
            posts=self.posts,
            now=datetime.now(timezone.utc)
        )
        
        with open(os.path.join(self.output_dir, 'feed.xml'), 'w', encoding='utf-8') as f:
            f.write(content)
    
    def generate_code_page(self):
        import yaml
        
        # Skip code page generation if projects.yaml doesn't exist
        if not os.path.exists('src/projects.yaml'):
            return
            
        with open('src/projects.yaml', 'r', encoding='utf-8') as f:
            projects = yaml.safe_load(f)
            
        template = self.env.get_template('code.html')
        content = template.render(
            year=datetime.now().year,
            projects=projects
        )
        
        with open(os.path.join(self.output_dir, 'code.html'), 'w', encoding='utf-8') as f:
            f.write(content)
    
    def generate_site(self):
        self.read_posts()
        self.copy_static_files()
        self.generate_home_page()
        self.generate_notes_page()
        self.generate_tags_page()
        self.generate_post_pages()
        self.generate_code_page()
        self.generate_feed()

def main():
    generator = BlogGenerator('posts', 'dist')
    generator.generate_site()

if __name__ == '__main__':
    main()
