from rest_framework import serializers
from .models import CharacterSheet, CharacterEquipment
from core.serializers import (
    CharacterTraitSerializer,
    FeatureSerializer,
    EquipmentTemplateSerializer,
)
from core.models import CharacterTrait, Feature


class CharacterEquipmentSerializer(serializers.ModelSerializer):
    # При просмотре инвентаря хотим видеть полную инфу о шаблоне предмета
    template = EquipmentTemplateSerializer(read_only=True)

    class Meta:
        model = CharacterEquipment
        fields = ["id", "template", "quantity", "location", "metadata"]


class CharacterSheetListSerializer(serializers.ModelSerializer):
    """Сериализатор для краткого отображения в списке персонажей."""

    class Meta:
        model = CharacterSheet
        fields = ["id", "name", "system", "stats"]  # Показываем только основное


class CharacterSheetDetailSerializer(CharacterSheetListSerializer):
    """Сериализатор для детального просмотра одного персонажа. Наследуется от краткого."""

    traits = CharacterTraitSerializer(many=True, read_only=True)
    features = FeatureSerializer(many=True, read_only=True)
    equipment = CharacterEquipmentSerializer(many=True, read_only=True)

    # Рекурсивно показываем компаньонов, используя этот же детальный сериализатор
    companions = serializers.SerializerMethodField()

    class Meta(CharacterSheetListSerializer.Meta):
        # Добавляем новые поля к полям родительского сериализатора
        fields = CharacterSheetListSerializer.Meta.fields + [
            "traits",
            "features",
            "equipment",
            "companions",
        ]

    def get_companions(self, obj):
        # Используем CharacterSheetDetailSerializer для вложенных компаньонов
        return CharacterSheetDetailSerializer(obj.companions.all(), many=True).data


class CharacterSheetCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления. Принимает ID для связей."""

    # Для записи мы ожидаем список ID, а не вложенные объекты
    traits = serializers.PrimaryKeyRelatedField(
        queryset=CharacterTrait.objects.all(), many=True, required=False
    )
    features = serializers.PrimaryKeyRelatedField(
        queryset=Feature.objects.all(), many=True, required=False
    )

    class Meta:
        model = CharacterSheet
        # `player` будет установлен автоматически, поэтому его здесь нет
        fields = ["id", "name", "system", "traits", "features", "stats", "conditions"]
