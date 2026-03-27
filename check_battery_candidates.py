import json

JSON_PATH = r"c:\Users\USER\Documents\programmation\frontend\src\data\mytek_mobiles.json"

def main():
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error: {e}")
        return

    candidates_2000 = []
    candidates_6000 = []
    candidates_7000 = []
    
    for p in data:
        t = p.get("title", "").lower()
        
        # Check for 2000ish
        if "2000" in t or "2500" in t or "feature" in p.get("category", "").lower() or "nokia" in t or "2go" in t and "16go" in t: 
            # Low spec phones might be 2000-3000 range, but user wants specifically 2000 filter.
            # Nokia 105 etc are often < 2000.
            if "mah" in t and ("2000" in t or "2500" in t):
                 candidates_2000.append(t)
            elif "nokia" in t or "itel" in t and "feature" in t: # simplistic check
                 candidates_2000.append(t + " (Inferred?)")

        # Check for 6000
        if "6000" in t or "pova" in t or "galaxy m" in t or "hot 30 play" in t or "c30" in t or "narzo" in t:
            candidates_6000.append(t)
            
        # Check for 7000
        if "7000" in t or "pova 2" in t or "pova 3" in t or "pova neo" in t: # Some Povas are 7000
            candidates_7000.append(t)

        # Check raw battery spec if available
        bat = p.get("specs", {}).get("battery", "")
        if "6000" in bat: candidates_6000.append(f"{t} [SPEC: {bat}]")
        if "7000" in bat: candidates_7000.append(f"{t} [SPEC: {bat}]")
        if "2000" in bat or "2500" in bat: candidates_2000.append(f"{t} [SPEC: {bat}]")

    print(f"--- 2000 mAh Candidates ({len(candidates_2000)}) ---")
    for c in set(candidates_2000): print(c)

    print(f"\n--- 6000 mAh Candidates ({len(candidates_6000)}) ---")
    for c in set(candidates_6000): print(c)
    
    print(f"\n--- 7000 mAh Candidates ({len(candidates_7000)}) ---")
    for c in set(candidates_7000): print(c)

if __name__ == "__main__":
    main()
