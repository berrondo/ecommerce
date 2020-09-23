
from django.urls import reverse


class TestViewIndex:
    def test_customer_is_logged_in(self, client, a_customer):
        client.login(username='bob', password='12345')

        from django.contrib import auth
        user = auth.get_user(client)
        assert user.is_authenticated

    def test_get(self, client):
        client.login(username='bob', password='12345')
        response = client.get(reverse('index'))
        assert response.status_code == 200

    def test_post(self, client, a_customer, an_order):
        client.login(username='bob', password='12345')
        response = client.post(reverse('orders'), data=an_order)

        assert response.status_code == 302
        assert a_customer.get_opened_order().picks.first().quantity == 1

    def test_post_the_same_product_twice(self, client, a_customer, an_order):
        client.login(username='bob', password='12345')
        response = client.post(reverse('orders'), data=an_order)

        assert response.status_code == 302
        assert a_customer.orders.first().picks.first().quantity == 1

        # again...
        response = client.post(reverse('orders'), data=an_order)
        assert response.status_code == 200
        assert "existe" in str(response.content)

    def test_delete_via_post(self, client, a_customer, an_order):
        client.login(username='bob', password='12345')
        response = client.post(reverse('orders'), data=an_order)

        assert response.status_code == 302
        assert a_customer.orders.first().picks.first().quantity == 1

        an_item = {
                "item_id": a_customer.orders.first().picks.first().id,
                "todo": 'excluir',
        }
        response = client.post(reverse('index'), data=an_item)
        assert response.status_code == 302
        assert not a_customer.orders.first().items.exists()

    def test_patch_via_post(self, client, a_customer, an_order):
        client.login(username='bob', password='12345')
        response = client.post(reverse('orders'), data=an_order)

        assert response.status_code == 302
        assert a_customer.orders.first().items.first().quantity == 1

        an_item = {
                "item_id": a_customer.orders.first().items.first().id,
                "quantity": 7,
                "todo": 'alterar',
        }
        response = client.post(reverse('index'), data=an_item)
        assert response.status_code == 302
        assert a_customer.orders.first().items.first().quantity == 7

    def test_patch_via_post_with_quantity_equals_zero_is_equivalent_to_delete(self, client, a_customer, an_order):
        client.login(username='bob', password='12345')
        response = client.post(reverse('orders'), data=an_order)

        assert response.status_code == 302
        assert a_customer.orders.first().items.first().quantity == 1

        an_item = {
                "item_id": a_customer.orders.first().items.first().id,
                "quantity": 0,
                "todo": 'alterar',
        }
        response = client.post(reverse('index'), data=an_item)
        assert response.status_code == 302
        assert not a_customer.orders.first().items.exists()
