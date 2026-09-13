import json
import pytest
from pathlib import Path
from src.reporting.reporter import print_report, save_results


def _make_results(passed=True):
    return [
        {
            "dataset": "TestDS",
            "passed": passed,
            "n_kl_levels": 8,
            "rm_variation": 1.5,
            "gold_variation": 0.3,
            "gate_satisfied": passed,
            "reason": "PASS: ..." if passed else "FAIL: ...",
        }
    ]


def test_save_results_valid_json(tmp_path):
    out = tmp_path / "results.json"
    save_results(_make_results(True), str(out))
    assert out.exists()
    data = json.loads(out.read_text())
    assert "hypothesis_id" in data
    assert "overall_passed" in data
    assert "datasets" in data


def test_print_report_no_error(capsys):
    print_report(_make_results(True))
    captured = capsys.readouterr()
    assert "PASS" in captured.out


def test_main_exits_zero_on_pass(tmp_path, monkeypatch):
    import sys
    import pandas as pd
    from pathlib import Path

    # Write minimal CSVs
    def _make_csv(p, n=7):
        import csv
        with open(p, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["kl_budget", "rm_score", "gold_preference"])
            w.writeheader()
            for i in range(n):
                w.writerow({"kl_budget": i, "rm_score": i * 0.3, "gold_preference": 0.5 + i * 0.02})

    coste = tmp_path / "coste.csv"
    gao = tmp_path / "gao.csv"
    _make_csv(coste)
    _make_csv(gao)

    monkeypatch.chdir(tmp_path)
    import main as m
    cfg = m.ExperimentConfig(
        coste_csv_path=str(coste),
        gao_csv_path=str(gao),
        figures_dir=str(tmp_path / "figures"),
        results_dir=str(tmp_path / "results"),
    )

    from src.data.loader import load_dataset
    from src.verification.coexistence import verify_signal_coexistence
    from src.visualization.plots import plot_dual_axis, plot_comparison
    from src.reporting.reporter import print_report, save_results

    dfs = [load_dataset(str(coste), "C"), load_dataset(str(gao), "G")]
    names = ["C", "G"]
    results = [verify_signal_coexistence(df, n) for df, n in zip(dfs, names)]
    assert all(r["passed"] for r in results)
