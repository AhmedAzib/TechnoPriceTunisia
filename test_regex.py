import re

text = "ZT-A30510H-10L - Carte Graphique ZOTAC GAMING GeForce RTX 3050 Twin Edge OC - Taille mémoire vidéo: 6 Go - Type de mémoire: GDDR6 - Type Carte Graphique: NVIDIA GeForce - Chipset Graphique: GeForce GeForce RTX 3050 Twin Edge OC - Interface: PCI Express 4.0 8x - Horloges de base: Boost: 1477 MHz - Noyaux Cuda: 2304 Unités - Horloge mémoire: 14 Gbit/s - Bus Mémoire: 96 bits - Prise en charge des versions DirectX: 12 Ultime - Version Opengl: 4.6 - Alimentation Recommandée: 450 Watts - Consommation d'énergie: 70 Watts - Affichage quadruple - Refroidissement: Deux ventilateurs de 70 mm + dissipateur thermique - Windows 11, 10 (v1809 novembre 2018 ou version ultérieure) / 7 64 bits - Connecteurs: 1x HDMI 2.1, 3x DisplayPort 1.4a - Dimensions: 161,9 x 111,2 x 40,2 mm - Garantie: 1 an"
text_upper = text.upper()

print(f"Text upper: {text_upper}")

# Regex from scraper
speed_match = re.search(r'(?:HORLOGE|VITESSE|SPEED).{0,20}?(?:MÉMOIRE|MEMORY).{0,10}?[:\-]?\s*(\d+(?:[.,]\d+)?)\s*(?:GBIT\/S|GBPS)', text_upper)
if speed_match:
    print(f"Match 1 Group 1: '{speed_match.group(1)}'")
    print(f"Full Match 1: '{speed_match.group(0)}'")
else:
    print("Match 1 failed")
    
    speed_match = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:GBIT\/S|GBPS)', text_upper)
    if speed_match:
        print(f"Match 2 Group 1: '{speed_match.group(1)}'")
        print(f"Full Match 2: '{speed_match.group(0)}'")
    else:
        print("Match 2 failed")
