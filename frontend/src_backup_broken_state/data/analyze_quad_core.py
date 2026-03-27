import json
import os
import glob
from collections import Counter

# Set up paths
data_dir = r"c:\Users\USER\Documents\programmation\frontend\src\data"
files = glob.glob(os.path.join(data_dir, "*_mobiles.json")) + glob.glob(os.path.join(data_dir, "samsung_tunisie.json")) + glob.glob(os.path.join(data_dir, "*_phones.json"))

quad_core_titles = []

print("Simulating CPU Classification to find 'Quad Core' composition...")

for file_path in files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for p in data:
            specs = p.get('specs', {})
            cpu = specs.get('cpu', 'Unknown')
            title = (p.get('title', '')).strip()
            t_lower = title.lower()
            full_text = (title + " " + specs.get('raw', '')).lower()
            
            # --- SIMULATE JS LOGIC ---
            
             # 1. Quad Core Logic
            isQuadCore = (
                'quad core' in full_text or 'quad-core' in full_text or '4 core' in full_text or '4-core' in full_text or
                # Known Low-End Quad Core Models
                'lesia young' in t_lower or 
                'itel a33' in t_lower or 'itel a17' in t_lower or 'itel a16' in t_lower or 'itel a37' in t_lower or 'itel a14' in t_lower or
                'evertek' in t_lower or 
                'nokia c1' in t_lower or 'nokia c2' in t_lower
            )
            
            if isQuadCore:
                if 'nokia' in t_lower:
                    quad_core_titles.append(title)

    except Exception as e:
        pass

print(f"\nTotal Nokia in 'Quad Core': {len(quad_core_titles)}")

print("\n--- NOKIA TITLES IN QUAD CORE ---")
for t in quad_core_titles:
    print(t)
