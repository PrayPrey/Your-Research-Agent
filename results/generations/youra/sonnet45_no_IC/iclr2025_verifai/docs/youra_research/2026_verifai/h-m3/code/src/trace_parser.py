"""Trace Parser - JSONL parsing with error handling."""

import json
from pathlib import Path
from typing import List, Dict


class TraceParser:
    """Parse MCP trace files in JSONL format."""

    def __init__(self, trace_folder: Path):
        """Initialize parser with trace folder path."""
        self.trace_folder = Path(trace_folder)

    def discover_traces(self) -> List[Path]:
        """Discover all .jsonl trace files.

        Returns:
            List of Path objects for trace files
        """
        if not self.trace_folder.exists():
            raise FileNotFoundError(f"Trace folder not found: {self.trace_folder}")

        traces = list(self.trace_folder.glob("*.jsonl"))
        if not traces:
            raise FileNotFoundError(f"No .jsonl files found in {self.trace_folder}")

        return sorted(traces)

    def parse_trace_file(self, file_path: Path) -> Dict:
        """Parse a single trace file.

        Args:
            file_path: Path to JSONL trace file

        Returns:
            Dict with keys: file, outcome, tool_calls
        """
        tool_calls = []

        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    tool_call = json.loads(line)
                    tool_calls.append(tool_call)
                except json.JSONDecodeError as e:
                    print(f"Warning: {file_path.name} line {line_num} malformed - {e}")
                    continue

        # Determine outcome from filename
        filename = file_path.name.lower()
        outcome = "fail" if "fail" in filename else "success"

        return {
            "file": file_path.name,
            "outcome": outcome,
            "tool_calls": tool_calls
        }

    def load_all_traces(self) -> List[Dict]:
        """Load all traces from folder.

        Returns:
            List of trace dicts
        """
        trace_files = self.discover_traces()
        traces = []

        for i, trace_file in enumerate(trace_files, 1):
            print(f"  Loading trace {i}/{len(trace_files)}: {trace_file.name}")
            trace = self.parse_trace_file(trace_file)
            traces.append(trace)

        return traces
