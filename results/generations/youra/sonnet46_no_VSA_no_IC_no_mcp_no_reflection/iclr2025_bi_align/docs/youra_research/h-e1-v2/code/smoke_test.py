"""Smoke test with synthetic data. Exits 1 on failure."""
import sys
import numpy as np

sys.path.insert(0, ".")
from stats_tester import mann_kendall, bootstrap_ci, evaluate_gate
from proxy_computer import compute_entropy, correction_freq, CORRECTION_REGEX


def run_smoke_test():
    errors = []

    # Test 1: increasing series should have tau > 0, p < 0.05
    series = np.arange(24, dtype=float) + np.random.default_rng(0).normal(0, 0.5, 24)
    res = mann_kendall(series)
    if not (res["tau"] > 0 and res["p"] < 0.05):
        errors.append(f"FAIL: increasing series not detected as trend (tau={res['tau']:.3f}, p={res['p']:.3f})")
    else:
        print(f"PASS: increasing trend detected (tau={res['tau']:.3f}, p={res['p']:.3f})")

    # Test 2: flat series gate should fail
    flat = np.ones(24)
    flat_res = mann_kendall(flat)
    # flat series has 0 variance, kendalltau returns nan/0; gate should not be significant
    if flat_res.get("significant", False):
        errors.append("FAIL: flat series incorrectly detected as significant trend")
    else:
        print("PASS: flat series correctly not significant")

    # Test 3: evaluate_gate
    mock_results = {
        "proxies": {
            "prompt_tokens": {"significant": True, "tau": 0.3, "p": 0.01},
            "vote_entropy": {"significant": True, "tau": 0.25, "p": 0.03},
            "correction_freq": {"significant": False, "tau": 0.05, "p": 0.4},
        }
    }
    evaluate_gate(mock_results)
    if not mock_results["gate"]["gate_passed"]:
        errors.append("FAIL: gate should pass with 2/3 significant proxies")
    else:
        print("PASS: gate evaluation correct (2/3 significant)")

    # Test 4: compute_entropy
    h = compute_entropy(100, 0, 0)
    if h != 0.0:
        errors.append(f"FAIL: entropy of pure distribution should be 0, got {h}")
    else:
        print("PASS: entropy(100,0,0) = 0.0")

    # Test 5: correction_freq regex
    conv = [
        {"role": "user", "content": "No, that's wrong."},
        {"role": "assistant", "content": "I apologize"},
        {"role": "user", "content": "Actually, I meant something else."},
    ]
    freq = correction_freq(conv)
    if freq <= 0:
        errors.append(f"FAIL: correction_freq should detect patterns, got {freq}")
    else:
        print(f"PASS: correction_freq={freq:.3f} (detected corrections)")

    # Test 6: bootstrap CI shape
    s = np.linspace(1, 10, 20)
    t = np.arange(20)
    ci = bootstrap_ci(s, t, B=100, seed=42)
    if not (len(ci) == 2 and ci[0] < ci[1]):
        errors.append(f"FAIL: bootstrap_ci should return (low, high), got {ci}")
    else:
        print(f"PASS: bootstrap_ci={ci}")

    if errors:
        for e in errors:
            print(e)
        sys.exit(1)
    print("\nAll smoke tests PASSED")


if __name__ == "__main__":
    run_smoke_test()
