from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.conf import settings

"""  model used in the application """
"""  creation of user model adding the email field """
class CustomUser(AbstractUser):
    email = models.EmailField()


class Event(models.Model):
    """ connecting the user and event model with user foreign key """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_date = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=200, null=True, blank=True)
   

    def __str__(self):
        return self.title
    
    """ absolute URL to be used in te creation of the calendar """
    def get_absolute_url(self):
        return reverse('manCal:event-detail', args=(self.id,))

    """ generating html url to be added to the event in the calendar """
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
    
    """ defining elements order """
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