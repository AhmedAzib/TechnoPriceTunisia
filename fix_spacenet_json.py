import json
import re

FILE = r"C:\Users\USER\Documents\programmation\frontend\src\data\spacenet_motherboards.json"

CHIPSET_SOCKET_MAP = {
    # Intel
    "Intel Z890": "LGA 1851", "Intel B860": "LGA 1851",
    "Intel Z790": "LGA 1700", "Intel B760": "LGA 1700", "Intel H770": "LGA 1700", "Intel H610": "LGA 1700",
    "Intel Z690": "LGA 1700", "Intel B660": "LGA 1700",
    "Intel H510": "LGA 1200", "Intel B560": "LGA 1200", "Intel Z590": "LGA 1200", "Intel H410": "LGA 1200", "Intel B460": "LGA 1200", "Intel Z490": "LGA 1200",
    "Intel H310": "LGA 1151", "Intel B360": "LGA 1151", "Intel Z390": "LGA 1151", "Intel Z370": "LGA 1151",
    "Intel H81": "LGA 1150", 
    "Intel G41": "LGA 775",
    
    # AMD
    "AMD X870": "AM5", "AMD B850": "AM5", "AMD B840": "AM5",
    "AMD X670": "AM5", "AMD B650": "AM5", "AMD A620": "AM5",
    "AMD X570": "AM4", "AMD B550": "AM4", "AMD A520": "AM4", "AMD B450": "AM4", "AMD A320": "AM4", "AMD X470": "AM4",
    "AMD sTRX4": "sTRX4"
}

def fix_data():
    try:
        with open(FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        fixed_count = 0
        for p in data:
            specs = p.get('specs', {})
            title = p.get('title', '').upper()
            chipset = specs.get('chipset')
            socket = specs.get('socket')
            
            # Rule 1.5: Fix Chipset based on Title (Priority over Description)
            # AMD
            if "A620" in title and chipset != "AMD A620":
                print(f"Fixing Chipset for {p['title']}: {chipset} -> AMD A620")
                specs['chipset'] = "AMD A620"
                chipset = "AMD A620"
            elif "B650" in title and chipset != "AMD B650":
                if "E" in title.split("B650")[1]: # distinct for B650E if needed, but let's stick to base
                    pass 
                print(f"Fixing Chipset for {p['title']}: {chipset} -> AMD B650")
                specs['chipset'] = "AMD B650"
                chipset = "AMD B650"
            elif "X670" in title and chipset != "AMD X670":
                print(f"Fixing Chipset for {p['title']}: {chipset} -> AMD X670")
                specs['chipset'] = "AMD X670"
                chipset = "AMD X670"
            elif "B550" in title and chipset != "AMD B550":
                specs['chipset'] = "AMD B550"
                chipset = "AMD B550"
            elif "A520" in title and chipset != "AMD A520":
                specs['chipset'] = "AMD A520"
                chipset = "AMD A520"
            
            # Intel
            if "H610" in title and chipset != "Intel H610":
                specs['chipset'] = "Intel H610"
                chipset = "Intel H610"
            elif "B760" in title and chipset != "Intel B760":
                specs['chipset'] = "Intel B760"
                chipset = "Intel B760"
            elif "Z790" in title and chipset != "Intel Z790":
                specs['chipset'] = "Intel Z790"
                chipset = "Intel Z790"
            elif "H510" in title and chipset != "Intel H510":
                specs['chipset'] = "Intel H510"
                chipset = "Intel H510"
            elif "H410" in title and chipset != "Intel H410":
                specs['chipset'] = "Intel H410"
                chipset = "Intel H410"

            # Rule 1: Enforce Socket based on Chipset
            if chipset in CHIPSET_SOCKET_MAP:
                expected_socket = CHIPSET_SOCKET_MAP[chipset]
                if socket != expected_socket:
                    print(f"Fixing Socket for {p['title']}: {socket} -> {expected_socket} (Based on Chipset {chipset})")
                    specs['socket'] = expected_socket
                    fixed_count += 1
            
            # Rule 2: Fix Brand based on Title
            if "MSI" in title and specs.get('brand') != "MSI":
                specs['brand'] = "MSI"
                fixed_count += 1
            elif "ASUS" in title and specs.get('brand') != "Asus":
                specs['brand'] = "Asus"
                fixed_count += 1
            elif ("GIGABYTE" in title or "GIGABITE" in title) and specs.get('brand') != "Gigabyte":
                specs['brand'] = "Gigabyte"
                pass # fixed_count handled generally
            elif "BIOSTAR" in title and specs.get('brand') != "Biostar":
                specs['brand'] = "Biostar"
                fixed_count += 1
            
            # Rule 3: DDR Type detection backup
            if specs.get('memory_type') == "Unknown":
                if "DDR5" in title: specs['memory_type'] = "DDR5"
                elif "DDR4" in title: specs['memory_type'] = "DDR4"
                elif "DDR3" in title: specs['memory_type'] = "DDR3"
            
            # Rule 4: Fix Form Factor for known series
            if specs.get('form_factor') == "Unknown":
                if "PROART" in title or "CREATOR" in title:
                     specs['form_factor'] = "ATX"
                     fixed_count += 1
                elif "GAMING PLUS" in title and "M" not in title.split("GAMING PLUS")[0][-5:]: 
                     # Heuristic: Gaming Plus without M prefix usually ATX? Risky.
                     # But Creator/ProArt are safe ATX.
                     pass 
            
            # Rule 5: Fix Stock Status to proper Case
            if p.get('status') == "En stock": p['status'] = "En Stock"

            p['specs'] = specs

        with open(FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"Fixed {fixed_count} issues. Saved to {FILE}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_data()
