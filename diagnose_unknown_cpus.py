import json
import re
import os

# Paths to data files
BASE_DIR = r"c:\Users\USER\Documents\programmation\frontend\src\data"
FILES = [
    "tunisianet_clean.json",
    "spacenet_products.json",
    "mytek_test.json",
    "wiki_clean.json"
]

def load_data(filename):
    path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return []

def normalize_cpu_mock(title, specs):
    t = title.upper()
    cpu = specs.get('cpu', 'Unknown')
    if not cpu or cpu == 'Unknown' or len(cpu) < 3:
        # Apple M-Series
        if re.search(r'\b(M[1-9]\s?(PRO|MAX|ULTRA)?)\b', t):
             m_match = re.search(r'\b(M[1-9]\s?(PRO|MAX|ULTRA)?)\b', t)
             return f"Apple {m_match.group(1).replace(' ', ' ').strip()}"
        
        # Snapdragon
        if "SNAPDRAGON" in t: return "Snapdragon X"

        # Intel Core Ultra
        mid_match = re.search(r'\bULTRA\s?([579])\b', t)
        if mid_match: return f"Intel Core Ultra {mid_match.group(1)}"
        
        # Intel Core (New Gen)
        core_match = re.search(r'\bCORE\s?([3579])\b', t)
        if core_match and "I3" not in t and "I5" not in t and "I7" not in t:
             return f"Intel Core {core_match.group(1)}"
        
        # Implicit U-Series (e.g. U7-150U)
        u_match = re.search(r'\bU([3579])-\d{3}', t)
        if u_match: return f"Intel Core {u_match.group(1)}"
             
        # Intel N-Series
        if re.search(r'\bN\d{3,4}\b', t) or re.search(r'\bN95\b', t): return "Intel Processor N-Series"

        # Intel Core i-Series
        if re.search(r'\bI9\b', t): return "Intel Core i9"
        if re.search(r'\bI7\b', t): return "Intel Core i7"
        if re.search(r'\bI5\b', t): return "Intel Core i5"
        if re.search(r'\bI3\b', t): return "Intel Core i3"
        
        # AMD Ryzen AI
        if "RYZEN AI" in t or re.search(r'\bAI\s?9\b', t) or "RYZEN AL" in t:
            if "9" in t or "300" in t or "370" in t: return "Ryzen AI 9"
            elif "7" in t: return "Ryzen AI 7"
            elif "5" in t: return "Ryzen AI 5"
            else: return "Ryzen AI"
            
        # AMD Ryzen Standard (and Typos/Shortcodes)
        if re.search(r'RYZEN\s?9', t) or re.search(r'RAYZEN\s?9', t) or re.search(r'\bR9\b', t): return "Ryzen 9"
        if re.search(r'RYZEN\s?7', t) or re.search(r'RAYZEN\s?7', t) or re.search(r'\bR7\b', t): return "Ryzen 7"
        if re.search(r'RYZEN\s?5', t) or re.search(r'RAYZEN\s?5', t) or re.search(r'\bR5\b', t): return "Ryzen 5"
        if re.search(r'RYZEN\s?3', t) or re.search(r'RAYZEN\s?3', t) or re.search(r'\bR3\b', t): return "Ryzen 3"
        
        # Budget
        if re.search(r'\b3050U\b', t) or re.search(r'\b3020E\b', t) or "ATHLON" in t: return "Athlon"
        
        # Legacy
        if "CELERON" in t: return "Celeron"
        if "PENTIUM" in t: return "Pentium"
        if "ATOM" in t: return "Intel Atom"
        if "QUAD CORE" in t: return "Quad Core"
        if "DUAL CORE" in t: return "Dual Core"
        
        return "Unknown"
    
    # --- CPU Standardization (Force Merge) ---
    # Replicate the new JS logic
    if "INTEL" in cpu.upper():
        # Check for Core/Ultra/i followed by number
        standard_match = re.search(r'(?:CORE|ULTRA|I)\s?([3579])\b', cpu.upper())
        if standard_match:
             return f"Intel Core i{standard_match.group(1)}"

    if cpu == "Unknown": return "Unknown"
    return cpu

def main():
    unknowns = []
    total = 0
    
    for filename in FILES:
        data = load_data(filename)
        for p in data:
            total += 1
            title = p.get('name', p.get('title', ''))
            specs = p.get('specs', {})
            
            # Run the MOCK normalization
            cpu = normalize_cpu_mock(title, specs)
            
            if cpu == "Unknown":
                unknowns.append(title)

    print(f"Total Products: {total}")
    print(f"Total Unknown CPUs: {len(unknowns)}")
    print("-" * 30)
    print("Top 50 Unknown Titles:")
    
    # Count frequency of words in unknown titles to help identify patterns
    word_freq = {}
    
    for t in unknowns:
        try:
             print(t[:100])
        except UnicodeEncodeError:
             print(t[:100].encode('utf-8', errors='ignore'))
        
        # Simple word counter
        words = t.upper().split()
        for w in words:
            word_freq[w] = word_freq.get(w, 0) + 1
            
    print("-" * 30)
    print("Most Frequent Words in Unknown Titles (Potential Patterns):")
    sorted_freq = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    for w, count in sorted_freq[:30]:
        print(f"{w}: {count}")

if __name__ == "__main__":
    main()
