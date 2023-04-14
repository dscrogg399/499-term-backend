from datetime import timedelta
from django.db import models

# Create your models here.

class Appliance_Type(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=50)
    wattage = models.FloatField() 
    gallons = models.FloatField() 
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField()

    @classmethod
    def create(cls, title, wattage, gallons, is_active):
        appliance_type = cls(title = title, wattage = wattage, gallons = gallons, is_active = is_active)
        return appliance_type
    
    def __str__(self):
        return self.id

class Appliance(models.Model):
    id = models.BigAutoField(primary_key=True)
    appliance_type = models.ForeignKey(
        Appliance_Type,
        on_delete=models.PROTECT,
        )
    title = models.CharField(max_length=50)
    status = models.BooleanField() #1 on, 0 off
    x = models.FloatField() 
    y = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField()

    @classmethod
    def create(cls, title, status, x, y, is_active):
        appliance = cls(title = title, status = status, x = x, y = y, is_active = is_active)
        return appliance

    def toggle_appliance(self, now):
        if self.status:
            #end event
            #get the last event connected to this appliance and end it
            try:
                event = Event.objects.filter(appliance_id=self.id, off_at=None, is_active=True).latest('created_at')
                event.end_event(now, self.appliance_type_id)
            except Event.DoesNotExist:
                pass
        else:
            #generate event
            event_log = Event_Log.objects.filter(is_active=True).latest('created_at')
            new_event = Event.start_event(self.id, event_log.id, now, True)
            new_event.save()
        self.status = not self.status
        self.save()

    
    def __str__(self):
        return self.id

class Aperture(models.Model):
    d_w = (
        (1, "door"), (2, "window")
    )
    id = models.BigAutoField(primary_key=True)
    type = models.IntegerField(choices=d_w)
    title = models.CharField(max_length=50, null=True)
    status = models.BooleanField() #1 on, 0 off
    x = models.FloatField() 
    y = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField()

    @classmethod
    def create(cls, status, type, title, x, y, is_active):
        aperture = cls(status = status, type = type, title = title, x = x, y = y, is_active = is_active)
        return aperture
    
    def __str__(self):
        return self.id

class Thermostat(models.Model):
    id = models.BigAutoField(primary_key=True)
    current_temp = models.FloatField()
    target_temp = models.FloatField()
    min_temp = models.FloatField()
    max_temp = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField()

    @classmethod
    def create(cls, current_temp, target_temp, min_temp, max_temp, is_active):
        thermostat = cls(current_temp, target_temp, min_temp, max_temp, is_active)
        return thermostat
    
    def __str__(self):
        return self.id


class Air_Quality(models.Model):
    id = models.BigAutoField(primary_key=True)
    co = models.IntegerField()
    co2 = models.IntegerField()
    humidity = models.FloatField()
    pm = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField()

    @classmethod
    def create(cls, co, co2, humidity, pm, is_active):
        air_quality = cls(co = co, co2 = co2, humidity = humidity, pm = pm, is_active = is_active)
        return air_quality
    
    def __str__(self):
        return self.id
    
class Budget_Target(models.Model):
    id = models.BigAutoField(primary_key=True)
    max_cost = models.FloatField()
    max_water = models.FloatField()
    max_energy = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField()

    @classmethod
    def create(cls, max_cost, max_water, max_energy, is_active):
        budget = cls(max_cost = max_cost, max_water = max_water, max_energy = max_energy, is_active = is_active)
        return budget
    
    def __str__(self):
        return self.id

class Event_Log(models.Model):
    id = models.BigAutoField(primary_key=True)
    watts_used = models.FloatField(null=True)
    water_used = models.FloatField(null=True)
    cost = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField()

    @classmethod
    def create(cls, is_active):
        event_log = cls(watts_used = 0, water_used = 0, cost = 0, is_active = is_active)
        return event_log
    
    def __str__(self):
        return self.id

class Event(models.Model):
    id = models.BigAutoField(primary_key=True)
    appliance = models.ForeignKey(
        Appliance,
        on_delete=models.PROTECT,
        null=True)
    log = models.ForeignKey(
        Event_Log,
        on_delete=models.PROTECT,
        null=True)
    on_at = models.DateTimeField()
    off_at = models.DateTimeField(null=True)
    watts_used = models.FloatField(null=True)
    water_used = models.FloatField(null=True)
    cost = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(null=True)

    @classmethod
    def create(cls, appliance_id, on_at, off_at, watts_used, water_used, cost, log_id, is_active):
        event = cls(appliance_id = appliance_id, on_at = on_at, off_at = off_at, watts_used = watts_used, 
                    water_used = water_used, cost = cost, log_id = log_id, is_active = is_active)
        return event
    
    # function for creating events without energy, water and cost parameters
    @classmethod
    def create_lite(cls, appliance_id, on_at, off_at, is_active):  
        event_lite = cls(appliance_id = appliance_id, on_at = on_at, off_at = off_at, is_active = is_active)
        return event_lite

    @classmethod
    def start_event(cls, appliance_id, log_id, on_at, is_active):  
        event_lite = cls(appliance_id = appliance_id, log_id = log_id, on_at = on_at, is_active = is_active)
        return event_lite
    
    def end_event(self, off_at, appliance_type_id):
        self.off_at = off_at
        # #calculate difference between on_at and off_at
        diff = (off_at - self.on_at).total_seconds() / 60

        # #get appliance type
        appliance_type = Appliance_Type.objects.get(id = appliance_type_id)
        # #calculate energy and water used
        self.watts_used = appliance_type.wattage * diff
        self.water_used = appliance_type.gallons * diff
        # #calculate cost
        self.cost = (self.watts_used * 0.00012) + (self.water_used * 0.003368983957219)

        #if device uses hot water, calculate hot water used
        if appliance_type_id in [11,12,13,15]:
            water_heater = Appliance_Type.objects.get(id = 8)
            hot_water = appliance_type.gallons * diff
            #if its a shower or bath, 65% hot water
            if appliance_type_id in [11,12]:
                hot_water *= 0.65
            #if its the clothes washer, 85% hot water
            elif appliance_type_id == 13:
                hot_water *= 0.85
            #else its the dishwasher, 100% hot water

            #post hoc calculation for water heater
            wh_on_duration = hot_water * 4
 
            #get the new on time 
            new_on_at= off_at - timedelta(minutes = wh_on_duration)

            #calculate the wattage and cost
            wh_watts = water_heater.wattage * wh_on_duration
            wh_cost = (wh_watts * 0.00012)

            #water heater is appliance id 37
            #create event
            wh_event = Event.create(37, new_on_at, off_at, wh_watts, 0, wh_cost, self.log_id, True)
            wh_event.save()


        # #update log
        self.save()
        return
    
    def __str__(self):
        return self.id