from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from .core import views


router = routers.DefaultRouter()
router.register(r'orders', views.OrderViewSet)
router.register(r'products', views.ProductViewSet)
# router.register(r'productorders', views.ProductOrderViewSet)


urlpatterns = [
    path('', views.index, name='index'),

    path('orders/',
         views.OrderView.as_view(), name='order'),
    path('orders/<int:pk>/',
         views.OrderUpdateView.as_view(), name='order-update'),
    path('orders/<slug:to_status>/<int:pk>/',
         views.OrderStatusView.as_view(), name='order-status'),

    path('orders/<int:order_pk>/items/<int:item_pk>',
         views.OrderItemUpdateView.as_view(), name='order-item-update'),
    path('orders/<int:order_pk>/items/<int:item_pk>/delete',
         views.OrderItemDeleteView.as_view(), name='order-item-delete'),

    path('products/',
         views.ProductView.as_view(), name='product'),
    path('products/add',
         views.ProductCreateView.as_view(), name='product-create'),
    path('products/<int:pk>',
         views.ProductUpdateView.as_view(), name='product-update'),
    path('products/<int:pk>/delete',
         views.ProductDeleteView.as_view(), name='product-delete'),

    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api/', include(router.urls)),
]
