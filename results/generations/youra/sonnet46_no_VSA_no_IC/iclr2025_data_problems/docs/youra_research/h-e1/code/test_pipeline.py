"""Minimal self-test for h-e1 pipeline. Run after lookup + trajectories complete."""
import sys
import json
import numpy as np
from pathlib import Path

CODE_DIR = Path(__file__).parent
sys.path.insert(0, str(CODE_DIR))

from src.data.domain_lookup import PILE_DOMAINS
from src.data.loader import build_checkpoint_steps, TOKENS_PER_STEP, SEQ_LEN
from src.analysis.stats import compute_variance_stats
from src.compute.trajectories import compute_domain_exposure_trajectories


def test_checkpoint_steps():
    steps = build_checkpoint_steps()
    assert len(steps) == 154, f"Expected 154, got {len(steps)}"
    assert steps[0] == 0
    assert steps[-1] == 143000
    assert steps == sorted(steps)
    print("PASS: test_checkpoint_steps")


def test_pile_domains():
    assert len(PILE_DOMAINS) == 22, f"Expected 22 domains, got {len(PILE_DOMAINS)}"
    assert "Pile-CC" in PILE_DOMAINS
    assert "Wikipedia (en)" in PILE_DOMAINS
    print("PASS: test_pile_domains")


def test_step_to_sample():
    from src.data.loader import step_to_sample
    assert step_to_sample(0) == 0
    assert step_to_sample(1) == TOKENS_PER_STEP // SEQ_LEN
    assert step_to_sample(143000) == 143000 * TOKENS_PER_STEP // SEQ_LEN
    print("PASS: test_step_to_sample")


def test_trajectories_synthetic():
    """Test trajectory computation with synthetic doc_idx and domain lookup."""
    n_docs = 1000
    doc_idx = np.arange(n_docs)  # identity mapping
    # Synthetic domain lookup: alternating 4 domains
    domains = PILE_DOMAINS[:4]
    doc_to_domain = {i: domains[i % 4] for i in range(n_docs)}

    # Mini checkpoint steps (only first few for speed)
    mini_steps = [0, 1, 2, 4, 8]

    from src.compute.trajectories import compute_domain_exposure_trajectories

    # Use the full PILE_DOMAINS list but only 4 will have non-zero counts
    traj = compute_domain_exposure_trajectories(
        type('DS', (), {'doc_idx': doc_idx, '__len__': lambda self: n_docs})(),
        doc_to_domain,
        mini_steps,
        PILE_DOMAINS,
    )

    assert traj.shape == (22, 5), f"Bad shape: {traj.shape}"
    assert not np.isnan(traj).any(), "NaN in trajectories"
    # 4 domains should each have ~25% exposure
    for step_idx in range(1, 5):
        non_zero = (traj[:, step_idx] > 0).sum()
        assert non_zero == 4, f"Expected 4 non-zero domains, got {non_zero}"
    print("PASS: test_trajectories_synthetic")


def test_variance_stats():
    # Synthetic: one domain varies, others flat
    traj = np.zeros((22, 154))
    traj[0] = np.linspace(0.1, 0.9, 154)  # high variance
    traj[1:] = 0.01  # low variance

    stats = compute_variance_stats(traj)
    assert "per_domain_std" in stats
    assert stats["per_domain_std"][0] > 0.1  # domain 0 has high std
    assert stats["n_domains_passing"] >= 1
    print("PASS: test_variance_stats")


def test_results_json():
    results_path = CODE_DIR / "outputs" / "results.json"
    if not results_path.exists():
        print("SKIP: test_results_json (not yet generated)")
        return
    with open(results_path) as f:
        results = json.load(f)
    assert "gate_passed" in results
    assert "per_model_stats" in results
    assert "domain_names" in results
    assert len(results["domain_names"]) == 22
    print(f"PASS: test_results_json (gate_passed={results['gate_passed']})")


if __name__ == "__main__":
    test_checkpoint_steps()
    test_pile_domains()
    test_step_to_sample()
    test_trajectories_synthetic()
    test_variance_stats()
    test_results_json()
    print("\nAll tests passed!")
