"""
Django settings for web project.

Generated by 'django-admin startproject' using Django 2.0.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""
import hashlib
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'i7r2tyl572bx2xa-5(6s*x#pcq-)y9bxk(%ro++lz9)&@t46nj'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mobile_res',
    'web_res',
    'map',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'sslserver',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'web.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), ],
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

WSGI_APPLICATION = 'web.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'sismoide',
        'USER': 'sismoide',
        'PASSWORD': 'sismoide123',
        'HOST': 'localhost',
        'PORT': '',
    }
}
#
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        # 'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'web.authentication.TokenAuthentication',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.ScopedRateThrottle',
        'rest_framework.throttling.AnonRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'reports': '20/day',  # todo: change to 1 per minute in production
        'events': '20/day',
        'mobile-read': '8/minute',
        'anon': '12/minute',
    }
}

NONCE_EXPIRATION_TIME = 60 * 10  # in seconds
HASH_CLASS = hashlib.sha256  # have to implement '.hexdigest()' method.
MOBILE_PATH_PREFIX = 'mobile'
WEB_PATH_PREFIX = 'web'
MAP_PATH_PREFIX = 'map'

CORS_ORIGIN_ALLOW_ALL = True

QUADRANT_LONG_DELTA = 0.054  # ~5km west-east center of Chile
QUADRANT_LAT_DELTA = 0.045  # ~5km north-south center of Chile

CHILE_MAX_LAT = -17.5  # zona más al norte de chile
CHILE_MIN_LAT = -56  # cabo de hornos

CHILE_MAX_LONG = - 67  # zona mas al este de Chile
CHILE_MIN_LONG = -109.546933  # isla de pascua

REPORT_AGGREGATION_SLICE_DELTA_TIME = 5  # in minutes

from pathlib import Path

QUAKEML_DIR = os.path.join(Path.home(), 'QuakeML')

# sistema de puntos para usuarios moviles
MOBILE_USER_POINTS_REPORT_SUBMIT = 1
MOBILE_USER_POINTS_INTENSITY_UPDATE = 2

"""
son 5km oeste-este centro
(-33.389726, -70.548273)
(-33.389720, -70.494241)
= delta_longitud = 0.054°

son 5km norte-sur centro
(-33.381341, -70.536420)
(-33.426430, -70.536419)
= delta_lat = 0.045°
"""
