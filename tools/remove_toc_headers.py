#!/usr/bin/env python3
"""Script to remove TOC headers from Python files."""

import os
import re
import sys


def remove_toc_headers(file_path: str) -> None:
    """Remove TOC headers from a Python file.

    Args:
        file_path: Path to the Python file
    """
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # TOC markers from TOCGenerator
    begin_marker = "# === FILE_TOC BEGIN ==="
    end_marker = "# === FILE_TOC END ==="

    # Pattern to match TOC block (including the markers and everything between)
    # Use re.DOTALL to make . match newlines
    pattern = rf"{re.escape(begin_marker)}.*?{re.escape(end_marker)}"

    # Remove TOC block
    new_content = re.sub(pattern, "", content, flags=re.DOTALL)

    # Clean up extra newlines that might be left
    new_content = re.sub(r"\n\n\n+", "\n\n", new_content)

    # Write back to file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Removed TOC header from: {file_path}")


def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python tools/remove_toc_headers.py <file_or_directory>")
        sys.exit(1)

    target = sys.argv[1]

    if os.path.isfile(target):
        if target.endswith(".py"):
            remove_toc_headers(target)
        else:
            print(f"Error: {target} is not a Python file")
            sys.exit(1)
    elif os.path.isdir(target):
        # Process all Python files in directory
        for root, _dirs, files in os.walk(target):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    remove_toc_headers(file_path)
    else:
        print(f"Error: {target} is not a valid file or directory")
        sys.exit(1)


if __name__ == "__main__":
    main()
