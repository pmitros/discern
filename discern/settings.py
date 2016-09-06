"""
Local settings file
"""
import sys
import os
from path import path
import logging
log = logging.getLogger(__name__)

#Initialize celery
import djcelery
djcelery.setup_loader()

# Django settings for ml_service_api project.
ROOT_PATH = path(__file__).dirname()
REPO_PATH = ROOT_PATH.dirname()
ENV_ROOT = REPO_PATH.dirname()

#ML Specific settings
ML_MODEL_PATH=os.path.join(REPO_PATH,"ml_models_api/") #Path to save and retrieve ML models from
TIME_BETWEEN_ML_CREATOR_CHECKS= 1 * 60 # seconds.  Time between ML creator checking to see if models need to be made.
TIME_BETWEEN_ML_GRADER_CHECKS= 10 # seconds.  Time between ML grader checking to see if models need to be made.
USE_S3_TO_STORE_MODELS= False #Determines whether or not models are placed in Amazon S3

#Credentials for the S3 bucket.  Do not edit here, but provide the right settings in env.json and auth.json, and then
#use aws.py as the settings file.
S3_BUCKETNAME="OpenEnded"
AWS_ACCESS_KEY_ID = None
AWS_SECRET_ACCESS_KEY = None

TIME_BEFORE_REMOVING_STARTED_MODEL = 10 * 60 * 60 # in seconds, time before removing an ml model that was started (assume it wont finish)
MODEL_CREATION_CACHE_LOCK_TIME = 5 * 60 * 60
GRADING_CACHE_LOCK_TIME = 60 * 60
INDEX_REFRESH_CACHE_LOCK_TIME = 24 * 60 * 60

LOGIN_REDIRECT_URL = "/frontend/"

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DB_PATH = "db/"

#Make the db path dir if it does not exist
if not os.path.isdir(DB_PATH):
    os.mkdir(DB_PATH)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': DB_PATH + 'service-api-db.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

#Need caching for API rate limiting
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'discern-cache'
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.abspath(REPO_PATH / "staticfiles")

#Make the static root dir if it does not exist
if not os.path.isdir(STATIC_ROOT):
    os.mkdir(STATIC_ROOT)

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.abspath(REPO_PATH / 'css_js_src/'),
)

STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'

PIPELINE_JS = {
    'util' : {
        'source_filenames': [
            'js/jquery-1.9.1.js',
            'js/json2.js',
            'js/underscore.js',
            'js/bootstrap.js',
            'js/backbone.js',
            'js/backbone.validations.js',
            'js/backbone-tastypie.js',
            'js/backbone-schema.js',
            'js/setup-env.js',
            'js/api-views.js',
            'js/jquery.cookie.js',
            ],
        'output_filename': 'js/util.js',
    }
}
SESSION_COOKIE_NAME = "mlserviceapisessionid"
CSRF_COOKIE_NAME = "mlserviceapicsrftoken"

API_MODELS = ["userprofile", "user", "membership", "course", "organization", "problem", "essay", "essaygrade"]

for model in API_MODELS:
    PIPELINE_JS[model] = {
        'source_filenames': [
            'js/views/{0}.js'.format(model)
        ],
        'output_filename': 'js/{0}.js'.format(model),
    }

PIPELINE_CSS = {
    'bootstrap': {
        'source_filenames': [
            'css/bootstrap.css',
            'css/bootstrap-responsive.css',
            'css/bootstrap-extensions.css',
            ],
        'output_filename': 'css/bootstrap.css',
        },
    'util_css' : {
        'source_filenames': [
            'css/jquery-ui-1.10.2.custom.css',
            ],
        'output_filename': 'css/util_css.css',
        }
}


PIPELINE_DISABLE_WRAPPER = True
PIPELINE_YUI_BINARY = "yui-compressor"

PIPELINE_CSS_COMPRESSOR = None
PIPELINE_JS_COMPRESSOR = None

PIPELINE_COMPILE_INPLACE = True
PIPELINE = True

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'u)4v9b&amp;9jhsg-&amp;&amp;^*!jff&amp;t1e7$em0uh8^i^w!ojjvr&amp;8$ok6-'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    "allauth.account.context_processors.account",
    "allauth.socialaccount.context_processors.socialaccount",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'request_provider.middleware.RequestProvider',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
    "allauth.account.auth_backends.AuthenticationBackend",
)

ANONYMOUS_USER_ID = -1

ROOT_URLCONF = 'discern.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'discern.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.abspath(REPO_PATH / "templates"),
    os.path.abspath(REPO_PATH / "freeform_data")
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    # remove django.contrib.sites to avoid this issue: https://github.com/edx/discern/issues/85
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'tastypie',
    'south',
    'djcelery',
    'pipeline',
    'guardian',
    'haystack',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'analytical',
    'freeform_data',
    'ml_grading',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

syslog_format = ("[%(name)s][env:{logging_env}] %(levelname)s "
                 "[{hostname}  %(process)d] [%(filename)s:%(lineno)d] "
                 "- %(message)s").format(
    logging_env="", hostname="")

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(levelname)s %(process)d '
                      '[%(name)s] %(filename)s:%(lineno)d - %(message)s',
            },
        'syslog_format': {'format': syslog_format},
        'raw': {'format': '%(message)s'},
        },
    'handlers': {
        'console': {
#            'level': 'DEBUG' if DEBUG else 'INFO',
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'stream': sys.stdout,
            },
        'null': {
            'level': 'DEBUG',
            'class':'django.utils.log.NullHandler',
            },
        },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
            },
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False
            },
        'django.db.backends': {
            'handlers': ['null'],  # Quiet by default!
            'propagate': False,
            'level':'DEBUG',
            },
        }
}

AUTH_PROFILE_MODULE = 'freeform_data.UserProfile'

BROKER_URL = 'redis://localhost:6379/5'
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
CELERY_RESULT_BACKEND = 'redis://localhost:6379/5'

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

#Haystack settings
HAYSTACK_SITECONF = 'discern.search_sites'
HAYSTACK_SEARCH_ENGINE = 'whoosh'
HAYSTACK_WHOOSH_PATH = os.path.join(REPO_PATH,"whoosh_api_index")
TIME_BETWEEN_INDEX_REBUILDS = 60 # seconds

#Check to see if the ml repo is available or not
FOUND_ML = False
try:
    import ease.grade
    FOUND_ML = True
except:
    pass

#Tastypie throttle settings
THROTTLE_AT = 10000 #Throttle requests after this number in below timeframe, dev settings, so high!
THROTTLE_TIMEFRAME= 60 * 60 #Timeframe in which to throttle N requests, seconds
THROTTLE_EXPIRATION= 24 * 60 * 60 # When to remove throttle entries from cache, seconds

#Model settings
MEMBERSHIP_LIMIT=1 #Currently users can only be in one organization

#Django-allauth settings
ACCOUNT_EMAIL_VERIFICATION = "none" #No email verification required locally
ACCOUNT_EMAIL_REQUIRED = True #Ask user to enter an email
ACCOUNT_AUTHENTICATION_METHOD="username_email" #Can enter username or email to login
ACCOUNT_PASSWORD_MIN_LENGTH = 3 #For testing, set password minimum low.

#Django email backend for local testing
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'