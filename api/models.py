from django.db import models

# Create your models here.
class Appliance_Type(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=50)
    wattage = models.IntegerField()
    gallons = models.IntegerField()
    is_active = models.BooleanField()

    @classmethod
    def create(cls, title, wattage, gallons, is_active):
        appliance = cls(title = title, wattage = wattage, gallons = gallons, is_active = is_active)
        return appliance
    
    def __str__(self):
        return self.id

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