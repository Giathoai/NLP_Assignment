"""
Utility functions for reading and writing txt and JSON files.
"""

import json
import os


def read_text(filepath: str) -> str:
    """Read a plain text file and return its content as a string."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def write_text(filepath: str, content: str) -> None:
    """Write a string to a plain text file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def read_json(filepath: str):
    """Read a JSON file and return the parsed Python object."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(filepath: str, data, indent: int = 2) -> None:
    """Serialize a Python object to a JSON file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def append_text(filepath: str, content: str) -> None:
    """Append a string to a plain text file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(content)
