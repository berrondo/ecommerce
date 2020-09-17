from ..models import User


class TestManager:
    def test_a_manager_is_created_in_the_correct_group(self, a_manager):
        assert User.objects.exists()
        assert a_manager.groups.first().name == 'managers'


    def test_manager_can_add_products(self, a_manager):
        ...  # ???



# from django.test import TestCase
# # from unittest import TestCase
# from django.contrib.auth.models import Group
# from ..models import User, Order, Product


# class TestCustomer(TestCase):
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()

#         cls.manager = User.objects.create_manager(
#             username='ann',
#             password='54321'
#         )
#         # login = self.client.login(username='ann', password='54321')
  
#     def test_create(self):
#         self.assertTrue(User.objects.exists())

#     def test_costumer_must_be_at_the_costumers_group(self):
#         group = self.manager.groups.first()
#         self.assertEqual(group.name, 'managers')

#     def test_manager_can_add_products(self):
#         ...  # ???
