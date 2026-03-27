import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()



from products.models import Product, Price

total = Product.objects.count()
cpu_na = Product.objects.filter(cpu="N/A").count()
ram_na = Product.objects.filter(ram="N/A").count()
storage_na = Product.objects.filter(storage="N/A").count()
screen_na = Product.objects.filter(screen_size="N/A").count()
gpu_na = Product.objects.filter(gpu="N/A").count()

print(f"Total Products: {total}")
print(f"Missing CPU: {cpu_na} ({cpu_na/total*100:.1f}%)")
print(f"Missing RAM: {ram_na} ({ram_na/total*100:.1f}%)")
print(f"Missing Storage: {storage_na} ({storage_na/total*100:.1f}%)")
print(f"Missing Screen: {screen_na} ({screen_na/total*100:.1f}%)")
print(f"Missing GPU: {gpu_na} ({gpu_na/total*100:.1f}%)")

print("\n--- Sample of Products with Missing CPU ---")
for p in Product.objects.filter(cpu="N/A")[:5]:
    print(f"[{p.id}] {p.name}")

