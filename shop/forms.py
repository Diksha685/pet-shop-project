from django import forms
from django.contrib.auth.models import User
from .models import Pet

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, min_length=6)
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm password")

    class Meta:
        model = User
        fields = ("username", "email", "first_name")

    def clean(self):
        cleaned = super().clean()
        p = cleaned.get("password")
        p2 = cleaned.get("password2")
        if p and p2 and p != p2:
            self.add_error("password2", "Passwords do not match.")
        return cleaned

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ["name", "species", "age", "price", "description", "image_url"]
