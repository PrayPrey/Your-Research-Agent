"""Tests for corpus_streamer.py — A-2."""
import json
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from corpus_streamer import save_hash_checkpoint, load_hash_checkpoint


def test_hash_checkpoint_roundtrip():
    with tempfile.TemporaryDirectory() as td:
        ckpt = Path(td) / "test_hashes.json"
        hashes = {"abc123": "Pile-CC", "def456": "Books3"}
        save_hash_checkpoint(hashes, ckpt, n_processed=1000)
        loaded, n = load_hash_checkpoint(ckpt)
        assert loaded == hashes
        assert n == 1000


def test_load_missing_checkpoint():
    loaded, n = load_hash_checkpoint(Path("/nonexistent/path/ckpt.json"))
    assert loaded == {}
    assert n == 0


def test_checkpoint_atomic_write():
    """Checkpoint uses .tmp file then os.replace — no partial writes."""
    with tempfile.TemporaryDirectory() as td:
        ckpt = Path(td) / "hashes.json"
        save_hash_checkpoint({"a": "b"}, ckpt, 1)
        assert ckpt.exists()
        # .tmp file should be removed after atomic replace
        assert not Path(td, "hashes.json.tmp").exists()


def test_checkpoint_overwrite():
    """Later write replaces earlier checkpoint."""
    with tempfile.TemporaryDirectory() as td:
        ckpt = Path(td) / "hashes.json"
        save_hash_checkpoint({"a": "Pile-CC"}, ckpt, 100)
        save_hash_checkpoint({"b": "Books3", "c": "Wikipedia (en)"}, ckpt, 200)
        loaded, n = load_hash_checkpoint(ckpt)
        assert "a" not in loaded
        assert loaded["b"] == "Books3"
        assert n == 200
