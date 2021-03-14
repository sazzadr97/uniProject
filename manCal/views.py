from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from .forms import signUpForm

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
        form = signUpForm()
    return render(request, "signup.html", {"form": form})

@login_required
def indexView(request):
    return render(request, "index.html")