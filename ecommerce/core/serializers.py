from rest_framework import serializers
from .models import Order, Product, ProductOrder


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('price', 'name')


class ProductOrderSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = ProductOrder
        fields = ('id', 'quantity', 'product', )


class OrderSerializer(serializers.ModelSerializer):
    picks = ProductOrderSerializer(many=True)
    class Meta:
        model = Order
        fields = ('id', 'customer', 'picks', )
