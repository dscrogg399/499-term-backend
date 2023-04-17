# import datetime
from django.apps import AppConfig



class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        from api import updater
        from .queue import EventQueue
        from .event_utils import startup_data_generator
        from .hvac_utils import historic_hvac_util
        from .models import Event, Appliance
        from datetime import timedelta, datetime
        from django.db.models import  Max

        now = datetime.now()

        # clean up hanging events
        events_to_update = Event.objects.filter(is_active=True, off_at=None)

        for event in events_to_update:
            # Set off_at to 1 minute after on_at
            event.end_event(event.on_at + timedelta(minutes=1), event.appliance.appliance_type_id)
            event.save()


        #get the max off_at time
        event_with_max_off_at = Event.objects.filter(is_active=True).aggregate(max_off_at=Max('off_at'))['max_off_at']
        max_event = Event.objects.get(off_at=event_with_max_off_at, is_active=True)
        queue = EventQueue.instance()
        historic_hvac_util(max_event.off_at, now)
        startup_data_generator(max_event.off_at)
        updater.start()


