# functions that will be used to populate tables with history of temperature data
from datetime import datetime, timedelta
from meteostat import Hourly, Point
import csv

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

    data = Hourly(birmingham, now - timedelta(hours=1), now)
    data = data.fetch()['temp'].tolist()

    data_datetime = [datetime.now(), data[0]]

    return(data_datetime)

print(getWeeklyHistory())
print(getTemperature())