from django.urls import include, path  # path объявляет маршрут; include подключает маршруты приложения.
urlpatterns = [path("", include("portal.urls"))]  # Все адреса от корня передаём приложению portal.
