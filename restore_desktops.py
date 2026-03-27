import json
import os
import glob
import re

# Restoration Map: Source -> Target
RESTORE_MAP = {
    "frontend/src/data/tunisianet_clean.json": "frontend/src/data/tunisianet_new.json", 
    "frontend/src/data/mytek_raw.json": "frontend/src/data/mytek_test.json", # assuming test was raw copy
    "frontend/src/data/wiki_clean.json": "frontend/src/data/wiki_raw.json"   # assuming raw was copy of clean or vice versa? 
    # Actually wiki_raw is usually the source. But I deleted from wiki_raw. 
    # Let's check sizes. Wiki raw was 500KB. now 483KB. 
    # wiki_clean is 384KB. 
    # I should probably just restore tunisianet_new from tunisianet_clean or raw.
}

def normalize_cpu_simple(cpu):
    if not cpu: return "Unknown"
    c = cpu.upper()
    if "I3" in c or "I5" in c or "I7" in c or "RYZEN" in c or "M1" in c or "M2" in c or "M3" in c:
        return "Known"
    return "Unknown"

def restore_and_refine():
    # Restore from raw to get the full dataset back
    try:
        source = "frontend/src/data/tunisianet_raw.json"
        target = "frontend/src/data/tunisianet_new.json"
        
        with open(source, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"Restored {len(data)} items from {os.path.basename(source)}")
        
        # Write back immediately to confirm restoration
        with open(target, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"Restored {target} to {len(data)} items.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    restore_and_refine()
