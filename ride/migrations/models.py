from django.db import models
from django.contrib.auth.models import User
from account.models import *

class RideRequest(models.Model):
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    destination = models.CharField(max_length=255)
    arrival_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[('Open', 'Open'), ('Confirm', 'Confirm'), ('Complete', 'Complete')], default='Open')
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    can_share = models.BooleanField()
    vehicle_type = models.CharField(max_length=255, blank=True, null=True)
    SPECIAL_REQUEST_CHOICES = [
        ('Green Energy', 'Green Energy'),
        ('Accessibility', 'Accessibility'),
        ('Luxury', 'Luxury'),
    ]
    special_request_info = models.CharField(max_length=255, choices=SPECIAL_REQUEST_CHOICES, blank=True, null=True)
    sharers = models.ManyToManyField(UserProfile, through='UserRide', related_name='shared_rides', blank=True)

class UserRide(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    ride_request = models.ForeignKey(RideRequest, on_delete=models.CASCADE)
    is_owner = models.BooleanField(default=False)
    passenger_num = models.IntegerField(default=1) 

