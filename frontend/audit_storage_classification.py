import json
import re

FILE = 'src/data/mytek_motherboards.json'

# Copy of the Manual Map from ProductsPage.jsx (simplified for python)
MANUAL_MAP = {
    "Carte Mère MSI A520M-A PRO (911-7C96-044)": "5",
    "Carte Mère ASROCK B450M-HDV R4.0 (90-MXB9N0-A0UAYZ)": "5",
    "Carte Mère MSI B450M-A PRO MAX II (911-7C52-044)": "5",
    "Carte Mère MSI PRO H610M-E DDR4 (911-7D48-066)": "5",
    "Carte Mère MSI PRO H610M-E DDR4 (911-7D48-062)": "5",
    "CARTE MERE ASROCK H510M-H2/M.2 SE Micro ATX LGA 1200": "5",
    "CARTE MERE ASROCK H510M-HDV/M.2 Micro ATX LGA 1200 64 Go": "5",
    "Carte Mère BIOSTAR H510M 2.0 Micro ATX Socket LGA 1200": "5",
    "Carte Mère ASUS PRIME H510M-A R2.0 mATX LGA1200": "6",
    "Carte Mère ASROCK H810M-X Wi-Fi": "5",
    "Carte Mère MSI PRO H610M-G DDR5 (911-7D46-225)": "5",
    "Carte Mère ASUS PRIME H610M-K D4 ARGB (90MB1HN0-M0EAY0)": "5",
    "Carte Mère BIOSTAR H610MH D5 (H610MH-D5)": "5",
    "Carte Mère MSI A620M-E PRO (911-7E28-004)": "5",
    "Carte Mère ASROCK A620M-HDV/M.2 (90-MXBL30-A0UAYZ)": "6",
    "CARTE MERE GIGABYTE A620M S2H (GA-A620M-S2H)": "5",
    "Carte Mère ASUS PRIME A520M-R AM4 (90MB1H60-M0EAY0)": "5",
    "Carte Mère MSI B760M BOMBER WIFI (911-7D97-003)": "6",
    "Carte Mère ASROCK B650M-HDV/M.2 (90-MXBLA0-A0UAYZ)": "6",
    "Carte Mère ASUS Prime B760M-K": "6",
    "Carte Mère GIGABYTE A620M H (GBT-A620M-H)": "5",
    "Carte Mère GIGABYTE B760M GAMING (GBT-B760M-GAMING)": "6",
    "Carte Mère ASUS GAMING A620M-F WIFI AM5": "5",
    "Carte Mère Gigabyte B550M K (1.0) AM4 (GA-B550M-K)": "6",
    "Carte Mère MSI B550M PRO-VDH WIFI (911-7C95-006)": "6",
    "Carte Mère ASUS PRIME B550M-A WIFI II (90MB19T0-M0EAY0)": "6",
    "Carte Mère Gigabyte B760M DS3H AX DDR4 (GA-B760M-DS3H-AX-DDR4)": "6",
    "Carte Mère MSI PRO B760M-P DDR4 (911-7E02-003)": "6",
    "Carte Mère MSI PRO B760M-P DDR5 (911-7E02-030)": "6",
    "Carte Mère MSI PRO B760M-P DDR4 m-ATX (4711377030991)": "6",
    "Carte Mère ASROCK B650M PRO RS (90-MXBLP0-A0UAYZ)": "7",
    "Carte Mère ASUS TUF GAMING B550-PLUS WIFI II (90MB19U0-M0EAY0)": "8",
    "Carte Mère Gigabyte B760 GAMING X AX DDR4 (GA-B760-GAMINGX-AX-DDR4)": "7",
    "Carte Mère MSI PRO B760-P WIFI DDR4 (911-7D98-002)": "6",
    "Carte Mère GIGABYTE B650 GAMING X AX (GA-B650-GAMING-X-AX)": "7",
    "Carte Mère Asus TUF GAMING B650-PLUS WIFI (90MB1BY0-M0EAY0)": "7",
    "Carte Mère GIGABYTE B650 EAGLE AX (GA-B650-EAGLE-AX)": "7",
    "Carte Mère MSI B650 GAMING PLUS WIFI (911-7E26-001)": "6",
    "Carte Mère MSI MAG B650 TOMAHAWK WIFI (911-7D75-001)": "9",
    "Carte Mère ASUS Rog Strix B650-A Gaming Wifi (90MB1BP0-M0EAY0)": "7",
    "Carte Mère ASUS PRIME B650M-A WIFI II AM5 (90MB1EG0-M0EAY0)": "6",
    "Carte Mère MSI PRO Z790-P WIFI (911-7E06-001)": "10",
    "Carte Mère MSI PRO Z790-A MAX WIFI (911-7E07-005)": "10",
    "Carte Mère GIGABYTE Z790 EAGLE AX (GBT-Z790-EAGLEAX)": "7",
    "Carte Mère MSI Z790 GAMING PLUS WIFI (911-7E06-004)": "10",
    "Carte Mère ASROCK Z790 PG Lightning/D4 (90-MXB9W0-A0UAYZ)": "8",
    "Carte Mère GIGABYTE Z790 UD (Z790-UD)": "9",
    "Carte Mère MSI PRO Z890-P WIFI (911-7E34-001)": "8",
    "Carte Mère MSI Z890 GAMING PLUS WIFI (911-7E34-002)": "8",
    "Carte Mère MSI PRO X870-P WIFI (911-7E47-001)": "6",
    "Carte Mère MSI PRO X870E-P WIFI (911-7E70-002)": "7",
    "Carte Mère ASROCK X870 Pro RS WIFI (90-MXBQ00-A0UAYZ)": "7",
    "Carte Mère ASROCK X870 Steel Legend Wifi (90-MXBPJ0-A0UAYZ)": "7",
    "Carte Mère ASROCK B860 PRO RS WIFI": "7",
    "Carte Mère ASUS B840-PLUS WIFI AM5 (90MB1IZ0-M0EAY0)": "6",
    "Carte Mère ASUS PRIME B760M-A WIFI D4 (90MB1CX0-M1EAY0)": "6",
    "Carte Mère ASROCK B760 Pro RS (90-MXBKS0-A0UAYZ)": "7",
    "Carte Mère ASUS Prime B550M-K": "6",
    "Carte Mère ASUS TUF Gaming A620-PRO Wifi": "6",
    "Carte Mère GIGABYTE B550M K (GBT-B550M-K)": "6",
    "Carte Mère GIGABYTE B550M K Micro ATX": "6",
    "Carte Mère GIGABYTE B760M D3HP (GBT-B760M-D3HPD4)": "6",
    "Carte Mère GIGABYTE B850 EAGLE ICE (GBT-B850-EAGLEICE)": "7",
    "Carte Mère MSI B850 GAMING PLUS WIFI (911-7E56-001)": "7",
    "Carte Mère MSI PRO B840-P WIFI": "6",
    "Carte Mère MSI PRO B850-P WIFI (911-7E56-008)": "7",
    "Carte Mère MSI PRO B860-P (911-7E41-002)": "7"
}

def analyze():
    with open(FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("--- Items with Count <= 4 ---")
    
    count_low = 0
    count_map = {}

    for item in data:
        title = item.get('title', 'Unknown')
        specs = item.get('specs', {})
        storage_raw = specs.get('mb_storage', 'Unknown')
        
        final_val = 'Unknown'
        
        if title in MANUAL_MAP:
            final_val = MANUAL_MAP[title]
        elif storage_raw != 'Unknown':
             sataCount = 4
             m2Count = 1
             
             sataMatch = re.search(r'(\d+)\s*x?\s*(?:Connecteurs\s*)?SATA', storage_raw, re.IGNORECASE) or re.search(r'(\d+)\s*connecteurs\s*SATA', storage_raw, re.IGNORECASE)
             if sataMatch: sataCount = int(sataMatch.group(1))
             elif "4x SATA" in storage_raw: sataCount = 4
             elif "6x SATA" in storage_raw: sataCount = 6
             
             m2Match = re.search(r'(\d+)\s*x?\s*M\.2', storage_raw, re.IGNORECASE) or re.search(r'(\d+)\s*socket\s*M\.2', storage_raw, re.IGNORECASE) or re.search(r'(\d+)\s*Hyper\s*M\.2', storage_raw, re.IGNORECASE)
             if "1 hyper m.2" in storage_raw.lower() and ", 1 m.2" in storage_raw.lower(): m2Count = 2
             elif "1 hyper m.2" in storage_raw.lower() and ",1 m.2" in storage_raw.lower(): m2Count = 2
             elif m2Match: m2Count = int(m2Match.group(1))
             
             final_val = str(sataCount + m2Count)
        
        # Track counts
        if final_val not in count_map: count_map[final_val] = 0
        count_map[final_val] += 1

        try:
            val_int = int(final_val)
            if val_int <= 4:
                print(f"[{final_val}] {title}")
                print(f"    Raw: {storage_raw}")
                print(f"    Calculated: SATA={sataCount} + M.2={m2Count}")
                count_low += 1
        except:
            if final_val != 'Unknown':
               print(f"[NAN] {title} -> {final_val}")

    print(f"\nTotal items <= 4: {count_low}")
    print("\n--- Value Distribution ---")
    for k, v in sorted(count_map.items()):
        print(f"{k}: {v}")

if __name__ == "__main__":
    analyze()
