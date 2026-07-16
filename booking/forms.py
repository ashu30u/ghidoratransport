from django import forms
from .models import Review


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