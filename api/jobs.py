#import request
from django.conf import settings
import re
import random
from datetime import datetime, timedelta
from .models import Appliance
import simpy
from django .conf import settings
import json
from .weather import getTemperature, getHumidity, getTemperatureAtTime
import numpy as np
from datetime import datetime, time, timezone
from api.models import Air_Quality, Aperture, Thermostat, Aperture, Appliance

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
    print("running air quality job")
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
            hvac.status  = False
        #if the current temp was lower and is now higher than the target temp
        elif not higher and updated_temp > target_temp:
            #toggle the hvac off
            hvac.status = False
    #if the hvac is off and the updated temp is outside the min and max range
    elif updated_temp < min or updated_temp > max:
        #toggle the hvac on
        hvac.status = True
    
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

def time_in_range(time_period, begin, end):
    return begin <= time_period.time() <= end

def random_time(begin, end):
    return begin + timedelta(minutes=random.uniform(0,(end-begin).seconds//60))
   
def random_duration(begin, end):
    return timedelta(minutes = random.uniform(begin, end))

def clothes_dryer_washer (env, time_period):
    currentAppliance = Appliance()

    if is_weekday(time_period):
       begin = datetime.strptime("5:30 PM", "%I%M %p").time()
       end = (datetime.strptime("5:30 PM", "%I:%M %p") + timedelta(minutes=10)).time()
       
       if time_in_range(time_period, begin, end) and random.random() < 0.57 and currentAppliance.title == "Washer":
           currentAppliance.status = True
           
       if time_in_range(time_period, begin, end) and currentAppliance.title == "Dryer":
                dryer_begin = end(datetime.strptime(begin) + timedelta(minutes = 5)).time()
                currentAppliance.status = True
           
def dishwasher (env, time_period):
    currentAppliance = Appliance()
    
    if is_weekday(time_period):
        
       begin = datetime.strptime("7:00 PM", "%I%M %p").time()
       end = (datetime.strptime("7:00 PM", "%I:%M %p") + timedelta(minutes=10)).time()
       
       if time_in_range(time_period, begin, end) and random.random() < 0.57 and currentAppliance.title == "Dishwasher":
           currentAppliance.status = True
           

def MasterBedroomTV(env, time_period):
    if is_weekday(time_period):
        0
        
        
def Refrigerator(env, time_period):
    currentAppliance = Appliance()
    begin = datetime.strptime("12:00 AM", "%I%M %p").time()
    end = (datetime.strptime("11:59 PM", "%I:%M %p"))
    
    if(currentAppliance.title == "Refrigerator" and time_in_range(time_period, begin, end)):
         currentAppliance.status = True
         

#def 
    
    
    
           
           
           
           
       
   
   
   
   
   
   
   
   
   
   
   
   # startTime = None
   
   # currentAppliance = Appliance()
   # timeInterval = None
   # for i in currentAppliance():
       # if currentAppliance.title == "Washer":
            # code that takes 57% chances into account
            # code that executes at 5:30pm for around 10 mins
        
        # not actual appliance names but dummy names until access them from db
     #   if(currentAppliance.title == "MBR Shower" or "BR Shower"):
        #status = true: on/open
        #status = false: off/closed
        #if(status = true)
                    
            
       # if(currentAppliance.title == "MBD Lamp 1" or "MBD Lamp 2" or "BD1 Lamp 1" or "BD1 Lamp 2" or "BD2 Lamp 1" or "BD2 Lamp 2" ):
            
        
       # if(currentAppliance.title == "LR Lamp 1" or "LR Lamp 2")
        
        # Master light?
     #   if(currentAppliance.title == "MBD Overhead" or "MBR Overhead"):
        
        #Bathroom Light?
      #  if(currentAppliance.title == "BR Overhead"):
            
        
       # if(currentAppliance.title == "BD1 Overhead or BD2 Overhead"):
        
        # LR Light?
        #if(currentAppliance.title == "KTC Overhead" or "LR Overhead"):
        
        
        #if(currentAppliance.title == "MBD TV"):
        
        
        #if(currentAppliance.title == "LR TV"):
        
        
        #if(currentAppliance.title == "MBR Fan" or "BR Fan"):
        
        #Master Bathroom Sink?
        #if(currentAppliance.title == "MBR Sink 1" or "MBR Sink 2" or "BR Sink"):
        
        
        #if(currentAppliance.title == "KTC Sink"):
        
        
        #if(currentAppliance.title == "Outdoor Tap"):
        
        # Master Bedroom and Bedroom Bath?
        #if(currentAppliance.title == "MBR Bath" or "BR Bath"):
        
        
        #if(currentAppliance.title == "Refrigerator"):
        
        
        #if(currentAppliance.title == "Stove"):
        
        
        #if(currentAppliance.title == "Oven"):
        
        
        #if(currentAppliance.title == "Microwave"):
        
        
        #if(currentAppliance.title == "Dishwasher"):
        
        
        #if(currentAppliance.title == "HVAC"):
        
        
        #if(currentAppliance.title == "Washer"):
        
        
        #if(currentAppliance.title == "Dryer"):
        
        
        #if(currentAppliance.title == "Water Heater"):
    
