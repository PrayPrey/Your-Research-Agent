"""Tests for visualize.py — task-012."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from visualize import plot_cosine_similarity_bar, generate_all_figures


def make_results(n=8, base_val=0.97):
    return {f"layer.{i}.self_attn.q_proj.lora_A": base_val - i * 0.005
            for i in range(n)}


def test_plot_creates_png(tmp_path):
    """plot_cosine_similarity_bar should create a PNG file."""
    results = make_results()
    out = str(tmp_path / "test_plot.png")
    plot_cosine_similarity_bar(results, model_name="TestModel", output_path=out)
    assert os.path.exists(out), "PNG file was not created"
    assert os.path.getsize(out) > 0, "PNG file is empty"


def test_generate_all_figures_creates_both_pngs(tmp_path):
    """generate_all_figures should create both llama2 and mistral PNG files."""
    llama_results = make_results(8, 0.90)
    mistral_results = make_results(8, 0.93)
    figures_dir = str(tmp_path / "figures")
    generate_all_figures(llama_results, mistral_results, figures_dir)
    assert os.path.exists(os.path.join(figures_dir, "cosine_similarity_bar_llama2.png"))
    assert os.path.exists(os.path.join(figures_dir, "cosine_similarity_bar_mistral.png"))


def test_plot_empty_results_no_crash(tmp_path):
    """Empty results dict should not raise an error."""
    out = str(tmp_path / "empty_plot.png")
    plot_cosine_similarity_bar({}, model_name="TestModel", output_path=out)
    # Should complete without exception (no file created for empty)
