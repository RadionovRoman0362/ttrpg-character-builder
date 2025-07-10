from django.shortcuts import render

from rest_framework import viewsets, permissions
from .models import CharacterSheet
from .permissions import IsOwner
from .serializers import (
    CharacterSheetListSerializer,
    CharacterSheetDetailSerializer,
    CharacterSheetCreateUpdateSerializer,
)

from django.contrib.auth.models import User

class CharacterSheetViewSet(viewsets.ModelViewSet):
    """
    API эндпоинт для управления листами персонажей.
    """
    # queryset будет определяться динамически в get_queryset
    queryset = CharacterSheet.objects.all()

    # Устанавливаем права доступа: пользователь должен быть аутентифицирован,
    # а для изменения объекта - быть его владельцем.
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        """
        Этот метод гарантирует, что пользователи увидят только своих персонажей.
        """
        # Фильтруем листы по текущему залогиненному пользователю
        # и показываем только "корневые" листы (не питомцев)
        # user = User.objects.first() # Берем первого пользователя (нашего суперюзера)
        # if not user: return self.queryset.none()
        # return self.queryset.filter(player=user, controlled_by__isnull=True)
        return self.queryset.filter(player=self.request.user, controlled_by__isnull=True)

    def perform_create(self, serializer):
        """
        При создании нового листа персонажа, автоматически привязываем его
        к текущему пользователю.
        """
        # user = User.objects.first() # Берем первого пользователя
        # serializer.save(player=user)
        serializer.save(player=self.request.user)

    def get_serializer_class(self):
        """
        Выбираем нужный сериализатор в зависимости от действия.
        """
        if self.action in ['create', 'update', 'partial_update']:
            return CharacterSheetCreateUpdateSerializer
        if self.action == 'retrieve':
            return CharacterSheetDetailSerializer
        # Для 'list' и других действий
        return CharacterSheetListSerializer
    