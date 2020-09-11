from django.contrib import admin
from .models import Cart, Product, ProductCart


class PickInline(admin.TabularInline):
    model = ProductCart
    extra = 1

class ProductModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']


class CartModelAdmin(admin.ModelAdmin):
    inlines = (PickInline,)


admin.site.register(Cart, CartModelAdmin)
admin.site.register(Product, ProductModelAdmin)
admin.site.register(ProductCart)
