import json
import os
import re

# File paths based on masterData.js
FILES = [
    "frontend/src/data/mytek_mobiles.json",
    "frontend/src/data/tunisianet_mobiles.json",
    "frontend/src/data/tunisiatech_mobiles.json",
    "frontend/src/data/wiki_mobiles.json",
    "frontend/src/data/spacenet_mobiles.json",
    "frontend/src/data/tdiscount_mobiles.json"
]

def load_data():
    all_products = []
    for file_path in FILES:
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Add source based on filename for debugging
                    source = os.path.basename(file_path).split('_')[0].title()
                    for p in data:
                        p['source'] = source
                        all_products.append(p)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
    return all_products

def classify(p):
    # SIMULATING MobilesPage.jsx LOGIC
    t = (p.get('title') or '').lower()
    specs = p.get('specs', {})
    if not specs: specs = {}
    
    cpu = specs.get('cpu', 'Unknown')
    brand = p.get('brand', 'Unknown')
    
    # --- BRAND INFERENCE (Simplified for CPU logic context) ---
    if not brand or brand == 'Unknown':
        if 'samsung' in t: brand = 'Samsung'
        elif 'apple' in t or 'iphone' in t: brand = 'Apple'
        elif 'xiaomi' in t or 'redmi' in t or 'poco' in t: brand = 'Xiaomi'
        elif 'oppo' in t: brand = 'Oppo'
        elif 'infinix' in t: brand = 'Infinix'
        elif 'tecno' in t: brand = 'Tecno'
        elif 'vivo' in t: brand = 'Vivo'
        elif 'honor' in t: brand = 'Honor'
        elif 'realme' in t: brand = 'Realme'
        elif 'huawei' in t: brand = 'Huawei'
        elif 'nokia' in t: brand = 'Nokia'
        elif 'itel' in t: brand = 'Itel'
        elif 'zte' in t or 'nubia' in t: brand = 'ZTE'
        elif 'lesia' in t: brand = 'Lesia'
        elif 'blackview' in t or 'oscal' in t: brand = 'Blackview'
        elif 'evertek' in t: brand = 'Evertek'
        elif 'logicom' in t: brand = 'Logicom'
        elif 'iku' in t: brand = 'IKU'
        elif 'oukitel' in t: brand = 'Oukitel'
        elif 'doogee' in t: brand = 'Doogee'
        elif 'cubot' in t: brand = 'Cubot'
        elif 'tcl' in t: brand = 'TCL'
        elif 'google' in t or 'pixel' in t: brand = 'Google'
    
    # --- CPU LOGIC REPLICATION ---
    
    # 1. Force Apple
    if brand == 'Apple' or 'iphone' in t:
        cpu = "Apple A-Series"

    # 2. Logic Variables
    tLower = t
    fullText = t # Simplified
    
    isHelioModel = (
        ('galaxy a05' in tLower) or ('galaxy a06' in tLower) or 
        ('galaxy a15' in tLower and '5g' not in tLower) or 
        ('galaxy a16' in tLower and '5g' not in tLower) or
        ('redmi 13c' in tLower) or ('redmi 12c' in tLower) or ('redmi 12 ' in tLower) or ('redmi a3' in tLower) or ('redmi a2' in tLower) or
        (('hot 40' in tLower or 'hot 30' in tLower or 'spark 20' in tLower or 'spark 10' in tLower or 'camon 20' in tLower or 'note 30' in tLower) and '5g' not in tLower)
    )

    isHuaweiSnapdragon = 'nova 8' in tLower or 'nova 9' in tLower or 'nova 10' in tLower or 'nova 11' in tLower or 'nova y90' in tLower
    isOnePlusNordMTK = ('nord 2' in tLower or 'nord ce' in tLower or 'nord 3' in tLower) and 'nord n10' not in tLower
    
    isHonorHelio = 'honor x5' in tLower or 'honor x6' in tLower or 'play 10' in tLower
    isHonorSnapdragon = 'honor x7' in tLower or 'honor x8' in tLower or 'honor x9' in tLower or 'honor 90' in tLower or 'honor 70' in tLower or 'honor 50' in tLower or 'honor 400' in tLower or 'honor 200' in tLower
    
    isItelHelio = 'itel rs4' in tLower or 'itel s24' in tLower
    isItelUnisoc = 'itel a70' in tLower or 'itel p55' in tLower or 'itel s23' in tLower or 'itel a05' in tLower or 'itel a50' in tLower or 'itel a90' in tLower or 'itel a48' in tLower or 'itel p40' in tLower

    isInfinixUnisoc = 'infinix smart 10' in tLower or 'infinix smart 9' in tLower or 'infinix smart 8' in tLower
    
    isSamsungExynos = ('galaxy a16' in tLower and '5g' in tLower) or 'galaxy a26' in tLower or 'galaxy a36' in tLower or 'galaxy a56' in tLower or 'galaxy s25' in tLower
    isSamsungZSeries = 'galaxy z' in tLower or 'fold' in tLower or 'flip' in tLower
    
    isRealmeUnisoc = 'realme c61' in tLower or 'realme c53' in tLower or 'realme c51' in tLower or 'realme c33' in tLower or 'realme c30' in tLower or 'realme note 50' in tLower or 'realme c55' in tLower
    isRealmeHelio = 'realme c55' in tLower or 'realme 11 ' in tLower
    
    isRedmiHelio = 'redmi a3' in tLower or 'redmi a2' in tLower or 'redmi a1' in tLower
    isRedmiUnisoc = 'redmi a5' in tLower
    
    isVivoUnisoc = 'vivo y04' in tLower or 'vivo y19s' in tLower
    isVivoHelio = ('vivo y' in tLower and 'y36' not in tLower and 'y35' not in tLower and not isVivoUnisoc)
    
    isOscalHelio = 'oscal tiger' in tLower
    
    isInfinixDimensity = 'infinix gt' in tLower
    isInfinixHot50_60_5G = ('hot 50' in tLower or 'hot 60' in tLower) and '5g' in tLower
    isInfinixHot50_60_4G = ('hot 50' in tLower or 'hot 60' in tLower) and '5g' not in tLower
    
    isInfinixHot_i_Unisoc = 'hot 40i' in tLower or 'hot 30i' in tLower or 'hot 20i' in tLower
    isTecnoPova = 'tecno pova' in tLower
    isTecnoSparkGo2023 = 'spark go 2023' in tLower
    isTecnoSparkGo_Unisoc = 'spark go' in tLower and not isTecnoSparkGo2023
    isTecnoSpark10C = 'spark 10c' in tLower
    isTecnoSparkHelio = ('spark 20' in tLower or 'spark 30' in tLower or 'spark 10' in tLower) and not isTecnoSparkGo_Unisoc and not isTecnoSpark10C

    isSamsungMediaTekModel = 'galaxy a05' in tLower or 'galaxy a15' in tLower or 'galaxy a24' in tLower or 'galaxy a34' in tLower or 'galaxy a04' in tLower or 'galaxy a06' in tLower or 'galaxy a07' in tLower or 'galaxy m' in tLower
    isSamsungUnisocModel = 'galaxy a03' in tLower
    isSamsungExynosModel = 'galaxy a16' in tLower or 'galaxy a25' in tLower or 'galaxy a35' in tLower or 'galaxy a55' in tLower or 'galaxy s' in tLower
    
    isUnisocGeneric = 'realme note 50' in tLower or 'realme note 60' in tLower or 'smart 10' in tLower
    
    isSamsungGeneric = (('galaxy' in tLower and ('a16' in tLower or 'a26' in tLower or 'a36' in tLower or 'a56' in tLower or 's25' in tLower)) or 'galaxy a' in tLower or 'galaxy s' in tLower or 'smartphone samsung' in tLower) and 'snapdragon' not in tLower and 'helio' not in tLower and 'dimensity' not in tLower and 'mediatek' not in tLower and 'octa core' not in tLower and not isSamsungMediaTekModel and not isSamsungUnisocModel
    
    isItelFallback = 'itel a' in tLower or 'itel p' in tLower or 'itel s' in tLower
    
    isInfinixSmart_Unisoc = 'infinix smart 10' in tLower or 'infinix smart 8' in tLower
    isInfinixSmart_Helio = 'infinix smart 9' in tLower
    isInfinixFallback = 'infinix smart' in tLower and not isInfinixSmart_Unisoc and not isInfinixSmart_Helio
    
    isLesiaUnisoc = 'lesia' in tLower or 'clever' in tLower or 'evertek' in tLower or 'iku' in tLower

    isQuadCore = 'quad core' in fullText or 'quad-core' in fullText or '4 core' in fullText or 'itel a33' in tLower or 'itel a17' in tLower or 'itel a16' in tLower or 'itel a37' in tLower or 'itel a14' in tLower or 'itel a58' in tLower or 'lesia young 1' in tLower or 'logicom lyra' in tLower or 'evertek' in tLower or 'nokia c1 ' in tLower or 'nokia c10' in tLower or 'nokia c2 ' in tLower

    # LOGIC APPLICATION
    manualOverride = False
    
    if 'iphone' in tLower and cpu != "Apple A-Series":
        cpu = "Apple A-Series"
        manualOverride = True

    if isQuadCore and cpu != "Quad Core":
        cpu = "Quad Core"
        manualOverride = True

    if cpu != "Quad Core":
        if isHonorHelio: cpu = "MediaTek Helio"; manualOverride = True
        if isHonorSnapdragon: cpu = "Snapdragon"; manualOverride = True
        if isItelHelio: cpu = "MediaTek Helio"; manualOverride = True
        
        if isRealmeHelio: cpu = "MediaTek Helio"; manualOverride = True
        elif isRealmeUnisoc: cpu = "Unisoc"; manualOverride = True
        
        if isRedmiHelio: cpu = "MediaTek Helio"; manualOverride = True
        if isVivoHelio: cpu = "MediaTek Helio"; manualOverride = True
        elif isVivoUnisoc: cpu = "Unisoc"; manualOverride = True
        
        if isOscalHelio: cpu = "MediaTek Series"; manualOverride = True
        if isInfinixDimensity: cpu = "MediaTek Series"; manualOverride = True
        if isInfinixHot50_60_5G: cpu = "MediaTek Series"; manualOverride = True
        elif isInfinixHot50_60_4G: cpu = "MediaTek Series"; manualOverride = True
        if isInfinixHot_i_Unisoc: cpu = "Unisoc"; manualOverride = True
        if isInfinixSmart_Unisoc: cpu = "Unisoc"; manualOverride = True
        if isInfinixSmart_Helio: cpu = "MediaTek Series"; manualOverride = True
        if isTecnoPova: cpu = "MediaTek Series"; manualOverride = True
        if isTecnoSparkGo_Unisoc: cpu = "Unisoc"; manualOverride = True
        elif isTecnoSparkGo2023: cpu = "MediaTek Series"; manualOverride = True
        elif isTecnoSpark10C: cpu = "Unisoc"; manualOverride = True
        elif isTecnoSparkHelio: cpu = "MediaTek Series"; manualOverride = True
        
        if isRedmiUnisoc: cpu = "Unisoc"; manualOverride = True
        if isSamsungMediaTekModel: cpu = "MediaTek Series"; manualOverride = True
        elif isSamsungUnisocModel: cpu = "Unisoc"; manualOverride = True
        if ('redmi a1' in tLower or 'redmi a2' in tLower or 'spark go 2023' in tLower): cpu = "MediaTek Series"; manualOverride = True
        if isUnisocGeneric and 'smart 9' not in tLower: cpu = "Unisoc"; manualOverride = True

        # RECOVERY BLOCK
        if cpu in ["Unknown", "Others", "Octa Core", "Quad Core", None]:
            if isSamsungZSeries: cpu = "Snapdragon"
            elif isSamsungExynosModel: cpu = "Samsung Exynos"
            elif isSamsungMediaTekModel: cpu = "MediaTek Series"
            elif 'redmi a5' in tLower: cpu = "Unisoc"
            elif 'redmi 15c' in tLower or 'redmi 14c' in tLower or 'redmi 13c' in tLower: cpu = "MediaTek Series"
            elif 'redmi 15' in tLower or 'redmi 14' in tLower: cpu = "MediaTek Series"
            elif 'redmi 13' in tLower and 'note' not in tLower: cpu = "MediaTek Series"
            elif 'redmi 12' in tLower and 'note' not in tLower and 'c' not in tLower: cpu = "MediaTek Series"
            elif 'redmi 10' in tLower and 'note' not in tLower and 'c' not in tLower: cpu = "MediaTek Series"
            elif 'redmi note 14' in tLower and '5g' in tLower: cpu = "MediaTek Series"
            elif 'redmi note 14s' in tLower: cpu = "MediaTek Series"
            elif 'redmi note 14' in tLower: cpu = "Snapdragon"
            elif 'xiaomi 14t' in tLower: cpu = "MediaTek Series"
            elif 'xiaomi 12' in tLower or 'xiaomi 13' in tLower or 'xiaomi 14' in tLower: cpu = "Snapdragon"
            elif '11t pro' in tLower: cpu = "Snapdragon"
            elif '11t' in tLower: cpu = "MediaTek Series"
            elif 'note 13 pro+' in tLower: cpu = "MediaTek Series"
            elif 'note 13 pro' in tLower and ('4g' in tLower or '5g' not in tLower): cpu = "MediaTek Series"
            elif 'note 13' in tLower and 'pro' not in tLower and 'plus' not in tLower: cpu = "Snapdragon"
            elif 'poco f' in tLower: cpu = "Snapdragon"
            elif 'poco x3' in tLower: cpu = "Snapdragon"
            elif 'poco m4' in tLower or 'poco m6' in tLower: cpu = "MediaTek Series"
            elif 'nord n10' in tLower: cpu = "Snapdragon"
            elif isOnePlusNordMTK: cpu = "MediaTek Series"
            elif 'oneplus' in tLower: cpu = "Snapdragon"
            elif 'nova y60' in tLower: cpu = "MediaTek Series"
            elif 'nova y70' in tLower: cpu = "Octa Core"
            elif isHuaweiSnapdragon: cpu = "Snapdragon"
            elif 'vivo v23' in tLower: cpu = "MediaTek Series"
            elif 'smart 9' in tLower: cpu = "MediaTek Series"
            elif 'smart 10' in tLower: cpu = "Unisoc"
            elif 'hot 40' in tLower or 'hot 20' in tLower: cpu = "MediaTek Series"
            elif 'spark go 2025' in tLower or 'spark go 1' in tLower or 'hot 60i' in tLower: cpu = "Unisoc"
            elif 'spark 30c' in tLower or 'spark 40c' in tLower or 'pova 6' in tLower or 'hot 60' in tLower or 'hot 50 pro' in tLower or 'note 50s' in tLower: cpu = "MediaTek Series"
            elif 'infinix note 40' in tLower or 'infinix note 30' in tLower: cpu = "MediaTek Series"
            elif 'itel s' in tLower or 'itel p' in tLower or 'itel a60' in tLower or 'itel a70' in tLower: cpu = "Unisoc"
            elif 'nokia g21' in tLower: cpu = "Unisoc"
            elif 'logicom' in tLower or 'iku' in tLower or 'tcl 503' in tLower: cpu = "Unisoc"
            elif 'doogee' in tLower: cpu = "MediaTek Series"
            elif 'lesia' in tLower or 'zte' in tLower or 'oscal flat' in tLower: cpu = "Unisoc"
            elif 'honor play' in tLower: cpu = "MediaTek Series"
            elif 'honor x5' in tLower or 'honor x6' in tLower or 'honor x7a' in tLower or 'honor x7b' in tLower: cpu = "MediaTek Series"
            elif 'honor x7' in tLower or 'honor x8' in tLower or 'honor x9' in tLower: cpu = "Snapdragon"
            elif 'tcl 403' in tLower: cpu = "MediaTek Series"
            elif 'oppo a60' in tLower or 'oppo a3 ' in tLower or 'a76' in tLower: cpu = "Snapdragon"
            elif 'oppo a3x' in tLower: cpu = "Snapdragon"
            elif 'oppo a6 pro' in tLower: cpu = "Octa Core"
            elif 'find x' in tLower: cpu = "Snapdragon"
            elif 'oppo a5x' in tLower or 'oppo a6x' in tLower or 'reno' in tLower: cpu = "MediaTek Series"
            elif 'oppo a5' in tLower: cpu = "Snapdragon"
            elif 'vivo y04' in tLower or 'y21' in tLower: cpu = "MediaTek Series"
            elif 'vivo y35' in tLower: cpu = "Snapdragon"
            elif 'vivo y19s' in tLower: cpu = "Unisoc"
            elif 'vivo v23' in tLower: cpu = "MediaTek Series"
            elif 'v40 lite' in tLower or 'v30 lite' in tLower or 'v50' in tLower or 'v40' in tLower or 'vivo v30' in tLower: cpu = "Snapdragon"
            elif 'realme 7i' in tLower: cpu = "Snapdragon"
            elif 'realme 9i' in tLower: cpu = "Snapdragon"
            elif 'realme c67' in tLower: cpu = "Snapdragon"
            elif 'realme 8' in tLower: cpu = "MediaTek Series"
            elif 'realme c61' in tLower: cpu = "Unisoc"
            elif 'realme c75' in tLower: cpu = "MediaTek Series"
            elif 'realme c33' in tLower or 'realme c51' in tLower: cpu = "Unisoc"
            
            # --- FINAL SCRUB (Matching MobilesPage.jsx) ---
            if cpu in ["Unknown", "Others", "Octa Core", "Quad Core", "N/A", None]:
                if 'itel s24' in tLower: cpu = "MediaTek Series"
                elif 'itel a' in tLower: cpu = "Unisoc"
                elif 'itel p' in tLower: cpu = "Unisoc"
                elif 'spark 8c' in tLower: cpu = "Unisoc"
                elif 'spark 8p' in tLower: cpu = "MediaTek Series"
                elif 'smart 7 hd' in tLower: cpu = "Unisoc"
                elif 'smart 8' in tLower: cpu = "Unisoc"
                elif 'hmd barbie' in tLower: cpu = "Unisoc"
                 
                elif 'itel s' in tLower: cpu = "Unisoc" # Catch remaining Itel S
                elif 'spark go' in tLower: cpu = "Unisoc"
                elif 'spark 10' in tLower: cpu = "MediaTek Series"
                elif 'smart 7' in tLower or 'smart 6' in tLower or 'smart hd' in tLower: cpu = "Unisoc"
                elif 'smart 5' in tLower: cpu = "Unisoc"
                elif 'hot 30' in tLower or 'hot 40' in tLower or 'hot 12' in tLower or 'hot 11' in tLower: cpu = "MediaTek Series"
                elif 'hot50' in tLower or 'hot 50' in tLower: cpu = "MediaTek Series"
                elif 'hmd' in tLower: cpu = "Unisoc" 
                 
                elif 'smartec' in tLower or ' lp ' in tLower or 'figi' in tLower or 'clever' in tLower or 'oale' in tLower or 'iplus' in tLower: cpu = "Unisoc"
                elif 'evertek' in tLower or 'logicom' in tLower or 'iku' in tLower: cpu = "Unisoc"
                 
                elif 'galaxy a16' in tLower or 'galaxy a25' in tLower or 'galaxy a26' in tLower or 'galaxy a36' in tLower or 'galaxy a56' in tLower: cpu = "Samsung Exynos"
                elif 'galaxy s25' in tLower: cpu = "Samsung Exynos"
                 
                elif 'vivo v29' in tLower: cpu = "Snapdragon"
                elif 'oppo a18' in tLower or 'oppo a38' in tLower or 'oppo a58' in tLower: cpu = "MediaTek Series"
                elif 'oppo a77s' in tLower or 'oppo a60' in tLower: cpu = "Snapdragon"
                elif 'oppo a6 pro' in tLower: cpu = "MediaTek Series"
                elif 'one plus' in tLower or 'oneplus' in tLower or 'nord10' in tLower or 'nord n10' in tLower: cpu = "Snapdragon"
                 
                elif 'note 14' in tLower and '5g' in tLower: cpu = "MediaTek Series"
                elif 'note 14' in tLower: cpu = "Snapdragon"
                elif 'note 12 pro' in tLower and '4g' in tLower: cpu = "Snapdragon"
                elif 'redmi 12' in tLower and 'pro' not in tLower: cpu = "MediaTek Series"
                elif 'note 13 pro' in tLower: cpu = "MediaTek Series"
                 
                elif 'nokia c' in tLower: cpu = "Unisoc"
                elif 'realme c25' in tLower or 'realme c11' in tLower or 'realme c21' in tLower: cpu = "Unisoc"
                elif 'realme c30' in tLower or 'realme c33' in tLower: cpu = "Unisoc"
                 
                elif 'tcl' in tLower: cpu = "MediaTek Series"
                elif 'lenovo' in tLower: cpu = "Unisoc"

        isMediaTekDetected = cpu in ["MediaTek Series", "MediaTek Helio", "MediaTek Dimensity"]
        isOctaCoreDetected = cpu == "Octa Core"
        if isSamsungGeneric and cpu != "Samsung Exynos" and not isMediaTekDetected and not isOctaCoreDetected:
            cpu = "Samsung Exynos"
            manualOverride = True
        
        if isItelFallback and cpu != "Octa Core" and cpu != "Unisoc": cpu = "Octa Core"; manualOverride = True
        if isInfinixFallback and cpu != "Octa Core" and cpu != "Unisoc": cpu = "Octa Core"; manualOverride = True

    # Generic Inference from Text
    if not manualOverride and (not cpu or cpu in ["Unknown", "N/A", "Others", "Octa Core", "Quad Core"]):
        if 'helio' in fullText or 'hélio' in fullText or 'g99' in fullText or 'g88' in fullText or 'g85' in fullText or 'g96' in fullText or 'g37' in fullText or 'g36' in fullText: cpu = "MediaTek Series"
        elif 'snapdragon' in fullText or 'qualcomm' in fullText: cpu = "Snapdragon"
        elif 'dimensity' in fullText: cpu = "MediaTek Series"
        elif 'exynos' in fullText: cpu = "Samsung Exynos"
        elif 'unisoc' in fullText or 'tiger' in fullText: cpu = "Unisoc"
        elif 'tensor' in fullText: cpu = "Google Tensor"
        elif 'kirin' in fullText: cpu = "HiSilicon Kirin"
        elif 'bionic' in fullText: cpu = "Apple A-Series"
        elif 'octa core' in fullText: cpu = "Octa Core"
        elif 'quad core' in fullText: cpu = "Quad Core"
    
            
    # Final Normalize
    if not cpu: cpu = "Others"
    if cpu in ["Unknown", "Octa Core"]: cpu = "Others" # User wants "Others" list, treating Octa Core as Others for now to see what they are? No, User said "Others" count is 114.
    
    # Actually User said "Others". In Filters, we usually map "Others" to "Others" or "Unknown".
    # If the user sees "Others" in the filter list, it likely comes from `filters.cpu.others`.
    # Let's see what maps to "Others".
    
    # In `MobilesPage.jsx`, cleanData.map(p => p.specs.cpu || 'Unknown') used for set.
    # Logic:
    # if (!specs.cpu) specs.cpu = "Others";
    
    return cpu, t

def main():
    products = load_data()
    others = []
    
    print(f"Total Products loaded: {len(products)}")
    
    for p in products:
        category = (p.get('category') or '').lower()
        title = (p.get('title') or '').lower()
        
        # Exact Filter match from MobilesPage
        is_mobile = (
            category == 'smartphone' or 
            category == 'tablet' or 
            category == 'feature phone' or 
            category == 'mobile' or 
            'smartphone' in title or 
            'tablette' in title or 
            'iphone' in title or 
            'galaxy s' in title or
            (str(p.get('id')).find('MK-MOB') != -1 or str(p.get('id')).find('mytek-mob') != -1)
        )
        
        if not is_mobile:
            continue
            
        final_cpu, t = classify(p)
        
        # User said "Others".
        # If final_cpu is null, Unknown, or Others.
        if final_cpu in ["Others", "Unknown", None, ""]:
            others.append(f"[{p.get('source')}] {p['title']}")
    
    print(f"Found {len(others)} items in 'Others' category:")
    for o in others:
        print(o)

if __name__ == "__main__":
    main()
