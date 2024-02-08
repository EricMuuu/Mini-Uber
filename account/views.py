from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .forms import *
from django.http import *

from ride.models import RideRequest
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from account.models import UserProfile, DriverProfile 
from django.contrib import messages
from django.db.models import Q

# Allow users to register
@csrf_exempt
def user_register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Create a User object
            user = form.save()
            password = form.cleaned_data.get('password1')
            user=authenticate(username=user.username, password=password)
            if user is not None:
                login(request, user)
            
            # Create a UserProfile object
            UserProfile.objects.create(
                user=user,
                username=user.username,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                phone=form.cleaned_data['phone'],
                email=form.cleaned_data['email'],
            )
            messages.success(request, "You have successfully registered")

            return redirect('login')
    else:
        form = UserRegistrationForm()

    return render(request, 'account/register.html', {'form':form})


# Allow users to sign-in -> authentication
@csrf_exempt
def loggin(request):
    if request.method == 'POST':
        form = UserAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = UserAuthenticationForm()

    return render(request, 'account/login.html', {'form': form})

# Allow user to logout in the dashboard
@login_required
@csrf_exempt    
def loggout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    else:
        return render(request, 'account/dashboard.html')

@login_required
@csrf_exempt
def dashboard_view(request):
    user_profile = UserProfile.objects.get(user=request.user)
    rides = RideRequest.objects.filter(
        Q(owner=request.user.userprofile) | Q(sharers=request.user.userprofile),
        status__in=['Open', 'Confirm']
    ).distinct()
    if request.method == 'POST' and 'switch_mode' in request.POST:
        if user_profile.is_driver:
            return redirect('driver_dashboard')

    return render(request, 'account/dashboard.html', {'user_profile': user_profile, 'rides': rides})

@login_required
@csrf_exempt
def driver_register(request):
    if request.method == "POST" and request.user.is_authenticated:
         form = DriverRegistrationForm(request.POST)
         if form.is_valid():
            # Updating the UserProfile:
            user_profile = UserProfile.objects.get(user=request.user)
            user_profile.is_driver = True
            user_profile.save()
            # Create DriverProfile
            driver_profile = DriverProfile.objects.create(
                user_profile=user_profile, 
                vehicle_model=form.cleaned_data['vehicle_model'],
                license_number=form.cleaned_data['license_number'],
                capacity=form.cleaned_data['capacity'],
                special_request_info=form.cleaned_data['special_request_info'])
            messages.success(request, 'Registration as a driver was successful!')
            messages.success(request, 'Please resign in to enter your account!')
            return redirect('login')
    else:
        form = DriverRegistrationForm()
    return render(request, 'account/driver_register.html', {'form': form})


@login_required
@csrf_exempt
def driver_dashboard(request):
    user_profile = UserProfile.objects.get(user=request.user)
    drivers = RideRequest.objects.filter(driver=request.user, status__in=['Open', 'Confirm'])
    if user_profile.is_driver:
        return render(request, 'account/driver_dashboard.html', {'user_profile': user_profile, 'ride_requests': drivers})
    if request.method == 'POST':
        if 'switch_to_user_dashboard' in request.POST:
            return redirect('dashboard')
    return redirect('driver_register') 


@login_required
@csrf_exempt
def userprofile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    context = {
        'user': request.user,
        'user_profile': user_profile
    }
    return render(request, 'account/userprofile.html', context)


@login_required
@csrf_exempt
def driverprofile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    driver_profile = DriverProfile.objects.get(user_profile=user_profile)
    context = {
        'user': request.user,
        'driver_profile': driver_profile,
        'user_profile': user_profile
    }
    return render(request, 'account/driverprofile.html', context)


@login_required
@csrf_exempt
def edit_driver_profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    try:
        driver_profile = DriverProfile.objects.get(user_profile=user_profile)
    except DriverProfile.DoesNotExist:
        # Handle the case where the driver profile does not exist
        driver_profile = None

    if request.method == 'POST':
        user_form = EditProfileForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=user_profile)
        driver_profile_form = DriverProfileForm(request.POST, instance=driver_profile)
        if user_form.is_valid() and profile_form.is_valid() and (driver_profile is None or driver_profile_form.is_valid()):
            user_form.save()
             # Save the User form
            updated_user = user_form.save()

            # Sync the fields from User to UserProfile if they are updated
            if 'first_name' in user_form.changed_data:
                user_profile.first_name = updated_user.first_name
            if 'last_name' in user_form.changed_data:
                user_profile.last_name = updated_user.last_name
            if 'email' in user_form.changed_data:
                user_profile.email = updated_user.email

            profile_form.save()
            if driver_profile is not None:
                driver_profile_form.save()
            return redirect('driverprofile')
    else:
        user_form = EditProfileForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)
        driver_profile_form = DriverProfileForm(instance=driver_profile)
    return render(request, 'account/edit_driver_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'driver_profile_form': driver_profile_form
    })

 
@login_required
@csrf_exempt
def edit_user_profile(request):
    if request.method == 'POST':
        user_form = EditProfileForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=request.user.userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            # Save the User form
            updated_user = user_form.save()

            # Sync the fields from User to UserProfile if they are updated
            profile_instance = profile_form.instance
            if 'first_name' in user_form.changed_data:
                profile_instance.first_name = updated_user.first_name
            if 'last_name' in user_form.changed_data:
                profile_instance.last_name = updated_user.last_name
            if 'email' in user_form.changed_data:
                profile_instance.email = updated_user.email
            # Save the UserProfile form
            profile_form.save()
            return redirect('userprofile')
    else:
        user_form = EditProfileForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.userprofile)
    return render(request, 'account/edit_user_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

