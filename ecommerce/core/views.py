from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse
from rest_framework import viewsets
from .models import Product, Order, ProductOrder
from .serializers import OrderSerializer, ProductSerializer, ProductOrderSerializer


def home(request):
    username = None
    if request.user.is_authenticated:
        username = request.user.username
    
    products = Product.objects.all()
    orders = list(Order.objects.filter(customer__username=username).all())
    return render(request, 'core/home.html', {'products': products, 'orders': orders})


class Comprar(generic.View):
    def get(self, request, **kwargs):
        return HttpResponse(str(kwargs))


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


# class ProductViewSet(viewsets.ModelViewSet):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer


# class ProductOrderViewSet(viewsets.ModelViewSet):
#     queryset = ProductOrder.objects.all()
#     serializer_class = ProductOrderSerializer