import json
import os
import glob

def clean_desktops(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        initial_count = len(data)
        cleaned_data = []
        
        desktop_keywords = [
            "pc de bureau", "unité centrale", "unite centrale", 
            "all in one", "all-in-one", "aio ", " aio",
            "mini pc", "bmax", # BMAX are mini PCs in this context usually
            "thinkcentre", "optiplex", "prodesk", "elitedesk", "ideacentre",
            "esprimo", "veriton", "vostro desktop", "inspiron desktop",
            "station de travail fixe", "tower", "sff "
        ]
        
        for p in data:
            t = (p.get('title') or p.get('name') or "").lower()
            
            # Safety: If it explicitly says "Portable" or "Laptop", assume it's a laptop
            # unless it also says "NON PORTABLE" (unlikely)
            if "portable" in t or "laptop" in t:
                cleaned_data.append(p)
                continue
                
            is_desktop = False
            for k in desktop_keywords:
                if k in t:
                    is_desktop = True
                    break
            
            if is_desktop:
                continue
            
            cleaned_data.append(p)
            
        removed = initial_count - len(cleaned_data)
        
        if removed > 0:
            print(f"[{os.path.basename(path)}] Removed {removed} desktops.")
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
        else:
            print(f"[{os.path.basename(path)}] Clean.")
            
    except Exception as e:
        print(f"Error {path}: {e}")

files = glob.glob("frontend/src/data/*.json")
for file_path in files:
    clean_desktops(file_path)
