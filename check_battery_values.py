import json

JSON_PATH = r"c:\Users\USER\Documents\programmation\frontend\src\data\mytek_mobiles.json"

def main():
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error: {e}")
        return

    bats = set()
    for p in data:
        spec = p.get("specs", {}).get("battery", "Unknown")
        bats.add(spec)

    print("Unique Battery Values:")
    for b in sorted(list(bats)):
        print(f"'{b}'")

if __name__ == "__main__":
    main()
