"""Tests for task-003/012/013/014: LLM inference and checkpoint-resume."""
import sys
import json
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from inference import (
    _get_completed_ids_jsonl,
    _get_completed_ids_logits,
    append_jsonl,
    load_greedy_outputs,
    load_stochastic_outputs,
)


def test_get_completed_ids_jsonl_empty():
    """Returns empty set when file doesn't exist."""
    ids = _get_completed_ids_jsonl("/nonexistent/file.jsonl")
    assert ids == set()


def test_get_completed_ids_jsonl():
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as f:
        f.write(json.dumps({"id": 0, "response": "r0"}) + "\n")
        f.write(json.dumps({"id": 5, "response": "r5"}) + "\n")
        path = f.name
    ids = _get_completed_ids_jsonl(path)
    assert ids == {0, 5}


def test_append_jsonl():
    with tempfile.TemporaryDirectory() as d:
        path = str(Path(d) / "out.jsonl")
        append_jsonl({"id": 0, "v": "a"}, path)
        append_jsonl({"id": 1, "v": "b"}, path)
        with open(path) as f:
            lines = [json.loads(l) for l in f]
        assert len(lines) == 2
        assert lines[0]["id"] == 0
        assert lines[1]["id"] == 1


def test_append_mode():
    """Existing file is not overwritten."""
    with tempfile.TemporaryDirectory() as d:
        path = str(Path(d) / "out.jsonl")
        append_jsonl({"id": 0}, path)
        append_jsonl({"id": 1}, path)
        with open(path) as f:
            lines = f.readlines()
        assert len(lines) == 2


def test_load_greedy_outputs():
    with tempfile.TemporaryDirectory() as d:
        path = str(Path(d) / "greedy_responses.jsonl")
        records = [{"id": 0, "response": "r0"}, {"id": 1, "response": "r1"}]
        with open(path, "w") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")
        result = load_greedy_outputs(d)
        assert result[0]["response"] == "r0"
        assert result[1]["response"] == "r1"


def test_load_stochastic_outputs():
    with tempfile.TemporaryDirectory() as d:
        path = str(Path(d) / "stochastic_samples.jsonl")
        records = [{"id": 0, "samples": ["a", "b", "c", "d", "e"]}]
        with open(path, "w") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")
        result = load_stochastic_outputs(d)
        assert len(result[0]) == 5


def test_resume_skips_done():
    """Pre-populated JSONL entries are skipped."""
    with tempfile.TemporaryDirectory() as d:
        path = str(Path(d) / "stochastic_samples.jsonl")
        with open(path, "w") as f:
            f.write(json.dumps({"id": 42, "samples": ["x"] * 5}) + "\n")
        ids = _get_completed_ids_jsonl(path)
        assert 42 in ids


def test_get_completed_ids_logits():
    """Scan .pt files for completed IDs."""
    with tempfile.TemporaryDirectory() as d:
        import torch
        (Path(d) / "example_10.pt").write_bytes(b"")
        (Path(d) / "example_20.pt").write_bytes(b"")
        ids = _get_completed_ids_logits(d)
        assert ids == {10, 20}
