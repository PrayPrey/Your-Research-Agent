"""Tests for visualize.py spec compliance."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd


def _make_df():
    np.random.seed(42)
    rows = []
    for scale in [70, 160]:
        for ppl in [20, 35, 50]:
            for j in [0.7, 0.9]:
                for seed in [1, 2, 3]:
                    rows.append({
                        "scale": scale, "ppl_threshold": ppl, "dedup_j": j,
                        "corpus": "dolma", "seed": seed,
                        "mmlu_4shot": 0.25 + np.random.normal(0, 0.01),
                        "hellaswag_0shot": 0.40 + np.random.normal(0, 0.01),
                        "contamination_rate": 0.01,
                    })
    return pd.DataFrame(rows)


def _make_meta():
    return [
        {"condition": f"dolma_ppl{t}_j{int(j*10):02d}",
         "corpus": "dolma", "ppl_threshold": t, "dedup_j": j,
         "token_count": 1_000_000_000, "contamination_rate": 0.01}
        for t in [20, 35, 50] for j in [0.7, 0.9]
    ]


def test_plot_bar_factorial(tmp_path):
    from visualize import plot_bar_factorial
    df = _make_df()
    plot_bar_factorial(df, str(tmp_path))
    assert os.path.exists(tmp_path / "bar_factorial.png")


def test_plot_interaction(tmp_path):
    from visualize import plot_interaction
    df = _make_df()
    plot_interaction(df, str(tmp_path))
    assert os.path.exists(tmp_path / "interaction_plot.png")


def test_plot_dedup_interaction(tmp_path):
    from visualize import plot_dedup_interaction
    df = _make_df()
    plot_dedup_interaction(df, str(tmp_path))
    assert os.path.exists(tmp_path / "dedup_interaction.png")


def test_plot_fineweb_replication(tmp_path):
    from visualize import plot_fineweb_replication
    df = _make_df()
    plot_fineweb_replication(df, str(tmp_path))
    assert os.path.exists(tmp_path / "fineweb_replication.png")


def test_plot_corpus_size_heatmap(tmp_path):
    from visualize import plot_corpus_size_heatmap
    meta = _make_meta()
    plot_corpus_size_heatmap(meta, str(tmp_path))
    assert os.path.exists(tmp_path / "corpus_size_heatmap.png")


def test_plot_contamination_table(tmp_path):
    from visualize import plot_contamination_table
    meta = _make_meta()
    plot_contamination_table(meta, str(tmp_path))
    assert os.path.exists(tmp_path / "contamination_table.png")


def test_generate_all_figures(tmp_path):
    from visualize import generate_all_figures
    df = _make_df()
    meta = _make_meta()
    generate_all_figures(df, meta, str(tmp_path))
    assert os.path.exists(tmp_path / "bar_factorial.png")
    assert os.path.exists(tmp_path / "interaction_plot.png")
