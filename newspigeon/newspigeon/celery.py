import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "newspigeon.settings")
app = Celery("newspigeon")
app.config_from_object("django.conf:settings", namespace="CELERY_")

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f"request: {self.request!r}")

