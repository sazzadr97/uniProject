from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'manCal'
urlpatterns = [
    path('index/', views.indexView, name="index"),
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('event/new/', views.create_event, name='event_new'),
    path('event/edit/<int:pk>/', views.EventEdit.as_view(), name='event_edit'),
    path('event/<int:event_id>/details/', views.event_details, name='event-detail'),
    path('add_eventmember/<int:event_id>', views.add_eventmember, name='add_eventmember'),
    path('event/<int:pk>/remove', views.EventMemberDeleteView.as_view(), name="remove_event"),
    path('event/<int:file_id>/<int:event_id>/fileremove', views.file_delete, name="remove_file"),
    path('event/addfiles/', views.add_files, name='add_files'),
    path('note/new_note/', views.add_note, name='add_note'),
    path('note/<int:note_id>/note_delete/', views.note_delete, name="note_delete"),
    path('weather/', views.weatherView, name='weather'),
    path('weather/<int:location_id>/location_delete/', views.location_delete, name="location_delete"),
    path('health/', views.healthView, name='health'),
    path('health/addExercise', views.addExercise, name='exercise_add'),

    path('profile/', views.profileView, name='profile'),



    
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)