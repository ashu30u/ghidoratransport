from django import forms
from .models import Comment, Post, Profile, Reel, Story




class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["content", "image", "location"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Write a caption...",
                    "class": "post-input",
                }
            ),
            "location": forms.TextInput(
                attrs={
                    "placeholder": "Add location (e.g. Raipur, CG)",
                    "class": "ig-input",
                }
            ),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.TextInput(
                attrs={
                    "placeholder": "Add a comment...",
                    "class": "comment-input",
                    "autocomplete": "off",
                }
            ),
        }


import re
from django.contrib.auth.models import User

class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=False, label="Name")
    username = forms.CharField(max_length=50, required=True, label="Username")

    class Meta:
        model = Profile
        fields = ["avatar", "bio", "note", "website", "gender"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 3, "maxlength": 200, "placeholder": "Bio..."}),
            "note": forms.TextInput(attrs={"placeholder": "Note... (e.g. Infinite ∞...)", "maxlength": 60}),
            "website": forms.URLInput(attrs={"placeholder": "Website..."}),
            "gender": forms.Select(choices=[("Male", "Male"), ("Female", "Female"), ("Custom", "Custom"), ("Prefer not to say", "Prefer not to say")]),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, "user") and self.instance.user:
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["username"].initial = self.instance.user.username

    def clean_username(self):
        username = self.cleaned_data.get("username", "").strip()
        if not username:
            raise forms.ValidationError("Username cannot be empty.")
        if len(username) < 2:
            raise forms.ValidationError("Username must be at least 2 characters long.")
        if not re.match(r"^[a-zA-Z0-9._]+$", username):
            raise forms.ValidationError("Usernames can only use letters, numbers, underscores, and periods.")
        
        # Check uniqueness excluding self
        user_id = self.instance.user.pk if (self.instance and hasattr(self.instance, "user") and self.instance.user) else None
        qs = User.objects.filter(username__iexact=username)
        if user_id:
            qs = qs.exclude(pk=user_id)
        if qs.exists():
            raise forms.ValidationError("This username is already taken. Please choose another one.")
        return username

    def save(self, commit=True):
        profile = super().save(commit=commit)
        if profile.user:
            first_name = self.cleaned_data.get("first_name", "").strip()
            username = self.cleaned_data.get("username", "").strip()
            if first_name is not None:
                profile.user.first_name = first_name
            if username:
                profile.user.username = username
            profile.user.save()
        return profile



class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ["media", "caption"]


class ReelForm(forms.ModelForm):
    class Meta:
        model = Reel
        fields = ["video", "caption", "audio_title"]
        widgets = {
            "caption": forms.Textarea(attrs={"rows": 2, "placeholder": "Write a caption for your reel...", "class": "ig-textarea"}),
            "audio_title": forms.TextInput(attrs={"placeholder": "Audio name (e.g. Original Audio)", "class": "ig-input"}),
        }

        widgets = {
            "caption": forms.TextInput(
                attrs={
                    "placeholder": "Add a story caption (optional)...",
                    "class": "comment-input",
                }
            ),
        }
