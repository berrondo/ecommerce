from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.auth.base_user import BaseUserManager


class CostumerUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()

        user.groups.add(Group.objects.create(name='costumers'))
        user.cart = Cart.objects.create(user=user)
        return user


class Costumer(User):
    objects = CostumerUserManager()


class Cart(models.Model):
    user = models.OneToOneField('Costumer', related_name='from_user', on_delete=models.CASCADE)
    contents = models.ManyToManyField('Product', through='Product_Cart', blank=True)

    def add_product(self, product, quantity=1):
        Product_Cart.objects.create(cart=self, product=product, quantity=quantity)

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


class Product_Cart(models.Model):
    cart = models.ForeignKey('Cart', related_name='picks', on_delete=models.CASCADE, verbose_name='carrinho')
    product = models.ForeignKey('Product', related_name='in_cart', on_delete=models.CASCADE, verbose_name='produto')
    quantity = models.PositiveIntegerField()

    class Meta:
        unique_together = ('cart', 'product')
        verbose_name = 'inclusão'
        verbose_name_plural = 'inclusões'

    def __str__(self):
        return f'Inclusão em {self.cart} de {self.quantity} {self.product}' 