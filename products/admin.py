from django.contrib import admin
from .models import Brand, Shop, Product, Price

class PriceInline(admin.TabularInline):
    model = Price
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'sector', 'cpu', 'ram', 'storage', 'gpu', 'gpu_brand', 'screen_size')
    list_filter = ('brand', 'sector', 'gpu_brand', 'cpu', 'ram', 'storage', 'gpu', 'screen_size')
    search_fields = ('name',)
    inlines = [PriceInline]

admin.site.register(Brand)
admin.site.register(Shop)
admin.site.register(Price)