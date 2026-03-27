import json
import os

path = 'src/data/mytek_mobiles.json'
try:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(f"Count: {len(data)}")
except Exception as e:
    print(f"Error: {e}")
