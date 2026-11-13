import re  # re нужна для строгой проверки записи даты перед преобразованием в объект date.
from django import forms  # forms предоставляет безопасную обработку POST и HTML-виджеты.
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm  # Используем готовые формы входа и создания пользователя с хешированием пароля.
from django.utils import timezone  # localdate даёт сегодняшнюю дату в часовом поясе проекта.
from .models import Application, Course, User  # Формы будут создавать и проверять объекты этих моделей.
class RegistrationForm(UserCreationForm):  # Наследование сохраняет проверку совпадения паролей и безопасный save.
    password1 = forms.CharField(label="Пароль", min_length=8, max_length=128, strip=False, widget=forms.PasswordInput(attrs={"minlength": 8, "autocomplete": "new-password"}))  # strip=False сохраняет пробелы пароля, а браузер проверяет минимальную длину.
    password2 = forms.CharField(label="Повторите пароль", strip=False, widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))  # Повтор защищает от случайной опечатки при регистрации.
    class Meta:  # Настраиваем поля унаследованной формы.
        model = User  # Форма связана с нашей моделью пользователя.
        fields = ["username", "full_name", "phone", "email"]  # is_staff намеренно отсутствует: роль нельзя передать из браузера.
        widgets = {  # HTML-атрибуты дают пользователю ранние подсказки до отправки на сервер.
            "username": forms.TextInput(attrs={"pattern": "[A-Za-z0-9]{6,50}", "minlength": 6, "autocomplete": "username"}),  # Браузер принимает только латиницу и цифры от шести символов.
            "full_name": forms.TextInput(attrs={"pattern": "[А-Яа-яЁё]+( [А-Яа-яЁё]+)*", "autocomplete": "name"}),  # Повторяем формат ФИО для немедленной проверки браузером.
            "phone": forms.TextInput(attrs={"pattern": r"8\([0-9]{3}\)[0-9]{3}-[0-9]{2}-[0-9]{2}", "placeholder": "8(999)123-45-67", "autocomplete": "tel"}),  # Подсказываем обязательный формат телефона.
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),  # input type=email включает встроенную браузерную проверку адреса.
        }  # Закрываем словарь виджетов.
    def clean_username(self):  # Django вызывает clean_<имя> после базовой проверки соответствующего поля.
        username = self.cleaned_data["username"]  # Получаем уже очищенный логин; обычные поля CharField обрезают крайние пробелы.
        if User.objects.filter(username__iexact=username).exists():  # __iexact ищет совпадение без учёта регистра; exists не загружает весь объект.
            raise forms.ValidationError("Этот логин уже занят.")  # Ошибка будет привязана к полю логина, а не превратится в сбой сервера.
        return username  # Возвращённое значение попадёт в cleaned_data и затем в модель.
class LoginForm(AuthenticationForm):  # Готовая форма безопасно вызывает authenticate и не раскрывает, существует ли логин.
    username = forms.CharField(label="Логин", max_length=50, widget=forms.TextInput(attrs={"autocomplete": "username"}))  # У входа нет ограничения minlength=6: экзаменационный Admin состоит из пяти букв.
    password = forms.CharField(label="Пароль", strip=False, widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}))  # Поле скрывает ввод и передаёт пароль без обрезания пробелов.
class ApplicationForm(forms.ModelForm):  # ModelForm проверяет поля и умеет создать объект заявки.
    start_date = forms.DateField(label="Дата начала обучения", input_formats=["%d.%m.%Y"], widget=forms.TextInput(attrs={"placeholder": "ДД.ММ.ГГГГ", "pattern": r"[0-9]{2}\.[0-9]{2}\.[0-9]{4}", "inputmode": "numeric"}))  # Принимаем только привычную запись даты; DateField дополнительно отвергает 31 февраля.
    class Meta:  # Выбираем редактируемую модель и разрешённые поля.
        model = Application  # Сохранять будем объект Application.
        fields = ["course", "start_date", "payment_method"]  # Владелец и статус не берутся из POST: их устанавливает сервер.
        widgets = {"payment_method": forms.RadioSelect}  # Два способа оплаты отображаются радиокнопками.
    def __init__(self, *args, **kwargs):  # Переопределяем конструктор, чтобы актуальные курсы читались при каждом открытии формы.
        super().__init__(*args, **kwargs)  # Сначала стандартный ModelForm создаёт все поля.
        self.fields["course"].queryset = Course.objects.filter(is_active=True).order_by("id")  # Закрытые курсы нельзя выбрать даже поддельным POST.
        self.fields["course"].label = "Курс"  # Заменяем техническую подпись поля на русскую.
    def clean_start_date(self):  # Добавляем правило к базовой проверке календарной даты.
        raw = self.data.get("start_date", "")  # Читаем исходную строку, чтобы проверить ведущие нули и разделители.
        if not re.fullmatch(r"[0-9]{2}\.[0-9]{2}\.[0-9]{4}", raw):  # fullmatch требует ровно ДД.ММ.ГГГГ, а не часть строки.
            raise forms.ValidationError("Введите дату строго в формате ДД.ММ.ГГГГ.")  # Выводим понятную ошибку непосредственно под датой.
        value = self.cleaned_data["start_date"]  # После DateField здесь уже объект datetime.date.
        if value < timezone.localdate():  # Прошедшая дата не подходит для начала нового обучения.
            raise forms.ValidationError("Дата начала не может быть в прошлом.")  # Возвращаем форму с ошибкой без сохранения заявки.
        return value  # Корректная дата передаётся дальше в модель.
class ReviewForm(forms.ModelForm):  # Отдельная форма не позволяет вместе с отзывом изменить курс или статус.
    review_text = forms.CharField(label="Ваш отзыв", max_length=2000, widget=forms.Textarea(attrs={"rows": 4, "placeholder": "Что вам понравилось в обучении?"}))  # Обязательный текст ограничен 2000 символами и очищается от крайних пробелов.
    class Meta:  # Указываем единственное разрешённое поле модели.
        model = Application  # Отзыв хранится в записи заявки.
        fields = ["review_text"]  # Остальные поля пользователь через эту форму не редактирует.
class StatusForm(forms.ModelForm):  # Администратор получает отдельную форму с проверкой допустимых статусов.
    class Meta:  # Настройка модели и полей административной формы.
        model = Application  # Меняем существующую заявку, переданную как instance.
        fields = ["status"]  # Через административный POST разрешена только смена статуса.
    def clean_status(self):  # Проверяем порядок движения по статусам на сервере.
        value = self.cleaned_data["status"]  # К этому моменту Django уже проверил, что код входит в choices.
        transitions = {"new": {"new", "studying"}, "studying": {"studying", "completed"}, "completed": {"completed"}}  # Можно оставить текущий статус или перейти на один шаг вперёд; назад нельзя.
        if value not in transitions[self.instance.status]:  # self.instance — заявка, загруженная сервером из БД, а не данные браузера.
            raise forms.ValidationError("Статусы меняются по порядку: Новая → Идет обучение → Обучение завершено.")  # Объясняем причину отказа вместо молчаливого сброса.
        return value  # Допустимый статус готов к сохранению.
