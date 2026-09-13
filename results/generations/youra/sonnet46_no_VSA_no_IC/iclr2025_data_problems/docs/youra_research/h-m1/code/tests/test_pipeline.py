"""Spec compliance tests for H-M1 pipeline."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest


def test_config_constants():
    from config import SEED, DOCS_PER_DOMAIN, MIN_TOKENS, CONNECTIVES, FORMAL_SYNTAX_RE, PILE_DOMAINS
    assert SEED == 42
    assert DOCS_PER_DOMAIN == 1000
    assert MIN_TOKENS == 100
    assert len(CONNECTIVES) >= 15
    assert "however" in CONNECTIVES
    assert FORMAL_SYNTAX_RE.search("def foo():") is not None
    assert len(PILE_DOMAINS) >= 21


def test_compute_proxies_entity_density():
    from src.proxies.compute import compute_proxies
    result = compute_proxies("The United Nations met in New York. However, France disagreed.")
    assert "entity_density" in result
    assert "narrative_coherence" in result
    assert "formal_syntax_density" in result
    assert result["entity_density"] > 0
    assert result["narrative_coherence"] > 0
    assert 0 <= result["entity_density"] <= 1
    assert 0 <= result["narrative_coherence"] <= 1
    assert 0 <= result["formal_syntax_density"] <= 1


def test_compute_proxies_code_text():
    from src.proxies.compute import compute_proxies
    code = "def foo(): import os; return os.path.join('a', 'b')"
    result = compute_proxies(code)
    assert result["formal_syntax_density"] > 0


def test_compute_proxies_empty():
    from src.proxies.compute import compute_proxies
    result = compute_proxies("")
    assert result["entity_density"] == 0.0
    assert result["narrative_coherence"] == 0.0


def test_sample_domains_basic():
    from src.data.loader import sample_domains
    fake_stream = [("Hello world this is a test document " * 20, "Wikipedia (en)")] * 10
    result = sample_domains(iter(fake_stream), docs_per_domain=3, min_tokens=5)
    assert "Wikipedia (en)" in result
    assert len(result["Wikipedia (en)"]) == 3


def test_welch_anova_significant():
    from src.analysis.stats import welch_anova
    rng = np.random.default_rng(42)
    scores = {
        "A": rng.normal(0.1, 0.02, 100).tolist(),
        "B": rng.normal(0.05, 0.02, 100).tolist(),
        "C": rng.normal(0.08, 0.02, 100).tolist(),
    }
    result = welch_anova(scores, proxy_name="entity_density")
    assert result["p_value"] < 0.05
    assert 0 < result["eta_squared"] <= 1
    assert result["significant"] is True


def test_tukey_hsd_pair():
    from src.analysis.stats import tukey_hsd, get_pair_result
    rng = np.random.default_rng(42)
    scores = {
        "Wikipedia (en)": rng.normal(0.12, 0.02, 100).clip(0).tolist(),
        "BookCorpus2": rng.normal(0.04, 0.02, 100).clip(0).tolist(),
    }
    result = tukey_hsd(scores)
    pair = get_pair_result(result, "Wikipedia (en)", "BookCorpus2")
    assert pair["reject"] is True
    assert pair["meandiff"] is not None


def test_domain_summary_stats():
    from src.analysis.stats import domain_summary_stats
    rng = np.random.default_rng(42)
    domain_scores = {
        "Wikipedia (en)": {
            "entity_density": rng.normal(0.1, 0.02, 50).clip(0).tolist(),
            "narrative_coherence": rng.normal(0.02, 0.005, 50).clip(0).tolist(),
            "formal_syntax_density": rng.normal(0.01, 0.003, 50).clip(0).tolist(),
        }
    }
    df = domain_summary_stats(domain_scores)
    assert not df.empty
    assert "mean" in df.columns
    assert "ci_lower" in df.columns
    assert "ci_upper" in df.columns


def test_evaluate_gate_pass():
    from src.analysis.stats import welch_anova, tukey_hsd, evaluate_gate
    rng = np.random.default_rng(42)
    domain_scores = {
        "Wikipedia (en)": {
            "entity_density": rng.normal(0.15, 0.02, 200).clip(0).tolist(),
            "narrative_coherence": rng.normal(0.02, 0.005, 200).clip(0).tolist(),
            "formal_syntax_density": rng.normal(0.01, 0.003, 200).clip(0).tolist(),
        },
        "BookCorpus2": {
            "entity_density": rng.normal(0.04, 0.02, 200).clip(0).tolist(),
            "narrative_coherence": rng.normal(0.10, 0.01, 200).clip(0).tolist(),
            "formal_syntax_density": rng.normal(0.01, 0.003, 200).clip(0).tolist(),
        },
        "Github": {
            "entity_density": rng.normal(0.03, 0.01, 200).clip(0).tolist(),
            "narrative_coherence": rng.normal(0.01, 0.005, 200).clip(0).tolist(),
            "formal_syntax_density": rng.normal(0.15, 0.03, 200).clip(0).tolist(),
        },
    }
    proxies = ["entity_density", "narrative_coherence", "formal_syntax_density"]
    anova_results = {}
    tukey_results = {}
    for proxy in proxies:
        proxy_scores = {d: v[proxy] for d, v in domain_scores.items()}
        anova_results[proxy] = welch_anova(proxy_scores, proxy_name=proxy)
        tukey_results[proxy] = tukey_hsd(proxy_scores)
    gate = evaluate_gate(domain_scores, anova_results, tukey_results)
    assert gate["gate_pass"] is True


def test_figures_run_without_error(tmp_path):
    from src.visualization.figures import (
        plot_domain_proxy_comparison, plot_focal_domain_violins,
        plot_proxy_correlation_scatter,
    )
    from src.analysis.stats import domain_summary_stats
    import pandas as pd
    rng = np.random.default_rng(42)
    domain_scores = {
        "Wikipedia (en)": {
            "entity_density": rng.normal(0.1, 0.02, 30).clip(0).tolist(),
            "narrative_coherence": rng.normal(0.03, 0.01, 30).clip(0).tolist(),
            "formal_syntax_density": rng.normal(0.01, 0.003, 30).clip(0).tolist(),
        },
        "BookCorpus2": {
            "entity_density": rng.normal(0.05, 0.02, 30).clip(0).tolist(),
            "narrative_coherence": rng.normal(0.08, 0.01, 30).clip(0).tolist(),
            "formal_syntax_density": rng.normal(0.01, 0.003, 30).clip(0).tolist(),
        },
    }
    summary = domain_summary_stats(domain_scores)
    out1 = str(tmp_path / "bar.png")
    plot_domain_proxy_comparison(summary, out1)
    assert os.path.exists(out1)

    out2 = str(tmp_path / "violin.png")
    plot_focal_domain_violins(domain_scores, ["Wikipedia (en)", "BookCorpus2"], out2)
    assert os.path.exists(out2)

    out3 = str(tmp_path / "scatter.png")
    plot_proxy_correlation_scatter(domain_scores, out3)
    assert os.path.exists(out3)
