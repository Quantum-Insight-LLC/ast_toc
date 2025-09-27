"""Unit tests for TOC generator module."""

import os
import tempfile

import pytest

from src.toc_generator.generator import TOCGenerator


def test_generate_toc_formatted_header_with_markers():
    """REQ-01: Хедер содержит FILE_TOC, Module, Purpose, Classes, Functions, Imports, Updated, Generated-By."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("def test_func():\n    pass\n")
        temp_path = f.name

    try:
        generator = TOCGenerator()
        ast_structure = {
            "classes": ["class TestClass"],
            "functions": ["def test_func()"],
            "imports": ["import os"],
        }

        generator.generate_toc(temp_path, ast_structure)

        with open(temp_path, encoding="utf-8") as f:
            content = f.read()

        # Check TOC block is at the very top
        assert content.startswith("# === FILE_TOC BEGIN ===")

        # Check all required fields are present
        assert "FILE_TOC" in content
        assert "Module:" in content
        assert "Purpose:" in content
        assert "Classes:" in content
        assert "Functions:" in content
        assert "Imports:" in content
        assert "Updated:" in content
        assert "Generated-By:" in content

        # Check markers
        assert "# === FILE_TOC BEGIN ===" in content
        assert "# === FILE_TOC END ===" in content

    finally:
        os.unlink(temp_path)


def test_generate_toc_header_above_docstring():
    """REQ-02: Хедер размещается в начале файла или над модульным docstring."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write('"""Module docstring."""\n\ndef test_func():\n    pass\n')
        temp_path = f.name

    try:
        generator = TOCGenerator()
        ast_structure = {"classes": [], "functions": ["def test_func()"], "imports": []}

        generator.generate_toc(temp_path, ast_structure)

        with open(temp_path, encoding="utf-8") as f:
            content = f.read()

        # TOC should be above docstring
        lines = content.split("\n")
        toc_begin_idx = next(
            i for i, line in enumerate(lines) if "# === FILE_TOC BEGIN ===" in line
        )
        docstring_idx = next(
            i for i, line in enumerate(lines) if '"""Module docstring."""' in line
        )

        assert toc_begin_idx < docstring_idx
        assert '"""Module docstring."""' in content  # Docstring preserved

    finally:
        os.unlink(temp_path)


def test_generate_toc_atomic_write_ok():
    """REQ-06: Атомарная запись с сохранением кодировки и перевода строк."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("def test_func():\n    pass\n")
        temp_path = f.name

    try:
        generator = TOCGenerator()
        ast_structure = {"classes": [], "functions": ["def test_func()"], "imports": []}

        generator.generate_toc(temp_path, ast_structure)

        # Check file is complete and valid
        with open(temp_path, encoding="utf-8") as f:
            content = f.read()

        assert "# === FILE_TOC BEGIN ===" in content
        assert "def test_func():" in content
        assert "    pass" in content

        # Check no partial files exist
        temp_dir = os.path.dirname(temp_path)
        temp_files = [f for f in os.listdir(temp_dir) if f.startswith(".ast_toc_tmp_")]
        assert len(temp_files) == 0

    finally:
        os.unlink(temp_path)


def test_generate_toc_preserve_encoding():
    """CONTRACT: FILE-CREATE-TOC - сохранение кодировки файла."""
    # Create file with UTF-8 BOM
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".py", delete=False) as f:
        content = "def test_func():\n    pass\n"
        f.write(content.encode("utf-8-sig"))
        temp_path = f.name

    try:
        generator = TOCGenerator()
        ast_structure = {"classes": [], "functions": ["def test_func()"], "imports": []}

        generator.generate_toc(temp_path, ast_structure)

        # Check encoding preserved
        with open(temp_path, "rb") as f:
            content_bytes = f.read()

        # Should still have UTF-8 BOM
        assert content_bytes.startswith(b"\xef\xbb\xbf")

    finally:
        os.unlink(temp_path)


def test_generate_toc_preserve_line_endings():
    """CONTRACT: FILE-CREATE-TOC - сохранение переводов строк."""
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".py", delete=False) as f:
        content = "def test_func():\r\n    pass\r\n"
        f.write(content.encode("utf-8"))
        temp_path = f.name

    try:
        generator = TOCGenerator()
        ast_structure = {"classes": [], "functions": ["def test_func()"], "imports": []}

        generator.generate_toc(temp_path, ast_structure)

        # Check line endings preserved
        with open(temp_path, "rb") as f:
            content_bytes = f.read()

        assert b"\r\n" in content_bytes

    finally:
        os.unlink(temp_path)


def test_generate_toc_insert_at_top():
    """CONTRACT: FILE-CREATE-TOC - вставка TOC блока в начало файла."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("# Comment\nimport os\ndef test_func():\n    pass\n")
        temp_path = f.name

    try:
        generator = TOCGenerator()
        ast_structure = {
            "classes": [],
            "functions": ["def test_func()"],
            "imports": ["import os"],
        }

        generator.generate_toc(temp_path, ast_structure)

        with open(temp_path, encoding="utf-8") as f:
            content = f.read()

        # TOC should be at the very top
        assert content.startswith("# === FILE_TOC BEGIN ===")

        # No empty lines before BEGIN
        lines = content.split("\n")
        assert lines[0] == "# === FILE_TOC BEGIN ==="

    finally:
        os.unlink(temp_path)


def test_generate_toc_update_existing():
    """CONTRACT: FILE-CREATE-TOC - обновление существующего TOC блока."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(
            "# === FILE_TOC BEGIN ===\nFILE_TOC\nModule: old\n# === FILE_TOC END ===\n\ndef old_func():\n    pass\n"
        )
        temp_path = f.name

    try:
        generator = TOCGenerator()
        ast_structure = {"classes": [], "functions": ["def new_func()"], "imports": []}

        generator.generate_toc(temp_path, ast_structure)

        with open(temp_path, encoding="utf-8") as f:
            content = f.read()

        # Should have only one TOC block
        begin_count = content.count("# === FILE_TOC BEGIN ===")
        end_count = content.count("# === FILE_TOC END ===")
        assert begin_count == 1
        assert end_count == 1

        # Should have updated function count
        assert "Functions: 1" in content

    finally:
        os.unlink(temp_path)
