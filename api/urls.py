from django.urls import path
from .views import *


urlpatterns = [
    path('', index, name='index'),
    # path('user/', user, name='user'),
    path('appliance_type/', appliance_type, name='appliance_type')
]