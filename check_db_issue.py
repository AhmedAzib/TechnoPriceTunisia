import os
import django
import sys

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from products.models import Product, Sector

def run_check():
    print("--- Checking Sectors ---")
    sectors = Sector.objects.all()
    for s in sectors:
        count = Product.objects.filter(sector=s).count()
        print(f"Sector: '{s.name}' (ID: {s.id}) - Product Count: {count}")

    print("\n--- Checking Products with 'Spacenet' in Source/Name ---")
    # Assuming user might mean 'source' or implied source. 
    # But since we suspect Sector filter, let's see products that SHOULD be Spacenet.
    # Looking for products with 'Spacenet' in link or title if source field is not on model (Model only has 'sector' and 'brand')
    # Wait, model definition I saw earlier:
    # class Product(models.Model):
    #     ...
    #     sector = ForeignKey...
    #     brand = ForeignKey...
    #     (No 'source' field in Product model! The JSON has 'source', but model doesn't seem to have it unless I missed it)
    
    spacenet_products = Product.objects.filter(link__icontains="spacenet")
    print(f"Products with 'spacenet' in link: {spacenet_products.count()}")
    
    if spacenet_products.exists():
        first = spacenet_products.first()
        print(f"Sample Spacenet Product: {first.name}")
        print(f"  Sector: {first.sector} (ID: {first.sector.id if first.sector else 'None'})")
        print(f"  Brand: {first.brand}")

    print("\n--- Checking Filter Behavior ---")
    # Simulate the query user is doing
    try:
        from products.views import ProductFilter
        # The filter set uses 'sector' field.
        # If I filter by sector ID it should work.
        # If I filter by sector NAME it might fail if not configured.
        
        # Find Spacenet Sector
        sn_sector = Sector.objects.filter(name__iexact="Spacenet").first()
        if sn_sector:
            qs = Product.objects.all()
            # Test filter with ID
            f_id = ProductFilter(data={'sector': sn_sector.id}, queryset=qs)
            print(f"Filter by ID ({sn_sector.id}): Valid? {f_id.is_valid()} - Count: {f_id.qs.count()}")
            
            # Test filter with Name (what frontend likely sends if it sends string)
            f_name = ProductFilter(data={'sector': "Spacenet"}, queryset=qs)
            print(f"Filter by Name ('Spacenet'): Valid? {f_name.is_valid()} - Count: {f_name.qs.count()}")
            if not f_name.is_valid():
                print(f"  Errors: {f_name.errors}")
        else:
            print("Sector 'Spacenet' not found in DB.")

    except Exception as e:
        print(f"Filter check error: {e}")

if __name__ == "__main__":
    run_check()
