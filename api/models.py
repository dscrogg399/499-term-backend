from django.db import models

# Create your models here.

#These are test models for the API and just serve as examples
# class User(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     username = models.CharField(max_length=50)
#     password = models.CharField(max_length=50)
#     email = models.CharField(max_length=50)

#     @classmethod
#     def create(cls, username, password, email):
#  
#        user = cls(username=username, password=password, email=email)
#         return user

#     def __str__(self):
#         return self.username
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
    watts_used = models.FloatField()
    water_used = models.FloatField()
    cost = models.FloatField()
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
        )
    log = models.ForeignKey(
        Event_Log,
        on_delete=models.PROTECT,
        )
    on_at = models.DateTimeField()
    off_at = models.DateTimeField()
    watts_used = models.FloatField()
    water_used = models.FloatField()
    cost = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField()

    @classmethod
    def create(cls, appliance_id, on_at, off_at, watts_used, water_used, cost, is_active):
        event = cls(appliance_id = appliance_id, on_at = on_at, off_at = off_at, watts_used = watts_used, 
                    water_used = water_used, cost = cost, is_active = is_active)
        return event
    
    def __str__(self):
        return self.id