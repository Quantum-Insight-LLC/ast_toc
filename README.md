# AST-TOC Daemon

Автоматический генератор структурных заголовков (TOC) для Python файлов на основе AST-анализа.

## Возможности

- 🔍 **AST-парсинг**: Автоматическое извлечение классов, методов, функций и импортов
- 📝 **Генерация TOC**: Структурированные заголовки с метаданными и маркерами
- 👀 **File Watcher**: Мониторинг изменений файлов в реальном времени (≤1 сек)
- ⚙️ **CLI**: Команды start/stop/status для управления демоном
- 🔧 **Конфигурация**: Гибкие настройки через `.ast_toc.yaml`
- 🛡️ **Безопасность**: Атомарная запись, сохранение кодировки и переводов строк
- 📊 **Логирование**: Подробные логи с уровнями INFO/ERROR/DEBUG
- 🚀 **Initial Scan**: Автоматическое сканирование и обновление TOC при запуске
- 🎯 **Идемпотентность**: Повторные запуски не создают лишних изменений
- 🧹 **Утилиты**: Скрипт для удаления TOC заголовков

## Установка

```bash
# Клонирование репозитория
git clone https://github.com/Quantum-Insight-LLC/ast_toc.git
cd ast_toc

# Создание виртуального окружения
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# или
.venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements-dev.txt
```

## Настройка Pre-commit хуков

```bash
# Установка pre-commit
pip install pre-commit

# Установка хуков в репозиторий
pre-commit install

# Ручной запуск на всех файлах
pre-commit run --all-files
```

## Использование

### Конфигурация

Создайте файл `.ast_toc.yaml` в корне проекта:

```yaml
watch_path: "./src"
pid_file: ".ast_toc.pid"
log_file: ".ast_toc.log"
insert_above_docstring: true
log_level: "INFO"
include: ["**/*.py"]
exclude: ["**/__pycache__/**", "**/.venv/**", "**/.git/**"]
max_file_mb: 1
logging_probe_on_start: []
initial_scan: true
```

### CLI команды

```bash
# Запуск демона (с initial_scan)
ast_toc start

# Проверка статуса
ast_toc status

# Остановка демона
ast_toc stop
```

### Утилиты

```bash
# Удаление TOC заголовков из файла
python tools/remove_toc_headers.py file.py

# Удаление TOC заголовков из директории
python tools/remove_toc_headers.py src/
```

### Пример TOC заголовка

```python
# === FILE_TOC BEGIN ===
# FILE_TOC
# Module: example
# Purpose: TODO: Add module purpose
# Classes: class MyClass, class AnotherClass
# Functions: MyClass.method(), def standalone_function(), def another_function()
# Imports: import os, from typing import List
# Updated: 2025-09-27 19:47:01
# Generated-By: ast_toc
# === FILE_TOC END ===

"""Module docstring here..."""

import os
from typing import List

class MyClass:
    def method(self):
        pass
```

## Разработка

```bash
# Запуск всех тестов
pytest

# Запуск unit-тестов
pytest tests/unit/ -v

# Запуск интеграционных тестов
pytest tests/integration/ -v

# Запуск e2e-тестов
pytest tests/e2e/ -v

# Проверка покрытия
pytest --cov=src --cov-report=html

# Линтинг
ruff check .

# Форматирование
black .

# Валидация трассируемости
python tools/validate_trace.py
```

## Структура проекта

```
ast_toc/
├── docs/                    # Документация
│   ├── ast_toc_tz.md       # Техническое задание
│   ├── canonical_brief_ast_toc.md
│   ├── pmm_ast_toc.yaml    # Project Memory Map
│   ├── contracts.yaml      # Контракты API
│   ├── trace_matrix.csv    # Матрица трассируемости
│   ├── errors-catalog.yaml # Каталог ошибок
│   ├── schemas/            # JSON схемы
│   └── scenarios/          # BDD сценарии
├── tests/                   # Тесты
│   ├── unit/               # Юнит-тесты (7 тестов)
│   ├── integration/        # Интеграционные тесты (10 тестов)
│   └── e2e/                # E2E тесты (12 тестов)
├── tools/                   # Инструменты
│   ├── validate_trace.py   # Валидатор трассируемости
│   └── remove_toc_headers.py # Удаление TOC заголовков
├── .github/workflows/       # CI/CD
└── src/                     # Исходный код
    ├── ast_parser/         # AST парсер
    ├── toc_generator/      # Генератор TOC
    ├── file_watcher/       # Мониторинг файлов
    └── cli/                # CLI интерфейс
```

## Требования

- Python ≥ 3.10
- Зависимости: `watchdog`, `pyyaml`, `jsonschema`

## Статус проекта

✅ **Готово к использованию**

- [x] Unit-тесты (7/7) - 100% покрытие
- [x] Integration-тесты (10/10) - 100% покрытие
- [x] E2E-тесты (12/12) - 100% покрытие
- [x] CLI интерфейс с командами start/stop/status
- [x] File watcher с мониторингом в реальном времени
- [x] AST парсер для извлечения структуры кода
- [x] TOC генератор с атомарной записью
- [x] Конфигурация через YAML
- [x] Логирование и обработка ошибок
- [x] Initial scan при запуске демона
- [x] Идемпотентность генерации TOC
- [x] Утилита для удаления TOC заголовков
- [x] Соответствие контрактам и требованиям

## Лицензия

MIT License
