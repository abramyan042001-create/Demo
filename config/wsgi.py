import os  # Импортируем работу с переменными окружения.
from django.core.wsgi import get_wsgi_application  # Фабрика создаёт WSGI-приложение для совместимого сервера.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # До загрузки приложения указываем его настройки.
application = get_wsgi_application()  # Это объект, которому WSGI-сервер передаёт HTTP-запросы.
