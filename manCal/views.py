from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from .forms import signUpForm, EventForm, AddMemberForm, AddLocation
import requests
from datetime import datetime, date
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.utils.safestring import mark_safe
from datetime import timedelta, date
import calendar
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from .models import *
from .utils import Calendar

from django.contrib.auth.forms import UserCreationForm

@login_required
def indexView(request):

    user = CustomUser.objects.get(username= request.user)
    today = datetime.today()
    start_time = today.replace(hour=23, minute=59)
    end_time = today.replace(hour=00, minute=1)
    events = Event.objects.filter(user = user)
    notes = Notes.objects.filter(user=user)
    events_today = []
    for event in events:
        if event.start_time <= start_time and event.end_time >= end_time:
            event_today = {
                'event_id' : event.id,
                'start_time': event.start_time,
                'end_time' : event.end_time,
                'content' : event.description,
                'title': event.title 
            }
            events_today.append(event_today) 
    context = {
        'events_today' : events_today,
        'notes' : notes
    }
    return render(request, "index.html", context)

@login_required
def homeView(request):
    if request.user.is_authenticated:
         return redirect("manCal:index")
    return render(request, 'home.html')


def loginView(request):
    # Get username and password from request
    username = request.POST['username']
    password = request.POST['password']

    # Authenticate the user, if it exist returns a user object, otherwise an None
    user = authenticate(request, username=username, password=password)

    # If user is authenticated
    if user is not None:

        # Save username and password to the session, plus loggedin variable set to True
        request.session['username'] = username
        request.session['password'] = password
        context = {
            'username': username,
            'password': password,
            'loggedin': True
        }

        response = render(request, 'index.html', context)

        # Remember last login in cookie
        now = D.datetime.utcnow()
        max_age = 365 * 24 * 60 * 60  #one year
        delta = now + D.timedelta(seconds=max_age)
        format = "%a, %d-%b-%Y %H:%M:%S GMT"
        expires = D.datetime.strftime(delta, format)
        response.set_cookie('last_login',now,expires=expires)

        #return response
        return redirect("/index")

    else:
        Http404('Wrong credentials')

# If logged in, session variables are cleaned up and user logged out. Otherwise redirected to login page
@login_required
def logoutView(request):
    logout(request)

def signUpView(request):
    if request.method == "POST":
        form = signUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Registration Successful!")
            return redirect("/login")
        else:
            print('failed after falidation')
    else:
        form = signUpForm()
    
    return render(request, "signup.html", {"form": form})



@login_required
def profileView(request):
    
    if request.method == 'POST':
        user = CustomUser.objects.get(username= request.user)
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        user.first_name= first_name
        user.last_name = last_name
        user.email=email
        user.save()
        return redirect("manCal:profile")

    context = {
        
    }

    return render(request, "profile.html", context)

def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return datetime.today()

def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month

def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month

class CalendarView(LoginRequiredMixin, generic.ListView):
    model = Event
    template_name = 'calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get('month', None))
        user = CustomUser.objects.get(username= self.request.user)
        cal = Calendar(d.year, d.month, user)
        html_cal = cal.formatmonth(withyear=True)
        notes = Notes.objects.filter(user=user)
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        context['notes'] = notes
        context['user']= user
        return context


@login_required
def create_event(request):    
    form = EventForm(request.POST or None)
    if request.POST and form.is_valid():
        title = form.cleaned_data['title']
        description = form.cleaned_data['description']
        start_time = form.cleaned_data['start_time']
        end_time = form.cleaned_data['end_time']
        location = form.cleaned_data['location']
        Event.objects.get_or_create(
            user=request.user,
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            location= location
        )
        return HttpResponseRedirect(reverse('manCal:calendar'))
    return render(request, 'event.html', {'form': form})

class EventEdit(LoginRequiredMixin, generic.UpdateView):
    model = Event
    fields = ['title', 'description', 'start_time', 'end_time', 'location']
    template_name = 'event.html'




class EventDelete(LoginRequiredMixin, generic.DeleteView):
    model = Event
    template_name = 'event_delete.html'
    success_url = reverse_lazy('manCal:calendar')
    
    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            return redirect('manCal:calendar')
        else:
            return super(EventDelete, self).post(request, *args, **kwargs)



@login_required
def event_details(request, event_id):
    event = Event.objects.get(id=event_id)
    eventmember = EventMember.objects.filter(event=event)
    eventfiles = EventFiles.objects.filter(event=event)
    API_KEY = 'AIzaSyDio4Zj99JOhP8SBQBM3CydIsc91ld-Jbs'
    address = event.location
    params = {
        'key' : API_KEY,
        'address': address
    }
    lat = 51.509865
    lon = -0.118092
    base_url = 'https://maps.googleapis.com/maps/api/geocode/json?'
    response = requests.get(base_url, params=params).json()
    
    if response['status'] == 'OK':
        geometry = response['results'][0]['geometry']
        
        #check if lat and lgn are obtained correctly
        lat = geometry['location']['lat']
        print(lat)
        lon = geometry['location']['lng']
        print(lon)

    context = {
        'event': event,
        'eventmember': eventmember,
        'eventfiles': eventfiles,
        'lat' : lat,
        'lon' : lon,

    }
    return render(request, 'event-details.html', context)



@login_required
def weatherView(request):
    url = 'http://api.openweathermap.org/data/2.5/onecall?lat={lat}&exclude=hourly,minutely&lon={lon}&units=metric&appid=dbd607d4b59f61a34125bf4f2a185f8d'
    user = CustomUser.objects.get(username= request.user)
    API_KEY = 'AIzaSyDio4Zj99JOhP8SBQBM3CydIsc91ld-Jbs'
    base_url = 'https://maps.googleapis.com/maps/api/geocode/json?'
    err_msg=''
    message= ''
    message_class=''

    if request.method == 'POST':
        location = request.POST.get('location')
        cityCount = Locations.objects.filter(user=user).filter(location = location).count()
        form = AddLocation(request.POST)
        print(location)
        if form.is_valid():
            if cityCount == 0:
                params = {
                'key' : API_KEY,
                'address': location
                }
                response_test = requests.get(base_url, params=params).json()
                if response_test['status'] == 'OK':
                    obj= form.save(commit=False)
                    obj.user = user
                    obj.save()
                    messages.success(request,"Location add.")
                    return redirect('manCal:weather')

                else:
                    messages.warning(request, "Location not found" )
                    return redirect('manCal:weather')
            if cityCount > 0:
                messages.warning(request, "Location already added" )
                return redirect('manCal:weather')   
        return redirect('manCal:weather')

    form = AddLocation()
    cities = Locations.objects.filter(user=user)

    weather_data = []

    for city in cities:
        params = {
        'key' : API_KEY,
        'address': city.location
        }
        
        response = requests.get(base_url, params=params).json()
        
        if response['status'] == 'OK':
            geometry = response['results'][0]['geometry']
            
            #check if lat and lgn are obtained correctly
            lat = geometry['location']['lat']
            lon = geometry['location']['lng']

            r = requests.get(url.format(lat=lat, lon=lon)).json()
            city_weather = {
                
                'location_id' : city.id,
                'city' : city.location,
                'temperature' : round(r['current']['temp']),
                'main' : r['daily'][0]['weather'][0]['main'],
                'icon' : r['daily'][0]['weather'][0]['icon'],
                'tempMax' : round(r['daily'][0]['temp']['max']),
                'tempMin' : round(r['daily'][0]['temp']['min']),
            }

        weather_data.append(city_weather)
    
    context = {
        'form' : form,
        'weather_data' : weather_data,
    }
    return render(request, 'weather.html', context)


@login_required
def add_eventmember(request, event_id):
    forms = AddMemberForm()
    if request.method == 'POST':
        forms = AddMemberForm(request.POST)
        if forms.is_valid():
            member = EventMember.objects.filter(event=event_id)
            event = Event.objects.get(id=event_id)
            if member.count() <= 9:
                user = forms.cleaned_data['user']
                EventMember.objects.create(
                    event=event,
                    user=user
                )
                return redirect('manCal:event-detail', event_id = event.id,)
            else:
                print('--------------User limit exceed!-----------------')
    context = {
        'form': forms
    }
    return render(request, 'add_member.html', context)


class EventMemberDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = EventMember
    template_name = 'event_delete.html'
    success_url = reverse_lazy('manCal:calendar')

    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            return redirect('manCal:calendar')
        else:
            return super(EventMemberDeleteView, self).post(request, *args, **kwargs)

@login_required
def file_delete(request, file_id, event_id):
    file = EventFiles.objects.get(id = file_id)
    file.delete()
    return redirect('manCal:event-detail', event_id = event_id,)

@login_required
def location_delete(request, location_id):
    location = Locations.objects.get(id = location_id)
    location.delete()
    return redirect('manCal:weather')

@login_required
def add_files(request):
    event_id = request.POST.get('event_id')
    event = Event.objects.get(id=event_id)
    files = request.FILES.getlist('files')
    for file in files:
        fs= FileSystemStorage()
        file_path = fs.save(file.name, file)
        sfile= EventFiles(event = event, files = file_path)
        sfile.save()


    return redirect('manCal:event-detail', event_id = event_id,)

@login_required
def add_note(request):
    user = CustomUser.objects.get(username= request.user)
    note = request.POST.get('note')
    if request.method == 'POST':
        Notes.objects.create(
            user = user,
            note = note
        )

    return redirect('manCal:calendar', )

@login_required
def note_delete(request, note_id):
    note= Notes.objects.get(id= note_id)
    note.delete()
    return redirect('manCal:calendar')


@login_required
def healthView(request):
    user = CustomUser.objects.get(username= request.user)
    
    if Exercise.objects.filter(user= user).exists():
        exercise = Exercise.objects.get(user= user)
        context = {
            'exercise' : exercise
        }
        return render(request, 'health.html', context)
    
    return render(request, 'health.html')

@login_required
def addExercise(request):
    if request.method == 'POST':
        user = CustomUser.objects.get(username= request.user)
        lunges_set = int(request.POST.get('Lunges_set'))
        lunges_rep = int(request.POST.get('Lunges_rep'))
        pushups_set = int(request.POST.get('Pushups_set'))
        pushups_rep = int(request.POST.get('Pushups_rep'))
        squats_set = int(request.POST.get('Squats_set'))
        squats_rep = int(request.POST.get('Squats_rep'))
        burpees_set = int(request.POST.get('Burpees_set'))
        burpees_rep = int(request.POST.get('Burpees_rep'))
        planks_set = int(request.POST.get('Planks_set'))
        planks_rep = int(request.POST.get('Planks_rep'))
        if not Exercise.objects.filter(user= user).exists():
            Exercise.objects.create(
                user= user,
                Lunges_set = lunges_set,
                Lunges_rep = lunges_rep,
                Pushups_set = pushups_set,
                Pushups_rep = pushups_rep,
                Squats_set = squats_set,
                Squats_rep = squats_rep,
                Burpees_set = burpees_set,
                Burpees_rep = burpees_rep,
                Planks_set = planks_set,
                Planks_rep = planks_rep
            )
            return redirect("manCal:health")
        else:
            exercise = Exercise.objects.get(user= user)
            exercise.Lunges_set = lunges_set
            exercise.Lunges_rep = lunges_rep
            exercise.Pushups_set = pushups_set
            exercise.Pushups_rep = pushups_rep
            exercise.Squats_set = squats_set
            exercise.Squats_rep = squats_rep
            exercise.Burpees_set = burpees_set
            exercise.Burpees_rep = burpees_rep
            exercise.Planks_set = planks_set
            exercise.Planks_rep = planks_rep
            exercise.save()
            return redirect("manCal:health")
