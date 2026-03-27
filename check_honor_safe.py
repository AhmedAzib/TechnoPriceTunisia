import json
import sys

# Force UTF-8 for stdout
sys.stdout.reconfigure(encoding='utf-8')

JSON_PATH = r"c:\Users\USER\Documents\programmation\frontend\src\data\mytek_mobiles.json"

def main():
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error: {e}")
        return

    print("--- HONOR PHONES MATCH ---")
    count = 0
    for p in data:
        t = p.get("title", "").lower()
        if "honor" in t:
             print(f"TITLE: {p.get('title')}")
             # print(f"SPECS: {p.get('specs')}")
             spec_bat = p.get('specs', {}).get('battery', 'Unknown')
             print(f"BATTERY SPEC: {spec_bat}")
             print("-" * 20)
             count += 1
    print(f"Total Honor phones found: {count}")

if __name__ == "__main__":
    main()
