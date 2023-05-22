from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from .forms import LoginForm, UserDataForm, UserForm, ResetForm, UserChangeForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import NoReverseMatch
from django.contrib.auth.models import User
from django.db.models import ObjectDoesNotExist
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.forms import SetPasswordForm, PasswordChangeForm
from django.apps import apps
from django.http import HttpResponseForbidden, HttpResponse, HttpResponseNotFound
from django.conf import settings

# Create your views here.
Order = apps.get_model('orders', 'Order')


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


def get_user_from_uidb64(request, uidb64):
    # decode user_id and get user
    user = None
    try:
        user_id = urlsafe_base64_decode(uidb64)
        user = User.objects.get(id=user_id)
    except (ValueError, ObjectDoesNotExist):
        pass
    return user


def reset_insert_email_view(request):
    # Check if user is not logged in.
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in.")
        return redirect('pages:home')
    form = ResetForm()
    if request.method == "POST":
        email = request.POST.get('email', '')
        user = None
        try:
            user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            messages.warning(request, "No user with this email exists.")
        if user is not None:
            uidb64 = urlsafe_base64_encode(str(user.id).encode())
            token = default_token_generator.make_token(user=user)
            url = request.build_absolute_uri(f'/users/reset/{uidb64}/{token}')
            sent = send_mail(
                'Password reset link',
                f'Click this link to reset your password:\n'
                f'{url}',
                'django-e-shop',
                [user.email],
                fail_silently=False,
            )
            if sent:
                messages.success(request, f"Password reset email has been sent to address {user.email}.")
                return redirect('pages:home')
            else:
                messages.warning(request, f"Error while sending email to address {user.email}")
    context = {
        'title': 'Insert email',
        'form': form
    }
    return render(request, 'users/reset_insert_email.html', context)


def reset_new_password_view(request, uidb64, token):
    # Check if user is not logged in.
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in.")
        return redirect('pages:home')
    # Check provided user id.
    user = get_user_from_uidb64(request, uidb64)
    if user is None:
        return HttpResponseNotFound
    # Check provided token.
    if not default_token_generator.check_token(user=user, token=token):
        return HttpResponse('401 Unauthorized. Token error.', status=401)
    form = SetPasswordForm(user, request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new_password = request.POST.get('new_password1', '')
            if new_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Password changed successfully.")
                return redirect('pages:home')
    context = {
        'title': "New password",
        'form': form
    }
    return render(request, 'users/new_password_form.html', context)


def check_user(request, uidb64):
    # Get user from uidb64.
    response = None
    user = get_user_from_uidb64(request, uidb64)
    # Check if decoded user exists.
    if user is None:
        response = HttpResponseNotFound(request)
    # Check if user is authenticated.
    elif not request.user.is_authenticated:
        # redirect to login page
        messages.warning(request, "Login required.")
        url = settings.LOGIN_URL + '?next=' + request.path
        response = redirect(url)
    # Check if user is authorized to access this page.
    elif user.id != request.user.id:
        response = HttpResponseForbidden(request)
    return user, response


def change_password_view(request, uidb64):
    user, response = check_user(request, uidb64)
    if response is not None:
        return response
    form = PasswordChangeForm(user, request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new_password = request.POST.get('new_password1', '')
            if new_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Password changed successfully.")
                return redirect('pages:home')
    context = {
        'title': 'Change password',
        'form': form,
    }
    return render(request, 'users/change_password_form.html', context)


def change_data_view(request, uidb64):
    user, response = check_user(request, uidb64)
    if response is not None:
        return response
    form_user = UserChangeForm(request.POST or None, instance=user)
    try:
        form_user_data = UserDataForm(request.POST or None, instance=user.user_data)
    except AttributeError:
        form_user_data = UserDataForm(request.POST or None)
    if request.method == 'POST':
        if form_user.is_valid() and form_user_data.is_valid():
            form_user.save()
            form_user_data.save()
            messages.success(request, "User data changed successfully.")
            return redirect('pages:home')
    context = {
        'title': 'Change user data',
        'form_user': form_user,
        'form_user_data': form_user_data
    }
    return render(request, 'users/change_user_data_form.html', context)


def users_orders_list(request, uidb64):
    user, response = check_user(request, uidb64)
    if response is not None:
        return response
    orders_list = Order.objects.filter(user=user)
    context = {
        'title': 'Change user data',
        'orders_list': orders_list,
    }
    return render(request, 'users/orders.html', context)







