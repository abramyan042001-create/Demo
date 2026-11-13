from getpass import getpass  # Позволяет ввести пароль в терминале без отображения символов.
from django.core.management.base import BaseCommand, CommandError  # Основа своей команды и понятная ошибка для терминала.
from portal.models import Course, User  # Подключаем таблицы курсов и пользователей.
class Command(BaseCommand):  # Django ищет в файле seed.py класс с именем Command.
    help = "Создать три курса и администратора."  # Описание появится в справке manage.py help seed.
    def handle(self, *args, **options):  # Этот метод выполнится после команды python manage.py seed.
        titles = ["Основы алгоритмизации и программирования", "Основы веб-дизайна", "Основы проектирования баз данных"]  # Названия трёх курсов из задания.
        for title in titles:  # По очереди берём каждое название.
            Course.objects.get_or_create(title=title)  # Создаём курс только если его ещё нет; повторный запуск не дублирует записи.
        if not User.objects.filter(username="Admin").exists():  # Существующему администратору не меняем пароль повторным запуском.
            password = getpass("Введите пароль администратора из задания: ")  # Пароль вводится локально, а не публикуется в GitHub.
            if len(password) < 8:  # Проверяем минимальную длину до создания пользователя.
                raise CommandError("Нужно не менее 8 символов.")  # Останавливаем команду с объяснением ошибки.
            User.objects.create_user(username="Admin", password=password, is_staff=True, full_name="Администратор", phone="8(900)000-00-00", email="admin@example.ru")  # create_user хеширует пароль; is_staff назначает административную роль.
        self.stdout.write("Курсы и администратор готовы.")  # Сообщаем, что начальные данные подготовлены.
