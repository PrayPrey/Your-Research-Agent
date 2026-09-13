import sys
import os
import numpy as np
import tempfile
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from analyze import bootstrap_ci, load_grad_norms


def test_bootstrap_ci_excludes_zero():
    # ratio norms consistently higher -> CI should exclude 0
    np.random.seed(42)
    binary = np.random.normal(1.0, 0.1, 400)
    ratio = np.random.normal(2.0, 0.1, 400)
    result = bootstrap_ci(binary, ratio, n_bootstrap=500)
    assert result["mean_diff"] > 0
    assert result["excludes_zero"] is True
    assert result["ci_lower"] < result["ci_upper"]


def test_bootstrap_ci_includes_zero():
    # equal norms -> CI should include 0
    np.random.seed(42)
    binary = np.ones(400)
    ratio = np.ones(400)
    result = bootstrap_ci(binary, ratio, n_bootstrap=500)
    assert abs(result["mean_diff"]) < 1e-10
    assert result["excludes_zero"] is False


def test_load_grad_norms():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("global_step,grad_norm,mean_reward,std_reward\n")
        for i in range(1, 6):
            f.write(f"{i},{float(i)},{0.1},{0.01}\n")
        path = f.name
    try:
        df = load_grad_norms(path)
        assert list(df.columns) == ["global_step", "grad_norm", "mean_reward", "std_reward"]
        assert len(df) == 5
        assert df["global_step"].tolist() == [1, 2, 3, 4, 5]
    finally:
        os.unlink(path)


if __name__ == "__main__":
    test_bootstrap_ci_excludes_zero()
    test_bootstrap_ci_includes_zero()
    test_load_grad_norms()
    print("analyze tests passed")
