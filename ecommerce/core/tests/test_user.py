from django.test import TestCase
# from ..models import BuyerUser
from django.contrib.auth.models import User, Group


class TestUser(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='bob', 
            password='12345')

        self.group = Group.objects.create(
            name='costumers'
        )
        self.user.groups.add(self.group)

        login = self.client.login(username='bob', password='12345')

    def test_create(self):
        self.assertTrue(User.objects.exists())

    def test_buyer_user_must_be_at_the_buyers_group(self):
        self.assertIsInstance(self.user.groups.first(), Group)

    # def test_when_created_buyer_must_have_a_cart(self):
    #     self.assertTrue(self.user.cart)