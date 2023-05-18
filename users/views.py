from django.shortcuts import render, redirect
from .forms import LoginForm, UserDataForm, UserForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import NoReverseMatch


# Create your views here.

def redirect_next_url(request):
    # after successful operation redirect to url in next parameter if it was provided or to home
    next_url = request.GET.get('next', False) or request.POST.get('next', False)
    if next_url:
        try:
            response = redirect(next_url)
            return response
        except NoReverseMatch:
            messages.warning(request, "Url not found.")
    return redirect('pages:home')


def register_view(request):
    logout(request)
    form_user = UserForm(request.POST or None)
    form_user_data = UserDataForm(request.POST or None)
    if request.method == "POST":
        if form_user.is_valid() and form_user_data.is_valid():
            # Create user
            user = form_user.save()
            # Associated UserData is created by post_save signal
            # assign data to user data
            form_user_data = UserDataForm(request.POST, instance=user.user_data)
            form_user_data.save()
            # login user after successful registration
            login(request, user)
            messages.success(request, f"User {user.username} successfully created.")
            return redirect_next_url(request)
    context = {
        'title': 'Register User',
        'form_user': form_user,
        'form_user_data': form_user_data
    }
    return render(request, 'users/register.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('pages:home')
    form = LoginForm(request.POST or None)
    if request.method == "POST":
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect_next_url(request)
        else:
            messages.warning(request, "Wrong login or password.")
    context = {
        'title': 'Login',
        'form': form
    }
    return render(request, 'users/login.html', context)


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('pages:home')


def no_login_order(request):
    # set attribute to order without logging in
    request.session['no_login_order'] = True
    return redirect_next_url(request)



