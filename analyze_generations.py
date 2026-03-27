import json
from collections import Counter

file_path = r'C:\Users\USER\Documents\programmation\frontend\src\data\tunisianet_processors.json'

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

counts = Counter()
missed = []
valid_gens = [
    "Core Ultra (Series 2)", "Core Ultra (Series 1)", 
    "14th Gen", "13th Gen", "12th Gen", "11th Gen", "10th Gen",
    "Ryzen 9000 Series", "Ryzen 8000 Series", "Ryzen 7000 Series", 
    "Ryzen 5000 Series", "Ryzen 4000 Series", "Ryzen 3000 Series"
]

for p in data:
    gen = p.get('specs', {}).get('generation', 'Unknown')
    counts[gen] += 1
    if gen not in valid_gens:
        missed.append((p['title'], gen))

print("Distribution:")
for g, c in counts.items():
    print(f"{g}: {c}")

print("\nMissed Items (Not in User List):")
for title, gen in missed:
    print(f"[{gen}] {title}")
