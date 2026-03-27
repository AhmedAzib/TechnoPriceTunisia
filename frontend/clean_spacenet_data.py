
import json

def clean_data():
    input_file = "src/data/spacenet_raw.json"
    output_file = "src/data/spacenet_products.json"
    
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    print(f"Original Count: {len(data)}")
    
    clean_products = []
    
    # Aggressive Exclusion List
    exclude_keywords = [
        "sac", "sacoche", "housse", "etui", "étui", "cover", "coque", "protection",
        "jeu", "game", "gaming", "ps4", "ps5", "xbox", "console", "manette", "volant",
        "toner", "cartouche", "encre", "bouteille", "papier", "ruban",
        "cable", "câble", "adaptateur", "connecteur", "convertisseur", "hub", "station", 
        "support", "refroidisseur", "ventilateur", "pate thermique",
        "micro", "casque", "ecouteur", "écouteur", "haut-parleur", "enceinte", "son",
        "souris", "clavier", "tapis", "kit", "bundle",
        "webcam", "camera", 
        "imprimante", "scanner", "photocopieur",
        "onduleur", "prise", "rallonge", "multiprise",
        "nettoyage", "spray", "chiffon",
        "logiciel", "antivirus", "office", "windows", "abonnement",
        "barrette", "memoire", "disque", "ssd", "hdd", "carte",
        "ecran", "moniteur", "tv", "projecteur"
    ]
    
    # Must explicitly start with or contain these distinct types
    # But filtering by exclusion is safer for "Edge cases"
    
    for item in data:
        title_lower = item['name'].lower()
        price_str = item['price'].replace(" TND", "").replace(",", ".").replace(" ", "")
        
        try:
            price_val = float(price_str)
        except:
            price_val = 0
            
        # 1. Price Filter (Laptops > 400 TND usually, let's say 300 to be safe for netbooks)
        if price_val < 350:
            continue
            
        # 2. Keyword Filter
        if any(bad in title_lower for bad in exclude_keywords):
            # Double check if it's a "Gaming Laptop" that got caught by 'gaming'
            # "Pc Portable Gaming" -> contains 'gaming'. 
            # We should be careful with 'gaming'.
            # If 'pc portable' is in title AND 'gaming' is in title, it is VALID.
            # But "Casque Gaming" is INVALID.
            
            is_gaming_laptop = ("pc" in title_lower or "ordinateur" in title_lower or "laptop" in title_lower) and \
                               ("gamer" in title_lower or "gaming" in title_lower)
            
            if is_gaming_laptop and "casque" not in title_lower and "souris" not in title_lower and "chaise" not in title_lower:
                 # It's likely a laptop
                 pass
            else:
                 # Real exclude
                 continue

        # 3. Type Correction
        # If "Mac" in title -> Type MacBook
        if "macbook" in title_lower or "apple" in title_lower:
            item['type'] = "MacBook"
        elif "gamer" in title_lower or "gaming" in title_lower:
            item['type'] = "Gamer"
        else:
            item['type'] = "Laptop" 

        clean_products.append(item)

    print(f"Cleaned Count: {len(clean_products)}")
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(clean_products, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    clean_data()
