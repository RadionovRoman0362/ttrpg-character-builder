from rest_framework import serializers
from .models import (
    GameSystem,
    TraitCategory,
    CharacterTrait,
    FeatureSet,
    Feature,
    EquipmentTemplate,
    DamageType,
)

# --- Базовые сериализаторы ---


class GameSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameSystem
        fields = ["id", "name", "version", "slug"]


class DamageTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DamageType
        fields = ["id", "name"]


class FeatureSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureSet
        fields = ["id", "name", "description", "set_type"]


# --- Сериализаторы с вложенностью ---


class FeatureSerializer(serializers.ModelSerializer):
    # Показываем не просто ID, а вложенный объект FeatureSet
    feature_set = FeatureSetSerializer(read_only=True)

    class Meta:
        model = Feature
        # Мы не показываем created_by, так как это внутренняя информация
        fields = ["id", "name", "description", "feature_set", "metadata"]


class TraitCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TraitCategory
        fields = ["id", "name"]


class CharacterTraitSerializer(serializers.ModelSerializer):
    """
    Основной сериализатор для "строительных блоков".
    Он будет рекурсивно показывать своих "детей" (подклассы).
    """

    # Показываем полные объекты, а не просто ID
    category = TraitCategorySerializer(read_only=True)
    features = FeatureSerializer(many=True, read_only=True)

    # Рекурсивный сериализатор для подклассов/подрас
    children = serializers.SerializerMethodField()

    class Meta:
        model = CharacterTrait
        fields = [
            "id",
            "name",
            "description",
            "category",
            "parent",  # parent показываем как ID, чтобы избежать бесконечной вложенности вверх
            "children",  # а детей - как полные объекты
            "features",
            "metadata",
        ]

    def get_children(self, obj):
        # Находим всех "детей" текущего объекта
        children_queryset = obj.children.all()
        # Сериализуем их с помощью этого же сериализатора
        serializer = self.__class__(children_queryset, many=True, context=self.context)
        return serializer.data


class EquipmentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentTemplate
        fields = ["id", "name", "description", "metadata"]
