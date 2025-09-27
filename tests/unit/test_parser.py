"""Unit tests for AST parser module."""

import os
import tempfile

import pytest

from src.ast_parser.parser import ASTParser


def test_parse_file_extracted_classes_and_functions():
    """REQ-03: Извлечение структуры через модуль ast с сигнатурами без аннотаций типов."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(
            """import os
from typing import List

class TestClass:
    def method1(self, arg1, arg2):
        pass

    def method2(self, *args, **kwargs):
        pass

def top_function(param1, param2):
    pass

def another_func(*args, **kwargs):
    pass
"""
        )
        temp_path = f.name

    try:
        parser = ASTParser()
        result = parser.parse_file(temp_path)

        # Check structure
        assert "classes" in result
        assert "functions" in result
        assert "imports" in result

        # Check classes
        assert len(result["classes"]) == 1
        assert "class TestClass" in result["classes"][0]

        # Check functions (including methods)
        assert len(result["functions"]) == 4
        assert "TestClass.method1(arg1, arg2)" in result["functions"]
        assert "TestClass.method2(*args, **kwargs)" in result["functions"]
        assert "def top_function(param1, param2)" in result["functions"]
        assert "def another_func(*args, **kwargs)" in result["functions"]

        # Check imports
        assert len(result["imports"]) == 2
        assert "import os" in result["imports"]
        assert "from typing import List" in result["imports"]

    finally:
        os.unlink(temp_path)


def test_parse_file_ignore_nested_functions():
    """CONTRACT: FILE-CREATE-TOC - игнорирование вложенных функций."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(
            """def outer_function():
    def nested_function():
        pass

    class NestedClass:
        def nested_method(self):
            pass

def top_function():
    pass
"""
        )
        temp_path = f.name

    try:
        parser = ASTParser()
        result = parser.parse_file(temp_path)

        # Should only have top-level function
        top_functions = [f for f in result["functions"] if f.startswith("def ")]
        assert len(top_functions) == 2  # outer_function and top_function
        assert "def outer_function()" in result["functions"]
        assert "def top_function()" in result["functions"]

        # Should not have nested functions
        assert "def nested_function()" not in result["functions"]
        assert "NestedClass.nested_method()" not in result["functions"]

    finally:
        os.unlink(temp_path)


def test_parse_file_no_type_annotations():
    """CONTRACT: FILE-CREATE-TOC - сигнатуры без аннотаций типов."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(
            """from typing import List, Dict

class TestClass:
    def method_with_types(self, param1: str, param2: int = 10) -> bool:
        pass

def function_with_types(param: List[str], default: Dict[str, int] = None) -> str:
    pass

def function_without_types(param1, param2):
    pass
"""
        )
        temp_path = f.name

    try:
        parser = ASTParser()
        result = parser.parse_file(temp_path)

        # Check that type annotations are removed
        for func in result["functions"]:
            assert ":" not in func  # No type annotations
            assert "=" not in func  # No default values
            assert "->" not in func  # No return type annotations

        # Check specific functions
        assert "TestClass.method_with_types(param1, param2)" in result["functions"]
        assert "def function_with_types(param, default)" in result["functions"]
        assert "def function_without_types(param1, param2)" in result["functions"]

    finally:
        os.unlink(temp_path)


def test_parse_file_extract_imports():
    """CONTRACT: FILE-CREATE-TOC - извлечение импортов верхнего уровня."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(
            """import os
import sys
from typing import List, Dict
from collections import defaultdict, Counter
from .local_module import local_func
from ..parent_module import parent_func

def some_function():
    import tempfile  # This should be ignored (nested import)
    pass
"""
        )
        temp_path = f.name

    try:
        parser = ASTParser()
        result = parser.parse_file(temp_path)

        # Check imports
        assert len(result["imports"]) == 6
        assert "import os" in result["imports"]
        assert "import sys" in result["imports"]
        assert "from typing import List, Dict" in result["imports"]
        assert "from collections import defaultdict, Counter" in result["imports"]
        assert "from local_module import local_func" in result["imports"]
        assert "from parent_module import parent_func" in result["imports"]

        # Nested import should be ignored
        assert "import tempfile" not in result["imports"]

    finally:
        os.unlink(temp_path)
