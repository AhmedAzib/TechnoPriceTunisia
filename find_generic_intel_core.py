
import json
import os
import glob
import re

files = glob.glob('frontend/src/data/*.json')

print("Scanning for items that fallback to generic 'Intel Core'...")

count = 0

for fp in files:
    try:
        with open(fp, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for p in data:
                t = p.get('name', p.get('title', '')).upper()
                
                # Simplified simulation of the "Intel Core" fallback logic
                # logic: if matches "GEN" but NOT i3/i5/i7/i9/N100/etc.
                
                # 1. Skip if it has explicit I3/I5/I7/I9/ULTRA/N-Series/CELERON
                if re.search(r'\bI[3579]\b', t): continue
                if re.search(r'\b(CORE|INTEL)\s?([3579])\b', t): continue # Core 5, Intel 7
                if re.search(r'\b(N100|N200|N4000|N4500|N5000|N95)\b', t): continue
                if "CELERON" in t or "PENTIUM" in t: continue
                if "RYZEN" in t or "AMD" in t: continue
                
                # 2. Check for Gen pattern that triggers the fallback
                # Regex from productUtils: /\d{1,2}(È|TH|ND|RD)?\s?G(É|E)N/
                if re.search(r'\d{1,2}(È|TH|ND|RD)?\s?G(É|E)N', t):
                    print(f"[{fp}] GENERIC: {t}")
                    count += 1
                elif "INTEL CORE" in t and not any(k in t for k in ["I3","I5","I7","I9"]):
                     # Also catch explicit "Intel Core" mentions that miss specific models
                     print(f"[{fp}] EXPLICIT GENERIC: {t}")
                     count += 1

    except Exception as e:
        pass

print(f"\nTotal Potential Generic 'Intel Core': {count}")
