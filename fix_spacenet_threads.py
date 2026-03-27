import json

FILE_PATH = r"C:\Users\USER\Documents\programmation\frontend\src\data\spacenet_processors.json"

THREADS_MAPPING = {
    # Legacy
    "E2140": "2 Threads",
    "Q8300": "4 Threads",
    "i5-650": "4 Threads", # 2C/4T
    "i3-4160": "4 Threads", # 2C/4T
    "i3-4170": "4 Threads", # 2C/4T
    "i5-4460": "4 Threads", # 4C/4T (No HT)
    "i3-7100": "4 Threads", # 2C/4T
    
    # Modern Intel
    "G6400": "4 Threads", # 2C/4T
    "10105": "8 Threads", # 4C/8T
    "10400": "12 Threads", # 6C/12T
    "11400": "12 Threads", # 6C/12T
    "11500": "12 Threads", # 6C/12T
    "11900": "16 Threads", # 8C/16T
    
    "12100": "8 Threads", # 4P/8T
    "12400": "12 Threads", # 6P/12T
    "12600K": "16 Threads", # 6P+4E = 12+4 = 16
    "12700K": "20 Threads", # 8P+4E = 16+4 = 20
    
    "13100": "8 Threads",
    "13400": "16 Threads", # 6P+4E = 16T
    "13700": "24 Threads", # 8P+8E = 16+8 = 24
    
    "14100": "8 Threads", # 4P+0E
    "14400": "16 Threads", # 6P+4E = 12+4 = 16
    "14700": "28 Threads", # 8P+12E = 16+12 = 28
    "14900": "32 Threads", # 8P+16E = 16+16 = 32
    
    # Ultra (Series 2 = No HT)
    "Ultra 5 225F": "14 Threads", # Assuming 245K equivalent (14 Cores) -> 14 Threads
    "Ultra 7 265K": "20 Threads", # 20 Cores -> 20 Threads
    
    # AMD
    "3100": "8 Threads", # 4C/8T
    "3500X": "6 Threads", # 6C/6T (No SMT)
    "3600": "12 Threads", # 6C/12T
    "4500": "12 Threads", # 6C/12T
    "5500": "12 Threads", # 6C/12T
    "5600": "12 Threads", # 6C/12T
    "5700": "16 Threads", # 8C/16T
    "5800": "16 Threads",
    "5900": "24 Threads",
    "5950": "32 Threads",
    
    "7500F": "12 Threads", # 6C/12T
    "7600": "12 Threads",
    "7700": "16 Threads", # 8C/16T
    "7900": "24 Threads",
    "7950": "32 Threads",
    
    "8500G": "12 Threads", # 6C (2+4) -> 12T
    "8600G": "16 Threads", # 8C/16T (Wait, 8600G is 6 cores? No, 8600G is 6 Cores/12 Threads. 8700G is 8C/16T. Correction needed.)
    "8700G": "16 Threads"
}

def get_threads(title, reference):
    title_upper = title.upper()
    
    # Direct Matches based on Ref keys
    
    # 14th Gen
    if "14900" in title_upper: return THREADS_MAPPING["14900"]
    if "14700" in title_upper: return THREADS_MAPPING["14700"]
    if "14400" in title_upper: return THREADS_MAPPING["14400"]
    if "14100" in title_upper: return THREADS_MAPPING["14100"]
    
    # 13th Gen
    if "13700" in title_upper: return THREADS_MAPPING["13700"]
    if "13400" in title_upper: return THREADS_MAPPING["13400"] 
    if "13100" in title_upper: return THREADS_MAPPING["13100"]
    
    # 12th Gen
    if "12700" in title_upper: return THREADS_MAPPING["12700K"] # All 12700 variants have 20T
    if "12600" in title_upper: 
        if "K" in title_upper: return THREADS_MAPPING["12600K"]
        return "12 Threads" # 12600 Non-K is 6C/12T (No E-cores)
    if "12400" in title_upper: return THREADS_MAPPING["12400"]
    if "12100" in title_upper: return THREADS_MAPPING["12100"]
    
    # 11th/10th
    if "11900" in title_upper: return THREADS_MAPPING["11900"]
    if "11500" in title_upper: return THREADS_MAPPING["11500"]
    if "11400" in title_upper: return THREADS_MAPPING["11400"]
    if "10105" in title_upper: return THREADS_MAPPING["10105"]
    if "10100" in title_upper: return THREADS_MAPPING["10105"]
    
    # Legacy
    if "G6400" in title_upper: return THREADS_MAPPING["G6400"]
    if "Q8300" in title_upper: return THREADS_MAPPING["Q8300"]
    if "E2140" in title_upper: return THREADS_MAPPING["E2140"]
    if "I3-4160" in title_upper: return THREADS_MAPPING["i3-4160"]
    if "I3-4170" in title_upper: return THREADS_MAPPING["i3-4170"]
    if "I3-7100" in title_upper: return THREADS_MAPPING["i3-7100"]
    if "I5-650" in title_upper: return THREADS_MAPPING["i5-650"]
    if "I5-4460" in title_upper: return THREADS_MAPPING["i5-4460"]
    
    # Ultra
    if "225F" in title_upper: return THREADS_MAPPING["Ultra 5 225F"]
    if "265K" in title_upper: return THREADS_MAPPING["Ultra 7 265K"]
    
    # AMD
    if "8600G" in title_upper: return "12 Threads" # Correction: 8600G is 6C/12T
    if "8500G" in title_upper: return THREADS_MAPPING["8500G"]
    if "5600" in title_upper: return THREADS_MAPPING["5600"]
    if "5500" in title_upper: return THREADS_MAPPING["5500"]
    if "4500" in title_upper: return THREADS_MAPPING["4500"]
    if "3600" in title_upper: return THREADS_MAPPING["3600"]
    if "3500X" in title_upper: return THREADS_MAPPING["3500X"]
    if "3100" in title_upper: return THREADS_MAPPING["3100"]
    
    if "7600" in title_upper: return THREADS_MAPPING["7600"]
    if "7500F" in title_upper: return THREADS_MAPPING["7500F"]
    
    return "Unknown"

def main():
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        updated_count = 0
        
        for item in data:
            threads = get_threads(item['title'], item['reference'])
            
            if threads != "Unknown":
                # Ensure consistent format
                item['specs']['threads'] = threads
                updated_count += 1
            else:
                pass
                # print(f"Unknown Threads: {item['title']}")
        
        print(f"Updated {updated_count}/{len(data)} items with Threads.")
        
        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
