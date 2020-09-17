
from django.urls import reverse
from ..views import Shop


class TestViewIndex:
    def test_get(self, client):
        response = client.get(reverse('index'))
        assert response.status_code == 200

    def test_post(self, client, a_customer, avocado):
        an_order = {
                # "user_id": a_customer.id, 
                "order_id": a_customer.orders.first().id, 
                "product_id": avocado.id,
                "qtd": 1,
        }
        response = client.post(reverse('index'), data=an_order)
        assert response.status_code == 302

    def test_delete(self, client, a_customer, avocado):
        an_order = {
                # "user_id": a_customer.id, 
                "order_id": a_customer.orders.first().id, 
                "product_id": avocado.id,
                "qtd": 1,
        }
        response = client.post(reverse('index'), data=an_order)
        assert response.status_code == 302

        a_pick = {
                "pick_id": a_customer.orders.first().picks.first().id, 
        }
        response = client.delete(reverse('index'), data=a_pick)
        assert response.status_code == 302

    def test_delete_via_post(self, client, a_customer, avocado):
        an_order = {
                # "user_id": a_customer.id, 
                "order_id": a_customer.orders.first().id, 
                "product_id": avocado.id,
                "qtd": 1,
        }
        response = client.post(reverse('index'), data=an_order)
        assert response.status_code == 302

        a_pick = {
                "pick_id": a_customer.orders.first().picks.first().id, 
                "_method": 'DELETE',
        }
        response = client.post(reverse('index'), data=a_pick)
        assert response.status_code == 302
