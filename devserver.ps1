taskkill /F /IM python.exe 2>$null
python src/generate_blog.py
python -m http.server 8000 --directory dist
