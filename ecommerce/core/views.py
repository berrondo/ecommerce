from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, PermissionDenied
from django.http import HttpResponseRedirect
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


def get_customer_context(request):
    opened_order = Order.objects.none()
    if user := get_user(request):
        if hasattr(user, 'orders'):
            opened_order, _ = Order.objects.get_or_create(
                customer=user,
                status=Order.OrderStatus.OPENED)

    products = Product.objects.filter(is_active=True).all()

    context = {
        'products': products,
        'orders': [opened_order],
        'opened_order': opened_order,
        'messages': messages.get_messages(request),
    }
    return context


def index(request):
    if user := get_user(request):
        if user.has_perm('core.can_manage_product'):
            return redirect('product')

    return render(request, 'core/index.html', get_customer_context(request))


class OrderListView(LoginRequiredMixin, generic.ListView):
    model = Order

    def get_queryset(self):
        queryset = super().get_queryset()

        if user := get_user(self.request):
            if user.has_perm('core.can_checkout_opened_orders'):
                queryset = self.model.objects.filter(customer=user).all()

            elif not user.has_perm('core.can_manage_product'):
                queryset = self.model.objects.none()

        return queryset


class _OrderCrudMixin(
        LoginRequiredMixin,
        UserPassesTestMixin,
        generic.base.ContextMixin,
        generic.View):

    model = Order
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            get_customer_context(self.request)
        )
        return context

    def test_func(self):
        """the customer must see and change only his own orders"""
        user = get_user(self.request)
        return self.get_object() in user.orders.all()


class OrderStatusView(_OrderCrudMixin, generic.UpdateView):
    def test_func(self):
        return True

    def post(self, request, *args, **kwargs):
        to_status = kwargs.get('to_status')
        order = self.get_object()

        # customers...
        if to_status == 'pending':
            if request.user.has_perm('core.can_checkout_opened_orders'):
                try:
                    order.checkout()
                except ValidationError as e:
                    messages.error(request, e.message)
            else:
                raise PermissionDenied()

        # managers...
        elif to_status == 'dispatched':
            if request.user.has_perm('core.can_dispatch_pending_orders'):
                order.status = self.model.OrderStatus.SHIPPED
                order.save()
                return redirect('product')
            else:
                raise PermissionDenied()

        return redirect('index')


class OrderUpdateView(_OrderCrudMixin, generic.UpdateView):
    def post(self, request, *args, **kwargs):
        if data := request.POST.dict():

            quantity = int(data.get('quantity', 0))

            product_id = int(data.get('product_id', 0))
            product = get_object_or_404(Product, id=product_id)

            try:
                self.get_object().add_item(product, quantity)
            except ValidationError as e:
                messages.error(request, e.message)

        return redirect('index')


class OrderDeleteView(_OrderCrudMixin, generic.DeleteView):
    success_url = reverse_lazy('index')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        for item in self.object.items.all():
            item.delete()
        return HttpResponseRedirect(success_url)


class OrderItemUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Order

    def post(self, request, *args, **kwargs):
        if data := request.POST.dict():
            user = get_user(request)
            order = get_object_or_404(self.model, pk=kwargs.get('order_pk', 0))

            if order not in user.orders.all():
                raise PermissionDenied()

            item = order.items.get(id=kwargs.get('item_pk', 0))

            quantity = int(data.get('quantity', 0))

            if not quantity:
                item.delete()

            else:
                item.quantity = quantity
                item.save()

        return redirect('index')


class OrderItemDeleteView(LoginRequiredMixin, generic.edit.DeleteView):
    model = Product


class _ProductCrudMixin(PermissionRequiredMixin, LoginRequiredMixin):
    model = Product
    fields = ['name', 'price', 'is_active']
    template_name = 'core/managing.html'
    success_url = reverse_lazy('product')
    permission_required = 'core.can_manage_product'


class ProductListView(_ProductCrudMixin, generic.ListView):
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
            'messages': messages.get_messages(self.request),
        })
        return context


class ProductCreateView(_ProductCrudMixin, generic.edit.CreateView):
    ...


class ProductUpdateView(_ProductCrudMixin, generic.edit.UpdateView):
    ...


class ProductDeleteView(_ProductCrudMixin, generic.edit.DeleteView):
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.is_active = False
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


# class OrderItemViewSet(viewsets.ModelViewSet):
#     queryset = OrderItem.objects.all()
#     serializer_class = OrderItemSerializer
