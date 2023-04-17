import datetime
import random
from django.db.models import  Max, Q
from api.models import Appliance, Appliance_Type, Event
from api.queue import EventQueue

from .utils import time_in_range, get_minutes_difference
from datetime import datetime, timedelta, time


def random_time(begin, end):
    return begin + timedelta(minutes=random.uniform(0,(end-begin).seconds//60))
   
def random_duration(begin, end):
    return timedelta(minutes = random.uniform(begin, end))

def should_event_occur(probability, start, end, now):
    if not time_in_range(now, start, end):
        return False
    total_minutes = int(get_minutes_difference(start, end))
    adjusted_probability = 1 - (1 - probability) ** (1 / total_minutes)
    
    return random.random() < adjusted_probability

def should_event_occur_loose(start, end, max_num, delta):
    adj_max = max_num + random.randint(-delta, delta)
    diff = get_minutes_difference(start, end)
    prob = adj_max/diff
    return random.random() < prob

def event_loop():
    print("running event loop")
    queue = EventQueue.instance()

    appliance_types_query = Appliance_Type.objects.filter(is_active=True)

    #appliance type lookup
    app_types = {}
    for app_type in appliance_types_query:
        appliance_type_dict = {
            'wattage': app_type.wattage,
            'gallons': app_type.gallons,
        }
        app_types[app_type.id] = appliance_type_dict

    excluded_ids = [26, 27, 34, 36, 37]
    query = Q(is_active=True) & ~Q(id__in=excluded_ids)
    appliances = Appliance.objects.filter(query).order_by('id')

    now = datetime.now()
    total_appliances = appliances.count()
    current = 0
    weekday = now.weekday() < 5
    day_key = "wd" if weekday else "we"
    for appliance in appliances:
        # print("Appliance " + str(current) + " of " + str(total_appliances))
        ranges = prob_dict[appliance.id][day_key]
        for r in ranges:
            if time_in_range(now.time(), r["start"], r["end"]):
                if random.random() < r["prob"]:
                    queue_event = {
                        "id": appliance.id,
                        "duration": r["dur"] + random.randint(-r["delta"], r["delta"]),
                        "wattage": app_types[appliance.appliance_type_id]["wattage"],
                        "gallons": app_types[appliance.appliance_type_id]["gallons"],
                        "start_time": now,
                        "end_time": r["end"],
                        "delta": r["delta"],
                        "app_type": appliance.appliance_type_id,
                    }
                    queued = queue.enqueue(queue_event)
                    
                    if queued:
                        appliance.toggle_appliance(now)
                    break
        current += 1
    queue.execute(now)
    print(queue.print_queue())
    print(queue.size)


def startup_data_generator(start): 
    print("running startup data generator")
    queue = EventQueue.instance()



    appliance_types_query = Appliance_Type.objects.filter(is_active=True)

    #appliance type lookup
    app_types = {}
    for app_type in appliance_types_query:
        appliance_type_dict = {
            'wattage': app_type.wattage,
            'gallons': app_type.gallons,
        }
        app_types[app_type.id] = appliance_type_dict

    excluded_ids = [26, 27, 34, 36, 37]
    query = Q(is_active=True) & ~Q(id__in=excluded_ids)
    appliances = Appliance.objects.filter(query).order_by('id')

    end = datetime.now()

    total_appliances = appliances.count()
    current = 0
    for appliance in appliances:
        print("Historical Event Generation: " + str(current) + " of " + str(total_appliances))
        now = start
        while now < end:
            weekday = now.weekday() < 5

            day_key = "wd" if weekday else "we"
            ranges = prob_dict[appliance.id][day_key]

            for r in ranges:
                if time_in_range(now.time(), r["start"], r["end"]):
                    if random.random() < r["prob"]:
                        queue_event = {
                            "id": appliance.id,
                            "duration": r["dur"] + random.randint(-r["delta"], r["delta"]),
                            "wattage": app_types[appliance.appliance_type_id]["wattage"],
                            "gallons": app_types[appliance.appliance_type_id]["gallons"],
                            "start_time": now,
                            "end_time": r["end"],
                            "delta": r["delta"],
                            "app_type": appliance.appliance_type_id,
                        }
                        queued = queue.enqueue(queue_event)
                        break
            now += timedelta(minutes=1)
        current += 1
        queue.historic_execute()
    print("historic data generation complete!")


prob_dict = {
#master bedroom lamp 1
1: {
    "wd": [{"start": time(20, 30), "end": time(22, 30), "dur": 120, "delta": 10, "prob": 1,}],
    "we": [{"start": time(20, 30), "end": time(22, 30), "dur": 120, "delta": 10, "prob": 1,}]
},
#master bedroom lamp 2
2: {
    "wd": [{"start": time(20, 30), "end": time(22, 30), "dur": 120, "delta": 10, "prob": 1,}],
    "we": [{"start": time(20, 30), "end": time(22, 30), "dur": 120, "delta": 10, "prob": 1,}] 
},
#master bedroom overhead
3: {
    "wd": [{"start": time(5, 0), "end": time(7, 25), "dur": 145, "delta": 2, "prob": 1,}, {"start": time(17, 30), "end": time(20, 30), "dur": 180, "delta": 10, "prob": 1,}],
    "we": [{"start": time(6, 0), "end": time(11, 0), "dur": 300, "delta": 30, "prob": 1,}, {"start": time(16, 0), "end": time(20, 30), "dur": 270, "delta": 10, "prob": 1,}]
},
#master bathroom overhead
4: {
    "wd": [{"start": time(5, 10), "end": time(7, 25), "dur": 135, "delta": 2, "prob": 1,}, {"start": time(18, 00), "end": time(20, 30), "dur": 6, "delta": 4, "prob": 0.038,}],
    "we": [{"start": time(7, 30), "end": time(8, 30), "dur": 60, "delta": 10, "prob": 1,}, {"start": time(8, 30), "end": time(20, 30), "dur": 6, "delta": 4, "prob": 0.0208,}],
},
#bathroom overhead
5: {
    "wd": [{"start": time(6, 10), "end": time(7, 25), "dur": 75, "delta": 2, "prob": 1,}, {"start": time(16, 00), "end": time(20, 30), "dur": 6, "delta": 4, "prob": 0.02,}],
    "we": [{"start": time(8, 30), "end": time(9, 30), "dur": 60, "delta": 10, "prob": 1,}, {"start": time(9, 30), "end": time(20, 30), "dur": 6, "delta": 4, "prob": 0.0227,}],
},
#bedroom 1 lamp 1
6: {
    "wd": [{"start": time(19, 30), "end": time(20, 30), "dur": 60, "delta": 10, "prob": 1,}],
    "we": [{"start": time(19, 30), "end": time(20, 30), "dur": 60, "delta": 10, "prob": 1,}],
}, 
#bedroom 1 lamp 2
7: {
    "wd": [{"start": time(19, 30), "end": time(20, 30), "dur": 60, "delta": 10, "prob": 1,}],
    "we": [{"start": time(19, 30), "end": time(20, 30), "dur": 60, "delta": 10, "prob": 1,}],
},
#bedroom 1 overhead
8: {
    "wd": [{"start": time(6, 0), "end": time(7, 25), "dur": 75, "delta": 2, "prob": 1,}, {"start": time(16, 00), "end": time(19, 30), "dur": 180, "delta": 10, "prob": 1,}],
    "we": [{"start": time(7, 0), "end": time(11, 0), "dur": 240, "delta": 30, "prob": 1,}, {"start": time(16, 00), "end": time(19, 30), "dur": 180, "delta": 10, "prob": 1,}],
},
#bedroom 2 lamp 1
9: {
    "wd": [{"start": time(19, 30), "end": time(20, 30), "dur": 60, "delta": 10, "prob": 1,}],
    "we": [{"start": time(19, 30), "end": time(20, 30), "dur": 60, "delta": 10, "prob": 1,}],
},
#bedroom 2 lamp 2
10: {
    "wd": [{"start": time(19, 30), "end": time(20, 30), "dur": 60, "delta": 10, "prob": 1,}],
    "we": [{"start": time(19, 30), "end": time(20, 30), "dur": 60, "delta": 10, "prob": 1,}],
},
#bedroom 2 overhead
11: {
    "wd": [{"start": time(6, 0), "end": time(7, 25), "dur": 75, "delta": 2, "prob": 1,}, {"start": time(16, 00), "end": time(19, 30), "dur": 180, "delta": 10, "prob": 1,}],
    "we": [{"start": time(7, 0), "end": time(11, 0), "dur": 240, "delta": 30, "prob": 1,}, {"start": time(16, 00), "end": time(19, 30), "dur": 180, "delta": 10, "prob": 1,}],
},
#kitchen overhead
12: {
    "wd": [{"start": time(6, 0), "end": time(7, 25), "dur": 75, "delta": 2, "prob": 1,}, {"start": time(16, 00), "end": time(20, 30), "dur": 270, "delta": 10, "prob": 1,}],
    "we": [{"start": time(7, 0), "end": time(11, 0), "dur": 240, "delta": 30, "prob": 1,}, {"start": time(16, 00), "end": time(20, 30), "dur": 270, "delta": 10, "prob": 1,}],
},
#living room lamp 1
13: {
    "wd": [{"start": time(19, 30), "end": time(20, 30), "dur": 60, "delta": 10, "prob": 1,}],
    "we": [{"start": time(19, 30), "end": time(20, 30), "dur": 60, "delta": 10, "prob": 1,}],
},
#living room lamp 2
14: {
    "wd": [{"start": time(19, 30), "end": time(20, 30), "dur": 60, "delta": 10, "prob": 1,}],
    "we": [{"start": time(19, 30), "end": time(20, 30), "dur": 60, "delta": 10, "prob": 1,}],
},
#living room overhead
15: {
    "wd": [{"start": time(6, 0), "end": time(7, 25), "dur": 75, "delta": 2, "prob": 1,}, {"start": time(16, 00), "end": time(19, 30), "dur": 180, "delta": 10, "prob": 1,}],
    "we": [{"start": time(7, 0), "end": time(11, 0), "dur": 240, "delta": 30, "prob": 1,}, {"start": time(16, 00), "end": time(19, 30), "dur": 180, "delta": 10, "prob": 1,}],
},
#mbed tv
16: {
    "wd": [{"start": time(5, 30), "end": time(6, 30), "dur": 60, "delta": 10, "prob": 1,}, {"start": time(21, 30), "end": time(22, 30), "dur": 60, "delta": 10, "prob": 1,}],
    "we": [{"start": time(7, 30), "end": time(9, 30), "dur": 120, "delta": 20, "prob": 1,}, {"start": time(21, 30), "end": time(23, 30), "dur": 120, "delta": 20, "prob": 1,}],
},
#lr tv
17: {
    "wd": [{"start": time(6, 0), "end": time(7, 0), "dur": 60, "delta": 10, "prob": 1,}, {"start": time(16, 00), "end": time(19, 00), "dur": 180, "delta": 10, "prob": 1,}],
    "we": [{"start": time(7, 0), "end": time(10, 30), "dur": 240, "delta": 20, "prob": 1,}, {"start": time(16, 00), "end": time(19, 30), "dur": 240, "delta": 10, "prob": 1,}],
},
#master bathroom fan
18: {
    "wd": [{"start": time(5, 10), "end": time(6, 0), "dur": 50, "delta": 6, "prob": 1,}, ],
    "we": [{"start": time(6, 10), "end": time(7, 0), "dur": 50, "delta": 6, "prob": 1,}, ],
},
#bathroom fan
19: {
    "wd": [{"start": time(5, 10), "end": time(6, 0), "dur": 50, "delta": 6, "prob": 1,}, ],
    "we": [{"start": time(6, 10), "end": time(7, 0), "dur": 50, "delta": 6, "prob": 1,}, ],
},
#master bathroom shower
25: {
    "wd": [{"start": time(5, 10), "end": time(5, 25), "dur": 15, "delta": 3, "prob": 1,}, {"start": time(5, 30), "end": time(5, 45), "dur": 15, "delta": 3, "prob": 1,},],
    "we": [{"start": time(6, 10), "end": time(6, 25), "dur": 15, "delta": 3, "prob": 1,}, {"start": time(6, 30), "end": time(6, 45), "dur": 15, "delta": 3, "prob": 1,}, {"start": time(16, 0), "end": time(16, 1), "dur": 15, "delta": 3, "prob": 0.5,}, {"start": time(16, 30), "end": time(16, 31), "dur": 15, "delta": 3, "prob": 0.5,}],
},
#bathroom bath
28: {
    "wd": [{"start": time(6, 10), "end": time(6, 25), "dur": 15, "delta": 3, "prob": 1,}, {"start": time(6, 30), "end": time(6, 45), "dur": 15, "delta": 3, "prob": 1,},],
    "we": [{"start": time(7, 10), "end": time(7, 25), "dur": 15, "delta": 3, "prob": 1,}, {"start": time(7, 30), "end": time(7, 45), "dur": 15, "delta": 3, "prob": 1,}, {"start": time(17, 0), "end": time(17, 1), "dur": 15, "delta": 3, "prob": 0.5,}, {"start": time(17, 30), "end": time(17, 31), "dur": 15, "delta": 3, "prob": 0.5,}],
},
#refrigerator
29: {
    "wd": [{"start": time(0, 0), "end": time(23, 59), "dur": 1439, "delta": 0, "prob": 1,},],
    "we": [{"start": time(0, 0), "end": time(23, 59), "dur": 1439, "delta": 0, "prob": 1,},],
},
#stove
30: {
    "wd": [{"start": time(18, 30), "end": time(18, 45), "dur": 15, "delta": 2, "prob": 1,}],
    "we": [{"start": time(7, 10), "end": time(7, 35), "dur": 15, "delta": 2, "prob": 1,}, {"start": time(19, 0), "end": time(19, 15), "dur": 15, "delta": 2, "prob": 1,}],
},
#oven
31: {
    "wd": [{"start": time(18, 30), "end": time(19, 15), "dur": 45, "delta": 10, "prob": 1,}],
    "we": [{"start": time(18, 30), "end": time(19, 30), "dur": 65, "delta": 15, "prob": 1,},],
},
#microwave
32: {
    "wd": [{"start": time(6, 0), "end": time(7, 0), "dur": 2, "delta": 1, "prob": 0.167,}, {"start": time(16, 0), "end": time(20, 0), "dur": 2, "delta": 1, "prob": 0.0417,},],
    "we": [{"start": time(7, 0), "end": time(10, 0), "dur": 2, "delta": 1, "prob": 0.0417,}, {"start": time(12, 0), "end": time(20, 0), "dur": 2, "delta": 1, "prob": 0.0156,},],
},
#dishwasher
33: {
    "wd": [{"start": time(19, 30), "end": time(19, 31), "dur": 45, "delta": 0, "prob": 0.57,},],
    "we": [{"start": time(19, 30), "end": time(19, 31), "dur": 45, "delta": 0, "prob": 0.57,},],
},
#washer
35: {
    "wd": [{"start": time(18, 0), "end": time(18, 1), "dur": 30, "delta": 0, "prob": 0.57,},],
    "we": [{"start": time(18, 0 ), "end": time(18, 1), "dur": 30, "delta": 0, "prob": 0.57,},],
},

}


def time_in_range(now, start, end):
    return (start <= now) and (now <= end)

