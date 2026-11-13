from django.urls import path  # path связывает адрес с функцией view и даёт маршруту имя.
from . import views  # Импортируем обработчики из текущего пакета portal.
urlpatterns = [  # Django проверяет маршруты сверху вниз до первого совпадения.
    path("", views.login_view, name="home"),  # Корень сайта показывает вход без необходимости помнить дополнительный путь.
    path("register/", views.register_view, name="register"),  # Регистрация нового пользователя.
    path("login/", views.login_view, name="login"),  # Авторизация пользователя или администратора.
    path("logout/", views.logout_view, name="logout"),  # Защищённый POST для выхода.
    path("applications/", views.applications_view, name="applications"),  # Личный список заявок.
    path("applications/new/", views.new_application_view, name="new_application"),  # Форма записи на курс.
    path("applications/<int:pk>/review/", views.review_view, name="review"),  # int:pk допускает только числовой идентификатор заявки.
    path("admin/", views.dashboard_view, name="dashboard"),  # Собственная панель администратора с фильтром и пагинацией.
    path("admin/<int:pk>/status/", views.status_view, name="status"),  # Отдельный POST-обработчик изменения статуса.
]  # Конец таблицы маршрутов приложения.
