from django.urls import path, include
from rest_framework_nested import routers
from .views import GameSystemViewSet, CharacterTraitViewSet

# Используем DefaultRouter для корневых эндпоинтов
router = routers.DefaultRouter()
router.register('systems', GameSystemViewSet, basename='systems')

# Используем вложенный роутер для трейтов внутри системы
systems_router = routers.NestedDefaultRouter(router, 'systems', lookup='system')
systems_router.register('traits', CharacterTraitViewSet, basename='system-traits')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(systems_router.urls)),
]