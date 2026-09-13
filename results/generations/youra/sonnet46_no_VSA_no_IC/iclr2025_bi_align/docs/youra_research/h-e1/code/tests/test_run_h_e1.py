"""Spec compliance tests for H-E1 pipeline — verify signatures and logic."""
import json
import sys
from collections import defaultdict
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from run_h_e1 import (
    classify_all,
    classify_paper,
    evaluate_gate,
    extract_paper_ids,
    fetch_references,
    resolve_papers,
)
from config import SCHEMES, COVERAGE_GATE, CROSS_GROUP_GATE


# ── classify_paper ────────────────────────────────────────────────────────────

class TestClassifyPaper:
    def test_scheme1_hci_venue(self):
        paper = {"venue": "CHI 2023", "fieldsOfStudy": None}
        assert classify_paper(paper, SCHEMES["scheme1"]) == "HCI"

    def test_scheme1_ml_nlp_venue(self):
        paper = {"venue": "NeurIPS 2022", "fieldsOfStudy": None}
        assert classify_paper(paper, SCHEMES["scheme1"]) == "ML_NLP"

    def test_scheme1_unclassified(self):
        paper = {"venue": "Nature", "fieldsOfStudy": None}
        assert classify_paper(paper, SCHEMES["scheme1"]) is None

    def test_scheme2_excludes_acl(self):
        paper = {"venue": "ACL 2022", "fieldsOfStudy": None}
        assert classify_paper(paper, SCHEMES["scheme2"]) is None

    def test_scheme2_includes_iclr(self):
        paper = {"venue": "ICLR 2023", "fieldsOfStudy": None}
        assert classify_paper(paper, SCHEMES["scheme2"]) == "ML_NLP"

    def test_scheme3_fos_hci_primary(self):
        paper = {"venue": "Nature", "fieldsOfStudy": ["Human-Computer Interaction"]}
        assert classify_paper(paper, SCHEMES["scheme3"]) == "HCI"

    def test_scheme3_fos_cs_then_venue_hci(self):
        paper = {"venue": "CHI 2022", "fieldsOfStudy": ["Computer Science"]}
        assert classify_paper(paper, SCHEMES["scheme3"]) == "HCI"

    def test_scheme3_fos_cs_then_venue_mlnlp(self):
        paper = {"venue": "ICLR 2023", "fieldsOfStudy": ["Computer Science"]}
        assert classify_paper(paper, SCHEMES["scheme3"]) == "ML_NLP"

    def test_scheme3_no_fos_fallback(self):
        paper = {"venue": "CSCW 2021", "fieldsOfStudy": None}
        assert classify_paper(paper, SCHEMES["scheme3"]) == "HCI"

    def test_none_venue_returns_none(self):
        paper = {"venue": None, "fieldsOfStudy": None}
        assert classify_paper(paper, SCHEMES["scheme1"]) is None

    def test_empty_venue_returns_none(self):
        paper = {"venue": "", "fieldsOfStudy": []}
        assert classify_paper(paper, SCHEMES["scheme1"]) is None


# ── classify_all ──────────────────────────────────────────────────────────────

class TestClassifyAll:
    def test_returns_paperId_keyed_dict(self):
        resolved = {
            "arXiv:1": {"paperId": "pid1", "venue": "CHI 2023", "fieldsOfStudy": None},
            "arXiv:2": {"paperId": "pid2", "venue": "NeurIPS 2022", "fieldsOfStudy": None},
            "arXiv:3": None,
        }
        result = classify_all(resolved, SCHEMES["scheme1"])
        assert "pid1" in result
        assert "pid2" in result
        assert result["pid1"] == "HCI"
        assert result["pid2"] == "ML_NLP"
        # None-valued papers skipped
        assert len(result) == 2


# ── evaluate_gate ─────────────────────────────────────────────────────────────

class TestEvaluateGate:
    def _make_ec(self, ml_ml=0, ml_hci=0, hci_ml=0, hci_hci=0) -> dict:
        d = defaultdict(int)
        d[("ML_NLP", "ML_NLP")] = ml_ml
        d[("ML_NLP", "HCI")] = ml_hci
        d[("HCI", "ML_NLP")] = hci_ml
        d[("HCI", "HCI")] = hci_hci
        return d

    def test_gate_pass_all_conditions_met(self):
        ec = self._make_ec(ml_hci=20, hci_ml=15)
        result = evaluate_gate(0.80, 80, 100, {"scheme1": ec})
        assert result["gate_pass"] is True
        assert result["schemes"]["scheme1"]["cross_group_total"] == 35
        assert result["schemes"]["scheme1"]["pass"] is True

    def test_gate_fail_low_coverage(self):
        ec = self._make_ec(ml_hci=20, hci_ml=15)
        result = evaluate_gate(0.50, 50, 100, {"scheme1": ec})
        assert result["gate_pass"] is False

    def test_gate_fail_low_edges(self):
        ec = self._make_ec(ml_hci=5, hci_ml=5)
        result = evaluate_gate(0.80, 80, 100, {"scheme1": ec})
        assert result["gate_pass"] is False

    def test_gate_pass_any_scheme(self):
        ec_fail = self._make_ec(ml_hci=5, hci_ml=5)
        ec_pass = self._make_ec(ml_hci=20, hci_ml=15)
        result = evaluate_gate(0.80, 80, 100, {"scheme1": ec_fail, "scheme2": ec_pass})
        assert result["gate_pass"] is True

    def test_gate_result_structure(self):
        ec = self._make_ec(ml_ml=10, ml_hci=20, hci_ml=15, hci_hci=8)
        result = evaluate_gate(0.75, 75, 100, {"scheme1": ec})
        s = result["schemes"]["scheme1"]
        assert "ML_NLP_ML_NLP" in s
        assert "ML_NLP_HCI" in s
        assert "HCI_ML_NLP" in s
        assert "HCI_HCI" in s
        assert "cross_group_total" in s
        assert "pass" in s
        assert s["cross_group_total"] == 35

    def test_coverage_stored(self):
        ec = self._make_ec()
        result = evaluate_gate(0.72, 72, 100, {"scheme1": ec})
        assert abs(result["coverage"] - 0.72) < 1e-9
        assert result["resolved"] == 72
        assert result["total"] == 100


# ── extract_paper_ids ─────────────────────────────────────────────────────────

class TestExtractPaperIds:
    def test_extracts_arxiv_ids(self, tmp_path):
        (tmp_path / "paper.md").write_text(
            "See https://arxiv.org/abs/2406.09264 for details."
        )
        ids = extract_paper_ids(tmp_path)
        assert "arXiv:2406.09264" in ids

    def test_deduplicates(self, tmp_path):
        (tmp_path / "a.md").write_text("arxiv.org/abs/1234.5678")
        (tmp_path / "b.md").write_text("arxiv.org/abs/1234.5678")
        ids = extract_paper_ids(tmp_path)
        assert ids.count("arXiv:1234.5678") == 1

    def test_strips_version(self, tmp_path):
        (tmp_path / "p.md").write_text("arxiv.org/abs/2301.00001v3")
        ids = extract_paper_ids(tmp_path)
        assert "arXiv:2301.00001" in ids
        assert not any("v3" in i for i in ids)

    def test_empty_dir(self, tmp_path):
        ids = extract_paper_ids(tmp_path)
        assert ids == []


# ── integration smoke test ────────────────────────────────────────────────────

def test_pipeline_smoke(tmp_path, monkeypatch):
    """End-to-end smoke: mock API calls, verify gate evaluation runs."""
    # Mock clone_corpus
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    (corpus_dir / "list.md").write_text(
        "- https://arxiv.org/abs/2406.09264 (CHI 2023)\n"
        "- https://arxiv.org/abs/2310.14870 (NeurIPS 2022)\n"
    )

    # Mock resolve_papers to return two papers
    mock_resolved = {
        "arXiv:2406.09264": {
            "paperId": "pid_hci",
            "venue": "CHI 2023",
            "fieldsOfStudy": ["Human-Computer Interaction"],
            "title": "HCI paper",
            "year": 2023,
            "externalIds": {},
        },
        "arXiv:2310.14870": {
            "paperId": "pid_ml",
            "venue": "NeurIPS 2022",
            "fieldsOfStudy": ["Computer Science"],
            "title": "ML paper",
            "year": 2022,
            "externalIds": {},
        },
    }

    # Mock fetch_references so ML paper cites HCI paper
    def mock_fetch_refs(paper_id, cache_dir):
        if paper_id == "pid_ml":
            return [{"paperId": "pid_hci", "title": "HCI paper", "venue": "CHI 2023", "fieldsOfStudy": ["Human-Computer Interaction"]}]
        return []

    monkeypatch.chdir(tmp_path)
    import run_h_e1
    monkeypatch.setattr(run_h_e1, "clone_corpus", lambda dest="corpus": corpus_dir)
    monkeypatch.setattr(run_h_e1, "resolve_papers", lambda ids, cache_dir: mock_resolved)
    monkeypatch.setattr(run_h_e1, "fetch_references", mock_fetch_refs)

    result = run_h_e1.main(
        corpus_dir=str(corpus_dir),
        cache_dir=str(tmp_path / "cache"),
        data_dir=str(tmp_path / "data"),
        figures_dir=str(tmp_path / "figures"),
        results_dir=str(tmp_path / "results"),
    )

    assert "coverage" in result
    assert "gate_pass" in result
    assert "schemes" in result
    # With 2 papers total, 2 resolved: coverage = 1.0 ≥ 0.70
    assert result["coverage"] == 1.0
    # scheme1: ML→HCI edge = 1, total cross = 1 < 30 → gate_pass = False (coverage ok, edges not)
    assert result["gate_pass"] is False  # only 1 cross edge, need 30
    # But the structure should be correct
    assert "scheme1" in result["schemes"]
    assert result["schemes"]["scheme1"]["ML_NLP_HCI"] == 1
