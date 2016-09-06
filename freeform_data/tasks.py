"""
Used by celery to decide what tasks it needs to do
"""

from celery import task
import logging
from celery.task import periodic_task
from datetime import timedelta
from django.conf import settings
from django.core.management import call_command
from helpers import single_instance_task

log = logging.getLogger(__name__)

@periodic_task(run_every=timedelta(seconds=settings.TIME_BETWEEN_INDEX_REBUILDS))
@single_instance_task(settings.INDEX_REFRESH_CACHE_LOCK_TIME)
def refresh_search_index():
    """
    A task that will periodically update the search index
    """
    call_command('update_index', interactive=False)