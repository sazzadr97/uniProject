from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import signUpForm, EventForm, AddMemberForm, AddLocation
import requests
from datetime import datetime, date
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.views import generic
from django.utils.safestring import mark_safe
from datetime import timedelta, date
import calendar
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from .models import *
from .utils import Calendar
from django.forms.models import model_to_dict

from django.contrib.auth.forms import UserCreationForm
#the tag @login_required make it so that only logged user can access the view
@login_required
def indexView(request):
    # the view collects infromation from multiple table, event and returns them to the user
    user = CustomUser.objects.get(username= request.user)
    today = datetime.today()
    start_time = today.replace(hour=23, minute=59)
    end_time = today.replace(hour=00, minute=1)
    events = Event.objects.filter(user = user)
    notes = Notes.objects.filter(user=user)
    events_today = []
    for event in events:
        #filtering events to see which are active on the day
        if event.start_time <= start_time and event.end_time >= end_time:
            #adding event infromation in a dictionary
            event_today = {
                'event_id' : event.id,
                'start_time': event.start_time,
                'end_time' : event.end_time,
                'content' : event.description,
                'title': event.title 
            }
            #appending created dictionary
            events_today.append(event_today) 
    context = {
        'events_today' : events_today,
        'notes' : notes
    }

    return render(request, "index.html", context)

#homepage view
def homeView(request):
    #check if user is authenticated
    if request.user.is_authenticated:
        #if true render index
         return redirect("manCal:index")
    #else render homepage
    return render(request, 'home.html')

#login view
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

#registration
def signUpView(request):
    #checking if methos is POST
    if request.method == "POST":
        #getting from from request
        form = signUpForm(request.POST)
        #validateing from
        if form.is_valid():
            #if valid save and redirect to login with messege
            form.save()
            messages.success(request,"Registration Successful!")
            return redirect("/login")
        else:
        #error
            print('failed after falidation')
    else:
        #clean up form
        form = signUpForm()
    
    return render(request, "signup.html", {"form": form})


#view to updated account info
@login_required
def profileView(request):
    #checking request methos
    if request.method == 'POST':
        #extracting form infromation form request and storing them in local variable
        user = CustomUser.objects.get(username= request.user)
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        #updateding existing value with updated one
        user.first_name= first_name
        user.last_name = last_name
        user.email=email
        #save and redirect to same page
        user.save()
        return redirect("manCal:profile")

    context = {
        
    }

    return render(request, "profile.html", context)

# start calendar render views
#get date for starting calendar date
def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return datetime.today()
#action to go prev month
def prev_month(d):
    #changeing the day with which the calendar is started
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    #coverting and formatting data for html
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month
##same as prev_month
def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month
#calendar genric list view
class CalendarView(LoginRequiredMixin, generic.ListView):
    model = Event
    #template to render
    template_name = 'calendar.html'
    #setting up context data
    def get_context_data(self, **kwargs):
        #supercalss call
        context = super().get_context_data(**kwargs)
        #getting date for calendar start
        d = get_date(self.request.GET.get('month', None))
        user = CustomUser.objects.get(username= self.request.user)
        #pasing initializing variable for calendar
        cal = Calendar(d.year, d.month, user)
        html_cal = cal.formatmonth(withyear=True)
        #getting user notes
        notes = Notes.objects.filter(user=user)
        #defining new context data
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        context['notes'] = notes
        context['user']= user
        return context

#create events
@login_required
def create_event(request):    
    form = EventForm(request.POST or None)
    #checking if the request type is post and if the form is valid
    if request.POST and form.is_valid():
        #getting specific inputs from Django form and storing them in separated variable
        title = form.cleaned_data['title']
        description = form.cleaned_data['description']
        start_time = form.cleaned_data['start_time']
        end_time = form.cleaned_data['end_time']
        location = form.cleaned_data['location']
        #creating new event object
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

#generic update view for event edit
class EventEdit(LoginRequiredMixin, generic.UpdateView):
    #In which model the data are stored
    model = Event
    #fields to update
    fields = ['title', 'description', 'start_time', 'end_time', 'location']
    #template to use to get data
    template_name = 'event.html'

#generic delete vie for event delete
class EventDelete(LoginRequiredMixin, generic.DeleteView):
    model = Event
    template_name = 'event_delete.html'
    success_url = reverse_lazy('manCal:calendar')
    #overriding data in confermation form to provide cancel button
    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            return redirect('manCal:calendar')
        else:
            return super(EventDelete, self).post(request, *args, **kwargs)

#event details view
@login_required
def event_details(request, event_id):
    #locating event in database useing the event_id given in the url
    event = Event.objects.get(id=event_id)
    #getting members and files attached to the event
    eventmember = EventMember.objects.filter(event=event)
    eventfiles = EventFiles.objects.filter(event=event)
    #defining variables for API call
    API_KEY = 'AIzaSyDio4Zj99JOhP8SBQBM3CydIsc91ld-Jbs'
    address = event.location
    params = {
        'key' : API_KEY,
        'address': address
    }
    lat = 51.509865
    lon = -0.118092
    base_url = 'https://maps.googleapis.com/maps/api/geocode/json?'
    #API response conteining geo-cordinates
    response = requests.get(base_url, params=params).json()
    #checking if the request was succesful
    if response['status'] == 'OK':
        geometry = response['results'][0]['geometry']
        
        #obtaing latiture and longitude
        lat = geometry['location']['lat']
        lon = geometry['location']['lng']

    context = {
        #pasing retrived data to the template
        'event': event,
        'eventmember': eventmember,
        'eventfiles': eventfiles,
        'lat' : lat,
        'lon' : lon,

    }
    return render(request, 'event-details.html', context)


#weather view
@login_required
def weatherView(request):
    #API variable for weather API
    url = 'http://api.openweathermap.org/data/2.5/onecall?lat={lat}&exclude=hourly,minutely&lon={lon}&units=metric&appid=dbd607d4b59f61a34125bf4f2a185f8d'
    user = CustomUser.objects.get(username= request.user)
    #API variable for google API
    API_KEY = 'AIzaSyDio4Zj99JOhP8SBQBM3CydIsc91ld-Jbs'
    base_url = 'https://maps.googleapis.com/maps/api/geocode/json?'
    #chekc if the search form was submitted or the page was reloaded
    if request.method == 'POST':
        #if form submitted, get input from request
        location = request.POST.get('location')
        #check if location already exist
        cityCount = Locations.objects.filter(user=user).filter(location = location).count()
        form = AddLocation(request.POST)
        #validateing from
        if form.is_valid():
            if cityCount == 0:
                #if city does not exist in database
                params = {
                'key' : API_KEY,
                'address': location
                }
                #check if the location exist useing google API
                response_test = requests.get(base_url, params=params).json()
                if response_test['status'] == 'OK':
                    #if exist save city in database
                    obj= form.save(commit=False)
                    obj.user = user
                    obj.save()
                    #should be simple params not weather becasue we are useing Google API
                    paramsWeather = {
                        'key' : API_KEY,
                        'address': obj.location
                    }
                    #getting location cord
                    response = requests.get(base_url, params=paramsWeather).json()
                    if response['status'] == 'OK':
                        #if infomation available 
                        geometry = response['results'][0]['geometry']

                        lat = geometry['location']['lat']
                        lon = geometry['location']['lng']
                        #send request for weather information
                        r = requests.get(url.format(lat=lat, lon=lon)).json()
                        #adding info in dictionary
                        city_weather = {
                            
                            'location_id' : obj.id,
                            'city' : obj.location,
                            'temperature' : round(r['current']['temp']),
                            'main' : r['daily'][0]['weather'][0]['main'],
                            'icon' : r['daily'][0]['weather'][0]['icon'],
                            'tempMax' : round(r['daily'][0]['temp']['max']),
                            'tempMin' : round(r['daily'][0]['temp']['min']),
                        }
                        #return dictionary to Ajax reqeust with JsonResponse
                        return JsonResponse({'city_weather' : city_weather, 'errorCode' : "200"}, status= 200)  
                else:
                    return JsonResponse({'error' : "Location not found", 'errorCode' : "500"}, status= 200)
            elif cityCount > 0:
                return JsonResponse({'error' : "Location already added", 'errorCode' : "500"}, status= 200)   
        return JsonResponse({'error' : "Invalid input", 'errorCode' : "500"}, status= 200)

    form = AddLocation()
    #if the page was loaded without from submittion
    #get all weather location saved by the user
    cities = Locations.objects.filter(user=user)
    #create empty arrasy to store all weather data about each city
    weather_data = []

    #do the same thing as we did when a city was added for each city in the database
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
        #append the data for the city to weather_data before passing to the next city
        weather_data.append(city_weather)
    
    context = {
        'form' : form,
        'weather_data' : weather_data,
    }
    return render(request, 'weather.html', context)

#add a member for an event
@login_required
def add_eventmember(request, event_id):
    forms = AddMemberForm()
    #check request method
    if request.method == 'POST':
        #if POST validate and sabe 
        forms = AddMemberForm(request.POST)
        if forms.is_valid():
            member = EventMember.objects.filter(event=event_id)
            event = Event.objects.get(id=event_id)
            #maximum 9 member for event
            if member.count() <= 9:
                #save meber
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

#delete member
@login_required
def member_delete(request, member_id):
    #get member useing the member_id in the url
    member = EventMember.objects.get(id= member_id)
    #delete form database
    member.delete()
    #return succesfful response to Ajax request
    return JsonResponse({'result' : 'ok'}, status=200)

#delete file, same process as delete member
@login_required
def file_delete(request, file_id):
    file = EventFiles.objects.get(id = file_id)
    file.delete()
    return JsonResponse({'result' : 'ok'}, status=200)

#delete location, same process as delete member
@login_required
def location_delete(request, location_id):
    location = Locations.objects.get(id = location_id)
    location.delete()
    return JsonResponse({'result' : 'ok'}, status=200)

#note delte same process as delete member
@login_required
def note_delete(request, note_id):
    note= Notes.objects.get(id= note_id)
    note.delete()
    return JsonResponse({'result' : 'ok'}, status=200)

#add file for event view
@login_required
def add_files(request):
    #getting the event to which we want to add file
    event_id = request.POST.get('event_id')
    event = Event.objects.get(id=event_id)
    #list of the file to upload, this is a list becasue in the HTML form we allowed the user to select multiple files
    files = request.FILES.getlist('files')
    #looping throw all seleted files
    for file in files:
        fs= FileSystemStorage()
        #saveing the file and getting the path to it
        file_path = fs.save(file.name, file)
        #creating new EventFiles object
        sfile= EventFiles(event = event, files = file_path)
        #saveing the object
        sfile.save()
    return redirect('manCal:event-detail', event_id = event_id,)

#create note
@login_required
def add_note(request):
    #getting the user and the content of the note
    if request.method == 'POST':
        user = CustomUser.objects.get(username= request.user)
        note = request.POST.get('note')
        #createing new note
        new_note = Notes.objects.create(
            user = user,
            note = note
        )
    #returning created object to Ajax request converting the model data to dictionary
    return JsonResponse({'note' : model_to_dict(new_note)}, status=200)
#update note status
@login_required
def note_complited(request, note_id):
    #getting note from note id
    note = Notes.objects.get(id=note_id)
    #changeing note staus
    if note.complited == True:
        note.complited = False
    elif note.complited == False:
        note.complited = True
    #saveing new status
    note.save()
    #returning to ajax like in crete note
    return JsonResponse({'note' : model_to_dict(note)}, status=200)


#exercise detail view
@login_required
def healthView(request):
    user = CustomUser.objects.get(username= request.user)
    #get exercise details if already created
    if Exercise.objects.filter(user= user).exists():
        exercise = Exercise.objects.get(user= user)
        context = {
            'exercise' : exercise
        }
        #passing data to template
        return render(request, 'health.html', context)
    #if not exist render without exercise data
    return render(request, 'health.html')

#update exercise
@login_required
def addExercise(request):
    if request.method == 'POST':
        #get variable from post request
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
        #if no previews data exsist, create new one
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
        # if exist update existing dat
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
