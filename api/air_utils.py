import random

from api.weather import getHumidity



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
        hum_delta = 0.01
    #otherwise, we vary slights for busy vs not busy
    else:
        if busy:
            hum_target = 0.55
            hum_delta = 0.1
        else:
            hum_target = 0.45
            hum_delta = 0.05
    #get the new varied value, rounded to 2 decimal places
    new_hum = calc_new_value(curr_hum * 100, hum_target * 100, hum_delta * 100)
    return round(new_hum/100, 2)