import json
import re

FILE = 'src/data/mytek_motherboards.json'

def audit():
    try:
        with open(FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    misclassified = []
    
    # Regex to detect Micro-ATX cues in title
    # e.g. B650M, H610M, A520M (The 'M' after 3 digits usually means Micro)
    # Also "Micro" in title
    micro_hint_pattern = re.compile(r'\b[A-Z][0-9]{3}M\b|-M\b|Micro', re.IGNORECASE)

    for item in data:
        specs = item.get('specs', {})
        fmt = specs.get('format', 'Unknown').upper()
        title = item['title']
        
        # Check if classified as ATX but has Micro hints
        if fmt == 'ATX':
            if micro_hint_pattern.search(title):
                misclassified.append(title)

    print(f"Potential Micro-ATX boards misclassified as ATX: {len(misclassified)}")
    for title in misclassified:
        print(f" - {title}")

if __name__ == "__main__":
    audit()
