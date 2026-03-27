import json
import re

user_text = """
Carte Mère - ASUS PRIME A520M-R
Carte Mère - ASUS H510M-R r2.0
Carte Mère - AMD GIGABYTE A520M K V2
Carte Mère - ASUS PRIME H610M-K D4 ARGB
Carte Mère - ASUS PRIME H610M-K D5 ARGB
Carte Mère - ASUS PRIME B760M-K D4
Carte Mère - ASUS PRIME B550M-K
Carte Mère - ASUS TUF GAMING B550M-PLUS WIFI II D4
Carte mère ASUS PRIME B760M-A WIFI D5
Carte Mère - ASUS TUF GAMING A620-PRO WIFI AM5
Carte mère ASUS PRIME B840-PLUS WIFI
Carte Mère - ASUS PRIME H770-PLUS D4
Carte mère ASUS TUF GAMING B850-PLUS WIFI
Carte mère ASUS ROG STRIX B850-A GAMING WIFI
Carte Mère - ASUS PRIME X670-P WIFI
Carte Mère - ASUS TUF X870 PLUS WIFI
Carte Mère - ASUS ROG STRIX B650E-F GAMING WIFI
Carte mère ASUS ROG STRIX B850-F GAMING WIFI
Carte Mère - ASUS TUF GAMING Z790-PLUS WIFI D4
Carte Mère - ASUS ProArt X670E-CREATOR WIFI
Carte mère ASUS PRIME TRX40-PRO
Carte Mère - ASUS ProArt X870E-CREATOR WIFI
Carte mère ASUS ROG CROSSHAIR X870E HERO
Carte mère ASUS ROG MAXIMUS Z790 HERO
CARTE MÈRE MSI CREATOR TRX40
"""

# Normalize user list
user_items = [line.strip() for line in user_text.strip().split('\n') if line.strip()]
print(f"User expects {len(user_items)} items.")

# Load scraped data
try:
    with open('frontend/src/data/sbs_motherboards.json', 'r', encoding='utf-8') as f:
        scraped_data = json.load(f)
except FileNotFoundError:
    print("Error: frontend/src/data/sbs_motherboards.json not found.")
    exit()

scraped_titles = [p['title'] for p in scraped_data]
print(f"Scraped {len(scraped_titles)} items.")

missing_items = []

print("\n--- Missing Items Analysis ---")
for u_item in user_items:
    # Normalized search
    found = False
    u_norm = u_item.upper().replace("CARTE MÈRE - ", "").replace("CARTE MÈRE ", "").replace("CARTE MERE ", "").strip()
    
    for s_title in scraped_titles:
        s_norm = s_title.upper().replace("CARTE MÈRE - ", "").replace("CARTE MÈRE ", "").replace("CARTE MERE ", "").strip()
        
        # Exact substring match
        if u_norm in s_norm or s_norm in u_norm:
            # Check for D4/D5 mismatch
            if "D4" in u_norm and "D5" in s_norm and "D4" not in s_norm: continue
            if "D5" in u_norm and "D4" in s_norm and "D5" not in s_norm: continue
            found = True
            break
            
    if not found:
        print(f"MISSING: {u_item}")
        missing_items.append(u_item)

print(f"\nTotal Missing: {len(missing_items)}")
