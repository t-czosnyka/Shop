from django.shortcuts import render, redirect, reverse
from .forms import LoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import NoReverseMatch

# Create your views here.


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
            next_url = request.POST.get('next', False)
            if next_url:
                try:
                    response = redirect(next_url)
                    return response
                except NoReverseMatch:
                    messages.warning(request, "Url not found.")
            return redirect('pages:home')
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



