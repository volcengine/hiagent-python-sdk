"""Export utilities for HiAgent SDK CLI output."""

import json
import sys
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pathlib import Path


class Exporter:
    """Handles output formatting for HiAgent SDK CLI."""

    def __init__(self, json_mode: bool = False):
        """Initialize exporter with output mode."""
        self.json_mode = json_mode

    def print_result(
        self,
        data: Any,
        success: bool = True,
        message: Optional[str] = None,
        **kwargs
    ) -> None:
        """Print result in requested format."""
        if self.json_mode:
            self._print_json(data, success, message, **kwargs)
        else:
            self._print_human(data, success, message, **kwargs)

    def _print_json(
        self,
        data: Any,
        success: bool,
        message: Optional[str],
        **kwargs
    ) -> None:
        """Print result in JSON format."""
        output = {
            "success": success,
            "data": self._serialize_data(data),
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }

        # Add extra fields
        for key, value in kwargs.items():
            if value is not None:
                output[key] = self._serialize_data(value)

        json.dump(output, sys.stdout, indent=2)
        sys.stdout.write("\n")
        sys.stdout.flush()

    def _print_human(
        self,
        data: Any,
        success: bool,
        message: Optional[str],
        **kwargs
    ) -> None:
        """Print result in human-readable format."""
        # Print message if provided
        if message:
            if success:
                print(f"✓ {message}")
            else:
                print(f"✗ {message}", file=sys.stderr)

        # Print data
        if data is not None:
            formatted = self._format_human(data)
            if formatted:
                print(formatted)

        # Print extra fields if any
        for key, value in kwargs.items():
            if value is not None:
                formatted = self._format_human(value)
                if formatted:
                    print(f"\n{key.replace('_', ' ').title()}:")
                    print(formatted)

    def _serialize_data(self, data: Any) -> Any:
        """Serialize data for JSON output."""
        if data is None:
            return None
        elif isinstance(data, (str, int, float, bool)):
            return data
        elif isinstance(data, (list, tuple)):
            return [self._serialize_data(item) for item in data]
        elif isinstance(data, dict):
            return {k: self._serialize_data(v) for k, v in data.items()}
        elif hasattr(data, "model_dump"):
            # Pydantic model
            return data.model_dump()
        elif hasattr(data, "__dict__"):
            # Other object with __dict__
            return self._serialize_data(data.__dict__)
        else:
            return str(data)

    def _format_human(self, data: Any, indent: int = 0) -> str:
        """Format data for human-readable output."""
        if data is None:
            return ""
        elif isinstance(data, (str, int, float, bool)):
            return "  " * indent + str(data)
        elif isinstance(data, (list, tuple)):
            if not data:
                return "  " * indent + "(empty)"
            result = []
            for i, item in enumerate(data):
                result.append("  " * indent + f"[{i}]")
                result.append(self._format_human(item, indent + 1))
            return "\n".join(result)
        elif isinstance(data, dict):
            if not data:
                return "  " * indent + "(empty)"
            result = []
            for key, value in data.items():
                result.append("  " * indent + f"{key}:")
                result.append(self._format_human(value, indent + 1))
            return "\n".join(result)
        elif hasattr(data, "model_dump"):
            # Pydantic model
            return self._format_human(data.model_dump(), indent)
        else:
            return "  " * indent + str(data)

    def print_table(self, rows: List[Dict[str, Any]], headers: Optional[List[str]] = None) -> None:
        """Print data as table."""
        if self.json_mode:
            self.print_result(rows)
            return

        if not rows:
            print("(empty)")
            return

        # Auto-detect headers if not provided
        if headers is None:
            headers = list(rows[0].keys())

        # Calculate column widths
        col_widths = {}
        for header in headers:
            col_widths[header] = max(len(str(header)), max(len(str(row.get(header, ""))) for row in rows))

        # Print header
        header_line = "  ".join(f"{str(h):<{col_widths[h]}}" for h in headers)
        print(header_line)
        print("-" * len(header_line))

        # Print rows
        for row in rows:
            row_line = "  ".join(f"{str(row.get(h, '')):<{col_widths[h]}}" for h in headers)
            print(row_line)

    def write_json_file(self, data: Any, filepath: Path) -> None:
        """Write data to JSON file."""
        with open(filepath, "w") as f:
            json.dump(self._serialize_data(data), f, indent=2)

    def read_json_file(self, filepath: Path) -> Any:
        """Read data from JSON file."""
        with open(filepath, "r") as f:
            return json.load(f)
