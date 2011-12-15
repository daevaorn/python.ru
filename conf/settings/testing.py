#-*- coding: utf-8 -*-
from default_settings import *

DEBUG = True
TEMPLATE_DEBUG = False

DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     '%(db_base)s',
        'USER':     '%(db_user)s',
        'PASSWORD': '%(db_password)s',
        'OPTIONS':  {'init_command': 'SET storage_engine=INNODB'},
    }
}

EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025

CACHE_BACKEND = 'dummy://'

TEMPLATE_STRING_IF_INVALID = '[undefined]'

INTERNAL_IPS = ('217.197.112.137', '127.0.0.1')

SCIPIO_AKISMET_KEY = '%(akismet_key)s'
SCIPIO_STORE_ROOT = '%(remote_lib_path)s/openid'
SCIPIO_TRUST_URL = 'http://%(hostname)s'
