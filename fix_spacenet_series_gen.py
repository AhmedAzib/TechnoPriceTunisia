import json

FILE_PATH = r"C:\Users\USER\Documents\programmation\frontend\src\data\spacenet_processors.json"

def get_series_gen(title, reference):
    t_upper = title.upper()
    r_upper = reference.upper()
    
    series = "Unknown"
    gen = "Unknown"
    
    # Normalize title to handle encoding weirdness (e.g. RYZEN)
    t_clean = t_upper.replace("", "").replace("™", "").replace("®", "")
    
    # --- INTEL ---
    if "INTEL" in t_clean:
        # PENTIUM
        if "PENTIUM" in t_clean:
            series = "Pentium"
            if "E2140" in t_clean: gen = "Dual-Core (Legacy)"
            elif "G6400" in t_clean: gen = "Gold Series (10th Gen)"
            else: gen = "Legacy"
            
        # CORE 2 QUAD
        elif "CORE 2 QUAD" in t_clean:
            series = "Core 2 Quad"
            gen = "Legacy"
        
        # CORE iX
        elif "CORE I" in t_clean or "I3-" in t_clean or "I5-" in t_clean or "I7-" in t_clean or "I9-" in t_clean:
            # Series
            if "I3" in t_clean: series = "Core i3"
            elif "I5" in t_clean: series = "Core i5"
            elif "I7" in t_clean: series = "Core i7"
            elif "I9" in t_clean: series = "Core i9"
            
            # Generation
            # Check 14th
            if "14900" in t_clean or "14700" in t_clean or "14600" in t_clean or "14400" in t_clean or "14100" in t_clean:
                gen = "14th Gen"
            # Check 13th
            elif "13900" in t_clean or "13700" in t_clean or "13600" in t_clean or "13500" in t_clean or "13400" in t_clean or "13100" in t_clean:
                gen = "13th Gen"
            # Check 12th
            elif "12900" in t_clean or "12700" in t_clean or "12600" in t_clean or "12400" in t_clean or "12100" in t_clean:
                gen = "12th Gen"
            # Check 11th
            elif "11900" in t_clean or "11700" in t_clean or "11600" in t_clean or "11500" in t_clean or "11400" in t_clean:
                gen = "11th Gen"
            # Check 10th
            elif "10900" in t_clean or "10700" in t_clean or "10600" in t_clean or "10400" in t_clean or "10100" in t_clean or "10105" in t_clean:
                gen = "10th Gen"
            # Check 7th
            elif "7100" in t_clean:
                gen = "7th Gen"
            # Check 4th
            elif "4690" in t_clean or "4790" in t_clean or "4460" in t_clean or "4170" in t_clean or "4160" in t_clean:
                gen = "4th Gen"
            # Check 1st Gen (3 digits)
            elif "I5-650" in t_clean:
                gen = "1st Gen (Legacy)"
                
        # ULTRA
        elif "ULTRA" in t_clean:
            if "ULTRA 7" in t_clean: series = "Core Ultra 7"
            if "ULTRA 5" in t_clean: series = "Core Ultra 5"
            if "ULTRA 9" in t_clean: series = "Core Ultra 9"
            
            if "265K" in t_clean or "225F" in t_clean or "245" in t_clean:
                gen = "Series 2"
            else:
                gen = "Series 1"

    # --- AMD ---
    elif "AMD" in t_clean or "RYZEN" in t_clean:
        # RYZEN
        if "RYZEN" in t_clean:
            # Series
            if "RYZEN 9" in t_clean: series = "Ryzen 9"
            elif "RYZEN 7" in t_clean: series = "Ryzen 7"
            elif "RYZEN 5" in t_clean: series = "Ryzen 5"
            elif "RYZEN 3" in t_clean: series = "Ryzen 3"
            
            # Generation
            # 9000
            if "9950" in t_clean or "9900" in t_clean or "9700" in t_clean or "9600" in t_clean:
                gen = "Ryzen 9000"
            # 8000
            elif "8700" in t_clean or "8600" in t_clean or "8500" in t_clean or "8400" in t_clean:
                gen = "Ryzen 8000"
            # 7000
            elif "7950" in t_clean or "7900" in t_clean or "7700" in t_clean or "7600" in t_clean or "7500" in t_clean:
                gen = "Ryzen 7000"
            # 5000
            elif "5950" in t_clean or "5900" in t_clean or "5800" in t_clean or "5700" in t_clean or "5600" in t_clean or "5500" in t_clean:
                gen = "Ryzen 5000"
            # 4000
            elif "4700" in t_clean or "4600" in t_clean or "4500" in t_clean or "4300" in t_clean:
                gen = "Ryzen 4000"
            # 3000
            elif "3950" in t_clean or "3900" in t_clean or "3800" in t_clean or "3700" in t_clean or "3600" in t_clean or "3500" in t_clean or "3400" in t_clean or "3300" in t_clean or "3200" in t_clean or "3100" in t_clean:
                gen = "Ryzen 3000"
            # 1000
            elif "1200" in t_clean:
                gen = "Ryzen 1000"

    return series, gen

def main():
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        updated_count = 0
        
        for item in data:
            s, g = get_series_gen(item['title'], item['reference'])
            
            item['specs']['series'] = s
            item['specs']['generation'] = g
            
            if s == "Unknown" or g == "Unknown":
                print(f"WARNING: Unknown Series/Gen for {item['title']} -> S:{s} G:{g}")
            else:
                updated_count += 1
                # print(f"Classified: {item['title'][:30]}... -> {s} / {g}")
        
        print(f"Updated {updated_count}/{len(data)} items with Series/Gen.")
        
        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
