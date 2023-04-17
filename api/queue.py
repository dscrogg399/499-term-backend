from datetime import timedelta

from api.models import Appliance, Appliance_Type, Event
from .utils import get_minutes_difference, time_in_range

class EventQueue:
    _instance = None

    def __init__(self):
        raise RuntimeError("Call instance() instead")

    def enqueue(self, item):
        #if item.id already in queue, reject
        # if item["id"] in self.lookup:
        #     print("enqueue failed")
        #     return
        #when an event comes in, add the index of the event to the lookup table with a key of the event's appliance id

        #use lookup table to check if the event has other conflicting events in the queue
        # print(self.lookup[item["id"]])
        if len(self.lookup[item["id"]]) > 0: 
            for i in self.lookup[item["id"]]:
                # print(self.queue)
                event_in_queue = self.queue[i]
                # print(event_in_queue)
                #start_time + duration = end_time
                #if the start time of the event is between the start and end time of the event in the queue
                end_time = event_in_queue["start_time"] + timedelta(minutes=event_in_queue["duration"])
                # print(end_time)
                if time_in_range(item["start_time"], event_in_queue["start_time"], end_time):
                    return False
                
                #if the time is too close to the end time, reject
                #take the difference in minutes between item["start_time"] and item["end_time"]
                #if the difference is less than 5 minutes, reject
                # print(get_minutes_difference(item["start_time"], end_time))
                new_end = item["start_time"].replace(hour=item["end_time"].hour, minute=item["end_time"].minute)
                remaining = get_minutes_difference(item["start_time"],new_end )
                if (remaining < item["delta"]):
                    return False
                # if get_minutes_difference(item["start_time"], end_time) < 5:

            self.lookup[item["id"]].append(self.size)
            # print(self.lookup)
        else:
            self.lookup[item["id"]].append(self.size)
        self.queue.append(item)
        self.size += 1
        return True

    def dequeue(self):
        #remove the first item in the queue and return it
        if self.size > 0:
            #remove the index of the event from the lookup table
            last_item = self.queue[self.size - 1]
            self.lookup[last_item["id"]].pop()
            self.size -= 1
            return self.queue.pop()
        else:
            return None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance.queue = []
            cls._instance.lookup = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [], 10: [], 11: [], 12: [], 13: [], 14: [], 15: [], 16: [], 17: [], 18: [], 19: [], 20: [], 21: [], 22: [], 23: [], 24: [], 25: [], 26: [], 27: [], 28: [], 29: [], 30: [], 31: [], 32: [], 33: [], 34: [], 35: [], 36: [], 37: []}
            cls._instance.size = 0
        return cls._instance

    def historic_execute(self):
        print("executing historic queue")
        print("queue size: ", self.size)
        max_queue = self.size
        while self.size > 0:
            print(str(self.size) + "/" + str(max_queue) + " remaining")
            #stubbed for historic
            item = self.dequeue()

            app_id = item["id"]
            wattage = item["wattage"]
            gallons = item["gallons"]
            start_time = item["start_time"]
            duration = item["duration"]
            end_time = start_time + timedelta(minutes=duration)

            app_type = item['app_type']

            watts_used = wattage * duration
            water_used = gallons * duration

            cost = (watts_used * 0.00012) + (water_used * 0.003368983957219)

            new_event = Event.create(app_id, start_time, end_time, watts_used, water_used, cost, True)

            #if device uses hot water, calculate hot water used
            if app_type in [11,12,13,15]:
                water_heater = Appliance_Type.objects.get(id = 8)
                hot_water = gallons * duration
                #if its a shower or bath, 65% hot water
                if app_type in [11,12]:
                    hot_water *= 0.65
                #if its the clothes washer, 85% hot water
                elif app_type == 13:
                    hot_water *= 0.85
                #else its the dishwasher, 100% hot water

                #post hoc calculation for water heater
                wh_on_duration = hot_water * 4
    
                #get the new on time 
                new_on_at = end_time - timedelta(minutes = wh_on_duration)

                #calculate the wattage and cost
                wh_watts = water_heater.wattage * wh_on_duration
                wh_cost = (wh_watts * 0.00012)

                #water heater is appliance id 37
                #create event
                wh_event = Event.create(37, new_on_at, end_time, wh_watts, 0, wh_cost, True)
                wh_event.save()
            #clothes washer carve out
            if app_id == 35:
                #get the dryer appliance type, dryer appliance id is 36
                dryer = Appliance_Type.objects.get(id = 14)
                #calculate the wattage and cost
                dryer_watts = dryer.wattage * duration
                dryer_cost = (dryer_watts * 0.00012)

                #create event
                dryer_event = Event.create(36, start_time, end_time, dryer_watts, 0, dryer_cost, True)
                dryer_event.save()

            new_event.save()

    def execute(self, now):
        print("executing queue")
        print("queue size: ", self.size)

        queue_events = self.queue
        length = len(queue_events)


        for i in range(length):
            #if the event duration has been exceeded by now, toggle the appliance
            if queue_events[i]["start_time"] + timedelta(minutes=queue_events[i]["duration"]) < now:
                #toggle the appliance
                appliance = Appliance.objects.get(id=queue_events[i]["id"])
                appliance.toggle_appliance(now)
                #carveout for dryer
                if appliance.id == 35:
                    # get the dryer appliance
                    dryer = Appliance.objects.get(id=36)
                    #turn the dryer on
                    dryer.toggle_appliance(now)
                    self.enqueue({"id": 36, "start_time": now + timedelta(minutes=5), "duration": 45, "delta": 0})
                #remove the event from the queue
                self.queue.pop(i)
                self.size -= 1
                print("executed event")
                self.cache_cleanup()


        # for event in self.queue:
        #     #if the event duration has been exceeded by now, toggle the appliance
        #     if event["start_time"] + timedelta(minutes=event["duration"]) < now:
        #         #toggle the appliance
        #         appliance = Appliance.objects.get(id=event["id"])
        #         appliance.toggle_appliance(now)
        #         #remove the event from the queue
        #         self.queue.pop(event)
        #         self.cache_cleanup(event)
        #         self.size -= 1
        #         print("executed event")

    def cache_cleanup(self):
        #rebuild the cache table after an event has been removed
        #clear the cache
        for key in self.lookup:
            self.lookup[key] = []
        for i in range(self.size):
            self.lookup[self.queue[i]["id"]].append(i)
            

    



    def __str__(self):
        return self.queue

    def print_queue(self):
        for item in self.queue:
            print(item)
"""

    Queue object for storing events
    {appliance_id, wattage, gallons, start_time, duration,}
"""