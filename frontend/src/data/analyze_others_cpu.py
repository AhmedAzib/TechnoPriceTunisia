import json
import os
import glob
from collections import Counter

data_dir = r"c:\Users\USER\Documents\programmation\frontend\src\data"
files = glob.glob(os.path.join(data_dir, "*_mobiles.json")) + glob.glob(os.path.join(data_dir, "samsung_tunisie.json")) + glob.glob(os.path.join(data_dir, "*_phones.json"))

others_titles = []

print("Simulating CPU Inference...")

for file_path in files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for item in data:
            specs = item.get('specs', {})
            cpu = specs.get('cpu', 'Unknown')
            title = item.get('title', '').strip()
            brand = item.get('brand', 'Unknown') # Crude check
            
            # Simulate the current logic in MobilesPage.jsx
            inferred_cpu = cpu
            
            if not cpu or cpu in ["Unknown", "N/A"]:
                full_text = (title + " " + specs.get('raw', '')).lower()
                
                if 'snapdragon' in full_text: inferred_cpu = "Snapdragon"
                elif 'helio' in full_text: inferred_cpu = "MediaTek Helio"
                elif 'dimensity' in full_text: inferred_cpu = "MediaTek Dimensity"
                elif 'exynos' in full_text: inferred_cpu = "Samsung Exynos"
                elif 'unisoc' in full_text or 'tiger' in full_text: inferred_cpu = "Unisoc"
                elif 'tensor' in full_text: inferred_cpu = "Google Tensor"
                elif 'kirin' in full_text: inferred_cpu = "HiSilicon Kirin"
                elif any(x in full_text for x in ['bionic', 'a14', 'a15', 'a16', 'a17', 'a18']): inferred_cpu = "Apple A-Series"
                elif brand == 'Apple': inferred_cpu = "Apple A-Series"
                elif 'octa core' in full_text or 'octa-core' in full_text: inferred_cpu = "Octa Core"
                else: inferred_cpu = "Others"

            if inferred_cpu == "Others":
                others_titles.append(title)

    except Exception as e:
        print(f"Error reading {file_path}: {e}")

print(f"Total 'Others': {len(others_titles)}")
print("\nTop 50 Most Common patterns in Others:")

# Simple N-gram analysis or just dumping common words could help, 
# but let's just dump the first 50 unique titles to spot patterns manually 
# as the user wants me to identify them.

unique_others = sorted(list(set(others_titles)))
for t in unique_others[:100]:
    print(t)
