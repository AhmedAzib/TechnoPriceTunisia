def infer_battery(title, category, raw_spec_battery):
    # Logic pasted from MobilesPage.jsx
    t = title.lower()
    specs = {"battery": raw_spec_battery}
    
    # 1. Determine raw value (from Specs or Title)
    rawBattery = -1;
    if (specs['battery'] and specs['battery'] != "Unknown"):
        # simple parse
        import re
        match = re.search(r'(\d+)', specs['battery'])
        if match: rawBattery = int(match.group(1))
    else:
        # Try title regex
        import re
        match = re.search(r'(\d+)\s*mah', t)
        if match: rawBattery = int(match.group(1))

    # 2. Override based on known models (Dictionary)
    inferredBucket = None

    if ('tecno pova' in t) or ('galaxy m' in t) or ('pova neo' in t) or ('7000' in t):
        if ('pova 2' in t) or ('pova 3' in t) or ('7000' in t): inferredBucket = "7000 mAh"
        else: inferredBucket = "6000 mAh"
    
    elif ('honor x7a' in t) or ('honor x7b' in t) or ('c30' in t): inferredBucket = "6000 mAh"
    elif ('iphone 16 pro max' in t) or ('iphone 15 pro max' in t) or ('iphone 14 pro max' in t): inferredBucket = "4000 mAh"
    # ... condensed ...
    
    # Low End / Feature Phones overrides
    elif ('nokia' in t) or (category == 'Feature Phone') or ('feature' in t): inferredBucket = "2000 mAh"
    elif ('lesia' in t) or ('benco' in t) or ('itel a' in t) or ('itel p3' in t): inferredBucket = "2000 mAh" # <--- Tested Line

    # 3. Bucketize Raw Value
    if (not inferredBucket and rawBattery > 0):
        if (rawBattery < 3000): inferredBucket = "2000 mAh"
        elif (rawBattery < 4000): inferredBucket = "3000 mAh"
        elif (rawBattery < 5000): inferredBucket = "4000 mAh"
        elif (rawBattery < 6000): inferredBucket = "5000 mAh"
        elif (rawBattery < 7000): inferredBucket = "6000 mAh"
        else: inferredBucket = "7000 mAh"

    # 4. Defaults
    if not inferredBucket:
        if 'iphone' in t: inferredBucket = "3000 mAh"
        else: inferredBucket = "5000 mAh"

    return inferredBucket

print("Testing Lesia Young 1...")
res = infer_battery("Smartphone LESIA YOUNG 1 2Go 16Go - Bleu Fonc", "Smartphone", "Unknown")
print(f"Result: {res}")

print("\nTesting Lesia Young with 2500mAh in title...")
res2 = infer_battery("Smartphone LESIA YOUNG 1 (2500mAh) - Test", "Smartphone", "Unknown")
print(f"Result: {res2}")
