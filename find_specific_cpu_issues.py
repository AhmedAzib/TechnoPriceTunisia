
import json
import os
import glob

files = glob.glob('frontend/src/data/*.json')

files = ['frontend/src/data/skymil_new.json']

# Lowercase keywords for safer matching
keywords = ["cu5", "f16"]

print("Scanning skymil_new.json for:", keywords)

for fp in files:
    try:
        with open(fp, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for p in data:
                t = p.get('name', p.get('title', '')).lower()
                for k in keywords:
                    if k in t:
                        print(f"[{fp}] FOUND: {p.get('title')}")
    except Exception as e:
        print(e)
