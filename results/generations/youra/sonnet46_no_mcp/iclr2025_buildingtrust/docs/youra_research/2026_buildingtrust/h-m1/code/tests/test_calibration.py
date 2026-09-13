import sys, os, json, tempfile
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import numpy as np
import calibration


def _make_sample(log_probs, target):
    return {
        "filtered_resps": [[lp, True] for lp in log_probs],
        "target": target,
    }


def test_compute_ece_brier_perfect():
    # All correct with high confidence
    samples = []
    for _ in range(100):
        lp = [0.0, -5.0, -5.0, -5.0]  # choice 0 is best
        samples.append(_make_sample(lp, 0))
    ece, brier = calibration.compute_ece_brier(samples)
    assert isinstance(ece, float)
    assert isinstance(brier, float)
    assert 0.0 <= ece <= 1.0
    assert 0.0 <= brier <= 1.0


def test_compute_ece_brier_returns_tuple():
    samples = [_make_sample([0.0, -1.0, -2.0, -3.0], 0) for _ in range(20)]
    result = calibration.compute_ece_brier(samples)
    assert len(result) == 2


def test_compute_ece_brier_empty():
    ece, brier = calibration.compute_ece_brier([])
    assert np.isnan(ece)
    assert np.isnan(brier)


def test_load_mmlu_samples_missing_raises():
    with tempfile.TemporaryDirectory() as tmp:
        try:
            calibration.load_mmlu_samples(Path(tmp) / "nonexistent")
            assert False, "Should raise"
        except FileNotFoundError:
            pass


def test_load_mmlu_samples_reads_jsonl():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp)
        sample = {"filtered_resps": [[0.0, True], [-1.0, False], [-2.0, False], [-3.0, False]], "target": 0}
        with open(p / "samples_mmlu_test.jsonl", "w") as f:
            f.write(json.dumps(sample) + "\n")
        samples = calibration.load_mmlu_samples(p)
        assert len(samples) == 1


def test_extract_calibration_keys():
    """Test that extract_calibration_for_model returns required keys (mocked)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        model_dir = tmp_path / "test-model" / "greedy"
        model_dir.mkdir(parents=True)
        sample = {"filtered_resps": [[0.0, True], [-1.0, False], [-2.0, False], [-3.0, False]], "target": 0}
        with open(model_dir / "samples_mmlu_test.jsonl", "w") as f:
            for _ in range(50):
                f.write(json.dumps(sample) + "\n")

        # Create stochastic dirs
        for seed in [42, 123, 456]:
            sd = tmp_path / "test-model" / f"stochastic_seed{seed}"
            sd.mkdir(parents=True)
            with open(sd / "samples_mmlu_test.jsonl", "w") as f:
                for _ in range(50):
                    f.write(json.dumps(sample) + "\n")

        result = calibration.extract_calibration_for_model("test-model", tmp_path)
        assert "ece_greedy" in result
        assert "brier_greedy" in result
        assert "ece_stochastic" in result
        assert "brier_stochastic" in result
