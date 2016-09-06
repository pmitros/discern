"""
Used by celery to decide what tasks it needs to do
"""

from celery import task
import logging
from celery.task import periodic_task
from freeform_data.models import Problem, Essay
from datetime import timedelta
from django.conf import settings
from ml_grading.ml_model_creation import handle_single_problem, MIN_ESSAYS_TO_TRAIN_WITH
from ml_grading.ml_grader import handle_single_essay
from django.db.models import Q, Count
from django.db import transaction
from freeform_data.tasks import single_instance_task
from django.core.cache import cache

log=logging.getLogger(__name__)

@periodic_task(run_every=timedelta(seconds=settings.TIME_BETWEEN_ML_CREATOR_CHECKS))
@single_instance_task(settings.MODEL_CREATION_CACHE_LOCK_TIME)
def create_ml_models():
    """
    Called periodically by celery.  Loops through each problem and tries to create a model for it.
    """
    transaction.commit_unless_managed()
    problems = Problem.objects.all()
    for problem in problems:
        create_ml_models_single_problem(problem)

@task()
def create_ml_models_single_problem(problem):
    """
    Celery task called by create_ml_models to create a single model
    """
    transaction.commit_unless_managed()
    lock_id = "celery-model-creation-{0}".format(problem.id)
    acquire_lock = lambda: cache.add(lock_id, "true", settings.MODEL_CREATION_CACHE_LOCK_TIME)
    release_lock = lambda: cache.delete(lock_id)
    if acquire_lock():
        try:
            handle_single_problem(problem)
        finally:
            release_lock()

@periodic_task(run_every=timedelta(seconds=settings.TIME_BETWEEN_ML_GRADER_CHECKS))
@single_instance_task(settings.GRADING_CACHE_LOCK_TIME)
def grade_ml():
    """
    Called periodically by celery.  Loops through each problem, sees if there are enough essays for ML grading to work,
    and then calls the ml grader if there are.
    """
    transaction.commit_unless_managed()
    #TODO: Add in some checking to ensure that count is of instructor graded essays only
    problems = Problem.objects.all().annotate(essay_count=Count('essay')).filter(essay_count__gt=(MIN_ESSAYS_TO_TRAIN_WITH-1))
    for problem in problems:
        grade_ml_essays(problem)

@task()
def grade_ml_essays(problem):
    """
    Called by grade_ml.  Handles a single grading task for a single essay.
    """
    transaction.commit_unless_managed()
    lock_id = "celery-essay-grading-{0}".format(problem.id)
    acquire_lock = lambda: cache.add(lock_id, "true", settings.GRADING_CACHE_LOCK_TIME)
    release_lock = lambda: cache.delete(lock_id)
    if acquire_lock():
        try:
            essays = Essay.objects.filter(problem=problem, has_been_ml_graded=False)
            #TODO: Grade essays in batches so ml model doesn't have to be loaded every single time (or cache the model files)
            for essay in essays:
                handle_single_essay(essay)
        finally:
            release_lock()