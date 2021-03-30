""" Module to define local django-settings """
from .base import *
from .base import env

# Override Celery config
CELERY_WORKER_CONCURRENCY = 1
