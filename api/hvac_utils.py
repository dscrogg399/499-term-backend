import datetime
import math

from api.models import Aperture, Appliance, Appliance_Type, Thermostat, Event
from api.utils import get_minutes_difference
from api.weather import getWeatherHistory

#this function mimics the hvac job but is slightly simplified, and optimized for historic data. It generates events
#rather than toggle appliances and does not call for weather every single time, rather it gets all the weather data we need
#for the time period
#time is the beginning time of the simulation
#now is the end time of the simulation
def historic_hvac_util(time, now):
    #get the weather upfront to avoid multiple calls
    weather = getWeatherHistory(time, now)

    #difference in minutes between now and start
    diff = math.floor(get_minutes_difference(time, now))
    print(diff)

    #get the thermostat and HVAC (thermostat id = 1, HVAC id = 34)
    thermostat = Thermostat.objects.get(id=1)
    hvac = Appliance.objects.get(id=34)
    hvac_appliance_type = Appliance_Type.objects.get(id=hvac.appliance_type_id)

    #turn off hvac if it was on
    if hvac.status:
        hvac.toggle_appliance(time)
        hvac.save()

    #target temp
    target_temp = thermostat.target_temp

    #min and max temp range
    min = target_temp - 2
    max = target_temp + 2

    #store current temp to manipulate
    current_temp = thermostat.current_temp

    #last time the hvac was toggled
    last_on = None

    #hvac status
    hvac_status = False

    for index in range(diff):
        print(str(index) + "/" + str(diff))

        higher = current_temp > thermostat.target_temp

        if hvac_status:
            if higher:
                current_temp -= 1
            else:
                current_temp += 1

        #dictionary keys and index
        index_date = time.date()
        index_hour = time.hour
        #calulate the update temperature for that time
        updated_temp = historic_temperature_calculation(current_temp,  weather[index_date][index_hour])
        
        #if hvac is off and temp in range, continue
        if not hvac_status and updated_temp >= min and updated_temp <= max:
            time += datetime.timedelta(minutes=1)
            #update the thermostat
            current_temp = updated_temp
            continue
        #if the hvac is off and the updated temp is outside the min and max range
        elif not hvac_status and updated_temp < min or updated_temp > max:
            #toggle the hvac on
            print("turning on")
            hvac_status = True
            last_on = time
            print(last_on)
        #else hvac is already on
        else:
            #if the current temp was higher and is now lower than the target temp
            if higher and updated_temp < target_temp:
                #generate hvac event
                timediff = get_minutes_difference(last_on, time)

                watts_used = hvac_appliance_type.wattage * timediff
                water_used = hvac_appliance_type.gallons * timediff

                cost = (watts_used * 0.00012) + (water_used * 0.003368983957219)

                new_event = Event.create(hvac.id, last_on, time, watts_used, water_used, cost, True)
                new_event.save()

                #toggle the hvac off
                hvac_status = False
            #if the current temp was lower and is now higher than the target temp
            elif not higher and updated_temp > target_temp:
                #generate hvac event
                timediff = get_minutes_difference(last_on, time)

                watts_used = hvac_appliance_type.wattage * timediff
                water_used = hvac_appliance_type.gallons * timediff

                cost = (watts_used * 0.00012) + (water_used * 0.003368983957219)

                new_event = Event.create(hvac.id, last_on, time, watts_used, water_used, cost, True)
                new_event.save()

                #toggle the hvac off
                hvac_status = False

        #update the thermostat
        current_temp = updated_temp
        #iterate 1 minute
        time += datetime.timedelta(minutes=1)
    print("complete!")

    #save thermostat
    thermostat.current_temp = current_temp
    thermostat.save()

    
def temperature_calculation(current_temp, outdoor):

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

#this function is used for historic data and ignores apertures to avoid having to query them, its a simplification but its necessary
def historic_temperature_calculation(current_temp, outdoor):
        #deltas are calculated per 10 degrees of difference between the outside and the inside
    diff = current_temp - outdoor
    temp_scale = diff/ 10

    temp_delta = 0.033 * temp_scale

    #calculate and set the new temperature
    return current_temp - temp_delta