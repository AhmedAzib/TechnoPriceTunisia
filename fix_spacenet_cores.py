import json
import re

FILE_PATH = r"C:\Users\USER\Documents\programmation\frontend\src\data\spacenet_processors.json"

# Detailed Mapping based on user's list and standard specs
# Format: "Distinctive Reference/Substring": "X Cores"
CORE_MAPPING = {
    # Intel Legacy
    "E2140": "2 Cores",
    "Q8300": "4 Cores",
    "i5-650": "2 Cores",
    "i3-4160": "2 Cores",
    "i3-4170": "2 Cores",
    "i5-4460": "4 Cores",
    "i3-7100": "2 Cores",
    
    # Intel Modern (10th/11th)
    "G6400": "2 Cores",
    "i3-10105": "4 Cores",
    "i5-10400": "6 Cores",
    "i5-11400": "6 Cores", # Covers F and non-F
    "i5-11500": "6 Cores",
    "i9-11900": "8 Cores", # Covers F
    
    # Intel 12th/13th/14th/Ultra
    "i3-12100": "4 Cores", # 4P+0E
    "i5-12400": "6 Cores", # 6P+0E
    "i5-12600K": "10 Cores", # 6P+4E (KF too)
    "i7-12700": "12 Cores", # 8P+4E (K/KF/F covers all generally 12)
    
    "i3-14100": "4 Cores", # 4P+0E
    "i5-14400": "10 Cores", # 6P+4E
    "i5-13400": "10 Cores",
    "i5-13500": "14 Cores",
    "i5-13600": "14 Cores",
    "i5-14600": "14 Cores",
    
    "i7-13700": "16 Cores", # 8P+8E (K/KF/F)
    "i7-14700": "20 Cores", # 8P+12E (K/KF/F/Tray)
    
    "i9-13900": "24 Cores",
    "i9-14900": "24 Cores",
    
    "Ultra 5 225": "14 Cores",  # Assuming Ultra 5 125H equivalent or 245K typo? 
                                # Wait, Ultra 5 245K is Arrow Lake (6P+8E = 14).
                                # The listing said "Ultra 5 225F" -> Probably "Ultra 5 245KF" (14 Cores).
                                # User pasted "Ultra 5 225F". Spacenet title likely typo for 245F/K. 
                                # 200 series Arrow Lake. U5 = 14 Cores (6P+8E).
    "Ultra 7 265K": "20 Cores", # 8P+12E
    
    # AMD
    "3100": "4 Cores",
    "3200G": "4 Cores",
    "3400G": "4 Cores",
    "3500X": "6 Cores",
    "3600": "6 Cores", # Covers 3600/X/XT
    "4500": "6 Cores",
    "4600G": "6 Cores",
    "5500": "6 Cores", # Covers 5500/GT
    "5600": "6 Cores", # Covers 5600/G/X
    "5700": "8 Cores", # Covers 5700/X/G
    "5800": "8 Cores", # Covers 5800X/X3D
    "5950X": "16 Cores",
    "7500F": "6 Cores",
    "7600": "6 Cores", # Covers 7600/X
    "7700": "8 Cores", # Covers 7700/X
    "7800X3D": "8 Cores",
    "7900": "12 Cores",
    "7950": "16 Cores",
    "8500G": "6 Cores",
    "8600G": "6 Cores",
    "8700G": "8 Cores",
    "9900X": "12 Cores"
}

def get_cores(title, reference):
    t_upper = title.upper()
    r_upper = reference.upper()
    
    # Priority Matching
    # Check specific models first
    if "14900" in t_upper: return "24 Cores"
    if "13900" in t_upper: return "24 Cores"
    if "14700" in t_upper: return "20 Cores"
    if "13700" in t_upper: return "16 Cores"
    if "12700" in t_upper: return "12 Cores"
    
    if "ULTRA 7" in t_upper: return "20 Cores"
    if "ULTRA 5" in t_upper: return "14 Cores" # Assuming 245K class
    
    if "14600" in t_upper: return "14 Cores"
    if "13600" in t_upper: return "14 Cores"
    
    if "12600" in t_upper: return "10 Cores"
    if "13500" in t_upper: return "14 Cores" # 6P+8E
    
    if "14400" in t_upper: return "10 Cores"
    if "13400" in t_upper: return "10 Cores"
    
    if "12400" in t_upper: return "6 Cores"
    if "11400" in t_upper: return "6 Cores"
    if "10400" in t_upper: return "6 Cores"
    if "11500" in t_upper: return "6 Cores"
    
    if "14100" in t_upper: return "4 Cores"
    if "13100" in t_upper: return "4 Cores"
    if "12100" in t_upper: return "4 Cores"
    if "10105" in t_upper: return "4 Cores"
    if "10100" in t_upper: return "4 Cores"
    
    if "11900" in t_upper: return "8 Cores" # Rocket Lake maxed at 8
    
    if "Q8300" in t_upper: return "4 Cores"
    if "E2140" in t_upper: return "2 Cores"
    if "G6400" in t_upper: return "2 Cores"
    
    if "I3-41" in t_upper: return "2 Cores" # 4160, 4170
    if "I3-7100" in t_upper: return "2 Cores"
    if "I5-650" in t_upper: return "2 Cores"
    if "I5-4460" in t_upper: return "4 Cores"
    
    # AMD
    if "5950X" in t_upper: return "16 Cores"
    if "7950" in t_upper: return "16 Cores"
    if "9900X" in t_upper: return "12 Cores" # Zen 5 9900X is 12
    if "7900" in t_upper: return "12 Cores"
    if "5900" in t_upper: return "12 Cores"
    
    if "5800" in t_upper: return "8 Cores"
    if "5700" in t_upper: return "8 Cores"
    if "7700" in t_upper: return "8 Cores"
    if "7800" in t_upper: return "8 Cores"
    if "8700" in t_upper: return "8 Cores"
    
    if "5600" in t_upper: return "6 Cores" # Covers G/X/GT
    if "5500" in t_upper: return "6 Cores" 
    if "4600" in t_upper: return "6 Cores"
    if "4500" in t_upper: return "6 Cores"
    if "3600" in t_upper: return "6 Cores"
    if "3500" in t_upper: return "6 Cores" 
    if "7600" in t_upper: return "6 Cores"
    if "7500" in t_upper: return "6 Cores"
    if "8600" in t_upper: return "6 Cores"
    if "8500" in t_upper: return "6 Cores" # 2+4
    if "8400" in t_upper: return "6 Cores"
    
    if "3400G" in t_upper: return "4 Cores"
    if "3200G" in t_upper: return "4 Cores"
    if "3100" in t_upper: return "4 Cores"
    if "1200" in t_upper: return "4 Cores" # Ryzen 3 1200
    
    return "Unknown"

def main():
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        updated_count = 0
        
        for item in data:
            old_cores = item.get('specs', {}).get('cores', 'Unknown')
            new_cores = get_cores(item['title'], item['reference'])
            
            if new_cores != "Unknown":
                item['specs']['cores'] = new_cores
                updated_count += 1
                # print(f"Updated {item['title'][:40]}... : {old_cores} -> {new_cores}")
            else:
                print(f"WARNING: Could not identify cores for: {item['title']}")
        
        print(f"Updated {updated_count}/{len(data)} items.")
        
        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
