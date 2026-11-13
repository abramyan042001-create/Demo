from pathlib import Path  # Path собирает пути одинаково в Windows, Linux и macOS.
import os  # os.environ позволяет передать секретный ключ снаружи, не меняя файл.
BASE_DIR = Path(__file__).resolve().parent.parent  # __file__ — этот файл; два parent поднимают нас в корень Demo.
from django.core.management.utils import get_random_secret_key  # Генератор создаёт криптографически случайный секретный ключ.
_secret_file = BASE_DIR / ".local_secret"  # Секрет хранится только на этом компьютере; файл исключён из Git.
if not os.environ.get("DJANGO_SECRET_KEY") and not _secret_file.exists():  # Создаём ключ лишь при первом запуске, если он не передан через окружение.
    try:  # Если два процесса запустятся одновременно, только один должен создать файл.
        with _secret_file.open("x", encoding="utf-8") as secret_handle:  # Режим x запрещает перезаписывать уже созданный секрет.
            secret_handle.write(get_random_secret_key())  # Записываем случайный ключ, не показывая его в терминале или репозитории.
        _secret_file.chmod(0o600)  # На POSIX разрешаем чтение и запись только владельцу файла.
    except FileExistsError:  # Другой процесс уже успел создать ключ до открытия файла.
        pass  # Используем ключ из существующего файла, не меняя действующие сессии.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY") or _secret_file.read_text(encoding="utf-8")  # Сначала выбираем ключ окружения, иначе постоянный локальный ключ.
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"  # В локальной подготовке включены подробные ошибки; значение 0 выключает их.
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "testserver"]  # Принимаем обращения к локальному серверу и от встроенного тестового клиента.
INSTALLED_APPS = [  # Здесь перечислены приложения, чьи модели и команды должен загрузить Django.
    "django.contrib.auth",  # Готовые пользователи, проверка паролей и права доступа.
    "django.contrib.contenttypes",  # Служебный справочник типов моделей, необходимый системе прав.
    "django.contrib.sessions",  # Хранение состояния входа между запросами.
    "django.contrib.messages",  # Одноразовые сообщения вроде «Заявка создана».
    "django.contrib.staticfiles",  # Поиск локальных CSS, JavaScript и изображений.
    "portal",  # Наше приложение с пользователями, курсами, заявками и страницами.
]  # Закрываем список установленных приложений.
MIDDLEWARE = [  # Middleware обрабатывают запрос по очереди до попадания во view.
    "django.middleware.security.SecurityMiddleware",  # Добавляет базовые защитные HTTP-заголовки.
    "django.contrib.sessions.middleware.SessionMiddleware",  # Загружает сессию по cookie браузера.
    "django.middleware.common.CommonMiddleware",  # Выполняет общую обработку URL и ответов.
    "django.middleware.csrf.CsrfViewMiddleware",  # Отклоняет POST без правильного CSRF-токена.
    "django.contrib.auth.middleware.AuthenticationMiddleware",  # Добавляет request.user на основании сессии.
    "django.contrib.messages.middleware.MessageMiddleware",  # Передаёт одноразовые сообщения следующей странице.
    "django.middleware.clickjacking.XFrameOptionsMiddleware",  # Запрещает чужому сайту встраивать наши страницы во фрейм.
]  # Порядок важен: пользователь определяется после загрузки сессии.
ROOT_URLCONF = "config.urls"  # Главная таблица соответствия URL и обработчиков лежит в config/urls.py.
TEMPLATES = [{  # Описываем единственный используемый движок HTML-шаблонов.
    "BACKEND": "django.template.backends.django.DjangoTemplates",  # Выбираем встроенный шаблонизатор Django.
    "DIRS": [BASE_DIR / "templates"],  # Общие шаблоны ищутся в папке templates корня проекта.
    "APP_DIRS": True,  # Разрешаем также поиск шаблонов внутри установленных приложений.
    "OPTIONS": {"context_processors": [  # Эти функции автоматически добавляют общие переменные шаблонам.
        "django.template.context_processors.request",  # Позволяет читать request и текущий URL в шаблоне.
        "django.contrib.auth.context_processors.auth",  # Делает user и perms доступными в HTML.
        "django.contrib.messages.context_processors.messages",  # Делает список messages доступным в HTML.
    ]},  # Закрываем список функций и словарь опций.
}]  # Закрываем настройки шаблонов.
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}  # SQLite хранит БД в одном файле; отдельный сервер не требуется.
AUTH_USER_MODEL = "portal.User"  # Используем свою модель, наследующую безопасные механизмы AbstractUser.
AUTH_PASSWORD_VALIDATORS = [{"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}}]  # Требование задания: пароль не короче восьми символов.
LANGUAGE_CODE = "ru-ru"  # Встроенные ошибки и элементы форм выводятся на русском языке.
TIME_ZONE = "Asia/Yekaterinburg"  # Часовой пояс проекта для отображения времени и проверки сегодняшней даты.
USE_I18N = True  # Включаем систему переводов Django.
USE_TZ = True  # В базе время хранится с учётом часовых поясов; Django преобразует его при отображении.
STATIC_URL = "static/"  # URL-префикс для локальных стилей, скриптов и картинок.
STATICFILES_DIRS = [BASE_DIR / "static"]  # Папка, из которой runserver отдаёт учебные статические ресурсы.
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"  # Первичный ключ id создаётся как большое автоматически растущее число.
LOGIN_URL = "login"  # Неавторизованных пользователей декоратор login_required направляет на страницу входа.
SESSION_COOKIE_HTTPONLY = True  # JavaScript не может прочитать cookie с идентификатором сессии.
SESSION_COOKIE_SAMESITE = "Lax"  # Ограничиваем отправку cookie при переходах с посторонних сайтов.
