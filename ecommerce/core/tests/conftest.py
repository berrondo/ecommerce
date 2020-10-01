import pytest
from django.urls import reverse as r

from ..models import create_user, Product


@pytest.fixture(autouse=True)
def enable_db_access(db):
    pass


@pytest.fixture
def a_manager():
    return create_user(username='ann', password='54321', in_group='managers')


@pytest.fixture
def a_customer():
    return create_user(username='bob', password='12345')


@pytest.fixture
def client_w_customer(client, a_customer):
    client.login(username=a_customer.username, password='12345')
    return client


@pytest.fixture
def another_customer():
    return create_user(username='joe', password='90')


@pytest.fixture()
def add_item(client_w_customer, an_order):
    response = client_w_customer.post(r('order-update', args=[1]), data=an_order, follow=True)
    return response


@pytest.fixture()
def client_w_manager(client, a_manager):
    client.login(username='ann', password='54321')
    return client


@pytest.fixture()
def register_product(client_w_manager):
    data = dict(
        name='Abacate',
        price=0.01,
        is_active=True,
    )
    response = client_w_manager.post(r('product-create'), data, follow=True)
    return response


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
def banana():
    return Product.objects.create(name='Banana', price=2.0)


@pytest.fixture
def no_active_product():
    return Product.objects.create(name='Uva', price=2.0, is_active=False)
