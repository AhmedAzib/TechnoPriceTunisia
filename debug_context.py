
keywords = ["TND", "DT", "price"]
import sys

with open("debug_selenium.html", "r", encoding="utf-8") as f:
    content = f.read()

for kw in keywords:
    print(f"--- Context for {kw} ---")
    idx = content.find(kw)
    if idx != -1:
        start = max(0, idx - 500)
        end = min(len(content), idx + 500)
        chunk = content[start:end]
        try:
             print(chunk)
        except UnicodeEncodeError:
             print(chunk.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding))
    else:
        print("Not found")
    print("\n")
