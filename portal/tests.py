from django.test import Client, TestCase  # Client проверяет обработчики без браузера, TestCase создаёт отдельную БД для тестов.
from .forms import ApplicationForm, RegisterForm  # Используем настоящие формы проекта.
from .models import Application, Course, User  # По моделям проверяем фактически сохранённые данные.
class PortalTests(TestCase):  # Проверки запускаются командой manage.py test; для изучения основ их читать необязательно.
    def setUp(self):  # Этот метод заново подготавливает данные перед каждым тестом.
        self.password = "OnlyForTests123"  # Открытая строка только для тестов, не пароль настоящего администратора.
        self.user = User.objects.create_user(username="student1", password=self.password, full_name="Иван Иванов", phone="8(999)123-45-67", email="test@example.ru")  # Обычный пользователь будет владельцем заявки.
        self.admin = User.objects.create_user(username="Admin", password=self.password, is_staff=True)  # Отдельный аккаунт получает роль администратора.
        self.course = Course.objects.create(title="Основы веб-дизайна")  # Один курс нужен для тестовых заявок.
        self.item = Application.objects.create(user=self.user, course=self.course, start_date="2027-05-01", payment_method="cash")  # Новая заявка использует default new.
        self.client.force_login(self.user)  # По умолчанию запросы выполняются от обычного пользователя.
    def registration(self):  # Этот помощник возвращает корректные поля регистрации.
        return {"username": "student2", "full_name": "Пётр Петров", "phone": "8(999)123-45-67", "email": "two@example.ru", "password1": self.password, "password2": self.password}  # Каждый вызов создаёт новый словарь, независимый от предыдущего теста.
    def test_registration(self):  # Проверяем создание пользователя, хеш пароля и отсутствие поддельных прав.
        data = self.registration()  # Получаем правильные данные.
        data["is_staff"] = "1"  # Злоумышленник добавляет поле, которого нет в нашей форме.
        self.assertRedirects(Client().post("/register/", data), "/login/")  # Гость после регистрации должен перейти на вход.
        user = User.objects.get(username="student2")  # Читаем созданный аккаунт прямо из тестовой БД.
        self.assertFalse(user.is_staff)  # Дополнительное POST-поле не дало административную роль.
        self.assertNotEqual(user.password, self.password)  # Сохранённый пароль не равен открытому тексту.
        self.assertTrue(user.check_password(self.password))  # При этом проверка хеша узнаёт правильный пароль.
    def test_invalid_registration(self):  # Проверяем, что сервер отклоняет некорректные поля независимо от браузера.
        cases = {"username": "кириллица", "full_name": "John", "phone": "+79991234567", "email": "wrong", "password1": "123", "password2": "other"}  # Каждый пример нарушает правило одного поля.
        for field, value in cases.items():  # Берём по одной паре поле — некорректное значение.
            data = self.registration()  # Остальные поля будут корректными.
            data[field] = value  # Меняем ровно одно поле.
            self.assertFalse(RegisterForm(data).is_valid(), field)  # Форма должна вернуть False, иначе отчёт покажет имя проблемного поля.
    def test_duplicate_login(self):  # Нельзя повторно зарегистрировать существующий логин.
        data = self.registration()  # Начинаем с корректного набора полей.
        data["username"] = "student1"  # Такой аккаунт уже есть в setUp.
        self.assertFalse(RegisterForm(data).is_valid())  # Унаследованная форма проверяет занятость логина.
    def test_login(self):  # Проверяем ошибку пароля, текст ссылки и короткий логин Admin.
        client = Client()  # Новый клиент пока не вошёл.
        response = client.post("/login/", {"username": "student1", "password": "wrong"})  # Отправляем неправильный пароль.
        self.assertTrue(response.context["form"].errors)  # Вместо входа форма должна показать ошибку.
        self.assertContains(response, "Еще не зарегистрированы? Регистрация")  # Проверяем точную подпись ссылки из задания.
        self.assertRedirects(client.post("/login/", {"username": "Admin", "password": self.password}), "/admin/")  # Admin из пяти букв успешно входит в административную панель.
    def test_guest_and_logout(self):  # Личный кабинет закрыт для гостя, а выход работает только через POST.
        self.assertEqual(Client().get("/applications/").status_code, 302)  # Гостю возвращается перенаправление на вход.
        self.assertEqual(self.client.get("/logout/").status_code, 405)  # GET-ссылка не завершает сессию.
        self.client.post("/logout/")  # Отправка формы завершает вход.
        self.assertEqual(self.client.get("/applications/").status_code, 302)  # Кабинет после выхода снова недоступен.
    def test_new_application(self):  # Сервер должен сам выбрать владельца и начальный статус заявки.
        data = {"course": self.course.pk, "start_date": "01.05.2027", "payment_method": "cash", "user": self.admin.pk, "status": "completed"}  # Дополнительные поля пытаются подменить владельца и статус.
        self.assertRedirects(self.client.post("/applications/new/", data), "/applications/")  # Корректная часть заявки сохраняется.
        item = Application.objects.latest("id")  # Получаем последнюю созданную запись.
        self.assertEqual((item.user_id, item.status), (self.user.pk, "new"))  # Владелец взят из сессии, статус остался new.
    def test_invalid_application(self):  # Проверяем дату, формат, оплату и курс.
        data = {"course": self.course.pk, "start_date": "01.05.2027", "payment_method": "cash"}  # Это корректная заявка до изменения одного поля.
        for changes in [{"start_date": "31.02.2027"}, {"start_date": "1.5.2027"}, {"payment_method": "card"}, {"course": 999999}]:  # Четыре независимых некорректных варианта.
            self.assertFalse(ApplicationForm(data | changes).is_valid())  # Каждый вариант должен получить серверный отказ.
    def test_owner(self):  # Другому аккаунту нельзя просматривать и комментировать чужую заявку.
        self.client.force_login(self.admin)  # Меняем пользователя клиента; у этого аккаунта собственных заявок нет.
        self.assertEqual(list(self.client.get("/applications/").context["items"]), [])  # Личный список не содержит чужую запись.
        self.assertEqual(self.client.post(f"/applications/{self.item.pk}/review/", {"review_text": "Чужой"}).status_code, 404)  # Подмена id в URL тоже не даёт доступ.
    def test_review(self):  # Проверяем запрет раннего отзыва и безопасный вывод текста после завершения.
        url = f"/applications/{self.item.pk}/review/"  # Адрес отзыва принадлежит нашей тестовой заявке.
        self.assertEqual(self.client.post(url, {"review_text": "Рано"}).status_code, 403)  # На статусе new сервер запрещает отзыв.
        self.item.status = "completed"  # Разрешаем отзыв, закончив обучение.
        self.item.save()  # Сохраняем изменение в тестовой БД.
        self.assertTrue(self.client.post(url, {"review_text": "   "}).context["form"].errors)  # Одни пробелы не считаются содержательным отзывом.
        self.client.post(url, {"review_text": "<script>test</script>"})  # Проверяем текст с HTML-разметкой.
        self.assertContains(self.client.get("/applications/"), "&lt;script&gt;test&lt;/script&gt;")  # Разметка показана как текст, а не исполнена.
    def test_admin_permissions(self):  # Оба административных обработчика должны проверять роль.
        self.assertEqual(self.client.get("/admin/").status_code, 403)  # Обычный пользователь не открывает общую панель.
        self.assertEqual(self.client.post(f"/admin/{self.item.pk}/status/", {"status": "completed"}).status_code, 403)  # Поддельный прямой POST тоже запрещён.
    def test_admin_functions(self):  # Проверяем фильтр, пагинацию и подтверждение смены статуса.
        self.client.force_login(self.admin)  # Входим с ролью администратора.
        for number in range(6):  # Добавляем записи, чтобы понадобилось несколько страниц по пять заявок.
            Application.objects.create(user=self.user, course=self.course, start_date="2027-05-01", payment_method="cash")  # У новых записей статус new.
        response = self.client.get("/admin/?status=new&page=1")  # Запрашиваем первую страницу с фильтром.
        self.assertEqual(len(response.context["page"]), 5)  # На одной странице должно быть пять записей.
        self.assertContains(response, "status=new&amp;page=2")  # Следующая страница сохраняет фильтр.
        self.assertEqual(len(self.client.get("/admin/?status=completed").context["page"]), 0)  # Завершённых заявок пока нет.
        result = self.client.post(f"/admin/{self.item.pk}/status/", {"status": "completed"}, follow=True)  # Официальное условие разрешает администратору выбрать завершённый статус.
        self.assertContains(result, "Статус обновлён.")  # После изменения отображается сообщение.
        self.client.post(f"/admin/{self.item.pk}/status/", {"status": "unknown"})  # Пробуем передать неизвестный код статуса.
        self.item.refresh_from_db()  # Считываем итоговое значение из БД.
        self.assertEqual(self.item.status, "completed")  # Неверный код не перезаписал корректный статус.
    def test_csrf(self):  # Проверяем защиту POST-форм от отправки без токена.
        client = Client(enforce_csrf_checks=True)  # Включаем настоящую CSRF-проверку даже в тестовом клиенте.
        self.assertEqual(client.post("/login/", {}).status_code, 403)  # Запрос без токена должен быть остановлен.
