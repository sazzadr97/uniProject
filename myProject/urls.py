from django.contrib import admin
from django.urls import path, include
from manCal import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('django.contrib.auth.urls')),
    path('signup/', views.signUpView, name="signup" ),
    path('', views.indexView, name="index"),
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('', include('manCal.urls')),
]
