import json
import re

FILE = 'src/data/mytek_motherboards.json'

MANUAL_MAP = {
            "Carte Mère MSI A520M-A PRO (911-7C96-044)": "4 x SATA + 1 x M.2",
            "Carte Mère ASROCK B450M-HDV R4.0 (90-MXB9N0-A0UAYZ)": "4 x SATA + 1 x M.2",
            "Carte Mère MSI B450M-A PRO MAX II (911-7C52-044)": "4 x SATA + 1 x M.2",
            "Carte Mère MSI PRO H610M-E DDR4 (911-7D48-066)": "4 x SATA + 1 x M.2",
            "Carte Mère MSI PRO H610M-E DDR4 (911-7D48-062)": "4 x SATA + 1 x M.2",
            "CARTE MERE ASROCK H510M-H2/M.2 SE Micro ATX LGA 1200": "4 x SATA + 1 x M.2",
            "CARTE MERE ASROCK H510M-HDV/M.2 Micro ATX LGA 1200 64 Go": "4 x SATA + 1 x M.2",
            "Carte Mère BIOSTAR H510M 2.0 Micro ATX Socket LGA 1200": "4 x SATA + 1 x M.2",
            "Carte Mère ASUS PRIME H510M-A R2.0 mATX LGA1200": "4 x SATA + 2 x M.2", 
            "Carte Mère ASROCK H810M-X Wi-Fi": "4 x SATA + 1 x M.2",
            "Carte Mère MSI PRO H610M-G DDR5 (911-7D46-225)": "4 x SATA + 1 x M.2",
            "Carte Mère ASUS PRIME H610M-K D4 ARGB (90MB1HN0-M0EAY0)": "4 x SATA + 1 x M.2",
            "Carte Mère BIOSTAR H610MH D5 (H610MH-D5)": "4 x SATA + 1 x M.2",
            "Carte Mère MSI A620M-E PRO (911-7E28-004)": "4 x SATA + 1 x M.2",
            "Carte Mère ASROCK A620M-HDV/M.2 (90-MXBL30-A0UAYZ)": "4 x SATA + 2 x M.2",
            "CARTE MERE GIGABYTE A620M S2H (GA-A620M-S2H)": "4 x SATA + 1 x M.2",
            "Carte Mère ASUS PRIME A520M-R AM4 (90MB1H60-M0EAY0)": "4 x SATA + 1 x M.2",
            "Carte Mère MSI B760M BOMBER WIFI (911-7D97-003)": "4 x SATA + 2 x M.2",
            "Carte Mère ASROCK B650M-HDV/M.2 (90-MXBLA0-A0UAYZ)": "4 x SATA + 2 x M.2",
            "Carte Mère ASUS Prime B760M-K": "4 x SATA + 2 x M.2",
            "Carte Mère GIGABYTE A620M H (GBT-A620M-H)": "4 x SATA + 1 x M.2",
            "Carte Mère GIGABYTE B760M GAMING (GBT-B760M-GAMING)": "4 x SATA + 2 x M.2",
            "Carte Mère ASUS GAMING A620M-F WIFI AM5": "4 x SATA + 1 x M.2",
            
            "Carte Mère Gigabyte B550M K (1.0) AM4 (GA-B550M-K)": "4 x SATA + 2 x M.2",
            "Carte Mère MSI B550M PRO-VDH WIFI (911-7C95-006)": "4 x SATA + 2 x M.2",
            "Carte Mère ASUS PRIME B550M-A WIFI II (90MB19T0-M0EAY0)": "4 x SATA + 2 x M.2",
            "Carte Mère Gigabyte B760M DS3H AX DDR4 (GA-B760M-DS3H-AX-DDR4)": "4 x SATA + 2 x M.2",
            "Carte Mère MSI PRO B760M-P DDR4 (911-7E02-003)": "4 x SATA + 2 x M.2",
            "Carte Mère MSI PRO B760M-P DDR5 (911-7E02-030)": "4 x SATA + 2 x M.2",
            "Carte Mère MSI PRO B760M-P DDR4 m-ATX (4711377030991)": "4 x SATA + 2 x M.2",
            "Carte Mère ASROCK B650M PRO RS (90-MXBLP0-A0UAYZ)": "4 x SATA + 3 x M.2", 
            "Carte Mère ASUS TUF GAMING B550-PLUS WIFI II (90MB19U0-M0EAY0)": "6 x SATA + 2 x M.2", 
            "Carte Mère Gigabyte B760 GAMING X AX DDR4 (GA-B760-GAMINGX-AX-DDR4)": "4 x SATA + 3 x M.2",
            "Carte Mère MSI PRO B760-P WIFI DDR4 (911-7D98-002)": "4 x SATA + 2 x M.2",
            "Carte Mère GIGABYTE B650 GAMING X AX (GA-B650-GAMING-X-AX)": "4 x SATA + 3 x M.2",
            "Carte Mère Asus TUF GAMING B650-PLUS WIFI (90MB1BY0-M0EAY0)": "4 x SATA + 3 x M.2",
            "Carte Mère GIGABYTE B650 EAGLE AX (GA-B650-EAGLE-AX)": "4 x SATA + 3 x M.2",
            "Carte Mère MSI B650 GAMING PLUS WIFI (911-7E26-001)": "4 x SATA + 2 x M.2",
            "Carte Mère MSI MAG B650 TOMAHAWK WIFI (911-7D75-001)": "6 x SATA + 3 x M.2",
            "Carte Mère ASUS Rog Strix B650-A Gaming Wifi (90MB1BP0-M0EAY0)": "4 x SATA + 3 x M.2",

            "Carte Mère MSI PRO Z790-P WIFI (911-7E06-001)": "6 x SATA + 4 x M.2",
            "Carte Mère MSI PRO Z790-A MAX WIFI (911-7E07-005)": "6 x SATA + 4 x M.2",
            "Carte Mère GIGABYTE Z790 EAGLE AX (GBT-Z790-EAGLEAX)": "4 x SATA + 3 x M.2",
            "Carte Mère MSI Z790 GAMING PLUS WIFI (911-7E06-004)": "6 x SATA + 4 x M.2",
            "Carte Mère ASROCK Z790 PG Lightning/D4 (90-MXB9W0-A0UAYZ)": "4 x SATA + 4 x M.2",
            "Carte Mère GIGABYTE Z790 UD (Z790-UD)": "6 x SATA + 3 x M.2",
            "Carte Mère MSI PRO Z890-P WIFI (911-7E34-001)": "4 x SATA + 4 x M.2",
            "Carte Mère MSI Z890 GAMING PLUS WIFI (911-7E34-002)": "4 x SATA + 4 x M.2",
            "Carte Mère MSI PRO X870-P WIFI (911-7E47-001)": "4 x SATA + 2 x M.2",
            "Carte Mère MSI PRO X870E-P WIFI (911-7E70-002)": "4 x SATA + 3 x M.2",
            "Carte Mère ASROCK X870 Pro RS WIFI (90-MXBQ00-A0UAYZ)": "4 x SATA + 3 x M.2",
            "Carte Mère ASROCK X870 Steel Legend Wifi (90-MXBPJ0-A0UAYZ)": "4 x SATA + 3 x M.2",
            
            "Carte Mère ASROCK B860 PRO RS WIFI": "4 x SATA + 3 x M.2",
            "Carte Mère ASUS B840-PLUS WIFI AM5 (90MB1IZ0-M0EAY0)": "4 x SATA + 2 x M.2",
            "Carte Mère ASUS PRIME B760M-A WIFI D4 (90MB1CX0-M1EAY0)": "4 x SATA + 2 x M.2",
            "Carte Mère ASROCK B760 Pro RS (90-MXBKS0-A0UAYZ)": "4 x SATA + 3 x M.2",
            "Carte Mère ASUS Prime B550M-K": "4 x SATA + 2 x M.2",
            "Carte Mère ASUS TUF Gaming A620-PRO Wifi": "4 x SATA + 2 x M.2",
            "Carte Mère GIGABYTE B550M K (GBT-B550M-K)": "4 x SATA + 2 x M.2",
            "Carte Mère GIGABYTE B550M K Micro ATX": "4 x SATA + 2 x M.2",
            "Carte Mère GIGABYTE B760M D3HP (GBT-B760M-D3HPD4)": "4 x SATA + 2 x M.2",
            "Carte Mère GIGABYTE B850 EAGLE ICE (GBT-B850-EAGLEICE)": "4 x SATA + 3 x M.2",
            "Carte Mère MSI B850 GAMING PLUS WIFI (911-7E56-001)": "4 x SATA + 3 x M.2",
            "Carte Mère MSI PRO B840-P WIFI": "4 x SATA + 2 x M.2",
            "Carte Mère MSI PRO B850-P WIFI (911-7E56-008)": "4 x SATA + 3 x M.2",
            "Carte Mère MSI PRO B860-P (911-7E41-002)": "4 x SATA + 3 x M.2"
}

def check():
    try:
        with open(FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    results = []

    for item in data:
        title = item.get('title', 'Unknown')
        specs = item.get('specs', {})
        storage = specs.get('mb_storage', 'Unknown')
        
        final_val = 'Unknown'
        
        if title in MANUAL_MAP:
            final_val = MANUAL_MAP[title]
        elif storage != 'Unknown':
             sataCount = "4"
             m2Count = "1"
             
             # SATA
             sataMatch = re.search(r'(\d+)\s*x?\s*(?:Connecteurs\s*)?SATA', storage, re.IGNORECASE) or re.search(r'(\d+)\s*connecteurs\s*SATA', storage, re.IGNORECASE)
             if sataMatch: sataCount = sataMatch.group(1)
             elif "4x SATA" in storage: sataCount = "4"
             elif "6x SATA" in storage: sataCount = "6"
             
             # M.2
             m2Match = re.search(r'(\d+)\s*x?\s*M\.2', storage, re.IGNORECASE) or re.search(r'(\d+)\s*socket\s*M\.2', storage, re.IGNORECASE) or re.search(r'(\d+)\s*Hyper\s*M\.2', storage, re.IGNORECASE)
             
             if "1 hyper m.2" in storage.lower() and ", 1 m.2" in storage.lower(): m2Count = "2"
             elif "1 hyper m.2" in storage.lower() and ",1 m.2" in storage.lower(): m2Count = "2"
             elif "1 hyper m.2" in storage.lower() and "1 m.2" in storage.lower(): m2Count = "2" # Heuristic
             elif m2Match: m2Count = m2Match.group(1)
             
             final_val = f"{sataCount} x SATA + {m2Count} x M.2"
        
        if final_val == 'Unknown':
            print(f"UNKNOWN FOUND: {title}")
            
        results.append(f"{final_val}") # Just list values to see unique text

    print("--- Unique Final Values ---")
    vals = sorted(list(set(results)))
    for v in vals:
        print(v)

if __name__ == "__main__":
    check()
