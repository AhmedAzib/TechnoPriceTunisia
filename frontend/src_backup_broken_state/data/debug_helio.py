import json
import os
import glob

data_dir = r"c:\Users\USER\Documents\programmation\frontend\src\data"
files = glob.glob(os.path.join(data_dir, "*_mobiles.json")) + glob.glob(os.path.join(data_dir, "samsung_tunisie.json")) + glob.glob(os.path.join(data_dir, "*_phones.json"))

matches = []
misses = []
current_values = {}

print("Simulating Helio Logic...")

for file_path in files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for p in data:
            specs = p.get('specs', {})
            cpu = specs.get('cpu', 'Unknown')
            title = p.get('title', '').strip()
            
            # Count current distribution
            current_values[cpu] = current_values.get(cpu, 0) + 1
            
            # Simulate Block Entry
            should_enter = (not cpu) or (cpu in ["Unknown", "N/A", "Others", "Octa Core"])
            
            # Simulate Logic
            new_cpu = cpu
            
            # Normalize Title for logic
            t_lower = title.lower()
            full_text = (title + " " + specs.get('raw', '')).lower()
            
            is_helio_candidate = False
            
            # Keyword Check
            if any(x in full_text for x in ['helio', 'g99', 'g88', 'g85', 'g96', 'g37', 'g36']):
                is_helio_candidate = True
            
            # Model Check (Simulate MobilesPage Chunk 1)
            t_lower = title.lower()
            
            # Chunk 1 Logic simulation
            isHonorHelio = ('honor x5' in t_lower or 'honor x6' in t_lower or 'honor x6a' in t_lower or 'honor x6b' in t_lower)
            isHonorSnapdragon = ('honor x7' in t_lower or 'honor x8' in t_lower or 'honor x9' in t_lower or 'honor 90' in t_lower or 'honor 70' in t_lower)
            isItelUnisoc = ('itel a70' in t_lower or 'itel p55' in t_lower or 'itel s23' in t_lower or 'itel a05' in t_lower)
            isRealmeUnisoc = ('realme c61' in t_lower or 'realme c53' in t_lower or 'realme c51' in t_lower or 'realme c33' in t_lower or 'realme c30' in t_lower)

            if isHonorHelio or isHonorSnapdragon or isItelUnisoc or isRealmeUnisoc:
                # This would be caught by current logic
                pass
            else:
                # Check if it IS one of these brands but NOT caught
                if 'honor' in t_lower:
                    misses.append(f"HONOR MISS: {title}")
                elif 'itel' in t_lower:
                    pass # Only print Honor misses for now to save space, or print all
                    misses.append(f"ITEL MISS: {title}")
                elif 'realme' in t_lower:
                    misses.append(f"REALME MISS: {title}")
                elif 'lesia' in t_lower or 'clever' in t_lower:
                    misses.append(f"LESIA/CLEVER MISS: {title}")

    except Exception as e:
        pass

print("\n--- CHUNK 1 MISSES (Target Brands) ---")
for m in misses[:100]: # Print top 100 misses
    print(m)
