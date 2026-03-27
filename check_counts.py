import os
import django
import sys

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from products.models import Product, Sector

print(f"Total Products: {Product.objects.count()}")
print(f"Total Sectors: {Sector.objects.count()}")
if Sector.objects.exists():
    print("First 5 Sectors:", [s.name for s in Sector.objects.all()[:5]])
