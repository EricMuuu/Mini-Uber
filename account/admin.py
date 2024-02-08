from django.contrib import admin

# Register your models here.
from .models import UserProfile, DriverProfile

admin.site.register(UserProfile)
admin.site.register(DriverProfile)