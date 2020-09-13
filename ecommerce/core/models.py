from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, password, **extra_fields):
        user = self.model(**extra_fields)
        user.set_password(password)
        user.staff = True
        user.save()
        return user

    def create_customer(self, password, **extra_fields):
        user = self.create_user(password, **extra_fields)
        user.groups.add(Group.objects.create(name='customers'))
        user.orders.add(Order.objects.create(customer=user))
        return user

    def create_manager(self, password, **extra_fields):
        user = self.create_user(password, **extra_fields)
        user.groups.add(Group.objects.create(name='managers'))
        return user


class User(User):
    objects = UserManager()


class Order(models.Model):
    customer = models.ForeignKey('User', related_name='orders', on_delete=models.CASCADE)
    content = models.ManyToManyField('Product', through='ProductOrder', blank=True)
    
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

    def add_product(self, product, quantity=1):
        pick, created = ProductOrder.objects.get_or_create(order=self, product=product)
        pick.quantity += quantity
        pick.save()
        return pick

    def remove_product(self, product):
        try:
            pick = ProductOrder.objects.get(product=product)
            pick.delete()
        except ProductOrder.DoesNotExist:
            ...

    def checkout(self):
        self.status = self.OrderStatus.TO_BE_SHIPPED
        # for p in self.content.all():
        #     self.content.filter(order=self, in_cart=p).price = p.price
        #     self.content(p).save()
        self.save()
        return self

    class Meta:
        verbose_name = 'pedido'
        verbose_name_plural = 'pedidos'

    def __str__(self):
        return f'Pedido {self.id}'


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'produto'
        verbose_name_plural = 'produtos'

    def __str__(self):
        return f'{self.name} ({self.price})'


class ProductOrder(models.Model):
    order = models.ForeignKey('Order', related_name='picks', on_delete=models.CASCADE, verbose_name='pedido')
    product = models.ForeignKey('Product', related_name='in_cart', on_delete=models.CASCADE, verbose_name='produto')
    quantity = models.PositiveIntegerField('quantidade', default=0)
    # purchased price:
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ('order', 'product')
        verbose_name = 'inclusão'
        verbose_name_plural = 'inclusões'

    def __str__(self):
        return f'Inclusão em {self.order} de {self.quantity} {self.product}'
