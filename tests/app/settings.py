from __future__ import unicode_literals

import os

INSTALLED_APPS = [
    "wagtailvideos",
    "tests.app",
    "taggit",
    "modelcluster",
    "wagtail",
    "wagtail.admin",
    "wagtail.users",
    "wagtail.sites",
    "wagtail.snippets",
    "wagtail.images",
    "wagtail.documents",
    "wagtail_modeladmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
]

SECRET_KEY = "not a secret"

ROOT_URLCONF = "tests.app.urls"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}

WAGTAIL_SITE_NAME = "Wagtail Videos"
WAGTAILADMIN_BASE_URL = "http://localhost:8080"

DEBUG = True

USE_TZ = True
TIME_ZONE = "Australia/Hobart"

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "DIRS": ["tests/templates"],
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DEFAULT_FILE_STORAGE = "tests.storage.RemoteStorage"

STATIC_ROOT = os.path.join(os.path.dirname(__file__), "static")
STATIC_URL = "/static/"

MEDIA_ROOT = os.path.join(os.path.dirname(__file__), "media")
MEDIA_URL = "/media/"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
