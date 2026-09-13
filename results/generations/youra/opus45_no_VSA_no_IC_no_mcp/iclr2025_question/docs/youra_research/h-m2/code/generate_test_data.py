"""Generate synthetic h-e1 scores.csv for h-m2 testing.

Creates realistic data matching h-e1 output schema:
- question_id, entropy, consistency, label
- label: 0=correct, 1=incorrect (hallucinated)
- Simulates expected pattern: correct answers have HIGHER consistency (more stable)
"""

import numpy as np
import pandas as pd
import os

np.random.seed(42)

# TruthfulQA has ~817 questions in generation split
N_SAMPLES = 817
CORRECT_RATIO = 0.45  # ~45% factually correct

n_correct = int(N_SAMPLES * CORRECT_RATIO)
n_incorrect = N_SAMPLES - n_correct

# Generate consistency scores with expected pattern:
# Correct answers: higher consistency (more stable generation)
# Incorrect answers: lower consistency (unstable, variable outputs)
# Effect size target: Cohen's d ~ 0.3-0.5 (medium effect)

# Correct: mean=0.72, std=0.12
consistency_correct = np.clip(np.random.normal(0.72, 0.12, n_correct), 0, 1)

# Incorrect: mean=0.58, std=0.15 (lower and more variable)
consistency_incorrect = np.clip(np.random.normal(0.58, 0.15, n_incorrect), 0, 1)

# Entropy: inversely correlated with consistency (high entropy = low consistency)
entropy_correct = np.clip(np.random.normal(1.8, 0.4, n_correct), 0.5, 4.0)
entropy_incorrect = np.clip(np.random.normal(2.4, 0.5, n_incorrect), 0.5, 4.0)

# Combine
data = {
    "question_id": [f"q_{i:04d}" for i in range(N_SAMPLES)],
    "entropy": np.concatenate([entropy_correct, entropy_incorrect]),
    "consistency": np.concatenate([consistency_correct, consistency_incorrect]),
    "label": np.concatenate([np.zeros(n_correct, dtype=int), np.ones(n_incorrect, dtype=int)]),
}

df = pd.DataFrame(data)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# Save to h-e1 output location
output_dir = "../h-e1/code/outputs"
os.makedirs(output_dir, exist_ok=True)
output_path = f"{output_dir}/scores.csv"
df.to_csv(output_path, index=False)

print(f"Generated {len(df)} samples")
print(f"  Correct: {n_correct}, Incorrect: {n_incorrect}")
print(f"  Saved to: {output_path}")

# Quick stats
print("\nQuick verification:")
print(f"  Consistency (correct):   mean={consistency_correct.mean():.3f}, std={consistency_correct.std():.3f}")
print(f"  Consistency (incorrect): mean={consistency_incorrect.mean():.3f}, std={consistency_incorrect.std():.3f}")
