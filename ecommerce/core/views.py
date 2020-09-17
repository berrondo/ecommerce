from django.shortcuts import redirect, render
from django.views import generic
from django.http import HttpResponse
from rest_framework import viewsets
from .models import Product, Order, ProductOrder
from .serializers import OrderSerializer, ProductSerializer


class Shop(generic.View):
    def get(self, request, **kwargs):
        username = None
        if request.user.is_authenticated:
            username = request.user.username
        
        products = Product.objects.all()
        orders = list(Order.objects.filter(customer__username=username).all())
        try: order_id = orders[0].id
        except IndexError: order_id = 0
        return render(request, 'core/home.html', {
            'products': products, 
            'orders': orders,
            'order_id': order_id,
        })

    def post(self, request, **kwargs):
        compra = request.POST.dict()
        if compra.get('_method') == 'DELETE':
            return self.delete(request, **kwargs)

        ProductOrder.objects.create(
            order=Order.objects.get(id=compra['order_id']),
            product=Product.objects.get(id=compra['product_id']),
            quantity=compra['qtd'],
        )
        return redirect('index')

    def delete(self, request, **kwargs):
        compra = request.POST.dict()
        ProductOrder.objects.get(id=compra['pick_id']).delete()
        return redirect('index')


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


# class ProductOrderViewSet(viewsets.ModelViewSet):
#     queryset = ProductOrder.objects.all()
#     serializer_class = ProductOrderSerializer