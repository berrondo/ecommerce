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
            opened_orders = [user.get_opened_order()]
        elif user.is_manager():
            opened_orders = Order.objects.filter(status=Order.OrderStatus.TO_BE_SHIPPED).all()

    return {
        'products': Product.objects.all(),
        'opened_orders': opened_orders,
        'msgs': msgs or [],
    }


class Shop(generic.View):
    @staticmethod
    def get(request, **kwargs):
        if user := get_user(request):
            if user.is_manager():
                return redirect('managing')

        return render(request, 'core/index.html', context(request))

    @staticmethod
    def post(request, **kwargs):
        if compra := request.POST.dict():
            order = get_opened_order(request)
            item_id = int(compra.get('item_id', 0))
            item = order.items.get(id=item_id)
            quantity = int(compra.get('quantity', 0))

            todo = compra.get('todo', '') if quantity else 'excluir'

            if todo == 'alterar':
                item.quantity = quantity
                item.save()

            if todo == 'excluir':
                item.delete()

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

    @staticmethod
    def post(request, *args, **kwargs):
        if compra := request.POST.dict():
            todo = compra.get('todo', '')
            order = get_opened_order(request)

            if todo == 'comprar':
                product_id = int(compra.get('product_id', 0))
                quantity = int(compra.get('quantity', 0))
                product = Product.objects.get(id=product_id)

                try:
                    order.add_item(product, quantity)
                except ValidationError as e:
                    return render(request, 'core/index.html', context(request, msgs=[e.message]))

            elif todo == 'fechar pedido':
                try:
                    order.checkout()
                except ValidationError as e:
                    return render(request, 'core/index.html', context(request, msgs=[e.message]))

            elif todo == 'esvaziar carrinho':
                for item in order.items.all():
                    item.delete()

            elif todo == 'despachar':
                if order_id := int(compra.get('order_id', 0)):
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
