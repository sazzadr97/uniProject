from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm

class signUpForm(UserCreationForm):
    # Change from textfield into datepicker
    dob = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))   
    class Meta:
        model = CustomUser
        # Order of info required at signup
        fields = ["username", "first_name", "last_name", "email", "dob", "password1", "password2"]