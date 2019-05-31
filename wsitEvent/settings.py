"""
Django settings for wsitEvent project.

Generated by 'django-admin startproject' using Django 1.8.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for master
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in master secret!
SECRET_KEY = '2wako5@=t$f8g+@%#aft4yw38%f66$&(yn(_0s5gwqo$!8p6&c'

# SECURITY WARNING: don't run with debug turned on in master!


os.environ['ENVIRONMENT_TYPE'] = 'tempmaster'
DEBUG = True
TEMPLATE_DEBUG = False
ALLOWED_HOSTS = ['*']

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app',
    'publicfront',
    'storages',
    'django_crontab'
)

import djcelery
djcelery.setup_loader()
# Celery config ##
BROKER_URL = "amqp://guest:guest@localhost://"
CELERY_IMPORTS = ('wsitEvent.tasks', )

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'publicfront.middleware.user_login_middleware.UserLoginMiddleware',
    # 'publicfront.middleware.timezone_middleware.TimezoneMiddleware',
    'publicfront.middleware.export_middleware.ExportMiddleware',
)

ROOT_URLCONF = 'wsitEvent.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "django.core.context_processors.media",
                # 'publicfront.views.common.get_style',
            ],
        },
    },
]

WSGI_APPLICATION = 'wsitEvent.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/ #databases



CRONJOBS = [
    ('*/1 * * * *', 'app.views.mobile_device.push_notification'),
    # ('1 0 * * *', 'app.views.gbhelper.cron_job_library.daily_job'),
    ('*/5 * * * *', 'app.views.gbhelper.cron_job_library.daily_job'),
]
# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/
LANGUAGE_CODE = 'en-us'

TIME_ZONE = None

USE_I18N = True

USE_L10N = True
EMAIL_SENDER = 'mahedi@workspaceit.com'
DEFAULT_FROM_EMAIL = EMAIL_SENDER
AWS_ACCESS_KEY_ID = 'AKIAJQF7DRAHJW36J6HA'
AWS_SECRET_ACCESS_KEY = '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'
SMTP_USERNAME = 'AKIAJQF7DRAHJW36J6HA'
SMTP_PASSWORD = 'I18QoT8iFJWp0bpvVBQ0isNKzsZ81wlSZIQRMp7r'
AWS_STORAGE_HOST = 's3.eu-west-1.amazonaws.com'
AWS_REGION_NAME = 'eu-west-1'

DATABASES = {
    'default': {
        'NAME': 'wsit_event_db',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'wsit',
        'PASSWORD': 'wsit97480',
        'HOST': '58.84.34.65',
        'PORT': '3306',
        'OPTIONS': {
            'autocommit': True,
        },
    }
}


if DEBUG:
    import logging
    l = logging.getLogger('django.db.backends')
    l.setLevel(logging.DEBUG)
    l.addHandler(logging.StreamHandler())


STATIC_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')
STATIC_URL = '/static/'

USE_TZ = False

SES_REGION = 'eu-west-1'

S3_BUCKET_NAME = ''

# S3 Bucket name
if os.environ['ENVIRONMENT_TYPE'] == 'tempmaster':
    S3_BUCKET_NAME = 'wsit-event-dev'
else:
    S3_BUCKET_NAME = 'wsit-event-dev'

AWS_STORAGE_BUCKET_NAME = S3_BUCKET_NAME

STATIC_URL_ALT = 'https://s3-eu-west-1.amazonaws.com/{bucket_name}/'.format(
        bucket_name=AWS_STORAGE_BUCKET_NAME)

LOCAL_ENV = False



if os.environ['ENVIRONMENT_TYPE'] == 'master':
    SITE_URL = 'http://127.0.0.1:8003/'
else:
    SITE_URL = 'http://127.0.0.1:8003'


# DIBS_ACTION_URL = 'https://sat1.dibspayment.com/dibspaymentwindow/entrypoint'
DIBS_ACTION_URL = ''
DIBS_ACCEPT_URL = 'payment-callback-success/'
DIBS_CANCEL_URL = 'payment-callback-cancel/'
DIBS_ACCEPT_RETURN_URL = 'payment-callback-success/'
DIBS_TEST = 0


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/wsit-event.log',
            'formatter': 'verbose'
        },
    },
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'loggers': {
        'app': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'publicfront': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    },
}

try:
    from .local_settings import *
except ImportError:
    pass





