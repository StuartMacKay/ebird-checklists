"""
Django settings
https://docs.djangoproject.com/en/4.2/topics/settings/

"""
import os
import socket

from django.core.exceptions import ImproperlyConfigured

import environ  # type: ignore

# #######################
#   PROJECT DIRECTORIES
# #######################

CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CONFIG_DIR)
DOWNLOAD_DIR = os.path.join(ROOT_DIR, "data", "downloads")
DATABASE_DIR = os.path.join(ROOT_DIR, "data", "databases")
LOG_DIR = os.path.join(ROOT_DIR, "logs")

# ###############
#   ENVIRONMENT
# ###############

env = environ.Env()

environ.Env.read_env(os.path.join(ROOT_DIR, '.env'))

DEBUG = env.bool("DJANGO_DEBUG", default=True)

# #####################
#   APPS & MIDDLEWARE
# #####################

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "debug_toolbar",
    "ebird.checklists",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

# ##############
#   WEB SERVER
# ##############

ROOT_URLCONF = "demo.urls"

WSGI_APPLICATION = "demo.wsgi.application"

if DEBUG:
    # From cookiecutter-django: We need to configure an IP address to
    # allow connections from, but in Docker we can't use 127.0.0.1 since
    # this runs in a container but we want to access the django_debug_toolbar
    # from our browser outside of the container.
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + [
        "127.0.0.1",
        "10.0.2.2",
    ]

# ############
#   DATABASE
# ############

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

DB_NAME = env.str("DB_NAME", default="checklists")

DATABASES = {
    "default": env.db_url(default=f"sqlite:///{DATABASE_DIR}/{DB_NAME}.sqlite3")
}

# ############
#   SECURITY
# ############

SECRET_KEY = env.str("DJANGO_SECRET_KEY", default="<not-set>")

# #############
#   TEMPLATES
# #############

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

# ########################
#   INTERNATIONALIZATION
# ########################

LANGUAGE_CODE = "en"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ################
#   STATIC FILES
# ################

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

STATIC_URL = "/static/"

# ###########
#   LOGGING
# ###########

LOG_LEVEL = env.str("DJANGO_LOG_LEVEL", default="INFO")

if LOG_LEVEL not in ("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"):
    raise ImproperlyConfigured("Unknown level for logging: " + LOG_LEVEL)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.json.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
        "simple": {
            "format": "{asctime} [{levelname}] {message}",
            "style": "{",
            'datefmt': '%Y-%m-%d %H:%M',
        },
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "json",
            "filename": os.path.join(LOG_DIR, "ebird-checklists.log"),
            "maxBytes": 1024 * 1024,
            "backupCount": 10,
        }
    },
    "loggers": {
        "django": {
            "level": "ERROR",
            "handlers": ["stdout"],
            "propagate": False,
        },
        "": {
            "handlers": ["stdout", "file"],
            "level": LOG_LEVEL,
        },
    },
}

# #####################
#   DJANGO EXTENSIONS
# #####################

SHELL_PLUS = "ipython"

# ####################
#   EBIRD CHECKLISTS
# ####################

EBIRD_API_KEY = env.str("EBIRD_API_KEY")
