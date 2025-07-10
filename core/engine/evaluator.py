import re
from functools import lru_cache
from json.decoder import JSONDecodeError
from django.core.exceptions import ObjectDoesNotExist

# ВАЖНО: Мы не импортируем модели CharacterSheet напрямую,
# чтобы избежать циклических зависимостей. Вместо этого, мы будем
# получать объект персонажа в конструкторе.


class RuleEvaluator:
    """
    Универсальный вычислитель правил, хранящихся в виде строковых формул.
    Работает в контексте одного конкретного листа персонажа.
    """

    def __init__(self, character_sheet):
        self.character = character_sheet
        # Получаем схему правил из metadata игровой системы.
        # Если ее нет, используем пустой словарь.
        try:
            self.rules_schema = self.character.system.metadata or {}
        except (JSONDecodeError, AttributeError):
            self.rules_schema = {}

    def evaluate(self, formula_string):
        """
        Основной метод для вычисления формулы.
        Пример: "trait_meta('Class', 'base_hp') + stat('level')"
        """
        print(f"--- Evaluating formula: '{formula_string}' ---")

        parts = formula_string.split(" ")

        # Простая логика для v1.0: предполагаем формулу вида "значение1 оператор значение2"
        if len(parts) != 3:
            # В будущем можно будет добавить поддержку более сложных формул
            raise ValueError(f"Unsupported formula format: {formula_string}")

        left_operand_str, operator, right_operand_str = parts

        left_value = self._resolve_value(left_operand_str)
        right_value = self._resolve_value(right_operand_str)

        print(f"Resolved: {left_value} {operator} {right_value}")

        if operator == "+":
            result = left_value + right_value
            print(f"Result: {result}")
            return result
        elif operator == "-":
            return left_value - right_value
        else:
            raise ValueError(f"Unsupported operator: {operator}")

    def _resolve_value(self, value_str):
        """
        Распознает, является ли строка числом, или функцией-хелпером,
        и возвращает вычисленное значение.
        """
        # Проверяем, является ли строка числом
        if value_str.isdigit() or (
            value_str.startswith("-") and value_str[1:].isdigit()
        ):
            return int(value_str)

        # Проверяем, является ли строка вызовом функции
        match = re.match(r"(\w+)\((.*)\)", value_str)
        if not match:
            raise ValueError(f"Invalid value or function format: {value_str}")

        func_name, args_str = match.groups()

        # "Белый список" разрешенных функций
        if func_name == "stat":
            return self._resolve_stat(*self._parse_args(args_str))
        elif func_name == "trait_meta":
            return self._resolve_trait_meta(*self._parse_args(args_str))
        elif func_name == "equipment_meta":
            return self._resolve_equipment_meta(*self._parse_args(args_str))
        else:
            raise ValueError(f"Unknown function: {func_name}")

    def _parse_args(self, args_str):
        """Простой парсер аргументов. Пример: "'Class', 'base_hp'" -> ["Class", "base_hp"]"""
        return [arg.strip().strip("'\"") for arg in args_str.split(",")]

    # --- Реализация функций-хелперов ---

    def _resolve_stat(self, stat_name):
        """Получает значение из character.stats"""
        try:
            return int(self.character.stats.get(stat_name, 0))
        except (ValueError, TypeError):
            return 0

    @lru_cache(maxsize=None)  # Кэшируем результат, чтобы не делать лишних запросов к БД
    def _get_trait_by_category(self, category_name):
        try:
            return self.character.traits.get(category__name__iexact=category_name)
        except ObjectDoesNotExist:
            return None

    def _resolve_trait_meta(self, category_name, path):
        """Получает значение из metadata трейта по категории."""
        trait = self._get_trait_by_category(category_name)
        if not trait:
            return 0

        # Простой парсер пути для v1.0. Пример: 'base_thresholds.major'
        value = trait.metadata
        try:
            for key in path.split("."):
                value = value[key]
            return int(value)
        except (KeyError, ValueError, TypeError):
            return 0

    @lru_cache(maxsize=None)
    def _get_equipment_in_location(self, location):
        try:
            # Для v1.0 ищем только первый предмет в указанной локации
            return self.character.equipment.get(location=location)
        except ObjectDoesNotExist:
            return None

    def _resolve_equipment_meta(self, location, path):
        """Получает значение из metadata экипированного предмета."""
        equipment = self._get_equipment_in_location(location)
        if not equipment:
            return 0

        value = equipment.template.metadata
        try:
            for key in path.split("."):
                value = value[key]
            return int(value)
        except (KeyError, ValueError, TypeError):
            return 0
