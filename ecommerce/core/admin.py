from django.contrib import admin
from .models import Order, Product, OrderItem


class PickInline(admin.TabularInline):
    model = OrderItem
    extra = 1

class ProductModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']


class CartModelAdmin(admin.ModelAdmin):
    inlines = (PickInline,)


admin.site.register(Order, CartModelAdmin)
admin.site.register(Product, ProductModelAdmin)
admin.site.register(OrderItem)
