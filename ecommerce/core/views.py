from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render, get_object_or_404
from django.views import generic
from rest_framework import viewsets

from .forms import ProductForm
from .models import Product, Order
from .serializers import OrderSerializer, ProductSerializer


def get_user(request):
    user = request.user
    if user.is_authenticated:
        username = request.user.username
        my_user = User.objects.filter(username=username).first()
        if my_user:
            user = my_user
    return user


def get_opened_order(request):
    if user := get_user(request):
        if hasattr(user, 'orders'):
            opened_order, _ = Order.objects.get_or_create(
                customer=user,
                status=Order.OrderStatus.OPENED)
            return opened_order


def get_orders(request, user):
    if in_group(user, 'customers'):
        return [get_opened_order(request)]
    elif in_group(user, 'managers'):
        return Order.objects.filter(status=Order.OrderStatus.TO_BE_SHIPPED).all()
    return []


def in_group(user, group_name):
    if hasattr(user, 'groups'):
        return user.groups.filter(name=group_name).exists()


def user_in_group(request, group_name):
    user = get_user(request)
    if in_group(user, group_name):
        return user
    return False


def get_context(request, msgs=None):
    return {
        'products': Product.objects.all(),
        'orders': get_orders(request, get_user(request)),
        'msgs': msgs or [],
    }


class IndexView(generic.View):
    def get(self, request, **kwargs):
        if user := get_user(request):
            if in_group(user, 'managers'):
                return redirect('products')
        return render(request, 'core/index.html', get_context(request))

    def post(self, request, *args, **kwargs):
        if data := request.POST.dict():
            order = get_opened_order(request)
            item_id = int(data.get('item_id', 0))
            item = order.items.get(id=item_id)
            quantity = int(data.get('quantity', 0))

            todo = data.get('todo', '') if quantity else 'excluir'

            # customers...
            if todo == 'alterar':
                item.quantity = quantity
                item.save()

            # customers...
            if todo == 'excluir':
                item.delete()

        return redirect('index')


class OrderStatusView(generic.View):
    model = Order

    def post(self, request, *args, **kwargs):
        to_status = kwargs.get('to_status')
        order = get_object_or_404(Order, pk=kwargs.get('pk'))

        # customers...
        if to_status == 'pending':
            try:
                order.checkout()
            except ValidationError as e:
                return render(request, 'core/index.html', get_context(request, msgs=[e.message]))

        # managers...
        elif to_status == 'dispatched':
            order.status = Order.OrderStatus.SHIPPED
            order.save()
            return redirect('products')

        return redirect('index')


class OrderView(generic.ListView):
    model = Order

    def get(self, request, *args, **kwargs):
        if user := user_in_group(request, 'customers'):
            self.queryset = Order.objects.filter(customer=user).all()
        elif not user_in_group(request, 'managers'):
            self.queryset = Order.objects.none()
        return super().get(request, args, kwargs)

    @staticmethod
    def post(request, *args, **kwargs):
        if data := request.POST.dict():
            todo = data.get('todo', '')
            order = get_opened_order(request)

            if order:
                # customers...
                if todo == 'comprar':
                    product_id = int(data.get('product_id', 0))
                    quantity = int(data.get('quantity', 0))
                    product = Product.objects.get(id=product_id)

                    try:
                        order.add_item(product, quantity)
                    except ValidationError as e:
                        return render(request, 'core/index.html', get_context(request, msgs=[e.message]))

                # customers...
                elif todo == 'esvaziar carrinho':
                    for item in order.items.all():
                        item.delete()

        return redirect('index')


class ProductView(generic.ListView):
    model = Product

    def get(self, request, *args, **kwargs):
        ctx = get_context(request)
        for p in ctx['products']:
            p.form_ = ProductForm(instance=p)
        ctx['form'] = ProductForm()
        return render(request, 'core/managing.html', ctx)

    def post(self, request, *args, **kwargs):
        if data := request.POST.dict():
            form = ProductForm(request.POST)
            todo = data.get('todo', '')

            # managers...
            if todo == 'cadastrar':
                if form.is_valid():
                    form.save()

            # managers...
            if todo == 'alterar':
                product_id = int(data.get('product_id', 0) or 0)
                product = self.model.objects.get(id=product_id)
                form.instance = product
                if form.is_valid():
                    form.save()

            # managers...
            if todo == 'excluir':
                product_id = int(data.get('product_id', 0) or 0)
                product = self.model.objects.get(id=product_id)
                product.delete()

        return redirect('products')


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


# class OrderItemViewSet(viewsets.ModelViewSet):
#     queryset = OrderItem.objects.all()
#     serializer_class = OrderItemSerializer
