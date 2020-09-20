from django.shortcuts import redirect, render
from django.views import generic
from rest_framework import viewsets
from .models import User, Product, Order, OrderItem
from .serializers import OrderSerializer, ProductSerializer


class Shop(generic.View):
    def _context(self, request, msgs=None):
        username = None
        if request.user.is_authenticated:
            username = request.user.username

        if username:
            opened_order = list(Order.objects.filter(
                    customer__username=username,
                    status=Order.OrderStatus.OPENED,
                ).all())
        else:
            opened_order = [Order.objects.create()]

        try: order_id = opened_order[0].id
        except IndexError: order_id = 0
        return {
            'products': Product.objects.all(), 
            'orders': opened_order,
            'order_id': order_id,
            'msgs': msgs or [],
        }

    def get(self, request, **kwargs):
        return render(request, 'core/home.html', self._context(request))

    def post(self, request, **kwargs):
        compra = request.POST.dict()
        todo = compra.get('todo')
        
        if todo == 'excluir':
            return self._delete(compra)

        if todo == 'alterar':
            return self._patch(compra)

        order, created = Order.objects.get_or_create(id=compra['order_id'])
        if created:
            ...

        product = Product.objects.get(id=compra['product_id'])
        quantity = compra['quantity']

        order_item, created = OrderItem.objects.get_or_create(
            order=order,
            product=product,
            quantity=quantity,
        )
        if created:
            return redirect('index')
        else:
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