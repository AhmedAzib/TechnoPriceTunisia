import json
import re

# Load JSON
JSON_PATH = r"c:\Users\USER\Documents\programmation\frontend\src\data\mytek_mobiles.json"
# Note: The frontend imports MASTER_DATA. If that's a js file, I can't easily read it with python unless I parse it or look at the JSON source if available.
# The user said "frontend/src/data/mytek_mobiles.json" was the source in previous turns. I'll check that first.

def main():
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"File not found: {JSON_PATH}")
        return

    # Extract CPUs
    cpus = set()
    brands = set()
    
    for p in data:
        # Check if it looks like a computer
        title = p.get("title", "").lower()
        if "laptop" in title or "pc portable" in title:
            print(f"Potential Laptop found: {title}")
            
        specs = p.get("specs", {})
        cpu = specs.get("cpu", "Unknown")
        cpus.add(cpu)
        brands.add(p.get("brand", "Unknown"))
        
    print("\nUnique CPUs found:")
    for c in sorted(list(cpus)):
        print(f"  - {c}")

    print("\nUnique Brands found:")
    for b in sorted(list(brands)):
        print(f"  - {b}")

if __name__ == "__main__":
    main()
