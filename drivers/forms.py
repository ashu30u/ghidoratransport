from django import forms
from .models import Driver, Vehicle


class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['name', 'mobile', 'photo', 'license_number', 'address', 'experience_years', 'status', 'is_default']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ramesh Kumar', 'class': 'form-input'}),
            'mobile': forms.TextInput(attrs={'placeholder': '9876543210', 'class': 'form-input'}),
            'license_number': forms.TextInput(attrs={'placeholder': 'CG123456789', 'class': 'form-input'}),
            'address': forms.TextInput(attrs={'placeholder': 'Dhamtari', 'class': 'form-input'}),
            'experience_years': forms.NumberInput(attrs={'placeholder': '5', 'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
        }


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['vehicle_number', 'vehicle_type', 'capacity', 'vehicle_image', 'rc_number']
        widgets = {
            'vehicle_number': forms.TextInput(attrs={'placeholder': 'CG05 AB 1234', 'class': 'form-input'}),
            'vehicle_type': forms.TextInput(attrs={'placeholder': 'Mahindra Pickup', 'class': 'form-input'}),
            'capacity': forms.TextInput(attrs={'placeholder': '1 Ton', 'class': 'form-input'}),
            'rc_number': forms.TextInput(attrs={'placeholder': 'RC Number', 'class': 'form-input'}),
        }
