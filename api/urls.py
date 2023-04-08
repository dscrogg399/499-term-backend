from django.urls import path
from .views import *


urlpatterns = [
    path('', index, name='index'),
    path('appliances/', appliances, name='appliances'),
    path('apertures/', apertures, name='apertures'),
    path('thermostat/', thermostat, name='thermostat'),
    path('air_quality/', air_quality, name='air_quality'),
    path('monthly_report/', monthly_report, name='monthly_report'),
    path('budget/', budget, name='budget'),
    path('create_event/', create_event, name='create_event')
]