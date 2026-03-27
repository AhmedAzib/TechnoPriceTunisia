import json
import requests
import re
import time
import random
import os

# Source File
SOURCE_FILE = 'src/data/mytek_motherboards.json'
# Output File (Extended)
# OUTPUT_FILE = 'src/data/mytek_motherboards_extended.json' 
# Actually, overwrite the source file to update properly? 
# Better: extend and overwrite.
OUTPUT_FILE = 'src/data/mytek_motherboards.json'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
}

def clean_capacity(cap_str):
    if not cap_str: return "Unknown"
    # Extract digits + Go/GB
    match = re.search(r'(\d+)\s*(Go|GB|Gb)', cap_str, re.IGNORECASE)
    if match:
        val = int(match.group(1))
        unit = "Go" # Standardize to Go
        return f"{val} {unit}"
    return "Unknown"

def scrape_memory_capacity():
    try:
        with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {SOURCE_FILE} not found.")
        return

    updated_count = 0
    total = len(data)
    
    print(f"Starting scrape for {total} motherboards...")

    for i, item in enumerate(data):
        # Skip if ALL have values
        specs = item.get('specs', {})
        mem_cap = specs.get('memory_capacity', 'Unknown')
        mem_speed = specs.get('memory_speed', 'Unknown')
        mem_type = specs.get('memory_type', 'Unknown')
        fmt = specs.get('format', 'Unknown')
        slots = specs.get('mb_slots', 'Unknown')
        storage = specs.get('mb_storage', 'Unknown')

        # Check for bad data (0000 MHz)
        invalid_speed = (mem_speed == 'Unknown' or '0000' in mem_speed or mem_speed == '0 MHz' or mem_speed.strip() == 'MHz')
        
        if mem_cap != 'Unknown' and not invalid_speed and mem_type != 'Unknown' and fmt != 'Unknown' and slots != 'Unknown' and storage != 'Unknown':
            continue
            
        url = item.get('link')
        if not url:
            continue

        print(f"[{i+1}/{total}] Scraping: {item['title']}...", end="", flush=True)

        try:
            time.sleep(random.uniform(0.5, 1.5)) # Polite delay
            response = requests.get(url, headers=HEADERS, timeout=10)
            
            if response.status_code == 200:
                html = response.text
                
                # Clean HTML (strip tags) to avoid matching hex colors like #000000
                html = re.sub(r'<[^>]+>', ' ', html)
                
                # Extract "Capacité mémoire" pattern
                # Usually in description meta tag or table
                # Pattern: Capacité mémoire: ... (\d+ Go)
                
                # 1. Memory Capacity
                match_cap = re.search(r'Capacité mémoire\s*:.*?(?:jusqu\'à)?\s*(\d+\s*Go)', html, re.IGNORECASE | re.DOTALL)
                if not match_cap:
                     match_cap = re.search(r'Max Memory\s*:.*?(\d+\s*GB)', html, re.IGNORECASE)
                
                if match_cap:
                    capacity = match_cap.group(1).replace("GB", "Go").replace("Gb", "Go")
                    if 'specs' not in item: item['specs'] = {}
                    item['specs']['memory_capacity'] = capacity
                    print(f" CAP: {capacity}", end="")
                    updated_count += 1
                
                # 2. Memory Speed (Fréquence Mémoire Supporté)
                # Patterns: 
                # "Fréquence Mémoire Supporté: up to 5100 MHz"
                # STRICTER: (\d{3,5}) to catch 3200, 4800, 8000. Avoids single/double digits.
                # Support MT/s (MegaTransfers/second) which is used on newer boards (AM5/Z890)
                match_speed = re.search(r'Fréquence Mémoire Supporté\s*:.*?(?:up to|Jusqu(?:\'|’)?à)?\s*(\d{3,5}).*?(?:MHz|MT/s)', html, re.IGNORECASE | re.DOTALL)
                
                if not match_speed:
                    # Fallback 2: "DDR4 3200MHz" or "DDR5 6000" (Generic DDR match)
                    # Look for "DDR[45] \d{4}" often implies max speed if mentioned in header/specs
                    match_speed = re.search(r'DDR[45]\s*(\d{4})\s*(?:Hz|MHz|MT/s|O\.C|OC)?', html, re.IGNORECASE)

                if match_speed:
                    speed = match_speed.group(1)
                    if 'specs' not in item: item['specs'] = {}
                    # Add " MHz" for consistency if it's just a number
                    item['specs']['memory_speed'] = f"{speed} MHz"
                    print(f" SPEED: {speed}", end="")
                    updated_count += 1
                else:
                     print(f" NO SPEED FOUND", end="")
                
                # 3. Memory Type (Type Mémoire: DDR4 / DDR5)
                # Pattern: "Type Mémoire: DDR4" or "Type Mémoire : DDR5"
                match_type = re.search(r'Type Mémoire\s*:.*?(\bDDR\d\b)', html, re.IGNORECASE)
                if not match_type:
                    # Fallback: Check for "DDR4" or "DDR5" appearing in specs/header nicely
                     match_type = re.search(r'\b(DDR[45])\b', html, re.IGNORECASE)

                if match_type:
                    m_type = match_type.group(1).upper()
                    if 'specs' not in item: item['specs'] = {}
                    item['specs']['memory_type'] = m_type
                    print(f" TYPE: {m_type}", end="")
                    updated_count += 1

                # 4. Format (Case Size)
                # Pattern: "Format de Carte Mère: Micro ATX"
                match_fmt = re.search(r'Format de Carte Mère\s*:.*?(ATX|Micro\s*ATX|Mini\s*ITX|E-ATX|CEB|EE-ATX)', html, re.IGNORECASE)
                if not match_fmt:
                     # Fallback 
                     if re.search(r'\bMicro\s*ATX\b', html, re.IGNORECASE): match_fmt = re.search(r'(Micro\s*ATX)', html, re.IGNORECASE)
                     elif re.search(r'\bMini\s*ITX\b', html, re.IGNORECASE): match_fmt = re.search(r'(Mini\s*ITX)', html, re.IGNORECASE)
                     elif re.search(r'\bE-ATX\b', html, re.IGNORECASE): match_fmt = re.search(r'(E-ATX)', html, re.IGNORECASE)
                     elif re.search(r'\bATX\b', html, re.IGNORECASE): match_fmt = re.search(r'(ATX)', html, re.IGNORECASE)

                if match_fmt:
                    fmt = match_fmt.group(1).replace(" ", "-").upper() # Standardize Micro-ATX
                    if fmt == "MICRO–ATX": fmt = "MICRO-ATX"
                    if 'specs' not in item: item['specs'] = {}
                    item['specs']['format'] = fmt
                    print(f" FMT: {fmt}", end="")
                    updated_count += 1

                # 5. Slots (Nombre de Slots Supportés)
                # Pattern: "Nombre de Slots Supportés: 4 x DDR4 DIMM Slots" or "2 x DDR4"
                match_slots = re.search(r'Nombre de Slots Supportés\s*:.*?(\d)\s*x', html, re.IGNORECASE)
                if not match_slots:
                     # Fallback check for just number
                     match_slots = re.search(r'Nombre de Slots Supportés\s*:.*?(\d)', html, re.IGNORECASE)

                if match_slots:
                    slots = match_slots.group(1)
                    if 'specs' not in item: item['specs'] = {}
                    item['specs']['mb_slots'] = slots
                    print(f" SLOTS: {slots}", end="")
                    updated_count += 1

                # 6. Storage (Nbre de disque dur supporté)
                # Pattern: "Nbre de disque dur supporté: 4 x SATA 6Gb/s" or "1 emplacement"
                match_storage = re.search(r'Nbre de disque dur supporté\s*:.*?(.*)', html, re.IGNORECASE)
                
                if match_storage:
                    storage = match_storage.group(1).strip()
                    # Clean up HTML tags if any (robustness)
                    storage = re.sub(r'<[^>]+>', '', storage).strip()
                    
                    if 'specs' not in item: item['specs'] = {}
                    item['specs']['mb_storage'] = storage
                    print(f" STRG: {storage[:15]}...", end="")
                    updated_count += 1

                print("") # Newline
            else:
                print(f" FAILED (Status: {response.status_code})")

        except Exception as e:
            print(f" ERROR: {str(e)}")

        # Save periodically (every 10 items)
        if (i + 1) % 10 == 0:
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Saved progress ({i+1} items processed).")

    # Final Save
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Scraping complete. Updated {updated_count} items.")

if __name__ == "__main__":
    scrape_memory_capacity()
