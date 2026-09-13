import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import tempfile
import pandas as pd
from config import Config
from visualizer import Visualizer


def _make_rates_df(n=10):
    subtasks = [f"task_{i}" for i in range(n)]
    rates = [i / n for i in range(n)]
    return pd.DataFrame({"subtask": subtasks, "n_items": [50] * n,
                         "n_contaminated": [int(r * 50) for r in rates],
                         "rate": rates})


def test_plot_contamination_rates_bar_creates_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg = Config(figures_dir=tmpdir)
        viz = Visualizer(cfg)
        df = _make_rates_df()
        viz.plot_contamination_rates_bar(df, p_value=0.001)
        assert os.path.exists(os.path.join(tmpdir, "contamination_rates_barplot.png"))


def test_save_results_writes_valid_csv_and_json():
    import json
    import pandas as pd
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from run_experiment import save_results
    from config import Config

    with tempfile.TemporaryDirectory() as tmpdir:
        cfg = Config(results_dir=tmpdir)
        df = _make_rates_df()
        stats = {"kruskal_stat": 10.0, "p_value": 0.001, "gate_pass": True, "max_pair_diff": 0.5}
        save_results(df, stats, cfg)

        csv_path = os.path.join(tmpdir, "contamination_rates.csv")
        json_path = os.path.join(tmpdir, "statistical_tests.json")

        assert os.path.exists(csv_path), f"CSV not found at {csv_path}"
        assert os.path.exists(json_path), f"JSON not found at {json_path}"

        loaded_df = pd.read_csv(csv_path)
        assert "subtask" in loaded_df.columns
        assert "rate" in loaded_df.columns

        with open(json_path) as f:
            loaded_stats = json.load(f)
        assert "p_value" in loaded_stats
        assert "gate_pass" in loaded_stats
