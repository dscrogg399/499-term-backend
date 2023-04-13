from django.conf import settings
import json
#import requests
import re
import random
from datetime import datetime, timedelta
from .models import Appliance
import simpy

#import googleapiclient.discovery
#import googleapiclient.errors
#from main.models import Media
    
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
         

def 
    
    
    
           
           
           
           
       
   
   
   
   
   
   
   
   
   
   
   
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








        
        
        
    
