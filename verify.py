import os
import django

# 1. Connect to the Project
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from products.models import Product

print("📦 Opening the Vault to check inventory...")
print("-" * 50)

# 2. Ask the database for ALL products
all_products = Product.objects.all()

# 3. Print them out
if all_products.exists():
    for p in all_products:
        print(f"🔹 NAME:  {p.name}")
        print(f"💰 PRICE: {p.price} TND")
        print(f"🏪 SHOP:  {p.shop_name}")
        print("-" * 50)
    print(f"✅ Total Products found: {len(all_products)}")
else:
    print("⚠️ The Vault is empty!")