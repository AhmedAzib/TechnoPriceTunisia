import json
import requests
import os

def check_images():
    path = "../src/data/samsung_tunisie.json"
    if not os.path.exists(path):
        print("File not found.")
        return

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Checking {len(data)} images...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.samsungtunisie.tn/"
    }

    issues = 0
    for i, product in enumerate(data[:20]): # Check first 20
        url = product.get("image", "")
        if not url:
            print(f"[{i}] No URL for {product['title']}")
            issues += 1
            continue
            
        try:
            r = requests.head(url, headers=headers, timeout=5)
            if r.status_code != 200:
                print(f"[{i}] FAIL {r.status_code}: {url}")
                issues += 1
            else:
                print(f"[{i}] OK: {url}")
        except Exception as e:
            print(f"[{i}] ERROR {e}: {url}")
            issues += 1

    print(f"\nTotal Issues in sample: {issues}")

if __name__ == "__main__":
    check_images()
