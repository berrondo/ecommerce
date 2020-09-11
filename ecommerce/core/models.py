from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomerUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()

        user.groups.add(Group.objects.create(name='customers'))
        user.cart = Cart.objects.create(customer=user)
        return user


class Customer(User):
    objects = CustomerUserManager()


class Cart(models.Model):
    customer = models.OneToOneField('Customer', related_name='cart', on_delete=models.CASCADE)
    content = models.ManyToManyField('Product', through='ProductCart', blank=True)

    def add_product(self, product, quantity=1):
        pick, created = ProductCart.objects.get_or_create(cart=self, product=product)
        pick.quantity += quantity
        pick.save()
        return pick

    def remove_product(self, product):
        try:
            pick = ProductCart.objects.get(product=product)
            pick.delete()
        except ProductCart.DoesNotExist:
            ...

    def checkout(self):
        order = Order.objects.create(customer=self.customer)
        # for pick in self.picks:
        #     order.pick = pick
        #     pick.delete()
        return order

    class Meta:
        verbose_name = 'carrinho'
        verbose_name_plural = 'carrinhos'

    def __str__(self):
        return f'Carrinho {self.id}'


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'produto'
        verbose_name_plural = 'produtos'

    def __str__(self):
        return f'{self.name} ({self.price})'


class ProductCart(models.Model):
    cart = models.ForeignKey('Cart', related_name='picks', on_delete=models.CASCADE, verbose_name='carrinho')
    product = models.ForeignKey('Product', related_name='in_cart', on_delete=models.CASCADE, verbose_name='produto')
    quantity = models.PositiveIntegerField('quantidade', default=0)

    class Meta:
        unique_together = ('cart', 'product')
        verbose_name = 'inclusão'
        verbose_name_plural = 'inclusões'

    def __str__(self):
        return f'Inclusão em {self.cart} de {self.quantity} {self.product}'


class ProductOrder(models.Model):
    # cart = models.ForeignKey('Cart', related_name='picks', on_delete=models.CASCADE, verbose_name='carrinho')
    product = models.ForeignKey('Product', related_name='ordered', on_delete=models.CASCADE, verbose_name='produto')
    quantity = models.PositiveIntegerField('quantidade')
    order =  models.ForeignKey('Order', related_name='produtos', on_delete=models.CASCADE, verbose_name='pedido')
    # price = ...

    # class Meta:
    #     unique_together = ('cart', 'product')
    #     verbose_name = 'inclusão'
    #     verbose_name_plural = 'inclusões'

    # def __str__(self):
    #     return f'Inclusão em {self.cart} de {self.quantity} {self.product}'


class Order(models.Model):
    customer = models.ForeignKey('Customer', related_name='orders', on_delete=models.CASCADE, verbose_name='pedidos')
    # picks = ...

    class OrderStatus(models.TextChoices):
        TO_BE_SHIPPED = 'TO_BE_SHIPPED', _('Pendente')
        SHIPPED = 'SHIPPED', _('Despachado')
        DELIVERED = 'DELIVERED', _('Entregue')

    status = models.CharField(
            max_length=15,
            choices=OrderStatus.choices,
            default=OrderStatus.TO_BE_SHIPPED,
    )
