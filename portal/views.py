from django.contrib import messages  # Сообщения объясняют результат действия после перехода на другую страницу.
from django.contrib.auth import login, logout  # Готовые функции создают и завершают сессию пользователя.
from django.contrib.auth.decorators import login_required  # Этот декоратор не пускает гостя на личные страницы.
from django.contrib.auth.forms import AuthenticationForm  # Готовая форма проверяет существующего пользователя и пароль.
from django.core.exceptions import PermissionDenied  # Это исключение возвращает HTTP 403: действие запрещено.
from django.core.paginator import Paginator  # Paginator разбивает длинный список на несколько страниц.
from django.shortcuts import get_object_or_404, redirect, render  # Эти помощники получают запись, перенаправляют и показывают HTML.
from django.views.decorators.http import require_POST  # Запрещаем изменять данные простым открытием ссылки через GET.
from .forms import ApplicationForm, RegisterForm, ReviewForm, StatusForm  # Подключаем формы нашего приложения.
from .models import Application, STATUSES  # Подключаем таблицу заявок и варианты статусов.

def register_view(request):  # Django вызывает функцию, когда открыт адрес регистрации.
    form = RegisterForm(request.POST if request.method == "POST" else None)  # При POST связываем форму с отправленными полями; при GET показываем пустую.
    if request.method == "POST" and form.is_valid():  # Проверяем, что форму отправили и все поля прошли серверную проверку.
        form.save()  # Родительский UserCreationForm сохраняет пользователя с хешем пароля.
        return redirect("login")  # После регистрации предлагаем войти; браузер выполняет новый GET-запрос.
    return render(request, "portal/form.html", {"form": form, "title": "Регистрация", "button": "Зарегистрироваться", "kind": "register"})  # Показываем форму; ошибки остаются рядом с её полями.

def login_view(request):  # Одна форма входа обслуживает пользователя и администратора.
    form = AuthenticationForm(request, data=request.POST if request.method == "POST" else None)  # Передаём готовой форме запрос и введённые логин/пароль.
    form.fields["username"].label = "Логин"  # Делаем подпись стандартной формы понятной и соответствующей заданию.
    if request.method == "POST" and form.is_valid():  # При неверных данных не создаём сессию, а ниже показываем ошибки формы.
        login(request, form.get_user())  # Запоминаем вошедшего пользователя в сессии; пароль в cookie не помещается.
        if request.user.is_staff:  # Проверяем флаг администратора, который хранится в БД.
            return redirect("dashboard")  # Администратора отправляем в общую панель заявок.
        return redirect("applications")  # Обычного пользователя отправляем к его заявкам.
    return render(request, "portal/form.html", {"form": form, "title": "Вход", "button": "Войти", "kind": "login"})  # Возвращаем пустую форму или форму с ошибкой входа.

@login_required  # До входа в эту функцию проверяем, что пользователь авторизован.
@require_POST  # Выход разрешён только через POST-форму с CSRF-токеном.
def logout_view(request):  # Эта функция завершает текущую сессию.
    logout(request)  # Django удаляет данные входа из сессии.
    return redirect("login")  # После выхода открываем страницу входа.

@login_required  # Гостю нельзя просматривать личный кабинет.
def applications_view(request):  # Показываем заявки того, кто вошёл в аккаунт.
    items = Application.objects.filter(user=request.user)  # SQL-фильтр выбирает только собственные заявки, а не скрывает чужие в HTML.
    return render(request, "portal/applications.html", {"items": items})  # Передаём список в шаблон под именем items.

@login_required  # Чтобы создать заявку, нужно сначала войти.
def new_application_view(request):  # Обрабатываем создание новой заявки.
    form = ApplicationForm(request.POST if request.method == "POST" else None)  # GET показывает поля; POST приносит данные для проверки.
    if request.method == "POST" and form.is_valid():  # Ничего не сохраняем до проверки курса, даты и оплаты.
        item = form.save(commit=False)  # Получаем объект в памяти: commit=False означает «пока не записывай в БД».
        item.user = request.user  # Назначаем владельцем того, кто вошёл, а не пользователя из поддельного POST.
        item.save()  # Теперь сохраняем заявку; статус new возьмётся из default в модели.
        messages.success(request, "Заявка создана.")  # Сохраняем короткое уведомление для следующей страницы.
        return redirect("applications")  # Возвращаемся к списку; обновление страницы не повторит предыдущий POST.
    return render(request, "portal/form.html", {"form": form, "title": "Новая заявка", "button": "Отправить заявку"})  # При ошибках снова показываем заполненную форму.

@login_required  # Отзыв может отправить только вошедший пользователь.
@require_POST  # Запись текста отзыва выполняется через POST, а не открытие ссылки.
def review_view(request, pk):  # pk приходит из URL и означает номер конкретной заявки.
    item = get_object_or_404(Application, pk=pk, user=request.user)  # Ищем запись сразу с проверкой владельца: чужой номер даст 404.
    if item.status != "completed":  # Даже если отправить форму вручную, сервер проверит завершение обучения.
        raise PermissionDenied("Отзыв доступен после завершения обучения.")  # Останавливаем обработку и возвращаем запрет 403.
    form = ReviewForm(request.POST, instance=item)  # instance связывает форму с существующей заявкой, чтобы обновить её, а не создать новую.
    if form.is_valid():  # Проверяем непустой текст и длину до 2000 символов.
        form.save()  # Сохраняем только разрешённое поле отзыва.
        messages.success(request, "Отзыв сохранён.")  # Объясняем пользователю результат сохранения.
        return redirect("applications")  # После успешного POST открываем список заявок.
    return render(request, "portal/form.html", {"form": form, "title": "Отзыв", "button": "Сохранить"})  # Некорректный текст не теряется: показываем его с ошибкой формы.

@login_required  # Панель тоже требует авторизованной сессии.
def dashboard_view(request):  # Показываем администратору заявки всех пользователей.
    if not request.user.is_staff:  # Вход в аккаунт сам по себе не даёт административную роль.
        raise PermissionDenied("Этот раздел только для администратора.")  # Обычный пользователь получает 403.
    items = Application.objects.all()  # Администратору разрешён список всех заявок.
    status = request.GET.get("status", "")  # Читаем фильтр из адреса; если параметра нет, используем пустую строку.
    if status:  # Непустой фильтр означает, что выбран конкретный статус.
        items = items.filter(status=status)  # ORM безопасно подставляет значение в запрос к БД.
    page = Paginator(items, 5).get_page(request.GET.get("page"))  # Делим результат на страницы по пять записей и выбираем нужную.
    return render(request, "portal/dashboard.html", {"page": page, "statuses": STATUSES, "selected": status})  # Передаём страницу записей, варианты статусов и текущий фильтр.

@login_required  # Отдельно защищаем обработчик записи статуса авторизацией.
@require_POST  # Менять состояние через GET нельзя.
def status_view(request, pk):  # pk — id заявки, для которой нажали кнопку «Сохранить».
    if not request.user.is_staff:  # Проверяем роль здесь тоже: злоумышленник может не открывать панель, а сразу прислать POST.
        raise PermissionDenied("Менять статус может только администратор.")  # Без нужной роли запрещаем изменение.
    item = get_object_or_404(Application, pk=pk)  # Загружаем нужную заявку или возвращаем 404.
    form = StatusForm(request.POST)  # Проверяем, что прислан один из трёх известных статусов.
    if form.is_valid():  # cleaned_data используем только после успешной проверки формы.
        new_status = form.cleaned_data["status"]  # Здесь уже проверенное значение, а не сырой текст из браузера.
        item.status = new_status  # Записываем выбранный допустимый статус в объект заявки.
        item.save()  # Сохраняем изменение в базе данных.
        messages.success(request, "Статус обновлён.")  # После перенаправления появится подтверждение сохранения.
    else:  # Обрабатываем неизвестный статус из поддельного запроса.
        messages.error(request, "Выбран неизвестный статус.")  # Возвращаем понятную ошибку вместо записи случайного значения.
    return redirect("dashboard")  # После обработки открываем обновлённую панель.
