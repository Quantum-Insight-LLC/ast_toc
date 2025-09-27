"""End-to-end tests for CLI module."""

import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest
import yaml


def test_start_exit_code_0():
    """REQ-04: CLI команды start - успешный запуск демона."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create config
        config_file = Path(temp_dir) / ".ast_toc.yaml"
        config_data = {
            "watch_path": str(Path(temp_dir) / "src"),
            "pid_file": str(Path(temp_dir) / ".ast_toc.pid"),
            "log_file": str(Path(temp_dir) / ".ast_toc.log"),
            "insert_above_docstring": True,
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Create src directory
        src_dir = Path(temp_dir) / "src"
        src_dir.mkdir()

        # Change to temp directory

        try:
            # Run start command
            result = subprocess.run(
                [sys.executable, "-m", "src.cli.cli", "start"],
                capture_output=True,
                text=True,
                cwd=temp_dir,
                env={**os.environ, "PYTHONPATH": os.getcwd()},
            )

            assert result.returncode == 0
            assert "daemon_started" in result.stdout

            # Check PID file exists
            pid_file = Path(temp_dir) / ".ast_toc.pid"
            assert pid_file.exists()

            # Check log file exists
            log_file = Path(temp_dir) / ".ast_toc.log"
            assert log_file.exists()

        finally:
            # Clean up any running daemons
            try:
                subprocess.run(
                    [sys.executable, "-m", "src.cli.cli", "stop"],
                    capture_output=True,
                    text=True,
                    cwd=temp_dir,
                    env={**os.environ, "PYTHONPATH": os.getcwd()},
                )
            except Exception:
                pass


def test_stop_exit_code_0():
    """REQ-04: CLI команды stop - успешная остановка демона."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create config
        config_file = Path(temp_dir) / ".ast_toc.yaml"
        config_data = {
            "watch_path": str(Path(temp_dir) / "src"),
            "pid_file": str(Path(temp_dir) / ".ast_toc.pid"),
            "log_file": str(Path(temp_dir) / ".ast_toc.log"),
            "insert_above_docstring": True,
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Create src directory
        src_dir = Path(temp_dir) / "src"
        src_dir.mkdir()

        # Change to temp directory

        try:
            # Start daemon
            subprocess.run(
                [sys.executable, "-m", "src.cli.cli", "start"],
                capture_output=True,
                text=True,
                cwd=temp_dir,
                env={**os.environ, "PYTHONPATH": os.getcwd()},
            )

            # Stop daemon
            result = subprocess.run(
                [sys.executable, "-m", "src.cli.cli", "stop"],
                capture_output=True,
                text=True,
                cwd=temp_dir,
                env={**os.environ, "PYTHONPATH": os.getcwd()},
            )

            assert result.returncode == 0
            assert "daemon_stopped" in result.stdout

            # Check PID file removed
            pid_file = Path(temp_dir) / ".ast_toc.pid"
            assert not pid_file.exists()

        finally:
            # Clean up any running daemons
            try:
                subprocess.run(
                    [sys.executable, "-m", "src.cli.cli", "stop"],
                    capture_output=True,
                    text=True,
                    cwd=temp_dir,
                    env={**os.environ, "PYTHONPATH": os.getcwd()},
                )
            except Exception:
                pass


def test_status_output_contains_pid():
    """REQ-04: CLI команды status - вывод running + PID или stopped."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create config
        config_file = Path(temp_dir) / ".ast_toc.yaml"
        config_data = {
            "watch_path": str(Path(temp_dir) / "src"),
            "pid_file": str(Path(temp_dir) / ".ast_toc.pid"),
            "log_file": str(Path(temp_dir) / ".ast_toc.log"),
            "insert_above_docstring": True,
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Create src directory
        src_dir = Path(temp_dir) / "src"
        src_dir.mkdir()

        # Change to temp directory

        try:
            # Start daemon
            subprocess.run(
                [sys.executable, "-m", "src.cli.cli", "start"],
                capture_output=True,
                text=True,
                cwd=temp_dir,
                env={**os.environ, "PYTHONPATH": os.getcwd()},
            )

            # Check status
            result = subprocess.run(
                [sys.executable, "-m", "src.cli.cli", "status"],
                capture_output=True,
                text=True,
                cwd=temp_dir,
                env={**os.environ, "PYTHONPATH": os.getcwd()},
            )

            assert result.returncode == 0
            assert "running (pid=" in result.stdout

        finally:
            # Clean up any running daemons
            try:
                subprocess.run(
                    [sys.executable, "-m", "src.cli.cli", "stop"],
                    capture_output=True,
                    text=True,
                    cwd=temp_dir,
                    env={**os.environ, "PYTHONPATH": os.getcwd()},
                )
            except Exception:
                pass


def test_start_logging_levels_present():
    """REQ-07: Логирование с уровнями INFO/ERROR/DEBUG в .ast_toc.log."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create config
        config_file = Path(temp_dir) / ".ast_toc.yaml"
        config_data = {
            "watch_path": str(Path(temp_dir) / "src"),
            "pid_file": str(Path(temp_dir) / ".ast_toc.pid"),
            "log_file": str(Path(temp_dir) / ".ast_toc.log"),
            "insert_above_docstring": True,
            "log_level": "DEBUG",
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Create src directory
        src_dir = Path(temp_dir) / "src"
        src_dir.mkdir()

        # Change to temp directory

        try:
            # Start daemon
            subprocess.run(
                [sys.executable, "-m", "src.cli.cli", "start"],
                capture_output=True,
                text=True,
                cwd=temp_dir,
                env={**os.environ, "PYTHONPATH": os.getcwd()},
            )

            # Check log file
            log_file = Path(temp_dir) / ".ast_toc.log"
            assert log_file.exists()

            with open(log_file) as f:
                log_content = f.read()

            # Check for logging levels
            assert "INFO" in log_content
            assert "ERROR" in log_content
            assert "DEBUG" in log_content

        finally:
            # Clean up any running daemons
            try:
                subprocess.run(
                    [sys.executable, "-m", "src.cli.cli", "stop"],
                    capture_output=True,
                    text=True,
                    cwd=temp_dir,
                    env={**os.environ, "PYTHONPATH": os.getcwd()},
                )
            except Exception:
                pass


def test_start_no_diff_on_restart():
    """ACPT-02: Повторный запуск не даёт диффов."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create config
        config_file = Path(temp_dir) / ".ast_toc.yaml"
        config_data = {
            "watch_path": str(Path(temp_dir) / "src"),
            "pid_file": str(Path(temp_dir) / ".ast_toc.pid"),
            "log_file": str(Path(temp_dir) / ".ast_toc.log"),
            "insert_above_docstring": True,
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Create src directory
        src_dir = Path(temp_dir) / "src"
        src_dir.mkdir()

        # Change to temp directory

        try:
            # First start
            result1 = subprocess.run(
                [sys.executable, "-m", "src.cli.cli", "start"],
                capture_output=True,
                text=True,
                cwd=temp_dir,
                env={**os.environ, "PYTHONPATH": os.getcwd()},
            )
            assert result1.returncode == 0

            # Stop
            subprocess.run(
                [sys.executable, "-m", "src.cli.cli", "stop"],
                capture_output=True,
                text=True,
                cwd=temp_dir,
                env={**os.environ, "PYTHONPATH": os.getcwd()},
            )

            # Second start
            result2 = subprocess.run(
                [sys.executable, "-m", "src.cli.cli", "start"],
                capture_output=True,
                text=True,
                cwd=temp_dir,
                env={**os.environ, "PYTHONPATH": os.getcwd()},
            )
            assert result2.returncode == 0

            # No diff on restart
            assert result1.stdout == result2.stdout

        finally:
            # Clean up any running daemons
            try:
                subprocess.run(
                    [sys.executable, "-m", "src.cli.cli", "stop"],
                    capture_output=True,
                    text=True,
                    cwd=temp_dir,
                    env={**os.environ, "PYTHONPATH": os.getcwd()},
                )
            except Exception:
                pass


def test_cli_start_daemon_started():
    """CONTRACT: CLI-START - запуск демона."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create config
        config_file = Path(temp_dir) / ".ast_toc.yaml"
        config_data = {
            "watch_path": str(Path(temp_dir) / "src"),
            "pid_file": str(Path(temp_dir) / ".ast_toc.pid"),
            "log_file": str(Path(temp_dir) / ".ast_toc.log"),
            "insert_above_docstring": True,
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Create src directory
        src_dir = Path(temp_dir) / "src"
        src_dir.mkdir()

        # Change to temp directory

        try:
            # Start daemon
            result = subprocess.run(
                [sys.executable, "-m", "src.cli.cli", "start"],
                capture_output=True,
                text=True,
                cwd=temp_dir,
                env={**os.environ, "PYTHONPATH": os.getcwd()},
            )

            assert result.returncode == 0
            assert "daemon_started" in result.stdout

        finally:
            # Clean up any running daemons
            try:
                subprocess.run(
                    [sys.executable, "-m", "src.cli.cli", "stop"],
                    capture_output=True,
                    text=True,
                    cwd=temp_dir,
                    env={**os.environ, "PYTHONPATH": os.getcwd()},
                )
            except Exception:
                pass


def test_cli_start_already_running_error():
    """CONTRACT: CLI-START - ошибка уже запущен."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create config
        config_file = Path(temp_dir) / ".ast_toc.yaml"
        config_data = {
            "watch_path": str(Path(temp_dir) / "src"),
            "pid_file": str(Path(temp_dir) / ".ast_toc.pid"),
            "log_file": str(Path(temp_dir) / ".ast_toc.log"),
            "insert_above_docstring": True,
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Create src directory
        src_dir = Path(temp_dir) / "src"
        src_dir.mkdir()

        # Change to temp directory

        try:
            # Start daemon
            subprocess.run(
                [sys.executable, "-m", "src.cli.cli", "start"],
                capture_output=True,
                text=True,
                cwd=temp_dir,
                env={**os.environ, "PYTHONPATH": os.getcwd()},
            )

            # Try to start again
            result = subprocess.run(
                [sys.executable, "-m", "src.cli.cli", "start"],
                capture_output=True,
                text=True,
                cwd=temp_dir,
                env={**os.environ, "PYTHONPATH": os.getcwd()},
            )

            assert result.returncode == 1
            assert "ERR-ALREADY-RUNNING" in result.stdout

        finally:
            # Clean up any running daemons
            try:
                subprocess.run(
                    [sys.executable, "-m", "src.cli.cli", "stop"],
                    capture_output=True,
                    text=True,
                    cwd=temp_dir,
                    env={**os.environ, "PYTHONPATH": os.getcwd()},
                )
            except Exception:
                pass


def test_cli_start_config_error():
    """CONTRACT: CLI-START - ошибка конфигурации."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create invalid config
        config_file = Path(temp_dir) / ".ast_toc.yaml"
        config_data = {
            "watch_path": str(Path(temp_dir) / "src"),
            "pid_file": str(Path(temp_dir) / ".ast_toc.pid"),
            "log_file": str(Path(temp_dir) / ".ast_toc.log"),
            # Missing insert_above_docstring
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Change to temp directory

        try:
            # Try to start with invalid config
            result = subprocess.run(
                [sys.executable, "-m", "src.cli.cli", "start"],
                capture_output=True,
                text=True,
                cwd=temp_dir,
                env={**os.environ, "PYTHONPATH": os.getcwd()},
            )

            assert result.returncode == 1
            assert "ERR-CONFIG" in result.stdout

        finally:
            # Clean up any running daemons
            try:
                subprocess.run(
                    [sys.executable, "-m", "src.cli.cli", "stop"],
                    capture_output=True,
                    text=True,
                    cwd=temp_dir,
                    env={**os.environ, "PYTHONPATH": os.getcwd()},
                )
            except Exception:
                pass


def test_cli_stop_daemon_stopped():
    """CONTRACT: CLI-STOP - остановка демона."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create config
        config_file = Path(temp_dir) / ".ast_toc.yaml"
        config_data = {
            "watch_path": str(Path(temp_dir) / "src"),
            "pid_file": str(Path(temp_dir) / ".ast_toc.pid"),
            "log_file": str(Path(temp_dir) / ".ast_toc.log"),
            "insert_above_docstring": True,
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Create src directory
        src_dir = Path(temp_dir) / "src"
        src_dir.mkdir()

        # Change to temp directory

        try:
            # Start daemon
            subprocess.run(
                [sys.executable, "-m", "src.cli.cli", "start"],
                capture_output=True,
                text=True,
                cwd=temp_dir,
                env={**os.environ, "PYTHONPATH": os.getcwd()},
            )

            # Stop daemon
            result = subprocess.run(
                [sys.executable, "-m", "src.cli.cli", "stop"],
                capture_output=True,
                text=True,
                cwd=temp_dir,
                env={**os.environ, "PYTHONPATH": os.getcwd()},
            )

            assert result.returncode == 0
            assert "daemon_stopped" in result.stdout

        finally:
            # Clean up any running daemons
            try:
                subprocess.run(
                    [sys.executable, "-m", "src.cli.cli", "stop"],
                    capture_output=True,
                    text=True,
                    cwd=temp_dir,
                    env={**os.environ, "PYTHONPATH": os.getcwd()},
                )
            except Exception:
                pass


def test_cli_stop_not_running_error():
    """CONTRACT: CLI-STOP - ошибка не запущен."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create config
        config_file = Path(temp_dir) / ".ast_toc.yaml"
        config_data = {
            "watch_path": str(Path(temp_dir) / "src"),
            "pid_file": str(Path(temp_dir) / ".ast_toc.pid"),
            "log_file": str(Path(temp_dir) / ".ast_toc.log"),
            "insert_above_docstring": True,
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Create src directory
        src_dir = Path(temp_dir) / "src"
        src_dir.mkdir()

        # Change to temp directory

        try:
            # Try to stop without starting
            result = subprocess.run(
                [sys.executable, "-m", "src.cli.cli", "stop"],
                capture_output=True,
                text=True,
                cwd=temp_dir,
                env={**os.environ, "PYTHONPATH": os.getcwd()},
            )

            assert result.returncode == 1
            assert "ERR-NOT-RUNNING" in result.stdout

        finally:
            # Clean up any running daemons
            try:
                subprocess.run(
                    [sys.executable, "-m", "src.cli.cli", "stop"],
                    capture_output=True,
                    text=True,
                    cwd=temp_dir,
                    env={**os.environ, "PYTHONPATH": os.getcwd()},
                )
            except Exception:
                pass


def test_cli_status_running_pid():
    """CONTRACT: CLI-STATUS - вывод running + PID."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create config
        config_file = Path(temp_dir) / ".ast_toc.yaml"
        config_data = {
            "watch_path": str(Path(temp_dir) / "src"),
            "pid_file": str(Path(temp_dir) / ".ast_toc.pid"),
            "log_file": str(Path(temp_dir) / ".ast_toc.log"),
            "insert_above_docstring": True,
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Create src directory
        src_dir = Path(temp_dir) / "src"
        src_dir.mkdir()

        # Change to temp directory

        try:
            # Start daemon
            subprocess.run(
                [sys.executable, "-m", "src.cli.cli", "start"],
                capture_output=True,
                text=True,
                cwd=temp_dir,
                env={**os.environ, "PYTHONPATH": os.getcwd()},
            )

            # Check status
            result = subprocess.run(
                [sys.executable, "-m", "src.cli.cli", "status"],
                capture_output=True,
                text=True,
                cwd=temp_dir,
                env={**os.environ, "PYTHONPATH": os.getcwd()},
            )

            assert result.returncode == 0
            assert "running (pid=" in result.stdout

        finally:
            # Clean up any running daemons
            try:
                subprocess.run(
                    [sys.executable, "-m", "src.cli.cli", "stop"],
                    capture_output=True,
                    text=True,
                    cwd=temp_dir,
                    env={**os.environ, "PYTHONPATH": os.getcwd()},
                )
            except Exception:
                pass


def test_cli_status_stopped():
    """CONTRACT: CLI-STATUS - вывод stopped."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create config
        config_file = Path(temp_dir) / ".ast_toc.yaml"
        config_data = {
            "watch_path": str(Path(temp_dir) / "src"),
            "pid_file": str(Path(temp_dir) / ".ast_toc.pid"),
            "log_file": str(Path(temp_dir) / ".ast_toc.log"),
            "insert_above_docstring": True,
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Create src directory
        src_dir = Path(temp_dir) / "src"
        src_dir.mkdir()

        # Change to temp directory

        try:
            # Check status without starting
            result = subprocess.run(
                [sys.executable, "-m", "src.cli.cli", "status"],
                capture_output=True,
                text=True,
                cwd=temp_dir,
                env={**os.environ, "PYTHONPATH": os.getcwd()},
            )

            assert result.returncode == 0
            assert "stopped" in result.stdout

        finally:
            # Clean up any running daemons
            try:
                subprocess.run(
                    [sys.executable, "-m", "src.cli.cli", "stop"],
                    capture_output=True,
                    text=True,
                    cwd=temp_dir,
                    env={**os.environ, "PYTHONPATH": os.getcwd()},
                )
            except Exception:
                pass
