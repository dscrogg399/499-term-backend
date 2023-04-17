from datetime import datetime, timedelta
import random
from api.air_utils import vary_co, vary_co2, vary_hum, vary_pm
from api.event_utils import should_event_occur
from api.hvac_utils import temperature_calculation
from api.utils import time_in_range
from .weather import getTemperatureAtTime
from datetime import datetime, time, timedelta
from api.models import Air_Quality, Aperture, Thermostat, Aperture, Appliance
import time as t

#start and end time of busy time is always the same, 6-7 pm. This is converted to UTC time
start_time = time(18, 0, 0)
end_time = time(19, 0, 0)

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
    if time_in_range(curr_time, start_time, end_time):
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





""" This is the hvac job. It takes a given time and updates the current temp of the thermostat 
    based off several things:
    1. If the HVAC is on, +- 1 degree/minute until the temp exceeds the target in either direction
    2. Also takes into account outside temp and open apertures
        a. Outside temp changes inside temp by 0.033 degrees * the difference between the outside temp and the inside temp / minute
        b Open apertures calculate in a similar way but with much higher rates of change, 0.4 for doors and 0.2 for windows
    
    It then determines whether its necessary to turn the HVAC on or off.

    This job runs every minute by default and can be called to generate historical data by passing in a date time that isnt current
    This function will be called from the normal event loop if the time is not between 23:59 and 00:00, to avoid issues with event generation
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

    #get the current temperature outside and the thermostat
    outdoor = getTemperatureAtTime(now)

    #calculate if temperature is higher or lower than target
    higher = thermostat.current_temp > thermostat.target_temp

    #if the hvac is already on, add or subtract one based off higher
    if hvac.status:
        if higher:
            current_temp -= 1
        else:
            current_temp += 1

    #now calculate the updated temp from outside temp difference and apertures using the current temp after hvac changes
    updated_temp = temperature_calculation(current_temp, outdoor)

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

def old_event_loop():
    now = datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=2)
    #get the current time
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
    
def door_job():
    now = datetime.now() 
    doors = Aperture.objects.filter(type=1)

    for door in doors:
        weekday = now.weekday() < 5
        day_key = "wd" if weekday else "we"
        ranges = door_dict[door.id][day_key]
        for range in ranges:
            if range["start"] < now.time() < range["end"]:
                rand = random.random()
                if rand < range["prob"]:
                    door.status = True
                    door.save()
                    print("door opened")
                    t.sleep(30)
                    door.status = False
                    door.save()
                    print("door closed")
                    break


door_dict = {
    14:{
        "wd": [{"start": time(16, 10), "end": time(19, 0), "prob": 0.05}],
        "we": [{"start": time(8, 0), "end": time(19, 0), "prob": 0.02424}]
    },
    15:{
        "wd": [{"start": time(7, 15) , "end": time(7,45), "prob": 0.13}, {"start": time(15, 50) , "end": time(16, 0), "prob": 0.2}],
        "we": [{"start": time(8, 0), "end": time(19, 0), "prob": 0.01212}]
    },
    16:{
        "wd": [{"start": time(7, 15) , "end": time(7,45), "prob": 0.13}, {"start": time(17, 15) , "end": time(17, 45), "prob": 0.1}],
        "we": [{"start": time(8, 0), "end": time(19, 0), "prob": 0.01212}]
    },
}

