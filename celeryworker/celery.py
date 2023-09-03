from celery import Celery

app = Celery("newspigeon2")
app.config_from_object("celeryconfig")

@app.task
def print_something():
    print("YO")