# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
from decouple import config
from unipath import Path
from celery.schedules import crontab

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).parent
CORE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Sử dụng custom User model
AUTH_USER_MODEL = 'users.User'
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='S#perS3crEt_1122')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

# load production server from .env
ALLOWED_HOSTS = ['localhost', '127.0.0.1', config('SERVER', default='127.0.0.1'), '103.143.207.113', 'demo.hinosoft.com', '192.168.104.107']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django_extensions',
    'rest_framework',
    'channels',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'django_celery_beat',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.home',  # Enable the inner home (home)
    'apps.users',  # Enable the inner users (authentication)
    'apps.customers',  # Enable the inner customers (customers)
    'apps.producttemplates',  # Enable the inner producttemplates (producttemplates)
    'apps.store',  # Enable the inner store (store)
]


SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "none"
SOICIAL_ACCOUNT_QUERY_EMAIL = True

SOICIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'fIELDS': [
            'email','first_name','last_name','name','picture']

    }
    }

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'core.urls'
LOGIN_REDIRECT_URL = "home"  # Route defined in home/urls.py
LOGOUT_REDIRECT_URL = "home"  # Route defined in home/urls.py
TEMPLATE_DIR = os.path.join(CORE_DIR, "apps/templates")  # ROOT dir for templates

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application'

CELERY_BROKER_URL = 'redis://redis:6379/0'

CELERY_BEAT_SCHEDULE = {
    'collect-data-every-minute': {
        'task': 'apps.home.tasks.collect_data',
        'schedule': crontab(minute='*/1'),  # chạy mỗi phút
        'args': [],
    },
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis", 6379)],
        },
    },
}

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        # 'NAME': 'SKU',
        'NAME': 'appseed_db',
        'USER': 'postgres',
        # 'PASSWORD': '123456',
        'PASSWORD': 'postgres',
        'HOST': 'db',
        # 'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

#############################################################
# SRC: https://devcenter.heroku.com/articles/django-assets

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(CORE_DIR, 'staticfiles')
STATIC_URL = '/static/'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(CORE_DIR, 'apps/static'),
)


#############################################################
#############################################################


ODDO_SERVER_URL = os.environ.get('ODDO_SERVER_URL', 'http://localhost:8069')
ODDO_DB = os.environ.get('ODDO_DB', 'btmh')
ODDO_USERNAME = os.environ.get('ODDO_USERNAME', 'admin')
ODDO_PASSWORD = os.environ.get('ODDO_PASSWORD', 'admin')

# CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

# =====================
# External service configs
# =====================
INTERNAL_API_BASE = config('INTERNAL_API_BASE', default='http://118.70.146.150:8869')
PRICE_API_BASE = config('PRICE_API_BASE', default='http://192.168.0.223:8096')

# Postgres for CTKM (EmailTCKT)
EMAILTCKT_PG_HOST = config('EMAILTCKT_PG_HOST', default='192.168.0.221')
EMAILTCKT_PG_PORT = config('EMAILTCKT_PG_PORT', default=5432, cast=int)
EMAILTCKT_PG_DB = config('EMAILTCKT_PG_DB', default='EmailTCKT')
EMAILTCKT_PG_USER = config('EMAILTCKT_PG_USER', default='postgres')
EMAILTCKT_PG_PASSWORD = config('EMAILTCKT_PG_PASSWORD', default='admin')

# CTKM / chiết khấu
PROMO_API_URL = config('PROMO_API_URL', default='http://192.168.0.223:8097/api/public/CTKM')
DISCOUNT_API_URL = config('DISCOUNT_API_URL', default='http://192.168.0.223:8097/api/public/all_ctmk')

# Tỷ giá vàng
TYGIA_API_BASE_URL = config('TYGIA_API_BASE_URL', default='https://tygia.baotinmanhhai.vn/api')
TYGIA_API_TOKEN = config('TYGIA_API_TOKEN', default='eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiIs')

TIME_ZONE = "Asia/Ho_Chi_Minh"
USE_TZ = True
