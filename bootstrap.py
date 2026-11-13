import argparse  # argparse разбирает флаги командной строки и автоматически создаёт справку --help.
from pathlib import Path  # Path нужен для путей, содержащих пробелы и кириллицу.
import subprocess  # subprocess запускает pip и manage.py отдельными процессами.
import sys  # sys.executable показывает Python, которым запущен этот файл.
import venv  # Стандартный модуль Python создаёт изолированное окружение без скачивания из интернета.
ROOT = Path(__file__).resolve().parent  # Рабочая папка определяется расположением файла, а не местом запуска терминала.
parser = argparse.ArgumentParser(description="Локальная установка и запуск Корочки.есть.")  # Описываем назначение программы в справке.
parser.add_argument("--prepare", action="store_true", help="Заранее скачать офлайн-пакеты; только этот режим использует интернет.")  # Этот флаг нужен для подготовки GitHub-копии до экзамена.
parser.add_argument("--no-run", action="store_true", help="Установить зависимости и подготовить БД без запуска сервера.")  # Отдельный режим удобен для проверки установки.
args = parser.parse_args()  # Проверяем аргументы пользователя и получаем объект с флагами.
if sys.version_info < (3, 10):  # Django 5.2 требует Python не ниже 3.10; рекомендуем 3.12.
    raise SystemExit("Нужен Python 3.10 или новее. Для подготовки рекомендуется Python 3.12.")  # Прерываем работу с понятным сообщением вместо ошибки импорта.
if args.prepare:  # Интернет используется только при явном запросе предварительной подготовки.
    subprocess.run([sys.executable, "-m", "pip", "download", "--only-binary=:all:", "--dest", str(ROOT / "offline_packages"), "-r", str(ROOT / "requirements-offline.txt")], cwd=ROOT, check=True)  # Скачиваем фиксированные wheel-пакеты, не устанавливая их в системный Python.
    print("Пакеты сохранены. Скопируйте всю папку проекта на компьютер для экзамена.")  # Говорим, что именно нужно перенести офлайн.
    raise SystemExit(0)  # Режим подготовки на этом заканчивается и не запускает приложение.
if not list((ROOT / "offline_packages").glob("*.whl")):  # Простая копия из GitHub не содержит бинарные пакеты; полный ZIP уже содержит их.
    raise SystemExit("Нет wheel-пакетов. Возьмите полный офлайн-архив либо заранее выполните python bootstrap.py --prepare при наличии интернета.")  # Не пытаемся незаметно скачать зависимости во время экзамена.
environment = ROOT / ".venv"  # Каждому компьютеру нужен собственный каталог виртуального окружения.
python = environment / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")  # Путь к исполняемому Python отличается в Windows и Linux/macOS.
if not python.exists():  # Готовое окружение можно использовать повторно.
    venv.EnvBuilder(with_pip=True).create(environment)  # Создаём окружение и встроенный pip средствами установленного Python.
commands = [  # Выполним подготовительные команды строго по порядку.
    [str(python), "-m", "pip", "install", "--no-index", "--find-links", str(ROOT / "offline_packages"), "-r", str(ROOT / "requirements-offline.txt")],  # --no-index запрещает pip обращаться к интернету.
    [str(python), "manage.py", "migrate", "--noinput"],  # Применяем схему из версионированных миграций к локальной SQLite.
    [str(python), "manage.py", "seed"],  # Создаём курсы и при первом запуске запрашиваем пароль администратора из задания.
    [str(python), "manage.py", "check"],  # Проверяем настройки и целостность конфигурации Django до запуска сервера.
]  # Закрываем перечень подготовительных команд.
for command in commands:  # Ошибка предыдущего шага не должна позволять перейти к следующему.
    subprocess.run(command, cwd=ROOT, check=True)  # Список аргументов корректно передаёт пути с пробелами; shell=True не используется.
if not args.no_run:  # Без специального флага сразу открываем локальный HTTP-сервер.
    print("Откройте в браузере http://127.0.0.1:8000/ . Остановка сервера: Ctrl+C.")  # Адрес относится к этому компьютеру и работает без интернета.
    subprocess.run([str(python), "manage.py", "runserver", "127.0.0.1:8000"], cwd=ROOT, check=True)  # Сервер разработки слушает только локальный адрес.
