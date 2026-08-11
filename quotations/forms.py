from django import forms
from .models import Quotation


class QuoteRequestForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = [
            'name', 'phone', 'email', 'pickup', 'destination',
            'goods_type', 'weight', 'quantity', 'vehicle_type', 'distance'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Aapka naam', 'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'placeholder': '9876543210', 'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Optional', 'class': 'form-input'}),
            'pickup': forms.TextInput(attrs={'placeholder': 'Dhamtari', 'class': 'form-input'}),
            'destination': forms.TextInput(attrs={'placeholder': 'Raipur', 'class': 'form-input'}),
            'goods_type': forms.TextInput(attrs={'placeholder': 'Furniture', 'class': 'form-input'}),
            'weight': forms.TextInput(attrs={'placeholder': '500 KG', 'class': 'form-input'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-input'}),
            'vehicle_type': forms.Select(attrs={'class': 'form-input'}),
            'distance': forms.NumberInput(attrs={'placeholder': 'KM (manual ya auto)', 'class': 'form-input'}),
        }


class AdminQuoteEditForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = ['base_fare', 'discount', 'is_approved']
        widgets = {
            'base_fare': forms.NumberInput(attrs={'class': 'form-input'}),
            'discount': forms.NumberInput(attrs={'class': 'form-input'}),
        }
