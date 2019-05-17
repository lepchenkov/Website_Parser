from celery import Celery

#initialize an app
#'tasks' is the name for the list of tasks
#the broker is where the messages are stored
#for rabbitMQ the connection string is amqp://localhost
app = Celery('tasks', broker='amqp://localhost//')



@app.task
def reverse(string):
    return string[::-1]
#any function that follows @app.task can then be executed by celery 
