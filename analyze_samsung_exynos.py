import json

# Load data - Using absolute path
path = 'c:/Users/USER/Documents/programmation/frontend/src/data/mytek_mobiles.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Analyzing Samsung Titles...")
count = 0
for p in data:
    t = p.get('title', '').strip()
    t_lower = t.lower()
    
    # Simulate valid Samsung detection
    is_samsung = ('galaxy' in t_lower) or ('samsung' in t_lower)
    
    if is_samsung:
        count += 1
        if count <= 50:
            print(f"- {t}")

print(f"\nTotal Samsungs found: {count}")
