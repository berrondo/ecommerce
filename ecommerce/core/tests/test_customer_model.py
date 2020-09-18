import pytest
from django.core.exceptions import ValidationError


class TestCustomerAndOrder:
    def test_a_customer_is_created_in_the_correct_group_with_an_opened_order(self, a_customer, order_1):
        assert a_customer.groups.first().name == 'customers'
        assert order_1.status == 'OPENED'
        assert order_1.get_status_display() == 'Aberto'

    def test_a_costumer_must_always_have_one_and_only_one_opened_order(self, a_customer, order_1):
        # even if he checks it out...
        order_1.checkout()

        assert a_customer.orders.count() == 2

        assert order_1.status == 'TO_BE_SHIPPED'
        assert order_1.get_status_display() == 'Pendente'

        last_order = a_customer.orders.last()

        assert last_order.status == 'OPENED'
        assert last_order.get_status_display() == 'Aberto'

        # or delete it
        last_order.delete()

        assert a_customer.orders.count() == 2
        assert a_customer.orders.last().status == 'OPENED'
        assert a_customer.orders.last().get_status_display() == 'Aberto'


    def test_the_default_quantity_for_a_chosen_product_is_1(self, a_customer, avocado, order_1):
        item = order_1.add_product(avocado)

        assert item.product.name == 'Abacate'
        assert item.quantity == 1

    def test_a_costumer_can_add_one_product_to_his_cart(self, a_customer, avocado, order_1):
        item = order_1.add_product(avocado, 1)

        assert item.product.name == 'Abacate'
        assert item.quantity == 1

    def test_a_costumer_can_change_the_quantity_of_a_chosen_product(self, a_customer, avocado, order_1):
        item = order_1.add_product(avocado, 1)
        assert item.quantity == 1

        item = order_1.add_product(avocado, 3)
        assert item.quantity == 3

    def test_a_costumer_can_exclude_a_product_from_his_cart(self, a_customer, avocado, order_1):
        item = order_1.add_product(avocado, 3)
        assert item.quantity == 3

        item = order_1.remove_product(avocado)
        assert not item
        assert not order_1.picks.exists()

        # deleting again...
        item = order_1.remove_product(avocado)
        assert not item
        assert not order_1.picks.exists()

    def test_setting_the_quantity_of_a_product_to_zero_is_equivalent_to_delete_it(self, a_customer, avocado, order_1):
        item = order_1.add_product(avocado, 3)
        assert item.quantity == 3

        item = order_1.add_product(avocado, 0)
        assert not item
        assert not order_1.picks.exists()

    def test_costumer_checkout_finalizes_the_order(self, a_customer, avocado, banana, order_1):
        order_1.add_product(avocado, 3)
        order_1.add_product(banana, 2)
        order_1.checkout()

        assert order_1.status == 'TO_BE_SHIPPED'
        assert order_1.get_status_display() == 'Pendente'

    def test_costumer_should_not_alter_a_not_opened_order(self, avocado, order_1):
        order_1.add_product(avocado, 3)

        order_1.checkout()
        assert order_1.status == 'TO_BE_SHIPPED'
        assert order_1.get_status_display() == 'Pendente'

        with pytest.raises(ValidationError):
            order_1.add_product(avocado, 2)

        with pytest.raises(ValidationError):
            order_1.remove_product(avocado)

        with pytest.raises(ValidationError):
            order_1.delete()
