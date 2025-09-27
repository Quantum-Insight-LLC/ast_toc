#!/usr/bin/env python3
"""
Валидатор трассируемости требований.
Проверяет корректность связей между PMM, контрактами и тестами.
"""

import csv
import os
import sys
import yaml
from pathlib import Path


def load_yaml(file_path):
    """Загружает YAML файл."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"ERROR: Не удалось загрузить {file_path}: {e}")
        sys.exit(1)


def load_csv(file_path):
    """Загружает CSV файл."""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:  # utf-8-sig для обработки BOM
            reader = csv.DictReader(f)
            return list(reader)
    except Exception as e:
        print(f"ERROR: Не удалось загрузить {file_path}: {e}")
        sys.exit(1)


def validate_csv_columns(csv_data):
    """Проверяет корректность колонок CSV."""
    expected_columns = {
        'req_id', 'req_desc', 'contract_id', 'module', 'file', 
        'symbol', 'test_id', 'test_level', 'metric_acceptance', 'notes'
    }
    
    if not csv_data:
        print("ERROR: CSV файл пустой")
        return False
        
    actual_columns = set(csv_data[0].keys())
    if actual_columns != expected_columns:
        missing = expected_columns - actual_columns
        extra = actual_columns - expected_columns
        if missing:
            print(f"ERROR: Отсутствуют колонки: {missing}")
        if extra:
            print(f"ERROR: Лишние колонки: {extra}")
        return False
    
    print("✓ Колонки CSV корректны")
    return True


def validate_required_fields(csv_data):
    """Проверяет отсутствие пустых req_id и test_id."""
    errors = []
    
    for i, row in enumerate(csv_data, 1):
        if not row.get('req_id', '').strip():
            errors.append(f"Строка {i}: пустой req_id")
        if not row.get('test_id', '').strip():
            errors.append(f"Строка {i}: пустой test_id")
    
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return False
    
    print("✓ Все req_id и test_id заполнены")
    return True


def extract_contract_ids(contracts):
    """Извлекает все contract_id из contracts.yaml."""
    contract_ids = set()
    
    # CLI команды
    for cmd in contracts.get('cli', {}).get('commands', []):
        if cmd.get('id'):
            contract_ids.add(cmd['id'])
    
    # File behaviors
    for behavior in contracts.get('files', {}).get('behaviors', []):
        if behavior.get('id'):
            contract_ids.add(behavior['id'])
    
    # Config
    if contracts.get('config'):
        contract_ids.add('CONFIG')
    
    # Data schemas
    for schema in contracts.get('data', {}).get('schemas', []):
        if schema.get('id'):
            contract_ids.add(schema['id'])
    
    return contract_ids


def validate_contract_coverage(csv_data, contracts):
    """Проверяет покрытие контрактов тестами."""
    contract_ids = extract_contract_ids(contracts)
    csv_contract_ids = {row['contract_id'] for row in csv_data if row['contract_id'].strip()}
    
    errors = []
    for contract_id in contract_ids:
        if contract_id not in csv_contract_ids:
            errors.append(f"Контракт {contract_id} не покрыт тестами")
    
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return False
    
    print("✓ Все контракты покрыты тестами")
    return True


def validate_test_files(csv_data):
    """Проверяет существование тестовых файлов."""
    errors = []
    
    for i, row in enumerate(csv_data, 1):
        test_id = row.get('test_id', '').strip()
        if test_id:
            # Извлекаем путь к файлу из test_id (формат: tests/unit/test_generator.py::test_function)
            if '::' in test_id:
                file_path = test_id.split('::')[0]
            else:
                file_path = test_id
            
            if not os.path.exists(file_path):
                errors.append(f"Строка {i}: тестовый файл не найден: {file_path}")
    
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return False
    
    print("✓ Все тестовые файлы существуют")
    return True


def validate_no_duplicates(csv_data):
    """Проверяет отсутствие дубликатов по (req_id, test_id)."""
    seen = set()
    errors = []
    
    for i, row in enumerate(csv_data, 1):
        req_id = row.get('req_id', '').strip()
        test_id = row.get('test_id', '').strip()
        key = (req_id, test_id)
        
        if key in seen:
            errors.append(f"Строка {i}: дубликат (req_id={req_id}, test_id={test_id})")
        else:
            seen.add(key)
    
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return False
    
    print("✓ Дубликаты отсутствуют")
    return True


def main():
    """Основная функция валидации."""
    print("=== Валидация трассируемости требований ===\n")
    
    # Определяем пути к файлам
    base_dir = Path(__file__).parent.parent
    pmm_file = base_dir / "docs" / "pmm_ast_toc.yaml"
    contracts_file = base_dir / "docs" / "contracts.yaml"
    trace_file = base_dir / "docs" / "trace_matrix.csv"
    
    # Проверяем существование файлов
    for file_path in [pmm_file, contracts_file, trace_file]:
        if not file_path.exists():
            print(f"ERROR: Файл не найден: {file_path}")
            sys.exit(1)
    
    # Загружаем данные
    print("Загрузка файлов...")
    pmm_data = load_yaml(pmm_file)
    contracts_data = load_yaml(contracts_file)
    csv_data = load_csv(trace_file)
    print("✓ Файлы загружены\n")
    
    # Выполняем валидации
    all_passed = True
    
    print("1. Проверка колонок CSV...")
    all_passed &= validate_csv_columns(csv_data)
    print()
    
    print("2. Проверка обязательных полей...")
    all_passed &= validate_required_fields(csv_data)
    print()
    
    print("3. Проверка покрытия контрактов...")
    all_passed &= validate_contract_coverage(csv_data, contracts_data)
    print()
    
    print("4. Проверка существования тестовых файлов...")
    all_passed &= validate_test_files(csv_data)
    print()
    
    print("5. Проверка на дубликаты...")
    all_passed &= validate_no_duplicates(csv_data)
    print()
    
    # Результат
    if all_passed:
        print("🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!")
        print(f"✓ Проверено {len(csv_data)} строк трассируемости")
        sys.exit(0)
    else:
        print("❌ ОБНАРУЖЕНЫ ОШИБКИ В ТРАССИРУЕМОСТИ!")
        sys.exit(1)


if __name__ == "__main__":
    main()
