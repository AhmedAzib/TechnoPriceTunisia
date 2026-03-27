import json

JSON_PATH = r"c:\Users\USER\Documents\programmation\frontend\src\data\mytek_mobiles.json"

def main():
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error: {e}")
        return

    count_7000 = 0
    count_6000 = 0
    
    print("--- Searching for High Battery Candidates ---")

    for p in data:
        t = p.get("title", "").lower().replace(r'\s+', ' ')
        
        # 7000 mAh Logic Check
        is_7000 = False
        if "tecno pova 2" in t or "tecno pova 3" in t or "pova neo" in t or "7000" in t:
             print(f"[7000 MATCH]: {t}")
             is_7000 = True
             count_7000 += 1
             
        # 6000 mAh Logic Check
        if not is_7000:
             if "tecno pova" in t or "galaxy m" in t or "infinix hot 30 play" in t:
                 print(f"[6000 MATCH]: {t}")
                 count_6000 += 1
             elif "honor x7a" in t or "honor x7b" in t or "c30" in t:
                 print(f"[6000 MATCH]: {t}")
                 count_6000 += 1
                 
    print(f"\nTotal 7000 mAh matches: {count_7000}")
    print(f"Total 6000 mAh matches: {count_6000}")

    # Broad search for potential misses
    print("\n--- Broad Search for Keywords ---")
    keywords = ["pova", "benco", "narzo", "rog", "galaxy m", "x7a", "x7b", "hot 30", "c30", "monster"]
    for p in data:
        t = p.get("title", "").lower()
        for k in keywords:
            if k in t:
                # Don't reprint if already matched above (simplistic check)
                print(f"KEYWORD '{k}' FOUND in: {t}")

if __name__ == "__main__":
    main()
