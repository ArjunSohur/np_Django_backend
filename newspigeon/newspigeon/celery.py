import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "newspigeon.settings")
app = Celery("newspigeon")
app.config_from_object("django.conf:settings", namespace="CELERY_")
app.conf.task_routes = {'home.tasks.fetch_articles': {'queue': 'queue1'}}

app.autodiscover_tasks()

