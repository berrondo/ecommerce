from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


def set_group_permissions(group):
    if group.name == 'customers':
        ...
        # group.permissions.add(
        #     can_view_products
        #     can_view_his_orders
        #     can_change_his_opened_orders  can_checkout_opened_orders
        #     can_delete_his_opened_orders
        # )
    if group.name == 'managers':
        ...
        # group.permissions.add(
        #     ('can__products', ''),
        #     ('can_view_orders', 'Can view orders'),
        #     ('can_dispatch_opened_orders', 'Can dispatch  opened orders'),
        # )
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
    content = models.ManyToManyField('Product', through='OrderItem', blank=True)

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
            raise ValidationError(f"Já existe ({item.quantity}) {product.name} em seu carrinho")

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
        self._nust_be_an_non_empty_order()

        self.status = self.OrderStatus.TO_BE_SHIPPED
        # for i in self.content.all():
        #     self.content.filter(order=self, in_cart=i).price = i.price
        #     self.content(i).save()
        self.save()
        return self

    def _nust_be_an_non_empty_order(self):
        if self.content.count() == 0:
            raise ValidationError("The Order is empty!")

    def _must_be_an_opened_order(self):
        if self.status != Order.OrderStatus.OPENED:
            raise ValidationError("Should not alter a not opened order!")


class Product(models.Model):
    name = models.CharField('nome', max_length=200, unique=True)
    price = models.DecimalField('preço', max_digits=10, decimal_places=2, default=0)

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


# class UserManager(BaseUserManager):
#     def create_user(self, password, **extra_fields):
#         user = self.model(**extra_fields)
#         user.set_password(password)
#         user.staff = True
#         user.save()
#         return user
#
#     def create_customer(self, password, **extra_fields):
#         user = self.create_user(password, **extra_fields)
#         customers_group, created = Group.objects.get_or_create(name='customers')
#         if created:
#             set_customers_group_permissions(customers_group)
#         user.groups.add(customers_group)
#         user.orders.add(Order.objects.create(customer=user))
#         return user
#
#     def create_manager(self, password, **extra_fields):
#         user = self.create_user(password, **extra_fields)
#         managers_group, created = Group.objects.get_or_create(name='managers')
#         if created:
#             set_managers_group_permissions(managers_group)
#         user.groups.add(managers_group)
#         return user

    # def is_customer(self):
    #     group_customers = self.groups.filter(name='customers')
    #     return group_customers.count() == 1

    # def is_manager(self):
    #     group_managers = self.groups.filter(name='managers')
    #     return group_managers.count() == 1

    # def get_opened_order(self):
    #     if self.is_customer():
    #         opened_order, _ = Order.objects.get_or_create(
    #             customer=self,
    #             status=Order.OrderStatus.OPENED)
    #         return opened_order
