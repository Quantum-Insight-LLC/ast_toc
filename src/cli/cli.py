# === FILE_TOC BEGIN ===
# FILE_TOC
# Module: cli
# Purpose: TODO: Add module purpose
# Classes: None
# Functions: def main(), def start_daemon(), def stop_daemon(), def status_daemon()
# Imports: import sys, from src.cli.config_loader import load_config, from src.cli.daemon import Daemon
# Updated: 2025-09-27 19:47:01
# Generated-By: ast_toc
# === FILE_TOC END ===

"""CLI interface for AST TOC daemon."""

import sys

from src.cli.config_loader import load_config
from src.cli.daemon import Daemon


def main() -> int:
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: ast_toc <start|stop|status>")
        return 1

    command = sys.argv[1]

    try:
        if command == "start":
            return start_daemon()
        elif command == "stop":
            return stop_daemon()
        elif command == "status":
            return status_daemon()
        else:
            print(f"Unknown command: {command}")
            return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


def start_daemon() -> int:
    """Start the daemon."""
    try:
        config = load_config()
    except Exception:
        print("ERR-CONFIG: Configuration error")
        return 1

    daemon = Daemon(config)

    # Check if already running
    if daemon.is_pid_file_exists():
        print("ERR-ALREADY-RUNNING: Daemon is already running")
        return 1

    # Start daemon
    daemon.start()

    print("daemon_started")
    return 0


def stop_daemon() -> int:
    """Stop the daemon."""
    try:
        config = load_config()
    except Exception:
        print("ERR-CONFIG: Configuration error")
        return 1

    daemon = Daemon(config)

    # Check if running
    if not daemon.is_pid_file_exists():
        print("ERR-NOT-RUNNING: Daemon is not running")
        return 1

    # Stop daemon
    daemon.stop()

    # Remove PID file
    daemon.remove_pid()

    print("daemon_stopped")
    return 0


def status_daemon() -> int:
    """Get daemon status."""
    try:
        config = load_config()
    except Exception:
        print("ERR-CONFIG: Configuration error")
        return 1

    daemon = Daemon(config)

    if daemon.is_pid_file_exists():
        try:
            with open(daemon.pid_file) as f:
                pid = f.read().strip()
            print(f"running (pid={pid})")
        except Exception:
            print("running (pid=unknown)")
    else:
        print("stopped")

    return 0


if __name__ == "__main__":
    sys.exit(main())
