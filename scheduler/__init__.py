'''Init file with celery app added'''
from __future__ import absolute_import, unicode_literals
from scheduler.celery import app as celery_app

__all__ = ['celery_app']
