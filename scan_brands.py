import json

JSON_PATH = r"c:\Users\USER\Documents\programmation\frontend\src\data\mytek_mobiles.json"

def main():
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error: {e}")
        return

    print("Scanning TECNO, INFINIX, SAMSUNG, HONOR only:")
    for p in data:
        t = p.get("title", "").lower()
        if "tecno" in t or "infinix" in t or "samsung" in t or "galaxy" in t or "honor" in t:
             print(f"{t}")

if __name__ == "__main__":
    main()
