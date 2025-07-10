import json
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

# Импортируем все наши модели из core
from core.models import (
    GameSystem,
    TraitCategory,
    DamageType,
    FeatureSet,
    Feature,
    CharacterTrait
)

class Command(BaseCommand):
    help = 'Loads data for a new game system from a JSON file'

    def add_arguments(self, parser):
        # Мы определяем один обязательный аргумент - путь к файлу
        parser.add_argument('json_file', type=str, help='The path to the JSON file to load.')

    def handle(self, *args, **options):
        # Получаем путь к файлу из аргументов
        json_file_path = options['json_file']
        self.stdout.write(self.style.SUCCESS(f'Processing {json_file_path}...'))

        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise CommandError(f'File not found at: {json_file_path}')
        except json.JSONDecodeError:
            raise CommandError(f'Error decoding JSON from: {json_file_path}')

        # Используем transaction.atomic, чтобы все операции были выполнены как одна.
        # Если где-то произойдет ошибка, все изменения откатятся.
        try:
            with transaction.atomic():
                self.load_data(data)
        except Exception as e:
            raise CommandError(f'An error occurred during data loading: {e}')

        self.stdout.write(self.style.SUCCESS('Successfully loaded all data!'))

    def load_data(self, data):
        # --- 1. Создаем или получаем GameSystem ---
        system_data = data.get('system')
        system, created = GameSystem.objects.get_or_create(
            slug=system_data['slug'],
            defaults={'name': system_data['name'], 'version': system_data['version']}
        )
        self.stdout.write(f'{"Created" if created else "Found"} Game System: {system.name}')

        # --- 2. Создаем категории, типы урона, наборы фич ---
        # Мы используем bulk_create для эффективности.
        # ignore_conflicts=True значит, что если запись уже существует, она будет проигнорирована.
        TraitCategory.objects.bulk_create(
            [TraitCategory(name=cat_name, system=system) for cat_name in data.get('trait_categories', [])],
            ignore_conflicts=True
        )
        DamageType.objects.bulk_create(
            [DamageType(name=dt_name, system=system) for dt_name in data.get('damage_types', [])],
            ignore_conflicts=True
        )
        FeatureSet.objects.bulk_create(
            [FeatureSet(name=fs['name'], set_type=fs['set_type'], system=system) for fs in data.get('feature_sets', [])],
            ignore_conflicts=True
        )
        self.stdout.write('Loaded Trait Categories, Damage Types, and Feature Sets.')

        # --- 3. Создаем Features (без связей) ---
        # Мы не можем использовать bulk_create здесь, так как нам нужно будет связывать их.
        # Вместо этого, будем создавать их по одному, проверяя существование.
        feature_map = {}
        for feature_data in data.get('features', []):
            feature, created = Feature.objects.get_or_create(
                name=feature_data['name'],
                system=system,
                defaults={
                    'description': feature_data.get('description', ''),
                    'metadata': feature_data.get('metadata', {})
                }
            )
            feature_map[feature.name] = feature # Сохраняем для будущих связей

        self.stdout.write('Loaded Features.')

        # --- 4. Создаем Character Traits (без связей) ---
        trait_map = {}
        for trait_data in data.get('character_traits', []):
            # Находим категорию по имени
            category = TraitCategory.objects.get(name=trait_data['category'], system=system)
            trait, created = CharacterTrait.objects.get_or_create(
                name=trait_data['name'],
                system=system,
                category=category,
                defaults={
                    'description': trait_data.get('description', ''),
                    'metadata': trait_data.get('metadata', {})
                }
            )
            trait_map[trait.name] = trait

        self.stdout.write('Loaded Character Traits.')

        # --- 5. Устанавливаем связи (второй проход) ---
        # Теперь, когда все объекты созданы, мы можем установить связи ManyToMany и ForeignKey
        
        # Связи для Features -> FeatureSet
        for feature_data in data.get('features', []):
            if feature_data.get('feature_set'):
                feature = feature_map[feature_data['name']]
                feature_set = FeatureSet.objects.get(name=feature_data['feature_set'], system=system)
                feature.feature_set = feature_set
                feature.save()

        # Связи для Character Traits -> Parent и Features
        for trait_data in data.get('character_traits', []):
            trait = trait_map[trait_data['name']]
            
            # Связь с родителем (для подклассов)
            if trait_data.get('parent'):
                parent_trait = trait_map[trait_data['parent']]
                trait.parent = parent_trait
                trait.save()

            # Связь с особенностями (ManyToMany)
            feature_names = trait_data.get('features', [])
            features_to_add = [feature_map[name] for name in feature_names]
            trait.features.set(features_to_add)

        self.stdout.write('Established all relationships.')