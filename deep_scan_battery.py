import json

JSON_PATH = r"c:\Users\USER\Documents\programmation\frontend\src\data\mytek_mobiles.json"

def main():
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error: {e}")
        return

    print("Scanning for 6000...")
    found_6000 = False
    for p in data:
        s = json.dumps(p).lower()
        if "6000" in s:
            print(f"MATCH 6000: {p.get('title')} --- {p.get('specs', {}).get('battery')}")
            found_6000 = True
    if not found_6000: print("No explicit '6000' found in any field.")

    print("\nScanning for 7000...")
    found_7000 = False
    for p in data:
        s = json.dumps(p).lower()
        if "7000" in s:
            print(f"MATCH 7000: {p.get('title')} --- {p.get('specs', {}).get('battery')}")
            found_7000 = True
    if not found_7000: print("No explicit '7000' found in any field.")

    print("\nScanning for 2000/2500...")
    for p in data:
        s = json.dumps(p).lower()
        if "2000" in s or "2500" in s:
            # Filter out price 2000 or year 2000 if possible, but raw dump is fine
            if "mah" in s or "batterie" in s:
                print(f"MATCH 2000ish: {p.get('title')} --- {p.get('specs', {}).get('battery')}")

if __name__ == "__main__":
    main()
