from django.test import TestCase
from django.contrib.auth.models import Group
from ..models import Costumer, Cart, Product, Product_Cart


class TestUser(TestCase):
    def setUp(self):
        self.costumer = Costumer.objects.create_user(
            username='bob',
            email='b@b.com',
            password='12345')

        # login = self.client.login(username='bob', password='12345')

    def test_create(self):
        self.assertTrue(Costumer.objects.exists())

    def test_costumer_must_be_at_the_costumers_group(self):
        group = self.costumer.groups.first()
        self.assertIsInstance(group, Group)
        self.assertEqual(group.name, 'costumers')

    def test_when_created_costumer_must_have_a_cart(self):
        self.assertIsInstance(self.costumer.cart, Cart)


# class TestCart(TestCase):
    def test_a_costumer_can_add_a_product_to_his_cart(self):
        a_pick = Product_Cart.objects.create(
            cart=self.costumer.cart,
            product=Product.objects.create(
                name='Abacate',
                price=1.0,
            ),
            quantity=1,
        )
        # self.costumer.cart.products.add(a_pick)
        self.assertEqual(self.costumer.cart.products.first().name, 'Abacate')