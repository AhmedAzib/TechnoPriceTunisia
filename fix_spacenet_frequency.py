import json

FILE_PATH = r"C:\Users\USER\Documents\programmation\frontend\src\data\spacenet_processors.json"

FREQUENCY_MAPPING = {
    # Legacy
    "E2140": "1.60 GHz",
    "Q8300": "2.50 GHz",
    "i5-650": "3.46 GHz", # Max Turbo
    "i3-4160": "3.60 GHz",
    "i3-4170": "3.70 GHz",
    "i5-4460": "3.40 GHz", # Max Turbo (Base 3.2)
    "i3-7100": "3.90 GHz",
    
    # Modern Intel
    "G6400": "4.00 GHz",
    "10105": "4.40 GHz", # Max Turbo
    "10400": "4.30 GHz", # Max Turbo
    "11400": "4.40 GHz", # Max Turbo (F included)
    "11500": "4.60 GHz", # Max Turbo
    "11900": "5.20 GHz", # Max Turbo (F included)
    
    "12100": "4.30 GHz", # Max Turbo
    "12400": "4.40 GHz", # Max Turbo (F included)
    "12600K": "4.90 GHz", # Max Turbo (P-core)
    "12700K": "5.00 GHz", # Max Turbo (P-core) (KF included)
    
    "13100": "4.50 GHz",
    "13400": "4.60 GHz",
    "13400F": "4.60 GHz",
    "13700F": "5.20 GHz",
    "13700K": "5.40 GHz",
    
    "14100": "4.70 GHz",
    "14400": "4.70 GHz",
    "14600": "5.30 GHz",
    "14700": "5.40 GHz", # Max Turbo
    "14700K": "5.60 GHz",
    "14900K": "6.00 GHz", # Thermal Velocity Boost (KF included)
    
    "Ultra 5 225F": "4.90 GHz", # Using site value as placeholder/closest match for this strange SKU
    "Ultra 7 265K": "5.50 GHz",
    
    # AMD
    "3100": "3.90 GHz", # Max Boost
    "3500X": "4.10 GHz",
    "3600": "4.20 GHz", # Max Boost
    "4500": "4.10 GHz", # Max Boost
    "5500": "4.20 GHz", # Max Boost
    "5600": "4.40 GHz",
    "5600X": "4.60 GHz",
    "5600G": "4.40 GHz",
    "5700X": "4.60 GHz",
    "5800X": "4.70 GHz",
    "5950X": "4.90 GHz",
    "7500F": "5.00 GHz",
    "7600": "5.10 GHz",
    "7700": "5.30 GHz",
    "7950X": "5.70 GHz",
    "8500G": "5.00 GHz",
    "8600G": "5.00 GHz",
    "8700G": "5.10 GHz"
}

def get_freq(title, reference):
    title_upper = title.upper()
    
    # Direct Matches based on Ref keys
    
    # Intel 14th
    if "14900" in title_upper: return FREQUENCY_MAPPING["14900K"]
    if "14700K" in title_upper: return FREQUENCY_MAPPING["14700K"]
    if "14700" in title_upper: return FREQUENCY_MAPPING["14700"]
    if "14400" in title_upper: return FREQUENCY_MAPPING["14400"]
    if "14100" in title_upper: return FREQUENCY_MAPPING["14100"]
    
    # Intel 13th
    if "13700K" in title_upper: return FREQUENCY_MAPPING["13700K"]
    if "13700F" in title_upper or "13700 " in title_upper: return FREQUENCY_MAPPING["13700F"]
    if "13400" in title_upper: return FREQUENCY_MAPPING["13400"]
    
    # Intel 12th
    if "12700K" in title_upper or "12700F" in title_upper: 
        if "12700 " in title_upper and "K" not in title_upper and "F" not in title_upper: return "4.90 GHz" # 12700 Non-K
        return FREQUENCY_MAPPING["12700K"] # K/KF 5.0
    if "12600K" in title_upper: return FREQUENCY_MAPPING["12600K"]
    if "12400" in title_upper: return FREQUENCY_MAPPING["12400"]
    if "12100" in title_upper: return FREQUENCY_MAPPING["12100"]
    
    # Intel 11th/10th
    if "11900" in title_upper: return FREQUENCY_MAPPING["11900"]
    if "11500" in title_upper: return FREQUENCY_MAPPING["11500"]
    if "11400" in title_upper: return FREQUENCY_MAPPING["11400"]
    if "10105" in title_upper: return FREQUENCY_MAPPING["10105"]
    
    # Legacy
    if "G6400" in title_upper: return FREQUENCY_MAPPING["G6400"]
    if "Q8300" in title_upper: return FREQUENCY_MAPPING["Q8300"]
    if "E2140" in title_upper: return FREQUENCY_MAPPING["E2140"]
    if "I3-4160" in title_upper: return FREQUENCY_MAPPING["i3-4160"]
    if "I3-4170" in title_upper: return FREQUENCY_MAPPING["i3-4170"]
    if "I3-7100" in title_upper: return FREQUENCY_MAPPING["i3-7100"]
    if "I5-650" in title_upper: return FREQUENCY_MAPPING["i5-650"]
    
    # Ultra
    if "225F" in title_upper: return FREQUENCY_MAPPING["Ultra 5 225F"]
    if "265K" in title_upper: return FREQUENCY_MAPPING["Ultra 7 265K"]
    
    # AMD
    if "3100" in title_upper: return FREQUENCY_MAPPING["3100"]
    if "3500X" in title_upper: return FREQUENCY_MAPPING["3500X"]
    if "3600" in title_upper: return FREQUENCY_MAPPING["3600"]
    if "4500" in title_upper: return FREQUENCY_MAPPING["4500"]
    
    return "Unknown"

def main():
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        updated_count = 0
        
        for item in data:
            freq = get_freq(item['title'], item['reference'])
            
            # Fallback checks?
            # Fallback checks?
            if freq != "Unknown":
                item['specs']['clock_speed'] = freq
                updated_count += 1
            else:
                pass
        
        print(f"Updated {updated_count}/{len(data)} items with Frequency.")
        
        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
