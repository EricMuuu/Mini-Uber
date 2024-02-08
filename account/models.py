from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=20)
    first_name = models.CharField(max_length=20, default='Bob')
    last_name = models.CharField(max_length=20, default='Allen')
    phone = models.CharField(max_length=10, default='1234567890')
    email = models.EmailField(default='example@example.com')
    is_driver = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class DriverProfile(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    vehicle_model = models.CharField(max_length=20, default='Benz')
    license_number = models.CharField(max_length=20, default='123ABC')
    capacity = models.IntegerField(validators=[MaxValueValidator(6)], default=4)
    SPECIAL_REQUEST_CHOICES = [
        ('Green Energy', 'Green Energy'),
        ('Accessibility', 'Accessibility'),
        ('Luxury', 'Luxury'),
    ]
    special_request_info = models.CharField(max_length=20, choices=SPECIAL_REQUEST_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.user_profile.username
