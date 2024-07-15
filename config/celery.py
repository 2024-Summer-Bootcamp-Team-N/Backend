from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Django의 설정 파일을 Celery의 기본 설정으로 사용하도록 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Django의 설정 파일에서 CELERY 관련 설정을 불러옴
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS + ['tasks'])

# Celery 설정 업데이트
app.conf.broker_connection_retry_on_startup = True

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
