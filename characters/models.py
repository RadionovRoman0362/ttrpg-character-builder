from django.db import models
from django.contrib.auth.models import User

from core.models import GameSystem, CharacterTrait, Feature, EquipmentTemplate

class CharacterSheet(models.Model):
    """
    Универсальная модель, представляющая лист любого персонажа, питомца или NPC.
    """
    # --- Основная информация ---
    player = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="character_sheets",
        help_text="Пользователь, владеющий этим листом персонажа"
    )
    name = models.CharField(max_length=200, help_text="Имя персонажа/существа")
    system = models.ForeignKey(
        GameSystem,
        on_delete=models.PROTECT, # Запрещаем удалять систему, если по ней есть персонажи
        related_name="character_sheets"
    )
    
    # --- Иерархия (для питомцев, фамильяров, дронов) ---
    controlled_by = models.ForeignKey(
        'self',
        on_delete=models.CASCADE, # Если хозяин удален, питомец тоже
        null=True,
        blank=True,
        related_name='companions',
        help_text="Если этот лист является питомцем, здесь указывается его хозяин"
    )

    # --- Выбранные строительные блоки (классы, расы, и т.д.) ---
    traits = models.ManyToManyField(
        CharacterTrait,
        blank=True,
        help_text="Набор выбранных черт: класс, раса, происхождение и т.д."
    )

    # --- Выбранные способности (карты доменов, заклинания) ---
    features = models.ManyToManyField(
        Feature,
        blank=True,
        help_text="Набор всех полученных особенностей и способностей"
    )
    
    # --- Текущее состояние и характеристики ---
    # Единый источник правды для всех числовых и вычисляемых параметров
    stats = models.JSONField(
        default=dict,
        blank=True,
        help_text="Все характеристики, ресурсы (HP, мана), и вычисляемые параметры (Evasion)"
    )

    # --- Активные состояния и эффекты ---
    conditions = models.JSONField(
        default=list,
        blank=True,
        help_text="Список активных состояний, например, ['poisoned', 'vulnerable']"
    )

    # --- Прочая информация ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Character Sheet"
        verbose_name_plural = "Character Sheets"

    def __str__(self):
        if self.controlled_by:
            return f"{self.name} (Companion to {self.controlled_by.name})"
        return f"'{self.name}' ({self.player.username}) - {self.system.name}"


class CharacterEquipment(models.Model):
    """
    Связывает персонажа с экземпляром предмета и хранит ЕГО УНИКАЛЬНОЕ СОСТОЯНИЕ.
    """
    character = models.ForeignKey(CharacterSheet, on_delete=models.CASCADE, related_name="equipment")
    
    # Ссылка на ШАБЛОН предмета
    template = models.ForeignKey(EquipmentTemplate, on_delete=models.CASCADE)
    
    quantity = models.PositiveIntegerField(default=1)
    
    # Где находится этот предмет?
    # 'inventory', 'equipped', 'implanted', 'installed_in_mech'
    location = models.CharField(max_length=50, default="inventory")
    
    # Ссылка на "родительский" предмет для модульности (например, оружие установлено на мех)
    parent_equipment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE, # Если мех уничтожен, уничтожаются и его части
        null=True,
        blank=True,
        related_name='attachments'
    )

    # Состояние конкретного экземпляра
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Character Equipment"
        verbose_name_plural = "Character Equipment"

    def __str__(self):
        return f"{self.quantity} x {self.template.name} ({self.character.name})"