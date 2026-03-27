import re

def clean_price(price_str):
    if not price_str:
        return 0.0
    # Clean string: remove spaces
    clean_str = price_str.replace('\xa0', '').replace(' ', '')
    
    # Handle Tunisian format: 1.200 or 1 200 = 1200. 1,200 = 1.2 (rare/wrong) or 1DT 200.
    # Usually dot is thousands, comma is decimal.
    # We remove dots (thousands separators)
    clean_str = clean_str.replace('.', '')
    # We replace comma with dot (decimal separator)
    clean_str = clean_str.replace(',', '.')
    
    # Extract number
    match = re.search(r'(\d+(\.\d+)?)', clean_str)
    if match:
        try:
            val = float(match.group(1))
            # Heuristic: If price is super low (e.g. 4.0 or 1.250) it's likely a formatting error
            # where thousands separator was treated as decimal.
            # Laptops are never < 200 DT.
            if 0 < val < 200:
                val *= 1000
            
            # safeguard for millimes input (e.g. 2000000 -> 2000)
            # Threshold: 50,000 TND (No laptop costs 50k, except errors)
            if val > 50000:
                val /= 1000
                
            return val
        except ValueError:
            return 0.0
    return 0.0

def clean_text(text):
    if not text:
        return ""
    return ' '.join(text.split())
