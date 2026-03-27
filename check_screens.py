import json
import os

JSON_PATH = r"c:\Users\USER\Documents\programmation\frontend\src\data\mytek_mobiles.json"

def main():
    if not os.path.exists(JSON_PATH):
        print(f"Error: {JSON_PATH} not found")
        return

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    unique_screens = {}
    for product in data:
        if "specs" in product:
            s = product["specs"].get("screen", "Missing")
            unique_screens[s] = unique_screens.get(s, 0) + 1
            
    print("Unique Screen Values:")
    for s, count in sorted(unique_screens.items()):
        print(f"  '{s}': {count}")

if __name__ == "__main__":
    main()
