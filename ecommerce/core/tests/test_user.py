from django.test import TestCase
# from unittest import TestCase
from django.contrib.auth.models import Group
from ..models import Customer, Cart, Product


class TestUser(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.customer = Customer.objects.create_user(
            username='bob',
            email='b@b.com',
            password='12345'
        )
        # login = self.client.login(username='bob', password='12345')
  
        cls.avocado = Product.objects.create(
            name='Abacate',
            price=1.0
        )  
        cls.banana = Product.objects.create(
            name='Banana',
            price=1.0
        )

    def test_create(self):
        self.assertTrue(Customer.objects.exists())

    def test_costumer_must_be_at_the_costumers_group(self):
        group = self.customer.groups.first()
        self.assertEqual(group.name, 'customers')

    def test_when_created_costumer_must_have_a_cart(self):
        self.assertIsInstance(self.customer.cart, Cart)

    def test_the_default_quantity_for_a_product_when_picked_to_a_cart_is_1(self):
        self.customer.cart.add_product(product=self.avocado)

        self.assertEqual(self.customer.cart.content.first().name, 'Abacate')
        self.assertEqual(self.customer.cart.picks.first().product.name, 'Abacate')
        self.assertEqual(self.customer.cart.picks.first().quantity, 1)

    def test_a_costumer_can_add_one_product_to_his_cart(self):
        self.customer.cart.add_product(product=self.avocado, quantity=1)

        self.assertEqual(self.customer.cart.content.first().name, 'Abacate')
        self.assertEqual(self.customer.cart.picks.first().quantity, 1)

    def test_a_costumer_can_change_the_quantity_of_a_product_already_in_his_cart(self):
        self.customer.cart.add_product(product=self.avocado, quantity=1)
        self.assertEqual(self.customer.cart.picks.first().quantity, 1)

        self.customer.cart.add_product(product=self.avocado, quantity=2)
        self.assertEqual(self.customer.cart.picks.first().quantity, 3)

    def test_costumer_can_exclude_a_product_from_his_cart(self):
        self.customer.cart.add_product(product=self.avocado, quantity=3)
        self.assertEqual(self.customer.cart.picks.first().quantity, 3)

        self.customer.cart.remove_product(product=self.avocado)
        self.assertFalse(self.customer.cart.picks.exists())

        # deleting again...
        self.customer.cart.remove_product(product=self.avocado)
        self.assertFalse(self.customer.cart.picks.exists())

    def test_costumer_checkout_generates_an_order(self):
        self.customer.cart.add_product(product=self.avocado, quantity=2)
        self.customer.cart.add_product(product=self.banana, quantity=3)
        self.customer.cart.checkout()

        self.assertTrue(self.customer.orders.exists())
        self.assertEqual(self.customer.orders.first().status, 'TO_BE_SHIPPED')