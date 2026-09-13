---
title: "Logic: H-E1 - Alignment-Induced Brier Reliability Overconfidence"
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
phase: Phase 3
date: 2026-03-14
tier: LIGHT
---

Applied: Standard evaluation pipeline (no domain-specific KB match)

# Logic: H-E1 — Alignment-Induced Brier Reliability Overconfidence

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Verify Checkpoints & Run lm-eval [Complexity: 14, Budget: 3 subtasks]

Applied: Standard shell iteration + HuggingFace ID resolution pattern

### API Signatures

```python
# calibration_analysis.py constants
BASE_MODEL_IDS: dict[str, str] = {
    "1.4b": "EleutherAI/pythia-1.4b",
    "2.8b": "EleutherAI/pythia-2.8b",
    "6.9b": "EleutherAI/pythia-6.9b",
}
# ALIGNED_MODEL_IDS filled by coder after HF Hub search for Li et al. 2024
ALIGNED_MODEL_IDS: dict[str, dict[str, str]] = {
    "1.4b": {"sft": "PLACEHOLDER", "dpo": "PLACEHOLDER", "ppo": "PLACEHOLDER"},
    "2.8b": {"sft": "PLACEHOLDER", "dpo": "PLACEHOLDER", "ppo": "PLACEHOLDER"},
    "6.9b": {"sft": "PLACEHOLDER", "dpo": "PLACEHOLDER", "ppo": "PLACEHOLDER"},
}
# LLaMA-2 proxies for Risk R1 fallback
FALLBACK_MODEL_IDS: dict[str, str] = {
    "sft": "meta-llama/Llama-2-7b-hf",
    "dpo": "meta-llama/Llama-2-7b-chat-hf",
    "ppo": "meta-llama/Llama-2-7b-chat-hf",
}

def parse_model_ids(
    fallback_sizes: list[str] | None = None,
) -> list[tuple[str, str]]:
    """Return list of (model_key, hf_id) for all 9 models.

    model_key format: "pythia-{size}-{alignment}"
    fallback_sizes: list of sizes to substitute with FALLBACK_MODEL_IDS (Risk R1)
    Returns: 9 (key, hf_id) tuples in fixed order
    """
    ...
```

```bash
#!/usr/bin/env bash
# run_evaluation.sh
# Usage: bash run_evaluation.sh [--smoke-test]
# --smoke-test: run 1 model, 10 items only

set -e
OUTPUT_BASE="./results"
BATCH_SIZE=8

# MODEL_KEYS and MODEL_IDS filled by coder after parse_model_ids() verification
MODEL_KEYS=( "pythia-1.4b-base" ... )  # 9 entries
MODEL_IDS=(  "EleutherAI/pythia-1.4b" ... )  # 9 entries matching MODEL_KEYS

for i in "${!MODEL_IDS[@]}"; do
  MODEL_KEY="${MODEL_KEYS[$i]}"
  MODEL_ID="${MODEL_IDS[$i]}"
  OUT_DIR="${OUTPUT_BASE}/${MODEL_KEY}"
  mkdir -p "${OUT_DIR}"

  lm_eval --model hf \
    --model_args "pretrained=${MODEL_ID},dtype=float16" \
    --tasks mmlu \
    --num_fewshot 0 \
    --output_path "${OUT_DIR}/" \
    --log_samples \
    --device cuda:0 \
    --batch_size ${BATCH_SIZE} \
  || lm_eval --model hf \
       --model_args "pretrained=${MODEL_ID},dtype=float16" \
       --tasks mmlu \
       --num_fewshot 0 \
       --output_path "${OUT_DIR}/" \
       --log_samples \
       --device cuda:0 \
       --batch_size 4  # OOM fallback
done
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | parse_model_ids | Build ID dict; HF Hub verification; populate fallback for Risk R1 |
| L-1-2 | run_evaluation.sh | Shell script with OOM retry (batch 8 -> 4) and --smoke-test flag |
| L-1-3 | Smoke test | Run 1 model 10 items; inspect JSONL output field names for load_lmeval_samples |

---

## A-2: Implement Brier Decomp + ECE [Complexity: 13, Budget: 2 subtasks]

Applied: Murphy 1973 bin-based decomposition, Guo 2017 ECE

### API Signatures

```python
import numpy as np
from scipy.special import softmax

def load_lmeval_samples(
    model_id: str,
    results_dir: str = "./results",
) -> tuple[np.ndarray, np.ndarray]:
    """Parse lm-eval --log_samples JSONL for one model.

    Returns: (logprobs, y_true)
    logprobs: (N, 4) float64 — raw log-probs before softmax
    y_true:   (N,)   int64  — gold labels 0-3
    """
    # Glob: results_dir/{model_id}/**/samples_mmlu*.jsonl
    # Per JSON line: extract 4-option log-probs and gold label field
    # Stack into arrays; verify shape (N, 4)
    ...


def compute_brier_decomposition(
    y_true: np.ndarray,   # (N,) int64  labels in {0,1,2,3}
    y_prob: np.ndarray,   # (N, 4) float64 softmax probabilities
    n_bins: int = 15,
) -> tuple[float, float, float]:
    """Murphy (1973) 3-component Brier decomposition.

    Returns: (reliability, resolution, uncertainty) all float
    reliability = Σ_k Σ_j (n_kj/N)(f_kj - o_kj)^2
    resolution  = Σ_k Σ_j (n_kj/N)(o_kj - o_bar_j)^2
    uncertainty = Σ_j o_bar_j * (1 - o_bar_j)
    k = bin index, j = class index (0..3)
    """
    # 1. one_hot = (y_true[:,None] == np.arange(4))  # (N, 4) bool
    # 2. bin_edges = np.linspace(0, 1, n_bins + 1)
    # 3. REL = RES = 0.0
    # 4. For j in 0..3:
    #      o_bar_j = one_hot[:, j].mean()
    #      bin_idx = np.digitize(y_prob[:, j], bin_edges) - 1  # (N,)
    #      bin_idx = np.clip(bin_idx, 0, n_bins - 1)
    #      For b in 0..n_bins-1:
    #        mask = (bin_idx == b)
    #        n_b = mask.sum()
    #        if n_b == 0: continue
    #        f_bj = y_prob[mask, j].mean()
    #        o_bj = one_hot[mask, j].mean()
    #        REL += (n_b / N) * (f_bj - o_bj) ** 2
    #        RES += (n_b / N) * (o_bj - o_bar_j) ** 2
    # 5. UNC = sum_j o_bar_j * (1 - o_bar_j)
    # 6. return (REL, RES, UNC)
    ...


def compute_ece(
    y_true: np.ndarray,   # (N,) int64  labels in {0,1,2,3}
    y_prob: np.ndarray,   # (N, 4) float64 softmax probabilities
    n_bins: int = 15,
) -> float:
    """Guo et al. (2017) top-1 confidence ECE.

    Returns: ECE scalar float in [0, 1]
    """
    # 1. conf    = y_prob.max(axis=1)           # (N,)
    # 2. pred    = y_prob.argmax(axis=1)         # (N,)
    # 3. correct = (pred == y_true).astype(float) # (N,)
    # 4. bin_edges = np.linspace(0, 1, n_bins + 1)
    # 5. ECE = 0.0
    #    For b in 0..n_bins-1:
    #      mask = (conf >= bin_edges[b]) & (conf < bin_edges[b+1])
    #      if mask.sum() == 0: continue
    #      ECE += (mask.sum() / N) * abs(correct[mask].mean() - conf[mask].mean())
    # 6. return ECE
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| logprobs (raw) | (N, 4) | N ~ 14042 for full MMLU |
| y_prob | (N, 4) | softmax(logprobs, axis=-1) |
| y_true | (N,) | int64, 0-indexed |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | load_lmeval_samples | JSONL glob + parse; field name confirmed from smoke test (L-1-3) |
| L-2-2 | compute_brier_decomposition + compute_ece | Murphy 1973 bin loop; Guo 2017 top-1 ECE |

---

## A-3: Bootstrap CI + Delta [Complexity: 11, Budget: 2 subtasks]

Applied: Percentile bootstrap CI (2.5th / 97.5th percentile)

### API Signatures

```python
def compute_delta_reliability(
    base_logprobs: np.ndarray,     # (N, 4) float64 raw log-probs
    aligned_logprobs: np.ndarray,  # (N, 4) float64 raw log-probs
    y_true: np.ndarray,            # (N,)   int64
    n_bins: int = 15,
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> tuple[float, float, float]:
    """Bootstrap 95% CI for delta Brier reliability (aligned - base).

    Returns: (delta_reliability, ci_lower, ci_upper)
    delta_reliability: point estimate (aligned.reliability - base.reliability)
    ci_lower, ci_upper: 2.5th / 97.5th percentile of bootstrap distribution
    """
    # 1. base_prob    = softmax(base_logprobs,    axis=-1)  # (N, 4)
    # 2. aligned_prob = softmax(aligned_logprobs, axis=-1)  # (N, 4)
    # 3. delta = compute_brier_decomposition(y_true, aligned_prob)[0]
    #          - compute_brier_decomposition(y_true, base_prob)[0]
    # 4. rng = np.random.default_rng(seed)
    # 5. boot_deltas = np.empty(n_bootstrap)
    #    for b in range(n_bootstrap):
    #      idx = rng.integers(0, N, size=N)
    #      rel_base    = compute_brier_decomposition(y_true[idx], base_prob[idx])[0]
    #      rel_aligned = compute_brier_decomposition(y_true[idx], aligned_prob[idx])[0]
    #      boot_deltas[b] = rel_aligned - rel_base
    # 6. ci_lower = np.percentile(boot_deltas, 2.5)
    #    ci_upper = np.percentile(boot_deltas, 97.5)
    # 7. return (delta, ci_lower, ci_upper)
    ...


def run_analysis(results_dir: str = "./results") -> dict:
    """Load all models, compute all metrics, save calibration_results.json.

    Returns results_dict keyed by model_id.
    Schema per key:
      base models:    {"ece": float, "brier_rel": float, "brier_res": float, "brier_unc": float}
      aligned models: {"ece": float, "brier_rel": float, "brier_res": float, "brier_unc": float,
                       "delta_rel": float, "ci_lower": float, "ci_upper": float}
    """
    # 1. all_logprobs: dict[str, np.ndarray]  # model_id -> (N, 4)
    #    all_ytrue:    dict[str, np.ndarray]  # model_id -> (N,)
    #    For each model_id in MODELS:
    #      logprobs, y_true = load_lmeval_samples(model_id, results_dir)
    #      all_logprobs[model_id] = logprobs
    #      all_ytrue[model_id]    = y_true
    # 2. For each model_id:
    #      y_prob = softmax(all_logprobs[model_id], axis=-1)
    #      rel, res, unc = compute_brier_decomposition(all_ytrue[model_id], y_prob)
    #      ece = compute_ece(all_ytrue[model_id], y_prob)
    #      results[model_id] = {"ece": ece, "brier_rel": rel, "brier_res": res, "brier_unc": unc}
    # 3. For each size in ["1.4b", "2.8b", "6.9b"]:
    #      base_id = f"pythia-{size}-base"
    #      For alignment in ["sft", "dpo", "ppo"]:
    #        aligned_id = f"pythia-{size}-{alignment}"
    #        delta, ci_lo, ci_hi = compute_delta_reliability(
    #            all_logprobs[base_id], all_logprobs[aligned_id], all_ytrue[base_id])
    #        results[aligned_id].update(delta_rel=delta, ci_lower=ci_lo, ci_upper=ci_hi)
    # 4. json.dump(results, open(f"{results_dir}/calibration_results.json", "w"), indent=2)
    # 5. Write CSV summary rows: model_id, ece, brier_rel, delta_rel, ci_lower, ci_upper
    # 6. return results
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | compute_delta_reliability | Bootstrap percentile CI; rng.integers(0, N, N) resampling |
| L-3-2 | run_analysis | Orchestrate all metrics; JSON + CSV output; argparse --smoke-test |

---

## Constants Reference

```python
# calibration_analysis.py top-level
MODELS: list[str] = [
    "pythia-1.4b-base", "pythia-1.4b-sft", "pythia-1.4b-dpo", "pythia-1.4b-ppo",
    "pythia-2.8b-base", "pythia-2.8b-sft", "pythia-2.8b-dpo", "pythia-2.8b-ppo",
    "pythia-6.9b-base", "pythia-6.9b-sft", "pythia-6.9b-dpo", "pythia-6.9b-ppo",
]
N_BINS: int = 15
N_BOOTSTRAP: int = 1000
SEED: int = 42
RESULTS_DIR: str = "./results"
```

---

*Generated: Phase 3 Logic Agent*
*Hypothesis: H-E1 (EXISTENCE, FOUNDATION, LIGHT tier)*
*Subtasks used: 7/7 (A-1: 3, A-2: 2, A-3: 2)*
