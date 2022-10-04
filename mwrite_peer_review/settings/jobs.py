"""
Django settings for mwrite_peer_review project.

Generated by 'django-admin startproject' using Django 1.10.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
import json
from os import getenv


def read_file_from_env(var):
    filename = os.environ[var]
    with open(filename, 'r') as file:
        contents = file.read()
    return contents.strip()


def getenv_bool(var, default='0'):
    return getenv(var, default).lower() in ('yes', 'on', 'true', '1',)


def getenv_csv(var, default=''):
    val = getenv(var, default)

    if len(val) == 0:
        return []

    return [x.strip(' ') for x in val.split(',')]


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEBUG = getenv_bool('MPR_DEBUG_MODE')
DEBUG = True
SECRET_KEY = 'unused'
APP_HOST = os.environ['MPR_APP_HOST']

EMAIL_HOST = os.environ['MPR_EMAIL_HOST']
EMAIL_PORT = os.environ['MPR_EMAIL_PORT']
SERVER_EMAIL = os.environ['MPR_SERVER_FROM_EMAIL']
ADMINS = list(map(lambda email: ('', email), getenv_csv('MPR_SERVER_TO_EMAILS')))

# Storage configuration
MEDIA_ROOT = os.environ['MPR_SUBMISSIONS_PATH']

TOLERANCE_ATTEMPTS: int = int(os.getenv('MPR_DIST_TOLERANCE_ATTEMPTS', 3))
TOLERANCE_RATE: float = float(os.getenv('MPR_DIST_TOLERANCE_ERROR_RATE', 0.25))
TOLERANCE_TEST_ERRONEOUS_FILENAME: str = os.getenv('MPR_TOLERANCE_TEST_ERRONEOUS_FILENAME')

# LTI configuration
LTI_CONSUMER_SECRETS = None
LTI_APP_REDIRECT = None
LTI_ENFORCE_SSL = False  # TODO want this to be True in prod; add config for X-Forwarded etc.

# Canvas API configuration
CANVAS_API_URL = os.environ['MPR_CANVAS_API_URL']
CANVAS_API_TOKEN = os.environ['MPR_CANVAS_API_TOKEN']

# Application definition
INSTALLED_APPS = ['peer_review']
MIDDLEWARE = []
AUTHENTICATION_BACKENDS = []
TEMPLATES = []
WSGI_APPLICATION = ''

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases
DATABASES = {
    'default': json.loads(read_file_from_env('MPR_DB_CONFIG_PATH'))
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = []

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True
USE_TZ = True
TIME_ZONE = os.environ['MPR_TIMEZONE']
TIME_OUTPUT_FORMAT = '%b %-d %-I:%M %p'  # if running on Windows, replace - with #


# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'all': {
#             'format': ('%(levelname)s %(asctime)s %(module)s %(process)d '
#                        '%(thread)d %(message)s'),
#         },
#         'debug': {
#             'format': ('%(asctime)s %(levelname)s %(message)s '
#                        '%(pathname)s:%(lineno)d'),
#         },
#         'simple': {
#             'format': '%(levelname)s %(name)s %(message)s'
#         },
#         'access_logs': {
#             'format': '%(message)s',
#         },
#
#     },
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#             'formatter': 'debug',
#         },
#         'mail_admins': {
#             'class': 'django.utils.log.AdminEmailHandler',
#             'formatter': 'debug'
#         }
#     },
#     'loggers': {
#         '': {
#             'handlers': ['console'],
#             'level': 'DEBUG',
#             # 'propagate': True,
#         },
#         'management_commands': {
#             'handlers': ['mail_admins'],
#             'level': 'ERROR',
#             'propagate': True
#         }
#     },
# }

LOGGING = {
    'version': 1,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    }
}
