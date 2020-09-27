import pytest

from django.urls import reverse


@pytest.fixture()
def _response(client, order_1, an_order):
    client.login(username='bob', password='12345')
    response = client.post(reverse('order-update', args=[order_1.pk]), data=an_order)
    return response


class TestCustomerViewActions:
    def test_customer_is_logged_in(self, client, a_customer):
        client.login(username='bob', password='12345')

        from django.contrib import auth
        user = auth.get_user(client)
        assert user.is_authenticated

        response = client.get(reverse('index'))
        assert response.status_code == 200
        assert 'bob' in str(response.content)

    def test_post(self,  a_customer, _response):
        assert _response.status_code == 302
        assert a_customer.orders.first().items.first().quantity == 1

    def test_post_the_same_product_twice(self, client, a_customer, order_1, an_order, _response):
        assert _response.status_code == 302
        assert a_customer.orders.first().items.first().quantity == 1

        # again...
        response = client.post(reverse('order-update', args=[order_1.pk]), data=an_order, follow=True)
        assert response.status_code == 200
        # assert "Seu carrinho já tem" in str(response.content)

    def test_delete_via_post(self, client, a_customer, order_1, _response):
        assert _response.status_code == 302
        assert a_customer.orders.first().items.first().quantity == 1

        an_item = {
                "item_id": a_customer.orders.first().items.first().id,
                "todo": 'excluir',
        }
        response = client.post(reverse('order-item-update', args=[order_1.pk, an_item['item_id']]), data=an_item)
        assert response.status_code == 302
        assert not a_customer.orders.first().items.exists()

    def test_patch_via_post(self, client, a_customer, order_1, _response):
        assert _response.status_code == 302
        assert a_customer.orders.first().items.first().quantity == 1

        an_item = {
                "item_id": a_customer.orders.first().items.first().id,
                "quantity": 7,
                "todo": 'alterar',
        }
        response = client.post(reverse('order-item-update', args=[order_1.pk, an_item['item_id']]), data=an_item)
        assert response.status_code == 302
        assert a_customer.orders.first().items.first().quantity == 7

    def test_patch_via_post_with_quantity_equals_zero_is_equivalent_to_delete(self, client, a_customer, order_1, _response):
        assert _response.status_code == 302
        assert a_customer.orders.first().items.first().quantity == 1

        an_item = {
                "item_id": a_customer.orders.first().items.first().id,
                "quantity": 0,
                "todo": 'alterar',
        }
        response = client.post(reverse('order-item-update', args=[order_1.pk, an_item['item_id']]), data=an_item)
        assert response.status_code == 302
        assert not a_customer.orders.first().items.exists()

    def test_a_customer_can_checkout_his_opened_order(self, client, a_customer, order_1, _response):
        response = client.post(reverse('order-status', args=['pending', 1]), follow=True)
        assert 'vazio' in str(response.content)
