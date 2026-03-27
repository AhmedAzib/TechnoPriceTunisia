#!/usr/bin/env python3
"""
Fix missing motherboard specs in JSON data file.
10000% Safe - Direct data update.
"""

import json
import os

DATA_FILE = r"c:\Users\USER\Documents\programmation\frontend\src\data\mytek_motherboards.json"

# Manual fixes based on audit results
FIXES = {
    # SOCKET FIXES (1 item)
    "Carte Mère ASROCK H810M-X Wi-Fi": {"socket": "LGA 1851"},
    
    # MEMORY CAPACITY FIXES (9 items)
    "Carte Mère MSI A520M-A PRO (911-7C96-044)": {"memory_capacity": "64 Go"},
    "Carte Mère ASROCK B450M-HDV R4.0 (90-MXB9N0-A0UAYZ)": {"memory_capacity": "64 Go", "memory_speed": "3200 MHz"},
    "Carte Mère MSI PRO H610M-E DDR4 (911-7D48-066)": {"memory_capacity": "64 Go"},
    "Carte Mère MSI PRO H610M-E DDR4 (911-7D48-062)": {"memory_capacity": "64 Go"},
    "Carte Mère MSI PRO H610M-G DDR5 (911-7D46-225)": {"memory_capacity": "64 Go", "memory_speed": "5600 MHz"},
    "Carte Mère MSI PRO B760M-P DDR5 (911-7E02-030)": {"memory_capacity": "128 Go"},
    "Carte Mère ASROCK B650M-HDV/M.2 (90-MXBLA0-A0UAYZ)": {"memory_capacity": "128 Go", "memory_speed": "6400 MHz"},
    "Carte Mère ASROCK B760 Pro RS (90-MXBKS0-A0UAYZ)": {"memory_capacity": "192 Go", "memory_speed": "7200 MHz"},
    "Carte Mère MSI PRO X870E-P WIFI (911-7E70-002)": {"memory_capacity": "256 Go"},
    
    # MEMORY SPEED FIXES (12 items - some already included above)
    "Carte Mère MSI B450M-A PRO MAX II (911-7C52-044)": {"memory_speed": "4400 MHz"},
    "CARTE MERE ASROCK H510M-H2/M.2 SE Micro ATX LGA 1200": {"memory_speed": "3200 MHz"},
    "CARTE MERE ASROCK H510M-HDV/M.2 Micro ATX LGA 1200 64 Go": {"memory_speed": "3200 MHz"},
    "Carte Mère BIOSTAR H510M 2.0 Micro ATX Socket LGA 1200": {"memory_speed": "3200 MHz"},
    "Carte Mère ASUS PRIME H510M-A R2.0 mATX LGA1200": {"memory_speed": "3200 MHz"},
    "Carte Mère ASROCK Pro B550 Phantom Gaming 4 (90-MXBCY0-A0UAYZ)": {"memory_speed": "4533 MHz"},
    "Carte Mère ASROCK B860 PRO RS WIFI": {"memory_speed": "6400 MHz"},
}

# Load data
with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# Apply fixes
fixes_applied = 0
for item in data:
    title = item.get("title", "")
    if title in FIXES:
        for key, value in FIXES[title].items():
            if "specs" not in item:
                item["specs"] = {}
            old_val = item["specs"].get(key, "MISSING")
            item["specs"][key] = value
            print(f"[FIX] {title[:50]}... | {key}: {old_val} -> {value}")
            fixes_applied += 1

# Save updated data
with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\n=== COMPLETE: {fixes_applied} fixes applied ===")
