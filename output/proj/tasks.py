from celery import Celery
from celery.schedules import crontab

app = Celery('proj', include=['proj.func'])
app.config_from_object('proj.celery_config')

# 每隔一分钟写入一次
app.conf.beat_schedule = {
    "scheduled_push": {
        "task": "proj.func.push",
        "schedule": crontab(minute="*/1")
    }
}

