"""
URL configuration for ttrpg_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include

# Импортируем вью для генерации схемы и UI
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # Наши основные эндпоинты API
    path("api/v1/", include("core.urls")),
    path("api/v1/", include("characters.urls")),
    # --- НОВЫЕ ПУТИ ДЛЯ ДОКУМЕНТАЦИИ ---
    # Эндпоинт, который генерирует сам файл schema.yml
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Опционально: Интерактивная документация Swagger UI
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # Опционально: Альтернативная документация Redoc
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
