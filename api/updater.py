from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .jobs import air_quality_job

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(air_quality_job, 'interval', seconds=300)
    scheduler.start()