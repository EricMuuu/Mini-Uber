from django.contrib import admin

# Register your models here.
from .models import RideRequest

admin.site.register(RideRequest)