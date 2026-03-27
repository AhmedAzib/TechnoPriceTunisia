
import json
import re
import os

FILE_PATH = r"C:\Users\USER\Documents\programmation\frontend\src\data\megapc_gpu.json"

def clean_text(text):
    if not text: return ""
    if not isinstance(text, str): return text
    # Keep alphanumeric, whitespace, standard marks
    # Python's \w includes [a-zA-Z0-9_] and Unicode characters for letters. 
    # But emojis are usually considered "symbols".
    # Regex: replace anything that is NOT a word char, whitespace, or basic punctuation with empty string
    return re.sub(r'[^\w\s\-\.,\/\(\)\+]', '', text).strip()

def clean_json():
    if not os.path.exists(FILE_PATH):
        print("File not found.")
        return

    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    cleaned_count = 0
    for item in data:
        # Clean specs values
        specs = item.get('specs', {})
        for k, v in specs.items():
            if isinstance(v, str):
                new_v = clean_text(v)
                if new_v != v:
                    specs[k] = new_v
                    cleaned_count += 1
        
        # Clean title? Usually title is okay but good to be safe
        new_title = clean_text(item.get('title', ''))
        if new_title != item.get('title', ''):
             item['title'] = new_title
             cleaned_count += 1
             
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"Cleaned {cleaned_count} fields in {len(data)} items.")

if __name__ == "__main__":
    clean_json()
