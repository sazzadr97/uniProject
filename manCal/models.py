from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField()


class Event(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_date = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=200, null=True, blank=True)
   

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('manCal:event-detail', args=(self.id,))

    @property
    def get_html_url(self):
        url = reverse('manCal:event-detail', args=(self.id,))
        return f'<a href="{url}"> {self.title} </a>'


class EventMember(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['event', 'user']

    def __str__(self):
        return str(self.user)

class EventFiles(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    files = models.FileField()
    
class Notes(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    note = models.TextField()
    complited = models.BooleanField(default=False)

    def __str__(self):
        return str(self.note)
    class Meta:
        ordering = ['complited', 'id']

class Locations(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    location = models.TextField()

    def __str__(self):
        return str(self.location)

class Exercise(models.Model):
    user = user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    Lunges_set = models.IntegerField()
    Lunges_rep = models.IntegerField()
    Pushups_set = models.IntegerField()
    Pushups_rep = models.IntegerField()
    Squats_set = models.IntegerField()
    Squats_rep = models.IntegerField()
    Burpees_set = models.IntegerField()
    Burpees_rep = models.IntegerField()
    Planks_set = models.IntegerField()
    Planks_rep = models.IntegerField()

    def __str__(self):
        return str(self.user)