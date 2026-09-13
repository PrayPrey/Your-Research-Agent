"""Spec tests for A-2 resume + donor-cache-reuse patch (task-003/009/010)."""
import csv
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import run_h_e1
from run_h_e1 import (CACHE_FIELDS, DONOR_CACHE_LLAMA2_TRIVIAQA,
                      resume_from_cache, run_sweep, verify_cache_reuse)


def _write_rows(path, example_ids, header=True, fields=None):
    fields = fields or CACHE_FIELDS
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if header:
            w.writeheader()
        for eid in example_ids:
            row = {k: 0.5 for k in fields}
            meta = {"example_id": eid, "dataset": "triviaqa",
                    "model": "llama2", "split": "pending", "label": eid % 2}
            row.update({k: v for k, v in meta.items() if k in fields})
            w.writerow(row)


def _fake_signals(empty=False):
    if empty:
        nan32 = np.full(32, np.nan)
        return {"entropy": nan32, "maxprob": nan32,
                "adj_kl": nan32, "top1_match": nan32}
    adj = np.full(32, 0.1)
    adj[0] = np.nan
    return {"entropy": np.full(32, 5.0), "maxprob": np.full(32, 0.3),
            "adj_kl": adj, "top1_match": np.full(32, 0.8)}


def test_resume_skips_written_ids(tmp_path):
    p = tmp_path / "cache.csv"
    _write_rows(p, [0, 1, 2, 5])
    assert resume_from_cache(str(p)) == {0, 1, 2, 5}


def test_resume_missing_file_empty_set(tmp_path):
    assert resume_from_cache(str(tmp_path / "nope.csv")) == set()


def test_resume_header_only_empty_set(tmp_path):
    p = tmp_path / "cache.csv"
    _write_rows(p, [])
    assert resume_from_cache(str(p)) == set()


def test_resume_truncates_corrupt_tail(tmp_path):
    p = tmp_path / "cache.csv"
    _write_rows(p, [0, 1])
    with open(p, "a", newline="") as f:
        f.write("2,triviaqa,llama2,pending,1,3.14")  # partial row, no newline
    ids = resume_from_cache(str(p))
    assert ids == {0, 1}
    # corrupt tail physically removed -> clean append possible
    df = pd.read_csv(p)
    assert list(df["example_id"]) == [0, 1]


def test_resume_header_mismatch_treated_as_missing(tmp_path):
    p = tmp_path / "cache.csv"
    _write_rows(p, [0, 1], fields=["example_id", "bogus"])
    assert resume_from_cache(str(p)) == set()


def test_donor_constant_points_at_sibling_h_e1_results():
    # v2 Gap C: donor is h-e1's Phase-4-finalized cell in the SIBLING folder,
    # not the stale pre-h-e1 _archive path v1 pointed at.
    assert "cache_llama2_triviaqa.csv" in DONOR_CACHE_LLAMA2_TRIVIAQA
    assert "_archive" not in DONOR_CACHE_LLAMA2_TRIVIAQA
    assert "h-e1/results" in DONOR_CACHE_LLAMA2_TRIVIAQA


def test_verify_cache_reuse_missing_donor(tmp_path):
    ok = verify_cache_reuse(None, None, str(tmp_path / "nope.csv"),
                            [{"q": 1}], "triviaqa", n_check=1)
    assert ok is False


def test_verify_cache_reuse_label_mismatch(tmp_path, monkeypatch):
    p = tmp_path / "donor.csv"
    _write_rows(p, [0, 1])  # labels 0, 1
    monkeypatch.setattr(run_h_e1, "generate_and_extract",
                        lambda *a, **k: ("some answer", _fake_signals()))
    # force label_response to disagree with donor label for example 0 (donor=0)
    monkeypatch.setattr(run_h_e1, "label_response", lambda *a, **k: 1)
    ok = verify_cache_reuse(None, None, str(p), [{}, {}], "triviaqa", n_check=2)
    assert ok is False


def test_run_sweep_donor_short_circuit_finalizes_pending(tmp_path, monkeypatch):
    """Donor rows copied, split='pending' finalized to selection/test, artifacts written."""
    donor = tmp_path / "donor.csv"
    n = 20
    _write_rows(donor, list(range(n)))
    results = tmp_path / "results"
    results.mkdir()
    import data as data_mod
    monkeypatch.setattr(run_h_e1, "RESULTS_DIR", str(results))
    monkeypatch.setattr(data_mod, "RESULTS_DIR", str(results))
    monkeypatch.setattr(run_h_e1, "verify_cache_reuse", lambda *a, **k: True)
    monkeypatch.setattr(run_h_e1, "generate_and_extract",
                        lambda *a, **k: ("x", _fake_signals()))

    class FakeCfg:
        vocab_size = 32000

    class FakeModel:
        config = FakeCfg()

    run_sweep(FakeModel(), None, "llama2", [{}] * n, "triviaqa",
              reuse_cache_path=str(donor))

    df = pd.read_csv(results / "cache_llama2_triviaqa.csv")
    assert len(df) == n
    assert set(df["split"]) == {"selection", "test"}          # no pending left
    assert (results / "test_split_locked_llama2_triviaqa.json").exists()
    assert (results / "top1_agreement_llama2_triviaqa.npy").exists()
    assert (results / "meta_llama2_triviaqa.json").exists()


def test_run_sweep_resume_appends_only_missing(tmp_path, monkeypatch):
    """Fresh-branch resume: pre-written ids skipped, only missing generated."""
    results = tmp_path / "results"
    results.mkdir()
    import data as data_mod
    monkeypatch.setattr(run_h_e1, "RESULTS_DIR", str(results))
    monkeypatch.setattr(data_mod, "RESULTS_DIR", str(results))
    n = 12
    pre = results / "cache_llama2_triviaqa.csv"
    _write_rows(pre, list(range(6)))  # first 6 already cached

    generated = []

    def fake_gen(model, tokenizer, example, dataset_name, max_new_tokens=32):
        generated.append(example["i"])
        return "ans", _fake_signals()

    monkeypatch.setattr(run_h_e1, "generate_and_extract", fake_gen)
    monkeypatch.setattr(run_h_e1, "label_response", lambda ex, t, d: ex["i"] % 2)

    class FakeCfg:
        vocab_size = 32000

    class FakeModel:
        config = FakeCfg()

    run_sweep(FakeModel(), None, "llama2", [{"i": i} for i in range(n)], "triviaqa")

    assert generated == list(range(6, n))  # only the missing half regenerated
    df = pd.read_csv(pre)
    assert sorted(df["example_id"]) == list(range(n))
    assert set(df["split"]) == {"selection", "test"}
