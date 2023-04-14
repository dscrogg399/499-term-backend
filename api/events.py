import random
import datetime

# showers & fans on(2), lights on/off3 (7 overhead, 4 lamps), tv usage (2), door open(1 front door, 1 back door, 1 door leading to garage), washer on, dryer on,
# faucet on(3 bed, 1 kitchen, 1 outside), stove, oven, microwave, dishwasher, window open(8 windows)
#
# HVAC Operation - +/- 1 deg F per minute of operation
#  HVAC will maintain the set temp within 2 degrees (i.e. if the inside temp goes beyond 2 degrees
# of the set temp, then it will start operation to bring the temp back to the set temp).
#  Interior Temp Change
# o House Closed – For every 10 deg F difference in external temp, interior temp will +/- 2
# deg F per hour
# o Open Door – For every 10 deg F difference in external temp, interior temp will +/- 2 deg
# F per 5 min door is open
# o Open Window - For every 10 deg F difference in external temp, interior temp will +/- 1
# deg F per 5 min window is open
#  Door Opening
# o Exterior door is open 30 seconds each time a person enters or leaves the house
# o M – F : 16 exit/enter events per day
# o S – S : 32 exit/enter events per day
#  Electricity Cost - $0.12 per kWh ( 1w = 1/1000 kw)
#  Water Cost –
# o $2.52 per 100 Cubic Feet of water
# o 1 Cubic Feet of water is 7.48 Gallons
# o 100 Cubic Feet is 748 Gallons
# o So 748 Gallons costs $2.52
#  All Light Bulbs are 60w
#  Bath exhaust fan – 30w
#  HVAC – 3500w
#  Refrigerator – 150w
#  Microwave
# o 1100w
# o M – F : 20 min/day
# o S – S : 30 min/day
#  Hot Water Heater
# o 4500w
# o 4 minutes to heat 1 gallon of water
#  Stove
# o 3500 watts
# o M – F : 15 min/day
# o S – S : 30 min/day
#  Oven
# o 4000 watts
# o M – F : 45 min/day
# o S – S : 60 min/day
#  TV
# o Living Room TV
#  636 watts
#  M – F : 4 hrs/day
#  S – S : 8 hrs/day
# o Bedroom TV
#  100 watts
#  M – F : 2 hrs/day
#  S – S : 4 hrs/day
#  Baths
# o M – F : 2 showers and 2 baths per day
# o S – S : 3 showers and 3 baths per day
# o Shower – 25 gallons of water used (65% hot water, 35% cold water)
# o Bath – 30 gallons of water used (65% hot water, 35% cold water)
#  Dishwasher
# o 1800 watts
# o 6 gallons of hot water per load
# o Runs 45 min per load
# o 4 loads of dishes per week
#  Clothes Washer
# o 500 watts
# o 20 gallons of water (85% hot water, 15% cold water) per load
# o Runs 30 min per load
# o 4 loads of clothes per week
#  Clothes Dryer
# o 3000 watts
# o Runs 30 min per load
# o 4 loads of clothes per week
#  Adults wake at 5AM, go to bed at 10:30PM
#  Kids wake at 6AM, go to bed at 8:30PM
#  Adults leave for work at 7:30AM, return home at 5:30PM
#  Kids leave for school at 7:30AM, return home at 4PM

def eventMaker():
    appliances  = ["Master shower", "shower", "Master exhaust fan", "exhaust fan", "Master bedroom overhead light", "bedroom overhead light",
                    "Kitchen overhead light", "Master overhead light", "bathroom overhead light", "bathroom overhead light", "Living Room overhead light",
                    "Living Room lamp", "Living Room lamp", "Master lamp", "lamp", "Master TV", "Living Room TV", "front door", "back door", "garage door", "washer", 
                    "dryer", "Master faucet", "faucet", "faucet", "kitchen faucet", "outside faucet", "stove", "oven", "microwave", "dishwasher",
                    "Living Room window", "Living Room window", "Living Room window", "Master window", "window", "bathroom window", "kitchen window", "kitchen window"]
    
    

#chances are made based on time
#showers only in master bedroom
