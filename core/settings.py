# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os, environ

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, True)
)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CORE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Take environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='S#perS3crEt_007')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

# Assets Management
ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/assets') 

# load production server from .env
ALLOWED_HOSTS        = ['localhost', 'hinosoft.com', 'localhost:85', '127.0.0.1',               env('SERVER', default='127.0.0.1'), 'https://hinosoft.com', '103.143.207.113' ]
CSRF_TRUSTED_ORIGINS = ['http://localhost:85', 'hinosoft.com', 'https://hinosoft.com', 'http://127.0.0.1', 'https://' + env('SERVER', default='127.0.0.1') ]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.home',  # Enable the inner home (home)
    'apps.chat',
    'apps.apec',
    'apps.vantaihahai',
    'rest_framework',
    'channels' , 
    'rest_framework_simplejwt'
]

CHANNEL_LAYERS = {
    'default' : {
        'BACKEND' : 'channels.layers.InMemoryChannelLayer', #cambiar a redis, esto solo sirve de prueba
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
                'apps.context_processors.cfg_assets_root',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'HOST': os.environ.get('POSTGRES_HOST'),
    #     'NAME': os.environ.get('POSTGRES_NAME'),
    #     'USER': os.environ.get('POSTGRES_USER'),
    #     'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
    #     'PORT': os.environ.get('POSTGRES_PORT'),

    # },
    'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite3',
        },
    "nonrel": {
        "ENGINE": "djongo",
        "NAME": os.environ.get('MONGO_DB_NAME'),
        'USERNAME':  os.environ.get('MONGO_DB_USERNAME'),
        'PASSWORD': os.environ.get('MONGO_DB_PASSWORD'),
        'HOST': os.environ.get('MONGO_DB_HOST'),
        'PORT': int(os.environ.get('MONGO_DB_PORT')),
        "CLIENT": {
            "host": os.environ.get('MONGO_DB_HOST'),
            "port": int(os.environ.get('MONGO_DB_PORT')),
            "username": os.environ.get('MONGO_DB_USERNAME'),
            "password": os.environ.get('MONGO_DB_PASSWORD'),
            'authMechanism': 'SCRAM-SHA-1',
        },
        'TEST': {
            'MIRROR': 'default',
        },
    }
}
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=72),
}
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
DATABASE_ROUTERS = ['apps.home.utils.db_routers.NonRelRouter', ]
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
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_IGNORE_RESULT = True
CELERY_BROKER_URL = os.environ.get('CELERY_URL')
BROKER_URL = os.environ.get('BROKER_URL')
CELERYD_HIJACK_ROOT_LOGGER = False
REDIS_CHANNEL_URL = os.environ.get('REDIS_CHANNEL_URL')
# settings.py
REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')
REDIS_DB = 0
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

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(CORE_DIR, 'apps/static'),
)


#############################################################
#############################################################
VANTAIHAHAI_CONFIG = {
        "user_id": 2,
        "user_context": {
            "lang": "vi_VN",
            "tz": "Asia/Saigon",
            "uid": 2
        },
        "company_id": 1,
        "access_token": "fd949520448ba5966593f194548f24cfc56fc519",
        "expires_in": 72000000,
        "refresh_token": "7dd3502a2eb684903b7e5c8fecd537796173460e",
        "refresh_expires_in": 72000000,
        'register_token':'123456',
        'url': 'https://vantaihahai.com',
        'db': 'fleet',
        'username':'admin',
        'password':'admin'
          
}

APEC_CONFIG = {
    'MINIO_ACCESS_KEY' : "FLoU4kYrt6EQ8eyWBLjD",
    'MINIO_SECRET_KEY' : "LBa3KybNAxwxHWuFPqKF00ppIi5iOotJXQQzriUa",
    'MINIO_BUCKET_NAME' : "apecerp",
    'MINIO_ENDPOINT_URL' : "http://42.113.122.201:9000/apecerp/",
    'MINIO_ENDPOINT' : "42.113.122.201:9000",
    'MINIO_PUBLIC_URL' : "https://minio.qcloud.asia/apecerp/",
    'SERVER_URL' : 'https://hrm.mandalahotel.com.vn',
    'SERVER_URL_DB' : 'apechrm_product_v3',
    'SERVER_USERNAME': 'admin_ho',
    'SERVER_PASSWORD': '369249ce990803ee489c47cf604e3c8622173f39',
# CLOUD_OUTPUT_REPORT_FOLDER = env('CLOUD_OUTPUT_REPORT_FOLDER', default='C:/Users/PC/Dropbox/APECHRMS/OuputReport_M2')

    'SERVER_CRM_USERNAME': 'yenbt',
    'SERVER_CRM_PASSWORD': 'c278b3b1aea761ebaccf5a4f2589716d4cc800df'
}