from django import forms
from .models import Review, ContactMessage


class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review

        fields = [
            "booking",
            "rating",
            "review",
        ]

        widgets = {

            "booking": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "rating": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "review": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Write your experience with Ghidora Transport..."
                }
            ),

        }


class ContactMessageForm(forms.ModelForm):

    class Meta:
        model = ContactMessage
        fields = ["name", "phone", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Aapka naam"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Mobile number"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email (optional)"}),
            "subject": forms.TextInput(attrs={"class": "form-control", "placeholder": "Subject"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Apna message likhein..."}),
        }