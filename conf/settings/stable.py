#-*- coding: utf-8 -*-
from default_settings import *

DEBUG = False
TEMPLATE_DEBUG = False

DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     '%(db_base)',
        'USER':     '%(db_user)s',
        'PASSWORD': '%(db_password)s',
        'OPTIONS':  {'init_command': 'SET storage_engine=INNODB'},
    }
}

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'daevaorn@gmail.com'
EMAIL_HOST_PASSWORD = 'spartakmoskva'
EMAIL_PORT = 587

CACHE_BACKEND = 'memcached://127.0.0.1:11211/?timeout=8640'

TEMPLATE_STRING_IF_INVALID = ''

INTERNAL_IPS = ('217.197.112.137', '127.0.0.1')

SCIPIO_AKISMET_KEY = '%(akismet_key)s'
SCIPIO_STORE_ROOT = '%(remote_lib_path)s/openid'
SCIPIO_TRUST_URL = 'http://%(hostname)s'

