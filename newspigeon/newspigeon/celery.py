import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "newspigeon.settings")
app = Celery("newspigeon")
app.config_from_object("django.conf:settings", namespace="CELERY_")

@app.task
def do_something():
    print("hi")

app.autodiscover_tasks()