from pathlib import Path  # Path позволяет собирать пути к файлам без ручных слешей Windows или Linux.
from django.core.management.utils import get_random_secret_key  # Готовая функция создаёт случайный ключ для подписи служебных данных Django.
BASE_DIR = Path(__file__).resolve().parent.parent  # Два parent поднимают нас из config/settings.py в корень проекта.
key_file = BASE_DIR / ".local_secret"  # Ключ хранится локально; этот файл исключён из Git.
if not key_file.exists():  # При первом запуске файла с ключом ещё нет.
    key_file.write_text(get_random_secret_key())  # Создаём ключ один раз, а не записываем общий секрет в публичный код.
SECRET_KEY = key_file.read_text()  # Повторно используем тот же ключ, чтобы вход не сбрасывался при каждом запуске.
DEBUG = True  # В учебном проекте включены подробные сообщения об ошибках.
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "testserver"]  # Разрешаем локальный браузер и тестовый клиент Django.
INSTALLED_APPS = [  # Перечисляем приложения, которые должны работать в проекте.
    "django.contrib.auth",  # Готовые пользователи, роли и проверка паролей.
    "django.contrib.contenttypes",  # Служебная таблица типов моделей для системы прав.
    "django.contrib.sessions",  # Хранение состояния «пользователь вошёл».
    "django.contrib.messages",  # Уведомления после отправки форм.
    "django.contrib.staticfiles",  # Подключение CSS, JavaScript и изображений.
    "portal",  # Наши модели, формы и страницы.
]  # Закрываем список приложений.
MIDDLEWARE = [  # Эти обработчики выполняются до view и после него.
    "django.middleware.security.SecurityMiddleware",  # Добавляет базовые защитные заголовки.
    "django.contrib.sessions.middleware.SessionMiddleware",  # Загружает сессию пользователя.
    "django.middleware.common.CommonMiddleware",  # Обрабатывает общие правила HTTP и адресов.
    "django.middleware.csrf.CsrfViewMiddleware",  # Проверяет защитный токен POST-форм.
    "django.contrib.auth.middleware.AuthenticationMiddleware",  # По сессии создаёт request.user.
    "django.contrib.messages.middleware.MessageMiddleware",  # Даёт доступ к уведомлениям messages.
]  # Сессия должна загружаться раньше, чем определяется пользователь.
ROOT_URLCONF = "config.urls"  # С этого файла Django начинает поиск нужного URL.
TEMPLATES = [{  # Настраиваем один движок HTML-шаблонов.
    "BACKEND": "django.template.backends.django.DjangoTemplates",  # Используем обычный шаблонизатор Django.
    "DIRS": [BASE_DIR / "templates"],  # Наши HTML-файлы находятся в папке templates.
    "APP_DIRS": True,  # Django также может искать шаблоны внутри приложений.
    "OPTIONS": {"context_processors": [  # Эти помощники добавляют общие переменные HTML-шаблонам.
        "django.template.context_processors.request",  # Передаёт текущий request.
        "django.contrib.auth.context_processors.auth",  # Передаёт пользователя user.
        "django.contrib.messages.context_processors.messages",  # Передаёт уведомления messages.
    ]},  # Завершаем список помощников и настройки движка.
}]  # Завершаем настройки шаблонов.
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}  # Одна SQLite-база хранится в файле db.sqlite3.
AUTH_USER_MODEL = "portal.User"  # Выбираем нашу модель пользователя; это нужно задать до первого migrate.
AUTH_PASSWORD_VALIDATORS = [{"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}}]  # Готовая проверка требует пароль не короче восьми символов.
LANGUAGE_CODE = "ru-ru"  # Готовые подписи и ошибки Django будут на русском языке.
TIME_ZONE = "Asia/Yekaterinburg"  # Указываем часовой пояс проекта.
USE_I18N = True  # Разрешаем встроенные переводы Django.
USE_TZ = True  # Включаем поддержку часовых поясов при работе с датой и временем.
STATIC_URL = "static/"  # URL-префикс для стилей, скриптов и картинок.
STATICFILES_DIRS = [BASE_DIR / "static"]  # Папка, где лежат наши статические файлы.
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"  # Поле id по умолчанию — автоматически растущее целое число.
LOGIN_URL = "login"  # login_required направляет гостя на маршрут с этим именем.
