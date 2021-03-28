from django import forms
from .models import CustomUser, Event, EventMember
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, DateInput

class signUpForm(UserCreationForm):
    # Change from textfield into datepicker 
    class Meta:
        model = CustomUser
        # Order of info required at signup
        fields = ["username", "email", "password1", "password2"]

class EventForm(ModelForm):
  class Meta:
    model = Event
    # datetime-local is a HTML5 input type, format to make date time show on fields
    widgets = {
      'start_time': DateInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
      'end_time': DateInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
    }
    exclude = ['user']

  def __init__(self, *args, **kwargs):
    super(EventForm, self).__init__(*args, **kwargs)
    # input_formats to parse HTML5 datetime-local input to datetime field
    self.fields['start_time'].input_formats = ('%Y-%m-%dT%H:%M',)
    self.fields['end_time'].input_formats = ('%Y-%m-%dT%H:%M',)

class AddMemberForm(forms.ModelForm):
  class Meta:
    model = EventMember
    fields = ['user']