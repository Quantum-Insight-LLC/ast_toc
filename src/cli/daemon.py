# === FILE_TOC BEGIN ===
# FILE_TOC
# Module: daemon
# Purpose: TODO: Add module purpose
# Classes: class Daemon
# Functions: Daemon.__init__(config), Daemon._setup_logging(), Daemon._should_write_logging_probe(), Daemon.start(), Daemon.stop(), Daemon._run(), Daemon.write_pid(), Daemon.remove_pid(), Daemon.is_pid_running(), Daemon.is_pid_file_exists(), Daemon.is_daemon_running(), Daemon._perform_initial_scan(), Daemon._toc_content_equal(existing_toc, new_toc)
# Imports: import logging, import os, import sys, import threading, import time, from pathlib import Path, from src.file_watcher.watcher import FileWatcher
# Updated: 2025-09-27 19:47:01
# Generated-By: ast_toc
# === FILE_TOC END ===

"""Daemon implementation for AST TOC."""

import logging
import os
import sys
import threading
import time
from pathlib import Path

from src.file_watcher.watcher import FileWatcher


class Daemon:
    """Daemon for monitoring Python files and updating TOC."""

    def __init__(self, config: dict):
        """Initialize daemon with configuration.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.pid_file = Path(config["pid_file"])
        self.log_file = Path(config["log_file"])
        self.watch_path = Path(config["watch_path"])
        self.log_level = config.get("log_level", "INFO")

        self.watcher: FileWatcher | None = None
        self.is_running = False
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

        self._setup_logging()

    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        # Clear existing handlers
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        # Configure logging
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(sys.stderr),
            ],
        )

        self.logger = logging.getLogger("ast_toc.daemon")

        # Setup ast_toc.watcher logger
        watcher_logger = logging.getLogger("ast_toc.watcher")
        watcher_logger.propagate = False

        self.logger.info("Logging initialized")

        # Check if we should write test probe messages
        should_probe = self._should_write_logging_probe()
        if should_probe:
            self.logger.debug("Debug logging enabled")
            self.logger.error("Error logging test")

    def _should_write_logging_probe(self) -> bool:
        """Check if we should write logging probe messages."""
        # Check environment variable
        if os.getenv("AST_TOC_TEST_MODE", "").lower() in ("true", "1", "yes"):
            return True

        # Check config field
        probe_levels = self.config.get("logging_probe_on_start", [])
        return len(probe_levels) > 0

    def start(self) -> None:
        """Start the daemon."""
        if self.is_running:
            return

        self.logger.info("Starting daemon")
        self.is_running = True
        self._stop_event.clear()

        # Initialize watcher
        self.watcher = FileWatcher(
            self.watch_path,
            include=self.config.get("include", ["**/*.py"]),
            exclude=self.config.get(
                "exclude", ["**/__pycache__/**", "**/.venv/**", "**/.git/**"]
            ),
            max_file_mb=self.config.get("max_file_mb", 1.0),
            insert_above_docstring=self.config.get("insert_above_docstring", True),
        )

        # Start watcher
        self.watcher.start()

        # Perform initial scan if enabled
        if self.config.get("initial_scan", True):
            self._perform_initial_scan()

        # Start daemon thread
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

        self.logger.info(f"Daemon started, monitoring {self.watch_path}")

        # Write PID file
        self.write_pid()

    def stop(self) -> None:
        """Stop the daemon."""
        if not self.is_running:
            return

        self.logger.info("Stopping daemon")
        self.is_running = False
        self._stop_event.set()

        if self.watcher:
            self.watcher.stop()

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

        self.logger.info("Daemon stopped")

    def _run(self) -> None:
        """Main daemon loop."""
        while not self._stop_event.is_set():
            time.sleep(0.1)

    def write_pid(self) -> None:
        """Write PID to file."""
        with open(self.pid_file, "w") as f:
            f.write(str(os.getpid()))

    def remove_pid(self) -> None:
        """Remove PID file."""
        if self.pid_file.exists():
            self.pid_file.unlink()

    def is_pid_running(self) -> bool:
        """Check if PID file exists and process is running."""
        if not self.pid_file.exists():
            return False

        try:
            with open(self.pid_file) as f:
                pid = int(f.read().strip())

            # Check if process exists
            os.kill(pid, 0)
            return True
        except (OSError, ValueError):
            # If PID file exists but process is dead, remove the file
            if self.pid_file.exists():
                self.pid_file.unlink()
            return False

    def is_pid_file_exists(self) -> bool:
        """Check if PID file exists (regardless of process state)."""
        return self.pid_file.exists()

    def is_daemon_running(self) -> bool:
        """Check if daemon is running (internal state)."""
        return self.is_running

    def _perform_initial_scan(self) -> None:
        """Perform initial scan of watch_path for Python files."""
        import fnmatch

        from src.ast_parser.parser import ASTParser
        from src.toc_generator.generator import TOCGenerator

        self.logger.info(f"Performing initial scan of {self.watch_path}")

        parser = ASTParser()
        generator = TOCGenerator()

        # Get include/exclude patterns
        include_patterns = self.config.get("include", ["**/*.py"])
        exclude_patterns = self.config.get(
            "exclude", ["**/__pycache__/**", "**/.venv/**", "**/.git/**"]
        )
        max_file_mb = self.config.get("max_file_mb", 1.0)

        # Walk through watch_path
        for root, dirs, files in os.walk(self.watch_path):
            # Skip excluded directories
            rel_root = os.path.relpath(root, self.watch_path)
            if rel_root == ".":
                rel_root = ""

            # Check if directory should be excluded
            skip_dir = False
            for exclude_pattern in exclude_patterns:
                if fnmatch.fnmatch(rel_root, exclude_pattern) or fnmatch.fnmatch(
                    f"{rel_root}/*", exclude_pattern
                ):
                    skip_dir = True
                    break

            if skip_dir:
                dirs.clear()  # Don't traverse into excluded directories
                continue

            # Process Python files
            for file in files:
                if not file.endswith(".py"):
                    continue

                file_path = os.path.join(root, file)
                rel_file_path = os.path.relpath(file_path, self.watch_path)

                # Check file size
                try:
                    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                    if file_size_mb > max_file_mb:
                        self.logger.warning(
                            f"Large file skipped: {file_path} ({file_size_mb:.1f}MB)"
                        )
                        continue
                except OSError:
                    continue

                # Check if file matches include patterns
                matches_include = False
                for include_pattern in include_patterns:
                    if fnmatch.fnmatch(rel_file_path, include_pattern):
                        matches_include = True
                        break

                if not matches_include:
                    continue

                # Check if file should be excluded
                should_exclude = False
                for exclude_pattern in exclude_patterns:
                    if fnmatch.fnmatch(rel_file_path, exclude_pattern):
                        should_exclude = True
                        break

                if should_exclude:
                    continue

                # Check if TOC needs updating
                try:
                    # Parse current file content
                    current_structure = parser.parse_file(file_path)

                    # Read file to check for existing TOC
                    with open(file_path, encoding="utf-8") as f:
                        content = f.read()

                    # Check if TOC exists and is up-to-date
                    toc_begin = generator.begin_marker
                    toc_end = generator.end_marker

                    if toc_begin in content and toc_end in content:
                        # Extract existing TOC block
                        begin_idx = content.find(toc_begin)
                        end_idx = content.find(toc_end) + len(toc_end)
                        existing_toc = content[begin_idx:end_idx]

                        # Generate new TOC to compare
                        new_toc = generator._create_toc_content(
                            file_path, current_structure
                        )

                        # Compare TOC content (excluding timestamp)
                        if self._toc_content_equal(existing_toc, new_toc):
                            continue  # TOC is up-to-date

                    # Generate/update TOC
                    generator.generate_toc(
                        file_path,
                        current_structure,
                        self.config.get("insert_above_docstring", True),
                    )
                    self.logger.info(f"Bootstrap TOC for {rel_file_path}")

                except Exception as e:
                    self.logger.error(f"Failed to process {rel_file_path}: {e}")

    def _toc_content_equal(self, existing_toc: str, new_toc: str) -> bool:
        """Compare TOC content excluding timestamp."""
        # Remove timestamp lines for comparison
        existing_lines = [
            line
            for line in existing_toc.split("\n")
            if not line.startswith("# Updated:")
        ]
        new_lines = [
            line for line in new_toc.split("\n") if not line.startswith("# Updated:")
        ]

        return existing_lines == new_lines
