"""
Django settings for config project.
"""

import os, random, string
from pathlib import Path
from dotenv import load_dotenv
from str2bool import str2bool
from datetime import timedelta

load_dotenv()  # take environment variables from .env.

BASE_DIR = Path(__file__).resolve().parent.parent

# Secret key
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    SECRET_KEY = ''.join(random.choice(string.ascii_lowercase) for i in range(32))

# Debug
DEBUG = str2bool(os.environ.get('DEBUG'))
ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://localhost:5085',
    'http://127.0.0.1:8000',
    'http://127.0.0.1:5085'
]

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Applications
INSTALLED_APPS = [
    'jazzmin',
    'admin_soft.apps.AdminSoftDashboardConfig',
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Serve UI pages
    "apps.pages",
    "apps.dyn_dt",
    "apps.dyn_api",
    "apps.charts",

    # Custom apps
    "apps.users",
    "apps.orders",
    # "apps.jwks"  # không bắt buộc, chỉ thêm nếu muốn Django load như app đầy đủ

    # DRF
    'rest_framework',
    'rest_framework.authtoken',

    # JWT
    'rest_framework_simplejwt.token_blacklist',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.common.middleware.ApiResponseMiddleware",
]

ROOT_URLCONF = "config.urls"

HOME_TEMPLATES = os.path.join(BASE_DIR, 'templates')

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [HOME_TEMPLATES],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
DB_ENGINE   = os.getenv('DB_ENGINE', None)
DB_USERNAME = os.getenv('DB_USERNAME', None)
DB_PASS     = os.getenv('DB_PASS', None)
DB_HOST     = os.getenv('DB_HOST', None)
DB_PORT     = os.getenv('DB_PORT', None)
DB_NAME     = os.getenv('DB_NAME', None)

if DB_ENGINE and DB_NAME and DB_USERNAME:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.' + DB_ENGINE,
            'NAME': DB_NAME,
            'USER': DB_USERNAME,
            'PASSWORD': DB_PASS,
            'HOST': DB_HOST,
            'PORT': DB_PORT,
        },
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_REDIRECT_URL = '/'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Dynamic settings
DYNAMIC_DATATB = {
    'product': "apps.pages.models.Product",
}
DYNAMIC_API = {
    'product': "apps.pages.models.Product",
}

# === JWT RS256 ===
KEYS_DIR = BASE_DIR / "keys"
with open(KEYS_DIR / "private.pem", "r") as f:
    PRIVATE_KEY = f.read()
with open(KEYS_DIR / "public.pem", "r") as f:
    PUBLIC_KEY = f.read()

SIMPLE_JWT = {
    "ALGORITHM": "RS256",
    "SIGNING_KEY": PRIVATE_KEY,
    "VERIFYING_KEY": PUBLIC_KEY,
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ISSUER": os.getenv("JWT_ISSUER", "https://auth.example.com"),
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    # "EXCEPTION_HANDLER": "apps.common.utils.exception_handler.custom_exception_handler"
}

# === Odoo Config ===
ODOO_SERVER_URL = os.getenv("ODOO_SERVER_URL", "https://btmherp.baotinmanhhai.vn")
ODOO_DB = os.getenv("ODOO_DB", "btmh_erp")
ODOO_USERNAME = os.getenv("ODOO_USERNAME", "adminbtmh")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "Btmh@2025#!")
ODOO_API_KEY = os.getenv("ODOO_API_KEY", "Btmh@2025#!")
ODOO_ADMIN_UID = os.getenv("ODOO_ADMIN_UID", 6)
# Nếu bạn có custom User model trong apps/users/models.py
AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = [
    "apps.users.backends.EmailOrUsernameBackend",  # cho phép login bằng email hoặc username
    "django.contrib.auth.backends.ModelBackend",   # backend mặc định
]

INTERNAL_API_BASE = os.getenv('INTERNAL_API_BASE', default='http://192.168.0.223:8096')
STORE_URL_FS01=os.getenv('STORE_URL_FS01',default='http://192.168.104.21:5085')

TYGIA_API_BASE_URL = os.getenv('TYGIA_API_BASE_URL', default='https://tygia.baotinmanhhai.vn/api')
TYGIA_API_TOKEN = os.getenv('TYGIA_API_TOKEN', default='eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiIs')