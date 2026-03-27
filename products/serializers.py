from rest_framework import serializers
from .models import Product, Price, Brand, Shop, Wishlist

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = '__all__'

class PriceSerializer(serializers.ModelSerializer):
    shop = ShopSerializer()
    class Meta:
        model = Price
        fields = ['shop', 'price', 'url']

class ProductSerializer(serializers.ModelSerializer):
    brand = BrandSerializer()
    
    # 👇 FIXED: We removed "source='prices'" because Django figures it out automatically
    prices = PriceSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'brand', 'sector', 'image_url', 'prices', 'cpu', 'ram', 'storage', 'screen_size', 'gpu']

class WishlistSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product', read_only=True)
    
    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'product', 'product_details', 'created_at']
        read_only_fields = ['user', 'created_at', 'product_details']