from django.contrib import messages  # Одноразовые сообщения показывают результат действия после перенаправления.
from django.contrib.auth import login, logout  # Стандартные функции создают и удаляют безопасную сессию.
from django.contrib.auth.decorators import login_required  # Декоратор не допускает гостя к личным страницам.
from django.core.exceptions import PermissionDenied  # Исключение превращается в HTTP 403 «нет доступа».
from django.core.paginator import Paginator  # Разбивает длинный список на страницы по заданному размеру.
from django.db import IntegrityError, transaction  # Транзакция и обработка конфликта защищают запись при одновременных запросах.
from django.shortcuts import get_object_or_404, redirect, render  # Получение объекта с 404, перенаправление и рендер HTML.
from django.views.decorators.http import require_POST  # Изменяющие данные обработчики должны принимать только POST.
from .forms import ApplicationForm, LoginForm, RegistrationForm, ReviewForm, StatusForm  # Импортируем наши формы с едиными серверными правилами.
from .models import Application  # Через ORM модели читаем и изменяем заявки, не склеивая SQL вручную.
def register_view(request):  # Функция получает HTTP-запрос и возвращает страницу регистрации или перенаправление.
    form = RegistrationForm(request.POST if request.method == "POST" else None)  # GET создаёт пустую форму; POST связывает её с отправленными полями.
    if request.method == "POST" and form.is_valid():  # Не сохраняем пользователя, пока все поля и оба пароля не проверены.
        try:  # Даже после is_valid конкурентный запрос может успеть занять такой же логин.
            with transaction.atomic():  # При конфликте откатываем только эту операцию создания пользователя.
                form.save()  # UserCreationForm использует set_password: в БД попадёт хеш, а не исходный пароль.
        except IntegrityError:  # Уникальное ограничение БД служит последним рубежом защиты от повторяющегося логина.
            form.add_error("username", "Этот логин уже занят. Выберите другой.")  # Вместо ошибки 500 оставляем заполненную форму с понятным сообщением.
        else:  # Этот блок выполняется только если создание пользователя прошло без исключения.
            messages.success(request, "Регистрация завершена. Теперь войдите.")  # Сохраняем уведомление на следующую страницу.
            return redirect("login")  # POST/Redirect/GET исключает повторную регистрацию при обновлении страницы.
    return render(request, "portal/form.html", {"form": form, "title": "Регистрация", "button": "Зарегистрироваться", "kind": "register"})  # Передаём шаблону форму, подписи и вид страницы.
def login_view(request):  # Вход использует одну страницу для обычного пользователя и администратора.
    form = LoginForm(request=request, data=request.POST if request.method == "POST" else None)  # AuthenticationForm проверяет пароль и активность учётной записи.
    if request.method == "POST" and form.is_valid():  # Только успешная проверка даёт право создать сессию.
        login(request, form.get_user())  # Django меняет идентификатор сессии и запоминает id пользователя.
        return redirect("dashboard" if request.user.is_staff else "applications")  # Роль из БД определяет стартовую страницу; пользовательский next не используется.
    return render(request, "portal/form.html", {"form": form, "title": "Вход в аккаунт", "button": "Войти", "kind": "login"})  # Неверные данные останутся в форме с общим сообщением об ошибке.
@login_required  # До вызова следующей функции проверяем наличие авторизованного пользователя.
@require_POST  # Выход изменяет сессию, поэтому ссылка GET не должна выходить из аккаунта.
def logout_view(request):  # Обработчик выхода получает защищённый CSRF-токеном POST.
    logout(request)  # Удаляем данные текущей сессии, чтобы старый идентификатор больше не давал доступ.
    return redirect("login")  # После выхода возвращаемся к форме авторизации.
@login_required  # Гость не может просматривать личный список заявок.
def applications_view(request):  # Обработчик кабинета пользователя.
    items = Application.objects.filter(user=request.user).select_related("course")  # Фильтр владельца стоит в SQL; select_related получает курс тем же запросом.
    return render(request, "portal/applications.html", {"items": items, "review_form": ReviewForm()})  # Передаём только собственные заявки и пустую форму отзыва.
@login_required  # Для создания заявки необходимо войти в аккаунт.
def new_application_view(request):  # Обработчик формы записи на курс.
    form = ApplicationForm(request.POST if request.method == "POST" else None)  # Различаем показ пустой формы и проверку отправленных данных.
    if request.method == "POST" and form.is_valid():  # Проверяются курс, дата и разрешённый способ оплаты.
        item = form.save(commit=False)  # Создаём объект в памяти, пока без INSERT: ему ещё нужен владелец.
        item.user = request.user  # Владельца берём из сессии; чужой user_id в POST игнорируется.
        item.status = Application.Status.NEW  # Нельзя самостоятельно записаться сразу с завершённым обучением.
        item.save()  # После заполнения обязательных полей выполняем INSERT в БД.
        messages.success(request, "Заявка создана.")  # Сообщаем пользователю, что данные сохранены.
        return redirect("applications")  # Перенаправляем на список; обновление браузера не создаст вторую заявку.
    return render(request, "portal/form.html", {"form": form, "title": "Новая заявка", "button": "Отправить заявку", "kind": "application"})  # При ошибке показываем ту же форму с введёнными данными.
@login_required  # Только вошедший пользователь может отправить отзыв.
@require_POST  # Отзыв записывается только POST-запросом с CSRF-токеном.
def review_view(request, pk):  # pk — целочисленный id заявки из URL.
    with transaction.atomic():  # Проверка статуса и запись отзыва составляют одну операцию.
        item = get_object_or_404(Application.objects.filter(user=request.user), pk=pk)  # Ищем сразу среди собственных заявок; чужой id даёт 404.
        if item.status != Application.Status.COMPLETED:  # Проверяем статус на сервере даже если кто-то вручную отправил скрытую форму.
            raise PermissionDenied("Отзыв доступен после завершения обучения.")  # Возвращаем 403 и ничего не сохраняем.
        form = ReviewForm(request.POST, instance=item)  # Связываем форму с существующей заявкой, чтобы выполнить UPDATE, а не INSERT.
        if form.is_valid():  # Проверяем обязательность и длину текста, а также ограничения модели.
            form.save()  # Сохраняем только проверенное поле review_text.
            messages.success(request, "Отзыв сохранён.")  # Готовим уведомление для личного кабинета.
            return redirect("applications")  # Завершаем успешный POST перенаправлением.
    return render(request, "portal/form.html", {"form": form, "title": "Отзыв об обучении", "button": "Сохранить отзыв", "kind": "review"}, status=400)  # Ошибки текста показываем рядом с формой, не теряя введённое.
@login_required  # Сначала проверяем сам факт входа в аккаунт.
def dashboard_view(request):  # Собственная административная панель: это не стандартная django-admin.
    if not request.user.is_staff:  # Роль проверяется по данным БД, а не по скрытой кнопке в HTML.
        raise PermissionDenied("Раздел доступен администратору.")  # Обычный пользователь получит HTTP 403.
    status = request.GET.get("status", "")  # Фильтр передаётся в строке URL, например ?status=new.
    items = Application.objects.select_related("user", "course")  # Одним запросом загружаем заявку, владельца и название курса.
    if status in Application.Status.values:  # В запрос допускаем только известные коды статуса.
        items = items.filter(status=status)  # ORM подставляет параметр безопасно, без SQL-инъекции.
    else:  # Пустой или неизвестный фильтр не должен ломать панель.
        status = ""  # Сбрасываем его к режиму «Все статусы».
    page = Paginator(items, 5).get_page(request.GET.get("page"))  # Показываем по пять записей; неверный номер страницы обрабатывается без ошибки 500.
    rows = [(item, StatusForm(instance=item)) for item in page]  # Каждой записи даём форму с выбранным текущим статусом.
    return render(request, "portal/dashboard.html", {"rows": rows, "page": page, "statuses": Application.Status.choices, "selected": status})  # Шаблон получает данные, формы и состояние фильтра.
@login_required  # Смена статуса требует авторизованного пользователя.
@require_POST  # Не допускаем изменение БД простым открытием URL.
def status_view(request, pk):  # pk указывает конкретную изменяемую заявку.
    if not request.user.is_staff:  # Повторяем проверку роли в самом обработчике записи, независимо от доступности панели.
        raise PermissionDenied("Менять статус может только администратор.")  # Возвращаем 403 при поддельном запросе обычного пользователя.
    with transaction.atomic():  # Объединяем чтение и сохранение статуса в транзакцию.
        item = get_object_or_404(Application, pk=pk)  # Если такой заявки нет, возвращаем 404 вместо падения приложения.
        old_status = item.status  # Запоминаем состояние БД до того, как форма изменит объект в памяти.
        form = StatusForm(request.POST, instance=item)  # Разрешаем редактировать только status и проверяем направление перехода.
        if form.is_valid():  # Код статуса и переход должны пройти все серверные проверки.
            updated = Application.objects.filter(pk=pk, status=old_status).update(status=form.cleaned_data["status"])  # Условный UPDATE не перезапишет статус, уже изменённый другим администратором.
            if updated:  # Значение 1 означает, что ровно одна строка успешно обновлена.
                messages.success(request, "Статус обновлён.")  # На следующей странице появится уведомление об успехе.
            else:  # Ноль строк означает, что параллельный запрос уже поменял исходное состояние.
                messages.error(request, "Заявка уже изменена. Обновите страницу.")  # Предлагаем перечитать актуальную запись, не затирая изменения.
        else:  # Неверный переход должен дать объяснение, а не молчаливый отказ.
            messages.error(request, " ".join(error for errors in form.errors.values() for error in errors))  # Собираем проверенные сообщения формы в одно уведомление.
    return redirect("dashboard")  # После любой попытки возвращаемся к актуальному списку заявок.
