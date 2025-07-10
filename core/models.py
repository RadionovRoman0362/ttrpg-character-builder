from django.db import models
from django.contrib.auth.models import User

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
    
class FeatureSet(models.Model):
    """
    Универсальная модель для именованной группы способностей.
    (Домен в Daggerheart, Школа магии в D&D и т.д.)
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    system = models.ForeignKey(GameSystem, on_delete=models.CASCADE, related_name="feature_sets")
    set_type = models.CharField(max_length=50, blank=True, help_text="Тип набора, например 'Domain'")

    class Meta:
        unique_together = ('system', 'name')
        verbose_name = "Feature Set"
        verbose_name_plural = "Feature Sets"

    def __str__(self):
        return f"{self.name} ({self.system.name})"
    
class Feature(models.Model):
    """
    Атомарная особенность, способность или заклинание.
    """
    name = models.CharField(max_length=200)
    description = models.TextField()
    system = models.ForeignKey(GameSystem, on_delete=models.CASCADE, related_name="features")
    
    # К какой группе/коллекции относится эта особенность (опционально)
    feature_set = models.ForeignKey(
        FeatureSet,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="features"
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE, # Если пользователь удаляется, его кастомные фичи тоже
        null=True,
        blank=True,
        related_name='custom_features',
        help_text="Если поле заполнено, эта 'особенность' создана пользователем (напр. Experience в Daggerheart)"
    )
    
    # Системно-специфичные данные: требования, стоимость, ресурсы и т.д.
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        pass

    def __str__(self):
        if self.created_by:
            return f"{self.name} (Custom, by {self.created_by.username})"
        return f"{self.name} ({self.system.name})"
    
class TraitCategory(models.Model):
    """
    Определяет ТИП строительного блока для конкретной игровой системы.
    Например: 'Класс', 'Раса', 'Происхождение', 'Предыстория', 'Клан'.
    """
    name = models.CharField(
        max_length=100,
        help_text="Тип характеристики, например, 'Класс' или 'Раса'"
    )
    system = models.ForeignKey(
        GameSystem,
        on_delete=models.CASCADE,
        related_name="trait_categories"
    )

    class Meta:
        # Имя категории должно быть уникальным в рамках одной игровой системы.
        # Не может быть двух категорий "Класс" для Daggerheart.
        unique_together = ('name', 'system')
        # Для корректного отображения в админке
        verbose_name = "Trait Category"
        verbose_name_plural = "Trait Categories"

    def __str__(self):
        return f"{self.name} ({self.system.name})"
    
class CharacterTrait(models.Model):
    """
    УНИВЕРСАЛЬНАЯ МОДЕЛЬ для любого строительного блока персонажа.
    Это может быть класс, раса, происхождение, подкласс - что угодно.
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # К какой игровой системе относится эта "черта"
    system = models.ForeignKey(
        GameSystem,
        on_delete=models.CASCADE,
        related_name="character_traits"
    )
    
    # К какой категории относится эта "черта"? Это Класс? Раса?
    category = models.ForeignKey(
        TraitCategory,
        on_delete=models.PROTECT, # Запрещаем удалять категорию, если к ней привязаны черты
        related_name="traits"
    )
    
    # Рекурсивная связь для поддержки иерархии (подклассы, подрасы)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL, # Если родитель удалится, подкласс не удаляется, а становится "корневым"
        null=True,
        blank=True,
        related_name='children'
    )

    # Какие особенности предоставляет эта черта (класс, раса и т.д.)
    features = models.ManyToManyField(Feature, blank=True)

    # Наше поле для хранения любых системно-специфичных данных
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Системно-специфичные данные, например, hit_die для D&D или base_evasion для Daggerheart"
    )

    class Meta:
        unique_together = ('system', 'category', 'name')
        verbose_name = "Character Trait"
        verbose_name_plural = "Character Traits"

    def __str__(self):
        return f"{self.name} ({self.category.name} | {self.system.name})"

class DamageType(models.Model):
    """
    Описывает типы урона (физический, огненный, психический и т.д.).
    Привязан к конкретной игровой системе.
    """
    name = models.CharField(max_length=50, help_text="Название типа урона")
    system = models.ForeignKey(GameSystem, on_delete=models.CASCADE, related_name="damage_types")

    class Meta:
        unique_together = ('name', 'system')

    def __str__(self):
        return f"{self.name} ({self.system.name})"

# --- Модели Предметов ---

class EquipmentTemplate(models.Model):
    """
    УНИВЕРСАЛЬНАЯ МОДЕЛЬ для любого предмета, которым может владеть персонаж.
    Это может быть оружие, броня, имплант, запчасть для меха, зелье, квестовый предмет.
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    system = models.ForeignKey(GameSystem, on_delete=models.CASCADE, related_name="equipment_templates")

    # Вместо жестких полей, у нас есть поле для всего
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        unique_together = ('system', 'name')
        verbose_name = "Equipment Template"
        verbose_name_plural = "Equipment Templates"

    def __str__(self):
        return f"{self.name} ({self.system.name})"
        