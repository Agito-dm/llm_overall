# llm_overall

Проект модульного LLM pipeline для интеллектуальной обработки пользовательского текста на Python.

## Возможности

- Обработка произвольного входного текста.
- Генерация краткого summary.
- Выделение трёх ключевых мыслей.
- Формирование полезного ответа.
- Вывод структурированного JSON.
- Работа с OpenAI-совместимым API.
- Базовая проверка ответа и обработка ошибок.

Проект развивается по семи этапам. Классификация, routing, расширенная Pydantic-валидация, multi-step workflow и fallback добавляются в последующие дни.

## Технологии

Python 3.12, OpenAI Python SDK, Pydantic, python-dotenv, pytest, Ruff.

## Установка

```powershell
git clone https://github.com/Agito-dm/llm_overall
cd llm_overall
conda create -n llm_overall python=3.12 -y
conda activate llm_overall
python -m pip install -e ".[dev]"
```

## Конфигурация

Создайте `.env` на основе `.env.example`:

```powershell
Copy-Item .env.example .env
```

Укажите API-ключ, название модели и при необходимости базовый URL совместимого API.

Секретные ключи не должны попадать в Git.

## Запуск

Обработка собственного текста:

```powershell
python main.py --text "Объясни принцип работы LLM"
```

Запуск трёх демонстрационных примеров:

```powershell
python main.py --demo --output outputs/day01_results.json
```

## Тестирование

```powershell
python -m pytest -v
python -m ruff check .
python -m pip check
```

## Архитектура

- `main.py` — интерфейс командной строки.
- `config.py` — конфигурация приложения.
- `llm_client.py` — API-клиент.
- `prompts.py` — шаблоны промптов.
- `pipeline.py` — обработка входного текста.
- `examples/` — демонстрационные данные.
- `tests/` — автоматические тесты.

## Roadmap

Требования и прогресс семи этапов находятся в `docs/roadmap.md`.

## Текущий статус

День 1 — базовый LLM pipeline реализован и проверен на трёх примерах.