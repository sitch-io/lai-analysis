from __future__ import absolute_import, unicode_literals
from celery import Celery

app = Celery(broker="amqp://guest:guest@localhost:5672",
             include=["celeryutils.tasks"])

if __name__ == '__main__':
    app.start()
