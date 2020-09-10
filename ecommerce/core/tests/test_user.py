from django.test import TestCase
from django.contrib.auth.models import Group
from ..models import Costumer, Cart, Product, Product_Cart


class TestUser(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.costumer = Costumer.objects.create_user(
            username='bob',
            email='b@b.com',
            password='12345'
        )
        # login = self.client.login(username='bob', password='12345')
  
        cls.product = Product.objects.create(
            name='Abacate',
            price=1.0
        )

    def test_create(self):
        self.assertTrue(Costumer.objects.exists())

    def test_costumer_must_be_at_the_costumers_group(self):
        group = self.costumer.groups.first()
        self.assertEqual(group.name, 'costumers')

    def test_when_created_costumer_must_have_a_cart(self):
        self.assertIsInstance(self.costumer.cart, Cart)

    def test_a_costumer_can_add_a_product_to_his_cart(self):
        self.costumer.cart.add_product(product=self.product, quantity=1)
        self.assertEqual(self.costumer.cart.contents.first().name, 'Abacate')
        # self.assertEqual(self.costumer.cart.contents.first().quantity, 1)

    # def test_a_costumer_can_take_change_the_quantity_of_a_product_already_in_his_cart(self):
    #     self.costumer.cart.add_product(product=self.product, quantity=1)
    #     self.assertEqual(self.costumer.cart.contents.first().quantity, 1)

    #     self.costumer.cart.contents('Abacate').quantity += 1
    #     self.assertEqual(self.costumer.cart.contents.first().quantity, 2)