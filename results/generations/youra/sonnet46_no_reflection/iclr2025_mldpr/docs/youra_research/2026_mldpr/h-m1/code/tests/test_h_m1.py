"""H-M1 spec compliance tests."""
import sys
import os
import pytest
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_pwc_raw():
    """Minimal synthetic PWC raw dataframe."""
    np.random.seed(42)
    rows = []
    tasks = [("image-classification", "ImageNet"), ("text-classification", "SST-2"),
             ("image-classification", "CIFAR-10")]
    models = [f"model_{i}" for i in range(50)]
    for task, dataset in tasks:
        for i, model in enumerate(models):
            for q in range(10):
                date = pd.Timestamp("2019-01-01") + pd.DateOffset(months=q * 3 + np.random.randint(0, 2))
                rows.append({
                    "task": task, "dataset": dataset, "model": model,
                    "evaluated_on": date,
                    "score": 80.0 - i * 0.5 + np.random.normal(0, 0.3),
                    "domain": "cv" if "image" in task else "nlp",
                    "quarter": date.to_period("Q").strftime("Q"),
                })
    df = pd.DataFrame(rows)
    df["quarter"] = pd.to_datetime(df["evaluated_on"]).dt.to_period("Q").astype(str)
    return df


@pytest.fixture
def sample_panel(sample_pwc_raw):
    from data_pipeline import compute_quarterly_panel
    return compute_quarterly_panel(sample_pwc_raw, min_submissions=5, min_quarters=4)


@pytest.fixture
def sample_sigma(sample_pwc_raw):
    from sigma_estimation import get_sigma_map
    return get_sigma_map(sample_pwc_raw)


@pytest.fixture
def sample_panel_with_compression(sample_panel, sample_sigma):
    from compression_detector import flag_compression
    return flag_compression(sample_panel, sample_sigma, threshold=1.5, min_consecutive=2)


# ── A-1: Data Pipeline ────────────────────────────────────────────────────────

class TestDataPipeline:
    def test_compute_quarterly_panel_schema(self, sample_pwc_raw):
        from data_pipeline import compute_quarterly_panel
        panel = compute_quarterly_panel(sample_pwc_raw, min_submissions=5, min_quarters=4)
        required = ["benchmark_id", "task", "dataset", "quarter",
                    "submission_count", "cumulative_count", "score_var_top10"]
        for col in required:
            assert col in panel.columns, f"Missing column: {col}"

    def test_cumulative_count_monotonic(self, sample_panel):
        for bm_id, grp in sample_panel.groupby("benchmark_id"):
            grp = grp.sort_values("quarter")
            assert (grp["cumulative_count"].diff().dropna() >= 0).all(), \
                f"cumulative_count not monotonic for {bm_id}"

    def test_load_panel_returns_tuple(self, sample_pwc_raw, monkeypatch):
        from data_pipeline import load_panel
        import data_pipeline
        monkeypatch.setattr(data_pipeline, "load_pwc_raw", lambda: sample_pwc_raw)
        result = load_panel(min_submissions=5, min_quarters=4)
        assert isinstance(result, tuple) and len(result) == 2

    def test_panel_has_rows(self, sample_panel):
        assert len(sample_panel) > 0


# ── A-2: Sigma Estimation ─────────────────────────────────────────────────────

class TestSigmaEstimation:
    def test_get_sigma_map_no_nans(self, sample_pwc_raw):
        from sigma_estimation import get_sigma_map
        sigma = get_sigma_map(sample_pwc_raw)
        assert sigma.isna().sum() == 0, "sigma_map has NaN values"

    def test_sigma_map_indexed_by_task_dataset(self, sample_pwc_raw):
        from sigma_estimation import get_sigma_map
        sigma = get_sigma_map(sample_pwc_raw)
        assert sigma.name == "sigma_meas"
        assert sigma.index.names == ["task", "dataset"]

    def test_sigma_map_positive(self, sample_pwc_raw):
        from sigma_estimation import get_sigma_map
        sigma = get_sigma_map(sample_pwc_raw)
        assert (sigma > 0).all(), "sigma_map has non-positive values"


# ── A-3: Compression Detector ─────────────────────────────────────────────────

class TestCompressionDetector:
    def test_flag_compression_adds_columns(self, sample_panel_with_compression):
        df = sample_panel_with_compression
        assert "compressed" in df.columns
        assert "compression_event" in df.columns
        assert "sigma_meas" in df.columns

    def test_compression_event_binary(self, sample_panel_with_compression):
        df = sample_panel_with_compression
        vals = df["compression_event"].dropna().unique()
        assert set(vals).issubset({0.0, 1.0, 0, 1}), f"Unexpected values: {vals}"

    def test_summarize_compression_keys(self, sample_panel_with_compression):
        from compression_detector import summarize_compression
        summary = summarize_compression(sample_panel_with_compression)
        assert "n_compression_events" in summary
        assert "n_qualifying_benchmarks" in summary
        assert "pct_compressed" in summary


# ── A-4: Spearman Baseline ────────────────────────────────────────────────────

class TestSpearmanBaseline:
    def test_returns_required_keys(self, sample_panel_with_compression):
        from spearman_baseline import compute_spearman_baseline
        result = compute_spearman_baseline(sample_panel_with_compression)
        assert "rho" in result
        assert "p_value" in result
        assert "n_obs" in result

    def test_n_obs_positive(self, sample_panel_with_compression):
        from spearman_baseline import compute_spearman_baseline
        result = compute_spearman_baseline(sample_panel_with_compression)
        assert result["n_obs"] > 0


# ── A-5/A-6: Granger Causality ────────────────────────────────────────────────

class TestGrangerCausality:
    def test_check_stationarity_returns_bool(self):
        from granger_causality import check_stationarity
        s = pd.Series(np.random.randn(30))
        result = check_stationarity(s)
        assert isinstance(result, bool)

    def test_make_stationary_returns_series(self):
        from granger_causality import make_stationary
        s = pd.Series(np.cumsum(np.random.randn(30)))
        result = make_stationary(s)
        assert isinstance(result, pd.Series)

    def test_test_granger_causality_returns_dict_or_none(self, sample_panel_with_compression):
        from granger_causality import test_granger_causality
        bm = sample_panel_with_compression["benchmark_id"].iloc[0]
        bm_df = sample_panel_with_compression[
            sample_panel_with_compression["benchmark_id"] == bm
        ].sort_values("quarter")
        result = test_granger_causality(bm_df, max_lag=2)
        assert result is None or isinstance(result, dict)
        if result is not None:
            assert all(isinstance(k, int) for k in result.keys())

    def test_aggregate_granger_panel_keys(self, sample_panel_with_compression):
        from granger_causality import run_granger_panel, aggregate_granger_panel
        fwd, rev = run_granger_panel(sample_panel_with_compression, max_lag=2)
        agg = aggregate_granger_panel(fwd, target_lag=2)
        assert "n_benchmarks_tested" in agg
        assert "n_significant_lag2" in agg
        assert "pct_significant_lag2" in agg


# ── A-7: Evaluate & Gate ──────────────────────────────────────────────────────

class TestEvaluate:
    def test_verify_mechanism_activated_returns_tuple(self, sample_panel_with_compression):
        from evaluate import verify_mechanism_activated
        from granger_causality import run_granger_panel, aggregate_granger_panel
        from spearman_baseline import compute_spearman_baseline
        sp = compute_spearman_baseline(sample_panel_with_compression)
        fwd, _ = run_granger_panel(sample_panel_with_compression, max_lag=2)
        activated, indicators = verify_mechanism_activated(
            sample_panel_with_compression, fwd, sp
        )
        assert isinstance(activated, bool)
        assert isinstance(indicators, dict)
        for key in ["panel_constructed", "sufficient_benchmarks", "spearman_computed",
                    "granger_computed", "spearman_significant", "granger_significant_lag2"]:
            assert key in indicators

    def test_check_gate_condition_or_logic(self):
        from evaluate import check_gate_condition
        # Both fail
        sp_fail = {"rho": 0.1, "p_value": 0.5, "n_obs": 100}
        agg_fail = {"n_benchmarks_tested": 30, "n_significant_lag2": 0,
                    "pct_significant_lag2": 0.0, "min_p_lag2": 0.8}
        passed, _ = check_gate_condition(sp_fail, agg_fail)
        assert passed is False

        # Spearman passes
        sp_pass = {"rho": 0.6, "p_value": 0.001, "n_obs": 100}
        passed, _ = check_gate_condition(sp_pass, agg_fail)
        assert passed is True

        # Granger passes
        agg_pass = {"n_benchmarks_tested": 30, "n_significant_lag2": 10,
                    "pct_significant_lag2": 0.33, "min_p_lag2": 0.01}
        passed, _ = check_gate_condition(sp_fail, agg_pass)
        assert passed is True

    def test_save_results_creates_file(self, tmp_path):
        from evaluate import save_results
        results = {"test": 1, "value": 0.5, "arr": [1, 2, 3]}
        out = str(tmp_path / "results.json")
        save_results(results, out)
        assert os.path.exists(out)
