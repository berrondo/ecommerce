class TestCustomerAndOrder:
    def test_a_customer_is_created_in_the_correct_group_with_an_opened_order(self, a_customer, order_1):
        assert a_customer.groups.first().name == 'customers'
        assert order_1.status == 'OPENED'

    def test_the_default_quantity_for_a_chosen_product_is_1(self, a_customer, avocado, order_1):
        item = order_1.add_product(avocado)

        assert item.product.name == 'Abacate'
        assert item.quantity == 1

    def test_a_costumer_can_add_one_product_to_his_cart(self, a_customer, avocado, order_1):
        item = order_1.add_product(avocado, 1)

        assert item.product.name == 'Abacate'
        assert item.quantity == 1

    def test_a_costumer_can_change_the_quantity_of_a_chosen_product(self, a_customer, avocado, order_1):
        item = order_1.add_product(avocado, 1)
        assert item.quantity == 1

        item = order_1.add_product(avocado, 3)
        assert item.quantity == 3

    def test_a_costumer_can_exclude_a_product_from_his_cart(self, a_customer, avocado, order_1):
        item = order_1.add_product(avocado, 3)
        assert item.quantity == 3

        item = order_1.remove_product(avocado)
        assert not item
        assert not order_1.picks.exists()

        # deleting again...
        item = order_1.remove_product(avocado)
        assert not item
        assert not order_1.picks.exists()

    def test_setting_the_quantity_of_a_product_to_zero_is_equivalent_to_delete_it(self, a_customer, avocado, order_1):
        item = order_1.add_product(avocado, 3)
        assert item.quantity == 3

        item = order_1.add_product(avocado, 0)
        assert not item
        assert not order_1.picks.exists()

    def test_costumer_checkout_finalizes_the_order(self, a_customer, avocado, banana, order_1):
        order_1.add_product(avocado, 3)
        order_1.add_product(banana, 2)
        order_1.checkout()

        assert order_1.status == 'TO_BE_SHIPPED'

    def test_costumer_should_not_alter_a_not_opened_order(self, a_customer, avocado, banana, order_1):
        order_1.add_product(avocado, 3)

        order_1.checkout()
        assert order_1.status == 'TO_BE_SHIPPED'

        order_1.add_product(avocado, 2)
        assert order_1.picks.first().quantity == 3

        

# from django.test import TestCase
# # from unittest import TestCase
# from django.contrib.auth.models import Group
# from ..models import User, Order, Product


# class TestCustomer(TestCase):
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()

#         cls.customer = User.objects.create_customer(
#             username='bob',
#             password='12345'
#         )
#         # login = self.client.login(username='bob', password='12345')
  
#         cls.avocado = Product.objects.create(
#             name='Abacate',
#             price=1.0
#         )  
#         cls.banana = Product.objects.create(
#             name='Banana',
#             price=1.0
#         )

#     def order_1(self):
#         return self.customer.orders.first()

#     def pick_1(self):
#         return self.customer.orders.first().picks.first()

#     def test_create(self):
#         self.assertTrue(User.objects.exists())

#     def test_costumer_must_be_at_the_costumers_group(self):
#         group = self.customer.groups.first()
#         self.assertEqual(group.name, 'customers')

#     def test_when_created_costumer_must_have_an_opened_order(self):
#         self.assertIsInstance(self.customer.orders.first(), Order)
#         self.assertEqual(self.customer.orders.first().status, 'OPENED')

#     def test_the_default_quantity_for_a_product_when_picked_to_an_order_is_1(self):
#         pick = self.customer.orders.first().add_product(product=self.avocado)

#         self.assertEqual(pick.product.name, 'Abacate')
#         self.assertEqual(pick.quantity, 1)
        
#         # self.assertEqual(self.customer.orders.first().content.name, 'Abacate')
#         self.assertEqual(self.pick_1().product.name, 'Abacate')
#         self.assertEqual(self.pick_1().quantity, 1)

#     def test_a_costumer_can_add_one_product_to_his_cart(self):
#         self.order_1().add_product(product=self.avocado, quantity=1)

#         # self.assertEqual(self.order_1().content.name, 'Abacate')
#         self.assertEqual(self.pick_1().quantity, 1)

#     def test_a_costumer_can_change_the_quantity_of_a_product_already_in_his_cart(self):
#         self.order_1().add_product(product=self.avocado, quantity=1)
#         self.assertEqual(self.pick_1().quantity, 1)

#         self.order_1().add_product(product=self.avocado, quantity=2)
#         self.assertEqual(self.pick_1().quantity, 2)

#     def test_a_costumer_can_exclude_a_product_from_his_cart(self):
#         self.order_1().add_product(product=self.avocado, quantity=3)
#         self.assertEqual(self.pick_1().quantity, 3)

#         self.order_1().remove_product(product=self.avocado)
#         self.assertFalse(self.order_1().picks.exists())

#         # deleting again...
#         self.order_1().remove_product(product=self.avocado)
#         self.assertFalse(self.order_1().picks.exists())

#     def test_costumer_checkout_finalizes_the_order(self):
#         self.order_1().add_product(product=self.avocado, quantity=2)
#         self.order_1().add_product(product=self.banana, quantity=3)
#         self.order_1().checkout()

#         self.assertEqual(self.order_1().status, 'TO_BE_SHIPPED')

#     def test_costumer_should_see_his_orders(self):
#         ...