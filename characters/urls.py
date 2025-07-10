from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CharacterSheetViewSet

router_characters = DefaultRouter()
router_characters.register('sheets', CharacterSheetViewSet, basename='sheets')

urlpatterns = [
    path('', include(router_characters.urls)),
]