from __future__ import absolute_import, unicode_literals
from config.celery import app

@app.task(bind=True)
def add(self, x, y):
    return x + y
