from django.contrib import admin
from .models import *
from .forms import signUpForm
from django.contrib.auth.admin import UserAdmin

""" list of table to be showen in the admin pannel """
admin.site.register(CustomUser)
admin.site.register(Event)
admin.site.register(EventMember)
admin.site.register(EventFiles)
admin.site.register(Notes)
admin.site.register(Locations)
admin.site.register(Exercise)




