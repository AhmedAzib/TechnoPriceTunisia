import json
import os
import glob
from collections import Counter

# Set up paths
data_dir = r"c:\Users\USER\Documents\programmation\frontend\src\data"
files = glob.glob(os.path.join(data_dir, "*_mobiles.json")) + glob.glob(os.path.join(data_dir, "samsung_tunisie.json")) + glob.glob(os.path.join(data_dir, "*_phones.json"))

unisoc_titles = []

print("Simulating CPU Classification to find 'Unisoc' composition...")

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
            
             # 1. Quad Core
            isQuadCore = (
                'quad core' in full_text or 'quad-core' in full_text or '4 core' in full_text or '4-core' in full_text or
                'lesia young' in t_lower or 'itel a33' in t_lower or 'itel a17' in t_lower or 'itel a16' in t_lower or 'itel a14' in t_lower or
                'evertek' in t_lower or 'nokia c1' in t_lower or 'nokia c2' in t_lower
            )
            if isQuadCore: cpu = "Quad Core"
            
            else:
                # 2. Apple
                if p.get('brand') == 'Apple' or 'iphone' in t_lower: cpu = "Apple A-Series"
                
                # 3. Forced Mappings
                elif 'honor' in t_lower and ('x5' in t_lower or 'x6' in t_lower or 'play 10' in t_lower): cpu = "MediaTek Helio"
                elif 'honor' in t_lower and ('x7' in t_lower or 'x8' in t_lower or 'x9' in t_lower or '90' in t_lower or '70' in t_lower or '50' in t_lower or '400' in t_lower or '200' in t_lower): cpu = "Snapdragon"
                
                elif 'itel' in t_lower and ('rs4' in t_lower or 's24' in t_lower): cpu = "MediaTek Helio"
                elif 'itel' in t_lower and ('a70' in t_lower or 'p55' in t_lower or 's23' in t_lower or 'a05' in t_lower or 'a50' in t_lower or 'a90' in t_lower or 'a60' in t_lower or 'a48' in t_lower or 'p40' in t_lower): cpu = "Unisoc"
                
                elif 'infinix' in t_lower and ('smart 10' in t_lower or 'smart 9' in t_lower or 'smart 8' in t_lower): cpu = "Unisoc"
                
                elif 'realme' in t_lower and ('c61' in t_lower or 'c53' in t_lower or 'c51' in t_lower or 'c33' in t_lower or 'c30' in t_lower or 'note 50' in t_lower): cpu = "Unisoc"
                elif 'realme' in t_lower and ('c55' in t_lower or '11 ' in t_lower): cpu = "MediaTek Helio"
                
                elif 'lesia' in t_lower or 'clever' in t_lower or 'evertek' in t_lower or 'iku' in t_lower: cpu = "Unisoc"
                
                # 4. Helio Force
                elif (
                    ('galaxy a05' in t_lower or 'galaxy a06' in t_lower or ('galaxy a15' in t_lower and '5g' not in t_lower) or ('galaxy a16' in t_lower and '5g' not in t_lower)) or
                    ('redmi 13c' in t_lower or 'redmi 12c' in t_lower or 'redmi 12 ' in t_lower or 'redmi a3' in t_lower or 'redmi a2' in t_lower) or
                    (('hot 40' in t_lower or 'hot 30' in t_lower or 'spark 20' in t_lower or 'spark 10' in t_lower or 'camon 20' in t_lower or 'note 30' in t_lower) and '5g' not in t_lower)
                ):
                     cpu = "MediaTek Helio"

                # 5. Normalization
                elif cpu and ('helio' in cpu.lower() or 'hélio' in cpu.lower() or ('mediatek' in cpu.lower() and 'dimensity' not in cpu.lower())): cpu = "MediaTek Helio"
                elif cpu and 'qualcomm' in cpu.lower(): cpu = "Snapdragon"
                
                # 6. Keyword Inference
                if not cpu or cpu in ["Unknown", "N/A", "Others", "Octa Core"]:
                    if 'helio' in full_text or 'g99' in full_text or 'g88' in full_text or 'g85' in full_text or 'g96' in full_text or 'g37' in full_text or 'g36' in full_text: cpu = "MediaTek Helio"
                    elif 'snapdragon' in full_text or 'qualcomm' in full_text: cpu = "Snapdragon"
                    elif 'dimensity' in full_text: cpu = "MediaTek Dimensity"
                    elif 'exynos' in full_text: cpu = "Samsung Exynos"
                    elif 'unisoc' in full_text or 'tiger' in full_text: cpu = "Unisoc"
                    elif 'tensor' in full_text: cpu = "Google Tensor"
                    elif 'kirin' in full_text: cpu = "HiSilicon Kirin"
                    elif 'bionic' in full_text: cpu = "Apple A-Series"
                    
            if cpu == "Unisoc":
                unisoc_titles.append(title)

    except Exception as e:
        pass

print(f"Total 'Unisoc' found: {len(unisoc_titles)}")

print("\n--- FIRST 50 UNISOC TITLES ---")
for t in unisoc_titles[:50]:
    print(t)

print("\n--- CHECKING FOR 'SAMSUNG' OR 'XIAOMI' IN UNISOC ---")
for t in unisoc_titles:
    if 'samsung' in t.lower() or 'xiaomi' in t.lower() or 'redmi' in t.lower():
        print(f"WARN: {t}")
