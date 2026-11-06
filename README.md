# llm_overall

Модульный LLM-пайплайн на Python для интеллектуальной обработки пользовательского текста с использованием Gemini API через OpenAI-совместимый интерфейс.

Проект разрабатывается по семиэтапному плану. **Текущий этап – День 4: Classification and Routing.**

## Возможности

- Обработка произвольного текста пользователя.
- Генерация краткого `summary` и трёх `key_points`.
- Определение категории запроса и намерения (`intent`).
- Явная маршрутизация генерации в зависимости от категории.
- Генерация полезного `final_answer` с учётом типа запроса.
- Структурированный JSON и валидация Pydantic.
- Логирование этапов и обработка ошибок валидации.
- Автоматические тесты с pytest.

### Категории запросов

| Категория | Назначение |
|---|---|
| `support` | Техническая помощь и инструкции |
| `feedback` | Отзывы и предложения |
| `complaint` | Жалобы и проблемы обслуживания |
| `sales` | Вопросы о покупке, тарифах и сравнении |
| `general_question` | Общие информационные вопросы |

## Технологии

Python 3.12, Gemini API, OpenAI Python SDK, Pydantic v2, python-dotenv, pytest, Ruff.

## Установка

```powershell
git clone https://github.com/Agito-dm/llm_overall.git
cd llm_overall
conda create -n llm_overall python=3.12 -y
conda activate llm_overall
python -m pip install -e ".[dev]"
```

## Конфигурация

Создайте `.env`:

```powershell
Copy-Item .env.example .env
```

Укажите API-ключ, название модели и базовый URL OpenAI-совместимого API согласно `.env.example`.

**Не добавляйте API-ключи и файл `.env` в Git.**

## Запуск

Классический режим Дней 1–3:

```powershell
python main.py --text "Объясни принцип работы LLM"
```

Режим классификации и маршрутизации Дня 4:

```powershell
python main.py --routed --text "После обновления программа перестала запускаться"
```

Запуск демонстрационных примеров:

```powershell
python main.py --demo
```

Сохранение результата:

```powershell
python main.py --routed --text "Что такое нейронная сеть?" --output outputs/result.json
```

## Архитектура

```text
src/llm_overall/
├── classification/
│   ├── categories.py
│   ├── classifier.py
│   └── routing.py
├── clients/
│   └── llm_client.py
├── core/
│   ├── pipeline.py
│   └── routed_pipeline.py
├── models/
│   ├── schemas.py
│   ├── routed_output.py
│   └── validation.py
├── prompts/
│   ├── classification_prompt.py
│   ├── generation_prompt.py
│   └── prompt_variants.py
└── config.py
```

Также используются `main.py`, каталоги `tests/`, `examples/` и `docs/`.

### Алгоритм routed pipeline

1. Пользователь передаёт текст.
2. Gemini классифицирует запрос и определяет `category` и `intent`.
3. Python-функция `get_route()` выбирает инструкцию генерации.
4. Gemini генерирует структурированный ответ согласно выбранному маршруту.
5. Pydantic валидирует результат; известные избыточные поля от модели удаляются перед проверкой.
6. Возвращается итоговый JSON с шестью полями.

Старый пайплайн сохранён для совместимости с предыдущими этапами.

## Тестирование

```powershell
python -m ruff check .
python -m ruff format --check .
python -m pytest -q
```

Последняя локальная проверка: **55 passed**, Ruff без замечаний.

Для реальной оценки Gemini:

```powershell
python -m examples.evaluate_day04
```

Скрипт проверяет десять пользовательских текстов, сохраняет результаты в `outputs/day04_results.json` и подсчитывает показатели успешности.

Первоначальный полный прогон завершился успешно на 8 из 10 примеров. Два оставшихся случая выявили избыточные поля JSON, обработка которых была добавлена позднее. После исправления автоматические тесты проходят; повторная полная оценка модели ещё не зафиксирована.

Реальные результаты зависят от доступности API, модели и ограничений квоты.

## Этапы разработки

| День | Тема | Статус |
|---|---|---|
| 1 | Basic LLM Pipeline | Завершён |
| 2 | Prompt Engineering | Завершён |
| 3 | Structured Output and Validation | Завершён |
| 4 | Classification and Routing | Реализован, финализация |
| 5 | Multi-step LLM Chain | Запланирован |
| 6 | Reliability, Guardrails and Fallback | Запланирован |
| 7 | Finalization | Запланирован |

Подробный план – `docs/roadmap.md`.

## Ограничения

- Качество классификации зависит от используемой LLM.
- Текущий routed pipeline выполняет два последовательных API-вызова.
- Массовые проверки могут упираться в RPM-квоту провайдера.
- Автоматические retries, fallback и дополнительная проверка ответа будут развиваться в Днях 5–6.
- Сервис не подключён к реальным системам оплаты, поддержки или управления подписками. Генерируемые ответы не означают фактического выполнения действий.
