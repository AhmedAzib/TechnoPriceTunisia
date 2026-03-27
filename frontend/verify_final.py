import json
import os

def verify():
    print("Verifying Data...")
    
    # 1. Check ZenBooks
    with open('src/data/mytek_laptops.json', 'r', encoding='utf-8') as f:
        mytek = json.load(f)
        
    zenbooks = [p for p in mytek if 'ZENBOOK' in p['title'].upper() and 'ULTRA' in p.get('specs', {}).get('cpu', '').upper()]
    print(f"\nFound {len(zenbooks)} ZenBooks with Ultra CPU:")
    for z in zenbooks:
        print(f" - {z['title']} | {z['specs']['cpu']} | {z['price']} TND")
        
    # 2. Check Prices in MegaPC/Skymil
    files = ['src/data/megapc_new.json', 'src/data/skymil_new.json']
    for fp in files:
        with open(fp, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        low_prices = [p for p in data if float(p.get('price', 0)) < 100]
        print(f"\n{fp}: Found {len(low_prices)} suspicious low prices (<100).")
        if len(low_prices) > 0:
            print(f"Sample: {low_prices[0]['price']} - {low_prices[0]['title']}")

if __name__ == "__main__":
    verify()
