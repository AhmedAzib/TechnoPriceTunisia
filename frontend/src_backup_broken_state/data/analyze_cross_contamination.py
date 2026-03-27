import json
import os
import glob
from collections import Counter

# Define paths
data_dir = r"c:\Users\USER\Documents\programmation\frontend\src\data"
files = glob.glob(os.path.join(data_dir, "*_mobiles.json")) + glob.glob(os.path.join(data_dir, "samsung_tunisie.json")) + glob.glob(os.path.join(data_dir, "*_phones.json"))

# Simulating the Categories
helio_bucket = []
unisoc_bucket = []
octa_bucket = []

# Keywords
helio_keywords = ['helio', 'g99', 'g88', 'g85', 'g96', 'g37', 'g36', 'g91', 'g81', 'p35', 'g25']
unisoc_keywords = ['unisoc', 'tiger', 't606', 't612', 't616', 't603', 'sc9863', 'sc7731', 'spreadtrum']

def check_keywords(text, keywords):
    for k in keywords:
        if k in text:
            return k
    return None

print("Loading Data...")

all_products = []
for f in files:
    try:
        with open(f, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if isinstance(data, list):
                all_products.extend(data)
            elif isinstance(data, dict): # Handle dict wrappers if any
                for key in data:
                    if isinstance(data[key], list):
                        all_products.extend(data[key])
    except Exception as e:
        print(f"Error loading {f}: {e}")

print(f"Total Products: {len(all_products)}")

# --- SIMULATE CURRENT CLASSIFICATION -- 
# Reuse logic from analyze_others_chunk but tailored to populate specific buckets
# We need to copy the LATEST logic here to correspond to current state
# ... (Simplified logic copying main parts)

for p in all_products:
    title = p.get('title', '')
    specs = p.get('specs', {})
    t_lower = title.lower()
    full_text = (title + " " + specs.get('raw', '')).lower()
    
    cpu = "Others"
    
    # --- LOGIC START ---
    
    # ... (Quad Core logic - skip for this analysis, we want Octa/Helio/Unisoc)
    
    # Flags (Copied from MobilesPage updates)
    isRedmiHelio = ('redmi a3' in t_lower or 'redmi a2' in t_lower or 'redmi a1' in t_lower)
    isRedmiUnisoc = ('redmi a5' in t_lower)
    isHonorHelio = ('honor x5' in t_lower or 'honor x6' in t_lower or 'play 10' in t_lower)
    isHonorSnapdragon = ('honor x7' in t_lower or 'honor x8' in t_lower or 'honor x9' in t_lower or 'honor 90' in t_lower)
    isItelHelio = ('itel rs4' in t_lower or 'itel s24' in t_lower)
    isRealmeHelio = ('realme c55' in t_lower or 'realme 11 ' in t_lower)
    isRealmeUnisoc = ('realme c61' in t_lower or 'realme c53' in t_lower or 'realme c51' in t_lower or 'realme c33' in t_lower or 'realme c30' in t_lower or 'realme note 50' in t_lower)
    isVivoHelio = ('vivo y' in t_lower or 'vivo v' in t_lower)
    isOscalHelio = ('oscal tiger' in t_lower)
    
    isInfinixDimensity = ('infinix gt' in t_lower)
    isInfinixHot50_60_5G = (('hot 50' in t_lower or 'hot 60' in t_lower) and '5g' in t_lower)
    isInfinixHot50_60_4G = (('hot 50' in t_lower or 'hot 60' in t_lower) and '5g' not in t_lower)
    isTecnoPova = ('tecno pova' in t_lower)
    isTecnoSparkGo = ('spark go' in t_lower)
    isTecnoSparkHelio = (('spark 20' in t_lower or 'spark 30' in t_lower or 'spark 10' in t_lower) and not isTecnoSparkGo)
    
    isSamsungGeneric = (('galaxy a' in t_lower or 'galaxy s' in t_lower or 'smartphone samsung' in t_lower) and 'snapdragon' not in t_lower)
    isItelFallback = ('itel a' in t_lower or 'itel p' in t_lower or 'itel s' in t_lower)
    isInfinixFallback = ('infinix smart' in t_lower)

    # Apply
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
    elif isRedmiUnisoc: cpu = "Unisoc"
    elif isSamsungGeneric: cpu = "Samsung Exynos"
    elif isItelFallback: cpu = "Octa Core"
    elif isInfinixFallback: cpu = "Octa Core"
    
    # Generic Inference
    if cpu == "Others":
        if 'helio' in full_text or 'g99' in full_text or 'g88' in full_text or 'g85' in full_text or 'g96' in full_text or 'g37' in full_text or 'g36' in full_text: cpu = "MediaTek Helio"
        elif 'unisoc' in full_text or 'tiger' in full_text: cpu = "Unisoc"
        elif 'octa core' in full_text or 'octa-core' in full_text: cpu = "Octa Core"

    # --- BUCKET ASSIGNMENT ---
    if cpu == "MediaTek Helio":
        helio_bucket.append((title, full_text))
    elif cpu == "Unisoc":
        unisoc_bucket.append((title, full_text))
    elif cpu == "Octa Core":
        octa_bucket.append((title, full_text))


# --- ANALYSIS ---
print("\n--- ANALYZING CROSS-CONTAMINATION ---")

print(f"\n1. UNISOC Bucket ({len(unisoc_bucket)}) checking for HELIO keywords:")
count = 0
for title, f in unisoc_bucket:
    k = check_keywords(f, helio_keywords)
    if k:
        print(f"  [WARN] Found '{k}' in Unisoc item: {title}")
        count += 1
if count == 0: print("  Clean.")

print(f"\n2. HELIO Bucket ({len(helio_bucket)}) checking for UNISOC keywords:")
count = 0
for title, f in helio_bucket:
    k = check_keywords(f, unisoc_keywords)
    # Ignore 'tiger' if oscal tiger (handled)
    if k == 'tiger' and 'oscal' in f: continue
    
    if k:
        print(f"  [WARN] Found '{k}' in Helio item: {title}")
        count += 1
if count == 0: print("  Clean.")

print(f"\n3. OCTA CORE Bucket ({len(octa_bucket)}) checking for HELIO/UNISOC keywords:")
count_h = 0
count_u = 0
for title, f in octa_bucket:
    k_h = check_keywords(f, helio_keywords)
    k_u = check_keywords(f, unisoc_keywords)
    
    if k_h:
        print(f"  [INFO] Can upgrade Octa -> Helio ({k_h}): {title}")
        count_h += 1
    if k_u:
        print(f"  [INFO] Can upgrade Octa -> Unisoc ({k_u}): {title}")
        count_u += 1

print(f"\nSummary: Found {count_h} potential Helios and {count_u} potential Unisocs in Octa Core.")
