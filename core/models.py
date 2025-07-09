from django.db import models

# --- Фундаментальные модели ---

class GameSystem(models.Model):
    """
    Описывает саму игровую систему, например, Daggerheart или D&D 5e.
    Это корневая модель, к которой будет привязано всё остальное.
    """
    name = models.CharField(max_length=100, unique=True, help_text="Название игровой системы, например, Daggerheart")
    version = models.CharField(max_length=20, blank=True, help_text="Версия системы, например, 1.0")
    slug = models.SlugField(unique=True, help_text="Короткое имя для URL, например, 'daggerheart'")

    def __str__(self):
        return f"{self.name} {self.version}"

class DamageType(models.Model):
    """
    Описывает типы урона (физический, огненный, психический и т.д.).
    Привязан к конкретной игровой системе.
    """
    name = models.CharField(max_length=50, help_text="Название типа урона")
    system = models.ForeignKey(GameSystem, on_delete=models.CASCADE, related_name="damage_types")

    class Meta:
        unique_together = ('name', 'system') # Тип урона должен быть уникальным в рамках одной системы

    def __str__(self):
        return f"{self.name} ({self.system.name})"

class Feature(models.Model):
    """
    Ключевая модель! Это любая атомарная особенность или способность.
    Например: "Ночное зрение", "Компетентность в тяжелой броне", "Уязвимость к огню".
    """
    name = models.CharField(max_length=200, help_text="Название особенности")
    description = models.TextField(help_text="Подробное описание того, что делает особенность")
    system = models.ForeignKey(GameSystem, on_delete=models.CASCADE, related_name="features")
    
    class Meta:
        unique_together = ('name', 'system')

    def __str__(self):
        return self.name

# --- Модели "Строительных блоков" персонажа ---

class Ancestry(models.Model):
    """Происхождение персонажа (аналог Расы в D&D)."""
    name = models.CharField(max_length=100)
    description = models.TextField()
    system = models.ForeignKey(GameSystem, on_delete=models.CASCADE, related_name="ancestries")
    # Происхождение предоставляет персонажу набор особенностей
    features = models.ManyToManyField(Feature, blank=True, related_name="ancestries")

    class Meta:
        unique_together = ('name', 'system')
        verbose_name_plural = "Ancestries" # Для корректного отображения в админке

    def __str__(self):
        return self.name

class Community(models.Model):
    """Сообщество персонажа (аналог Предыстории в D&D)."""
    name = models.CharField(max_length=100)
    description = models.TextField()
    system = models.ForeignKey(GameSystem, on_delete=models.CASCADE, related_name="communities")
    features = models.ManyToManyField(Feature, blank=True, related_name="communities")

    class Meta:
        unique_together = ('name', 'system')
        verbose_name_plural = "Communities"

    def __str__(self):
        return self.name

class CharacterClass(models.Model):
    """Игровой класс персонажа."""
    name = models.CharField(max_length=100)
    description = models.TextField()
    system = models.ForeignKey(GameSystem, on_delete=models.CASCADE, related_name="classes")
    features = models.ManyToManyField(Feature, blank=True, related_name="classes")

    # Наше "секретное оружие" для гибкости.
    # Сюда можно будет записывать уникальные для системы поля.
    # Например, для D&D: {"hit_die": "d8"}, для Daggerheart: {"primary_domains": ["blade", "valor"]}
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ('name', 'system')
        verbose_name_plural = "Character Classes"

    def __str__(self):
        return self.name


# --- Модели Предметов ---

class Item(models.Model):
    """Базовая модель для всех предметов в игре."""
    name = models.CharField(max_length=200)
    description = models.TextField()
    system = models.ForeignKey(GameSystem, on_delete=models.CASCADE, related_name="items")
    metadata = models.JSONField(default=dict, blank=True, help_text="Доп. поля, например, вес, стоимость и т.д.")
    
    class Meta:
        unique_together = ('name', 'system')

    def __str__(self):
        return self.name

class Weapon(Item):
    """Модель для оружия, наследуется от Item."""
    damage_dice = models.CharField(max_length=50, help_text="Кости урона, например, '1d8' или '2d6'")
    damage_type = models.ForeignKey(DamageType, on_delete=models.PROTECT, related_name="weapons")

    def __str__(self):
        return f"{self.name} ({self.damage_dice} {self.damage_type.name})"
        