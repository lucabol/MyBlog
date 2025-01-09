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
        
        # Copy CSS file
        import shutil
        shutil.copy2('src/style.css', os.path.join(css_dir, 'style.css'))
        
        # Copy static assets
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
