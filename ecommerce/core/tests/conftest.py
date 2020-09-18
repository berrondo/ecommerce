import pytest

from ..models import User, Product


@pytest.fixture(autouse=True)
def enable_db_access(db):
    pass


@pytest.fixture
def a_customer():
    return User.objects.create_customer(username='bob', password='12345')


@pytest.fixture
def order_1(a_customer):
    return a_customer.orders.first()


@pytest.fixture
def an_order(a_customer, avocado):
    return {
            "order_id": a_customer.orders.first().id, 
            "product_id": avocado.id,
            "quantity": 1,
    }


@pytest.fixture
def avocado():
    return Product.objects.create(name='Abacate', price=1.0)  


@pytest.fixture
def a_manager():
    return User.objects.create_manager(username='ann', password='54321')


@pytest.fixture
def banana():
    return Product.objects.create(name='Banana', price=2.0)  
