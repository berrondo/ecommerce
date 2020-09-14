from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from .core import views


router = routers.DefaultRouter()
router.register(r'orders', views.OrderViewSet)
# router.register(r'products', views.ProductViewSet)
# router.register(r'productorders', views.ProductOrderViewSet)


urlpatterns = [
    path('', views.home, name='home'),
    path('pedidos/<int:id_pedido>/produtos/<int:id_produto>/quantidade/<int:qtd>', 
         views.Comprar.as_view(), name='comprar'),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api/', include(router.urls)),
]
