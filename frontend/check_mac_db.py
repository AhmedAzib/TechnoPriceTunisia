import json
import os

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'src', 'data', 'mytek_laptops.json')

def check():
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"Total items in DB: {len(data)}")
    
    mac_links = []
    mac_titles = []
    
    user_titles_hints = [
        "M1 8Go 256Go", "M4 16Go 256Go", "M4 16Go 512Go", "M4 24Go 512Go",
        "M5 16Go 512Go", "M5 16Go 1To", "M4 Pro 24G 512G", "M5 24Go 1To"
    ]
    
    count = 0
    for item in data:
        t = item.get('title', '').upper()
        l = item.get('link', '').lower()
        cat = item.get('sub_category', '')
        
        is_mac = False
        if 'MACBOOK' in t: is_mac = True
        if 'APPLE' in t: is_mac = True
        if 'MAC.HTML' in l: is_mac = True
        if cat == 'Mac': is_mac = True
        
        if is_mac:
            count += 1
            print(f"[{count}] Found: {item['title']}")
            # print(f"    Link: {item['link']}")
            mac_titles.append(item['title'])

    print(f"\nTotal Confirmed Macs found: {count}")
    
    # Check what is missing from User's list (simplified)
    # Just checking counts of specific models
    print("\n--- Missing Model Check ---")
    # M1
    m1 = sum(1 for t in mac_titles if "M1" in t.upper())
    print(f"M1 Models: {m1} (User list has 1)")
    
    # M4
    m4 = sum(1 for t in mac_titles if "M4" in t.upper())
    print(f"M4 Models: {m4} (User list has 10?)")
    
    # M5 (User listed M5?? MyTek usually has M3/M4, maybe M5 is typo in user request or brand new? 
    # User text says: 'Processeur: Apple M5'. Wait, M5 doesn't exist yet properly? 
    # Ah, maybe MyTek has typos or I am out of date. User says M5. I will check for M5)
    m5 = sum(1 for t in mac_titles if "M5" in t.upper())
    print(f"M5 Models: {m5}")

    # M4 Pro
    m4pro = sum(1 for t in mac_titles if "M4 PRO" in t.upper())
    print(f"M4 Pro Models: {m4pro}")

if __name__ == "__main__":
    check()
