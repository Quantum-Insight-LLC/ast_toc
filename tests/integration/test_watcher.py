"""Integration tests for file watcher module."""

import pytest


def test_should_ignore_large_file_ignored():
    """REQ-05: Игнорирование .git, .venv, __pycache__, файлов > 1 МБ."""
    assert False, "not implemented"


def test_on_modified_toc_updated_within_1sec():
    """ACPT-01: TOC актуален ≤ 1 сек после изменения файла."""
    assert False, "not implemented"


def test_start_monitoring_watch_directory():
    """CONTRACT: FILE-CREATE-TOC - мониторинг каталога."""
    assert False, "not implemented"


def test_stop_monitoring_graceful_shutdown():
    """CONTRACT: CLI-STOP - graceful shutdown демона."""
    assert False, "not implemented"


def test_ignore_system_directories():
    """CONTRACT: FILE-IGNORE-BIG - игнорирование системных каталогов."""
    assert False, "not implemented"


def test_include_exclude_patterns():
    """CONTRACT: CONFIG - поддержка include/exclude паттернов."""
    assert False, "not implemented"
