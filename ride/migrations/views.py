from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import *
from ride.models import RideRequest
from datetime import datetime
from django.contrib import messages
from django.core.mail import send_mail
from .models import RideRequest
from account.models import *
from django.db.models import Q, Sum, Count, F
from django.http import HttpResponseForbidden
from .utility import gmail_authenticate, send_message
from django.views.decorators.csrf import csrf_exempt

# Allow user to request a ride
@login_required
@csrf_exempt 
def request_ride(request):
    if request.method == 'POST':
        ride_request_form = RideRequestForm(request.POST)
        user_ride_form = UserRideForm(request.POST)

        if ride_request_form.is_valid() and user_ride_form.is_valid():
            passenger_num = user_ride_form.cleaned_data['passenger_num']
            ride_request = ride_request_form.save(commit=False)
            ride_request.owner = request.user.userprofile
            ride_request.vehicle_type = request.POST.get('vehicle_type', '')
            ride_request.special_request_info = request.POST.get('special_request_info', '')
            ride_request.can_share = request.POST.get('can_share') == 'on'
            ride_request.save()
            UserRide.objects.create(
                user=request.user.userprofile,
                ride_request=ride_request,
                is_owner=True,
                passenger_num=passenger_num
            )
            return redirect('dashboard')
    else:
        ride_request_form = RideRequestForm()
        user_ride_form = UserRideForm()

    return render(request, 'ride/request_ride.html', {'ride_request_form': ride_request_form, 'user_ride_form': user_ride_form})


# Edit the ride when it is not confirmed, for user
@login_required
@csrf_exempt
def edit_ride_request(request, ride_request_id):
    ride_request = get_object_or_404(RideRequest, id=ride_request_id)

    is_owner = request.user == ride_request.owner.user
    is_sharer = request.user in [sharer.user for sharer in ride_request.sharers.all()]
    if not (is_owner or is_sharer):
        return HttpResponseForbidden("You are not authorized to edit this ride.")

    if ride_request.status != 'Open':
        return HttpResponseForbidden("Your ride is already confirmed")

    user_ride = get_object_or_404(UserRide, ride_request=ride_request, user=request.user.userprofile)
    if is_owner:
        # User is the owner, allow modification of all specified attributes
        ride_form = OwnerRideForm(request.POST or None, instance=ride_request)
        sharer_form = UserRideForm(request.POST or None, instance=user_ride)
    else:
        # User is a sharer, only allow modification of passenger_num
        ride_form = None
        sharer_form = UserRideForm(request.POST or None, instance=user_ride)

    if request.method == 'POST' and sharer_form.is_valid() and (ride_form is None or ride_form.is_valid()):
        # Update passenger_num in the associated UserRide instance
        user_ride.passenger_num = sharer_form.cleaned_data['passenger_num']
        user_ride.save()

        if ride_form:
            ride_request.destination = ride_form.cleaned_data['destination']
            ride_request.arrival_time = ride_form.cleaned_data['arrival_time']
            ride_request.vehicle_type = ride_form.cleaned_data['vehicle_type']
            ride_request.special_request_info = ride_form.cleaned_data['special_request_info']
            ride_request.save()

        return redirect('ride_list')  # Redirect to ride_list after successful edit

    return render(request, 'ride/edit_ride_request.html', {'ride_form': ride_form, 'sharer_form': sharer_form, 'ride_request': ride_request, 'is_owner': is_owner})

@login_required
@csrf_exempt
def driver_search_ride(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    driver_profile = get_object_or_404(DriverProfile, user_profile=user_profile)
    driver_special_requests = driver_profile.special_request_info

    # Get open rides that match the driver's special requests and ensure the driver is not the owner of the ride
    open_rides = RideRequest.objects.filter(
        Q(status='Open') & 
        (Q(special_request_info=driver_profile.special_request_info) | Q(special_request_info='') | Q(special_request_info=None)) & 
        Q(vehicle_type=driver_profile.vehicle_model) &
        ~Q(owner=user_profile)  # Exclude rides where the driver is the owner
    )
    filtered_rides = []
    for ride in open_rides:
        total_passengers = UserRide.objects.filter(
            ride_request=ride,
        ).aggregate(Sum('passenger_num'))['passenger_num__sum'] or 0

        if total_passengers <= driver_profile.capacity:
            filtered_rides.append((ride,total_passengers))
    return render(request, 'ride/driver_search_ride.html', {'open_rides': filtered_rides})

@login_required
@csrf_exempt
def user_search_ride(request):
    destination = request.GET.get('destination', '')
    earliest_arrival_time_str = request.GET.get('earliest_arrival_time', '')
    latest_arrival_time_str = request.GET.get('latest_arrival_time', '')
    passengers = request.GET.get('passengers', None)

    print("Destination:", destination)
    print("Earliest Arrival Time:", earliest_arrival_time_str)
    print("Latest Arrival Time:", latest_arrival_time_str)
    print("Passengers:", passengers)

    # Convert string to datetime
    earliest_arrival_time = datetime.strptime(earliest_arrival_time_str, '%Y-%m-%dT%H:%M') if earliest_arrival_time_str else None
    latest_arrival_time = datetime.strptime(latest_arrival_time_str, '%Y-%m-%dT%H:%M') if latest_arrival_time_str else None

    # Perform the ride search based on the criteria
    open_rides = RideRequest.objects.filter(
        status='Open',
        destination__icontains=destination,
        arrival_time__range=(earliest_arrival_time, latest_arrival_time),
        can_share=True,
    )

    # Users who are already part of this ride would not be able to see it in search
    excluded_rides = open_rides.filter(owner=request.user.userprofile) | open_rides.filter(sharers__user=request.user)
    open_rides = open_rides.exclude(id__in=excluded_rides)

    open_rides_with_passengers = []
    for ride in open_rides:
        total_passengers = UserRide.objects.filter(ride_request=ride).aggregate(Sum('passenger_num'))['passenger_num__sum']
        if total_passengers < 6:
            open_rides_with_passengers.append({
                'ride_request': ride,
                'total_passengers': total_passengers
            })
    return render(request, 'ride/search_ride.html', {'open_rides_with_passengers': open_rides_with_passengers})



@login_required
@csrf_exempt
def join_ride(request, ride_request_id):
    ride_request = get_object_or_404(RideRequest, id=ride_request_id)
    if request.method == 'POST':
        form = SharerRideForm(request.POST)
        if form.is_valid():
            # Create a UserRide instance for the user in this ride
            passenger_num = request.POST.get('passenger_num')
            user_ride = form.save(commit=False)
            user_ride.user = request.user.userprofile
            user_ride.ride_request = ride_request
            user_ride.is_owner = False
            user_ride.passenger_num = passenger_num
            user_ride.save()
            print("User successfully joined the ride!")
            return redirect('ride_list')
        else:
            print("invalid", form.errors)
    else:
        form = SharerRideForm()

    return render(request, 'ride/search_ride.html', {'form': form, 'ride_request': ride_request})

@login_required
@csrf_exempt
def ride_list(request):
    owned_rides = RideRequest.objects.filter(owner=request.user.userprofile, userride__is_owner=True)
    shared_rides = RideRequest.objects.filter(sharers__user=request.user).exclude(owner=request.user.userprofile)

    return render(request, 'ride/ride_list.html', {
        'owned_rides': owned_rides, 
        'shared_rides': shared_rides
    })


@login_required
@csrf_exempt
def ride_status(request, ride_request_id):
    ride_request = get_object_or_404(RideRequest, id=ride_request_id)
    
    # Check the user's role in the ride (owner or sharer)
    is_owner = ride_request.owner.user == request.user
    is_sharer = request.user in [sharer.user for sharer in ride_request.sharers.all()]

    if not (is_owner or is_sharer):
        return HttpResponseForbidden("You are not authorized to view this ride.")

    # Common information
    total_passengers = UserRide.objects.filter(
        ride_request=ride_request
    ).aggregate(Sum('passenger_num'))['passenger_num__sum'] or 0

    driver_profile = None
    if ride_request.driver:
        user_profile = UserProfile.objects.filter(user=ride_request.driver).first()
        if user_profile:
            driver_profile = DriverProfile.objects.filter(user_profile=user_profile).first()

    # Owner-specific information
    owner_passengers = UserRide.objects.filter(
        ride_request=ride_request, 
        user=ride_request.owner
    ).aggregate(Sum('passenger_num'))['passenger_num__sum'] or 0

    # Sharer-specific information
    sharers_info = []
    if is_sharer:
        for sharer in ride_request.sharers.exclude(user=ride_request.owner.user).all():
            num_passengers = UserRide.objects.filter(
                ride_request=ride_request, 
                user=sharer
            ).aggregate(Sum('passenger_num'))['passenger_num__sum'] or 0
            sharers_info.append({'sharer': sharer, 'num_passengers': num_passengers})

    context = {
        'ride_request': ride_request,
        'is_owner': is_owner,
        'is_sharer': is_sharer,
        'total_passengers': total_passengers,
        'driver_profile': driver_profile,
        'owner_passengers': owner_passengers,
        'sharers_info': sharers_info,
    }
    return render(request, 'ride/ride_status.html', context)


@login_required
@csrf_exempt
def driver_ride_status(request, ride_request_id):
    ride_request = get_object_or_404(
        RideRequest, 
        id=ride_request_id
    )
    driver_profile = get_object_or_404(DriverProfile, user_profile=request.user.userprofile)
    # Check if the logged-in driver is the driver for this ride
    if ride_request.driver != request.user:
        return HttpResponseForbidden("You are not authorized to view this ride.")

    total_passengers = UserRide.objects.filter(
        ride_request=ride_request
    ).aggregate(Sum('passenger_num'))['passenger_num__sum'] or 0
    owner_username = None
    owner_num_passengers = 0
    # Check if the owner is not the driver
    if ride_request.owner != driver_profile.user_profile:
        owner_username = ride_request.owner.user.username

        owner_ride_info = UserRide.objects.filter(       # to get the number of passengers for the owner
            ride_request=ride_request, 
            user=ride_request.owner
        ).first()

        if owner_ride_info:
            owner_num_passengers = owner_ride_info.passenger_num
    sharers_info = ride_request.sharers.exclude(user=request.user).exclude(user=ride_request.owner.user).all()
    # Compile sharers' details (username and number of passengers)
    sharers_details = []
    for sharer in sharers_info:
        num_passengers = UserRide.objects.filter(
            ride_request=ride_request, 
            user=sharer
        ).aggregate(Sum('passenger_num'))['passenger_num__sum'] or 0
        sharers_details.append({
            'username': sharer.user.username,
            'num_passengers': num_passengers
        })

    context = {
        'ride_request': ride_request,
        'total_passengers': total_passengers,
        'owner_username': owner_username,
        'owner_num_passengers': owner_num_passengers,
        'sharers_details': sharers_details,
    }
    return render(request, 'ride/driver_ride_status.html', context)


@login_required
@csrf_exempt
def claim_ride(request, ride_request_id):
    ride_request = RideRequest.objects.get(pk=ride_request_id)

    # Update the ride status to 'Confirm' and save the driver details
    ride_request.status = 'Confirm'
    ride_request.driver = request.user
    ride_request.save()

    # Use Gmail API for sending emails
    service = gmail_authenticate()

    # Email content
    sender_email = "m271693043@gmail.com"
    owner_email = ride_request.owner.user.email
    sharer_emails = ride_request.sharers.exclude(id=ride_request.owner.id).values_list('user__email', flat=True)

    # Send confirmation email
    send_confirmation_email(service, sender_email, owner_email, sharer_emails, request.user.username)
    
    # Redirect to the existing driver dashboard
    return redirect('driver_dashboard')

@csrf_exempt
def send_confirmation_email(service, sender_email, owner_email, sharer_emails, username):
    # Email content
    subject = "Ride Confirmation"

    message_body = f"Dear {owner_email},\n\nYour ride request has been confirmed by {username}.\n\n"

    for sharer_email in sharer_emails:
        message_body += f"Dear {sharer_email},\n\nYour shared ride has been confirmed by {username}.\n\n"

    message_body += "Thank you for using our ride service."

    # Send emails
    send_message(service, sender_email, owner_email, subject, message_body)
    for sharer_email in sharer_emails:
        send_message(service, sender_email, sharer_email, subject, message_body)


@login_required
@csrf_exempt
def complete_ride(request, ride_request_id):
    ride_request = RideRequest.objects.get(pk=ride_request_id)
    ride_request.status = 'Complete'
    ride_request.driver = request.user
    ride_request.save()
    return redirect('driver_dashboard')

@login_required
@csrf_exempt
def driver_confirmed_ridelist(request):
    # Filter for rides where the current user is the driver and the status is 'Confirmed'
    driver_confirmed_ridelist = RideRequest.objects.filter(driver=request.user, status='Confirm')
    return render(request, 'ride/driver_confirmed_ridelist.html', {'driver_confirmed_ridelist': driver_confirmed_ridelist})
