from datetime import timedelta  # Будущая дата в тестах не устаревает при смене календарного дня.
from io import StringIO  # Перехватываем вывод seed, чтобы тестовый отчёт не засорялся служебным текстом.
from unittest.mock import patch  # Подменяем только интерактивный ввод пароля для автоматического теста команды.
from django.core.management import call_command  # Запускаем seed тем же механизмом, что и manage.py.
from django.db import IntegrityError, transaction  # Проверяем реальные ограничения SQLite и откат нарушения.
from django.test import Client, TestCase  # TestCase создаёт отдельную тестовую БД, Client отправляет запросы без сетевого сервера.
from django.urls import reverse  # Получаем URL по имени маршрута, не дублируя строки путей в тестах.
from django.utils import timezone  # Вычисляем сегодняшнюю дату в том же часовом поясе, что и приложение.
from .forms import ApplicationForm, RegistrationForm  # Прямые тесты форм проверяют сервер независимо от браузерной валидации.
from .models import Application, Course, User  # Читаем фактически сохранённые записи для проверки результатов запросов.
class PortalTests(TestCase):  # Все тесты этого класса выполняются изолированно от пользовательской БД.
    @classmethod  # setUpTestData вызывается один раз для начальных данных всего класса.
    def setUpTestData(cls):  # cls позволяет сохранять подготовленные объекты как атрибуты класса.
        cls.password = "OnlyForAutomatedTests42"  # Это открытая тестовая строка, она не используется для реального администратора.
        with patch("portal.management.commands.seed.getpass", return_value=cls.password):  # Автотест не должен ждать ввод в терминале.
            call_command("seed", stdout=StringIO())  # Создаём три курса и тестового Admin в отдельной тестовой БД.
        cls.admin = User.objects.get(username="Admin")  # Сохраняем ссылку на администратора, созданного настоящей командой.
        cls.student = User.objects.create_user(username="student123", password=cls.password, full_name="Иванов Иван", phone="8(999)123-45-67", email="one@example.ru")  # Первый пользователь будет владельцем заявки.
        cls.other = User.objects.create_user(username="student456", password=cls.password, full_name="Петров Пётр", phone="8(999)222-33-44", email="two@example.ru")  # Второй пользователь нужен для проверки изоляции данных.
        cls.course = Course.objects.first()  # Берём настоящий курс из начального справочника.
    def setUp(self):  # Эта подготовка выполняется перед каждым тестом отдельно.
        self.client.force_login(self.student)  # Большинство проверок выполняются от имени обычного пользователя.
        self.future = timezone.localdate() + timedelta(days=30)  # Дата заявки всегда остаётся в будущем относительно запуска тестов.
        self.item = Application.objects.create(user=self.student, course=self.course, start_date=self.future, payment_method="cash")  # В каждом тесте создаём собственную начальную заявку.
    def registration_data(self, **changes):  # Вспомогательный метод сокращает повторение исходных полей регистрации.
        data = dict(username="newuser123", password1=self.password, password2=self.password, full_name="Сидоров Иван", phone="8(999)123-45-67", email="new@example.ru")  # Корректный набор данных, от которого тесты меняют только одно условие.
        data.update(changes)  # Именованные аргументы заменяют нужное поле для конкретной проверки.
        return data  # Возвращаем новый независимый словарь для очередного запроса.
    def test_registration_hash_and_no_privilege_escalation(self):  # Даже поддельное поле is_staff не должно давать административную роль.
        response = Client().post(reverse("register"), self.registration_data(is_staff="1", is_superuser="1"))  # Гость пытается зарегистрироваться с дополнительными полями прав.
        self.assertRedirects(response, reverse("login"))  # Успешная регистрация заканчивается переходом на вход.
        user = User.objects.get(username="newuser123")  # Проверяем созданную запись непосредственно в БД.
        self.assertFalse(user.is_staff or user.is_superuser)  # Никаких административных привилегий форма не сохранила.
        self.assertNotEqual(user.password, self.password)  # В колонке password нет исходной строки пароля.
        self.assertTrue(user.check_password(self.password))  # При этом проверка хеша правильно узнаёт введённый пароль.
    def test_registration_validation(self):  # Проверяем все ключевые правила формы таблицей некорректных примеров.
        cases = [("username", "short"), ("username", "русский123"), ("username", "test_user"), ("full_name", "John Smith"), ("full_name", "Иван2"), ("phone", "+79991234567"), ("phone", "8(999)1234567"), ("email", "wrong"), ("password1", "short"), ("password2", "different")]  # Каждая пара нарушает одно конкретное правило задания.
        for field, value in cases:  # Выполняем проверки всех примеров независимо друг от друга.
            with self.subTest(field=field, value=value):  # В отчёте видно, какое именно поле и значение сломало тест.
                form = RegistrationForm(self.registration_data(**{field: value}))  # Создаём связанную форму без участия браузера.
                self.assertFalse(form.is_valid())  # Сервер обязан отклонить каждое некорректное значение.
    def test_duplicate_login_case_insensitive(self):  # Запрещаем повторение логина, в том числе с другим регистром.
        form = RegistrationForm(self.registration_data(username="STUDENT123"))  # Такой логин уже есть в начальных данных как student123.
        self.assertFalse(form.is_valid())  # Проверка формы должна найти совпадение до INSERT.
        self.assertIn("username", form.errors)  # Ошибка привязана именно к полю логина.
    def test_login_error_and_required_link(self):  # Форма входа показывает сообщение и точный текст ссылки на регистрацию.
        response = Client().post(reverse("login"), {"username": "student123", "password": "wrong"})  # Отправляем неправильный пароль от существующего аккаунта.
        self.assertEqual(response.status_code, 200)  # При ошибке входа показывается форма, а не серверный сбой.
        self.assertTrue(response.context["form"].errors)  # Пользователь получает понятное сообщение о неудачном входе.
        self.assertContains(response, "Еще не зарегистрированы? Регистрация")  # Проверяем буквальное требование к тексту ссылки.
    def test_short_admin_login_is_allowed(self):  # Специальный логин Admin короче минимума регистрации, но должен работать.
        response = Client().post(reverse("login"), {"username": "Admin", "password": self.password})  # Проверяем реальную форму входа, а не force_login.
        self.assertRedirects(response, reverse("dashboard"))  # Сервер распознаёт роль и открывает панель администратора.
    def test_guests_redirected(self):  # Личные и административные страницы требуют сессии пользователя.
        guest = Client()  # Новый клиент не имеет cookies авторизованного аккаунта.
        for name in ["applications", "new_application", "dashboard"]:  # Проверяем все три защищённые GET-страницы.
            with self.subTest(route=name):  # Отдельно показываем проблемный маршрут, если защита нарушилась.
                self.assertEqual(guest.get(reverse(name)).status_code, 302)  # Гость должен быть перенаправлен на страницу входа.
    def test_logout_requires_post(self):  # Выход по GET не должен случайно завершать сессию пользователя.
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)  # GET получает «метод не поддерживается».
        self.assertRedirects(self.client.post(reverse("logout")), reverse("login"))  # Корректный POST завершает сессию.
        self.assertEqual(self.client.get(reverse("applications")).status_code, 302)  # После выхода кабинет снова недоступен.
    def test_create_application_ignores_owner_and_status(self):  # Владелец и начальный статус должны назначаться только сервером.
        data = {"course": self.course.pk, "start_date": self.future.strftime("%d.%m.%Y"), "payment_method": "phone_transfer", "user": self.other.pk, "status": "completed"}  # Злоумышленник подменяет дополнительные POST-поля.
        response = self.client.post(reverse("new_application"), data)  # Отправляем обычную форму создания заявки.
        self.assertRedirects(response, reverse("applications"))  # Валидная часть заявки сохраняется успешно.
        item = Application.objects.latest("id")  # Находим новую запись, а не заявку из setUp.
        self.assertEqual((item.user_id, item.status), (self.student.pk, "new"))  # Поддельные владелец и статус не попали в БД.
    def test_application_date_and_payment_validation(self):  # Проверяем невозможные даты, формат, прошлое и запрещённые коды оплаты.
        base = {"course": self.course.pk, "start_date": self.future.strftime("%d.%m.%Y"), "payment_method": "cash"}  # Начальная корректная форма заявки.
        cases = [{"start_date": "31.02.2027"}, {"start_date": "01.01.2020"}, {"start_date": "1.1.2027"}, {"start_date": "2027-01-01"}, {"payment_method": "card"}, {"course": 999999}]  # Данные, которые нельзя принимать даже без браузерных ограничений.
        for changes in cases:  # Каждое нарушение проверяем с остальными правильными полями.
            with self.subTest(changes=changes):  # В отчёте сохраняем проблемный вариант данных.
                self.assertFalse(ApplicationForm(base | changes).is_valid())  # Серверная форма должна отклонять некорректный запрос.
    def test_inactive_course_rejected(self):  # Закрытый курс не должен приниматься ручной отправкой id.
        self.course.is_active = False  # Меняем доступность курса в объекте.
        self.course.save()  # Сохраняем флаг в тестовую БД.
        form = ApplicationForm({"course": self.course.pk, "start_date": self.future.strftime("%d.%m.%Y"), "payment_method": "cash"})  # Подставляем id недоступного курса вручную.
        self.assertFalse(form.is_valid())  # Queryset поля курса проверяет доступность на стороне сервера.
    def test_only_owner_sees_application(self):  # Чужие заявки нельзя получить через собственный список.
        self.client.force_login(self.other)  # Переключаем клиента на второго пользователя.
        response = self.client.get(reverse("applications"))  # Открываем личный кабинет второго аккаунта.
        self.assertEqual(list(response.context["items"]), [])  # SQL-фильтр владельца исключил чужую запись.
        self.assertEqual(self.client.post(reverse("review", args=[self.item.pk]), {"review_text": "Чужой отзыв"}).status_code, 404)  # Подмена id в URL также не даёт доступ к записи.
    def test_review_before_completion_forbidden(self):  # Скрыть форму недостаточно: сервер должен запретить ранний отзыв.
        response = self.client.post(reverse("review", args=[self.item.pk]), {"review_text": "Рано"})  # Вручную отправляем отзыв для новой заявки.
        self.assertEqual(response.status_code, 403)  # Проверка статуса возвращает запрет доступа.
        self.item.refresh_from_db()  # Перечитываем запись, чтобы проверить отсутствие побочного изменения.
        self.assertEqual(self.item.review_text, "")  # Никакой отзыв не сохранился.
    def test_admin_role_required_for_both_endpoints(self):  # Панель и обработчик смены статуса защищаются независимо друг от друга.
        self.assertEqual(self.client.get(reverse("dashboard")).status_code, 403)  # Обычный пользователь не открывает общую панель.
        self.assertEqual(self.client.post(reverse("status", args=[self.item.pk]), {"status": "studying"}).status_code, 403)  # Поддельный POST также не повышает привилегии.
    def test_status_order_and_completed_review(self):  # Полный жизненный цикл доказывает совместимость статусов и отзыва.
        admin = Client()  # Отдельный клиент сохраняет независимую административную сессию.
        admin.force_login(self.admin)  # Входим ролью администратора без повторной проверки пароля в этом тесте.
        admin.post(reverse("status", args=[self.item.pk]), {"status": "completed"})  # Пытаемся пропустить этап обучения.
        self.item.refresh_from_db()  # Загружаем фактический статус из БД.
        self.assertEqual(self.item.status, "new")  # Недопустимый скачок должен оставить исходный статус.
        for status in ["studying", "completed"]:  # Проходим два разрешённых перехода по порядку.
            self.assertRedirects(admin.post(reverse("status", args=[self.item.pk]), {"status": status}), reverse("dashboard"))  # Каждый POST завершается успешным перенаправлением.
        response = self.client.post(reverse("review", args=[self.item.pk]), {"review_text": "<script>alert(1)</script>"})  # Текст похож на HTML-атаку, но должен храниться и выводиться как обычный текст.
        self.assertRedirects(response, reverse("applications"))  # После завершения отзыв действительно разрешён.
        self.assertContains(self.client.get(reverse("applications")), "&lt;script&gt;alert(1)&lt;/script&gt;")  # Автоэкранирование шаблона предотвращает выполнение JavaScript из отзыва.
        admin.post(reverse("status", args=[self.item.pk]), {"status": "new"})  # Проверяем попытку отката статуса после оставленного отзыва.
        self.item.refresh_from_db()  # Считываем итоговое состояние.
        self.assertEqual(self.item.status, "completed")  # Возврат назад запрещён, условие хранения отзыва не нарушено.
    def test_review_required_and_length(self):  # Форма отзыва должна объяснять пустой и слишком длинный текст.
        self.item.status = "completed"  # Для проверки текста предварительно разрешаем сам отзыв.
        self.item.save()  # Сохраняем завершённое обучение в БД.
        for text in ["   ", "я" * 2001]:  # Пробелы очищаются; второй вариант превышает предел на один символ.
            with self.subTest(length=len(text)):  # В отчёте различаем пустой и слишком длинный отзыв.
                response = self.client.post(reverse("review", args=[self.item.pk]), {"review_text": text})  # Отправляем неподходящий текст.
                self.assertEqual(response.status_code, 400)  # Невалидный текст отображается в форме с ошибкой, а не сохраняется.
    def test_admin_filter_pagination_and_feedback(self):  # Панель должна фильтровать, разбивать записи по страницам и сообщать результат.
        self.client.force_login(self.admin)  # Для административных функций нужна соответствующая роль.
        for _ in range(6):  # Добавляем достаточно записей, чтобы появились две страницы по пять заявок.
            Application.objects.create(user=self.other, course=self.course, start_date=self.future, payment_method="cash")  # Все дополнительные заявки имеют статус new.
        response = self.client.get(reverse("dashboard"), {"status": "new", "page": "1"})  # Применяем фильтр и запрашиваем первую страницу.
        self.assertEqual(len(response.context["rows"]), 5)  # Размер страницы строго соответствует настройке панели.
        self.assertTrue(response.context["page"].has_next())  # Оставшиеся записи доступны через пагинацию.
        self.assertContains(response, "status=new&amp;page=2")  # Ссылка следующей страницы сохраняет фильтр.
        empty = self.client.get(reverse("dashboard"), {"status": "completed"})  # Завершённых заявок в этом тесте ещё нет.
        self.assertEqual(len(empty.context["rows"]), 0)  # Фильтр действительно действует на запрос к БД.
        result = self.client.post(reverse("status", args=[self.item.pk]), {"status": "studying"}, follow=True)  # Меняем статус и открываем страницу перенаправления.
        self.assertContains(result, "Статус обновлён.")  # Одноразовое сообщение подтверждает успешное сохранение.
    def test_csrf_rejects_untrusted_post(self):  # Обычный тестовый Client отключает CSRF, поэтому эту проверку включаем явно.
        strict = Client(enforce_csrf_checks=True)  # Этот клиент воспроизводит проверку токена настоящим middleware.
        response = strict.post(reverse("login"), {"username": "Admin", "password": self.password})  # Отправляем POST без предварительно полученного CSRF-токена.
        self.assertEqual(response.status_code, 403)  # Сервер отклоняет запрос, даже несмотря на правильный пароль.
    def test_database_constraints(self):  # Проверяем, что ограничения существуют в самой SQLite, а не только в формах.
        for changes in [{"status": "hacked"}, {"payment_method": "card"}, {"review_text": "Ранний отзыв"}]:  # Три попытки нарушить правила непосредственным UPDATE.
            with self.subTest(changes=changes):  # Отдельно фиксируем каждое ограничение.
                with self.assertRaises(IntegrityError), transaction.atomic():  # Вложенная транзакция откатывает запрещённый UPDATE и не ломает последующие проверки.
                    Application.objects.filter(pk=self.item.pk).update(**changes)  # Обходим формы намеренно: последним барьером должна стать БД.
    def test_seed_is_repeatable_without_password_reset(self):  # Повторный seed не должен дублировать курсы или менять пароль администратора.
        before = self.admin.password  # Запоминаем исходный хеш тестового администратора.
        with patch("portal.management.commands.seed.getpass") as prompt:  # Следим, запрашивается ли пароль повторно.
            call_command("seed", stdout=StringIO())  # Выполняем команду второй раз на той же базе.
            prompt.assert_not_called()  # Существующий аккаунт не должен требовать нового пароля.
        self.admin.refresh_from_db()  # Перечитываем сохранённые поля после команды.
        self.assertEqual(self.admin.password, before)  # Хеш остался прежним, действующие учётные данные не сброшены.
        self.assertEqual(Course.objects.count(), 3)  # В справочнике по-прежнему ровно три курса.
