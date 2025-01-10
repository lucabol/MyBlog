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
        
    def _process_post_file(self, filename):
        """Process a single post file and return post data."""
        filepath = os.path.join(self.posts_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
            
        return {
            'title': post.get('title', 'Untitled'),
            'date': self._process_post_date(post.get('date')),
            'author': self._process_post_author(post.get('author')),
            'tags': post.get('tags', []),
            'content': self._convert_markdown(post.content),
            'url': f'posts/{os.path.splitext(filename)[0]}.html'
        }
        
    def read_posts(self):
        for filename in os.listdir(self.posts_dir):
            if filename.endswith('.md'):
                post_data = self._process_post_file(filename)
                self.posts.append(post_data)
                for tag in post_data['tags']:
                    self.tags[tag].append(post_data)
        
        self.posts.sort(key=lambda x: x['date'], reverse=True)
    
    def generate_home_page(self):
        self._render_and_write('home.html', 
                             os.path.join(self.output_dir, 'index.html'),
                             recent_posts=self.posts[:5])
    
    def generate_notes_page(self):
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
            self._render_and_write('tag.html',
                                 os.path.join(tags_dir, f'{tag}.html'),
                                 tag=tag,
                                 posts_by_year=posts_by_year,
                                 sorted_years=sorted_years)
    
    def generate_post_pages(self):
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
    
    def generate_feed(self):
        self._render_and_write('feed.xml',
                             os.path.join(self.output_dir, 'feed.xml'),
                             posts=self.posts,
                             now=datetime.now(timezone.utc))
    
    def generate_code_page(self):
        import yaml
        
        # Skip code page generation if projects.yaml doesn't exist
        if not os.path.exists('src/projects.yaml'):
            return
            
        with open('src/projects.yaml', 'r', encoding='utf-8') as f:
            projects = yaml.safe_load(f)
            
        self._render_and_write('code.html',
                             os.path.join(self.output_dir, 'code.html'),
                             projects=projects)
    
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
