# llm_overall

Модульный LLM-пайплайн на Python для интеллектуальной обработки пользовательского текста с использованием Gemini API через OpenAI-совместимый интерфейс.

Проект реализует требования семидневного учебного задания `roadmap_tg.md`: от базовой обработки текста до единого пятиэтапного LLM workflow с классификацией, маршрутизацией, валидацией, self-check и обработкой ошибок. Установка и тесты успешно проверены из чистого клона GitHub.

## Возможности

- Обработка произвольного текста пользователя.
- Генерация краткого `summary` и трёх `key_points`.
- Определение категории запроса и намерения (`intent`).
- Явная маршрутизация генерации в зависимости от категории.
- Генерация полезного `final_answer` с учётом типа запроса.
- Структурированный JSON и валидация Pydantic.
- Пятиэтапная цепочка с передачей промежуточных результатов и Self-check.
- Повторные попытки при временных ошибках API, fallback и ограничения длины ответа.
- Настраиваемый интервал между вызовами LLM.
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

### Ограничения Gemini API

Gemini API имеет ограничения по количеству запросов в минуту
(RPM), входным токенам в минуту (TPM) и запросам в день (RPD).

Во время разработки для используемой модели Gemini 3.5
Flash-Lite в Google AI Studio отображались следующие лимиты:

- RPM: 15 запросов в минуту.
- TPM: 250 000 входных токенов в минуту.
- RPD: 500 запросов в день.

Лимиты могут изменяться в зависимости от модели, проекта
и уровня доступа.

Полный пятиэтапный pipeline обычно выполняет четыре
обращения к LLM на один текст. Пять демонстрационных
сценариев требуют 20 запросов без retry и fallback.

Для ограничения частоты запросов используется переменная
окружения `LLM_REQUEST_INTERVAL_SECONDS`.

Рекомендуемый интервал для указанной конфигурации — 6 секунд:

```powershell
$env:LLM_REQUEST_INTERVAL_SECONDS = "6"
python main.py --full --demo --output outputs/day07_results.json
```

Интервал применяется между началами последовательных
запросов одного экземпляра LLMClient, включая retry
и fallback.

По умолчанию значение равно 0, то есть ожидание отключено.
Для отключения вручную:

```powershell
$env:LLM_REQUEST_INTERVAL_SECONDS = "0"
```

Ограничение снижает риск HTTP 429, но не исключает
превышения других квот или одновременных запросов.

Актуальные лимиты доступны в Google AI Studio:
https://aistudio.google.com/rate-limit

## Запуск

Классический режим Дней 1–3:

```powershell
python main.py --text "Объясни принцип работы LLM"
```

Режим классификации и маршрутизации Дня 4:

```powershell
python main.py --routed --text "После обновления программа перестала запускаться"
```

Запуск демонстрационных примеров классического режима:

```powershell
python main.py --demo
```

День 5 – полный пятиэтапный workflow (один из пяти сценариев):

```powershell
python run_day05.py --example 1
```

Сохранение результата в routed-режиме:

```powershell
python main.py --routed --text "Что такое нейронная сеть?" --output outputs/result.json
```

### Полный pipeline (День 7)

Обработка произвольного текста через все пять этапов:

```powershell
python main.py --full --text "После обновления приложения возникла ошибка 503"
```

Запуск пяти демонстрационных сценариев:

```powershell
$env:LLM_REQUEST_INTERVAL_SECONDS = "6"
python main.py --full --demo --output outputs/day07_results.json
```

Сценарии расположены в `examples/full_pipeline_inputs.json`
и охватывают support, feedback, complaint, sales и general_question.

Результат содержит:

- `summary` — краткое содержание текста;
- `category` — тип запроса;
- `sentiment` — тональность;
- `key_points` — три ключевые мысли;
- `final_answer` — полезный ответ;
- `intent` — намерение пользователя;
- `important_details` — значимые детали;
- `self_check` — результат проверки качества.

Для полного pipeline обычно выполняются четыре обращения
к модели. При временных ошибках или невалидных ответах
возможны дополнительные запросы.

## Архитектура

Проект разделён на интерфейс запуска, клиент LLM, бизнес-логику, классификацию, схемы данных и промпты. Основные точки входа находятся в корне репозитория; реализация — в `src/llm_overall/`.

```text
llm_overall/
├── main.py                         # CLI: basic, routed и full; --text, --demo, --output
├── run_day05.py                    # Демонстрационный запуск цепочки Дня 5
├── pyproject.toml                  # Зависимости и конфигурация pytest
├── .env.example                    # Шаблон конфигурации API
├── README.md                       # Установка, запуск и устройство проекта
├── examples/
│   ├── sample_inputs.json         # Примеры базового и routed-режимов
│   ├── full_pipeline_inputs.json  # Пять сценариев полного pipeline
│   └── evaluate_day04.py          # Оценка классификации и routing
├── docs/
│   ├── roadmap.md                  # Этапы разработки
│   ├── day05_report.md             # Результаты multi-step chain
│   ├── day06_report.md             # Retry, fallback и негативные тесты
│   └── day07_report.md             # Финальный аудит и проверка проекта
├── tests/                          # Unit- и интеграционные тесты, в том числе CLI
└── src/
    └── llm_overall/
        ├── config.py               # Чтение конфигурации и переменных окружения
        ├── clients/
        │   └── llm_client.py       # OpenAI-совместимый API, retry, паузы, логи
        ├── classification/
        │   ├── categories.py       # Категории и допустимые значения
        │   ├── classifier.py       # Классификация текста и определение intent
        │   └── routing.py          # Инструкция генерации по категории
        ├── core/
        │   ├── pipeline.py         # Базовая обработка (Дни 1–3)
        │   ├── routed_pipeline.py  # Классификация и routing (День 4)
        │   ├── meaning.py          # Извлечение смысла и важных деталей
        │   ├── multi_step_pipeline.py  # Полный пятиэтапный workflow
        │   └── self_check.py       # Проверка ответа на противоречия и пропуски
        ├── models/
        │   ├── schemas.py          # Базовые модели структурированного ответа
        │   ├── routed_output.py    # Схема результата маршрутизации
        │   ├── chain_models.py     # Модели данных для полной цепочки
        │   ├── json_normalization.py # Очистка Markdown-обёрток JSON
        │   └── validation.py       # Проверки и диагностика JSON
        └── prompts/
            ├── prompt_variants.py      # Варианты A/B/C (День 2)
            ├── classification_prompt.py # Промпт классификации
            ├── generation_prompt.py    # Промпт routed-генерации
            ├── meaning_prompt.py       # Промпт извлечения смысла
            ├── chain_generation_prompt.py # Основной и fallback-промпты
            └── self_check_prompt.py    # Промпт проверки качества
```

В пакетных каталогах также находятся служебные файлы `__init__.py`; они опущены для читаемости дерева. `outputs/` создаётся при сохранении результатов и не должен включаться в Git.

### Режимы обработки

| Режим | Команда | Назначение |
|---|---|---|
| Basic | `python main.py --text "..."` | Summary, ключевые мысли и полезный ответ |
| Routed | `python main.py --routed --text "..."` | Классификация, intent и выбор инструкции |
| Full | `python main.py --full --text "..."` | Полная цепочка с промежуточными данными и self-check |

`--routed` и `--full` взаимоисключающие. Опция `--demo` запускает предопределённые примеры, а `--output` сохраняет JSON.

### Алгоритм полного pipeline

```text
Текст пользователя
       |
       v
1. Extract meaning: summary, sentiment, key_points, important_details
       |
       v
2. Classify request: category, intent
       |
       v
3. Build structured fields: сбор промежуточных данных в Python
       |
       v
4. Generate final answer: route instruction + контекст предыдущих шагов
       |                 |
       |          Невалидный ответ?
       |                 +--> Fallback prompt --> повторная валидация
       v
5. Self-check result: противоречия и потерянные детали
       |
       v
Structured JSON: summary, category, sentiment, key_points,
                 final_answer, intent, important_details, self_check
```

В нормальном случае выполняются четыре вызова LLM: извлечение смысла, классификация, генерация и self-check. Третий этап выполняется локально в Python. Дополнительные обращения возможны при retry и fallback.

### Сохранённые возможности предыдущих дней

- **Дни 1–3:** базовый pipeline, сравнительная оценка промптов A/B/C и Pydantic-валидация JSON.
- **День 4:** отдельный routed pipeline с явной функцией `get_route()` для выбора инструкции по категории.
- **День 5:** полная последовательная цепочка и отдельный self-check.
- **День 6:** retry до трёх попыток с exponential backoff, fallback при невалидной генерации, ограничения `final_answer` (80 слов и 2000 символов), диагностические логи.
- **День 7:** интеграция полного workflow в `main.py`, пять демонстрационных сценариев, тесты CLI и подготовка к проверке чистого клона.

Описание этапов приведено в `docs/day05_report.md`, `docs/day06_report.md` и `docs/day07_report.md`.

## Тестирование

```powershell
python -m pip check
python -m ruff check .
python -m ruff format --check .
python -m pytest -q
```

Последняя проверка Дня 7:

- `pytest`: **97 passed**.
- `ruff check`: **All checks passed**.
- `ruff format --check`: **55 files already formatted**.
- `pip check`: **No broken requirements found**.

В отдельном окружении Conda с Python 3.12 проект успешно
установлен через `pip install -e ".[dev]"`.

Пять реальных end-to-end сценариев Gemini завершились
успешно: 20 API-вызовов, пять правильных категорий
и пять успешных результатов self-check.

Для отдельной оценки routed pipeline Дня 4:

```powershell
python -m examples.evaluate_day04
```

Скрипт проверяет десять пользовательских текстов, сохраняет результаты в `outputs/day04_results.json` и подсчитывает показатели успешности.

Ранние прогоны Дня 4 выявили проблемы формата ответа и ограничения API. После исправлений автоматические тесты проходят; повторная полная оценка всех десяти текстов через реальный API отдельно не зафиксирована.

Реальные результаты зависят от доступности API, модели и ограничений квоты.

## Этапы разработки

| День | Тема | Статус |
|---|---|---|
| 1 | Basic LLM Pipeline | Завершён |
| 2 | Prompt Engineering | Завершён |
| 3 | Structured Output and Validation | Завершён |
| 4 | Classification and Routing | Завершён |
| 5 | Multi-step LLM Chain | Завершён |
| 6 | Reliability, Guardrails and Fallback | Завершён |
| 7 | Finalization | Завершён (clean-clone PASS) |

Ход разработки отражён в `docs/roadmap.md`; итоговый аудит требований — в `docs/day07_report.md`.

## Ограничения

- Качество классификации зависит от используемой LLM.
- Routed pipeline Дня 4 выполняет два API-вызова; multi-step pipeline Дня 5 – четыре.
- Массовые проверки могут упираться в RPM-квоту провайдера.
- Self-check реализован в День 5, но может пропускать неподтверждённые заявления и не гарантирует достоверность ответа.
- Retry, fallback и guardrails реализованы, но не гарантируют успешную работу при длительной недоступности API и не устраняют фактические ошибки генерации.
- Время и число обращений к Gemini могут увеличиваться при повторных попытках и fallback.
- Сервис не подключён к реальным системам оплаты, поддержки или управления подписками. Генерируемые ответы не означают фактического выполнения действий.
- Регулятор частоты ограничивает запросы одного экземпляра `LLMClient`, но не координирует разные процессы или клиентов.
- Проверка из отдельного окружения проведена; воспроизводимость подтверждена: новый клон GitHub, 97 passed, Ruff без замечаний.
