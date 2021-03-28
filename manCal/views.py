from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from .forms import signUpForm, EventForm, AddMemberForm

from datetime import datetime, date
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.utils.safestring import mark_safe
from datetime import timedelta
import calendar
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from .models import *
from .utils import Calendar

from django.contrib.auth.forms import UserCreationForm

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

        response = render(request, 'news/index.html', context)

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
        return redirect("/login")
    else:
        print('register failed after validation')
        form = signUpForm()
    
    print('register failed')
    return render(request, "signup.html", {"form": form})

@login_required
def indexView(request):
    return render(request, "index.html")

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
    login_url = 'signup'
    model = Event
    template_name = 'calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get('month', None))
        cal = Calendar(d.year, d.month)
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        return context


@login_required
def create_event(request):    
    form = EventForm(request.POST or None)
    if request.POST and form.is_valid():
        title = form.cleaned_data['title']
        description = form.cleaned_data['description']
        start_time = form.cleaned_data['start_time']
        end_time = form.cleaned_data['end_time']
        Event.objects.get_or_create(
            user=request.user,
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time
        )
        return HttpResponseRedirect(reverse('manCal:calendar'))
    return render(request, 'event.html', {'form': form})

class EventEdit(generic.UpdateView):
    model = Event
    fields = ['title', 'description', 'start_time', 'end_time']
    template_name = 'event.html'

@login_required
def event_details(request, event_id):
    event = Event.objects.get(id=event_id)
    context = {
        'event': event,
    }
    return render(request, 'event-details.html', context)


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
                return redirect('manCal:calendar')
            else:
                print('--------------User limit exceed!-----------------')
    context = {
        'form': forms
    }
    return render(request, 'add_member.html', context)

class EventMemberDeleteView(generic.DeleteView):
    model = EventMember
    template_name = 'event_delete.html'
    success_url = reverse_lazy('manCal:calendar')