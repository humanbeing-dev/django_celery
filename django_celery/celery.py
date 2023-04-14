"""
https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html
"""
import os
import logging

from django.conf import settings

from celery import Celery
from celery.signals import after_setup_logger


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_celery.settings")
app = Celery("django_celery")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


# @after_setup_logger.connect()
# def on_after_setup_logger(logger, **kwargs):
#     formatter = logger.handlers[0].formatter
#     file_handler = logging.FileHandler('celery.log')
#     file_handler.setFormatter(formatter)
#     logger.addHandler(file_handler)


@app.task
def divide(x, y):
    # from celery.contrib import rdb
    # rdb.set_trace()

    import time

    time.sleep(5)
    return x / y
