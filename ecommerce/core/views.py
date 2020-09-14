from django.shortcuts import render
from .models import Product, Order

def home(request):
    username = None
    if request.user.is_authenticated:
        username = request.user.username
    
    products = Product.objects.all()
    orders = list(Order.objects.filter(customer__username=username).all())
    return render(request, 'core/home.html', {'products': products, 'orders': orders})