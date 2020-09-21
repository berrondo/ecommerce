from django.shortcuts import redirect, render, get_object_or_404
from django.views import generic
from django.core.exceptions import ValidationError
from rest_framework import viewsets
from .models import User, Product, Order, OrderItem
from .serializers import OrderSerializer, ProductSerializer


def get_user(request):
    if request.user.is_authenticated:
        username = request.user.username
        user = get_object_or_404(User, username=username)
        return user


def get_opened_order(request):
    import pdb; pdb.set_trace()
    if user := get_user(request):
        return user.get_opened_order()


class Shop(generic.View):
  
    def _context(self, request, msgs=None):
        opened_order = []
        order_id = 0
        if user := get_user(request):
            opened_order = [user.get_opened_order()]
            order_id = opened_order[0].id

        return {
            'products': Product.objects.all(), 
            'orders': opened_order,
            'order_id': order_id,
            'msgs': msgs or [],
        }

    def get(self, request, **kwargs):
        if user := get_user(request):
            if user.is_manager():
                return redirect('managing')

        return render(request, 'core/index.html', self._context(request))

    def post(self, request, **kwargs):
        compra = request.POST.dict()
        todo = compra.get('todo')
        
        if todo == 'excluir':
            return self._delete(request, compra)

        if todo == 'alterar':
            return self._patch(request, compra)
        
        # if todo == 'comprar':
        return self._buy(request, compra)

        return redirect('index')

    def _buy(self, request, compra):
        order = get_opened_order(request)
        product = Product.objects.get(id=compra['product_id'])
        quantity = int(compra['quantity'])

        try:
            order.add_item(product, quantity)
            return redirect('index')

        except ValidationError as e:
            return render(
                request, 
                'core/index.html', 
                self._context(request, msgs=[e.message])
            )

    def _delete(self, request, compra):
        order = get_opened_order(request)
        item = order.picks.get(id=compra['pick_id'])
        item.delete()
        return redirect('index')

    def _patch(self, request, compra):
        quantity = compra['quantity']

        if quantity == '0':
            return self._delete(request, compra)
            
        order = get_opened_order(request)
        item = order.picks.get(id=compra['pick_id'])
        item.quantity = quantity
        item.save()
        return redirect('index')


def close(request):
    compra = request.POST.dict()
    todo = compra['todo']
    order = get_opened_order(request)

    try:
        if todo == 'fechar pedido':
            order.checkout()
        elif todo == 'excluir pedido':
            order.delete()
    except ValidationError as e:
        return redirect('index') #,msgs=[e.message])
    return redirect('index')


def managing(request):
    ctx = {
        'products': Product.objects.all(), 
        'msgs': [],
    }
    return render(request, 'core/managing.html', ctx)


class OrderView(generic.ListView):
    model = Order


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