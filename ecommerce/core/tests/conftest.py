import pytest

from ..models import create_user, Product


@pytest.fixture(autouse=True)
def enable_db_access(db):
    pass


@pytest.fixture
def a_customer():
    return create_user(username='bob', password='12345')


@pytest.fixture
def order_1(a_customer):
    return a_customer.orders.first()


@pytest.fixture
def an_order(a_customer, avocado):
    return {
            "product_id": avocado.id,
            "quantity": 1,
            "todo": "comprar",
    }


@pytest.fixture
def avocado():
    return Product.objects.create(name='Abacate', price=1.0)  


@pytest.fixture
def a_manager():
    return create_user(username='ann', password='54321', in_group='managers')


@pytest.fixture
def banana():
    return Product.objects.create(name='Banana', price=2.0)  
