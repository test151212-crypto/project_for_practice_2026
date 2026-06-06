from rest_framework import serializers
from .models import Category, Order

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.username', read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('customer', 'status', 'published_at', 'moderator', 'rejection_reason')
        extra_kwargs = {'files': {'required': False}}