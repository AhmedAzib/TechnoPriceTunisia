
import json
import os
import re

# Paths to data files
BASE_DIR = r"c:\Users\USER\Documents\programmation\frontend\src\data"
FILES = [
    "tunisianet_clean.json",
    "spacenet_products.json",
    "mytek_test.json",
    "wiki_clean.json"
]

SUSPICIOUS_KEYWORDS = [
    "IMPRIMANTE", "SOURIS", "CLAVIER", "ECRAN", "MONITEUR", 
    "CABLE", "ADAPTATEUR", "SACOCHE", "BOITIER", "REFROIDISSEUR", 
    "ANTIVIRUS", "OFFICE ", "WINDOWS", "GARANTIE", "SUPPORT", 
    "LOGICIEL", "TONER", "CARTOUCHE", "WEBCAM", "MICROPHONE",
    "CASQUE", "ECOUTEUR", "HAUT-PARLEUR", "ONDULEUR", "TABLETTE",
    "PROJECTEUR", "SERVER", "SERVEUR", "MEMOIRE RAM", "BARRETTE",
    "DISQUE DUR", "SSD", "CLE USB", "CARTE GRAPHIQUE", "CARTE MERE",
    "PROCESSEUR", "VENTILATEUR", "ALIMENTATION", "WATERCOOLING",
    "CHAISE", "BUREAU", "MANETTE", "CONSOLE", "JEU XBOX", "JEU PS",
    "NINTENDO SWITCH", "PLAYSTATION", "XBOX SERIES"
]

def load_data(filename):
    path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(path): return []
    try:
        with open(path, 'r', encoding='utf-8') as f: return json.load(f)
    except: return []

def main():
    problematic_items = []
    total_scanned = 0

    for filename in FILES:
        data = load_data(filename)
        for p in data:
            total_scanned += 1
            t = (p.get('name') or p.get('title') or "").upper()
            
            # Stronger check: Missing CPU AND Missing RAM
            # (Valid laptops almost always have both)
            cpu = p.get('specs', {}).get('cpu')
            ram = p.get('specs', {}).get('ram')
            
            # Helper to normalize "Unknown"
            def is_unk(val): return not val or val == 'Unknown' or val == 'N/A'
            
            if is_unk(cpu) and is_unk(ram):
                 problematic_items.append({
                     'title': t,
                     'file': filename,
                     'reason': "Missing CPU & RAM"
                 })
            else:
                # Also check for explicit non-computer starts
                # e.g. "CHARGEUR", "BATTERIE", "ECOUTEUR"
                starts = ["CHARGEUR", "BATTERIE", "SAC ", "SACOCHE", "SOURIS", "CLAVIER", "CABLE", "ADAPTATEUR", "BOITIER", "REFROIDISSEUR", "SUPPORT"]
                for s in starts:
                    if t.startswith(s):
                         problematic_items.append({
                             'title': t,
                             'file': filename,
                             'reason': f"Starts with {s}"
                         })
                         break

    print("-" * 30)
    print(f"Total Products Scanned: {total_scanned}")
    print(f"Suspicious Non-Computers Found: {len(problematic_items)}")
    print("-" * 30)
    print("Top 50 Suspicious Items:")
    for i, item in enumerate(problematic_items[:50]):
        print(f"{i+1}. [{item['file']}] {item['title']}")

if __name__ == "__main__":
    main()
