# Product Requirements Document: H-M2
# Pre-Softmax Logit Margin Inflation — Alignment Confidence Mechanism

---

**Frontmatter:**
```yaml
hypothesis_id: h-m2
hypothesis_type: MECHANISM
tier: FULL
phase: Phase 3
generated_at: 2026-03-15
based_on: h-m2/02c_experiment_brief.md
prerequisites_satisfied:
  - h-e1 (MUST_WORK PASS): alignment inflates Brier reliability confirmed
  - h-m1 (MUST_WORK PASS): ECE_base < 0.15 for all 3 Pythia sizes confirmed
stepsCompleted:
  - Executive Summary
  - Problem Statement
  - Goals and Non-Goals
  - Functional Requirements
  - Data Specification
  - Evaluation Metrics
  - Non-Functional Requirements
  - Dependencies
  - Success Criteria
```

---

## 1. Executive Summary

H-M2 is a **logit-level mechanism verification** experiment that tests whether alignment training (SFT/DPO/PPO) inflates the pre-softmax confidence margin (top-1 minus top-2 log-probability) in Pythia LLMs evaluated on MMLU. This is causal Step 2 in the RLHF alignment → calibration degradation chain: H-E1 confirmed calibration degradation exists; H-M1 confirmed the causal baseline; H-M2 diagnoses the logit-level mechanism driving that degradation.

**Primary Implementation Path (PREFERRED — Zero New Compute):** Extract per-item log-prob vectors from cached H-E1 lm-eval `--log_samples` outputs and compute margin statistics. These log-probs ARE the pre-softmax values (lm-eval `loglikelihood` returns raw LM log-probs before softmax normalization).

**Fallback Path:** Re-run lm-eval v0.4.11 with `--log_samples` flag for all 12 Pythia models on MMLU if cached outputs lack per-item logit vectors.

**Gate:** SHOULD_WORK — Δmargin_PPO > 0 in ≥2/3 Pythia sizes with bootstrap 95% CI lower bound > 0. Failure → EXPLORE (alignment acts post-softmax; H2 candidate). Pipeline continues regardless.

---

## 2. Problem Statement

### Background

H-E1 demonstrated alignment increases Brier reliability; H-M1 confirmed base Pythia models are well-calibrated (ECE_base = {1.4b: 0.0849, 2.8b: 0.0597, 6.9b: 0.0792}). The question is: *how* does alignment inflate calibration error at the logit level? The confidence inflation mechanism (H1 in the main hypothesis) predicts that alignment training increases the gap between the highest and second-highest log-prob across answer choices — enlarging the effective "certainty signal" in the model's output distribution.

### Research Question

Under forced-choice MMLU evaluation, does alignment training (SFT/DPO/PPO) systematically increase mean pre-softmax logit margins (top-1 − top-2 log-prob) relative to matched Pythia base models, with the inflation ordered PPO >= DPO > SFT across model sizes?

### Mechanistic Importance

The margin inflation test discriminates between three mechanistic pathways:
- **H1 (Scale Distortion):** Margins inflate uniformly → Brier_rel increases (H-M2 tests this)
- **H2 (Boundary Shift):** Rank ordering changes → different mechanism, test in H-M3
- **H3 (Framing Susceptibility):** Subject-dependent patterns → test in H-M3 via TruthfulQA

---

## 3. Goals and Non-Goals

### Goals

1. **Compute Δmargin** for all 9 aligned model-size pairs (PPO/DPO/SFT × 1.4B/2.8B/6.9B)
2. **Verify SHOULD_WORK gate:** Δmargin_PPO > 0 in ≥2/3 sizes with bootstrap CI lower > 0
3. **Test gradient ordering:** Δmargin_PPO >= Δmargin_DPO > Δmargin_SFT via Wilcoxon signed-rank
4. **Generate 5 required figures** including gate metrics bar chart and mechanistic visualizations
5. **Produce 04_validation.md** report with PASS/FAIL gate result and exploration notes if FAIL

### Non-Goals

- Training any models
- Modifying lm-eval harness behavior
- Computing ECE or Brier decomposition (delegated to H-E1)
- Collecting new datasets
- Evaluating models outside the Pythia alignment ladder

---

## 4. Functional Requirements

### FR-1: Log-Probability Vector Extraction (Primary Path A)

**Priority:** MUST HAVE
**Source:** h-m2/02c_experiment_brief.md §Dataset + §Models

The system SHALL implement Path A (primary):
- Load cached H-E1 lm-eval `--log_samples` JSON outputs from `h-e1/results/`
- Parse per-item log-probability vectors of shape (N_items, 4) per model
- Verify N_items == 14042 for each model (MMLU full test set)
- Return structured dict: `{model_id: logprob_matrix}` for all 12 Pythia models

```python
# FR-1 Interface
def load_logprob_matrices(results_dir: str = "h-e1/results") -> dict[str, np.ndarray]:
    """
    Load cached lm-eval --log_samples outputs.
    Args:
        results_dir: Path to directory containing per-model lm-eval JSON outputs
    Returns:
        {model_id: logprob_matrix} where logprob_matrix.shape == (14042, 4)
        model_ids: "pythia-{1.4b|2.8b|6.9b}-{base|sft|dpo|ppo}"
    """
```

### FR-2: Fallback lm-eval Re-Execution (Path B)

**Priority:** MUST HAVE (fallback)
**Source:** h-m2/02c_experiment_brief.md §Training Protocol

The system SHALL implement Path B when H-E1 log-prob vectors are unavailable:
- Execute lm-eval v0.4.11 with `--log_samples` for all 12 Pythia models on MMLU
- Critical flag: `--log_samples` is REQUIRED to capture per-item logit vectors
- Save outputs to `h-m2/results/{model_id}/`
- Execute one model at a time (sequential for GPU memory management)

```bash
# FR-2 Execution Template (Path B fallback)
lm_eval --model hf \
  --model_args "pretrained=<MODEL_ID>,dtype=float32" \
  --tasks mmlu \
  --num_fewshot 4 \
  --output_path ./h-m2/results/<MODEL_ID>/ \
  --log_samples \
  --device cuda:0

# Model IDs (Risk R1 fallback — already cached from H-E1):
# Base: EleutherAI/pythia-{1.4b|2.8b|6.9b}
# SFT:  lomahony/pythia-{1.4b|2.8b|6.9b}-deduped-tldr
# DPO:  Leogrin/pythia-{1.4b|2.8b|6.9b}-sft-tldr-dpo
# PPO:  usvsnsp/pythia-{1.4b|2.8b|6.9b}-sft-tldr-ppo
```

### FR-3: Pre-Softmax Logit Margin Computation

**Priority:** MUST HAVE
**Source:** h-m2/02c_experiment_brief.md §Core Mechanism Implementation

The system SHALL implement margin computation as a new module `margin_analysis.py`:
- Extend h-e1/code/calibration_analysis.py (import, not reimplementation)
- Compute per-item margin: max(log_prob) − second_max(log_prob) over 4 choices
- Compute mean Δmargin = mean(margin_aligned) − mean(margin_base) per model pair
- Compute bootstrap 95% CI (n=1000) for each Δmargin value

```python
# FR-3 Interface (new module: h-m2/code/margin_analysis.py)
import numpy as np
from scipy import stats

def compute_logit_margins(logprob_matrix: np.ndarray) -> np.ndarray:
    """
    Args:
        logprob_matrix: np.ndarray shape (N_items, 4)
                        Pre-softmax log-probs from lm-eval loglikelihood
    Returns:
        margins: np.ndarray shape (N_items,)
                 margin_i = rank1_logprob_i − rank2_logprob_i
    """
    sorted_logprobs = np.sort(logprob_matrix, axis=1)[:, ::-1]
    return sorted_logprobs[:, 0] - sorted_logprobs[:, 1]

def compute_delta_margin(
    base_logprobs: np.ndarray,
    aligned_logprobs: np.ndarray,
    n_bootstrap: int = 1000,
    seed: int = 42
) -> tuple[float, float, float]:
    """
    Args:
        base_logprobs: (N_items, 4) from base model
        aligned_logprobs: (N_items, 4) from aligned model (same items)
        n_bootstrap: number of bootstrap resamples
    Returns:
        (delta_mean, ci_lower_95, ci_upper_95) in nats
    """
    np.random.seed(seed)
    base_margins = compute_logit_margins(base_logprobs)
    aligned_margins = compute_logit_margins(aligned_logprobs)
    delta_per_item = aligned_margins - base_margins
    delta_mean = float(np.mean(delta_per_item))
    n = len(delta_per_item)
    boot_means = [
        np.mean(np.random.choice(delta_per_item, n, replace=True))
        for _ in range(n_bootstrap)
    ]
    ci_lower = float(np.percentile(boot_means, 2.5))
    ci_upper = float(np.percentile(boot_means, 97.5))
    return delta_mean, ci_lower, ci_upper
```

### FR-4: SHOULD_WORK Gate Evaluation

**Priority:** MUST HAVE
**Source:** h-m2/02c_experiment_brief.md §Gate Condition

The system SHALL implement gate evaluation:
- Check Δmargin_PPO > 0 AND bootstrap CI lower > 0 for each Pythia size
- Gate PASS condition: ≥2/3 PPO sizes satisfy both conditions
- Return: gate_result ∈ {"PASS", "FAIL"} and exploration notes if FAIL

```python
# FR-4 Interface
def evaluate_should_work_gate(
    delta_results: dict[str, tuple[float, float, float]]
) -> tuple[str, list[str], dict]:
    """
    Args:
        delta_results: {model_pair: (delta_mean, ci_lower, ci_upper)}
                       model_pair format: "ppo_{size}" e.g. "ppo_1.4b"
    Returns:
        (gate_result, failed_checks, exploration_notes)
        gate_result: "PASS" if ≥2/3 PPO sizes have delta_mean > 0 AND ci_lower > 0
    """
    ppo_sizes = ["1.4b", "2.8b", "6.9b"]
    passing_sizes = []
    failed_checks = []
    for size in ppo_sizes:
        key = f"ppo_{size}"
        delta_mean, ci_lower, _ = delta_results.get(key, (-1, -1, -1))
        if delta_mean > 0 and ci_lower > 0:
            passing_sizes.append(size)
        else:
            failed_checks.append(f"PPO {size}: delta={delta_mean:.4f}, ci_lower={ci_lower:.4f}")
    gate_result = "PASS" if len(passing_sizes) >= 2 else "FAIL"
    exploration_notes = {}
    if gate_result == "FAIL":
        exploration_notes = {
            "action": "EXPLORE",
            "hypothesis": "Alignment may act post-softmax (H2 boundary shift candidate)",
            "next_step": "Check DPO margin results; proceed to H-M3 regardless"
        }
    return gate_result, failed_checks, exploration_notes
```

### FR-5: Gradient Ordering Test (PPO >= DPO > SFT)

**Priority:** SHOULD HAVE
**Source:** h-m2/02c_experiment_brief.md §Secondary Metric

The system SHALL test gradient ordering across 3 Pythia sizes using Wilcoxon signed-rank test:
- Compare Δmargin vectors (one value per model size) across alignment methods
- H0: PPO_delta == DPO_delta; H1: PPO_delta > DPO_delta (one-sided)
- H0: DPO_delta == SFT_delta; H1: DPO_delta > SFT_delta (one-sided)
- Report p-values and effect sizes

```python
# FR-5 Interface
def test_gradient_ordering(
    delta_ppo: list[float],   # Δmargin for PPO across 3 sizes
    delta_dpo: list[float],   # Δmargin for DPO across 3 sizes
    delta_sft: list[float]    # Δmargin for SFT across 3 sizes
) -> dict[str, float]:
    """
    Returns: {
        'ppo_ge_dpo_stat': Wilcoxon stat,
        'ppo_ge_dpo_p': p-value (one-sided, PPO > DPO),
        'dpo_gt_sft_stat': Wilcoxon stat,
        'dpo_gt_sft_p': p-value (one-sided, DPO > SFT)
    }
    Note: With n=3 (3 model sizes), Wilcoxon test has limited power.
    Sign test is equally valid; report both.
    """
    from scipy.stats import wilcoxon
    try:
        stat_pd, p_pd = wilcoxon(delta_ppo, delta_dpo, alternative='greater')
        stat_ds, p_ds = wilcoxon(delta_dpo, delta_sft, alternative='greater')
    except ValueError:
        # Fallback to sign test if ties present
        stat_pd, p_pd = float('nan'), float('nan')
        stat_ds, p_ds = float('nan'), float('nan')
    return {
        'ppo_ge_dpo_stat': float(stat_pd), 'ppo_ge_dpo_p': float(p_pd),
        'dpo_gt_sft_stat': float(stat_ds), 'dpo_gt_sft_p': float(p_ds)
    }
```

### FR-6: Mechanism Activation Verification

**Priority:** MUST HAVE
**Source:** h-m2/02c_experiment_brief.md §Mechanism Activation Indicators

The system SHALL verify mechanism activation before accepting results:
- Confirm logprob_matrix shape == (14042, 4) for each model
- Confirm margin values are positive (log-prob gaps should be ≥ 0 by construction)
- Log verification status and shape checks to stdout

```python
# FR-6 Interface
def verify_mechanism_activated(results_dict: dict) -> tuple[bool, dict]:
    """
    Verify that margin inflation mechanism was correctly computed.
    Returns: (mechanism_verified: bool, indicators: dict)
    """
    indicators = {
        "logprob_matrix_shape_ok": results_dict.get("n_items_processed") == 14042,
        "margins_positive": results_dict.get("ppo_1.4b_margin_mean", -1) >= 0,
        "delta_computed": results_dict.get("ppo_1.4b_delta_margin") is not None,
        "bootstrap_ci_computed": results_dict.get("ppo_1.4b_ci_lower") is not None,
        "delta_positive_ppo_count": sum(
            results_dict.get(f"ppo_{s}_delta_margin", -1) > 0
            for s in ["1.4b", "2.8b", "6.9b"]
        ),
        "ci_lower_positive_ppo_count": sum(
            results_dict.get(f"ppo_{s}_ci_lower", -1) > 0
            for s in ["1.4b", "2.8b", "6.9b"]
        )
    }
    mechanism_verified = (
        indicators["logprob_matrix_shape_ok"] and
        indicators["margins_positive"] and
        indicators["delta_computed"]
    )
    return mechanism_verified, indicators
```

### FR-7: Figure Generation

**Priority:** MUST HAVE (mandatory) + SHOULD HAVE (additional)
**Source:** h-m2/02c_experiment_brief.md §Visualization Requirements

The system SHALL generate:

**Mandatory Figure:**
- **Figure 1:** Δmargin bar chart (PPO/DPO/SFT × 1.4B/2.8B/6.9B) with bootstrap 95% CI error bars
  - X-axis: model size (1.4B, 2.8B, 6.9B); grouped bars per alignment method
  - Y-axis: Δmargin (nats); dashed zero line
  - Color: red=PPO, orange=DPO, blue=SFT
  - Save to: `h-m2/figures/figure_01_delta_margin_gate.png`

**Additional Figures (Strongly Recommended):**
- **Figure 2:** Margin Distribution Violin Plot — full per-item margin distributions for base vs PPO 1.4B
  - Save to: `h-m2/figures/figure_02_margin_violin.png`
- **Figure 3:** Δmargin vs ΔECE Scatter — Δmargin_PPO vs ΔECE_PPO across 9 model-size pairs
  - Save to: `h-m2/figures/figure_03_delta_margin_vs_delta_ece.png`
- **Figure 4:** Gradient Ordering Heatmap — 3×3 heatmap (alignment × model size) of Δmargin
  - Save to: `h-m2/figures/figure_04_gradient_ordering_heatmap.png`
- **Figure 5:** Cumulative Margin Distribution (CDF) — base vs PPO 1.4B margin CDFs
  - Save to: `h-m2/figures/figure_05_margin_cdf.png`

### FR-8: Validation Report Generation

**Priority:** MUST HAVE
**Source:** Phase 4 pipeline requirements

The system SHALL generate `h-m2/04_validation.md` containing:
- Experiment metadata (hypothesis ID, type, date, gate type)
- Gate result: PASS/FAIL with SHOULD_WORK gate type
- Δmargin values for all 9 alignment-size pairs (9 values)
- Bootstrap 95% CI lower bounds for PPO (3 values)
- Gradient ordering test results (Wilcoxon p-values)
- Exploration notes if gate FAIL
- Figure paths and descriptions
- Key findings list (≥3 findings)
- Data path used (Path A or Path B)

---

## 5. Data Specification

### Primary Dataset

| Attribute | Value |
|-----------|-------|
| Name | MMLU (Massive Multitask Language Understanding) |
| Version | Full test set (cais/mmlu, HuggingFace) |
| Size | 14,042 items across 57 subjects |
| Format | 4-option multiple-choice; log-prob continuation scoring |
| Cache | `~/.cache/huggingface/datasets/cais___mmlu` |
| Download | NOT required — already cached from H-E1 |
| Preprocessing | None — lm-eval handles; log-probs accessed pre-softmax |

### Data Sources

| Source | Usage |
|--------|-------|
| `h-e1/results/` (lm-eval JSON outputs) | **Primary (Path A):** Per-item logit vectors |
| HuggingFace Hub (12 Pythia checkpoints) | **Fallback (Path B):** Re-run lm-eval if cache missing |
| `h-e1/04_validation.md` | Context: base ECE values and H-E1 ΔECE (for FR-3 scatter) |
| `~/.cache/huggingface/datasets/cais___mmlu` | **Fallback (Path B):** Cached MMLU dataset |

### Model Registry

| Role | Model ID | Size | Alignment |
|------|----------|------|-----------|
| Base | EleutherAI/pythia-1.4b | 1.4B | None |
| Base | EleutherAI/pythia-2.8b | 2.8B | None |
| Base | EleutherAI/pythia-6.9b | 6.9B | None |
| SFT | lomahony/pythia-1.4b-deduped-tldr | 1.4B | SFT |
| SFT | lomahony/pythia-2.8b-deduped-tldr | 2.8B | SFT |
| SFT | lomahony/pythia-6.9b-deduped-tldr | 6.9B | SFT |
| DPO | Leogrin/pythia-1.4b-sft-tldr-dpo | 1.4B | DPO |
| DPO | Leogrin/pythia-2.8b-sft-tldr-dpo | 2.8B | DPO |
| DPO | Leogrin/pythia-6.9b-sft-tldr-dpo | 6.9B | DPO |
| PPO | usvsnsp/pythia-1.4b-sft-tldr-ppo | 1.4B | PPO |
| PPO | usvsnsp/pythia-2.8b-sft-tldr-ppo | 2.8B | PPO |
| PPO | usvsnsp/pythia-6.9b-sft-tldr-ppo | 6.9B | PPO |

*Note: Risk R1 already activated in H-E1 — these are the validated public fallback model IDs.*

### Data Priority

1. **Path A (PREFERRED):** Load per-item log-prob vectors from `h-e1/results/` — 0 new GPU-hours
2. **Path B (FALLBACK):** Re-run lm-eval v0.4.11 with `--log_samples` for all 12 models (~2-3 hours on A100)

---

## 6. Evaluation Metrics

### Primary Metrics (Gate-Determining)

| Metric | Definition | Threshold | Gate |
|--------|-----------|-----------|------|
| Δmargin_PPO_1.4b | mean(PPO margin) − mean(base margin), 1.4B | > 0, CI lower > 0 | SHOULD_WORK |
| Δmargin_PPO_2.8b | mean(PPO margin) − mean(base margin), 2.8B | > 0, CI lower > 0 | SHOULD_WORK |
| Δmargin_PPO_6.9b | mean(PPO margin) − mean(base margin), 6.9B | > 0, CI lower > 0 | SHOULD_WORK |
| PPO sizes passing | Count of PPO sizes with Δmargin > 0 AND CI lower > 0 | ≥ 2/3 | SHOULD_WORK |

**Gate Logic:** ≥2/3 PPO sizes must satisfy BOTH Δmargin > 0 AND bootstrap 95% CI lower > 0 for PASS.

### Secondary Metrics (Informative/Ordering)

| Metric | Definition | Expected | Non-gating |
|--------|-----------|----------|-----------|
| Δmargin_DPO_{size} | DPO margin inflation per size | Positive, < PPO | ✓ |
| Δmargin_SFT_{size} | SFT margin inflation per size | Near 0 or small | ✓ |
| Gradient ordering | Wilcoxon: PPO >= DPO p-value | p < 0.1 (n=3) | ✓ |
| DPO > SFT ordering | Wilcoxon: DPO > SFT p-value | p < 0.1 (n=3) | ✓ |
| Δmargin vs ΔECE correlation | Pearson r across 9 pairs | Positive | ✓ |

### Expected Values (based on H-E1 calibration results)

| Model-Size Pair | Expected Δmargin | Basis |
|----------------|-----------------|-------|
| PPO 1.4b | +0.05 to +0.20 nats | H-E1 ΔECE_rel=0.0406 |
| PPO 2.8b | +0.04 to +0.15 nats | H-E1 ΔECE_rel=0.0423 |
| PPO 6.9b | Near 0 or negative | H-E1 ΔECE_rel=-0.0036 (exception) |
| DPO 1.4b | +0.10 to +0.35 nats | H-E1 ΔECE_rel=0.1048 (strongest) |
| SFT (all sizes) | Near 0 | Weakest alignment pressure |

---

## 7. Non-Functional Requirements

### NFR-1: Computational Efficiency
- Path A execution: < 10 minutes (log-prob loading + numpy margin computation)
- Path B execution (if needed): < 3 hours for 12 models sequentially on single GPU
- Memory: ≤ 24 GB VRAM for 6.9B model (float32); ≤ 16 GB for 1.4B/2.8B

### NFR-2: Reproducibility
- Bootstrap seed fixed (seed=42 in numpy.random.seed)
- Greedy decoding (temperature=1.0, no sampling)
- Identical lm-eval v0.4.11 configuration as H-E1 (4-shot MMLU)
- Single GPU execution only (`export CUDA_VISIBLE_DEVICES=<id>`)

### NFR-3: Code Reuse
- MUST import from `h-e1/code/calibration_analysis.py` (no reimplementation of log-prob parsing)
- MUST use lm-eval v0.4.11 for Path B (same version as H-E1)
- New code in `h-m2/code/margin_analysis.py` — extend, don't duplicate

### NFR-4: Error Handling
- Path A log-prob vectors missing → activate Path B automatically with warning log
- Shape mismatch (N_items ≠ 14042) → raise ValueError with diagnostic message
- Negative margin values (impossible by construction) → raise AssertionError
- NaN in results → raise ValueError and report affected model

### NFR-5: Output Organization
- Results: `h-m2/results/` (if Path B)
- Figures: `h-m2/figures/` (5 figures)
- Code: `h-m2/code/margin_analysis.py`
- Report: `h-m2/04_validation.md`

---

## 8. Dependencies

### 8.1 Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| numpy | ≥1.24 | Margin computation, bootstrap CI, array operations |
| scipy | ≥1.10 | Wilcoxon signed-rank test, statistical tests |
| matplotlib | ≥3.7 | Figure generation (bar, violin, scatter, heatmap, CDF) |
| seaborn | ≥0.12 | Violin and heatmap visualization |
| pyyaml | ≥6.0 | verification_state.yaml parsing |
| lm-eval | v0.4.11 | MMLU log-probability extraction (Path B only) |
| torch | ≥2.0 | Model inference (Path B) |
| transformers | ≥4.35 | Pythia model loading (Path B) |
| accelerate | ≥0.24 | Large model loading (Path B, 6.9B) |

### 8.2 External References (Non-Installable)

| Resource | Location | Purpose |
|----------|----------|---------|
| H-E1 lm-eval outputs | `h-e1/results/` | Primary: per-item log-prob vectors (Path A) |
| H-E1 Validation Report | `h-e1/04_validation.md` | ΔECE values for scatter plot (FR-7 Figure 3) |
| H-E1 Code | `h-e1/code/calibration_analysis.py` | Log-prob parsing, ECE utilities (FR-3 inheritance) |
| EleutherAI/pythia-{1.4b|2.8b|6.9b} | HuggingFace Hub | Base models (cached from H-E1, Path B fallback) |
| lomahony/Leogrin/usvsnsp variants | HuggingFace Hub | Aligned models (cached from H-E1, Path B fallback) |
| MMLU | `cais/mmlu` HuggingFace Hub | Dataset (cached from H-E1) |

### 8.3 Hardware Requirements

| Resource | Requirement |
|----------|------------|
| GPU | 1× CUDA GPU (≥24 GB VRAM for 6.9B model float32) |
| RAM | ≥32 GB system RAM |
| Storage | ≥100 GB for lm-eval outputs × 12 models (Path B) |

---

## 9. Success Criteria

### Primary (SHOULD_WORK Gate)

```
PASS condition:
  Δmargin_PPO_1.4b > 0 AND CI_lower_1.4b > 0  (size 1 pass)
  Δmargin_PPO_2.8b > 0 AND CI_lower_2.8b > 0  (size 2 pass)
  Δmargin_PPO_6.9b > 0 AND CI_lower_6.9b > 0  (size 3 pass)
  COUNT(passing_sizes) >= 2

FAIL condition: < 2 PPO sizes satisfy both conditions
FAIL consequence: EXPLORE — alignment acts post-softmax (H2 candidate);
  document for H-M3 analysis; pipeline continues to H-M3 regardless
```

### Secondary (Informative)

```
EXPECTED (but non-blocking):
  Gradient ordering: Δmargin_PPO >= Δmargin_DPO > Δmargin_SFT (sign test)
  Δmargin vs ΔECE: positive correlation across 9 model-size pairs
  DPO shows largest Δmargin (consistent with H-E1 strongest ΔECE)
```

### Deliverables

| Deliverable | Required |
|-------------|---------|
| `h-m2/04_validation.md` | ✅ MUST |
| `h-m2/figures/figure_01_delta_margin_gate.png` | ✅ MUST |
| `h-m2/figures/figure_0[2-5]_*.png` | ✅ STRONGLY RECOMMENDED |
| Gate result written to verification_state.yaml | ✅ MUST |
| Δmargin values logged for H-M3/M4 context | ✅ MUST |
| `h-m2/code/margin_analysis.py` | ✅ MUST |

---

## 10. Phase 2C → Phase 3 Completeness Check

| Phase 2C Item | Present in PRD |
|---------------|----------------|
| Dataset: MMLU cais/mmlu, 14,042 items | ✅ FR-1, §5 |
| Base models: pythia-1.4b, 2.8b, 6.9b | ✅ FR-1, §5 Model Registry |
| Aligned models: SFT/DPO/PPO × 3 sizes (9 models) | ✅ FR-1, §5 Model Registry |
| Public fallback (Risk R1): lomahony/Leogrin/usvsnsp | ✅ §5 Model Registry |
| Path A (H-E1 log-prob reuse) | ✅ FR-1, §5 Data Priority |
| Path B fallback (lm-eval re-run with --log_samples) | ✅ FR-2 |
| Margin formula: top-1 − top-2 log-prob | ✅ FR-3 compute_logit_margins() |
| Δmargin = aligned mean − base mean | ✅ FR-3 compute_delta_margin() |
| Bootstrap CI n=1000, seed=42 | ✅ FR-3 |
| SHOULD_WORK gate: Δmargin_PPO > 0, CI lower > 0, ≥2/3 sizes | ✅ FR-4, §9 |
| Gradient ordering: Wilcoxon PPO >= DPO > SFT | ✅ FR-5 |
| Mandatory figure (Δmargin bar chart + CI) | ✅ FR-7 Figure 1 |
| Additional figures (4 recommended) | ✅ FR-7 Figures 2-5 |
| Code inheritance from h-e1 calibration_analysis.py | ✅ FR-3, §7 NFR-3 |
| Mechanism activation verification | ✅ FR-6 |
| Exploration notes if gate FAIL | ✅ FR-4, FR-8 |
| Δmargin vs ΔECE scatter (mechanistic link) | ✅ FR-7 Figure 3 |

---

*Generated by Phase 3: Implementation Planning*
*Hypothesis: H-M2 | Type: MECHANISM | Tier: FULL | Base: H-M1 (prerequisite)*
