import http.server
import socketserver
import shutil
import os
from generate_blog import main as generate_blog

def main():
    # Kill any running Python processes except the current one
    current_pid = os.getpid()
    os.system(f'wmic process where "name=\'python.exe\' and processid!={current_pid}" call terminate 2>nul')
    
    # Delete dist directory if it exists
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    # Generate the blog
    generate_blog()
    
    # Start the server
    PORT = 8000
    DIRECTORY = "dist"
    
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=DIRECTORY, **kwargs)

    # Allow reuse of the address
    socketserver.TCPServer.allow_reuse_address = True
    
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Serving at http://localhost:{PORT}")
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 10048:  # Port already in use
            print(f"Port {PORT} is already in use. Please stop any running servers first.")
        else:
            raise

if __name__ == '__main__':
    main()
