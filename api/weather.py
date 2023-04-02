# functions that will be used to populate tables with history of temperature data
from datetime import datetime, timedelta
from meteostat import Hourly, Point

#creates a point for Birmingham, AL
birmingham = Point(33.5186, -86.8104)

# gets hourly data for the past week, excluding the current hour, 168 entries
def getWeeklyHistory():
    end = datetime.now() - timedelta(hours=1)
    beginning = end - timedelta(days = 7)

    data = Hourly(birmingham, beginning, end)
    data = data.fetch()
    data_trim = data['temp'].tolist()

    return(data_trim)

def getTemperature():
    now = datetime.now()

    data = Hourly(birmingham, now - timedelta(hours=1), now)
    data = data.fetch()['temp'].tolist()

    return(data)

print(getTemperature())