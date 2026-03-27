
import os
import django
from django.db.models import Count

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from products.models import Product

print("--- Top 20 GPUs ---")
top_gpus = Product.objects.values('gpu').annotate(count=Count('gpu')).order_by('-count')[:20]
for x in top_gpus:
    print(f"{x['gpu']}: {x['count']}")
