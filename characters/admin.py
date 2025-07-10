from django.contrib import admin
from .models import CharacterSheet, CharacterEquipment

@admin.register(CharacterSheet)
class CharacterSheetAdmin(admin.ModelAdmin):
    list_display = ('name', 'player', 'system', 'controlled_by')
    list_filter = ('system', 'player')
    search_fields = ('name',)

@admin.register(CharacterEquipment)
class CharacterEquipmentAdmin(admin.ModelAdmin):
    list_display = ('get_character_name', 'template', 'quantity', 'location')
    list_filter = ('character', 'template', 'location')

    # Метод, чтобы красиво отображать имя персонажа
    def get_character_name(self, obj):
        return obj.character.name
    get_character_name.short_description = 'Character' # Название колонки
    get_character_name.admin_order_field = 'character__name' # Сортировка