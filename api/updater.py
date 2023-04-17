from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .jobs import air_quality_job, hvac_job, door_job
from .event_utils import event_loop
# from .event_utils import 
def start():

    scheduler = BackgroundScheduler()
    scheduler.add_job(air_quality_job, 'interval', seconds=60)
    scheduler.add_job(hvac_job, 'interval', seconds=60)
    scheduler.add_job(event_loop, 'interval', seconds=60)
    scheduler.add_job(door_job, 'interval', seconds=60)
    scheduler.start()