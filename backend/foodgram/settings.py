import os
from pathlib import Path

from django.core.management.utils import get_random_secret_key

from dotenv import load_dotenv

load_dotenv()

PAGE_SIZE = 6

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", get_random_secret_key())

if not SECRET_KEY:
    SECRET_KEY = get_random_secret_key()

DEBUG = os.getenv('DEBUG', 'False') == 'True'


# ALLOWED_HOSTS = ['89.169.172.126', 'localhost', '127.0.0.1', 'foodgram.webhop.me', '*']

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1, localhost').split(', ')

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "djoser",
    "drf_yasg",
    "django_filters",
    "users.apps.UsersConfig",
    "api.apps.ApiConfig",
    "recipes.apps.RecipesConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "foodgram.urls"

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

WSGI_APPLICATION = "foodgram.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", default="django.db.backends.postgresql"),
        "NAME": os.getenv("DB_NAME", default="postgres"),
        "USER": os.getenv("POSTGRES_USER", default="foodgram_user"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", default="foodgram_password"),
        "HOST": os.getenv("DB_HOST", default="db"),
        "PORT": os.getenv("DB_PORT", default="5432"),
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": ("django.contrib.auth.password_validation."
                 "UserAttributeSimilarityValidator"),
    },
    {
        "NAME": ("django.contrib.auth.password_validation."
                 "MinimumLengthValidator"),
    },
    {
        "NAME": ("django.contrib.auth.password_validation."
                 "CommonPasswordValidator"),
    },
    {
        "NAME": ("django.contrib.auth.password_validation."
                 "NumericPasswordValidator"),
    },
]


LANGUAGE_CODE = "ru-RU"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = "/static/"

# STATIC_ROOT = BASE_DIR / "collected_static"

STATIC_ROOT = os.path.join(BASE_DIR, "static")
# STATIC_ROOT = BASE_DIR.joinpath('static')

MEDIA_URL = "/media/"

MEDIA_ROOT = "/app/media"

# MEDIA_ROOT = BASE_DIR.joinpath('media')

AUTH_USER_MODEL = "users.FoodgramUser"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    "SEARCH_PARAM": "name",
    "DEFAULT_PAGINATION_CLASS": "api.pagination.LimitPagination",
    "PAGE_SIZE": PAGE_SIZE,
}

DJOSER = {
    "LOGIN_FIELD": "email",
    "HIDE_USERS": False,
    "SERIALIZERS": {
        "user": "api.serializers.FoodgramUserSerializer",
        "current_user": "api.serializers.FoodgramUserSerializer",
    },
    "PERMISSIONS": {
        "user": ["rest_framework.permissions.IsAuthenticatedOrReadOnly"],
        "user_list": ["rest_framework.permissions.AllowAny"],
    },
}
