from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import GameSystem, CharacterTrait, EquipmentTemplate, Feature
from .serializers import (
    GameSystemSerializer,
    CharacterTraitSerializer,
    EquipmentTemplateSerializer,
    FeatureSerializer,
)

# Мы добавим недостающие ViewSet'ы для полноты картины


@extend_schema(tags=["Core - Game Systems"])
class GameSystemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API эндпоинт для просмотра игровых систем.
    Доступен всем.
    """

    queryset = GameSystem.objects.all()
    serializer_class = GameSystemSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema(tags=["Core - Rules"])
class CharacterTraitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API эндпоинт для просмотра "строительных блоков" (классов, рас и т.д.).
    Фильтруется по системе и по категории.
    """

    serializer_class = CharacterTraitSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        system_pk = self.kwargs.get("system_pk")
        if not system_pk:
            return CharacterTrait.objects.none()

        queryset = CharacterTrait.objects.filter(system__pk=system_pk)

        category_name = self.request.query_params.get("category")
        if category_name:
            queryset = queryset.filter(category__name__iexact=category_name)

        return queryset.filter(parent__isnull=True).prefetch_related(
            "features", "children"
        )

    @extend_schema(
        summary="Список строительных блоков системы",
        description="Получить список корневых строительных блоков (например, классов или рас) для конкретной игровой системы.",
        parameters=[
            OpenApiParameter(
                name="category",
                description="Фильтр по имени категории (например, Class, Ancestry). Регистронезависимый.",
                required=False,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        """Получить список корневых Character Traits для системы."""
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Детальная информация о блоке")
    def retrieve(self, request, *args, **kwargs):
        """Получить полную информацию об одном Character Trait, включая подклассы и особенности."""
        return super().retrieve(request, *args, **kwargs)


@extend_schema(tags=["Core - Rules"])
class EquipmentTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """API эндпоинт для просмотра шаблонов экипировки."""

    queryset = EquipmentTemplate.objects.all()
    serializer_class = EquipmentTemplateSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(summary="Список всех шаблонов экипировки")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Детальная информация о шаблоне экипировки")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


@extend_schema(tags=["Core - Rules"])
class FeatureViewSet(viewsets.ReadOnlyModelViewSet):
    """API эндпоинт для просмотра всех особенностей (Features)."""

    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(summary="Список всех особенностей")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Детальная информация об особенности")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
