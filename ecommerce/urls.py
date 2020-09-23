from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from .core import views


router = routers.DefaultRouter()
router.register(r'orders', views.OrderViewSet)
router.register(r'products', views.ProductViewSet)
# router.register(r'productorders', views.ProductOrderViewSet)


urlpatterns = [
    path('', views.Shop.as_view(), name='index'),
    path('orders/', views.OrderView.as_view(), name='orders'),
    path('products/', views.ProductView.as_view(), name='products'),
    path('managing/', views.managing, name='managing'),

    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api/', include(router.urls)),
]
