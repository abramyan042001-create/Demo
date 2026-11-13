import re  # Регулярное выражение удалит временные CSRF-токены из статических снимков.
from datetime import date  # date создаёт фиксированную учебную дату для макетов.
from pathlib import Path  # Path безопасно формирует пути выходных HTML-файлов.
from django.conf import settings  # BASE_DIR указывает корень проекта независимо от текущей папки терминала.
from django.contrib.auth.models import AnonymousUser  # Объект гостя нужен для правильного меню публичных макетов.
from django.core.management.base import BaseCommand  # Команда будет доступна через python manage.py export_mobile.
from django.core.paginator import Paginator  # Готовим демонстрационную пагинацию администратора без чтения реальных заявок.
from django.template.loader import render_to_string  # Используем тот же HTML-шаблон, что и рабочий портал.
from django.test import RequestFactory  # Создаём запрос в памяти, без запуска сервера и обращения к интернету.
from portal.forms import ApplicationForm, LoginForm, RegistrationForm, StatusForm  # Берём настоящие формы для визуального соответствия рабочим страницам.
from portal.models import Application, Course, User  # Несохранённые объекты дадут учебные данные без персональной информации из БД.
class Command(BaseCommand):  # Django найдёт эту команду по имени файла.
    help = "Экспортировать пять статических мобильных макетов 390×844 без пользовательских данных."  # Описание доступно в справке manage.py.
    def handle(self, *args, **options):  # Стандартная точка выполнения команды.
        out = Path(settings.BASE_DIR) / "mobile"  # Отдельная папка соответствует требованию отдельного HTML на каждую страницу.
        out.mkdir(exist_ok=True)  # Повторный запуск использует существующую папку.
        student = User(id=100, username="student123", full_name="Иванов Иван", phone="8(999)123-45-67", email="student@example.ru")  # Объект остаётся только в памяти: save не вызывается.
        admin = User(id=101, username="Admin", full_name="Администратор", is_staff=True)  # Макет админки получает меню роли администратора без пароля и сессии.
        course = Course(id=1, title="Основы веб-дизайна")  # Демонстрационный курс не читается из пользовательских записей.
        item = Application(id=1, user=student, course=course, start_date=date(2027, 5, 1), payment_method="cash", status="completed", review_text="Спасибо за понятные практические занятия!")  # Учебная заявка показывает доступный отзыв.
        page = Paginator([item], 5).get_page(1)  # В макете панели достаточно одной демонстрационной заявки.
        specs = [  # Каждая запись описывает имя файла, шаблон, роль и контекст страницы.
            ("login", "form", AnonymousUser(), {"form": LoginForm(), "title": "Вход в аккаунт", "button": "Войти", "kind": "login"}),  # Публичный макет авторизации.
            ("register", "form", AnonymousUser(), {"form": RegistrationForm(), "title": "Регистрация", "button": "Зарегистрироваться", "kind": "register"}),  # Публичный макет регистрации со всеми полями.
            ("applications", "applications", student, {"items": [item]}),  # Макет кабинета со своей заявкой и формой отзыва.
            ("new-application", "form", student, {"form": ApplicationForm(), "title": "Новая заявка", "button": "Отправить заявку", "kind": "application"}),  # Макет формирования заявки с реальным справочником курсов.
            ("admin", "dashboard", admin, {"rows": [(item, StatusForm(instance=item))], "page": page, "statuses": Application.Status.choices, "selected": ""}),  # Макет панели со сменой статуса и фильтром.
        ]  # Завершаем перечень пяти обязательных страниц.
        for name, template, user, context in specs:  # Экспортируем страницы по очереди из общей системы шаблонов.
            request = RequestFactory().get("/")  # Подготавливаем фиктивный GET-запрос для контекстных процессоров.
            request.user = user  # Выбранная роль управляет навигацией и видимостью разделов.
            html = render_to_string(f"portal/{template}.html", context, request=request)  # Генерируем готовый HTML с учебными данными.
            html = html.replace('/static/', '../static/')  # Относительные пути позволяют открыть HTML двойным щелчком без Django-сервера.
            links = {"/": "login.html", "/login/": "login.html", "/register/": "register.html", "/applications/": "applications.html", "/applications/new/": "new-application.html", "/admin/": "admin.html"}  # Статические макеты могут переходить друг к другу без локального сервера.
            for source, target in links.items():  # Обновляем только href, оставляя неработающие POST-формы явно заблокированными.
                html = html.replace(f'href="{source}"', f'href="{target}"')  # Меню макета открывает соседний HTML, а не несуществующий абсолютный путь file://.
            html = re.sub(r'<input[^>]*name="csrfmiddlewaretoken"[^>]*>', '<!-- CSRF удалён: это статический макет без отправки данных. -->', html)  # Не сохраняем временные токены в репозитории.
            html = html.replace('<form ', '<form onsubmit="return false" ')  # Макеты показывают внешний вид, но ничего не отправляют и не меняют.
            css = (Path(settings.BASE_DIR) / "static/css/style.css").read_text(encoding="utf-8")  # Берём те же мобильные правила, что использует рабочий сайт.
            mobile_css = css.split("@media (max-width: 760px) {")[1].split("} /* Завершаем мобильные")[0].split("\n", 1)[1]  # Извлекаем тело мобильного блока без внешней media query, чтобы макет оставался мобильным на широком мониторе.
            html = html.replace('</head>', '<style>body { width:390px; min-height:844px; margin:0 auto; } /* Холст 390×844. */\n' + mobile_css + '</style></head>')  # Фиксируем размер холста и применяем мобильные правила независимо от ширины окна.
            html = html.replace('<main id="main"', '<p style="text-align:center;font-size:12px">Макет 390×844 · данные учебные · формы не отправляются</p><main id="main"')  # Отличаем статическую демонстрацию от рабочего приложения.
            lines = [line + ' <!-- Статический элемент интерфейса; исходная логика и пояснения находятся в templates/. -->' if line.strip() and not line.lstrip().startswith('<!--') else line for line in html.splitlines()]  # Комментируем непустые строки экспортированной разметки и указываем читаемый первоисточник.
            (out / f"{name}.html").write_text("\n".join(lines) + "\n", encoding="utf-8")  # Сохраняем отдельный UTF-8 HTML для каждой обязательной страницы.
        self.stdout.write(self.style.SUCCESS("Созданы пять макетов в mobile/. Откройте их при ширине окна 390 px."))  # Сообщаем путь и условие точной мобильной проверки.
