from rest_framework import serializers
from .models import User, Order, Product, OrderItem


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', )


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('price', 'name')


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = ('id', 'quantity', 'product', )


class OrderSerializer(serializers.ModelSerializer):
    customer = UserSerializer()
    picks = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ('id', 'customer', 'picks', )
