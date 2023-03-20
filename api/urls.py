from django.urls import path
from .views import *


urlpatterns = [
    path('', index, name='index'),
    path('user/', user, name='user'),
    path('appliance/', appliance, name='appliance')
]