from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django import forms
from django.core.serializers import serialize
from django.forms.models import model_to_dict
import json

from api.models import *

# Create your views here.
def index(request):   
    return HttpResponse("Team 4")

# def user(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         email = request.POST.get('email')
#         user = User.create(username, password, email)
#         user.save()
#         return JsonResponse({"code": "200", "message": "User created successfully", "new_id": user.id})
#     elif request.method == 'GET':
#         try:
#             user = User.objects.get(id=request.GET.get('id'))
#             return JsonResponse({"code": "200", "message": "User found", "user": { "username": user.username, "email": user.email}})
#         except User.DoesNotExist:
#             return JsonResponse({"code": "404", "message": "User not found"})
#     else:
#         return JsonResponse({"code": "400", "message": "Invalid request method"})

def appliances(request):
    if request.method == 'POST':
        input_id = request.POST.get('id')

        try:
            appliance_get = Appliance.objects.get(id=input_id)
            appliance_get.status = not appliance_get.status
            appliance_get.save()
            return JsonResponse({"code": "200", "message": "appliance toggled", "appliance status": appliance_get.status})
           
        except Appliance.DoesNotExist:
            return JsonResponse({"code": "404", "message": "appliance does not exist"})

    elif request.method == 'GET':
        appliances = Appliance.objects.all().values('id', 'title', 'status', 'x', 'y', 'appliance_type').order_by('id')
        serialized_appliances = json.dumps(str(appliances))
        return JsonResponse({"data": serialized_appliances})
    
    else:
        return JsonResponse({"code": "400", "message": "Invalid request method"})


def apertures(request):
    if request.method == 'POST':
        input_id = request.POST.get('id')

        try:
            aperture_get = Aperture.objects.get(id=input_id)
            aperture_get.status = not aperture_get.status
            aperture_get.save()
            return JsonResponse({"code": "200", "message": "aperture toggled", "aperture status": aperture_get.status})

        except Aperture.DoesNotExist:
            return JsonResponse({"code": "404", "message": "aperture does not exist"})

    elif request.method == 'GET':
        apertures = Aperture.objects.all().values('id', 'type', 'title', 'status', 'x', 'y').order_by('id')
        serialized_apertures = json.dumps(str(apertures))
        return JsonResponse({"data": serialized_apertures})
    
    else:
        return JsonResponse({"code": "400", "message": "Invalid request method"})


def thermostat(request):
    if request.method == 'POST':
        thermostat_get = Thermostat.objects.get()
        thermostat_get.target_temp = request.POST.get('target_temp')
        thermostat_get.min_temp = request.POST.get('min_temp')
        thermostat_get.max_temp = request.POST.get('max_temp')
        thermostat_get.save()
        return JsonResponse({"code": "200", "message": "Thermostat set", "id": thermostat_get.id})

    elif request.method == 'GET':
        thermostat = Thermostat.objects.all().values('id', 'current_temp', 'target_temp', 'min_temp', 'max_temp').order_by('id')
        serialized_thermostat = json.dumps(str(thermostat))
        return JsonResponse({"data": serialized_thermostat})
    
    else:
        return JsonResponse({"code": "400", "message": "Invalid request method"})


def air_quality(request):
    if request.method == 'POST':
        air_quality_get = Air_Quality.objects.get()
        air_quality_get.co = request.POST.get('co')
        air_quality_get.co2 = request.POST.get('co2')
        air_quality_get.humidity = request.POST.get('humidity')
        air_quality_get.pm = request.POST.get('pm')
        air_quality_get.save()
        return JsonResponse({"code": "200", "message": "Air quality set", "id": air_quality_get.id})

    elif request.method == 'GET':
        air_quality = Air_Quality.objects.all().values('id', 'co', 'co2', 'humidity', 'pm')
        serialized_air_quality = json.dumps(str(air_quality))
        return JsonResponse({"data": serialized_air_quality})
    
    else:
        return JsonResponse({"code": "400", "message": "Invalid request method"})
    

def monthly_report(request):
    # used to filter for specific reports?
    # month = request.POST.get('month')
    # year = request.POST.get('year')

    event_log = Event_Log.objects.all().values('watts_used', 'water_used', 'cost')
    serialized_event_log = json.dumps(str(event_log))
    return JsonResponse({"data": serialized_event_log})


def budget(request):
    if request.method == 'POST':
        budget_get = Budget_Target.objects.get()
        budget_get.max_cost = request.POST.get('max_cost')
        budget_get.max_water = request.POST.get('max_water')
        budget_get.max_energy = request.POST.get('max_energy')
        budget_get.save()
        return JsonResponse({"code": "200", "message": "Budget set", "id": budget_get.id})

    elif request.method == 'GET':
        budgets = Budget_Target.objects.all().values('id', 'max_cost', 'max_water', 'max_energy')
        serialized_budgets = json.dumps(str(budgets))
        return JsonResponse({"data": serialized_budgets})
    
    else:
        return JsonResponse({"code": "400", "message": "Invalid request method"})
    

def create_event(request):
    appliance_id = request.POST.get('appliance_id')
    on_at = request.POST.get('on_at')
    off_at = request.POST.get('off_at')

    # new_event = Event_Log.create()
    return JsonResponse({"code": "200", "message": "Event created"})
    

    