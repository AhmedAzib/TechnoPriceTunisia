import json
import os
import re

JSON_PATH = r"c:\Users\USER\Documents\programmation\frontend\src\data\mytek_mobiles.json"

def normalize_screen(screen_text):
    if not screen_text or screen_text == "Unknown":
        return "Unknown"
    
    # Extract number (handling e.g. 6.5" or 6,5")
    # Replace comma with dot for parsing
    clean_text = screen_text.replace(',', '.').replace('"', '').strip()
    
    match = re.search(r'(\d+\.?\d*)', clean_text)
    if match:
        try:
            val = float(match.group(1))
            
            # User Rule: "second number after , is not important" -> Truncate to 1 decimal
            # e.g. 6.56 -> 6.5
            # Logic: int(val * 10) / 10
            truncated = int(val * 10) / 10.0
            
            # Format back to string
            return f"{truncated}\""
        except ValueError:
            return screen_text
            
    return screen_text

def main():
    if not os.path.exists(JSON_PATH):
        print(f"Error: {JSON_PATH} not found")
        return

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    updates = 0
    unique_changes = set()
    
    for product in data:
        if "specs" in product and "screen" in product["specs"]:
            original = product["specs"]["screen"]
            normalized = normalize_screen(original)
            
            if original != normalized:
                product["specs"]["screen"] = normalized
                unique_changes.add(f"{original} -> {normalized}")
                updates += 1

    if updates > 0:
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully updated {updates} products.")
        print("Sample changes:")
        for change in list(unique_changes)[:10]:
            print(f"  {change}")
    else:
        print("No updates needed.")

if __name__ == "__main__":
    main()
