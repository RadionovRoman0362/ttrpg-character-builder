# Руководство по моделированию данных для TTRPG Character Builder

Этот документ описывает, как использовать наши универсальные модели данных для добавления правил из любой настольно-ролевой системы. Он служит "шпаргалкой" для разработчиков и контент-менеджеров.

## Основная философия

Наша архитектура основана на принципе "Сущность-Шаблон". Вместо создания отдельных таблиц для "Классов", "Рас" или "Предметов", мы используем несколько универсальных моделей-шаблонов (`CharacterTrait`, `Feature`, `EquipmentTemplate`), гибкость которых достигается за счет JSON-поля `metadata`.

---

## "Рецепт" добавления новой игровой системы

Следуйте этим шагам, чтобы описать правила новой системы (например, Daggerheart) для загрузки в базу данных.

### Шаг 1: Создание `GameSystem`

Это отправная точка. Для каждой новой системы создается одна запись.

- **Модель:** `core.GameSystem`
- **Пример для Daggerheart:**
  - `name`: "Daggerheart"
  - `version`: "1.0"
  - `slug`: "daggerheart"

### Шаг 2: Определение "Строительных блоков" (`TraitCategory`)

Определите, из каких "крупных" частей состоит персонаж в этой системе.

- **Модель:** `core.TraitCategory`
- **Пример для Daggerheart:** Создаем три записи, привязанные к `GameSystem` "Daggerheart":
  1. `name`: "Class"
  2. `name`: "Ancestry"
  3. `name`: "Community"
- **Пример для D&D 5e:**
  1. `name`: "Class"
  2. `name`: "Race"
  3. `name`: "Background"

### Шаг 3: Описание конкретных сущностей (`CharacterTrait`)

Теперь создайте записи для каждого конкретного выбора (каждого класса, расы и т.д.).

- **Модель:** `core.CharacterTrait`
- **Примеры для Daggerheart:**
  - **Класс:**
    - `name`: "Guardian"
    - `category`: Ссылка на `TraitCategory` "Class (Daggerheart)"
    - `metadata`:
      ```json
      {
        "base_evasion": 10,
        "base_hp": 12,
        "base_stress": 6,
        "grants_access_to": [
          {
            "type": "FeatureSet",
            "set_type": "Domain",
            "names": ["Blade", "Valor"]
          }
        ]
      }
      ```
  - **Подкласс:**
    - `name`: "Stalwart"
    - `category`: Ссылка на `TraitCategory` "Class (Daggerheart)"
    - `parent`: Ссылка на `CharacterTrait` "Guardian"
  - **Происхождение:**
    - `name`: "Faerie"
    - `category`: Ссылка на `TraitCategory` "Ancestry (Daggerheart)"

### Шаг 4: Определение "Групп способностей" (`FeatureSet`)

Если в системе есть именованные коллекции способностей (Домены, Школы магии), опишите их здесь.

- **Модель:** `core.FeatureSet`
- **Пример для Daggerheart:**
  - `name`: "Blade", `set_type`: "Domain", `system`: "Daggerheart"
  - `name`: "Valor", `set_type`: "Domain", `system`: "Daggerheart"
  - `name`: "Arcana", `set_type`: "Domain", `system`: "Daggerheart"

### Шаг 5: Описание атомарных Способностей (`Feature`)

Это самые мелкие "кирпичики": заклинания, черты, приемы.

- **Модель:** `core.Feature`
- **Примеры:**
  - **Карта Домена (Daggerheart):**
    - `name`: "Reckless"
    - `description`: "Описание способности..."
    - `feature_set`: Ссылка на `FeatureSet` "Blade"
    - `metadata`: `{"type": "domain_card", "requirements": {"level": 2}}`
  - **Черта от Происхождения:**
    - `name`: "Faerie's Tiny Stature"
    - `description`: "Описание..."
    - `feature_set`: `null` (не принадлежит домену)
    - `metadata`: `{"type": "ancestry_trait"}`

**Важно:** После создания `Feature` не забудьте привязать его к `CharacterTrait`, который его предоставляет. Например, `Feature` "Faerie's Tiny Stature" нужно добавить в `features` для `CharacterTrait` "Faerie".

### Шаг 6: Описание Предметов (`EquipmentTemplate`)

Создайте шаблоны для всего снаряжения, доступного в системе.

- **Модель:** `core.EquipmentTemplate`
- **Примеры:**
  - **Оружие:**
    - `name`: "Broadsword"
    - `metadata`:
      ```json
      {
        "type": "weapon",
        "weapon_type": "primary",
        "hands": 1,
        "damage": "d8",
        "damage_type_name": "Physical",
        "range": "Melee",
        "properties": {
          "Reliable": "+1 to attack rolls"
        }
      }
      ```
  - **Броня:**
    - `name`: "Chainmail Armor"
    - `metadata`:
      ```json
      {
        "type": "armor",
        "armor_type": "heavy",
        "base_armor_score": 4,
        "base_thresholds": { "major": 7, "severe": 15 },
        "properties": {
          "evasion_penalty": -1
        }
      }
      ```
  - **Зелье:**
    - `name`: "Minor Health Potion"
    - `metadata`:
      ```json
      {
        "type": "consumable",
        "effect": { "clear_hp": "1d4" }
      }
      ```

### Шаг 7: Как моделируется пользовательский контент

- **Концепция:** Любая сущность, создаваемая игроком, а не данная правилами (например, `Experience` в Daggerheart), — это тоже `Feature`.
- **Реализация:**
  1. Создается новая запись в таблице `core.Feature`.
  2. Поле `created_by` заполняется ссылкой на `User`, который создал эту фичу.
  3. В `metadata` описываются ее уникальные свойства.
     - **Пример для `Experience`:**
       - `name`: "Вырос уличным вором"
       - `created_by`: Ссылка на пользователя
       - `metadata`: `{"type": "experience_tag", "modifier": 2, "cost": {"resource": "hope", "amount": 1}}`
  4. Этот новый `Feature` привязывается к `CharacterSheet` игрока через связь `ManyToManyField`.

---

Эта структура позволяет нам описать практически любую игровую механику, не изменяя схему базы данных.
