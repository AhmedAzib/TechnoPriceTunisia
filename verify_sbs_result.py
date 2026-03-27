import json

def verify_sbs_data():
    try:
        with open("sbs_gpu.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        print(f"Loaded {len(data)} products.")
        
        seen_links = set()
        duplicates = []
        
        for item in data:
            if item['link'] in seen_links:
                duplicates.append(item['link'])
            seen_links.add(item['link'])
            
        if duplicates:
            print(f"ERROR: Found {len(duplicates)} duplicates!")
            for d in duplicates[:5]:
                print(f"  - {d}")
        else:
            print("SUCCESS: No duplicates found.")
            
        print("Detailed check complete.")
        
    except FileNotFoundError:
        print("sbs_gpu.json not found yet.")
    except Exception as e:
        print(f"Error checking data: {e}")

if __name__ == "__main__":
    verify_sbs_data()
