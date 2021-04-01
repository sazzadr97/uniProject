from django.contrib import admin
from django.urls import path, include
from manCal import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('django.contrib.auth.urls')),
    path('signup/', views.signUpView, name="signup" ),
    path('', include('manCal.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
