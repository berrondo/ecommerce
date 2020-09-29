from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


def set_group_permissions(group):
    if group.name == 'customers':
        ...
        # group.permissions.add(('customer_permissions', 'Customer Permissions'))
        #     can_view_products
        #     can_view_his_orders
        #     can_change_his_opened_orders  can_checkout_opened_orders
        #     can_delete_his_opened_orders
    if group.name == 'managers':
        ...
        # group.permissions.add(('manager_permissions', 'Manager Permissions'))
        #     ('can__products', '') ,
        #     ('can_view_orders', 'Can view orders'),
        #     ('can_dispatch_opened_orders', 'Can dispatch  opened orders'),
    return group


def create_user(username, password, in_group='customers'):
    user, _ = User.objects.get_or_create(username=username)
    user.set_password(password)
    user.is_staff = True  # can use django admin
    user.save()
    group, created = Group.objects.get_or_create(name=in_group)
    if created:
        set_group_permissions(group)
    user.groups.add(group)
    if group.name == 'customers':
        user.orders.add(Order.objects.create(customer=user))
    user.save()
    return user


class Order(models.Model):
    customer = models.ForeignKey('auth.User', related_name='orders', on_delete=models.CASCADE)
    products = models.ManyToManyField('Product', through='OrderItem', blank=True)

    @property
    def total(self):
        return sum(i.sub_total for i in self.items.all())
    
    class OrderStatus(models.TextChoices):
        OPENED = 'OPENED', _('Aberto')
        TO_BE_SHIPPED = 'TO_BE_SHIPPED', _('Pendente')
        SHIPPED = 'SHIPPED', _('Despachado')
        DELIVERED = 'DELIVERED', _('Entregue')

    status = models.CharField(
            max_length=15,
            choices=OrderStatus.choices,
            default=OrderStatus.OPENED,
    )

    class Meta:
        verbose_name = 'pedido'
        verbose_name_plural = 'pedidos'
        ordering = ['-id']

    def __str__(self):
        return f'Pedido {self.id}'

    def add_item(self, product, quantity=1):
        self._must_be_an_opened_order()

        if quantity == 0:
            return self.remove_item(product)
        
        item, created = self.items.get_or_create(order=self, product=product)
        if not created:
            raise ValidationError(f"Seu carrinho já tem {product.name} ({item.quantity}).")

        item.quantity = quantity
        item.price = product.price
        item.save()
        return item

    def remove_item(self, product):
        self._must_be_an_opened_order()

        try:
            item = self.items.get(product=product)
            item.delete()
        except OrderItem.DoesNotExist:
            ...

    def checkout(self):
        self._must_be_an_opened_order()
        self._must_be_an_non_empty_order()

        self.status = self.OrderStatus.TO_BE_SHIPPED
        # for i in self.content.all():
        #     self.content.filter(order=self, in_cart=i).price = i.price
        #     self.content(i).save()
        self.save()
        return self

    def delete(self):
        self._must_be_an_empty_order()
        self._must_be_an_opened_order()
        super().delete()

    def _must_be_an_empty_order(self):
        if self.products.count() > 0:
            raise ValidationError("The order is not empty!")

    def _must_be_an_non_empty_order(self):
        if self.products.count() == 0:
            raise ValidationError("The order is empty!")

    def _must_be_an_opened_order(self):
        if self.status != Order.OrderStatus.OPENED:
            raise ValidationError("Should not alter a not opened order!")


class Product(models.Model):
    name = models.CharField('nome', max_length=200, unique=True)
    price = models.DecimalField('preço', max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField('ativo', default=True)

    class Meta:
        verbose_name = 'produto'
        verbose_name_plural = 'produtos'

    def __str__(self):
        return f'{self.name} ({self.price})'


class OrderItem(models.Model):
    order = models.ForeignKey('Order', related_name='items', on_delete=models.CASCADE, verbose_name='pedido')
    product = models.ForeignKey('Product', related_name='order_item', on_delete=models.CASCADE, verbose_name='produto')
    quantity = models.PositiveIntegerField('quantidade', default=0)
    # purchased price:
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def sub_total(self):
        return self.quantity * self.product.price

    class Meta:
        unique_together = ('order', 'product')
        verbose_name = 'inclusão'
        verbose_name_plural = 'inclusões'

    def __str__(self):
        return f'Inclusão em {self.order} de {self.quantity} {self.product}'
