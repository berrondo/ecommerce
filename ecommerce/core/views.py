from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
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
        'opened_order': get_opened_order(request),
        'msgs': msgs or [],
    }


def index(request):
    if user := get_user(request):
        if in_group(user, 'managers'):
            return redirect('product')
    return render(request, 'core/index.html', get_context(request))


class OrderView(generic.ListView):
    model = Order

    def get(self, request, *args, **kwargs):
        if user := user_in_group(request, 'customers'):
            self.queryset = Order.objects.filter(customer=user).all()
        elif not user_in_group(request, 'managers'):
            self.queryset = Order.objects.none()
        return super().get(request, args, kwargs)


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
                return render(request, 'core/index.html',
                              get_context(request, msgs=[e.message]))

        # managers...
        elif to_status == 'dispatched':
            order.status = Order.OrderStatus.SHIPPED
            order.save()
            return redirect('product')

        return redirect('index')


class OrderUpdateView(generic.View):
    def post(self, request, *args, **kwargs):
        if data := request.POST.dict():
            order = get_object_or_404(Order, pk=int(kwargs.get('pk', 0) or 0))
            quantity = int(data.get('quantity', 0))

            todo = data.get('todo', '')

            # customers...
            if todo == 'comprar':
                product_id = int(data.get('product_id', 0))
                product = Product.objects.get(id=product_id)

                try:
                    order.add_item(product, quantity)
                except ValidationError as e:
                    return render(request, 'core/index.html',
                                  get_context(request, msgs=[e.message]))

            # customers...
            elif todo == 'esvaziar carrinho':
                for item in order.items.all():
                    item.delete()

        return redirect('index')


class OrderItemUpdateView(generic.UpdateView):
    def post(self, request, *args, **kwargs):
        if data := request.POST.dict():
            order = get_object_or_404(Order, pk=kwargs.get('order_pk', 0))
            item = order.items.get(id=kwargs.get('item_pk', 0))

            quantity = int(data.get('quantity', 0))

            # customers...
            if not quantity:
                item.delete()

            # customers...
            else:
                item.quantity = quantity
                item.save()

        return redirect('index')


class OrderIndexDeleteView(generic.edit.DeleteView):
    model = Product


class ProductView(generic.ListView):
    model = Product

    def get(self, request, *args, **kwargs):
        ctx = get_context(request)
        for p in ctx['products']:
            p.form_ = ProductForm(instance=p)
        ctx['form'] = ProductForm()
        return render(request, 'core/managing.html', ctx)


class _ProductCrudMixin:
    model = Product
    fields = ['name', 'price']
    template_name = 'core/managing.html'
    success_url = reverse_lazy('product')


class ProductCreateView(_ProductCrudMixin, generic.edit.CreateView):
    ...


class ProductUpdateView(_ProductCrudMixin, generic.edit.UpdateView):
    ...


class ProductDeleteView(_ProductCrudMixin, generic.edit.DeleteView):
    ...


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


# class OrderItemViewSet(viewsets.ModelViewSet):
#     queryset = OrderItem.objects.all()
#     serializer_class = OrderItemSerializer
