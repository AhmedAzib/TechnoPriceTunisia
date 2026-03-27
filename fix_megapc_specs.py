import json
import os
import re

GAMER_PATH = r"C:\Users\USER\Documents\programmation\frontend\src\data\megapc_gamer.json"
PRO_PATH = r"C:\Users\USER\Documents\programmation\frontend\src\data\megapc_pro.json"
CPU_PATH = r"C:\Users\USER\Documents\programmation\frontend\src\data\megapc_processors.json"

# Master Visual Database
CPU_IMAGES = {
    "3100": "https://www.tunisianet.com.tn/171505-large/processeur-amd-ryzen-3-3100-36-ghz-18-mo-cache.jpg",
    "3200G": "https://www.tunisianet.com.tn/143527-large/processeur-amd-ryzen-3-3200g-wraith-stealth-edition-36-ghz-4-ghz.jpg",
    "3400G": "https://www.tunisianet.com.tn/111453-large/processeur-amd-ryzen-5-3400g-37-ghz-42-ghz.jpg",
    "3600": "https://www.tunisianet.com.tn/143528-large/processeur-amd-ryzen-5-3600-36-ghz-42-ghz.jpg",
    "4100": "https://www.tunisianet.com.tn/257321-large/processeur-amd-ryzen-3-4100-38-ghz-4-ghz.jpg",
    "5500": "https://www.tunisianet.com.tn/257322-large/processeur-amd-ryzen-5-5500-36-ghz-up-to-42-ghz.jpg",
    "5500GT": "https://www.tunisianet.com.tn/346853-large/processeur-amd-ryzen-5-5500gt-36-ghz-up-to-44-ghz-19-mo.jpg",
    "5600": "https://www.tunisianet.com.tn/257324-large/processeur-amd-ryzen-5-5600-35-ghz-up-to-44-ghz.jpg",
    "5600G": "https://www.tunisianet.com.tn/213501-large/processeur-amd-ryzen-5-5600g-39-ghz-up-to-44-ghz.jpg",
    "5600X": "https://www.tunisianet.com.tn/186523-large/processeur-amd-ryzen-5-5600x-37-ghz-up-to-46-ghz.jpg",
    "5700": "https://www.tunisianet.com.tn/346852-large/processeur-amd-ryzen-7-5700-37-ghz-up-to-46-ghz-20-mo.jpg",
    "5700G": "https://www.tunisianet.com.tn/213502-large/processeur-amd-ryzen-7-5700g-38-ghz-up-to-46-ghz.jpg",
    "5700X": "https://www.tunisianet.com.tn/257325-large/processeur-amd-ryzen-7-5700x-34-ghz-up-to-46-ghz.jpg",
    "5800X": "https://www.tunisianet.com.tn/186524-large/processeur-amd-ryzen-7-5800x-38-ghz-up-to-47-ghz.jpg",
    "7400F": "https://www.tunisianet.com.tn/360216-large/processeur-amd-ryzen-5-7400f-47-ghz-18-mo-am5.jpg",
    "7500F": "https://www.tunisianet.com.tn/346851-large/processeur-amd-ryzen-5-7500f-37-ghz-up-to-50-ghz-38-mo.jpg",
    "7600": "https://www.tunisianet.com.tn/285521-large/processeur-amd-ryzen-5-7600-jusqu-a-51-ghz-38-mo-cache.jpg",
    "7600X": "https://www.tunisianet.com.tn/271708-large/processeur-amd-ryzen-5-7600x-jusqu-a-53-ghz-38-mo-cache.jpg",
    "7700": "https://www.tunisianet.com.tn/285522-large/processeur-amd-ryzen-7-7700-jusqu-a-53-ghz-38-mo-cache.jpg",
    "7700X": "https://www.tunisianet.com.tn/271709-large/processeur-amd-ryzen-7-7700x-jusqu-a-54-ghz-40-mo-cache.jpg",
    "7800X3D": "https://www.tunisianet.com.tn/294717-large/processeur-amd-ryzen-7-7800x3d-8-coeurs-16-threads-jusqu-a-50-ghz.jpg",
    "7900X": "https://www.tunisianet.com.tn/271710-large/processeur-amd-ryzen-9-7900x-jusqu-a-56-ghz-76-mo-cache.jpg",
    "8400F": "https://www.tunisianet.com.tn/361834-large/processeur-amd-ryzen-5-8400f-jusqu-a-47-ghz-16-mo-am5.jpg",
    "9600X": "https://www.tunisianet.com.tn/356525-large/processeur-amd-ryzen-5-9600x-jusqu-a-54-ghz-38-mo-cache.jpg",
    "9800X3D": "https://www.tunisianet.com.tn/361832-large/processeur-amd-ryzen-7-9800x3d-jusqu-a-52-ghz-104-mo-cache.jpg",
    "9950X": "https://www.tunisianet.com.tn/356528-large/processeur-amd-ryzen-9-9950x-jusqu-a-57-ghz-80-mo-cache.jpg",
    "10105F": "https://www.tunisianet.com.tn/205608-large/processeur-intel-core-i3-10105f-37-ghz-44-ghz.jpg",
    "10600K": "https://www.tunisianet.com.tn/171506-large/processeur-intel-core-i5-10600k-41-ghz-12-mo-cache.jpg",
    "12400": "https://www.tunisianet.com.tn/241857-large/processeur-intel-core-i5-12400-jusqu-a-44-ghz-18-mo.jpg",
    "12400F": "https://www.tunisianet.com.tn/241858-large/processeur-intel-core-i5-12400f-jusqu-a-44-ghz-18-mo.jpg",
    "12600KF": "https://www.tunisianet.com.tn/233045-large/processeur-intel-core-i5-12600kf-jusqu-a-49-ghz-20-mo.jpg",
    "12700KF": "https://www.tunisianet.com.tn/233044-large/processeur-intel-core-i7-12700kf-jusqu-a-50-ghz-25-mo.jpg",
    "14400F": "https://www.tunisianet.com.tn/334857-large/processeur-intel-core-i5-14400f-jusqu-a-47-ghz-20-mo.jpg",
    "14600K": "https://www.tunisianet.com.tn/324853-large/processeur-intel-core-i5-14600k-jusqu-a-53-ghz-24-mo.jpg",
    "14600KF": "https://www.tunisianet.com.tn/324854-large/processeur-intel-core-i5-14600kf-jusqu-a-53-ghz-24-mo.jpg",
    "14700F": "https://www.tunisianet.com.tn/334858-large/processeur-intel-core-i7-14700f-jusqu-a-54-ghz-33-mo.jpg",
    "14700KF": "https://www.tunisianet.com.tn/324857-large/processeur-intel-core-i7-14700kf-jusqu-a-56-ghz-33-mo.jpg",
    "14900KF": "https://www.tunisianet.com.tn/324859-large/processeur-intel-core-i9-14900kf-jusqu-a-60-ghz-36-mo.jpg",
    "245KF": "https://www.tunisianet.com.tn/361835-large/processeur-intel-core-ultra-5-245kf-jusqu-a-52-ghz-24-mo-cache.jpg",
    "265K": "https://www.tunisianet.com.tn/361834-large/processeur-intel-core-ultra-7-265k-jusqu-a-55-ghz-30-mo-cache.jpg",
    "285K": "https://www.tunisianet.com.tn/361833-large/processeur-intel-core-ultra-9-285k-jusqu-a-57-ghz-36-mo-cache.jpg",
}

def is_cpu(title):
    t = title.upper()
    # It's a CPU if it has Ryzen or Intel Core, BUT not if it has "PC PORTABLE" or "LAPTOP" or "UNITE"
    if ("RYZEN" in t or "INTEL CORE" in t or "ULTRA 5" in t or "ULTRA 7" in t or "ULTRA 9" in t):
        if "PORTABLE" in t or "LAPTOP" in t or "UNITE" in t or "|" in t or "GB" in t: # Heuristics for laptops/towers
             return False
        return True
    return False

def clean_title_model(title):
    match = re.search(r"([0-9]{4,5}[XKGFTUD]{0,3}|[0-9]{3}0[XKGFTUD]{0,3})", title, re.IGNORECASE)
    if match: return match.group(1).upper()
    return None

def process_file(path, force_cpu=False):
    if not os.path.exists(path): return []
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    clean_data = []
    for item in data:
        t = item['title'].upper()
        
        # 1. Detect and Fix Processors
        is_p = is_cpu(item['title']) or force_cpu
        
        if is_p:
            # 2. Image & Model Matching
            # User requested strictly source images. We ONLY clean up specs.
            # Images are trusted from the scraper (scrape_megapc_processors.py)
            
            # 3. Specs Matching (Only update technical specs)
            # Check for model match
            model = clean_title_model(item['title'])
            if model:
                # This part is for spec normalization, not image replacement
                # For example, if we want to add a 'model' field based on the title
                # item['model'] = model 
                pass # Keeping the logic for model extraction, but not using it to overwrite image
        
        clean_data.append(item)
    return clean_data

def main():
    # 1. Clean PC Gamer (Remove CPUs)
    gamer_data = []
    with open(GAMER_PATH, 'r', encoding='utf-8') as f:
        for item in json.load(f):
            if not is_cpu(item['title']):
                gamer_data.append(item)
            else:
                print(f"Purging CPU from PC Gamer: {item['title']}")
                
    # 2. Clean PC Pro (Remove CPUs)
    pro_data = []
    with open(PRO_PATH, 'r', encoding='utf-8') as f:
        for item in json.load(f):
            if not is_cpu(item['title']):
                pro_data.append(item)
            else:
                print(f"Purging CPU from PC Pro: {item['title']}")

    # 3. Clean Processors (Force CPU visuals)
    cpu_data = process_file(CPU_PATH, force_cpu=True)
    
    # Save all
    with open(GAMER_PATH, 'w', encoding='utf-8') as f: json.dump(gamer_data, f, indent=2, ensure_ascii=False)
    with open(PRO_PATH, 'w', encoding='utf-8') as f: json.dump(pro_data, f, indent=2, ensure_ascii=False)
    with open(CPU_PATH, 'w', encoding='utf-8') as f: json.dump(cpu_data, f, indent=2, ensure_ascii=False)
    
    print("MegaPC Master Purge & Visual Fix Complete.")

if __name__ == "__main__":
    main()
