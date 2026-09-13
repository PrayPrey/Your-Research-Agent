"""Tests for visualize.py: figure generation with mock data."""
import sys, os, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _make_delta_norms():
    from config import CATEGORIES, RETRIEVAL_HEAVY, GENERATION_HEAVY
    mohawk = {cat: (0.3 if cat in RETRIEVAL_HEAVY else 0.1) for cat in CATEGORIES}
    lawcat = {cat: (0.1 if cat in RETRIEVAL_HEAVY else 0.08) for cat in CATEGORIES}
    hybrid4 = {cat: 0.15 for cat in CATEGORIES}
    return {"mohawk": mohawk, "lawcat": lawcat, "hybrid4": hybrid4}


def test_plot_delta_norm_bars_creates_file():
    from visualize import plot_delta_norm_bars
    dn = _make_delta_norms()
    with tempfile.TemporaryDirectory() as tmpdir:
        out = os.path.join(tmpdir, "fig1.png")
        plot_delta_norm_bars(dn, out)
        assert os.path.exists(out), "fig1_bar.png not created"
        assert os.path.getsize(out) > 1000, "fig1_bar.png too small"


def test_plot_delta_norm_heatmap_creates_file():
    from visualize import plot_delta_norm_heatmap
    dn = _make_delta_norms()
    with tempfile.TemporaryDirectory() as tmpdir:
        out = os.path.join(tmpdir, "fig2.png")
        plot_delta_norm_heatmap(dn, out)
        assert os.path.exists(out)
        assert os.path.getsize(out) > 1000


def test_plot_error_bars_creates_file():
    from visualize import plot_error_bars
    dn = _make_delta_norms()
    ci_data = {"interaction_ratio": 3.0, "interaction_ratio_ci_low": 1.5, "interaction_ratio_ci_high": 5.0}
    with tempfile.TemporaryDirectory() as tmpdir:
        out = os.path.join(tmpdir, "fig3.png")
        plot_error_bars(dn, ci_data, out)
        assert os.path.exists(out)


def test_plot_ratio_across_categories_creates_file():
    from visualize import plot_ratio_across_categories
    dn = _make_delta_norms()
    with tempfile.TemporaryDirectory() as tmpdir:
        out = os.path.join(tmpdir, "fig4.png")
        plot_ratio_across_categories(dn["mohawk"], dn["lawcat"], out)
        assert os.path.exists(out)


def test_generate_all_figures():
    from visualize import generate_all_figures
    dn = _make_delta_norms()
    analysis = {"interaction_ratio": 3.0, "interaction_ratio_ci_low": 1.5, "interaction_ratio_ci_high": 5.0}
    with tempfile.TemporaryDirectory() as tmpdir:
        generate_all_figures(dn, analysis, tmpdir)
        for fname in ["fig1_bar.png", "fig2_heatmap.png", "fig3_errorbars.png", "fig4_ratio.png"]:
            assert os.path.exists(os.path.join(tmpdir, fname)), f"Missing {fname}"
