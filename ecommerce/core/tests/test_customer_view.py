import pytest

from django.urls import reverse as r


class TestCustomerLogIn:
    def test_customer_is_logged_in(self, client, a_customer):
        client.login(username='bob', password='12345')

        from django.contrib import auth
        user = auth.get_user(client)
        assert user.is_authenticated

        response = client.get(r('index'))
        assert response.status_code == 200
        assert 'bob' in str(response.content)


class TestCustomerProductsList:
    def test_a_customer_can_only_see_to_buy_active_products(self, client_w_customer,
                                                            avocado, no_active_product):
        response = client_w_customer.get(r('index'))
        assert 'bob' in str(response.content)
        assert 'Abacate' in str(response.content)
        assert "Uva" not in str(response.content)



@pytest.fixture()
def add_item(client, an_order):
    client.login(username='bob', password='12345')
    response = client.post(r('order-update', args=[1]), data=an_order, follow=True)
    return response


class TestCustomerAddingToOrder:
    def test_post_to_include_an_item_in_the_order(self, a_customer, add_item):
        assert add_item.status_code == 200
        assert a_customer.orders.first().items.first().quantity == 1

    def test_post_the_same_item_twice(self, client, a_customer, an_order, add_item):
        assert add_item.status_code == 200
        assert a_customer.orders.first().items.first().quantity == 1

        # again...
        response = client.post(r('order-update', args=[1]), data=an_order, follow=True)
        assert response.status_code == 200
        # assert "Seu carrinho já tem" in str(response.content)


class TestCustomerChangingOrderItems:
    def test_delete_via_post_to_exclude_an_item_from_the_order(self, client, a_customer, add_item):
        assert add_item.status_code == 200
        assert a_customer.orders.first().items.first().quantity == 1

        an_item = {
                "todo": 'excluir',
        }
        response = client.post(r('order-item-update', args=[1, 1]), data=an_item, follow=True)
        assert response.status_code == 200
        assert not a_customer.orders.first().items.exists()

    def test_patch_via_post_to_update_an_item_fields(self, client, a_customer, add_item):
        assert add_item.status_code == 200
        assert a_customer.orders.first().items.first().quantity == 1

        an_item = {
                "quantity": 7,
                "todo": 'alterar',
        }
        response = client.post(r('order-item-update', args=[1, 1]), data=an_item, follow=True)
        assert response.status_code == 200
        assert a_customer.orders.first().items.first().quantity == 7

    def test_patch_via_post_with_quantity_equals_zero_is_equivalent_to_delete(self, client, a_customer, add_item):
        assert add_item.status_code == 200
        assert a_customer.orders.first().items.first().quantity == 1

        an_item = {
                "quantity": 0,
                "todo": 'alterar',
        }
        response = client.post(r('order-item-update', args=[1, 1]), data=an_item, follow=True)
        assert response.status_code == 200
        assert not a_customer.orders.first().items.exists()


class TestCustomerCheckingOutOrder:
    def test_a_customer_can_checkout_his_opened_order(self, client, a_customer, add_item):
        response = client.post(r('order-status-update', args=[1, 'pending']), follow=True)
        assert 'vazio' in str(response.content)
