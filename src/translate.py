import os
import time
from dotenv import dotenv_values

# Load only from .env file, ignore environment variables
config = dotenv_values('.env')

def translate_story(markdown_text, target_language, max_retries=3):
    """Translate markdown text to target language using Gemini API."""
    api_key = config.get('GEMINI_API_KEY')
    if not api_key or api_key == 'your-api-key-here':
        return None
    
    from google import genai
    from google.genai import types
    
    client = genai.Client(api_key=api_key)
    
    lang_name = 'Italian' if target_language == 'it' else 'English'
    
    prompt = f"""Translate this story to {lang_name}. 
Keep all markdown formatting intact (headers, bold, italic, links, etc.).
Preserve the tone, style, and literary quality of the original.
Only output the translated text, no explanations.

---
{markdown_text}
---"""
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-3-pro-preview',
                contents=prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(
                        thinking_level=types.ThinkingLevel.HIGH
                    )
                )
            )
            return response.text
        except Exception as e:
            if '429' in str(e) and attempt < max_retries - 1:
                wait_time = 60 * (attempt + 1)
                print(f"    ⏳ Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"    ❌ Error: {e}")
                return None
    return None

def translation_exists(slug, target_language):
    """Check if a translation already exists in source folder."""
    folder = 'en' if target_language == 'en' else 'it'
    path = os.path.join(folder, f'{slug}.md')
    return os.path.exists(path)

def save_translation(slug, translated_markdown, target_language):
    """Save translated markdown to source folder."""
    folder = 'en' if target_language == 'en' else 'it'
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, f'{slug}.md')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(translated_markdown)

def load_translation(slug, target_language):
    """Load translated markdown from source folder."""
    folder = 'en' if target_language == 'en' else 'it'
    filepath = os.path.join(folder, f'{slug}.md')
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def has_api_key():
    """Check if a valid Gemini API key is configured."""
    api_key = config.get('GEMINI_API_KEY')
    return api_key and api_key != 'your-api-key-here'

def print_api_key_info():
    """Print info about which API key is being used."""
    api_key = config.get('GEMINI_API_KEY')
    if not api_key:
        print("🔑 No GEMINI_API_KEY found in .env file")
    elif api_key == 'your-api-key-here':
        print("🔑 GEMINI_API_KEY is placeholder in .env file")
    else:
        masked = api_key[:8] + '...' + api_key[-4:]
        print(f"🔑 Using GEMINI_API_KEY from .env: {masked}")
