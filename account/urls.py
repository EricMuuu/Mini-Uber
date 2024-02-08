from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from ride.views import *

urlpatterns = [
    path('register/', views.user_register, name='register'),
    path('login/', views.loggin, name='login'),
    path('driver_register/', views.driver_register, name='driver_register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.loggout, name='logout'),
    # path('request_ride_from_dashboard/', views.request_ride_from_dashboard, name='request_ride_from_dashboard'),
    path('driver_dashboard/', views.driver_dashboard, name='driver_dashboard'), 

    path('userprofile/', views.userprofile, name='userprofile'),
    path('userprofile/edit_user_profile/', views.edit_user_profile, name='edit_user_profile'),
    # path('userprofile/change_password/', views.change_password, name='change_password'),

    path('driverprofile/', views.driverprofile, name='driverprofile'),
    path('driverprofile/edit_driver_profile/', views.edit_driver_profile, name='edit_driver_profile'),

    path('search_open_rides/', user_search_ride, name='search_open_rides'),
    path('search_open_rides/driver/', driver_search_ride, name='search_open_rides_driver'),
    
]
