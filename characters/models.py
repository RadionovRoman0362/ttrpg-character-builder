from django.db import models
from django.contrib.auth.models import User

# Импортируем "строительные блоки" из нашего приложения core
from core.models import GameSystem, Ancestry, CharacterClass, Community, Item

class CharacterSheet(models.Model):
    """
    Основная модель, представляющая лист персонажа.
    Хранит выборы игрока и его уникальные характеристики.
    """
    # --- Основная информация ---
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name="characters", help_text="Пользователь, владеющий персонажем")
    name = models.CharField(max_length=200, help_text="Имя персонажа")
    
    # --- Выбор правил из core ---
    system = models.ForeignKey(GameSystem, on_delete=models.PROTECT, related_name="character_sheets")
    ancestry = models.ForeignKey(Ancestry, on_delete=models.SET_NULL, null=True, blank=True, related_name="characters")
    character_class = models.ForeignKey(CharacterClass, on_delete=models.SET_NULL, null=True, blank=True, related_name="characters")
    community = models.ForeignKey(Community, on_delete=models.SET_NULL, null=True, blank=True, related_name="characters")

    # --- Состояние персонажа ---
    level = models.PositiveIntegerField(default=1)
    current_hp = models.IntegerField(default=10, help_text="Текущие хиты")
    max_hp = models.IntegerField(default=10, help_text="Максимальные хиты")
    
    # --- Характеристики (статы) для Daggerheart ---
    # Мы можем вынести их в JSONField, но для начала для ясности оставим так.
    # В будущем можно сделать более гибкую систему статов.
    strength = models.IntegerField(default=0)
    finesse = models.IntegerField(default=0)
    agility = models.IntegerField(default=0)
    instinct = models.IntegerField(default=0)
    presence = models.IntegerField(default=0)
    knowledge = models.IntegerField(default=0)

    # --- Прочая информация ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"'{self.name}' ({self.player.username}) - {self.system.name}"


class CharacterInventory(models.Model):
    """
    Промежуточная таблица для связи персонажей и предметов в их инвентаре.
    """
    character = models.ForeignKey(CharacterSheet, on_delete=models.CASCADE, related_name="inventory_items")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="in_inventories")
    quantity = models.PositiveIntegerField(default=1)
    is_equipped = models.BooleanField(default=False)

    class Meta:
        unique_together = ('character', 'item') # Один и тот же предмет не может лежать в инвентаре дважды разными строками
        verbose_name_plural = "Character Inventories"

    def __str__(self):
        return f"{self.quantity} x {self.item.name} in {self.character.name}'s inventory"