import random
from django.core.management.base import BaseCommand
from products.models import Product, Price, Brand, Shop

class Command(BaseCommand):
    help = 'Fill database with realistic data, working images, and SMART SECTORS'

    def handle(self, *args, **kwargs):
        self.stdout.write("🧹 Clearing old data...")
        Price.objects.all().delete()
        Product.objects.all().delete()
        
        self.stdout.write("🏭 Starting Laptop Factory V3 (Smart Sectors)...")

        # 1. Create Shops
        shops = [
            {'name': 'MyTek', 'url': 'https://mytek.tn'},
            {'name': 'TunisiaNet', 'url': 'https://tunisianet.com.tn'},
            {'name': 'Wiki', 'url': 'https://wiki.tn'},
            {'name': 'Scoop', 'url': 'https://scoop.com.tn'},
        ]
        
        shop_objs = []
        for s in shops:
            shop, _ = Shop.objects.get_or_create(name=s['name'], defaults={'url': s['url']})
            shop_objs.append(shop)
        
        # 2. Define Options
        brands = ['Lenovo', 'HP', 'Dell', 'Asus', 'MSI', 'Acer']
        cpus = ['Intel i3', 'Intel i5', 'Intel i7', 'AMD Ryzen 5', 'AMD Ryzen 7']
        rams = ['8GB', '16GB', '32GB']
        storages = ['256GB SSD', '512GB SSD', '1TB SSD']
        screens = ['13.3 Inch', '14 Inch', '15.6 Inch', '17.3 Inch']
        
        # High Quality Images
        images = [
            "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500&q=80", # Silver
            "https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?w=500&q=80", # Dell
            "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=500&q=80", # White
            "https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=500&q=80", # Mac Style
            "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=500&q=80", # Gaming Style
        ]

        # 3. Generate 30 Laptops with Logic
        count = 0
        for i in range(30):
            brand_name = random.choice(brands)
            brand, _ = Brand.objects.get_or_create(name=brand_name)
            
            # Smart Model Names
            if brand_name == 'Asus':
                model = random.choice(['Vivobook', 'Zenbook', 'ROG Strix', 'TUF Gaming'])
            elif brand_name == 'Lenovo':
                model = random.choice(['IdeaPad', 'ThinkPad', 'Legion', 'Yoga'])
            elif brand_name == 'HP':
                model = random.choice(['Pavilion', 'Spectre', 'Omen', 'Victus'])
            elif brand_name == 'Dell':
                model = random.choice(['Inspiron', 'Vostro', 'XPS', 'Alienware'])
            else:
                model = random.choice(['Modern', 'Prestige', 'Katana', 'Stealth'])

            # --- SMART SECTOR LOGIC ---
            # If the name sounds like a gaming laptop, classify it as Gaming
            gaming_keywords = ['ROG', 'TUF', 'Legion', 'Omen', 'Victus', 'Alienware', 'Katana', 'Stealth']
            
            if model in gaming_keywords:
                sector = 'Gaming'
                cpu = 'Intel i7' # Gaming laptops usually have better CPUs
                ram = '16GB'
            else:
                sector = 'Office'
                cpu = random.choice(cpus)
                ram = random.choice(rams)
            # ---------------------------

            name = f"{brand_name} {model} - {cpu} / {ram}"
            
            product, created = Product.objects.get_or_create(
                name=name,
                defaults={
                    'brand': brand,
                    'sector': sector, # <--- Using our smart variable
                    'image_url': random.choice(images),
                    'cpu': cpu,
                    'ram': ram,
                    'storage': random.choice(storages),
                    'screen_size': random.choice(screens)
                }
            )

            # Prices
            base_price = 2500 if sector == 'Gaming' else 1200
            
            for _ in range(random.randint(1, 3)):
                shop = random.choice(shop_objs)
                final_price = base_price + random.randint(-200, 200)
                
                Price.objects.get_or_create(
                    product=product,
                    shop=shop,
                    defaults={'price': float(final_price), 'url': shop.url}
                )

            count += 1
            self.stdout.write(".", ending="")
            self.stdout.flush()

        print()
        self.stdout.write(self.style.SUCCESS(f"✅ Created {count} laptops (Gaming & Office mixed)!"))