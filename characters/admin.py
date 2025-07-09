from django.contrib import admin
from .models import CharacterSheet, CharacterInventory

# Мы можем создать более кастомные классы админки для лучшего отображения.
# Например, чтобы инвентарь отображался прямо на странице персонажа.
# Но для начала хватит и простой регистрации.

admin.site.register(CharacterSheet)
admin.site.register(CharacterInventory)