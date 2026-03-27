import json

# Load data - Using absolute path
path = 'c:/Users/USER/Documents/programmation/frontend/src/data/mytek_mobiles.json' # This is likely normalized by now if I saved it? No, raw JSON isn't normalized by the React app.
# I need to simulate the React logic OR checking the raw data won't help if the logic is in JS.
# But I can check the TITLES of the things I targeted.
# My JS logic targeted: lesia, logicom, iku, zte a, itel a, itel s18, realme note, smart 10, spark go, redmi a, tcl, honor play.

print("Checking potential False Positives in Unisoc Logic...")

# I will just list titles matching the 'risky' keywords and their raw specs if available
risky_keywords = ['tcl', 'honor play', 'zte', 'itel', 'realme note', 'spark go', 'smart 10']

with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for p in data:
    t = p.get('title', '').lower()
    for k in risky_keywords:
        if k in t:
            print(f"[{k.upper()}] {p['title']} | RawCPU: {p.get('specs',{}).get('cpu')}")
