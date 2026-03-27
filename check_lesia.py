import json

JSON_PATH = r"c:\Users\USER\Documents\programmation\frontend\src\data\mytek_mobiles.json"

def main():
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error: {e}")
        return

    print("Scanning for Lesia...")
    for p in data:
        t = p.get("title", "").lower()
        if "lesia" in t:
             print(f"TITLE: {p.get('title')}")
             print(f"SPECS: {p.get('specs')}")
             print("-" * 20)

if __name__ == "__main__":
    main()
