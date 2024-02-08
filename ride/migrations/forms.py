from django import forms
from django.contrib.auth.models import User
from .models import *

# Form for ride request
# class RideRequestForm(forms.ModelForm):
#     class Meta:
#         model = RideRequest
#         fields = ['destination', 'arrival_time', 'num_passengers', 'vehicle_type', 'can_share', 'special_request_info']

#     def __init__(self, *args, **kwargs):
#         instance = kwargs.get('instance')
#         super(RideRequestForm, self).__init__(*args, **kwargs)
#         # We update instead of creating a new one
#         if instance:
#             self.fields['destination'].initial = instance.destination
#             self.fields['arrival_time'].initial = instance.arrival_time
#             self.fields['vehicle_type'].initial = instance.vehicle_type
#             self.fields['can_share'].initial = instance.can_share
#             self.fields['special_request_info'].initial = instance.special_request_info

class RideRequestForm(forms.ModelForm):
    class Meta:
        model = RideRequest
        fields = ['destination', 'arrival_time', 'vehicle_type', 'can_share', 'special_request_info']



class UserRideForm(forms.ModelForm):
    class Meta:
        model = UserRide
        fields = ['passenger_num']

    def __init__(self, *args, **kwargs):
        super(UserRideForm, self).__init__(*args, **kwargs)
        if 'passenger_num' in self.fields:
            self.fields['passenger_num'].widget.attrs['min'] = 1

# Used for owner edit ride
class OwnerRideForm(forms.ModelForm):
    class Meta:
        model = RideRequest
        fields = ['destination', 'arrival_time', 'vehicle_type', 'special_request_info']

    def __init__(self, *args, **kwargs):
        super(OwnerRideForm, self).__init__(*args, **kwargs)

# Used for sharer edit ride
class SharerRideForm(forms.ModelForm):
    class Meta:
        model = UserRide
        fields = ['passenger_num']

    def __init__(self, *args, **kwargs):
        super(SharerRideForm, self).__init__(*args, **kwargs)
        self.fields['passenger_num'].widget.attrs['min'] = 1