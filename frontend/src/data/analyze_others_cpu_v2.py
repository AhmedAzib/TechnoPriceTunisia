import json
import os
import glob

data_dir = r"c:\Users\USER\Documents\programmation\frontend\src\data"
files = glob.glob(os.path.join(data_dir, "*_mobiles.json")) + glob.glob(os.path.join(data_dir, "samsung_tunisie.json")) + glob.glob(os.path.join(data_dir, "*_phones.json"))

others_titles = []

print("Simulating NEW CPU Inference Logic...")

for file_path in files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for item in data:
            specs = item.get('specs', {})
            cpu = specs.get('cpu', 'Unknown')
            title = item.get('title', '').strip()
            brand = item.get('brand', 'Unknown')
            
            inferred_cpu = cpu
            
            if not cpu or cpu in ["Unknown", "N/A", "Others", "Octa Core"]:
                full_text = (title + " " + specs.get('raw', '')).lower()
                
                # Broad keywords
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
                
                # --- DEEP MODEL MAPPING (Python Port) ---
                if not inferred_cpu or inferred_cpu in ["Unknown", "Others", "Octa Core"]:
                     lower_title = title.lower()
                     
                     if brand == 'Apple' or 'iphone' in lower_title: inferred_cpu = "Apple A-Series"
                     
                     elif 'galaxy s2' in lower_title or 'galaxy z' in lower_title: inferred_cpu = "Snapdragon"
                     elif 'galaxy a5' in lower_title or 'galaxy a3' in lower_title or 'galaxy a2' in lower_title: inferred_cpu = "Samsung Exynos"
                     elif 'galaxy a1' in lower_title or 'galaxy a0' in lower_title: inferred_cpu = "MediaTek Helio"

                     elif 'redmi note' in lower_title: inferred_cpu = "MediaTek Dimensity"
                     elif 'redmi 1' in lower_title or 'redmi a' in lower_title: inferred_cpu = "MediaTek Helio"
                     elif 'poco f' in lower_title: inferred_cpu = "Snapdragon"
                     elif 'poco x' in lower_title or 'poco m' in lower_title: inferred_cpu = "MediaTek Dimensity"

                     elif 'gt 10' in lower_title or 'gt 20' in lower_title: inferred_cpu = "MediaTek Dimensity"
                     elif 'note 30' in lower_title or 'note 40' in lower_title: inferred_cpu = "MediaTek Helio"
                     elif 'hot 30' in lower_title or 'hot 40' in lower_title or 'hot 50' in lower_title: inferred_cpu = "MediaTek Helio"
                     elif 'smart 8' in lower_title or 'smart 9' in lower_title or 'smart 7' in lower_title: inferred_cpu = "Unisoc"

                     elif 'phantom' in lower_title: inferred_cpu = "MediaTek Dimensity"
                     elif 'camon' in lower_title: inferred_cpu = "MediaTek Helio"
                     elif 'spark' in lower_title: inferred_cpu = "MediaTek Helio"
                     elif 'pop' in lower_title: inferred_cpu = "Unisoc"

                     elif 'honor 90' in lower_title or 'honor 70' in lower_title or 'honor 50' in lower_title: inferred_cpu = "Snapdragon"
                     elif 'honor x9' in lower_title or 'honor x8' in lower_title or 'honor x7' in lower_title: inferred_cpu = "Snapdragon"
                     elif 'honor x6' in lower_title or 'honor x5' in lower_title: inferred_cpu = "MediaTek Helio"
                     elif 'honor play' in lower_title: inferred_cpu = "Unisoc"

                     elif 'realme c' in lower_title: inferred_cpu = "Unisoc"
                     elif 'realme 1' in lower_title: inferred_cpu = "MediaTek Dimensity"

                     elif 'itel' in lower_title: inferred_cpu = "Unisoc"
                     elif 'lesia' in lower_title or 'clever' in lower_title or 'evertek' in lower_title or 'iku' in lower_title: inferred_cpu = "Unisoc"
                     
                     else: inferred_cpu = "Others"

            if inferred_cpu == "Others":
                others_titles.append(title)

    except Exception as e:
        print(f"Error reading {file_path}: {e}")

print(f"Total 'Others' Remaining: {len(others_titles)}")
unique_others = sorted(list(set(others_titles)))
for t in unique_others[:50]:
    print(t)
