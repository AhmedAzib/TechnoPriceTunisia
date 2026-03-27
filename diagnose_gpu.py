import json
import re
import os

# Paths to data files
BASE_DIR = r"c:\Users\USER\Documents\programmation\frontend\src\data"
FILES = [
    "tunisianet_clean.json",
    "spacenet_products.json",
    "mytek_test.json",
    "wiki_clean.json"
]

def load_data(filename):
    path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return []

def normalize_gpu_mock(title, specs):
    t = (title or "").upper()
    gpu = str(specs.get('gpu', '') or '').upper() # Force string
    
    # Mocking CURRENT simple logic to see what fails
    if not gpu or gpu == 'UNKNOWN' or gpu == 'INTEGRATED':
        if "RTX 4060" in t: gpu = "RTX 4060"
        elif "RTX 4050" in t: gpu = "RTX 4050"
        elif "RTX 3050" in t: gpu = "RTX 3050"
        elif "RTX 4070" in t: gpu = "RTX 4070"
        elif "GTX 1650" in t: gpu = "GTX 1650"
        else: gpu = "Unknown"
        
    return gpu

def main():
    gpu_counts = {}
    unknown_examples = []

    print(f"Loading data from {len(FILES)} files...")
    
    for filename in FILES:
        data = load_data(filename)
        for p in data:
            title = p.get('name', p.get('title', ''))
            specs = p.get('specs', {})
            
            # If specs.gpu is effectively empty/unknown in source, we want to know
            raw_gpu = specs.get('gpu', 'Unknown')
            
            # Run our mock normalization
            normalized_gpu = normalize_gpu_mock(title, specs)
            
            gpu_counts[normalized_gpu] = gpu_counts.get(normalized_gpu, 0) + 1
            
            if normalized_gpu == 'Unknown':
                unknown_examples.append({
                    'title': title,
                    'raw_gpu': raw_gpu,
                    'source': filename
                })

    print("-" * 30)
    print("GPU Value Distribution:")
    # Sort by count desc
    sorted_gpu = sorted(gpu_counts.items(), key=lambda x: x[1], reverse=True)
    for g, count in sorted_gpu:
        print(f"'{g}': {count}")

    print("-" * 30)
    print(f"Top 50 Unknown GPU Titles (out of {len(unknown_examples)}):")
    for i, item in enumerate(unknown_examples[:50]):
        print(f"{i+1}. [{item['source']}] T: {item['title']} | Raw: {item['raw_gpu']}")

if __name__ == "__main__":
    main()
