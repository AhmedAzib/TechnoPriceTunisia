from django.db import models
from django.contrib.auth.models import User

class Sector(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(blank=True, null=True)

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class Shop(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField(blank=True)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    link = models.URLField(unique=True, null=True, blank=True) # Added to match user request, though Price model handles scraping links
    image_url = models.URLField(blank=True, null=True)
    
    # Foreign Keys
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, null=True, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True, blank=True)
    
    # Specs (legacy detailed fields kept for scraper)
    cpu = models.CharField(max_length=100, blank=True, null=True, verbose_name="Processor")
    ram = models.CharField(max_length=50, blank=True, null=True, verbose_name="RAM Memory")
    storage = models.CharField(max_length=50, blank=True, null=True, verbose_name="Storage")
    screen_size = models.CharField(max_length=50, blank=True, null=True, verbose_name="Screen Size")
    gpu = models.CharField(max_length=50, blank=True, null=True, verbose_name="Graphics Card")
    gpu_brand = models.CharField(max_length=50, blank=True, null=True, verbose_name="GPU Brand")
    
    # Advanced Specs
    refresh_rate = models.CharField(max_length=50, blank=True, null=True, verbose_name="Refresh Rate")
    resolution = models.CharField(max_length=50, blank=True, null=True, verbose_name="Resolution")
    os = models.CharField(max_length=100, blank=True, null=True, verbose_name="OS")
    ports = models.TextField(blank=True, null=True, verbose_name="Ports")
    panel_type = models.CharField(max_length=50, blank=True, null=True, verbose_name="Panel Type")
    
    # General specs text fallback
    specs = models.TextField(blank=True, null=True)
    
    # Current Price shortcut
    current_price = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.name

class Price(models.Model):
    product = models.ForeignKey(Product, related_name='prices', on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=3)
    url = models.URLField()

    def __str__(self):
        return f"{self.price} for {self.product.name} at {self.shop.name}"

class PriceHistory(models.Model):
    product = models.ForeignKey(Product, related_name='history', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=3)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.price}"

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} likes {self.product.name}"