import json
from collections import Counter

FILE = r"frontend\src\data\tunisianet_clean.json"

JUNK_KEYWORDS = [
    "sacoche", "sac à dos", "souris", "clavier", "casque", "écouteur", 
    "tapis", "refroidisseur", "support", "cable", "câble", "chargeur", 
    "adaptateur", "hub", "station", "webcam", "micro", "haut parleur", 
    "enceinte", "imprimante", "scanner", "toner", "cartouche", 
    "logiciel", "microsoft", "kaspersky", "bitdefender", "eset", 
    "disque dur", "ssd", "barrette", "mémoire", "ram", "carte mère", 
    "carte graphique", "processeur", "alimentation", "boitier", 
    "ecran", "moniteur", "onduleur", "serveur" # Maybe servers are okay? User said "computers".
]

def analyze():
    with open(FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"Total Initial Items: {len(data)}")
    
    junk_counts = Counter()
    junk_items = []
    clean_candidates = []
    
    for item in data:
        t = item['title'].lower()
        is_junk = False
        for kw in JUNK_KEYWORDS:
            if kw in t:
                # Safe guards?
                # "Clavier" -> "Pc Portable ... Clavier Retroéclairé" (Safe guard needed)
                # "Souris" -> "Pc ... + Souris" (Safe guard needed)
                
                # If keyword is "sacoche" and it says "avec sacoche" -> Keep (it's a bundle). 
                # If it says "Sacoche pour PC" -> Junk.
                
                # Heuristic: 
                # If title starts with "Pc Portable" or "Pc de Bureau" or "Ordinateur", it's likely a computer.
                # If title starts with "Sacoche" or "Souris", it's junk.
                
                if t.startswith(kw):
                    is_junk = True
                    junk_counts[kw] += 1
                    break
                    
                # Strict check for some words anywhere if they are the main subject?
                if kw in ["imprimante", "toner", "cartouche", "ecran", "moniteur", "onduleur"]:
                    # "Ecran" might be "15.6 pouces Ecran". 
                    # But standalone "Ecran Lenovo..." is junk.
                    if not ("pc portable" in t or "ordinateur" in t or "pc de bureau" in t):
                         is_junk = True
                         junk_counts[kw] += 1
                         break
                         
        if is_junk:
            junk_items.append(item['title'])
        else:
            clean_candidates.append(item)
            
    print("\n--- Junk Analysis ---")
    for kw, count in junk_counts.most_common():
        print(f"{kw}: {count}")
        
    print(f"\nTotal Junk Identified: {len(junk_items)}")
    print(f"Remaining Candidates: {len(clean_candidates)}")
    
    # Check for implicit non-computers (titles that don't start with PC/Ordinateur)
    print("\n--- Starts With Analysis (Remaining) ---")
    starts = Counter()
    for item in clean_candidates:
        first_word = item['title'].split()[0].lower()
        starts[first_word] += 1
        
    for w, c in starts.most_common(20):
        print(f"{w}: {c}")

if __name__ == "__main__":
    analyze()
