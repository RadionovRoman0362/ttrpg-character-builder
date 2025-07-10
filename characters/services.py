from core.engine.evaluator import RuleEvaluator


class CharacterStateService:
    """
    Сервис для управления состоянием и вычисляемыми параметрами персонажа.
    """

    def recalculate_and_save(self, character):
        """
        Пересчитывает все вычисляемые параметры персонажа и сохраняет их.
        Этот метод является идемпотентным - его можно безопасно вызывать много раз.
        """
        print(f"--- Recalculating stats for Character ID: {character.id} ---")

        # Инициализируем наш движок правил для конкретного персонажа
        evaluator = RuleEvaluator(character)

        # Получаем схему вычисляемых статов из правил игровой системы
        # Убеждаемся, что работаем со словарем, даже если в metadata ничего нет
        schema = evaluator.rules_schema.get("character_sheet_schema", {})
        computed_stats_schema = schema.get("computed_stats", {})

        if not computed_stats_schema:
            print("No computed_stats schema found. Exiting.")
            # Если для этой системы нет вычисляемых статов, ничего не делаем
            return character

        # Создаем копию объекта stats, чтобы изменять ее
        # Это хорошая практика, чтобы не менять объект "на лету"
        updated_stats = character.stats.copy()
        print(f"Initial stats: {updated_stats}")

        # Проходим по каждому вычисляемому стату, описанному в схеме
        for stat_name, rule in computed_stats_schema.items():
            formula = rule.get("formula")
            if not formula:
                continue

            try:
                # Вычисляем новое значение с помощью нашего движка
                new_value = evaluator.evaluate(formula)
                # Записываем результат в наш обновленный словарь stats
                updated_stats[stat_name] = new_value
            except ValueError as e:
                # В будущем здесь можно будет добавить логирование ошибок
                print(
                    f"Error evaluating formula for '{stat_name}' on character {character.id}: {e}"
                )
                # Пропускаем этот стат, но не прерываем весь процесс
                continue

        print(f"Final calculated stats: {updated_stats}")
        character.stats = updated_stats
        character.save(update_fields=["stats"])

        return character
