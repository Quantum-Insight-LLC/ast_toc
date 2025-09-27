# AST-TOC Daemon

Автоматический генератор структурных заголовков (TOC) для Python файлов на основе AST-анализа.

## Возможности

- 🔍 **AST-парсинг**: Автоматическое извлечение классов, методов, функций и импортов
- 📝 **Генерация TOC**: Структурированные заголовки с метаданными
- 👀 **File Watcher**: Мониторинг изменений файлов в реальном времени
- ⚙️ **CLI**: Команды start/stop/status для управления демоном
- 🔧 **Конфигурация**: Гибкие настройки через `.ast_toc.yaml`

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

```bash
# Запуск демона
ast_toc start

# Проверка статуса
ast_toc status

# Остановка демона
ast_toc stop
```

## Разработка

```bash
# Запуск тестов
pytest

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
│   └── trace_matrix.csv    # Матрица трассируемости
├── tests/                   # Тесты
│   ├── unit/               # Юнит-тесты
│   ├── integration/        # Интеграционные тесты
│   └── e2e/                # E2E тесты
├── tools/                   # Инструменты
│   └── validate_trace.py   # Валидатор трассируемости
├── .github/workflows/       # CI/CD
└── src/                     # Исходный код (будет добавлен)
```

## Требования

- Python ≥ 3.10
- Зависимости: `watchdog`, `pyyaml`

## Лицензия

MIT License
