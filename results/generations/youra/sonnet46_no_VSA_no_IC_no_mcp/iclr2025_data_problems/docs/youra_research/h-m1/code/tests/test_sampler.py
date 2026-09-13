"""Tests for sampler.py — A-3."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sampler import DocWithMeta, compute_subset_proportions


def test_compute_subset_proportions_basic():
    hashes = {"a": "Pile-CC", "b": "Pile-CC", "c": "Books3", "d": "Wikipedia (en)"}
    props = compute_subset_proportions(hashes)
    assert abs(props["Pile-CC"] - 0.5) < 1e-9
    assert abs(props["Books3"] - 0.25) < 1e-9
    assert abs(props["Wikipedia (en)"] - 0.25) < 1e-9
    assert abs(sum(props.values()) - 1.0) < 1e-9


def test_subset_proportions_single():
    hashes = {"x": "OnlySubset"}
    props = compute_subset_proportions(hashes)
    assert props["OnlySubset"] == 1.0


def test_docwithmeta_fields():
    doc = DocWithMeta(text="hello", doc_id="abc", pile_subset="Pile-CC", is_removed=True)
    assert doc.text == "hello"
    assert doc.is_removed is True


def test_docwithmeta_serialization():
    from dataclasses import asdict
    doc = DocWithMeta(text="test", doc_id="hash1", pile_subset="Books3", is_removed=False)
    d = asdict(doc)
    assert d["text"] == "test"
    assert d["is_removed"] is False
    restored = DocWithMeta(**d)
    assert restored.doc_id == "hash1"
