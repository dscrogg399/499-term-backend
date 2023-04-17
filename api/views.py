import json

from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.db.models import F
from datetime import datetime
from django.db.models import Sum, Window, F
from django.db.models.functions import TruncDate
from django.db.models.functions.window import RowNumber
from .event_utils import *
from api.models import *
from django.utils.dateparse import parse_datetime, parse_date
from django.views.decorators.http import require_GET
from .jobs import * 
from calendar import monthrange


def index(request):   
    # test()
    # startup_data_generator()
    # event_loop()
    # door_job()
    return HttpResponse("Team 4")

#appliances, GET returns full list POST toggles appliance and returns updated appliance
def appliances(request):
    if request.method == 'POST':
        input_id = json.loads(request.body)['id']

        try:
            appliance_get = Appliance.objects.get(id=input_id)
            now = datetime.now()
            if appliance_get.is_active:
                appliance_get.toggle_appliance(now)
                message = "Appliance toggled on" if appliance_get.status else "Appliance toggled off"
                return JsonResponse({"code": 200, "message": message, "data": {"pk": int(appliance_get.id), "fields": {"title": str(appliance_get.title), 
                                    "status": appliance_get.status, "x": appliance_get.x, "y": appliance_get.y, 
                                    "appliance_type": appliance_get.appliance_type_id}}})
           
        except Appliance.DoesNotExist:
            return JsonResponse({"code": 404, "message": "appliance does not exist"})

    elif request.method == 'GET':
        appliances = Appliance.objects.all().order_by("id").filter(is_active=True)
        serialized_appliances = serializers.serialize('json', appliances, fields=('id', 'title', 'status', 'x', 'y', 'appliance_type'))
        return JsonResponse({"code": 200, "message": "Appliance list fetched", "data": json.loads(serialized_appliances)})
    
    else:
        return JsonResponse({"code": 400, "message": "Invalid request method"})

#apertures, GET returns full list POST toggles aperture and returns updated aperture
def apertures(request):
    if request.method == 'POST':
        input_id = json.loads(request.body)['id']

        try:
            aperture_get = Aperture.objects.get(id=input_id)
            if aperture_get.is_active:
                aperture_get.status = not aperture_get.status
                aperture_get.save()
                message = "Apertured Opened" if aperture_get.status else "Aperture Closed"
                return JsonResponse({"code": "200", "message": message, "data": {"pk": int(aperture_get.id), "fields": {"title": str(aperture_get.title), 
                                     "status": str(aperture_get.status), "x": str(aperture_get.x), "y": str(aperture_get.y), "type": str(aperture_get.type)}}})

        except Aperture.DoesNotExist:
            return JsonResponse({"code": 404, "message": "aperture does not exist"})

    elif request.method == 'GET':
        apertures = Aperture.objects.all().order_by('id').filter(is_active=True)
        serialized_apertures = serializers.serialize('json', apertures, fields=('id', 'title', 'status', 'x', 'y', 'type'))
        return JsonResponse({"code": 200, "message": "Aperture list fetched", "data": json.loads(serialized_apertures)})
    
    else:
        return JsonResponse({"code": 400, "message": "Invalid request method"})

#thermostat, GET returns thermostat object, POST sets target temp and returns updated thermostat
def thermostat(request):
    if request.method == 'POST':
        thermostat_get = Thermostat.objects.get(id=1)
        thermostat_get.target_temp = json.loads(request.body)['target_temp']
        thermostat_get.save()
        return JsonResponse({"code": 200, "message": "Thermostat set", "data": {"target_temp": thermostat_get.target_temp, "current_temp": thermostat_get.current_temp}})

    elif request.method == 'GET':
        thermostat_get = Thermostat.objects.get()
        return JsonResponse({"code": 200, "message": "Got thermostat", "data": {"target_temp": thermostat_get.target_temp, "current_temp": thermostat_get.current_temp}})
    
    else:
        return JsonResponse({"code": 400, "message": "Invalid request method"})


def air_quality(request):
    if request.method == 'POST':
        air_quality_get = Air_Quality.objects.get()
        air_quality_get.co = json.loads(request.body)['co_level']
        air_quality_get.co2 = json.loads(request.body)['co2_level']
        air_quality_get.humidity = json.loads(request.body)['humidity']
        air_quality_get.pm = json.loads(request.body)['pm_level']
        air_quality_get.save()
        return JsonResponse({"code": 200, "message": "Air quality set", "data": {"co_level": float(air_quality_get.co), "co2_level": float(air_quality_get.co2), 
                             "humidity": float(air_quality_get.humidity), "pm_level": float(air_quality_get.pm)}})

    elif request.method == 'GET':
        air_quality_get = Air_Quality.objects.get()
        return JsonResponse({"code": 200, "message": "Got air quality", "data": {"co_level": float(air_quality_get.co), "co2_level": float(air_quality_get.co2), 
                             "humidity": float(air_quality_get.humidity), "pm_level": float(air_quality_get.pm)}})
    
    else:
        return JsonResponse({"code": 400, "message": "Invalid request method"})
    

def monthly_report(request):
    if request.method == "POST":
        # used to filter for specific reports
        date = parse_date(json.loads(request.body)['date'])

        #get the day of month of the first event in a month
        first_event = Event.objects.filter(
            is_active=True,
            off_at__isnull=False,
            on_at__year=date.year,  # Filter events by the year of the given date
            on_at__month=date.month  # Filter events by the month of the given date
        ).order_by('on_at').first()

        first_day = first_event.on_at.day if first_event else 1

        #get the difference in days between first day of month and first event
        # get all the events for the month excluding the event log for today
        events = Event.objects.filter(
            is_active=True,
            off_at__isnull=False,
            on_at__year=date.year,  # Filter events by the year of the given date
            on_at__month=date.month  # Filter events by the month of the given date
        ).annotate(
            date=TruncDate('on_at')  # Truncate the datetime to date
        ).values(
            'date'  # Group by the date
        ).annotate(
            watts_used=Sum('watts_used'),
            water_used=Sum('water_used'),
            cost=Sum('cost'),
            row_number=Window(expression=RowNumber(), order_by=F('date').asc())
        ).order_by('date')

        #generate empty events if necessary
        final_events = []
        for item in events:
            final_events.append({"date": item['date'], "watts_used": item['watts_used'], "water_used": item['water_used'], "cost": item['cost']})

        return JsonResponse({"code": 200, "message": "Monthly report fetched", "first_day": first_day, "data": final_events}, safe=False)
    else:
        return JsonResponse({"code": 400, "message": "Invalid request method"})


def budget(request):
    if request.method == 'POST':
        budget_get = Budget_Target.objects.get()
        budget_get.max_cost = json.loads(request.body)['max_cost']
        budget_get.max_water =  json.loads(request.body)['max_water']
        budget_get.max_energy = json.loads(request.body)['max_energy']
        budget_get.is_active = json.loads(request.body)['is_active']
        budget_get.save()
        return JsonResponse({"code": 200, "message": "Budget set", "data": {"id": int(budget_get.id), "max_cost": float(budget_get.max_cost), 
                             "max_water": float(budget_get.max_water), "max_energy": float(budget_get.max_energy), "is_active": bool(budget_get.is_active)}})

    elif request.method == 'GET':
        budget_get = Budget_Target.objects.get()
        return JsonResponse({"code": 200, "message": "Budget fetched", "data": {"id": int(budget_get.id), "max_cost": float(budget_get.max_cost), 
                             "max_water": float(budget_get.max_water), "max_energy": float(budget_get.max_energy), "is_active": bool(budget_get.is_active)}})
    
    else:
        return JsonResponse({"code": 400, "message": "Invalid request method"})
    

def create_event(request):
    if request.method == 'POST':
        appliance_id = json.loads(request.body)['appliance_id']
        on_at = parse_datetime(json.loads(request.body)['on_at'])
        off_at = parse_datetime(json.loads(request.body)['off_at'])

        try:
            appliance = Appliance.objects.get(id=appliance_id)
            new_event = Event.start_event(appliance_id, on_at, True)
            new_event.save()
            new_event.end_event(off_at, appliance.appliance_type_id)


            return JsonResponse({"code": 200, "message": "Event created", "data": {"pk": int(new_event.id), "fields": {"appliance": new_event.appliance.id,  "on_at": new_event.on_at, "off_at": new_event.off_at, "watts_used": new_event.watts_used, "water_used": new_event.water_used, "cost": new_event.cost, "created_at": new_event.created_at,  "is_active": new_event.is_active, "title": appliance.title}
                             }})
        except Exception as e:
            return JsonResponse({"code": 500, "message": str(e)})
    else:
        return JsonResponse({"code": 400, "message": "Invalid request method"})
    

@require_GET
def get_todays_events(request):
    now = datetime.now()
    events = Event.objects.filter(
        is_active=True,
        off_at__isnull=False,
        on_at__date=now
    ).select_related('appliance').order_by('-on_at')

    serialized_events = serializers.serialize(
        'json',
        events,
        fields=('pk', 'appliance', 'on_at', 'off_at', 'watts_used', 'water_used', 'cost', 'created_at', 'is_active'),
        use_natural_primary_keys=True,
        use_natural_foreign_keys=True
    )

    serialized_events_list = json.loads(serialized_events)
    for event, appliance in zip(serialized_events_list, events):
        event['fields']['title'] = appliance.appliance.title

    return JsonResponse({"code": 200, "message": "Today's events fetched", "data": serialized_events_list}, safe=False)
    
        
    

    

    