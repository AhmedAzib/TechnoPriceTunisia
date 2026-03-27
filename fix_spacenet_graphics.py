import json

FILE_PATH = r"C:\Users\USER\Documents\programmation\frontend\src\data\spacenet_processors.json"

GRAPHICS_MAPPING = {
    # Legacy - Chipset based or None
    "E2140": "None (Requires Discrete GPU)",
    "Q8300": "None (Requires Discrete GPU)",
    
    # Legacy - iGPU
    "i5-650": "Intel HD Graphics",
    "i3-4160": "Intel HD Graphics 4400",
    "i3-4170": "Intel HD Graphics 4400",
    "i5-4460": "Intel HD Graphics 4600",
    "i3-7100": "Intel HD Graphics 630",
    
    # Modern Intel - F/KF (No iGPU)
    "11400F": "None (Requires Discrete GPU)",
    "12400F": "None (Requires Discrete GPU)",
    "13400F": "None (Requires Discrete GPU)",
    "13100F": "None (Requires Discrete GPU)",
    "14100F": "None (Requires Discrete GPU)",
    "10400F": "None (Requires Discrete GPU)",
    "11900F": "None (Requires Discrete GPU)",
    "12600KF": "None (Requires Discrete GPU)",
    "12700KF": "None (Requires Discrete GPU)",
    "13700F": "None (Requires Discrete GPU)",
    "13700KF": "None (Requires Discrete GPU)",
    "14700F": "None (Requires Discrete GPU)",
    "14700KF": "None (Requires Discrete GPU)",
    "14900KF": "None (Requires Discrete GPU)",
    "225F": "None (Requires Discrete GPU)", # Ultra 5 225F (likely 245KF)
    "14600KF": "None (Requires Discrete GPU)",
    
    # Modern Intel - iGPU
    "G6400": "Intel UHD Graphics 610",
    "10105": "Intel UHD Graphics 630",
    "12400": "Intel UHD Graphics 730", # Non-F
    "13400": "Intel UHD Graphics 730",
    "14400": "Intel UHD Graphics 730",
    "11500": "Intel UHD Graphics 750",
    "12600K": "Intel UHD Graphics 770", # K has iGPU
    "12700K": "Intel UHD Graphics 770",
    "13700K": "Intel UHD Graphics 770",
    "14700K": "Intel UHD Graphics 770",
    "14900K": "Intel UHD Graphics 770",
    "13700": "Intel UHD Graphics 770",
    "14700": "Intel UHD Graphics 770",
    "12700": "Intel UHD Graphics 770",
    
    "Ultra 7 265K": "Intel Graphics (4 Xe-Cores)",
    "Ultra 5 245K": "Intel Graphics (4 Xe-Cores)", 
    
    # AMD
    "3100": "None (Requires Discrete GPU)",
    "3500X": "None (Requires Discrete GPU)",
    "3600": "None (Requires Discrete GPU)",
    "4500": "None (Requires Discrete GPU)",
    "5500": "None (Requires Discrete GPU)",
    "5600": "None (Requires Discrete GPU)",
    "5700": "None (Requires Discrete GPU)",
    "5800": "None (Requires Discrete GPU)",
    "5900": "None (Requires Discrete GPU)",
    "5950": "None (Requires Discrete GPU)",
    "7500F": "None (Requires Discrete GPU)",
    
    # AMD APUs (G) & 7000/9000 Series (Have Basic iGPU)
    "3200G": "Radeon Vega 8 Graphics",
    "3400G": "Radeon RX Vega 11 Graphics",
    "4600G": "Radeon Graphics (7 Cores)",
    "5600G": "Radeon Graphics (7 Cores)",
    "5700G": "Radeon Graphics (8 Cores)",
    "8500G": "Radeon 740M",
    "8600G": "Radeon 760M",
    "8700G": "Radeon 780M",
    
    "7600": "AMD Radeon Graphics (2 Cores)", # Non-F 7000 series has iGPU
    "7700": "AMD Radeon Graphics (2 Cores)",
    "7900": "AMD Radeon Graphics (2 Cores)",
    "7950": "AMD Radeon Graphics (2 Cores)",
    "9600": "AMD Radeon Graphics (2 Cores)",
    "9700": "AMD Radeon Graphics (2 Cores)",
    "9900": "AMD Radeon Graphics (2 Cores)"
}

def get_graphics(title, reference):
    title_upper = title.upper()
    ref_upper = reference.upper()
    
    # Check strict mapping
    
    # 1. Match F/KF suffix specifically first (Override generic number match)
    if "F" in ref_upper or "F" in title_upper.split() or "KF" in title_upper.split():
        # Double check if it's really an F SKU (e.g. 11400F) using regex?
        # Simple string check "11400F"
        pass 

    # Logic: Search for keys in title. Be careful with substrings (e.g. 650 vs 6500)
    
    # Specific Identifiers
    
    # Intel Unique
    if "E2140" in title_upper: return GRAPHICS_MAPPING["E2140"]
    if "Q8300" in title_upper: return GRAPHICS_MAPPING["Q8300"]
    if "G6400" in title_upper: return GRAPHICS_MAPPING["G6400"]
    
    # Order matters: check longer strings first to avoid partial matches
    
    # 14th Gen
    if "14900KF" in title_upper or "14900F" in title_upper: return GRAPHICS_MAPPING["14900KF"]
    if "14900K" in title_upper or "14900" in title_upper: return GRAPHICS_MAPPING["14900K"]
    
    if "14700KF" in title_upper or "14700F" in title_upper: return GRAPHICS_MAPPING["14700KF"]
    if "14700K" in title_upper: return GRAPHICS_MAPPING["14700K"]
    if "14700" in title_upper: return GRAPHICS_MAPPING["14700"] # Non-K
    
    if "14600KF" in title_upper: return GRAPHICS_MAPPING["14600KF"]
    if "14600K" in title_upper: return "Intel UHD Graphics 770"
    
    if "14400F" in title_upper: return GRAPHICS_MAPPING["14700KF"] # Typo safe? No, 14400F
    if "14400" in title_upper: 
        if "F" in title_upper[title_upper.find("14400"):]: return GRAPHICS_MAPPING["13400F"] # Same class
        return GRAPHICS_MAPPING["14400"]
        
    if "14100F" in title_upper: return GRAPHICS_MAPPING["14100F"]
    
    # 13th Gen
    if "13900" in title_upper: 
        if "F" in title_upper: return GRAPHICS_MAPPING["14900KF"] 
        return GRAPHICS_MAPPING["14900K"]
        
    if "13700" in title_upper:
        if "F" in title_upper: return GRAPHICS_MAPPING["13700F"]
        return GRAPHICS_MAPPING["13700K"]
        
    if "13600" in title_upper:
        if "F" in title_upper: return GRAPHICS_MAPPING["12600KF"]
        return "Intel UHD Graphics 770"
        
    if "13400" in title_upper:
        if "F" in title_upper: return GRAPHICS_MAPPING["13400F"]
        return GRAPHICS_MAPPING["13400"]
        
    if "13100" in title_upper:
        if "F" in title_upper: return GRAPHICS_MAPPING["13100F"]
        return "Intel UHD Graphics 730"

    # 12th Gen
    if "12900" in title_upper: return "Intel UHD Graphics 770"
    if "12700" in title_upper:
        if "F" in title_upper: return GRAPHICS_MAPPING["12700KF"]
        return GRAPHICS_MAPPING["12700K"]
    if "12600" in title_upper:
        if "F" in title_upper: return GRAPHICS_MAPPING["12600KF"]
        return GRAPHICS_MAPPING["12600K"]
    if "12400" in title_upper:
        if "F" in title_upper: return GRAPHICS_MAPPING["12400F"]
        return GRAPHICS_MAPPING["12400"]
        
    if "12100" in title_upper:
        if "F" in title_upper: return GRAPHICS_MAPPING["13100F"]
        return "Intel UHD Graphics 730"

    # 11th Gen
    if "11900" in title_upper:
        if "F" in title_upper: return GRAPHICS_MAPPING["11900F"]
        return "Intel UHD Graphics 750"
    if "11500" in title_upper: return GRAPHICS_MAPPING["11500"]
    if "11400" in title_upper:
        if "F" in title_upper: return GRAPHICS_MAPPING["11400F"]
        return GRAPHICS_MAPPING["11500"] # 11400 also UHD 730 actually. 11500 is 750. 
        # Fix: 11400 is UHD 730. 
        
    # 10th Gen
    if "10900" in title_upper:
        if "F" in title_upper: return GRAPHICS_MAPPING["10400F"]
        return GRAPHICS_MAPPING["10105"] # UHD 630
    if "10700" in title_upper:
        if "F" in title_upper: return GRAPHICS_MAPPING["10400F"]
        return GRAPHICS_MAPPING["10105"] # UHD 630
    if "10400" in title_upper:
        if "F" in title_upper: return GRAPHICS_MAPPING["10400F"]
        return GRAPHICS_MAPPING["10105"] # UHD 630
    if "10105" in title_upper: return GRAPHICS_MAPPING["10105"]
    if "10100" in title_upper: 
        if "F" in title_upper: return GRAPHICS_MAPPING["10400F"]
        return GRAPHICS_MAPPING["10105"]

    # Older
    if "I3-41" in title_upper: return GRAPHICS_MAPPING["i3-4160"]
    if "I3-7100" in title_upper: return GRAPHICS_MAPPING["i3-7100"]
    if "I5-4460" in title_upper: return GRAPHICS_MAPPING["i5-4460"]
    if "I5-650" in title_upper: return GRAPHICS_MAPPING["i5-650"]
    
    # Ultra
    if "ULTRA 7" in title_upper: return GRAPHICS_MAPPING["Ultra 7 265K"]
    if "ULTRA 5" in title_upper: 
        if "225F" in title_upper or "245KF" in title_upper or "F" in title_upper: return GRAPHICS_MAPPING["225F"]
        return "Intel Graphics (4 Xe-Cores)"

    # AMD
    if "8600G" in title_upper: return GRAPHICS_MAPPING["8600G"]
    if "8500G" in title_upper: return GRAPHICS_MAPPING["8500G"]
    if "5600G" in title_upper: return GRAPHICS_MAPPING["5600G"]
    if "4600G" in title_upper: return GRAPHICS_MAPPING["4600G"]
    if "3400G" in title_upper: return GRAPHICS_MAPPING["3400G"]
    if "3200G" in title_upper: return GRAPHICS_MAPPING["3200G"]
    
    if "3100" in title_upper: return GRAPHICS_MAPPING["3100"]
    if "3500X" in title_upper: return GRAPHICS_MAPPING["3500X"]
    if "3600" in title_upper: return GRAPHICS_MAPPING["3600"]
    if "4500" in title_upper: return GRAPHICS_MAPPING["4500"]
    if "5500" in title_upper: return GRAPHICS_MAPPING["5500"]
    if "5600" in title_upper: return GRAPHICS_MAPPING["5600"]
    if "5700" in title_upper: return GRAPHICS_MAPPING["5700"]
    if "5800" in title_upper: return GRAPHICS_MAPPING["5800"]
    if "5900" in title_upper: return GRAPHICS_MAPPING["5900"]
    
    # Ryzen 7000/9000 (Non-F = Has Graphics)
    if "7600" in title_upper or "7700" in title_upper or "7900" in title_upper or "7950" in title_upper:
        if "F" in title_upper: return GRAPHICS_MAPPING["7500F"]
        return GRAPHICS_MAPPING["7600"] # 2 Cores
        
    return "Unknown" # Fallback

def main():
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        updated_count = 0
        
        for item in data:
            old_gpu = item.get('specs', {}).get('graphics', 'Unknown')
            new_gpu = get_graphics(item['title'], item['reference'])
            
            # Special case for "11400" non-F which uses 730 not 750
            if "11400" in item['title'] and "F" not in item['title']:
                new_gpu = "Intel UHD Graphics 730"

            item['specs']['graphics'] = new_gpu
            updated_count += 1
            # print(f"GPU: {item['title'][:30]}... -> {new_gpu}")
        
        print(f"Updated {updated_count}/{len(data)} items with graphics info.")
        
        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
