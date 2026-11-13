from django import forms  # Подключаем формы: они показывают поля и проверяют введённые значения.
from django.contrib.auth.forms import UserCreationForm  # Готовая регистрация умеет сравнивать пароли и безопасно сохранять их хеш.
from .models import Application, STATUSES, User  # Берём наши модели и список статусов из соседнего файла models.py.
class RegisterForm(UserCreationForm):  # Наследуем готовую форму, чтобы не писать сохранение пароля с нуля.
    username = forms.RegexField(label="Логин", regex=r"\A[A-Za-z0-9]{6,50}\Z", max_length=50, min_length=6, widget=forms.TextInput(attrs={"pattern": "[A-Za-z0-9]{6,50}"}))  # Разрешаем 6–50 латинских букв и цифр; pattern проверяет это также в браузере.
    full_name = forms.RegexField(label="ФИО", regex=r"\A[А-Яа-яЁё]+(?: [А-Яа-яЁё]+)*\Z", max_length=150, widget=forms.TextInput(attrs={"pattern": "[А-Яа-яЁё]+( [А-Яа-яЁё]+)*"}))  # Разрешаем кириллицу и пробел между словами; Ё и ё указаны отдельно.
    phone = forms.RegexField(label="Телефон", regex=r"\A8\([0-9]{3}\)[0-9]{3}-[0-9]{2}-[0-9]{2}\Z", widget=forms.TextInput(attrs={"placeholder": "8(999)123-45-67", "pattern": r"8\([0-9]{3}\)[0-9]{3}-[0-9]{2}-[0-9]{2}"}))  # Проверяем точный формат телефона; обратная косая черта делает скобки обычными символами.
    email = forms.EmailField(label="Email")  # Обязательное поле проверяет формат адреса и выводит в HTML input type=email.
    password1 = forms.CharField(label="Пароль", min_length=8, strip=False, widget=forms.PasswordInput(attrs={"minlength": 8}))  # Пароль не короче восьми символов; strip=False не удаляет пробелы из пароля.
    password2 = forms.CharField(label="Повторите пароль", strip=False, widget=forms.PasswordInput)  # Повтор нужен для проверки опечатки; сравнение уже есть в родительской форме.
    class Meta:  # Здесь говорим ModelForm, с какой таблицей и полями работать.
        model = User  # Результатом регистрации будет новый объект User.
        fields = ["username", "full_name", "phone", "email"]  # Административных полей нет: посетитель не может сам назначить себе права.
class ApplicationForm(forms.ModelForm):  # Эта форма умеет создать заявку по проверенным полям.
    start_date = forms.DateField(label="Дата начала обучения", input_formats=["%d.%m.%Y"], widget=forms.TextInput(attrs={"placeholder": "ДД.ММ.ГГГГ", "pattern": r"[0-9]{2}\.[0-9]{2}\.[0-9]{4}"}))  # Человек вводит ДД.ММ.ГГГГ; DateField проверяет существование даты, например отвергает 31 февраля.
    class Meta:  # Настраиваем связь формы с моделью заявки.
        model = Application  # Сохранять будем объект Application.
        fields = ["course", "start_date", "payment_method"]  # Владельца и статус пользователь не вводит: их задаст сервер.
        labels = {"course": "Курс"}  # Заменяем техническое название поля course русской подписью.
        widgets = {"payment_method": forms.RadioSelect}  # Вместо списка способы оплаты показываются двумя радиокнопками.
    def clean_start_date(self):  # Django вызывает этот метод, когда базовая проверка даты уже прошла.
        text = self.data["start_date"]  # Берём исходную строку, чтобы убедиться в наличии ведущих нулей.
        value = self.cleaned_data["start_date"]  # Берём уже проверенный объект даты, полученный от DateField.
        if text != value.strftime("%d.%m.%Y"):  # Сравниваем введённую строку с точным форматом: 1.1.2027 не равно 01.01.2027.
            raise forms.ValidationError("Введите дату в формате ДД.ММ.ГГГГ.")  # Django покажет эту ошибку под полем, а не сохранит заявку.
        return value  # Возвращаем корректную дату обратно в данные формы.
class ReviewForm(forms.ModelForm):  # Отдельная форма позволяет менять отзыв, не затрагивая владельца и статус.
    review_text = forms.CharField(label="Ваш отзыв", max_length=2000, widget=forms.Textarea(attrs={"rows": 3}))  # Отзыв обязателен, ограничен 2000 символами и вводится в многострочное поле.
    class Meta:  # Настраиваем единственное редактируемое поле.
        model = Application  # Отзыв хранится прямо в заявке.
        fields = ["review_text"]  # Другие поля заявки эта форма не принимает.
class StatusForm(forms.Form):  # Простая форма проверит статус, присланный администратором.
    status = forms.ChoiceField(choices=STATUSES)  # ChoiceField отвергнет любое значение, которого нет в нашем списке статусов.
