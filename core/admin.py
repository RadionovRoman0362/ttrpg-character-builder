from django.contrib import admin
from .models import (
    GameSystem,
    DamageType,
    Feature,
    Ancestry,
    Community,
    CharacterClass,
    Item,
    Weapon,
)

# Простая регистрация для большинства моделей
admin.site.register(GameSystem)
admin.site.register(DamageType)
admin.site.register(Feature)
admin.site.register(Ancestry)
admin.site.register(Community)
admin.site.register(CharacterClass)
admin.site.register(Item)
admin.site.register(Weapon)