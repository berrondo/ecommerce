from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    # id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Product
        fields = ['name', 'price']
