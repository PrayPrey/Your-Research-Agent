---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7]
hypothesis_id: h-m1
type: MECHANISM
generated_at: 2026-08-21
author: yoon303@etri.re.kr
---

# PRD: H-M1 — Variance Selection Ranking Signal Validation

## 1. Executive Summary

H-M1 validates that the variance-based top-50 problem selection (variance_i = p_i*(1-p_i)) from H-E1 profiling produces a **real, non-random signal** — the selected problems genuinely have higher mean variance than a random-50 baseline. This is a pure statistical analysis experiment: no model inference, no training. The input is the profiling output JSON from H-E1; the output is a comparison report, gate decision, and 4 diagnostic figures.

**Gate:** MUST_WORK — mean(variance_i, variance-50) > mean(variance_i, random-50). Failure invalidates H-M2 through H-M4.

---

## 2. Problem Statement

H-E1 confirmed that the MBPP training split has sufficient variance structure (>50 problems with variance_i > 0.1). H-M1 answers: does the top-50 variance ranking actually select problems that are **more informative** than a random selection? This validates the **mechanism** behind YOURA's variance-guided curriculum — that the profiling signal is real and the ranking is stable, not a sampling artifact.

**Success demonstrates:** The top-50 selection by variance_i provides higher expected gradient signal than random-50, confirming that GRPO training on variance-selected problems will encounter fewer silent groups.

---

## 3. Functional Requirements

### FR-1: Load H-E1 Profiling Artifacts
- Load `docs/youra_research/h-e1/results/mbpp_variance_profile.json`
- Parse `problems` dict (keyed by task_id str) → numpy arrays: `problem_ids`, `p_i`, `variance_i` (shape 374)
- Read `k` from `data["metrics"]["k"]` (actual value may differ from spec; do not hardcode)
- Validate: p_i ∈ [0,1], variance_i ∈ [0,0.25]
- **Fallback:** If JSON absent, call H-E1 `profile_mbpp.py` via subprocess to regenerate

### FR-2: Variance-Guided Top-50 Selection
- Sort all 374 problems by variance_i descending (numpy argsort, recomputed — not from stored rank)
- Select top-50 indices (deterministic)
- Compute: `variance_50_var = variance_i[top50_idx]`
- Compute: `mean_var_selected = mean(variance_50_var)`

### FR-3: Random-50 Baseline
- Generate random-50 with fixed seed=42: `numpy.random.default_rng(42).choice(374, 50, replace=False)`
- Compute: `mean_var_random = mean(variance_i[random50_idx])`

### FR-4: Primary Gate Metric
- `gate_passed = mean_var_selected > mean_var_random`
- `difference = mean_var_selected - mean_var_random`
- Log: `[H-M1] Gate: mean_var_selected={:.4f} > mean_var_random={:.4f}: {gate_passed}`

### FR-5: Boundary Non-Degeneracy (Diagnostic)
- `boundary_gap = variance_i[rank-50] - variance_i[rank-51]`
- Expected: boundary_gap > 0; diagnostic only, does not gate

### FR-6: Mann-Whitney U Test
- `scipy.stats.mannwhitneyu(variance_50_var, random_50_var, alternative='greater')`
- Report: `mwu_stat`, `mwu_p`; expected p < 0.05 (diagnostic)

### FR-7: Mechanism Verification Asserts
```python
assert len(variance_50_idx) == 50
assert variance_i[ranked_idx[0]] >= variance_i[ranked_idx[-1]]
assert np.all(variance_i[variance_50_idx] >= variance_i[ranked_idx[50]])
```

### FR-8: Visualization — 4 Figures
- **Fig 1 (mandatory):** Bar chart: mean(variance_i) for variance-50 vs random-50, individual data points as strip plot
- **Fig 2:** Side-by-side histograms of variance_i (bins=10, [0,0.25]); overlay full-374 in grey
- **Fig 3:** Rank plot: sorted variance_i for 374 problems, vertical line at rank-50 boundary, shaded selected region
- **Fig 4:** Empirical CDF of variance_i for variance-50 vs random-50

Output: `docs/youra_research/h-m1/figures/`

### FR-9: Results JSON
Save `docs/youra_research/h-m1/results/comparison_results.json`:
```json
{
  "gate_passed": bool,
  "mean_var_selected": float,
  "mean_var_random": float,
  "difference": float,
  "boundary_gap": float,
  "mwu_stat": float,
  "mwu_p": float,
  "variance_50_ids": [int, ...],
  "random_50_ids": [int, ...],
  "seed": 42
}
```

---

## 4. Data Specification

### Primary Input: H-E1 Profiling Output (local, no download)
- **Source:** `docs/youra_research/h-e1/results/mbpp_variance_profile.json`
- **Format:** JSON with `problems` dict (task_id str → {p_i, variance_i, pass_count, k, rank_by_variance}), plus `gate_passed`, `metrics`, `top_ids`
- **Size:** 374 problems

### Fallback Dataset (only if H-E1 JSON absent; auto-downloads)
- **Source:** HuggingFace `google-research-datasets/mbpp`, split="train"
- **Load:** `load_dataset("google-research-datasets/mbpp", "full", split="train")`

---

## 5. Models

**Primary path:** No model needed — operates on H-E1 profiling JSON.

**Fallback only** (if JSON absent): `deepseek-ai/deepseek-coder-7b-instruct-v1.5`, frozen, bfloat16, k=8 completions (~2-4h GPU).

---

## 6. Evaluation Metrics

| Metric | Type | Gate | Expected |
|--------|------|------|----------|
| `mean_var_selected > mean_var_random` | Primary | MUST PASS | difference > 0.05 |
| `boundary_gap > 0` | Diagnostic | — | >0 |
| Mann-Whitney U p-value | Statistical | Diagnostic | <0.05 |

**PoC Pass Condition:**
1. `mean_var_selected > mean_var_random`
2. Code runs without error
3. `boundary_gap > 0` (desirable)

---

## 7. Dependencies

### 7.1 Python Packages
```
numpy>=1.20
scipy>=1.7
matplotlib>=3.5
datasets>=2.0        # fallback only
transformers>=4.35   # fallback only
torch>=2.0           # fallback only
```

### 7.2 Local Artifacts
- `docs/youra_research/h-e1/results/mbpp_variance_profile.json` — primary input (present)
- `docs/youra_research/h-e1/code/profile_mbpp.py` — fallback subprocess target

---

## 8. Non-Functional Requirements

- **Reproducibility:** seed=42 for random-50; deterministic numpy argsort
- **Compute:** ~30 seconds CPU (primary); ~2-4h GPU (fallback)
- **No training:** Zero gradient updates
- **Output:** All artifacts in `docs/youra_research/h-m1/`

---

## 9. Success Criteria

**PASS:** `mean_var_selected > mean_var_random`, code runs, figures generated
**FAIL/PIVOT:** `mean_var_selected <= mean_var_random` → pivot k=16 or alternative criterion

Downstream: PASS → H-M2–H-M4 proceed. FAIL → full chain invalidated.
