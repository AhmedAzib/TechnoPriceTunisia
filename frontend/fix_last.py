#!/usr/bin/env python3
"""Fix remaining missing memory_speed for H810M-X Wi-Fi"""
import json

DATA_FILE = r"c:\Users\USER\Documents\programmation\frontend\src\data\mytek_motherboards.json"

with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    if "H810M-X Wi-Fi" in item.get("title", ""):
        item["specs"]["memory_speed"] = "6400 MHz"
        print(f"[FIX] {item['title']} -> memory_speed: 6400 MHz")
        break

with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("DONE!")
