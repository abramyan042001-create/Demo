from django.contrib.auth.models import AbstractUser  # Наследуем готовую модель с хешированием паролей и флагом is_staff.
from django.db import models  # models предоставляет классы таблиц, полей, индексов и ограничений.
from django.db.models.functions import Lower  # Lower переводит логин в нижний регистр для проверки уникальности без учёта регистра.
from .validators import login_validator, name_validator, phone_validator  # Берём единые правила полей из соседнего файла.
class User(AbstractUser):  # Класс описывает таблицу пользователей; is_staff выступает ролью администратора в БД.
    username = models.CharField("Логин", max_length=50, unique=True, validators=[login_validator])  # Переопределяем логин: ограничиваем длину, формат и запрещаем дубликаты.
    full_name = models.CharField("ФИО", max_length=150, validators=[name_validator])  # Храним полное имя пользователя отдельным обязательным полем.
    phone = models.CharField("Телефон", max_length=16, validators=[phone_validator])  # Телефон — текст, чтобы скобки и дефисы не потерялись.
    email = models.EmailField("Email", max_length=120)  # EmailField проверяет корректный формат адреса при валидации формы.
    class Meta:  # Вложенный класс задаёт дополнительные правила таблицы.
        constraints = [models.UniqueConstraint(Lower("username"), name="unique_login_casefold")]  # Ivanov12 и ivanov12 считаются одним логином на уровне БД.
class Course(models.Model):  # Отдельная таблица справочника курсов устраняет повторение названия в каждой заявке.
    title = models.CharField("Название", max_length=200, unique=True)  # Каждый курс имеет уникальное читаемое название.
    is_active = models.BooleanField("Открыт для записи", default=True)  # Закрытый курс остаётся в истории, но недоступен для новых заявок.
    def __str__(self):  # Django вызывает этот метод, когда нужно показать объект человеку.
        return self.title  # Поэтому выпадающий список отображает название, а не Course object.
class Application(models.Model):  # Одна запись этой таблицы — одна заявка одного пользователя на один курс.
    class Status(models.TextChoices):  # Перечисление хранит устойчивые коды и отдельные русские подписи.
        NEW = "new", "Новая"  # Код new хранится в БД; «Новая» показывается в интерфейсе.
        STUDYING = "studying", "Идет обучение"  # Второй допустимый статус означает, что обучение уже началось.
        COMPLETED = "completed", "Обучение завершено"  # Только при этом статусе разрешён отзыв.
    class Payment(models.TextChoices):  # Второе перечисление задаёт два разрешённых способа оплаты.
        CASH = "cash", "Наличными"  # Первый способ — наличные.
        TRANSFER = "phone_transfer", "Переводом по номеру телефона"  # Второй способ — перевод по номеру телефона.
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="applications")  # Внешний ключ связывает заявку с владельцем; PROTECT запрещает удалить пользователя с заявками.
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="applications")  # Связь многие-к-одному со справочником курсов; историю нельзя случайно удалить.
    start_date = models.DateField("Дата начала обучения")  # DateField хранит настоящую дату, а не произвольную строку.
    payment_method = models.CharField("Способ оплаты", max_length=20, choices=Payment.choices)  # choices задаёт варианты поля формы и валидацию.
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.NEW)  # Новая заявка всегда получает начальный статус на сервере.
    review_text = models.TextField("Отзыв", max_length=2000, blank=True, default="")  # Необязательный отзыв храним в самой заявке: один текст на одно обучение.
    created_at = models.DateTimeField("Создана", auto_now_add=True)  # Время первой записи выставляется автоматически и не меняется при обновлении.
    class Meta:  # Общие настройки хранения и выборки заявок.
        ordering = ["-created_at", "-id"]  # Минус означает убывание: самые свежие заявки идут первыми.
        indexes = [models.Index(fields=["user", "-created_at"], name="app_user_created"), models.Index(fields=["status"], name="app_status")]  # Индексы ускоряют список владельца и фильтр администратора.
        constraints = [  # Эти проверки выполняет сама БД даже при записи в обход формы.
            models.CheckConstraint(condition=models.Q(status__in=["new", "studying", "completed"]), name="valid_status"),  # Запрещаем неизвестный код статуса.
            models.CheckConstraint(condition=models.Q(payment_method__in=["cash", "phone_transfer"]), name="valid_payment"),  # Запрещаем неизвестный способ оплаты.
            models.CheckConstraint(condition=models.Q(review_text="") | models.Q(status="completed"), name="review_after_completion"),  # Непустой отзыв допустим только у завершённого обучения.
        ]  # Закрываем список ограничений таблицы заявок.
