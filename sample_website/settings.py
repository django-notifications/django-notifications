""" Django notification settings for tests """
# -*- coding: utf-8 -*-
import os
import socket

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SECRET_KEY = "secret_key"  # nosec

DEBUG = True
TESTING = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "test.sqlite3",
    }
}

MIDDLEWARE = (
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sessions",
    "debug_toolbar",
    # As "external" lib
    "notifications",
    # The sample app
    "sample_app",
]

ROOT_URLCONF = "sample_website.urls"
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
STATIC_ROOT = os.path.join(BASE_DIR, "static-files")

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

LOGIN_REDIRECT_URL = "test/"
LOGIN_URL = "/admin/login/"
APPEND_SLASH = True

DJANGO_NOTIFICATIONS_CONFIG = {
    "USE_JSONFIELD": True,
}
USE_TZ = True

ALLOWED_HOSTS = ["*"]

hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]
