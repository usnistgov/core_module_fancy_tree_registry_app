""" Test settings
"""

SECRET_KEY = "fake-key"

INSTALLED_APPS = [
    # Django apps
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    # Local apps
    "core_main_app",
    "core_main_registry_app",
    "core_parser_app",
    "tests",
]

# In-memory test DB
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    },
}

SERVER_URI = "http://example.com"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
CELERYBEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
MONGODB_INDEXING = False
MONGODB_ASYNC_SAVE = False
