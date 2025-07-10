from django.shortcuts import render

from rest_framework import viewsets, permissions
from rest_framework.response import Response

from .models import GameSystem, CharacterTrait
from .serializers import GameSystemSerializer, CharacterTraitSerializer

class GameSystemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API эндпоинт для просмотра игровых систем.
    Доступен всем.
    """
    queryset = GameSystem.objects.all()
    serializer_class = GameSystemSerializer
    permission_classes = [permissions.AllowAny]


class CharacterTraitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API эндпоинт для просмотра "строительных блоков" (классов, рас и т.д.).
    Фильтруется по системе и по категории.
    """
    serializer_class = CharacterTraitSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        """
        Этот метод переопределяется для динамической фильтрации.
        Мы будем получать только те трейты, которые относятся к нужной системе.
        """
        # Получаем slug системы из URL-адреса
        # (?P<system_slug>...) в urls.py
        system_pk = self.kwargs.get('system_pk')
        if not system_pk:
            return CharacterTrait.objects.none()
        
        # Фильтруем основной queryset по PK системы
        queryset = CharacterTrait.objects.filter(system__pk=system_pk)

        # Дополнительно фильтруем по категории, если она указана в query-параметрах
        # Например: /api/v1/.../traits/?category=Class
        category_name = self.request.query_params.get('category')
        if category_name:
            # Фильтруем по имени категории
            # __iexact делает поиск нечувствительным к регистру
            queryset = queryset.filter(category__name__iexact=category_name)
        
        # Мы хотим получать только "корневые" трейты (те, у которых нет родителя)
        # Например, при запросе классов мы хотим видеть "Guardian", а не "Stalwart".
        # "Stalwart" будет виден внутри "Guardian" благодаря вложенному сериализатору.
        return queryset.filter(parent__isnull=True).prefetch_related('features', 'children')
    