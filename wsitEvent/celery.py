from __future__ import absolute_import
from celery import Celery
from django.conf import settings

import os


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wsitEvent.settings')

app = Celery('wsitEvent',
             broker=''
                    'amqp://guest:guest@localhost://',
             backend='amqp',
             include=['wsitEvent.tasks'])
# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=86400,
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],
)


if __name__ == '__main__':
    app.start()
