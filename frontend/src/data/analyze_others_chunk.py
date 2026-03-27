import json
import os
import glob
from collections import Counter

# Set up paths
data_dir = r"c:\Users\USER\Documents\programmation\frontend\src\data"
files = glob.glob(os.path.join(data_dir, "*_mobiles.json")) + glob.glob(os.path.join(data_dir, "samsung_tunisie.json")) + glob.glob(os.path.join(data_dir, "*_phones.json"))

others_titles = []
unisoc_titles = []

print("Simulating CPU Classification to find 'Others'...")

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
            
            # --- SIMULATE JS LOGIC (Updated to match MobilesPage.jsx Chunk 3) ---
            
             # 1. 5G/Model Force
            # Samsung A-series 5G -> Exynos (Removed aggresive rule, but check if we need to simulate valid detection)
            
            # 2. Chunk 1/Refinement Targets
            isHonorHelio = ('honor x5' in t_lower or 'honor x6' in t_lower or 'play 10' in t_lower)
            isHonorSnapdragon = ('honor x7' in t_lower or 'honor x8' in t_lower or 'honor x9' in t_lower or 'honor 90' in t_lower or 'honor 70' in t_lower or 'honor 50' in t_lower or 'honor 400' in t_lower or 'honor 200' in t_lower)
            
            isItelHelio = ('itel rs4' in t_lower or 'itel s24' in t_lower)
            # isItelUnisoc removed
            
            # isInfinixUnisoc removed
            
            isRealmeUnisoc = ('realme c61' in t_lower or 'realme c53' in t_lower or 'realme c51' in t_lower or 'realme c33' in t_lower or 'realme c30' in t_lower or 'realme note 50' in t_lower or 'realme c55' in t_lower) 
            isRealmeHelio = ('realme c55' in t_lower or 'realme 11 ' in t_lower)
            
            isRedmiHelio = ('redmi a5' in t_lower or 'redmi a3' in t_lower or 'redmi a2' in t_lower or 'redmi a1' in t_lower)
            isVivoHelio = ('vivo y' in t_lower or 'vivo v' in t_lower)
            isOscalHelio = ('oscal tiger' in t_lower)
            
            # Chunk 3: Infinix & Tecno
            isInfinixDimensity = ('infinix gt' in t_lower)
            isInfinixHot50_60_5G = (('hot 50' in t_lower or 'hot 60' in t_lower) and '5g' in t_lower)
            isInfinixHot50_60_4G = (('hot 50' in t_lower or 'hot 60' in t_lower) and '5g' not in t_lower)
            
            isTecnoPova = ('tecno pova' in t_lower)
            isTecnoSparkGo = ('spark go' in t_lower)
            isTecnoSparkHelio = (('spark 20' in t_lower or 'spark 30' in t_lower or 'spark 10' in t_lower) and not isTecnoSparkGo)
            
            # Chunk 4: Fallbacks & Samsung
            isRedmiUnisoc = ('redmi a5' in t_lower)
            isSamsungGeneric = (('galaxy a' in t_lower or 'galaxy s' in t_lower or 'smartphone samsung' in t_lower) and 'snapdragon' not in t_lower)
            isItelFallback = ('itel a' in t_lower or 'itel p' in t_lower or 'itel s' in t_lower)
            isInfinixFallback = ('infinix smart' in t_lower)

            # Quad Core Logic
            isQuadCore = (
                'quad core' in full_text or 'quad-core' in full_text or '4 core' in full_text or '4-core' in full_text or
                'itel a33' in t_lower or 'itel a17' in t_lower or 'itel a16' in t_lower or 'itel a37' in t_lower or 'itel a14' in t_lower or
                'evertek' in t_lower or 
                'nokia c1 ' in t_lower or 'nokia c10' in t_lower or 'nokia c2 ' in t_lower
            )

            # Apply Logic
            if isQuadCore and cpu != "Quad Core":
                 cpu = "Quad Core"
            
            if cpu != "Quad Core":
                if isHonorHelio: cpu = "MediaTek Helio"
                elif isHonorSnapdragon: cpu = "Snapdragon"
                elif isItelHelio: cpu = "MediaTek Helio"
                
                elif isRealmeHelio: cpu = "MediaTek Helio"
                elif isRealmeUnisoc: cpu = "Unisoc"
                elif isRedmiHelio: cpu = "MediaTek Helio"
                elif isVivoHelio: cpu = "MediaTek Helio"
                elif isOscalHelio: cpu = "MediaTek Helio"
                
                elif isInfinixDimensity: cpu = "MediaTek Dimensity"
                elif isInfinixHot50_60_5G: cpu = "MediaTek Dimensity"
                elif isInfinixHot50_60_4G: cpu = "MediaTek Helio"
                elif isTecnoPova: cpu = "MediaTek Helio"
                elif isTecnoSparkGo: cpu = "Unisoc"
                elif isTecnoSparkHelio: cpu = "MediaTek Helio"
                
                # Chunk 4
                elif isRedmiUnisoc: cpu = "Unisoc"
                elif isSamsungGeneric: cpu = "Samsung Exynos"
                
                # Fallbacks (Only if nothing else caught it)
                elif isItelFallback: cpu = "Octa Core"
                elif isInfinixFallback: cpu = "Octa Core"
                
                # Apple Force
                elif p.get('brand') == 'Apple' or 'iphone' in t_lower: cpu = "Apple A-Series"
                
                # Broad Helio Force
                elif (
                    ('galaxy a05' in t_lower or 'galaxy a06' in t_lower or ('galaxy a15' in t_lower and '5g' not in t_lower) or ('galaxy a16' in t_lower and '5g' not in t_lower)) or
                    ('redmi 13c' in t_lower or 'redmi 12c' in t_lower or 'redmi 12 ' in t_lower or 'redmi a3' in t_lower or 'redmi a2' in t_lower) or
                    (('hot 40' in t_lower or 'hot 30' in t_lower or 'spark 20' in t_lower or 'spark 10' in t_lower or 'camon 20' in t_lower or 'note 30' in t_lower) and '5g' not in t_lower)
                ):
                     cpu = "MediaTek Helio"
                     
                # Normalization
                if cpu and ('helio' in cpu.lower() or 'hélio' in cpu.lower() or ('mediatek' in cpu.lower() and 'dimensity' not in cpu.lower())): cpu = "MediaTek Helio"
                elif cpu and 'qualcomm' in cpu.lower(): cpu = "Snapdragon"

                # Text Inference
                if not cpu or cpu in ["Unknown", "N/A", "Others", "Octa Core"]:
                    if 'helio' in full_text or 'g99' in full_text or 'g88' in full_text or 'g85' in full_text or 'g96' in full_text or 'g37' in full_text or 'g36' in full_text: cpu = "MediaTek Helio"
                    elif 'snapdragon' in full_text or 'qualcomm' in full_text: cpu = "Snapdragon"
                    elif 'dimensity' in full_text: cpu = "MediaTek Dimensity"
                    elif 'exynos' in full_text: cpu = "Samsung Exynos"
                    elif 'unisoc' in full_text or 'tiger' in full_text: cpu = "Unisoc"
                    elif 'tensor' in full_text: cpu = "Google Tensor"
                    elif 'kirin' in full_text: cpu = "HiSilicon Kirin"
                    elif 'bionic' in full_text: cpu = "Apple A-Series"
                    elif 'octa core' in full_text or 'octa-core' in full_text: cpu = "Octa Core"
                    elif 'quad core' in full_text: cpu = "Quad Core"
                    else: cpu = "Others"

            if cpu == "Others":
                others_titles.append(title)
            
            if cpu == "Unisoc":
                if 'infinix' in t_lower:
                    unisoc_titles.append(title)

    except Exception as e:
        pass

print(f"Total 'Others' found: {len(others_titles)}")
print(f"Total Infinix in 'Unisoc': {len(unisoc_titles)}")

print("\n--- INFINIX TITLES IN UNISOC ---")
for t in unisoc_titles:
    print(t)

# Analyze patterns
# We want to find common model names in the list
words = []
for t in others_titles:
    # simple tokenization
    parts = t.replace('-', ' ').replace('/', ' ').split()
    # Keep pairs of words to find models like "Galaxy A54", "Redmi Note", etc
    if len(parts) >= 2:
        words.append(parts[0] + " " + parts[1])
        if len(parts) >= 3:
             words.append(parts[0] + " " + parts[1] + " " + parts[2])

print("\nTop 50 Recurring Patterns in 'Others':")
c = Counter(words)
for k, v in c.most_common(50):
    print(f"{k}: {v}")

print("\nFirst 30 Unique Titles:")
unique = sorted(list(set(others_titles)))
for t in unique[:30]:
    print(t)
