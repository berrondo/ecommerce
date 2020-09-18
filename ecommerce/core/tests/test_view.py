
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
                "quantity": 1,
        }
        response = client.post(reverse('index'), data=an_order)
        assert response.status_code == 302
        assert a_customer.orders.first().picks.first().quantity == 1

    def test_delete_via_post(self, client, a_customer, avocado):
        an_order = {
                # "user_id": a_customer.id, 
                "order_id": a_customer.orders.first().id, 
                "product_id": avocado.id,
                "quantity": 1,
        }
        response = client.post(reverse('index'), data=an_order)
        assert response.status_code == 302
        assert a_customer.orders.first().picks.first().quantity == 1

        a_pick = {
                "pick_id": a_customer.orders.first().picks.first().id, 
                "todo": 'excluir',
        }
        response = client.post(reverse('index'), data=a_pick)
        assert response.status_code == 302
        assert not a_customer.orders.first().picks.exists()

    def test_patch_via_post(self, client, a_customer, avocado):
        an_order = {
                # "user_id": a_customer.id, 
                "order_id": a_customer.orders.first().id, 
                "product_id": avocado.id,
                "quantity": 1,
        }
        response = client.post(reverse('index'), data=an_order)
        assert response.status_code == 302
        assert a_customer.orders.first().picks.first().quantity == 1

        a_pick = {
                "pick_id": a_customer.orders.first().picks.first().id,
                "quantity": 7,
                "todo": 'alterar',
        }
        response = client.post(reverse('index'), data=a_pick)
        assert response.status_code == 302
        assert a_customer.orders.first().picks.first().quantity == 7

    # def test_delete(self, client, a_customer, avocado):
    #     an_order = {
    #             # "user_id": a_customer.id, 
    #             "order_id": a_customer.orders.first().id, 
    #             "product_id": avocado.id,
    #             "quantity": 1,
    #     }
    #     response = client.post(reverse('index'), data=an_order)
    #     assert response.status_code == 302

    #     a_pick = {
    #             "pick_id": a_customer.orders.first().picks.first().id, 
    #     }
    #     response = client.delete(reverse('index'), data=a_pick)
    #     assert response.status_code == 302

    # def test_patch(self, client, a_customer, avocado):
    #     an_order = {
    #             # "user_id": a_customer.id, 
    #             "order_id": a_customer.orders.first().id, 
    #             "product_id": avocado.id,
    #             "quantity": 1,
    #     }
    #     response = client.post(reverse('index'), data=an_order)
    #     assert response.status_code == 302
    #     assert a_customer.orders.first().picks.first().quantity == 1

    #     a_pick = {
    #             "pick_id": a_customer.orders.first().picks.first().id,
    #             "quantity": 7,
    #     }
    #     response = client.patch(reverse('index'), data=a_pick)
    #     assert response.status_code == 302
    #     assert a_customer.orders.first().picks.first().quantity == 7
