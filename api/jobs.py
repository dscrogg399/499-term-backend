from django .conf import settings
import json
from .weather import getTemperature, getHumidity
import random
import numpy as np
from datetime import datetime, time, timezone

from api.models import Air_Quality, Aperture

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
