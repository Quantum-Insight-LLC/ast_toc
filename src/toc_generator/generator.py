"""TOC generator for Python files."""

import os
import shutil
import tempfile
import tokenize
from datetime import datetime


class TOCGenerator:
    """Generator for table of contents headers in Python files."""

    def __init__(self):
        self.begin_marker = "# === FILE_TOC BEGIN ==="
        self.end_marker = "# === FILE_TOC END ==="

    def generate_toc(
        self,
        file_path: str,
        ast_structure: dict[str, list[str]],
        insert_above_docstring: bool = True,
    ) -> None:
        """Generate and insert TOC header into Python file.

        Args:
            file_path: Path to Python file
            ast_structure: Dict with classes, functions, imports
            insert_above_docstring: Whether to insert above docstring
        """
        # Read original file
        encoding, line_ending = self._detect_file_properties(file_path)

        with open(file_path, encoding=encoding, newline="") as f:
            content = f.read()

        # Generate TOC content
        toc_content = self._create_toc_content(file_path, ast_structure)

        # Insert TOC into content
        new_content = self._insert_toc(content, toc_content, insert_above_docstring)

        # Write atomically
        self._atomic_write(file_path, new_content, encoding, line_ending)

    def _detect_file_properties(self, file_path: str) -> tuple[str, str]:
        """Detect file encoding and line ending."""
        # Detect encoding
        try:
            with tokenize.open(file_path) as f:
                encoding = f.encoding
        except Exception:
            encoding = "utf-8"

        # Detect line ending
        with open(file_path, "rb") as f:
            content = f.read()
            if b"\r\n" in content:
                line_ending = "\r\n"
            elif b"\n" in content:
                line_ending = "\n"
            else:
                line_ending = "\n"

        return encoding, line_ending

    def _create_toc_content(
        self, file_path: str, ast_structure: dict[str, list[str]]
    ) -> str:
        """Create TOC header content."""
        module_name = os.path.basename(file_path).replace(".py", "")
        purpose = "TODO: Add module purpose"

        classes = ast_structure.get("classes", [])
        functions = ast_structure.get("functions", [])
        imports = ast_structure.get("imports", [])

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        toc_lines = [
            self.begin_marker,
            "FILE_TOC",
            f"Module: {module_name}",
            f"Purpose: {purpose}",
            f"Classes: {len(classes)}",
            f"Functions: {len(functions)}",
            f"Imports: {len(imports)}",
            f"Updated: {now}",
            "Generated-By: ast_toc",
            self.end_marker,
        ]

        return "\n".join(toc_lines)

    def _insert_toc(
        self, content: str, toc_content: str, insert_above_docstring: bool
    ) -> str:
        """Insert TOC into file content."""
        lines = content.split("\n")

        # Remove existing TOC if present
        lines = self._remove_existing_toc(lines)

        # Find insertion point
        insert_pos = self._find_insertion_point(lines, insert_above_docstring)

        # Insert TOC
        toc_lines = toc_content.split("\n")
        new_lines = lines[:insert_pos] + toc_lines + [""] + lines[insert_pos:]

        return "\n".join(new_lines)

    def _remove_existing_toc(self, lines: list[str]) -> list[str]:
        """Remove existing TOC block from lines."""
        begin_idx = None
        end_idx = None

        for i, line in enumerate(lines):
            if self.begin_marker in line:
                begin_idx = i
            elif self.end_marker in line and begin_idx is not None:
                end_idx = i
                break

        if begin_idx is not None and end_idx is not None:
            # Remove TOC block and any following empty lines
            new_lines = lines[:begin_idx]
            # Skip empty lines after TOC
            for i in range(end_idx + 1, len(lines)):
                if lines[i].strip():
                    new_lines.extend(lines[i:])
                    break
            return new_lines

        return lines

    def _find_insertion_point(
        self, lines: list[str], insert_above_docstring: bool
    ) -> int:
        """Find where to insert TOC."""
        if not insert_above_docstring:
            return 0

        # Look for module docstring
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('"""') or stripped.startswith("'''"):
                return i

        return 0

    def _atomic_write(
        self, file_path: str, content: str, encoding: str, line_ending: str
    ) -> None:
        """Write file atomically preserving encoding and line endings."""
        # Create temporary file
        temp_fd, temp_path = tempfile.mkstemp(
            dir=os.path.dirname(file_path), prefix=".ast_toc_tmp_", suffix=".py"
        )

        try:
            # Write to temp file
            with os.fdopen(temp_fd, "w", encoding=encoding, newline="") as f:
                # Normalize line endings
                normalized_content = content.replace("\n", line_ending)
                f.write(normalized_content)

            # Atomic rename
            shutil.move(temp_path, file_path)

        except Exception:
            # Clean up temp file on error
            try:
                os.unlink(temp_path)
            except Exception:
                pass
            raise
