from django.urls import path
from ride.views import *
from . import views

urlpatterns = [
    path('request_ride/', request_ride, name='request_ride'),
    path('edit_ride_request/<int:ride_request_id>/', views.edit_ride_request, name='edit_ride_request'),
    path('join_ride/<int:ride_request_id>/', join_ride, name='join_ride'),
   
    path('ride_list/', views.ride_list, name='ride_list'),
    path('driver_confirmed_ridelist/', views.driver_confirmed_ridelist, name='driver_confirmed_ridelist'),
    
    path('user_search_ride/', user_search_ride, name='user_search_ride'),
    path('driver_search_ride/', driver_search_ride,name='driver_search_ride'),
    
    path('ride_status/<int:ride_request_id>/', ride_status,name='ride_status'),
    path('driver_ride_status/<int:ride_request_id>/', driver_ride_status, name='driver_ride_status'),

    path('claim_ride/<int:ride_request_id>/', claim_ride, name='claim_ride'),
    path('complete_ride/<int:ride_request_id>/', complete_ride, name='complete_ride'),
    
]

