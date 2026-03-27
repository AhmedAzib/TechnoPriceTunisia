
import os
import django
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from products.models import Product

p = Product.objects.get(id=108)
if not p:
    print("Product 108 not found.")
    exit()

print(f"Testing Product: {p.name}")
name_lower = p.name.lower()
print(f"Lower Name: {name_lower}")
print(f"Current CPU: {p.cpu}")


cpu = "N/A"

# Mimic the logic tree
if 'apple' in name_lower:
    print("Hit Apple")
elif 'core' in name_lower and any(x in name_lower for x in [' 3 ', ' 5 ', ' 7 ', 'ultra']):
    print("Hit Core Ultra")
elif re.search(r'\b(n[1-9]\d{1,3})\b', name_lower):
    print("Hit N-Series")
    n_match = re.search(r'\b(n[1-9]\d{1,3})\b', name_lower)
    cpu = f"Intel {n_match.group(1).upper()}"
elif 'intel' in name_lower:
    print("Hit Generic Intel")
    if 'celeron' in name_lower: cpu = "Intel Celeron"
    # ...

print(f"Result CPU: {cpu}")
