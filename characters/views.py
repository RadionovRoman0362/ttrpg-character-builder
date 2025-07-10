from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import CharacterSheet
from .permissions import IsOwner
from .serializers import (
    CharacterSheetListSerializer,
    CharacterSheetDetailSerializer,
    CharacterSheetCreateUpdateSerializer,
)
from .services import CharacterStateService


@extend_schema(tags=["Characters"])
@extend_schema_view(
    list=extend_schema(
        summary="Получить список своих персонажей",
        description="Возвращает постраничный список всех персонажей, принадлежащих текущему пользователю.",
    ),
    retrieve=extend_schema(
        summary="Получить детальную информацию о персонаже",
        description="Возвращает полную информацию о конкретном листе персонажа, включая трейты, фичи, экипировку и компаньонов.",
    ),
    create=extend_schema(
        summary="Создать нового персонажа",
        description="Создает новый лист персонажа. Игрок (player) автоматически присваивается текущему пользователю.",
        request=CharacterSheetCreateUpdateSerializer,  # Явно указываем сериализатор для запроса
        responses={
            201: CharacterSheetDetailSerializer
        },  # Явно указываем сериализатор для ответа
    ),
    update=extend_schema(
        summary="Полностью обновить персонажа",
        description="Полностью заменяет данные листа персонажа. Требует передачи всех полей.",
        request=CharacterSheetCreateUpdateSerializer,
        responses={200: CharacterSheetDetailSerializer},
    ),
    partial_update=extend_schema(
        summary="Частично обновить персонажа",
        description="Изменяет одно или несколько полей листа персонажа. Требует передачи только изменяемых полей.",
        request=CharacterSheetCreateUpdateSerializer,
        responses={200: CharacterSheetDetailSerializer},
    ),
    destroy=extend_schema(
        summary="Удалить персонажа",
        description="Безвозвратно удаляет лист персонажа и все связанные с ним данные (инвентарь, компаньоны).",
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
        return self.queryset.filter(
            player=self.request.user, controlled_by__isnull=True
        )

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
        if self.action in ["create", "update", "partial_update"]:
            return CharacterSheetCreateUpdateSerializer
        if self.action == "retrieve":
            return CharacterSheetDetailSerializer
        return CharacterSheetListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Стандартное сохранение, которое создает объект и M2M связи
        instance = serializer.save(player=self.request.user)

        # Принудительно обновляем инстанс из БД, чтобы подтянуть M2M связи
        instance.refresh_from_db()

        # А ТЕПЕРЬ, когда все связи установлены, вызываем сервис
        state_service = CharacterStateService()
        recalculated_instance = state_service.recalculate_and_save(character=instance)

        # Формируем ответ на основе самого свежего объекта
        response_serializer = CharacterSheetDetailSerializer(recalculated_instance)
        headers = self.get_success_headers(response_serializer.data)
        return Response(
            response_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Стандартное обновление
        updated_instance = serializer.save()

        updated_instance.refresh_from_db()

        # И снова вызываем сервис ПОСЛЕ всех операций
        state_service = CharacterStateService()
        recalculated_instance = state_service.recalculate_and_save(
            character=updated_instance
        )

        # Формируем ответ
        response_serializer = CharacterSheetDetailSerializer(recalculated_instance)
        return Response(response_serializer.data)
