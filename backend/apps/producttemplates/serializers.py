# apps/product/serializers.py
from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        # Hiển thị tất cả các trường, bao gồm cả 'info'
        fields = '__all__'