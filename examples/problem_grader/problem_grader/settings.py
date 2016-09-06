import sys
import os
from path import path

# Django settings for problem_grader project.

ROOT_PATH = path(__file__).dirname()
REPO_PATH = ROOT_PATH.dirname()
ENV_ROOT = REPO_PATH.dirname()

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

LOGIN_REDIRECT_URL = '/grader'

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'db/grader.db',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'problem-grader'
    }
}

#Avoid clashes with api by changing these
SESSION_COOKIE_NAME = "problemgradersessionid"
CSRF_COOKIE_NAME = "problemgradercsrftoken"

#Figure out where the API is!
API_URL_BASE = "http://127.0.0.1:7999/"
API_URL_INTERMEDIATE = "essay_site/api/v1/"
FULL_API_START = API_URL_BASE + API_URL_INTERMEDIATE


# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

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
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

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
            'js/bootstrap.js',
            'js/jquery.cookie.js',
            'js/underscore.js',
            ],
        'output_filename': 'js/util.js',
        },
    'course' : {
        'source_filenames': [
            'js/course.js',
        ],
        'output_filename': 'js/course.js',
    },
    'problem' : {
        'source_filenames': [
            'js/problem.js',
            ],
        'output_filename': 'js/problem.js',
    },
    'essay' : {
    'source_filenames': [
        'js/essay.js',
        'js/essay_nav.js'
        ],
    'output_filename': 'js/essay.js',
    },
    'essaygrade' : {
        'source_filenames': [
            'js/essaygrade.js',
            'js/essay_nav.js',
            ],
        'output_filename': 'js/essaygrade.js',
        },
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
SECRET_KEY = 'p*51#*%wyw^y3a@%s*ak+xb$o4sfsr#xkj@d-n^ammtelysp@@'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'problem_grader.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'problem_grader.wsgi.application'

AUTH_PROFILE_MODULE = 'grader.UserProfile'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.abspath(REPO_PATH / "templates"),
    os.path.abspath(REPO_PATH / "grader")
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'grader',
    'south',
    'pipeline',
)

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
            'level': 'DEBUG' if DEBUG else 'INFO',
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
