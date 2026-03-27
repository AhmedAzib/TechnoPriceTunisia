
import json
import os
import glob
import re

files = glob.glob('frontend/src/data/*.json')

skus = [
    "15-fd0030nk", "15-fd0315nk", "15-fd0036nk", "15-fd0089nk", "15-fd0119nk", 
    "15-FD0028NK", "15-c", "Matebook Huawei X pro"
]

print("Scanning for problematic SKUs...")

for fp in files:
    try:
        with open(fp, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for p in data:
                t = p.get('name', p.get('title', ''))
                # matched_sku = next((s for s in skus if s in t), None) # Case sensitive?
                
                # Case insensitive check
                matched_sku = None
                for s in skus:
                    if s.lower() in t.lower():
                        matched_sku = s
                        break
                
                if matched_sku:
                    print(f"[{fp}] SKU: {matched_sku} | Price: {p.get('price')} | Title: {t}")
    except: pass
