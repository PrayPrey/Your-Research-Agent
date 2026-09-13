"""Tests for H-E1 pipeline spec compliance."""
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline import (
    HFCoverageChecker,
    MetricsAggregator,
    OpenMLTemporalChecker,
    PipelineOrchestrator,
    RaffParser,
    Visualizer,
)
from config import HF_FIELDS, THRESHOLDS


# ---------------------------------------------------------------------------
# RaffParser Tests
# ---------------------------------------------------------------------------

@pytest.fixture
def raff_csv(tmp_path):
    """Create a minimal Raff-like CSV with 255 rows."""
    rows = [{"paper_id": i, "reproducibility_label": i % 2, "dataset": f"ds_{i % 30}", "year": 2000 + (i % 18)}
            for i in range(255)]
    df = pd.DataFrame(rows)
    path = tmp_path / "raff.csv"
    df.to_csv(path, index=False)
    return str(path)


def test_raff_parser_load(raff_csv):
    parser = RaffParser(raff_csv)
    df = parser.load()
    assert len(df) == 255
    assert isinstance(df, pd.DataFrame)


def test_raff_parser_unique_datasets(raff_csv):
    parser = RaffParser(raff_csv)
    parser.load()
    names = parser.unique_datasets()
    assert isinstance(names, list)
    assert len(names) > 0
    assert all(isinstance(n, str) for n in names)


def test_raff_parser_paper_years(raff_csv):
    parser = RaffParser(raff_csv)
    parser.load()
    years = parser.paper_years()
    assert isinstance(years, dict)
    # years values should be integers
    for v in years.values():
        assert isinstance(v, int)


# ---------------------------------------------------------------------------
# HFCoverageChecker Tests
# ---------------------------------------------------------------------------

def test_hf_checker_aggregate_empty():
    checker = HFCoverageChecker(fields=HF_FIELDS)
    result = checker.aggregate({})
    assert result["coverage_rate"] == 0.0
    assert result["n_found"] == 0
    assert result["n_queried"] == 0


def test_hf_checker_aggregate_all_found():
    checker = HFCoverageChecker(fields=HF_FIELDS)
    scores = {"mnist": 0.8, "cifar10": 0.6}
    result = checker.aggregate(scores)
    assert result["coverage_rate"] == 1.0
    assert result["n_found"] == 2
    assert result["n_queried"] == 2
    assert abs(result["mean_field_score"] - 0.7) < 1e-9


def test_hf_checker_aggregate_partial():
    checker = HFCoverageChecker(fields=HF_FIELDS)
    scores = {"mnist": 0.8, "unknown": None}
    result = checker.aggregate(scores)
    assert result["coverage_rate"] == 0.5
    assert result["n_found"] == 1
    assert result["n_queried"] == 2


def test_hf_checker_aggregate_per_dataset_passthrough():
    checker = HFCoverageChecker(fields=HF_FIELDS)
    scores = {"a": 0.5, "b": None}
    result = checker.aggregate(scores)
    assert result["per_dataset"] == scores


@patch("pipeline.HFCoverageChecker._query_one", return_value=0.7)
def test_hf_checker_check_all_calls_query(mock_query):
    checker = HFCoverageChecker(fields=HF_FIELDS)
    with patch("time.sleep"):
        result = checker.check_all(["mnist", "cifar10"])
    assert len(result) == 2
    assert mock_query.call_count == 2


# ---------------------------------------------------------------------------
# OpenMLTemporalChecker Tests
# ---------------------------------------------------------------------------

def make_openml_df():
    return pd.DataFrame({
        "name": ["MNIST", "CIFAR-10", "ImageNet", "UnknownDS"],
        "name_norm": ["mnist", "cifar-10", "imagenet", "unknownds"],
        "upload_date": pd.to_datetime(["1990-01-01", "2005-06-15", "2010-03-01", "2015-07-01"]),
    })


def test_openml_checker_check_all_basic():
    checker = OpenMLTemporalChecker()
    df = make_openml_df()
    dataset_names = ["mnist", "cifar-10", "imagenet"]
    paper_years = {"mnist": 1998, "cifar-10": 2009, "imagenet": 2012}
    result = checker.check_all(dataset_names, paper_years, df)
    assert "filter_success_rate" in result
    assert "n_valid" in result
    assert "n_queried" in result
    assert result["n_queried"] == 3
    # mnist: upload 1990 < paper_year 1998 → valid
    assert result["pre_pub_counts"]["mnist"] >= 1


def test_openml_checker_no_match():
    checker = OpenMLTemporalChecker()
    df = make_openml_df()
    result = checker.check_all(["no-such-dataset"], {"no-such-dataset": 2000}, df)
    assert result["n_valid"] == 0
    assert result["filter_success_rate"] == 0.0


def test_openml_checker_missing_year():
    checker = OpenMLTemporalChecker()
    df = make_openml_df()
    # No year provided for mnist → should count as 0
    result = checker.check_all(["mnist"], {}, df)
    assert result["pre_pub_counts"]["mnist"] == 0


# ---------------------------------------------------------------------------
# MetricsAggregator Tests
# ---------------------------------------------------------------------------

def test_metrics_aggregator_gate_pass():
    agg = MetricsAggregator(THRESHOLDS)
    raff_df = pd.DataFrame({"paper_id": range(255)})
    hf_result = {"coverage_rate": 0.65, "mean_field_score": 0.4, "n_found": 30, "n_queried": 47, "per_dataset": {}}
    openml_result = {"filter_success_rate": 0.80, "n_valid": 38, "n_queried": 47, "pre_pub_counts": {}}
    results = agg.compute(raff_df, hf_result, openml_result)
    assert results["gate"]["pass"] is True
    assert results["gate"]["hf_coverage_pass"] is True
    assert results["gate"]["openml_temporal_pass"] is True


def test_metrics_aggregator_gate_fail_hf():
    agg = MetricsAggregator(THRESHOLDS)
    raff_df = pd.DataFrame({"paper_id": range(255)})
    hf_result = {"coverage_rate": 0.30, "mean_field_score": 0.2, "n_found": 14, "n_queried": 47, "per_dataset": {}}
    openml_result = {"filter_success_rate": 0.80, "n_valid": 38, "n_queried": 47, "pre_pub_counts": {}}
    results = agg.compute(raff_df, hf_result, openml_result)
    assert results["gate"]["pass"] is False
    assert results["gate"]["hf_coverage_pass"] is False


def test_metrics_aggregator_activation_indicators():
    agg = MetricsAggregator(THRESHOLDS)
    raff_df = pd.DataFrame({"paper_id": range(255)})
    hf_result = {"coverage_rate": 0.65, "mean_field_score": 0.4, "n_found": 30, "n_queried": 47, "per_dataset": {}}
    openml_result = {"filter_success_rate": 0.80, "n_valid": 38, "n_queried": 47, "pre_pub_counts": {}}
    results = agg.compute(raff_df, hf_result, openml_result)
    assert results["activation"]["all_activated"] is True
    assert results["activation"]["hf_n_queried_ok"] is True
    assert results["activation"]["openml_n_queried_ok"] is True


# ---------------------------------------------------------------------------
# Visualizer Tests (output file creation)
# ---------------------------------------------------------------------------

def test_visualizer_gate_metrics_bar(tmp_path):
    viz = Visualizer(output_dir=str(tmp_path))
    results = {
        "hf": {"coverage_rate": 0.65},
        "openml": {"filter_success_rate": 0.80},
    }
    viz.gate_metrics_bar(results)
    assert (tmp_path / "gate_metrics.png").exists()


def test_visualizer_openml_histogram(tmp_path):
    viz = Visualizer(output_dir=str(tmp_path))
    counts = {"mnist": 12, "cifar-10": 3, "unknown": 0}
    viz.openml_run_histogram(counts)
    assert (tmp_path / "openml_run_dist.png").exists()


def test_visualizer_dataset_freq_bar(tmp_path):
    viz = Visualizer(output_dir=str(tmp_path))
    df = pd.DataFrame({"dataset": ["mnist"] * 5 + ["cifar10"] * 3 + ["imagenet"] * 2})
    viz.dataset_freq_bar(df)
    assert (tmp_path / "dataset_freq.png").exists()


# ---------------------------------------------------------------------------
# Integration: PipelineOrchestrator (mocked APIs)
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_raff_csv(tmp_path):
    rows = [{"paper_id": i, "reproducibility_label": i % 2, "dataset": f"ds{i % 5}", "year": 2000 + (i % 10)}
            for i in range(255)]
    df = pd.DataFrame(rows)
    path = tmp_path / "raff.csv"
    df.to_csv(path, index=False)
    return str(path)


def test_orchestrator_runs_and_returns_results(mock_raff_csv, tmp_path):
    """Full integration test with mocked HF and OpenML APIs."""
    hf_scores = {f"ds{i}": 0.6 for i in range(5)}
    openml_df = pd.DataFrame({
        "name": [f"ds{i}" for i in range(5)],
        "name_norm": [f"ds{i}" for i in range(5)],
        "upload_date": pd.to_datetime(["1995-01-01"] * 5),
    })

    with patch.object(HFCoverageChecker, "check_all", return_value=hf_scores), \
         patch.object(OpenMLTemporalChecker, "fetch_all", return_value=openml_df), \
         patch("time.sleep"):
        config = {
            "raff_csv": mock_raff_csv,
            "hf_token": None,
            "results_dir": str(tmp_path / "results"),
        }
        orch = PipelineOrchestrator(config=config)
        results = orch.run()

    assert "gate" in results
    assert "hf" in results
    assert "openml" in results
    assert "raff" in results
    assert "activation" in results
    # Check results.json was saved
    assert (tmp_path / "results" / "results.json").exists()
