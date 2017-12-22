# Import celery.
# Konieczne jest zaimportowanie modułu celery w pliku
# __init__.py projektu, aby mieć pewność,
# że zostanie wczytany podczas uruchamiania Django.
from .celery import app as celery_app