from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .jobs import air_quality_job, hvac_job, event_loop, event_summary
def start():

    scheduler = BackgroundScheduler()
    # scheduler.add_job(air_quality_job, 'interval', seconds=300)
    # scheduler.add_job(event_loop, 'interval', seconds=10)
    # scheduler.add_job(event_summary, 'interval', seconds=5)
    scheduler.start()