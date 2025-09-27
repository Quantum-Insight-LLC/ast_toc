"""Integration tests for file watcher module."""

import os
import tempfile
import time
from pathlib import Path

import pytest

from src.file_watcher.watcher import FileWatcher


def test_should_ignore_large_file_ignored():
    """REQ-05: Игнорирование .git, .venv, __pycache__, файлов > 1 МБ."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create large file (> 1MB)
        large_file = Path(temp_dir) / "large.py"
        with open(large_file, "w") as f:
            f.write("def test():\n    pass\n")
            # Make it > 1MB
            f.write("#" * (1024 * 1024 + 100))

        watcher = FileWatcher(Path(temp_dir), max_file_mb=1.0)

        # Should ignore large file
        assert watcher.should_ignore(large_file)

        # Modify file and check no TOC is added
        with open(large_file, "a") as f:
            f.write("\n# Modified")

        watcher.on_modified(large_file)

        # Check no TOC was added
        with open(large_file) as f:
            content = f.read()
        assert "# === FILE_TOC BEGIN ===" not in content


def test_on_modified_toc_updated_within_1sec():
    """ACPT-01: TOC актуален ≤ 1 сек после изменения файла."""
    with tempfile.TemporaryDirectory() as temp_dir:
        src_dir = Path(temp_dir) / "src"
        src_dir.mkdir()

        test_file = src_dir / "test.py"
        with open(test_file, "w") as f:
            f.write("def test_func():\n    pass\n")

        watcher = FileWatcher(src_dir)
        watcher.start()

        # Measure latency
        start_time = time.time()
        watcher.on_modified(test_file)

        # Wait for TOC update
        assert watcher.wait_for_toc_update(test_file, timeout=1.0)

        latency_ms = (time.time() - start_time) * 1000
        assert latency_ms <= 1000  # ACPT-01: ≤ 1 sec

        # Verify TOC was added
        with open(test_file) as f:
            content = f.read()
        assert "# === FILE_TOC BEGIN ===" in content


def test_start_monitoring_watch_directory():
    """CONTRACT: FILE-CREATE-TOC - мониторинг каталога."""
    with tempfile.TemporaryDirectory() as temp_dir:
        src_dir = Path(temp_dir) / "src"
        src_dir.mkdir()

        watcher = FileWatcher(src_dir)
        watcher.start()

        assert watcher.is_running

        # Create file in subdirectory
        sub_dir = src_dir / "sub"
        sub_dir.mkdir()
        test_file = sub_dir / "test.py"

        with open(test_file, "w") as f:
            f.write("def test():\n    pass\n")

        watcher.on_modified(test_file)

        # Check TOC was added
        with open(test_file) as f:
            content = f.read()
        assert "# === FILE_TOC BEGIN ===" in content


def test_stop_monitoring_graceful_shutdown():
    """CONTRACT: CLI-STOP - graceful shutdown демона."""
    with tempfile.TemporaryDirectory() as temp_dir:
        src_dir = Path(temp_dir) / "src"
        src_dir.mkdir()

        watcher = FileWatcher(src_dir)
        watcher.start()
        assert watcher.is_running

        watcher.stop(timeout=0.1)
        assert not watcher.is_running

        # After stop, modifications should not be processed
        test_file = src_dir / "test.py"
        with open(test_file, "w") as f:
            f.write("def test():\n    pass\n")

        watcher.on_modified(test_file)

        # No TOC should be added
        with open(test_file) as f:
            content = f.read()
        assert "# === FILE_TOC BEGIN ===" not in content


def test_ignore_system_directories():
    """CONTRACT: FILE-IGNORE-BIG - игнорирование системных каталогов."""
    with tempfile.TemporaryDirectory() as temp_dir:
        src_dir = Path(temp_dir) / "src"
        src_dir.mkdir()

        # Create system directories
        cache_dir = src_dir / "__pycache__"
        cache_dir.mkdir()
        git_dir = src_dir / ".git"
        git_dir.mkdir()
        venv_dir = src_dir / ".venv"
        venv_dir.mkdir()

        # Create files in system directories
        cache_file = cache_dir / "test.pyc"
        git_file = git_dir / "test.py"
        venv_file = venv_dir / "test.py"

        for file_path in [cache_file, git_file, venv_file]:
            with open(file_path, "w") as f:
                f.write("def test():\n    pass\n")

        watcher = FileWatcher(src_dir)

        # All should be ignored
        assert watcher.should_ignore(cache_file)
        assert watcher.should_ignore(git_file)
        assert watcher.should_ignore(venv_file)


def test_include_exclude_patterns():
    """CONTRACT: CONFIG - поддержка include/exclude паттернов."""
    with tempfile.TemporaryDirectory() as temp_dir:
        src_dir = Path(temp_dir) / "src"
        src_dir.mkdir()

        # Create files
        py_file = src_dir / "test.py"
        txt_file = src_dir / "test.txt"
        excluded_file = src_dir / "excluded.py"

        for file_path in [py_file, txt_file, excluded_file]:
            with open(file_path, "w") as f:
                f.write("def test():\n    pass\n")

        # Test include pattern
        watcher = FileWatcher(src_dir, include=["**/*.py"])
        assert not watcher.should_ignore(py_file)
        assert watcher.should_ignore(txt_file)

        # Test exclude pattern
        watcher = FileWatcher(src_dir, exclude=["**/excluded.py"])
        assert not watcher.should_ignore(py_file)
        assert watcher.should_ignore(excluded_file)
