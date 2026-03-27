import json
import re

FILE = 'src/data/mytek_motherboards.json'

def audit():
    try:
        with open(FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    print("--- Current Slot Values in JSON ---")
    counts = {}
    details = []

    for item in data:
        title = item.get('title', 'Unknown')
        specs = item.get('specs', {})
        slots = specs.get('mb_slots', 'Unknown')
        
        # Track counts
        counts[slots] = counts.get(slots, 0) + 1
        
        # Track details for "1", "Unknown", or suspicious items
        # Also generally list them to see what's what
        details.append(f"[{slots}] {title}")

    print(f"Value Counts: {counts}")
    print("\n--- Detailed List ---")
    for d in sorted(details):
        print(d)

if __name__ == "__main__":
    audit()
