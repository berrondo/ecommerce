from django.shortcuts import redirect, render
from django.views import generic
from django.http import HttpResponse
from django.db import transaction
from django.db.utils import IntegrityError
from rest_framework import viewsets
from .models import User, Product, Order, OrderItem
from .serializers import OrderSerializer, ProductSerializer


class Shop(generic.View):
    def _context(self, request, msgs=None):
        username = None
        customer = None
        if request.user.is_authenticated:
            username = request.user.username
            try: customer = User.objects.get_by_natural_key(username=username)
            except: ...

        products = Product.objects.all()
        orders = list(Order.objects.filter(
            customer__username=username,
            status=Order.OrderStatus.OPENED,
        ).all())

        try: order_id = orders[0].id
        except IndexError: order_id = 0

        ctx =  {
            'products': products, 
            'orders': orders,
            'order_id': order_id,
            'msgs': msgs or [],
        }
        return ctx

    def get(self, request, **kwargs):
        return render(request, 'core/home.html', self._context(request))

    def post(self, request, **kwargs):
        compra = request.POST.dict()
        
        if compra.get('todo') == 'excluir':
            return self._delete(compra)

        if compra.get('todo') == 'alterar':
            return self._patch(compra)

        try: order = Order.objects.get(id=compra['order_id'])
        except: order = Order.objects.create
        product = Product.objects.get(id=compra['product_id'])
        quantity = compra['quantity']
        try:
            with transaction.atomic():
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                )
                return redirect('index')

        except IntegrityError:
            return render(
                request, 
                'core/home.html', 
                self._context(request, msgs=[f"Já existe ({quantity}) {product.name} em seu pedido"])
            )

    def _delete(self, compra):
        OrderItem.objects.get(id=compra['pick_id']).delete()
        return redirect('index')

    def _patch(self, compra):
        quantity = compra['quantity']
        if quantity == '0':
            return self._delete(compra)
            
        pick = OrderItem.objects.get(id=compra['pick_id'])
        pick.quantity = quantity
        pick.save()
        return redirect('index')


def close(request):
    compra = request.POST.dict()
    todo = compra['todo']
    order = Order.objects.get(id=compra['order_id'])
    if todo == 'fechar pedido':
        order.checkout()
    elif todo == 'excluir pedido':
        order.delete()
    return redirect('index')


class OrderView(generic.ListView):
    model = Order


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


# class OrderItemViewSet(viewsets.ModelViewSet):
#     queryset = OrderItem.objects.all()
#     serializer_class = OrderItemSerializer