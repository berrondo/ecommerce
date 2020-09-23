from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render, get_object_or_404
from django.views import generic
from rest_framework import viewsets

from .models import User, Product, Order
from .serializers import OrderSerializer, ProductSerializer


def get_user(request):
    if request.user.is_authenticated:
        username = request.user.username
        user = get_object_or_404(User, username=username)
        return user


def get_opened_order(request):
    if user := get_user(request):
        return user.get_opened_order()


def context(request, msgs=None):
    opened_orders = []
    if user := get_user(request):
        if user.is_customer():
            opened_orders = user.get_opened_order()
        elif user.is_manager():
            opened_orders = Order.objects.filter(status=Order.OrderStatus.TO_BE_SHIPPED).all()

    return {
        'products': Product.objects.all(),
        'opened_orders': opened_orders,
        'msgs': msgs or [],
    }


class Shop(generic.View):
    def get(self, request, **kwargs):
        if user := get_user(request):
            if user.is_manager():
                return redirect('managing')

        return render(request, 'core/index.html', context(request))

    def post(self, request, **kwargs):
        compra = request.POST.dict()
        todo = compra.get('todo')
        
        if todo == 'excluir':
            return self._delete(request, compra)

        if todo == 'alterar':
            return self._patch(request, compra)

        return redirect('index')

    def _delete(self, request, compra):
        order = get_opened_order(request)[0]
        item = order.picks.get(id=compra['pick_id'])
        item.delete()
        return redirect('index')

    def _patch(self, request, compra):
        quantity = compra['quantity']

        if quantity == '0':
            return self._delete(request, compra)
            
        order = get_opened_order(request)[0]
        item = order.picks.get(id=compra['pick_id'])
        item.quantity = quantity
        item.save()
        return redirect('index')


def managing(request):
    return render(request, 'core/managing.html', context(request))


class OrderView(generic.ListView):
    model = Order

    def get(self, request, *args, **kwargs):
        user = get_user(request)
        if user.is_customer():
            self.queryset = Order.objects.filter(customer=user).all()
        return super().get(request, args, kwargs)

    def post(self, request, *args, **kwargs):
        compra = request.POST.dict()
        todo = compra['todo']
        order = get_opened_order(request)[0]

        if todo == 'comprar':
            product = Product.objects.get(id=compra['product_id'])
            quantity = int(compra['quantity'])

            try:
                order.add_item(product, quantity)
            except ValidationError as e:
                return render(request, 'core/index.html', context(request, msgs=[e.message]))

        elif todo == 'fechar pedido':
            try:
                order.checkout()
            except ValidationError as e:
                return render(request, 'core/index.html', context(request, msgs=[e.message]))

        elif todo == 'excluir pedido':
            for item in order.picks.all():
                item.delete()

        elif todo == 'despachar':
            order_id = compra['order_id']
            order = Order.objects.get(id=order_id)
            order.status = Order.OrderStatus.SHIPPED
            order.save()
            return render(request, 'core/managing.html', context(request))

        return redirect('index')


class ProductView(generic.ListView):
    model = Product


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


# class OrderItemViewSet(viewsets.ModelViewSet):
#     queryset = OrderItem.objects.all()
#     serializer_class = OrderItemSerializer
