
from django.urls import reverse


class TestViewIndex:
    def test_get(self, client):
        response = client.get(reverse('index'))
        assert response.status_code == 200

    def test_post(self, client, a_customer, an_order):
        response = client.post(reverse('index'), data=an_order)

        assert response.status_code == 302
        assert a_customer.orders.first().picks.first().quantity == 1

    def test_post_the_same_product_twice(self, client, a_customer, an_order):
        response = client.post(reverse('index'), data=an_order)

        assert response.status_code == 302
        assert a_customer.orders.first().picks.first().quantity == 1

        # again...
        response = client.post(reverse('index'), data=an_order)
        assert response.status_code == 200
        assert "existe" in str(response.content)

    def test_delete_via_post(self, client, a_customer, an_order):
        response = client.post(reverse('index'), data=an_order)

        assert response.status_code == 302
        assert a_customer.orders.first().picks.first().quantity == 1

        an_item = {
                "pick_id": a_customer.orders.first().picks.first().id, 
                "todo": 'excluir',
        }
        response = client.post(reverse('index'), data=an_item)
        assert response.status_code == 302
        assert not a_customer.orders.first().picks.exists()

    def test_patch_via_post(self, client, a_customer, an_order):
        response = client.post(reverse('index'), data=an_order)

        assert response.status_code == 302
        assert a_customer.orders.first().picks.first().quantity == 1

        an_item = {
                "pick_id": a_customer.orders.first().picks.first().id,
                "quantity": 7,
                "todo": 'alterar',
        }
        response = client.post(reverse('index'), data=an_item)
        assert response.status_code == 302
        assert a_customer.orders.first().picks.first().quantity == 7

    def test_patch_via_post_with_quantity_equals_zero_is_equivalent_to_delete(self, client, a_customer, an_order):
        response = client.post(reverse('index'), data=an_order)

        assert response.status_code == 302
        assert a_customer.orders.first().picks.first().quantity == 1

        an_item = {
                "pick_id": a_customer.orders.first().picks.first().id,
                "quantity": 0,
                "todo": 'alterar',
        }
        response = client.post(reverse('index'), data=an_item)
        assert response.status_code == 302
        assert not a_customer.orders.first().picks.exists()




    # def test_delete(self, client, a_customer, avocado):
    #     an_order = {
    #             # "user_id": a_customer.id, 
    #             "order_id": a_customer.orders.first().id, 
    #             "product_id": avocado.id,
    #             "quantity": 1,
    #     }
    #     response = client.post(reverse('index'), data=an_order)
    #     assert response.status_code == 302

    #     an_item = {
    #             "pick_id": a_customer.orders.first().picks.first().id, 
    #     }
    #     response = client.delete(reverse('index'), data=an_item)
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

    #     an_item = {
    #             "pick_id": a_customer.orders.first().picks.first().id,
    #             "quantity": 7,
    #     }
    #     response = client.patch(reverse('index'), data=an_item)
    #     assert response.status_code == 302
    #     assert a_customer.orders.first().picks.first().quantity == 7
