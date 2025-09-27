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
