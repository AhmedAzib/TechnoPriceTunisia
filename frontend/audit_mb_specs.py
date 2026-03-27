#!/usr/bin/env python3
"""Audit motherboard specs for missing socket, memory_capacity, memory_speed values."""

import json
import os

DATA_DIR = r"c:\Users\USER\Documents\programmation\frontend\src\data"

# All motherboard JSON files
MB_FILES = [
    "mytek_motherboards.json",
    "tunisianet_motherboards.json",
    "spacenet_motherboards.json",
]

missing_socket = []
missing_capacity = []
missing_speed = []

for filename in MB_FILES:
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        print(f"[SKIP] {filename} not found")
        continue
    
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print(f"\n=== {filename} ({len(data)} items) ===")
    
    for item in data:
        title = item.get("title", "NO TITLE")
        specs = item.get("specs", {})
        
        socket = specs.get("socket", "")
        mem_cap = specs.get("memory_capacity", "")
        mem_speed = specs.get("memory_speed", "")
        
        if not socket or socket == "Unknown":
            missing_socket.append(title)
        if not mem_cap or mem_cap == "Unknown":
            missing_capacity.append(title)
        if not mem_speed or mem_speed == "Unknown":
            missing_speed.append(title)

print("\n" + "="*60)
print(f"MISSING SOCKET ({len(missing_socket)} items):")
for t in missing_socket:
    print(f"  - {t}")

print(f"\nMISSING MEMORY_CAPACITY ({len(missing_capacity)} items):")
for t in missing_capacity:
    print(f"  - {t}")

print(f"\nMISSING MEMORY_SPEED ({len(missing_speed)} items):")
for t in missing_speed:
    print(f"  - {t}")
