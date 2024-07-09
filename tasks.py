from __future__ import absolute_import, unicode_literals
from Backend.config.celery import shared_task

@shared_task
def add(x, y):
    return x + y
