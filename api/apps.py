# import datetime
from django.apps import AppConfig
# from api.models import Event
# from .hvac_utils import historic_hvac_util
# from django.db.models import  Max


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        from api import updater
        updater.start()

    # """
    # This job is the driver for the historic HVAC job and the hisoric event loop job.
    # It grabs the latest on at time from the events and considers that as the last time the server was operating
    # It passes that time and now into both the historic_hvac_util and historic_event_loop_util functions
    # Those functions simulate the event loop and hvac job for every minute between the two times, using
    # optimizations to make it run much faster than it would to actually turn the devices on and off
    # """
    # def startup_job():
    # #get time of last event in record and run the historic jobs from then to now
    #     event_with_max_on_at = Event.objects.filter(is_active=True).aggregate(max_on_at=Max('on_at'))['max_on_at']
    #     max_event = Event.objects.get(on_at=event_with_max_on_at, is_active=True)

    #     historic_hvac_util(max_event.on_at, datetime.now())
