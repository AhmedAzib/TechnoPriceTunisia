import json
import os
import glob

def analyze_unknown_cpu():
    files = glob.glob("frontend/src/data/*.json")
    
    unknowns = []
    
    for path in files:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for p in data:
                # We need to apply logic similar to productUtils to see what ENDS UP as Unknown
                # But here we just check raw JSON or look for keywords
                
                # Check for desktop keywords in title
                t = (p.get('title') or p.get('name') or "").lower()
                
                # Loose check for "Unknown" based on user hint
                # Since we don't have the JS runtime here, we rely on the fact the user SEES them as Unknown.
                # But the JSON files might not have the normalized 'specs' yet if they are raw.
                # However, the user is looking at the App, so they see the result of `productUtils.js`.
                
                # Let's list items that look like Desktops
                keywords = [
                    "pc de bureau", "unité centrale", "all in one", "aio", 
                    "desktop", "tour", "sff", "optiplex", "thinkcentre", "prodesk", "elitedesk",
                    "ideacentre", "veriton", "esprimo", "vostro desktop", "inspiron desktop"
                ]
                
                is_desktop = any(k in t for k in keywords)
                
                if is_desktop:
                    unknowns.append(f"[DESKTOP-DETECTED] {t} ({os.path.basename(path)})")
                else:
                    # Also look for CPU models that are desktop only just in case
                    # raw specs might have it
                    pass

        except:
            pass
            
    # Also specifically look for "Unknown" if we can infer it, but better to dump the "Desktops" we found first
    return unknowns

found = analyze_unknown_cpu()
print(f"Found {len(found)} potential desktops.")
for x in found[:50]:
    print(x)
