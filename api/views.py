from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django import forms
from django.core import serializers
from django.core.serializers import serialize
from django.forms.models import model_to_dict
from django.db.models import F
from datetime import datetime
import json
import pytz

from api.models import *
from .jobs import event_loop
from django.utils.dateparse import parse_datetime, parse_date


def index(request):   
    event_loop()
    return HttpResponse("Team 4")


def appliances(request):
    if request.method == 'POST':
        input_id = request.POST.get('id')

        try:
            appliance_get = Appliance.objects.get(id=input_id)
            now = datetime.utcnow().replace(tzinfo=None)
            appliance_get.toggle_appliance(now)
            if appliance_get.is_active:
                message = "Appliance toggled on" if appliance_get.status else "Appliance toggled off"
                return JsonResponse({"code": "200", "message": message, "data": {"pk": int(appliance_get.id), "fields": {"title": str(appliance_get.title), 
                                    "status": str(appliance_get.status), "x": str(appliance_get.x), "y": str(appliance_get.y), 
                                    "type": str(appliance_get.appliance_type.title)}}})
           
        except Appliance.DoesNotExist:
            return JsonResponse({"code": "404", "message": "appliance does not exist"})

    elif request.method == 'GET':
        appliances = Appliance.objects.all().order_by("id").filter(is_active=True)
        serialized_appliances = serializers.serialize('json', appliances, fields=('id', 'title', 'status', 'x', 'y', 'appliance_type'))
        return JsonResponse({"code": 200, "message": "Appliance list fetched", "data": json.loads(serialized_appliances)})
    
    else:
        return JsonResponse({"code": "400", "message": "Invalid request method"})


def apertures(request):
    if request.method == 'POST':
        input_id = request.POST.get('id')

        try:
            aperture_get = Aperture.objects.get(id=input_id)
            if aperture_get.is_active:
                aperture_get.status = not aperture_get.status
                aperture_get.save()
                message = "Apertured Opened" if aperture_get.status else "Aperture Closed"
                return JsonResponse({"code": "200", "message": message, "data": {"pk": int(aperture_get.id), "fields": {"title": str(aperture_get.title), 
                                     "status": str(aperture_get.status), "x": str(aperture_get.x), "y": str(aperture_get.y), "type": str(aperture_get.type)}}})

        except Aperture.DoesNotExist:
            return JsonResponse({"code": "404", "message": "aperture does not exist"})

    elif request.method == 'GET':
        apertures = Aperture.objects.all().order_by('id').filter(is_active=True)
        serialized_apertures = serializers.serialize('json', apertures, fields=('id', 'title', 'status', 'x', 'y', 'type'))
        return JsonResponse({"code": 200, "message": "Aperture list fetched", "data": json.loads(serialized_apertures)})
    
    else:
        return JsonResponse({"code": "400", "message": "Invalid request method"})


def thermostat(request):
    if request.method == 'POST':
        thermostat_get = Thermostat.objects.get()
        thermostat_get.target_temp = request.POST.get('target_temp')
        thermostat_get.save()
        return JsonResponse({"code": "200", "message": "Thermostat set", "data": {"target_temp": thermostat_get.target_temp, "current_temp": thermostat_get.current_temp}})

    elif request.method == 'GET':
        thermostat_get = Thermostat.objects.get()
        return JsonResponse({"code": "200", "message": "Got thermostat", "data": {"target_temp": thermostat_get.target_temp, "current_temp": thermostat_get.current_temp}})
    
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
        return JsonResponse({"code": "200", "message": "Air quality set", "data": {"co_level": float(air_quality_get.co), "co2_level": float(air_quality_get.co2), 
                             "humidity": float(air_quality_get.humidity), "pm_level": float(air_quality_get.pm)}})

    elif request.method == 'GET':
        air_quality_get = Air_Quality.objects.get()
        return JsonResponse({"code": "200", "message": "Got air quality", "data": {"co_level": float(air_quality_get.co), "co2_level": float(air_quality_get.co2), 
                             "humidity": float(air_quality_get.humidity), "pm_level": float(air_quality_get.pm)}})
    
    else:
        return JsonResponse({"code": "400", "message": "Invalid request method"})
    

def monthly_report(request):
    if request.method == "GET":
        # used to filter for specific reports
        date = parse_date(request.GET.get('date'))


        event_logs = Event_Log.objects.all().order_by('id').filter(is_active=True, created_at__month=date.month, created_at__year=date.year)
    
        serialized_event_logs = serializers.serialize('json', event_logs)
        return JsonResponse({"code": "200", "message": "Monthly report fetched", "data": json.loads(serialized_event_logs)})
    else:
        return JsonResponse({"code": "400", "message": "Invalid request method"})


def budget(request):
    if request.method == 'POST':
        budget_get = Budget_Target.objects.get()
        budget_get.max_cost = request.POST.get('max_cost')
        budget_get.max_water = request.POST.get('max_water')
        budget_get.max_energy = request.POST.get('max_energy')
        if 'is_active' in request.POST:
            print(request.POST.get('is_active'))
            budget_get.is_active = request.POST.get('is_active').lower() == 'true'
        budget_get.save()
        return JsonResponse({"code": "200", "message": "Budget set", "data": {"id": int(budget_get.id), "max_cost": float(budget_get.max_cost), 
                             "max_water": float(budget_get.max_water), "max_energy": float(budget_get.max_energy), "is_active": bool(budget_get.is_active)}})

    elif request.method == 'GET':
        budget_get = Budget_Target.objects.get()
        return JsonResponse({"code": "200", "message": "Budget fetched", "data": {"id": int(budget_get.id), "max_cost": float(budget_get.max_cost), 
                             "max_water": float(budget_get.max_water), "max_energy": float(budget_get.max_energy), "is_active": bool(budget_get.is_active)}})
    
    else:
        return JsonResponse({"code": "400", "message": "Invalid request method"})
    

def create_event(request):
    if request.method == 'POST':
        appliance_id = request.POST.get('appliance_id')
        on_at = parse_datetime(request.POST.get('on_at'))
        off_at = parse_datetime(request.POST.get('off_at'))

        try:
            appliance = Appliance.objects.get(id=appliance_id)
            event_log = Event_Log.objects.filter(is_active=True).latest('created_at')
            new_event = Event.start_event(appliance_id, event_log.id, on_at, True)
            new_event.save()
            new_event.end_event(off_at, appliance.appliance_type_id)


            return JsonResponse({"code": "200", "message": "Event created", "data": {"id": int(new_event.id), 
                             "appliance_id": new_event.appliance.id, "on_at": new_event.on_at, "off_at": new_event.off_at, "log_id": new_event.log_id, "watts_used": new_event.watts_used, "water_used": new_event.water_used, "cost": new_event.cost}})
        except Exception as e:
            return JsonResponse({"code": "500", "message": str(e)})
    else:
        return JsonResponse({"code": "400", "message": "Invalid request method"})
    

def get_todays_events(request):

    if request.method == 'GET':
        # get events and values, with appliance title from the appliance model
        # filter active events where off_at is not null (has been turned off) and the on_at is the same as current day
        # order query set by most recent events based on when they were turned off
        events = Event.objects.all().order_by('on_at').filter(is_active=True, off_at__isnull=False, on_at__date=datetime.now().date())

        serialized_events = serializers.serialize('json', events)
        return JsonResponse({"code": "200", "message": "Today's events fetched", "data": json.loads(serialized_events)})
    else:
        return JsonResponse({"code": "400", "message": "Invalid request method"})
    
        
    

    

    