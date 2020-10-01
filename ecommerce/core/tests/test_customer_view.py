from django.urls import reverse as r

from ..models import Product


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

        data = {
             "todo": 'excluir',
        }
        response = client.post(r('order-item-update', args=[1, 1]), data, follow=True)
        assert response.status_code == 200
        assert not a_customer.orders.first().items.exists()

    def test_patch_via_post_to_update_an_item_fields(self, client, a_customer, add_item):
        assert add_item.status_code == 200
        assert a_customer.orders.first().items.first().quantity == 1

        data = {
            "quantity": 7,
            "todo": 'alterar',
        }
        response = client.post(r('order-item-update', args=[1, 1]), data, follow=True)
        assert response.status_code == 200
        assert a_customer.orders.first().items.first().quantity == 7

    def test_patch_via_post_with_quantity_equals_zero_is_equivalent_to_delete(self, client, a_customer, add_item):
        assert add_item.status_code == 200
        assert a_customer.orders.first().items.first().quantity == 1

        data = {
            "quantity": 0,
            "todo": 'alterar',
        }
        response = client.post(r('order-item-update', args=[1, 1]), data, follow=True)
        assert response.status_code == 200
        assert not a_customer.orders.first().items.exists()


class TestCustomerCheckingOutOrder:
    def test_a_customer_can_checkout_his_opened_order(self, client, a_customer, add_item):
        response = client.post(r('order-status-update', args=[1, 'pending']), follow=True)
        assert 'vazio' in str(response.content)


class TestCustomerCantDo:
    def test_a_customer_can_not_add_product(self, client_w_customer):
        data = dict(
            name='Abacate',
            price=0.01,
            is_active=True,
        )
        response = client_w_customer.post(r('product-create'), data, follow=True)
        assert 'bob' not in str(response.content)
        assert not Product.objects.exists()
        assert response.status_code == 403

    def test_a_customer_can_not_edit_product(self, register_product, client_w_customer):
        data = dict(
            name='Abacateeeeeeeeeeeeeeeeeeee',
            price=0.01,
            is_active=True,
        )
        response = client_w_customer.post(r('product-update', args=[1]), data, follow=True)
        assert 'bob' not in str(response.content)
        assert Product.objects.first().name == 'Abacate'
        assert response.status_code == 403

    def test_a_customer_can_not_delete_product(self, register_product, client_w_customer):
        response = client_w_customer.post(r('product-delete', args=[1]), follow=True)
        assert 'bob' not in str(response.content)
        assert Product.objects.exists()
        assert response.status_code == 403

    def test_a_customer_can_not_mess_with_another_customer_order(self, client, a_customer, add_item, another_customer):
        assert a_customer.orders.first().items.first().product.name == 'Abacate'

        client.logout()
        client.login(username=another_customer.username, password='90')

        response = client.get(r('index'))
        assert response.status_code == 200
        assert 'joe' in str(response.content)

        data = {
            "quantity": 7,
            "todo": 'alterar',
        }
        response = client.post(r('order-item-update', args=[1, 1]), data, follow=True)
        assert response.status_code == 403
