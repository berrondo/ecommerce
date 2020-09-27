from django.contrib.auth.mixins import LoginRequiredMixin
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
    opened_order = Order.objects.none()
    if user := get_user(request):
        if hasattr(user, 'orders'):
            opened_order, _ = Order.objects.get_or_create(
                customer=user,
                status=Order.OrderStatus.OPENED)
    return opened_order


def in_group(user, group_name):
    if hasattr(user, 'groups'):
        return user.groups.filter(name=group_name).exists()


def get_customer_context(request):
    opened_order = get_opened_order(request)
    context = {
        'products': Product.objects.all(),
        'orders': [opened_order],
        'opened_order': opened_order,
        'msgs': [],
    }
    return context


def index(request):
    if user := get_user(request):
        if in_group(user, 'managers'):
            return redirect('product')

    return render(request, 'core/index.html', get_customer_context(request))


class OrderView(LoginRequiredMixin, generic.ListView):
    model = Order

    def get_queryset(self):
        queryset = super().get_queryset()

        if user := get_user(self.request):
            if in_group(user, 'customers'):
                queryset = self.model.objects.filter(customer=user).all()

            elif not in_group(user, 'managers'):
                queryset = self.model.objects.none()

        return queryset


class _OrderCrudMixin(LoginRequiredMixin):
    model = Order
    template_name = 'core/index.html'
    msgs = []

    # def __init__(self, **kwargs):
    #     super().__init__(kwargs)
    #     self.msgs = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            get_customer_context(self.request)
        )
        context['msgs'] = self.msgs
        return context


class OrderStatusView(_OrderCrudMixin, generic.UpdateView):
    def post(self, request, *args, **kwargs):
        to_status = kwargs.get('to_status')
        order = get_object_or_404(self.model, pk=kwargs.get('pk'))

        # customers...
        if to_status == 'pending':
            try:
                order.checkout()
            except ValidationError as e:
                self.msgs.append(e.message)

        # managers...
        elif to_status == 'dispatched':
            order.status = self.model.OrderStatus.SHIPPED
            order.save()
            return redirect('product')

        return redirect('index')


class OrderUpdateView(_OrderCrudMixin, generic.UpdateView):
    def post(self, request, *args, **kwargs):
        if data := request.POST.dict():
            order = get_object_or_404(self.model, pk=kwargs.get('pk', 0))
            quantity = int(data.get('quantity', 0))

            todo = data.get('todo', '')

            # customers...
            if todo == 'comprar':
                product_id = int(data.get('product_id', 0))
                product = Product.objects.get(id=product_id)

                try:
                    order.add_item(product, quantity)
                except ValidationError as e:
                    self.msgs.append(e.message)

            # customers...
            elif todo == 'esvaziar carrinho':
                for item in order.items.all():
                    item.delete()

        return redirect('index')


class OrderItemUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Order

    def post(self, request, *args, **kwargs):
        if data := request.POST.dict():
            order = get_object_or_404(self.model, pk=kwargs.get('order_pk', 0))
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


class OrderItemDeleteView(LoginRequiredMixin, generic.edit.DeleteView):
    model = Product


class ProductView(LoginRequiredMixin, generic.ListView):
    model = Product
    template_name = 'core/managing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = Product.objects.all()
        for p in products:
            p.form_ = ProductForm(instance=p)
        context.update({
            'form': ProductForm(),
            'products': products,
            'orders': Order.objects.filter(status=Order.OrderStatus.TO_BE_SHIPPED).all(),
            # 'msgs': msgs or [],
        })
        return context


class _ProductCrudMixin(LoginRequiredMixin):
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
