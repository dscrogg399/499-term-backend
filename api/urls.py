from django.urls import path
from .views import *


urlpatterns = [
    path('', index, name='index'),
    # path('user/', user, name='user'),
    path('get_appliance_statuses/', get_appliance_statuses, name='get_appliance_statuses')
]