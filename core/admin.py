from django.contrib import admin
from .models import (
    GameSystem,
    DamageType,
    TraitCategory,
    CharacterTrait,
    FeatureSet,
    Feature,
    EquipmentTemplate,
)

# Для удобства можно создать кастомные классы админки
# Например, чтобы фильтровать по системе или категории


@admin.register(GameSystem)
class GameSystemAdmin(admin.ModelAdmin):
    list_display = ("name", "version", "slug")


@admin.register(CharacterTrait)
class CharacterTraitAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "system", "parent")
    list_filter = ("system", "category")
    search_fields = ("name", "description")


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ("name", "system", "feature_set", "created_by")
    list_filter = ("system", "feature_set", "created_by")
    search_fields = ("name", "description")


@admin.register(EquipmentTemplate)
class EquipmentTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "system")
    list_filter = ("system",)
    search_fields = ("name", "description")


# Простая регистрация для остальных моделей
admin.site.register(DamageType)
admin.site.register(TraitCategory)
admin.site.register(FeatureSet)
