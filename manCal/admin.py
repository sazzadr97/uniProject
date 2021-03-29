from django.contrib import admin
from .models import CustomUser, Event, EventMember
from .forms import signUpForm
from django.contrib.auth.admin import UserAdmin


admin.site.register(CustomUser)
admin.site.register(Event)
admin.site.register(EventMember)


