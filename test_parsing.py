
import re

text_example = """
Carte Graphique - ZOTAC GAMING GEFORCE RTX 3060 TWIN EDGE 12GB GDDR6
ZOTAC
1 039,000 TND
Taxe incluse
Rupture de stock
Cœurs : CUDA3584
Mémoire vidéo : 12 Go de mémoire GDDR6
Bus mémoire : 192 bits
Horloge moteurBoost : 1 777 MHz
Horloge mémoire : 15 Gbit/s
PCI express : 4.0 16x
Sorties : 3 x DisplayPort 1.4a (jusqu'à 7680x4320@60Hz )
HDMI 2.1* (jusqu'à 7680x4320@60Hz )
Capacité multi-affichage : Affichage quadruple
Alimentation recommandée : 600W
Consommation d'énergie : 170W
Longueur de la carte : 224,1 mm x 116,3 mm x 39,2 mm
Quantité :
1
"""

def clean_text(text):
    if not text: return ""
    return re.sub(r'\s+', ' ', text).strip()

def parse_spec_lines(text):
    specs = {}
    lines = text.split('\n')
    current_key = None
    
    for line in lines:
        line = clean_text(line)
        if not line: continue
        
        # Skip pricing/stock info lines if they appear in the description block
        if "TND" in line and any(c.isdigit() for c in line): continue
        if line in ["Taxe incluse", "Rupture de stock", "En stock", "ZOTAC", "Quantité :", "1"]: continue
        
        if ':' in line:
            # Check if it's a "Key : Value" line
            parts = line.split(':', 1)
            key = clean_text(parts[0])
            value = clean_text(parts[1])
            
            # Heuristic: Keys are usually short (e.g. < 40 chars)
            if len(key) < 50: 
                specs[key] = value
                current_key = key
            else:
                # If no clear key, maybe append to previous?
                if current_key:
                    specs[current_key] += " " + line
        else:
            # Continuation line?
            if current_key:
                specs[current_key] += " " + line
                
    return specs

parsed = parse_spec_lines(text_example)
import json
print(json.dumps(parsed, indent=2, ensure_ascii=False))
