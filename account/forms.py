from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.forms import AuthenticationForm
from .models import *
from django.core.exceptions import ValidationError

# User Registration
class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone = forms.CharField(max_length=10, required=True)
    email = forms.EmailField(max_length=254, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'phone')

    def save(self,commit=True):
        user=super(UserRegistrationForm, self).save(commit=False)
        user.first_name=self.cleaned_data['first_name']
        user.last_name=self.cleaned_data['last_name']
        user.phone=self.cleaned_data['phone']
        user.email=self.cleaned_data['email']

        if commit:
            user.save()
        return user

# User Login
class UserAuthenticationForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']


# Driver Registration
class DriverRegistrationForm(forms.ModelForm):
    class Meta:
        model = DriverProfile
        fields = ['vehicle_model', 'license_number', 'capacity','special_request_info']


class EditProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields=['email','first_name','last_name','password']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone']  

class DriverProfileForm(forms.ModelForm):
    VEHICLE_MODEL_CHOICES = [
        ('Sedan', 'Sedan'),
        ('Hatchback', 'Hatchback'),
        ('Luxury Sedan', 'Luxury Sedan'),
        ('Standard SUV', 'Standard SUV'),
        ('Large SUV', 'Large SUV'),
    ]

    vehicle_model = forms.ChoiceField(choices=VEHICLE_MODEL_CHOICES)
    
    class Meta:
        model = DriverProfile
        fields = ['vehicle_model','license_number','capacity','special_request_info']
    def clean_capacity(self):
        capacity = self.cleaned_data.get('capacity')
        if capacity <= 0:
            raise ValidationError('Capacity must be greater than 0.')
        return capacity
