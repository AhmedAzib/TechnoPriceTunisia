import re

def clean_price(price_str):
    if not price_str: return 0.0
    clean = re.sub(r'[^\d,]', '', price_str).replace(',', '.')
    try: return float(clean)
    except: return 0.0

def robust_clean_price(price_str):
    if not price_str: return 0.0
    # Replace comma with dot for easier regex matching of standard float format
    # But Tunisia uses comma for decimals usually.
    # Pattern: Look for digits, maybe dots/commas, then maybe decimals
    # Matches: 129,000 or 129.000 or 1 290,000
    
    # First, normalize spaces - removing ALL unicode whitespace variations if possible
    # specific fix for narrow non-breaking space \u202f
    s = price_str.replace(' ', '').replace(u'\xa0', '').replace(u'\u202f', '')
    
    # Regex to find the first valid price-like number
    # Supports: 123,456 or 123.456 or 123
    # We assume the price is the *first* number found if multiple exist
    match = re.search(r'(\d+(?:[.,]\d+)?)', s)
    if match:
        val_str = match.group(1)
        # Fix comma to dot
        val_str = val_str.replace(',', '.')
        # If multiple dots, e.g. 1.234.567, it's likely thousand separators.
        # But SpaceNet uses 129,000 DT (3 decimals) typically.
        # If we have 1.234, it might be 1234 or 1.234.
        # Let's assume standard float conversion after replacing , with .
        try:
            return float(val_str)
        except:
             return 0.0
    return 0.0

# Initial robust version that mimics the original logic but tries to be smarter?
# Actually, the original logic removes ALL non-digit/comma.
# If input is "209,000 DT\nHT: 175,000 DT", original: "209,000175,000" -> "209.000175.000" -> Fail.

cases = [
    ("209,000 DT", 209.0),
    ("209.000 DT", 209.0),
    ("1 209,000 DT", 1209.0),
    ("1\u202f039,000 DT", 1039.0), # Narrow non-breaking space
    ("209,000 DT\nHT: 175,000 DT", 209.0),
    ("0.000 DT", 0.0),
    ("", 0.0),
    ("En rupture", 0.0),
    ("209,000", 209.0)
]

print("--- Testing Original ---")
for inputs, expected in cases:
    try:
        res = clean_price(inputs)
        print(f"Input: {ascii(inputs)} -> Original: {res} (Expected: {expected}) - {'PASS' if res == expected else 'FAIL'}")
    except Exception as e:
        print(f"Input: {ascii(inputs)} -> Original Error: {e}")

print("\n--- Testing Robust ---")
for inputs, expected in cases:
    res = robust_clean_price(inputs)
    print(f"Input: {ascii(inputs)} -> Robust: {res} (Expected: {expected}) - {'PASS' if res == expected else 'FAIL'}")
