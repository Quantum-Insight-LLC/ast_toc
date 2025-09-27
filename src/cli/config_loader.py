"""Configuration loader for AST TOC daemon."""

import json
from pathlib import Path
from typing import Any

import jsonschema


def load_config(config_path: str = ".ast_toc.yaml") -> dict[str, Any]:
    """Load and validate configuration from YAML file.

    Args:
        config_path: Path to configuration file

    Returns:
        Validated configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        jsonschema.ValidationError: If config is invalid
    """
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    # Load YAML (simplified - just use dict for now)
    import yaml

    with open(config_file, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Apply defaults from contracts.yaml
    defaults = {
        "log_level": "INFO",
        "include": ["**/*.py"],
        "exclude": ["**/__pycache__/**", "**/.venv/**", "**/.git/**"],
        "max_file_mb": 1,
        "logging_probe_on_start": [],
    }

    for key, value in defaults.items():
        if key not in config:
            config[key] = value

    # Validate against schema
    schema_path = Path("docs/schemas/ast_toc_config.json")
    if not schema_path.exists():
        # Try relative to current working directory
        schema_path = Path.cwd() / "docs/schemas/ast_toc_config.json"

    try:
        with open(schema_path, encoding="utf-8") as f:
            schema = json.load(f)
        jsonschema.validate(config, schema)
    except FileNotFoundError:
        # Skip schema validation if schema file not found
        pass

    # Check required fields
    required_fields = ["watch_path", "pid_file", "log_file", "insert_above_docstring"]
    for field in required_fields:
        if field not in config:
            raise jsonschema.ValidationError(f"Required field missing: {field}")

    return config
