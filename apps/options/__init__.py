from __future__ import absolute_import, unicode_literals

# Import the Celery app to ensure tasks are registered
from config.celery import app as celery_app

__all__ = ('celery_app',)