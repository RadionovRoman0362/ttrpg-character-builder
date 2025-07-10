from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import CharacterSheet
from .permissions import IsOwner
from .serializers import (
    CharacterSheetListSerializer,
    CharacterSheetDetailSerializer,
    CharacterSheetCreateUpdateSerializer,
)

@extend_schema(tags=['Characters'])
@extend_schema_view(
    list=extend_schema(
        summary="Получить список своих персонажей",
        description="Возвращает постраничный список всех персонажей, принадлежащих текущему пользователю."
    ),
    retrieve=extend_schema(
        summary="Получить детальную информацию о персонаже",
        description="Возвращает полную информацию о конкретном листе персонажа, включая трейты, фичи, экипировку и компаньонов."
    ),
    create=extend_schema(
        summary="Создать нового персонажа",
        description="Создает новый лист персонажа. Игрок (player) автоматически присваивается текущему пользователю.",
        request=CharacterSheetCreateUpdateSerializer, # Явно указываем сериализатор для запроса
        responses={201: CharacterSheetDetailSerializer} # Явно указываем сериализатор для ответа
    ),
    update=extend_schema(
        summary="Полностью обновить персонажа",
        description="Полностью заменяет данные листа персонажа. Требует передачи всех полей.",
        request=CharacterSheetCreateUpdateSerializer,
        responses={200: CharacterSheetDetailSerializer}
    ),
    partial_update=extend_schema(
        summary="Частично обновить персонажа",
        description="Изменяет одно или несколько полей листа персонажа. Требует передачи только изменяемых полей.",
        request=CharacterSheetCreateUpdateSerializer,
        responses={200: CharacterSheetDetailSerializer}
    ),
    destroy=extend_schema(
        summary="Удалить персонажа",
        description="Безвозвратно удаляет лист персонажа и все связанные с ним данные (инвентарь, компаньоны)."
    ),
)
class CharacterSheetViewSet(viewsets.ModelViewSet):
    """
    API эндпоинт для управления листами персонажей.
    Требует аутентификации.
    """
    queryset = CharacterSheet.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        """
        Этот метод гарантирует, что пользователи увидят только своих персонажей.
        """
        return self.queryset.filter(player=self.request.user, controlled_by__isnull=True)

    def perform_create(self, serializer):
        """
        При создании нового листа персонажа, автоматически привязываем его
        к текущему пользователю.
        """
        serializer.save(player=self.request.user)

    def get_serializer_class(self):
        """
        Выбираем нужный сериализатор в зависимости от действия.
        """
        if self.action in ['create', 'update', 'partial_update']:
            return CharacterSheetCreateUpdateSerializer
        if self.action == 'retrieve':
            return CharacterSheetDetailSerializer
        return CharacterSheetListSerializer