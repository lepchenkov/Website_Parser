import time
from celery import Celery
from oma_celery import descrete_parsing


app = Celery('periodic', broker='amqp://localhost//')

@app.task
def run_parsing_procedure():
    descrete_parsing()

app.conf.beat_schedule = {
    "run_parsing": {
        "task": "periodic.run_parsing_procedure",
        "schedule": 2.0
    }
}
