import os
from celery import Celery
from django.conf import settings

# Ustawienie domyślnego modułu ustawień Django dla programu 'celery'.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myshop.settings')

app = Celery('myshop')

# wczytanie konfiguracji z ustawień projektu.
app.config_from_object('django.conf:settings')

# automatyczne wykrywanie zadań asynchronicznych zdefiniowanych w aplikacji.
# Celery będzie szukać pliku tasks.py we wszystkich
# katalogach aplikacji i wczyta zdefiniowane tam zadania asynchroniczne.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)