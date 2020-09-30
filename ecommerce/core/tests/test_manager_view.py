import pytest
from django.urls import reverse as r

from ..models import Product, Order
from ..views import in_group


class TestManagerCreationAndLogIn:
    def test_a_manager_is_created_in_the_correct_group(self, a_manager):
        assert a_manager.groups.first().name == 'managers'
        assert in_group(a_manager, 'managers')

    def test_manager_is_logged_in(self, client, a_manager):
        client.login(username='ann', password='54321')

        from django.contrib import auth
        user = auth.get_user(client)
        assert user.is_authenticated


class TestManagerManagingProducts:
    def test_a_manager_can_add_a_product(self, register_product):
        assert register_product.status_code == 200
        assert Product.objects.first().name == 'Abacate'
        assert Product.objects.first().is_active
        assert 'Abacate' in str(register_product.content)

    def test_a_manager_can_change_a_product(self, client_w_manager, register_product):
        new_data = dict(
            name='Abacateeee',
            price=0.01,
        )
        response = client_w_manager.post(r('product-update', args=[1]), new_data, follow=True)
        assert response.status_code == 200
        assert Product.objects.first().name == 'Abacateeee'
        assert 'Abacateeee' in str(response.content)

    def test_a_manager_can_delete_a_product(self, client_w_manager, register_product):
        response = client_w_manager.post(r('product-delete', args=[1]), follow=True)
        assert response.status_code == 200
        assert not Product.objects.first().is_active
        assert 'Abacate' in str(response.content)

    @pytest.mark.parametrize('wrong_price', ((0, -0.01),))
    def test_a_product_should_not_have_price_lte_zero(self, client_w_manager, register_product, wrong_price):
        new_data = dict(
            price=wrong_price,
        )
        response = client_w_manager.post(r('product-update', args=[1]), new_data, follow=True)
        assert response.status_code == 200
        assert 'Certifique-se que este valor seja maior ou igual a 0.01.' in str(response.content)


class TestManagerDispatchingOrder:
    def test_a_manager_can_change_the_status_order_from_pending_to_dispatched(self, client_w_customer, an_order, a_manager):
        client = client_w_customer

        response = client.post(r('order-update', args=[1]), an_order, follow=True)
        assert 'bob' in str(response.content)
        assert 'Abacate' in str(response.content)

        response = client.post(r('order-status-update', args=[1, 'pending']), follow=True)
        assert response.status_code == 200
        assert 'vazio' in str(response.content)
        assert Order.objects.get(pk=1).status == Order.OrderStatus.TO_BE_SHIPPED

        client.logout()
        assert client.login(username=a_manager.username, password='54321')

        response = client.post(r('order-status-update', args=[1, 'dispatched']), follow=True)
        assert response.status_code == 200
        assert Order.objects.get(pk=1).status == Order.OrderStatus.SHIPPED
        assert 'Pendente' not in str(response.content)

    def test_a_manager_can_not_checkout_an_order(self, client_w_customer, an_order, a_manager):
        client = client_w_customer

        response = client.post(r('order-update', args=[1]), an_order, follow=True)
        assert 'bob' in str(response.content)
        assert 'Abacate' in str(response.content)

        client.logout()
        assert client.login(username=a_manager.username, password='54321')

        response = client.post(r('order-status-update', args=[1, 'pending']), follow=True)
        assert response.status_code == 403
        assert Order.objects.get(pk=1).status == Order.OrderStatus.OPENED
