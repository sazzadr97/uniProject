from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm

class signUpForm(UserCreationForm):
    # Change from textfield into datepicker 
    class Meta:
        model = CustomUser
        # Order of info required at signup
        fields = ["username", "email", "password1", "password2"]