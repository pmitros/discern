"""
Deployment settings file
"""

from settings import *
import json

DEBUG=False

TIME_BETWEEN_INDEX_REBUILDS = 60 * 30 # seconds

#Tastypie throttle settings
THROTTLE_AT = 100 #Throttle requests after this number in below timeframe
THROTTLE_TIMEFRAME= 60 * 60 #Timeframe in which to throttle N requests, seconds
THROTTLE_EXPIRATION= 24 * 60 * 60 # When to remove throttle entries from cache, seconds

with open(os.path.join(ENV_ROOT,"env.json")) as env_file:
    ENV_TOKENS = json.load(env_file)

with open(os.path.join(ENV_ROOT, "auth.json")) as auth_file:
    AUTH_TOKENS = json.load(auth_file)

DATABASES = AUTH_TOKENS.get('DATABASES', DATABASES)
CACHES = AUTH_TOKENS.get('CACHES', CACHES)

AWS_ACCESS_KEY_ID = AUTH_TOKENS.get('AWS_ACCESS_KEY_ID', AWS_ACCESS_KEY_ID)
AWS_SECRET_ACCESS_KEY = AUTH_TOKENS.get('AWS_SECRET_ACCESS_KEY', AWS_SECRET_ACCESS_KEY)

USE_S3_TO_STORE_MODELS = ENV_TOKENS.get('USE_S3_TO_STORE_MODELS', USE_S3_TO_STORE_MODELS)
S3_BUCKETNAME = ENV_TOKENS.get('S3_BUCKETNAME', S3_BUCKETNAME)

BROKER_URL = AUTH_TOKENS.get('BROKER_URL', BROKER_URL)
CELERY_RESULT_BACKEND = AUTH_TOKENS.get('CELERY_RESULT_BACKEND', CELERY_RESULT_BACKEND)


ELB_HOSTNAME = ENV_TOKENS.get('ELB_HOSTNAME', None)

DNS_HOSTNAME = ENV_TOKENS.get('DNS_HOSTNAME', None)

if ELB_HOSTNAME is not None:
    ALLOWED_HOSTS += [ELB_HOSTNAME]

if DNS_HOSTNAME is not None:
    ALLOWED_HOSTS += [DNS_HOSTNAME]

EMAIL_BACKEND = ENV_TOKENS.get('EMAIL_BACKEND', EMAIL_BACKEND)

DEFAULT_FROM_EMAIL = ENV_TOKENS.get('DEFAULT_FROM_EMAIL')

ACCOUNT_EMAIL_VERIFICATION = ENV_TOKENS.get('ACCOUNT_EMAIL_VERIFICATION', ACCOUNT_EMAIL_VERIFICATION)

AWS_SES_REGION_NAME = ENV_TOKENS.get('AWS_SES_REGION_NAME', 'us-east-1')
if AWS_SES_REGION_NAME is not None:
    AWS_SES_REGION_ENDPOINT = 'email.{0}.amazonaws.com'.format(AWS_SES_REGION_NAME)

#Set this for django-analytical.  Because django-analytical enables the service if the key exists,
#ensure that the settings value is only created if the key exists in the deployment settings.
ga_key = AUTH_TOKENS.get("GOOGLE_ANALYTICS_PROPERTY_ID", "")
if len(ga_key)>1:
    GOOGLE_ANALYTICS_PROPERTY_ID = ga_key

#Try to set the domain for the current site
#Needed to get the right site name for email activation
#Comment out, as this is causing issues in deployment.
#TODO: Move to a fixture
"""
try:
    if DNS_HOSTNAME is not None:
        from django.contrib.sites.models import Site
        current_site = Site.objects.get(id=SITE_ID)

        current_site.domain = DNS_HOSTNAME
        current_site.name = DNS_HOSTNAME
        current_site.save()
except:
    log.info("Could not set site name and domain.  Not a problem if this is a dev/sandbox environment.  May cause confusion with email activation in production.")
"""