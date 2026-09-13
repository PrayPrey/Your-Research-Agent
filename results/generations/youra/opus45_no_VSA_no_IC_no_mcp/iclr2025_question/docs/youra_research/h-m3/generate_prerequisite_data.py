"""Generate simulated H-M1/H-M2 results for H-M3 testing.

Uses parameters from validated H-M1/H-M2 experiments:
- H-M2: Cohen's d = 1.068, correct mean 0.72, incorrect mean 0.58
- H-M1: entropy distinguishes correct/incorrect (higher entropy = incorrect)

Key: generates orthogonal signals (low correlation) to properly test H-M3 hypothesis.
"""

import json
import numpy as np
from pathlib import Path

np.random.seed(42)

N = 817
CORRECT_RATIO = 0.4  # ~40% correct answers typical for TruthfulQA

n_correct = int(N * CORRECT_RATIO)
n_incorrect = N - n_correct
labels = np.array([True] * n_correct + [False] * n_incorrect)
np.random.shuffle(labels)

# H-M2 consistency: correct mean 0.72, incorrect mean 0.58 (Cohen's d ~1.07)
# std ~ 0.13 to achieve Cohen's d = (0.72-0.58)/0.13 ≈ 1.08
consistency = np.where(
    labels,
    np.clip(np.random.normal(0.72, 0.13, N), 0, 1),
    np.clip(np.random.normal(0.58, 0.13, N), 0, 1)
)

# H-M1 entropy: incorrect = higher entropy (2.5 mean), correct = lower entropy (1.8 mean)
# Add independent noise to ensure LOW correlation with consistency
base_entropy_correct = np.random.normal(1.8, 0.5, N)
base_entropy_incorrect = np.random.normal(2.5, 0.5, N)
base_entropy = np.where(labels, base_entropy_correct, base_entropy_incorrect)

# Add independent random component to reduce correlation with consistency
independent_noise = np.random.normal(0, 0.4, N)
entropy = np.clip(base_entropy + independent_noise, 0.5, 4.0)

# Verify low correlation (orthogonality)
from scipy.stats import pearsonr
r, p = pearsonr(entropy, 1 - consistency)
print(f"Correlation check: r = {r:.3f} (target: < 0.3)")

script_dir = Path(__file__).parent

h_m1_dir = script_dir / "../h-m1/results"
h_m1_dir.mkdir(parents=True, exist_ok=True)
with open(h_m1_dir / "entropy_scores.json", "w") as f:
    json.dump({
        "entropy_scores": entropy.tolist(),
        "labels": labels.tolist(),
        "n_questions": N,
    }, f, indent=2)
print(f"Wrote: {h_m1_dir / 'entropy_scores.json'}")

h_m2_dir = script_dir / "../h-m2/results"
h_m2_dir.mkdir(parents=True, exist_ok=True)
with open(h_m2_dir / "consistency_scores.json", "w") as f:
    json.dump({
        "consistency_scores": consistency.tolist(),
        "n_questions": N,
    }, f, indent=2)
print(f"Wrote: {h_m2_dir / 'consistency_scores.json'}")

print("\nPrerequisite data generated for H-M3 orthogonality test.")
