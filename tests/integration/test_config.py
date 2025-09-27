"""Integration tests for configuration module."""

import tempfile
from pathlib import Path

import jsonschema
import pytest
import yaml

from src.cli.config_loader import load_config


def test_load_config_config_schema_valid():
    """REQ-08: Конфигурация через .ast_toc.yaml с настройками watch_path, include/exclude."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / ".ast_toc.yaml"

        config_data = {
            "watch_path": "./src",
            "pid_file": ".ast_toc.pid",
            "log_file": ".ast_toc.log",
            "insert_above_docstring": True,
            "log_level": "INFO",
            "include": ["**/*.py"],
            "exclude": ["**/__pycache__/**", "**/.venv/**"],
            "max_file_mb": 1.5,
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Load and validate config
        config = load_config(str(config_file))

        # Check schema validation passed
        assert config["watch_path"] == "./src"
        assert config["include"] == ["**/*.py"]
        assert config["exclude"] == ["**/__pycache__/**", "**/.venv/**"]
        assert config["max_file_mb"] == 1.5


def test_config_required_fields():
    """CONTRACT: CONFIG - обязательные поля: watch_path, pid_file, log_file, insert_above_docstring."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / ".ast_toc.yaml"

        # Missing required field
        config_data = {
            "watch_path": "./src",
            "pid_file": ".ast_toc.pid",
            "log_file": ".ast_toc.log",
            # Missing insert_above_docstring
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Should raise validation error
        with pytest.raises(jsonschema.ValidationError):
            load_config(str(config_file))


def test_config_defaults():
    """CONTRACT: CONFIG - значения по умолчанию."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / ".ast_toc.yaml"

        # Minimal config with only required fields
        config_data = {
            "watch_path": "./src",
            "pid_file": ".ast_toc.pid",
            "log_file": ".ast_toc.log",
            "insert_above_docstring": True,
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        config = load_config(str(config_file))

        # Check defaults are applied
        assert config["log_level"] == "INFO"
        assert config["include"] == ["**/*.py"]
        assert config["exclude"] == ["**/__pycache__/**", "**/.venv/**", "**/.git/**"]
        assert config["max_file_mb"] == 1


def test_config_schema_validation():
    """CONTRACT: CONFIG - валидация схемы конфигурации."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / ".ast_toc.yaml"

        # Invalid max_file_mb (too small)
        config_data = {
            "watch_path": "./src",
            "pid_file": ".ast_toc.pid",
            "log_file": ".ast_toc.log",
            "insert_above_docstring": True,
            "max_file_mb": 0.05,  # Below minimum 0.1
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Should raise validation error
        with pytest.raises(jsonschema.ValidationError):
            load_config(str(config_file))

        # Invalid log_level
        config_data["max_file_mb"] = 1.0
        config_data["log_level"] = "INVALID"

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        with pytest.raises(jsonschema.ValidationError):
            load_config(str(config_file))
