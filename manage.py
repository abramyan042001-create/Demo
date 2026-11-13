import os  # os позволяет задать переменную окружения, из которой Django узнает файл настроек.
import sys  # sys.argv содержит команду из терминала: например, migrate или runserver.
if __name__ == "__main__":  # Запускаем команды только при прямом запуске файла, а не при его импорте.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # Указываем модуль config/settings.py; существующую настройку не перезаписываем.
    from django.core.management import execute_from_command_line  # Импортируем диспетчер команд Django после выбора настроек.
    execute_from_command_line(sys.argv)  # Передаём Django все аргументы терминала; дальше он сам выбирает нужную команду.
