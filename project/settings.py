"""
Django settings for AYR project.
"""
import os
from pathlib import Path

import dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
dotenv_file = os.path.join(BASE_DIR, ".env")
if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)
SECRET_KEY = os.environ["SECRET_KEY"]

DEBUG = os.environ.get("WEBAPP_DEBUG", "true") == "true"

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "mozilla_django_oidc",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "app",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "mozilla_django_oidc.middleware.SessionRefresh",
]

ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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

WSGI_APPLICATION = "project.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["WEBAPP_DB_NAME"],
        "USER": os.environ["WEBAPP_DB_USER"],
        "PASSWORD": os.environ["WEBAPP_DB_PASSWORD"],
        "HOST": os.environ.get("WEBAPP_DB_HOST", "webapp-db"),
        "PORT": os.environ.get("WEBAPP_DB_PORT", "5432"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}


AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "mozilla_django_oidc.auth.OIDCAuthenticationBackend",
)
KEYCLOACK_BASE_URI = os.environ["KEYCLOACK_BASE_URI"]
KEYCLOACK_REALM_NAME = os.environ["KEYCLOACK_REALM_NAME"]
KEYCLOACK_REALM_BASE_URI = f"{KEYCLOACK_BASE_URI}/realms/{KEYCLOACK_REALM_NAME}"


OIDC_RP_CLIENT_ID = os.environ["OIDC_RP_CLIENT_ID"]
OIDC_RP_CLIENT_SECRET = os.environ["OIDC_RP_CLIENT_SECRET"]

OIDC_RP_SIGN_ALGO = "RS256"
OIDC_OP_JWKS_ENDPOINT = f"{KEYCLOACK_REALM_BASE_URI}/protocol/openid-connect/certs"
OIDC_OP_AUTHORIZATION_ENDPOINT = (
    f"{KEYCLOACK_REALM_BASE_URI}/protocol/openid-connect/auth"
)
OIDC_OP_TOKEN_ENDPOINT = f"{KEYCLOACK_REALM_BASE_URI}/protocol/openid-connect/token"
OIDC_OP_USER_ENDPOINT = f"{KEYCLOACK_REALM_BASE_URI}/protocol/openid-connect/userinfo"
OIDC_OP_LOGOUT_URL_METHOD = "app.auth.provider_logout"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
CSRF_TRUSTED_ORIGINS = [
    "https://keycloak.ayr.labs.zaizicloud.net/",
    "https://webapp.ayr.labs.zaizicloud.net/",
    "https://dev-keycloak-loadbalancer-1788036597.eu-west-2.elb.amazonaws.com",
    "https://dev-loadbalancer-108847439.eu-west-2.elb.amazonaws.com",
    "http://dev-keycloak-loadbalancer-1788036597.eu-west-2.elb.amazonaws.com",
    "http://dev-loadbalancer-108847439.eu-west-2.elb.amazonaws.com",
    "https://keycloak.ayr.labs.zaizicloud.net",
    "https://webapp.ayr.labs.zaizicloud.net",
    "http://keycloak.ayr.labs.zaizicloud.net",
    "http://webapp.ayr.labs.zaizicloud.net",
]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
