import pytest
from django.core.exceptions import ValidationError


class TestCustomerAndOrder:
    def test_a_customer_is_created_in_the_correct_group_with_an_opened_order(self, a_customer, order_1):
        assert a_customer.groups.first().name == 'customers'
        assert a_customer.is_customer()

        assert order_1.status == 'OPENED'
        assert order_1.get_status_display() == 'Aberto'
        assert a_customer.get_opened_order() == order_1

    def test_the_default_quantity_for_a_chosen_product_is_1(self, avocado, order_1):
        item = order_1.add_item(avocado)

        assert item.product.name == 'Abacate'
        assert item.quantity == 1

    def test_a_customer_can_add_one_product_to_his_cart(self, avocado, order_1):
        item = order_1.add_item(avocado, 1)

        assert item.product.name == 'Abacate'
        assert item.quantity == 1

    def test_a_customer_can_change_the_quantity_of_a_chosen_product(self, avocado, order_1):
        item = order_1.add_item(avocado, 1)
        assert item.quantity == 1

        item = order_1.update_item(avocado, 3)
        assert item.quantity == 3

    def test_a_customer_can_exclude_a_product_from_his_cart(self, avocado, order_1):
        item = order_1.add_item(avocado, 3)
        assert item.quantity == 3

        item = order_1.remove_item(avocado)
        assert not item
        assert not order_1.picks.exists()

        # deleting again...
        item = order_1.remove_item(avocado)
        assert not item
        assert not order_1.picks.exists()

    def test_setting_the_quantity_of_a_product_to_zero_is_equivalent_to_delete_it(self, avocado, order_1):
        item = order_1.add_item(avocado, 3)
        assert item.quantity == 3

        item = order_1.add_item(avocado, 0)
        assert not item
        assert not order_1.picks.exists()

    def test_customer_checkout_finalizes_the_order(self, avocado, banana, order_1):
        order_1.add_item(avocado, 3)
        order_1.add_item(banana, 2)
        order_1.checkout()

        assert order_1.status == 'TO_BE_SHIPPED'
        assert order_1.get_status_display() == 'Pendente'

    def test_customer_should_not_alter_a_not_opened_order(self, avocado, order_1):
        order_1.add_item(avocado, 3)

        order_1.checkout()
        assert order_1.status == 'TO_BE_SHIPPED'
        assert order_1.get_status_display() == 'Pendente'

        with pytest.raises(ValidationError):
            order_1.add_item(avocado, 2)

        with pytest.raises(ValidationError):
            order_1.remove_item(avocado)

        with pytest.raises(ValidationError):
            order_1.delete()

    def test_should_not_be_possible_to_checkout_or_delete_an_empty_order(self, order_1):
        with pytest.raises(ValidationError):
            order_1.checkout()

        with pytest.raises(ValidationError):
            order_1.delete()

