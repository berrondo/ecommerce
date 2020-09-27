import pytest
from django.urls import reverse

from ..models import Product, Order
from ..views import in_group


@pytest.fixture()
def client_w_manager(client, a_manager):
    client.login(username='ann', password='54321')
    return client


@pytest.fixture
def client_w_customer(client, a_customer):
    client.login(username='bob', password='12345')
    return client


class TestManager:
    def test_a_manager_is_created_in_the_correct_group(self, a_manager):
        assert a_manager.groups.first().name == 'managers'
        assert in_group(a_manager, 'managers')

    def test_manager_is_logged_in(self, client, a_manager):
        client.login(username='ann', password='54321')

        from django.contrib import auth
        user = auth.get_user(client)
        assert user.is_authenticated

    def test_a_manager_can_add_a_product(self, client_w_manager):
        client = client_w_manager

        data = dict(
            name='Abacate',
            price=0.01,
        )

        response = client.post(reverse('product-create'), data=data, follow=True)
        assert response.status_code == 200
        assert Product.objects.first().name == 'Abacate'
        assert 'Abacate' in str(response.content)

    def test_a_manager_can_change_a_product(self, client_w_manager):
        client = client_w_manager

        data = dict(
            name='Abacate',
            price=0.01,
        )

        response = client.post(reverse('product-create'), data=data, follow=True)
        assert response.status_code == 200
        assert Product.objects.first().name == 'Abacate'
        assert 'Abacate' in str(response.content)

        new_data = dict(
            name='Abacateeee',
            price=0.01,
        )

        pk = Product.objects.first().pk
        response = client.post(reverse('product-update', args=[pk]), data=new_data, follow=True)
        assert response.status_code == 200
        assert Product.objects.first().name == 'Abacateeee'
        assert 'Abacateeee' in str(response.content)

    def test_a_manager_can_delete_a_product(self, client_w_manager):
        client = client_w_manager

        data = dict(
            name='Abacate',
            price=0.01,
        )

        response = client.post(reverse('product-create'), data=data, follow=True)
        assert response.status_code == 200
        assert Product.objects.first().name == 'Abacate'
        assert 'Abacate' in str(response.content)

        pk = Product.objects.first().pk
        response = client.post(reverse('product-delete', args=[pk]), follow=True)
        assert response.status_code == 200
        assert not Product.objects.exists()
        assert 'Abacate' not in str(response.content)

    def test_a_manager_can_change_the_status_order_from_pending_to_dipatched(
            self, client_w_customer, order_1, an_order, a_manager):
        client = client_w_customer

        response = client.post(reverse('order-update', args=[order_1.pk]), data=an_order, follow=True)
        assert 'bob' in str(response.content)
        assert 'Abacate' in str(response.content)

        response = client.post(reverse('order-status', args=['pending', order_1.pk]), follow=True)
        assert response.status_code == 200
        assert 'vazio' in str(response.content)
        assert Order.objects.get(pk=order_1.pk).status == Order.OrderStatus.TO_BE_SHIPPED

        client.logout()
        assert client.login(username=a_manager.username, password='54321')

        response = client.post(reverse('order-status', args=['dispatched', order_1.pk]), follow=True)
        assert response.status_code == 200
        assert Order.objects.get(pk=order_1.pk).status == Order.OrderStatus.SHIPPED
        assert 'Pendente' not in str(response.content)
