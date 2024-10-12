import os
from pathlib import Path

from dotenv import load_dotenv
from split_settings.tools import include

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

DEBUG = os.environ.get("DEBUG", False) == "True"

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(",")

# Приложения: config/components/applications.py
include(
    "components/applications.py",
)

# Промежуточное ПО: config/components/middlewares.py
include(
    "components/middlewares.py",
)

ROOT_URLCONF = "config.urls"

# Шаблоны: config/components/templates.py
include(
    "components/templates.py",
)

WSGI_APPLICATION = "config.wsgi.application"


# База данных: config/components/database.py
include(
    "components/database.py",
)


# Валидация паролей: config/components/password_validation.py
include(
    "components/password_validation.py",
)


# Интернационализация: config/components/internationalization.py
include(
    "components/internationalization.py",
)


# Статические файлы (CSS, JavaScript, Images)
STATIC_URL = "static/"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
