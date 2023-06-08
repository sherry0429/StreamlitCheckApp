from celery import Celery
from celery.schedules import crontab

app = Celery('proj', include=['proj.func'])
app.config_from_object('proj.celery_config')

# 定时任务
app.conf.beat_schedule = {
    "scheduled_push": {
        "task": "proj.func.push",
        "schedule": 10
    }
}

# crontab(minute="*/1")