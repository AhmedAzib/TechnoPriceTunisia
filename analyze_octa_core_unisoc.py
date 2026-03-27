import json

path = 'c:/Users/USER/Documents/programmation/frontend/src/data/tunisianet_mobiles.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Analyzing Octa Core phones from Tunisianet...")
count = 0
candidates = []

for p in data:
    source = p.get('source', '')
    specs = p.get('specs', {})
    cpu = specs.get('cpu', 'Unknown')
    title = p.get('title', '').lower()
    
    # Filter for Tunisianet and Octa Core (or Unknown/Others which might hide them)
    if 'tunisianet' in source.lower() and (cpu == 'Octa Core' or cpu == 'Unknown' or cpu == 'Others'):
        # Check for potential Unisoc hints in title or just list them to inspect
        candidates.append(p['title'])

print(f"Total pure Octa Core/Unknown candidates from Tunisianet: {len(candidates)}")
print("Sample Candidates:")
for c in candidates[:50]:
    print(c)
