import json
import os

JSON_PATH = r"c:\Users\USER\Documents\programmation\frontend\src\data\mytek_mobiles.json"

def normalize_cpu_name(cpu):
    if not cpu or cpu == "Unknown":
        return "Unknown"
    
    cpu_upper = cpu.upper().strip()
    
    # 1. UNISOC Normalization
    # User Request: "T7225", "Unisoc", "Unisoc T7250" -> "Unisoc"
    if "T7225" in cpu_upper:
        return "Unisoc"
    if "UNISOC T7250" in cpu_upper: # Specific model mentioned
        return "Unisoc"
    if "UNISOC" in cpu_upper: # Catch-all for other Unisoc if desired, but user listed specific ones. Let's apply broadly for "Unisoc"
        # User said: "Unisoc (13) Unisoc T7250 (15) T7225 (4) ... in one option"
        # So yes, they want them all as "Unisoc"
        return "Unisoc"

    # 2. SNAPDRAGON Normalization
    # User Request: "Snapdragon", "Snapdragon 685" -> "Snapdragon"
    if "SNAPDRAGON" in cpu_upper:
        # Check if it is the specific 685 or just general Snapdragon 
        # User wants "Snapdragon" and "Snapdragon 685" to be "Snapdragon"
        # They didn't explicitly say ALL snapdragons, but "put those 2... together".
        # Safe to assume they want a cleaner list.
        # But let's be careful not to destroy "Snapdragon 8 Gen 2" if they didn't ask.
        # However, for 685 specifically:
        if "685" in cpu_upper:
            return "Snapdragon"
        if cpu_upper == "SNAPDRAGON":
            return "Snapdragon"
            
    return cpu

def main():
    if not os.path.exists(JSON_PATH):
        print(f"Error: {JSON_PATH} not found")
        return

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    updates = 0
    for product in data:
        if "specs" in product and "cpu" in product["specs"]:
            original = product["specs"]["cpu"]
            normalized = normalize_cpu_name(original)
            
            if original != normalized:
                product["specs"]["cpu"] = normalized
                updates += 1
                # print(f"Updated: {original} -> {normalized}")

    if updates > 0:
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Successfully updated {updates} products.")
    else:
        print("No updates needed.")

if __name__ == "__main__":
    main()
