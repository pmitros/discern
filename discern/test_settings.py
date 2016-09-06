from settings import *
import logging

south_logger=logging.getLogger('south')
south_logger.setLevel(logging.INFO)

warning_logger=logging.getLogger('py.warnings')
warning_logger.setLevel(logging.ERROR)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME' : DB_PATH + 'service-api-test-db.db',
        }
}

# Nose Test Runner
INSTALLED_APPS += ('django_nose',)
NOSE_ARGS = [ '--with-xunit', '--with-coverage',
              '--cover-html-dir', 'cover',
             '--cover-package', 'freeform_data',
             '--cover-package', 'ml_grading',]
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

#Celery settings
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERY_ALWAYS_EAGER = True
BROKER_BACKEND = 'memory'

#Haystack settings
HAYSTACK_WHOOSH_PATH = os.path.join(ENV_ROOT,"whoosh_api_index_test")

#Model settings
MEMBERSHIP_LIMIT=50 #For testing purposes, relax membership limits

#Some errors only pop up with debug as false
DEBUG=False