# === FILE_TOC BEGIN ===
# FILE_TOC
# Module: watcher
# Purpose: TODO: Add module purpose
# Classes: class FileWatcher
# Functions: FileWatcher.__init__(root_path), FileWatcher._setup_logger(), FileWatcher.start(), FileWatcher.stop(timeout), FileWatcher.should_ignore(path), FileWatcher.on_modified(path), FileWatcher.wait_for_toc_update(path, timeout)
# Imports: import fnmatch, import logging, import time, from pathlib import Path, from src.ast_parser.parser import ASTParser, from src.toc_generator.generator import TOCGenerator
# Updated: 2025-09-27 19:47:01
# Generated-By: ast_toc
# === FILE_TOC END ===

"""File watcher for monitoring Python files and updating TOC."""

import fnmatch
import logging
import time
from pathlib import Path

from src.ast_parser.parser import ASTParser
from src.toc_generator.generator import TOCGenerator


class FileWatcher:
    """File watcher that monitors Python files and updates TOC headers."""

    def __init__(
        self,
        root_path: Path,
        *,
        include: list[str] = None,
        exclude: list[str] = None,
        max_file_mb: float = 1.0,
        insert_above_docstring: bool = True,
    ):
        """Initialize file watcher.

        Args:
            root_path: Root directory to watch
            include: Include patterns
            exclude: Exclude patterns
            max_file_mb: Maximum file size in MB
            insert_above_docstring: Whether to insert TOC above docstring
        """
        self.root_path = Path(root_path)
        self.include = include or ["**/*.py"]
        self.exclude = exclude or ["**/__pycache__/**", "**/.venv/**", "**/.git/**"]
        self.max_file_mb = max_file_mb
        self.insert_above_docstring = insert_above_docstring

        self.parser = ASTParser()
        self.generator = TOCGenerator()
        self.is_running = False
        self.logger = self._setup_logger()

        # For testing - track TOC updates
        self._toc_updates = {}

    def _setup_logger(self) -> logging.Logger:
        """Setup logger for file operations."""
        logger = logging.getLogger("ast_toc.watcher")
        logger.setLevel(logging.INFO)
        # Logger setup is now centralized in daemon.py
        return logger

    def start(self) -> None:
        """Start monitoring directory."""
        self.is_running = True
        self.logger.info(f"Started monitoring {self.root_path}")

    def stop(self, timeout: float = 1.0) -> None:
        """Stop monitoring with graceful shutdown."""
        self.is_running = False
        time.sleep(timeout)  # Allow current operations to complete
        self.logger.info("Stopped monitoring")

    def should_ignore(self, path: Path) -> bool:
        """Check if file should be ignored.

        Args:
            path: File path to check

        Returns:
            True if file should be ignored
        """
        path_str = str(path)

        # Check file size
        try:
            size_mb = path.stat().st_size / (1024 * 1024)
            if size_mb > self.max_file_mb:
                self.logger.warning(f"Large file skipped: {path} ({size_mb:.1f}MB)")
                return True
        except OSError:
            return True

        # Check system directories
        system_dirs = ["__pycache__", ".git", ".venv"]
        for part in path.parts:
            if part in system_dirs:
                return True

        # Check include patterns
        include_match = False
        for pattern in self.include:
            if fnmatch.fnmatch(path_str, pattern):
                include_match = True
                break

        if not include_match:
            return True

        # Check exclude patterns
        for pattern in self.exclude:
            if fnmatch.fnmatch(path_str, pattern):
                return True

        return False

    def on_modified(self, path: Path) -> None:
        """Handle file modification event.

        Args:
            path: Path to modified file
        """
        if not self.is_running:
            return

        if self.should_ignore(path):
            return

        if not path.suffix == ".py":
            return

        try:
            # Parse file structure
            ast_structure = self.parser.parse_file(str(path))

            # Generate TOC
            self.generator.generate_toc(
                str(path), ast_structure, self.insert_above_docstring
            )

            # Track for testing
            self._toc_updates[str(path)] = time.time()
            self.logger.info(f"Updated TOC for {path}")

        except Exception as e:
            self.logger.error(f"Failed to update TOC for {path}: {e}")

    def wait_for_toc_update(self, path: Path, timeout: float = 1.0) -> bool:
        """Wait for TOC update to complete (for testing).

        Args:
            path: File path to wait for
            timeout: Maximum wait time in seconds

        Returns:
            True if TOC was updated within timeout
        """
        start_time = time.time()
        path_str = str(path)

        while time.time() - start_time < timeout:
            if path_str in self._toc_updates:
                return True
            time.sleep(0.05)  # 50ms polling

        return False
