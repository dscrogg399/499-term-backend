#import request
from django.conf import settings
import re
import random
from datetime import datetime, timedelta
from .models import Appliance
from django .conf import settings
import json
from .weather import getTemperature, getHumidity, getTemperatureAtTime
#import numpy as np
from datetime import datetime, time, timezone, timedelta
from api.models import Air_Quality, Aperture, Thermostat, Aperture, Appliance, Event_Log, Event
import numpy as np

#import googleapiclient.discovery
#import googleapiclient.errors
#from main.models import Media

#start and end time of busy time is always the same, 6-7 pm. This is converted to UTC time
start_time = time(23, 0, 0)
end_time = time(0, 0, 0)

""" This job runs every five minutes. It updates the air quality values in the database.
I gathered average values for CO, CO2, PM, and humidity from these sites:
CO: https://www.epa.gov/indoor-air-quality-iaq/what-average-level-carbon-monoxide-homes#:~:text=Average%20levels%20in%20homes%20without,be%2030%20ppm%20or%20higher.
CO2: https://www.co2meter.com/blogs/news/co2-levels-at-home
PM 2.5: https://www.indoorairhygiene.org/pm2-5-explained/
Humidity: https://indoortemp.com/resources/ideal-home-humidity-level-control

I then varied these values randomly within a target range depending on a few things:
Busy time - betwen 6pm - 7pm is the busiest time of day for the family, when the most appliances will be on, they will probably be cooking
and the family will be gathered together breathing a lot.
Apertures open - if any apertures are open, this can significantly affect the concetrations of each of these

CO:
    When its busy more appliances are on so CO is higher
    When apertures are open, CO is lower because it is equalized with the air outisde
CO2:
    When its busy more appliances are on so CO2 is higher and more people are in the house breathing
    When apertures are open, CO2 is lower because it is equalized with the air outisde
PM 2.5:
    Actions the family does don't affect PM that much, so its only slightly raised during busy time but has a higher delta
    When apertures are open, PM is actually higher since the PM of outside air in birmingham is always higher than inse
    This is because birmingham's poor air quality + AC units filtering the air
Humidity:
    When its busy, more hot water is probably being used and more people are breathing, so humidity is higher
    When apertures are open, humidity is equalized withing a very small delta of outside air

"""
def air_quality_job():
    #get current time
    curr_time = datetime.now().time()
    is_busy = False
    is_aps_open = False

    #check if its busy time
    if curr_time >= start_time and curr_time <= end_time:
        is_busy = True
    
    #get Apertures where status = true, if we have any set is_aps_open = true
    apertures = Aperture.objects.filter(status=True)
    if (apertures.count() > 0):
        is_aps_open = True
    
    air_quality = Air_Quality.objects.get(id=1)
    air_quality.co = vary_co(air_quality.co, is_aps_open, is_busy)
    air_quality.co2 = vary_co2(air_quality.co2, is_aps_open, is_busy)
    air_quality.pm = vary_pm(air_quality.pm, is_aps_open, is_busy)
    air_quality.humidity = vary_hum(air_quality.humidity, is_aps_open, is_busy)
    air_quality.save()


#helper function that takes in a current value, the target value, and the delta to vary by.
def calc_new_value(curr_val, target, delta):
    min = target - delta
    max = target + delta

    #val needs to be raised
    if curr_val < min:
        diff = min - curr_val
        change = random.uniform(0.5 * diff, diff)
        return curr_val + change
    #val needs to be lowered
    elif curr_val > max:
        diff = curr_val - max
        change = random.uniform(0.5 * diff, diff)
        return curr_val - change
    #val is within range
    else:
        return target + random.uniform(-delta, delta)


def vary_co(curr_co, aps_open, busy):
    co_delta = 0
    co_target = 0
    #busy with apertures closed, high target and high delta
    if busy:
        co_target = 5
        co_delta = 1
        #busy with apertures open, low target and low delta
        if aps_open:
            co_target = 0.5
            co_delta = 0.1
    #not busy with apertures open, low target and low delta
    elif aps_open:
        co_target = 0.5
        co_delta = 0.1
    #not busy with apertures closed, medium target and medium delta
    else:
        co_target = 2.5
        co_delta = 0.2

    #get the new varied value, rounded
    return round(calc_new_value(curr_co, co_target, co_delta))

    

def vary_co2(curr_co2, aps_open, busy):
    co2_delta = 0
    co2_target = 0
    #busy with apertures closed, high target and high delta
    if busy:
        co2_target = 1100
        co2_delta = 300
        #busy with apertures open, medium target and medium delta
        if aps_open:
            co2_target = 500
            co2_delta = 200
    #not busy with apertures open, low target and low delta
    elif aps_open:
        co2_target = 450
        co2_delta = 100
    #not busy with apertures closed, medium target and medium delta
    else:
        co2_target = 700
        co2_delta = 200
    
    #get the new varied value, rounded
    return round(calc_new_value(curr_co2, co2_target, co2_delta))

    

def vary_pm(curr_pm, aps_open, busy):
    pm_delta = 0
    pm_target = 0
    #busy with apertures closed, medium target and medium delta
    if busy:
        pm_target = 15
        pm_delta = 5
        #busy with apertures open, high target and high delta
        if aps_open:
            pm_target = 25
            pm_delta = 10
    #not busy with apertures open, medium target and high delta
    elif aps_open:
        pm_target = 20
        pm_delta = 10
    #not busy with apertures closed, low target and low delta
    else:
        pm_target = 12
        pm_delta = 2.5
    
    #get the new varied value, unrounded
    return calc_new_value(curr_pm, pm_target, pm_delta)

def vary_hum(curr_hum, aps_open, busy):
    hum_delta = 0
    hum_target = 0

    #with humidity, its more important if the apertures are open or closed so we check that first
    #apertures open, get target humidity from the outdoor weather
    if aps_open:
        humidity = getHumidity()
        hum_target = humidity / 100
        hum_delta = 0.02
    #otherwise, we vary slights for busy vs not busy
    else:
        if busy:
            hum_target = 0.55
            hum_delta = 0.2
        else:
            hum_target = 0.45
            hum_delta = 0.15

    #get the new varied value, rounded to 2 decimal places
    return round(calc_new_value(curr_hum, hum_target, hum_delta), 2)


""" This is the hvac job. It takes a given time and updates the current temp of the thermostat 
    based off several things:
    1. If the HVAC is on, +- 1 degree/minute until the temp exceeds the target in either direction
    2. Also takes into account outside temp and open apertures
        a. Outside temp changes inside temp by 0.033 degrees * the difference between the outside temp and the inside temp / minute
        b Open apertures calculate in a similar way but with much higher rates of change, 0.4 for doors and 0.2 for windows
    
    It then determines whether its necessary to turn the HVAC on or off.

    This job runs every minute by default and can be called to generate historical data by passing in a date time that isnt current
    This function will be called from the normal event loop if the time is not between 23:59 and 00:00, to avoid issues with event log generation
"""
def hvac_job():
    #update this to use a date time from params
    now= datetime.now()

    #get the thermostat and HVAC (thermostat id = 1, HVAC id = 34)
    thermostat = Thermostat.objects.get(id=1)
    hvac = Appliance.objects.get(id=34)

    #target temp
    target_temp = thermostat.target_temp

    #min and max temp range
    min = target_temp - 2
    max = target_temp + 2

    #store current temp to manipulate
    current_temp = thermostat.current_temp

    #calculate if temperature is higher or lower than target
    higher = thermostat.current_temp > thermostat.target_temp

    #if the hvac is already on, add or subtract one based off higher
    if hvac.status:
        if higher:
            current_temp -= 1
        else:
            current_temp += 1

    #now calculate the updated temp from outside temp difference and apertures using the current temp after hvac changes
    updated_temp = temperature_calculation(current_temp, now)

    #now manage the hvac based on the updated temp
    #if the hvac is already on
    if hvac.status:
        #if the current temp was higher and is now lower than the target temp
        if higher and updated_temp < target_temp:
            #toggle the hvac off, need the function
            hvac.toggle_appliance(now)
        #if the current temp was lower and is now higher than the target temp
        elif not higher and updated_temp > target_temp:
            #toggle the hvac off
            hvac.toggle_appliance(now)
    #if the hvac is off and the updated temp is outside the min and max range
    elif updated_temp < min or updated_temp > max:
        #toggle the hvac on
        hvac.toggle_appliance(now)

    #update the thermostat
    thermostat.current_temp = updated_temp
    thermostat.save()
    #update the hvac
    hvac.save()
    
def temperature_calculation(current_temp, now):
    #get the current temperature outside and the thermostat
    outdoor = getTemperatureAtTime(now)

    
    #deltas are calculated per 10 degrees of difference between the outside and the inside
    diff = current_temp - outdoor
    temp_scale = diff/ 10

    #get the doors and windows
    doors = Aperture.objects.filter(type=1, status = True)
    windows = Aperture.objects.filter(type=2, status = True)

    #calculate the deltas, multiply by the temp scale. This will give positibe or negative deltas depending on outdoor temp
    #passive delta is 0.033/min
    temp_delta = 0.033 * temp_scale
    #doors have a temp delta of 0.4/min
    door_delta = (doors.count() * 0.4) * temp_scale
    #windows have a temp delta of 0.2/min
    window_delta = (windows.count() * 0.2) * temp_scale

    total_delta = temp_delta + door_delta + window_delta

    #calculate and set the new temperature
    return current_temp - total_delta

def is_weekday(time_period):
    return time_period.weekday() < 5

def time_in_range(now, start, end):
    return start <= now <= end

def random_time(begin, end):
    return begin + timedelta(minutes=random.uniform(0,(end-begin).seconds//60))
   
def random_duration(begin, end):
    return timedelta(minutes = random.uniform(begin, end))

def should_event_occur(probability, start, end, now):
    if not time_in_range(now, start, end):
        return False
    total_minutes = int((end - start).total_seconds() / 60)
    adjusted_probability = 1 - (1 - probability) ** (1 / total_minutes)
    
    return random.random() < adjusted_probability

def event_loop():
    now = datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=2)
    #get the current time
    on_Appliances = Appliance.objects.filter(status = True, is_active = True)
    off_Appliances =  Appliance.objects.filter(status = False, is_active = True)

    for appliance in off_Appliances:
        if appliance.id == 33:
            # start = now.replace(hour=23, minute=0) + timedelta(days=-1)
            # end = now.replace(hour=3, minute=59)
            # current_datetime = start

            trues = 0
            not_trues = 0
            for _ in range(10000):
                start = now.replace(hour=23, minute=0) + timedelta(days=-1)
                end = now.replace(hour=3, minute=59)
                current_datetime = start
                event_occurred = False
                while current_datetime < end and not event_occurred:
                    if should_event_occur(0.99, start, end, current_datetime):
                        trues += 1
                        event_occurred = True
                    current_datetime += timedelta(minutes=1)
                if not event_occurred:
                    not_trues += 1
            
            print(trues)
            print(not_trues)
            print(trues / (trues + not_trues))


def event_summary():

    now = datetime.utcnow().replace(tzinfo=None)
    tomorrow = now.replace(hour=00, minute=00, second=00, microsecond=00) + timedelta(days=1)

    # list of appliance ids that were toggled off
    toggled_ids = []

    appliances = Appliance.objects.all().order_by("id").filter(is_active=True)
    for appliance in appliances:
        # only turn off appliances that are still on
        if appliance.status == True:
            appliance.toggle_appliance(now)
            # save the toggled appliance id to list to use for turning back on 
            toggled_ids.append(appliance.id)

    # get todays log, where the created at date matches the current day, month and year
    # also get today's events for summing the total water and power used
    try:
        todays_log = Event_Log.objects.get(is_active=True, created_at__day=now.day, created_at__month=now.month, created_at__year=now.year)
    except Event_Log.MultipleObjectsReturned:
        print("\n Multiple logs exist for this day:")
        print(Event_Log.objects.all().values())
    todays_events = Event.objects.all().filter(is_active=True, off_at__isnull=False, on_at__date=datetime.now().date())

    # for loops sum total water and power from all the day's events
    water_sum = 0
    for event in todays_events:
        water_sum += event.water_used
    watts_sum = 0
    for event in todays_events:
        watts_sum += event.watts_used

    # calculate total cost from sums and set to today's log, save to DB
    total_cost = (water_sum * 0.003368984) + (watts_sum * 0.00012)
    todays_log.water_used = water_sum
    todays_log.watts_used = watts_sum
    todays_log.cost = total_cost
    todays_log.save()

    # create a log for the new (next) day, using the time delta value of tomorrow, save to DB
    new_day_log = Event_Log.create(True)
    new_day_log.save()
    new_day_log.created_at = tomorrow
    new_day_log.save()

    # re query appliances to get any updates. renamed to avoid any issues with previous query variable
    appliances_again = Appliance.objects.all().order_by("id").filter(is_active=True)
    # if any appliances were toggled off, then use those ids to match them from appliances 
    # and turn them back on with the now time being tomorrow
    if len(toggled_ids) > 0:
        for appliance_two in appliances_again:
            for toggle_id in toggled_ids:
                if appliance_two.id == toggle_id:
                    appliance_two.toggle_appliance(tomorrow)

    



# weekday_prob_dict = {
#     # Mbed lamp 1
#     1: {
#         "pm": {
#             "start": {
#                 "hour": 20,
#                 "minute": 30,
#                 "delta": 10
#             },
#             "end": {
#                 "hour": 10,
#                 "minute": 30,
#                 "delta": 10
#             }
#         },
#     },
#     # Mbed lamp 2
#     2: {
#         "pm": {
#             "start": {
#                 "hour": 20,
#                 "minute": 30,
#                 "delta": 10
#                 },
#             "end": {
#                 "hour": 10,
#                 "minute": 30,
#                 "delta": 10
#             }
#         },
#     },
#     #Mbed overhead light
#     3: {
#         "am": {
#             "start": {
#                 "hour": 5,
#                 "minute": 0,
#                 "delta": 10
#             },
#             "end": {
#                 "hour": 7,
#                 "minute": 25,
#                 "delta": 2
#             },
#         "pm": {
#             "start": {
#                 "hour": 17,
#                 "minute": 30,
#                 "delta": 10
#             },
#             "end": {
#                 "hour": 20,
#                 "minute": 30,
#                 "delta": 10
#             }
#         }
#         }
#     },
#     #Mbath overhead light
#     4: {
#         "pm": {
#             "start": {
#                 "hour": 18,
#                 "minute": 0,
#             },
#             "end": {
#                 "hour": 20,
#                 "minute": 30,
#             },
#             "num": 3,
#             "delta": 2,
#             "duration": 6,
#             "dur_delta": 4
#         },



#     },
#     #bathroom overhead light
#     5: {
#         "pm": {
#             "start": {
#                 "hour": 18,
#                 "minute": 0,
#             },
#             "end": {
#                 "hour": 20,
#                 "minute": 30,
#             },
#             "num": 3,
#             "delta": 2,
#             "duration": 6,
#             "dur_delta": 4
#         },
#     },
#     #Bedroom 1 lamp 1
#     6: {
#         "pm": {
#             "start": {
#                 "hour": 19,
#                 "minute": 30,
#             },
#             "end": {
#                 "hour": 20,
#                 "minute": 30,
#             },
#         },
#     },
#     #Bedroom 1 lamp 2
#     7: {
#         "pm": {
#             "start": {
#                 "hour": 19,
#                 "minute": 30,
#             },
#             "end": {
#                 "hour": 20,
#                 "minute": 30,
#             },
#         },
#     },
#     #Bedroom 1 overhead light
#     8: {
#         "am": {
#             "start": {
#                 "hour": 6,
#                 "minute": 0,
#                 "delta": 10
#             },
#             "end": {
#                 "hour": 7,
#                 "minute": 25,
#                 "delta": 2
#             },
#         },
#         "pm": {
#             "start": {
#                 "hour": 16,
#                 "minute": 0,
#                 "delta": 10
#             },
#             "end": {
#                 "hour": 19,
#                 "minute": 30,
#                 "delta": 10
#             },
#         },
#     },
#     #Bedroom 2 lamp 1
#     9: {
#         "pm": {
#             "start": {
#                 "hour": 19,
#                 "minute": 30,
#             },
#             "end": {
#                 "hour": 20,
#                 "minute": 30,
#             },
#         },
#     },
#     #Bedroom 2 lamp 2
#     10: {
#         "pm": {
#             "start": {
#                 "hour": 19,
#                 "minute": 30,
#             },
#             "end": {
#                 "hour": 20,
#                 "minute": 30,
#             },
#         },
#     },
#     #Bedroom 2 overhead light
#     11: {
#         "am": {
#             "start": {
#                 "hour": 6,
#                 "minute": 0,
#                 "delta": 10
#             },
#             "end": {
#                 "hour": 7,
#                 "minute": 25,
#                 "delta": 2
#             },
#         },
#         "pm": {
#             "start": {
#                 "hour": 16,
#                 "minute": 0,
#                 "delta": 10
#             },
#             "end": {
#                 "hour": 19,
#                 "minute": 30,
#                 "delta": 10
#             },
#         },
#     },
#     #kitchen overhead light
#     12: {
#         "am": {
#             "start": {
#                 "hour": 6,
#                 "minute": 0,
#                 "delta": 10
#             },
#             "end": {
#                 "hour": 7,
#                 "minute": 25,
#                 "delta": 2
#             },
#         },
#         "pm": {
#             "start": {
#                 "hour": 16,
#                 "minute": 0,
#                 "delta": 10
#             },
#             "end": {
#                 "hour": 19,
#                 "minute": 30,
#                 "delta": 10
#             },
#         },
#     },
#     #LR lamp 1
#     13: {
#         "pm": {
#             "start": {
#                 "hour": 16,
#                 "minute": 0,
#             },
#             "end": {
#                 "hour": 20,
#                 "minute": 30,
#             },
#             "num": 6,
#             "delta": 4,
#             "duration": 27,
#             "dur_delta": 15
#         },
#     },
#     #LR lamp 2
#     14: {
#         "pm": {
#             "start": {
#                 "hour": 16,
#                 "minute": 0,
#             },
#             "end": {
#                 "hour": 20,
#                 "minute": 30,
#             },
#             "num": 6,
#             "delta": 4,
#             "duration": 27,
#             "dur_delta": 15
#         },
#     },
#     #LR overhead
#     15: {
#         "am": {
#             "start": {
#                 "hour": 6,
#                 "minute": 0,
#                 "delta": 10
#             },
#             "end": {
#                 "hour": 7,
#                 "minute": 25,
#                 "delta": 2
#             },
#         },
#         "pm": {
#             "start": {
#                 "hour": 16,
#                 "minute": 0,
#                 "delta": 10
#             },
#             "end": {
#                 "hour": 19,
#                 "minute": 30,
#                 "delta": 10
#             },
#         },
#     },
#     #Mbed tv
#     16: {
#         "am": {
#             "start": {
#                 "hour": 5,
#                 "minute": 30,
#                 "delta": 10
#             },
#             "end": {
#                 "hour": 6,
#                 "minute": 30,
#                 "delta": 10
#             },
#         },
#         "pm": {
#             "start": {
#                 "hour": 21,
#                 "minute": 0,
#                 "delta": 10
#             },
#             "end": {
#                 "hour": 22,
#                 "minute": 30,
#                 "delta": 10
#             },
#         },
#     },
#     #lr tv
#     17: {
#         "am": {
#             "start": {
#                 "hour": 6,
#                 "minute": 0,
#                 "delta": 10
#             },
#             "end": {
#                 "hour": 7,
#                 "minute": 0,
#                 "delta": 10
#             },
#         },
#         "pm": {
#             "start": {
#                 "hour": 4,
#                 "minute": 0,
#                 "delta": 10
#             },
#             "end": {
#                 "hour": 7,
#                 "minute": 30,
#                 "delta": 10
#             },
#             "duration": 180,
#             "dur_delta": 30
#         },
#     },
#     #mbath shower
#     25: {
#         "am": {
#             "start": {
#                 "hour": 5,
#                 "minute": 10,
#                 "delta": 5,
#                 "duration": 15,
#                 "dur_delta": 2
#             },
#         }
#     },
#     #bathroom bath
#     28: {
#         "am": {
#             "start": {
#                 "hour": 6,
#                 "minute": 0,
#                 "delta": 5,
#                 "duration": 15,
#                 "dur_delta": 2
#             },
#         }
#     },
#     #stove
#     30: {
#         "pm": {
#             "start": {
#                 "hour": 18,
#                 "minute": 30,
#                 "delta": 30,
#                 "duration": 15,
#                 "dur_delta": 2
#             },
#         }
#     },
#     #oven
#     31: {
#         "pm": {
#             "start": {
#                 "hour": 18,
#                 "minute": 30,
#                 "delta": 30,
#                 "duration": 45,
#                 "dur_delta": 0
#             },
#     }
#     },
#     #microwave
#     32: {
#         "am": {
#             "start": {
#                 "hour": 6,
#                 "minute": 0,
#                 "delta": 10,
#             },
#             "end": {
#                 "hour": 7,
#                 "minute": 0,
#                 "delta": 10,
#             },
#             "duration": 10,
#             "dur_delta": 2
#         },
#         "pm": {
#             "start": {
#                 "hour": 16,
#                 "minute": 0,
#                 "delta": 10,
#             },
#             "end": {
#                 "hour": 20,
#                 "minute": 0,
#                 "delta": 10,
#             },
#             "duration": 10,
#             "dur_delta": 2
#         }
#     },
#     #dishwasher
#     33: {
#         "probability": 0.57,
#         "start": {
#             "hour": 19,
#             "minute": 00,
#             "delta": 10,
#         },
#         "duration": 45,
#     },
#     #washer
#     34: {
#         "probability": 0.57,
#         "start": {
#             "hour": 17,
#             "minute": 0,
#             "delta": 10,    
#         },
#         "duration": 30,
#     },
# }

