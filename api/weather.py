# functions that will be used to populate tables with history of temperature data
from datetime import datetime, timedelta
from meteostat import Hourly, Point
import csv
import ssl

ssl._create_default_https_context = ssl._create_stdlib_context


#creates a point for Birmingham, AL
birmingham = Point(33.5186, -86.8104)

# gets hourly data for the past week, excluding the current hour, 168 entries
def getWeeklyHistory():
    end = datetime.now()
    beginning = end - timedelta(days = 7)

    data = Hourly(birmingham, beginning, end)
    data = data.fetch()
    data_trim = data['temp'].tolist()

    data_trim_datetime = []

    for i in range(len(data_trim)):
        data_trim_datetime.append([beginning + timedelta(hours=i), data_trim[i]])

    return(data_trim_datetime)

# gets data for the current hour
def getTemperature():
    now = datetime.now()

    #get weather from meteostat
    data = Hourly(birmingham, now - timedelta(hours=1), now)
    temp = data.fetch()['temp'].tolist()[0]

    #convert to fahrenheit
    temp = celsius_to_fahrenheit(temp)

    return(temp)


def getHumidity():
    now = datetime.now()

    #get weather from meteostat
    data = Hourly(birmingham, now - timedelta(hours=1), now)
    humidity = data.fetch()['rhum'].tolist()[0]

    return(humidity)

def celsius_to_fahrenheit(celsius_temp):
    fahrenheit_temp = (celsius_temp * 9/5) + 32
    return fahrenheit_temp