import ssl

from datetime import datetime, timedelta
from meteostat import Hourly, Point


# functions that will be used to populate tables with history of temperature data
ssl._create_default_https_context = ssl._create_stdlib_context

#creates a point for Birmingham, AL
birmingham = Point(33.5186, -86.8104)

# gets hourly data for the given time frame excluding the current hour, 168 entries
def getWeatherHistory(start, end):

    data = Hourly(birmingham, start, end)
    data = data.fetch()
    data_trim = data['temp'].tolist()
    

    data_trim_datetime = []

    for i in range(len(data_trim)):
        data_trim_datetime.append([start + timedelta(hours=i), celsius_to_fahrenheit(data_trim[i])])

    result = {}

    for entry in data_trim_datetime:
        dt, value = entry
        date = dt.date()
        hour = dt.hour

        if date not in result:
            result[date] = [None] * 24

        result[date][hour] = value

    return result


#get temp at specific time
def getTemperatureAtTime(time):
        #get weather from meteostat
    data = Hourly(birmingham, time - timedelta(hours=1), time)
    temp = data.fetch()['temp'].tolist()[0]

    #convert to fahrenheit
    temp = celsius_to_fahrenheit(temp)

    return(temp)

#gets humidity at a given time
def getHumidity():
    now = datetime.now()
    #get weather from meteostat
    data = Hourly(birmingham, now - timedelta(minutes=1), now)
    humidity = data.fetch()['rhum'].tolist()[0]

    return(humidity)

#convert C to F
def celsius_to_fahrenheit(celsius_temp):
    fahrenheit_temp = (celsius_temp * 9/5) + 32
    return fahrenheit_temp

