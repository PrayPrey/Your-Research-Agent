# Experiment Design: H-M3

**Date:** 2026-03-15
**Author:** Anonymous
**Hypothesis Statement:** The dominant alignment-induced logit perturbation mechanism is H1 (monotonic scale distortion): Spearman rank correlation between base and aligned 4-option log-prob vectors is ≥0.9 (preserving rank order), and the Brier reliability increase is concentrated in shared-argmax items (pure confidence inflation), not changed-argmax items (accuracy collapse). H2 (boundary shift) is diagnosed if ρ < 0.85; H3 (framing susceptibility) is diagnosed via TruthfulQA MC1 alignment × distractor interaction.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** — Causal Step 3: Mechanism Discrimination (H1 vs H2 vs H3)

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** h-m2 (PASS — margin inflation PPO≥DPO>SFT confirmed in ≥2/3 Pythia sizes)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM (Causal Step 3 — Mechanism Discrimination)
- **Prerequisites:** H-M2 (PASS)

### Gate Condition

**Type:** SHOULD_WORK
**Primary:** Mean Spearman ρ ≥ 0.9 for all alignment methods (H1: scale distortion consistent)
**Secondary:** Brier reliability increases in shared-argmax subset, Cohen's d ≥ 0.1 for PPO
**Failure Response:**
- IF ρ < 0.85: Document H2 (boundary restructuring) as dominant mechanism; update ATS applicability
- IF neither H1/H2: Test H3 framing as fallback; EXPLORE alternative calibration interventions

---

## Continuation Context

This is a **data-extraction continuation experiment** — no new model inference required.

**Inherits from H-M2 (PASS):**
- lm-eval v0.4.11 output files with 4-option log-prob vectors for all 9 Pythia models on MMLU
- H-E1 calibration_analysis.py with Brier decomposition (reliability + resolution)
- H-M2 margin_analysis.py with pre-softmax logit extraction
- Risk R1 active: public fallback models (lomahony/Leogrin/usvsnsp) verified for all 3 sizes

**New computations required:**
1. Per-item Spearman ρ over 4-option log-prob vectors (base vs aligned, per model pair)
2. Shared/changed-argmax partition of MMLU items
3. Brier reliability computed separately for each subset
4. TruthfulQA MC1 lm-eval run (secondary dataset — extends H-E1 run or separate pass)
5. TruthfulQA alignment × distractor interaction (H3 diagnostic)

### Previous Hypothesis Results (if applicable)

**H-E1 (MUST_WORK PASS):**
- ΔBrier reliability > 0 for PPO+DPO in ≥2/3 sizes (CI lower > 0)
- Risk R1 active: fallback models (lomahony/Leogrin/usvsnsp)
- MMLU cached at: ~/.cache/huggingface/datasets/cais___mmlu
- lm-eval outputs available at: h-e1/code/ (reusable)

**H-M1 (MUST_WORK PASS):**
- ECE_base < 0.15 for all 3 Pythia sizes (1.4b=0.0849, 2.8b=0.0597, 6.9b=0.0792)
- Base models well-calibrated → alignment-induced shifts attributable to alignment

**H-M2 (SHOULD_WORK PASS):**
- Δmargin > 0 for PPO in ≥2/3 Pythia sizes (CI lower > 0 for 1.4b + 2.8b)
- Margin inflation confirmed: PPO 1.4b=0.394, PPO 2.8b=0.253; DPO 1.4b=0.491
- 6.9b-PPO exception persists (Δmargin=-0.036, consistent with H-E1 ΔReliability)
- lm-eval output files with pre-softmax log-prob vectors available for reuse

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1:** "Spearman rank correlation logit distribution calibration" — 5 results
- Similarity range: 0.305–0.327
- Top result: consistency_models launch scripts (irrelevant)
- All results: diffusion model / distributed training content
- **Conclusion:** No relevant results — KB is diffusion-model focused, no calibration content

**Query 2:** "LLM calibration RLHF alignment mechanism discrimination" — 5 results
- Best result: hf.co/papers/2305.14314 (similarity 0.427)
- All other results: HuggingFace blog posts on quantization/diffusers
- **Conclusion:** No relevant implementation cases for Spearman ρ or Brier decomposition

### Archon Code Examples

**Query 3:** "Spearman correlation probability vector PyTorch" — No relevant results
- Results: PyTorch installation verification, distributed ops
- **Conclusion:** No calibration-related code examples in KB

**Query 4:** "Brier score decomposition reliability resolution shared argmax" — No relevant results
- Results: cuBLAS operations, diffusion pipeline comparisons
- **Conclusion:** Archon KB (source 8b1c7f40739544a6) does not contain ECE/calibration code

**Overall Archon Assessment:** No relevant findings. Implementation will rely on:
1. Prior pipeline (H-E1 calibration_analysis.py — proven working)
2. scipy.stats.spearmanr (standard Python scientific library)
3. Standard Brier decomposition from Murphy (1973) as used in H-E1

### Exa GitHub Implementations

Exa MCP unavailable (HTTP 402 — Payment Required). Consistent with H-M1/H-M2 history.

**Fallback implementation sources (from prior hypotheses):**
- H-E1 validated `calibration_analysis.py` implements Brier decomposition (reliability + resolution)
- H-M2 validated `margin_analysis.py` provides lm-eval log-prob extraction pattern
- scipy.stats.spearmanr: well-known, no external search needed
- Standard argmax-partitioning: `np.argmax(base_logprobs) == np.argmax(aligned_logprobs)`

**Serena Analysis Needed:** false — pipeline extends prior validated code, no new complex code.

### 🎯 Implementation Priority Assessment

**CRITICAL: Extending prior validated pipeline — no new external implementations needed**

H-M3 is an analysis-only extension of H-E1/H-M2:
- Primary data source: lm-eval output files from H-E1 (cached, verified)
- New computation: Spearman ρ (scipy.stats.spearmanr, 1 line), shared-argmax partition (numpy, 1 line)
- TruthfulQA: already in Phase 2A experimental setup; requires lm-eval --tasks truthfulqa_mc1 pass

**Recommended Implementation Path:**
- Primary: Extend H-E1 `calibration_analysis.py` with Spearman ρ + argmax partition functions
- Fallback: Re-run lm-eval for TruthfulQA MC1 if not already cached from H-E1 run
- Justification: Minimizes compute (0 new MMLU GPU-hours), reuses validated code, controlled comparison

### Code Analysis (Serena MCP)

*Skipped* — Code from prior hypotheses was sufficiently clear. H-M3 extends calibration_analysis.py (H-E1) and margin_analysis.py (H-M2) with standard scipy/numpy operations. No complex new code requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Primary Dataset: MMLU (Reuse from H-E1)**
- **Name:** MMLU (Massive Multitask Language Understanding)
- **Source:** cais/mmlu (HuggingFace)
- **Type:** standard (NOT synthetic — real benchmark dataset)
- **Split:** Full test set (~14,042 items, 57 subjects)
- **Format:** 4-option multiple-choice questions
- **Cache:** ~/.cache/huggingface/datasets/cais___mmlu (verified from H-E1)
- **Role:** Main dataset for Spearman ρ analysis and shared/changed-argmax Brier partitioning

**Secondary Dataset: TruthfulQA MC1**
- **Name:** TruthfulQA Multiple Choice 1 (MC1)
- **Source:** HuggingFace via lm-eval --tasks truthfulqa_mc1
- **Type:** standard (real benchmark dataset)
- **Split:** Full test set (817 questions)
- **Format:** Multiple-choice, single correct answer
- **Role:** H3 framing susceptibility diagnostic — alignment × distractor interaction test

**Continuation Note:** MMLU evaluation is reused from H-E1 (0 new GPU-hours for MMLU). TruthfulQA MC1 may require a separate lm-eval pass if not cached from H-E1 run.

**Loading Information** (for Phase 4 download):
- Method: lm-eval-harness (inference engine)
- Identifier: `--tasks mmlu` (MMLU), `--tasks truthfulqa_mc1` (TruthfulQA)
- Code:
  ```bash
  # MMLU (reuse from H-E1 if outputs cached, else re-run)
  lm_eval --model hf --model_args pretrained=<model_id> --tasks mmlu --device cuda:0 --output_path ./lm_eval_outputs/
  # TruthfulQA MC1
  lm_eval --model hf --model_args pretrained=<model_id> --tasks truthfulqa_mc1 --device cuda:0 --output_path ./lm_eval_outputs/
  ```

### Models

#### Baseline Model

**Pythia Base Models (Reuse from H-E1)**
- **Architecture:** Pythia (EleutherAI autoregressive causal LM)
- **Sizes:** 1.4B, 2.8B, 6.9B
- **Source:** EleutherAI/pythia-{1.4b|2.8b|6.9b} (HuggingFace)
- **Role in H-M3:** Provide base log-prob vectors for Spearman ρ comparison
- **Status:** Cached from H-E1 (Risk R1: using public fallback base models)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace AutoModelForCausalLM via lm-eval
- Identifier: `EleutherAI/pythia-1.4b`, `EleutherAI/pythia-2.8b`, `EleutherAI/pythia-6.9b`
- Code:
  ```python
  # lm-eval handles loading automatically
  from lm_eval.models.huggingface import HFLM
  model = HFLM(pretrained="EleutherAI/pythia-1.4b")
  ```

#### Proposed Model

**Architecture:** Same Pythia alignment ladder (SFT/DPO/PPO variants) as H-E1/H-M2

**Role in H-M3:** Provide aligned log-prob vectors for Spearman ρ comparison with base

**Aligned model sources (Risk R1 active, from H-E1):**
- PPO: lomahony/Pythia-{1.4b|2.8b|6.9b}-deduped-tldr-ppo (or equivalent)
- DPO: Leogrin/eleutherai-pythia-{size}-dpo-ultrafeedback (or equivalent)
- SFT: usvsnsp/pythia-{size}-sft (or equivalent)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Mechanism Discrimination (H1 vs H2 vs H3)
# H-M3: Spearman ρ analysis + Shared/Changed-Argmax Brier partition
# Based on: H-E1 calibration_analysis.py + scipy.stats.spearmanr
# Reference: Murphy (1973) Brier decomposition, scipy documentation

import numpy as np
from scipy import stats

def compute_spearman_rho_per_item(base_logprobs, aligned_logprobs):
    """
    Compute per-item Spearman ρ over 4-option log-prob vectors.
    Args:
        base_logprobs: (N, 4) — base model log-probs for N MMLU items
        aligned_logprobs: (N, 4) — aligned model log-probs for N MMLU items
    Returns:
        rho_per_item: (N,) — Spearman ρ for each item
        mean_rho: float — mean across all items
    """
    rho_per_item = np.array([
        stats.spearmanr(base_logprobs[i], aligned_logprobs[i]).correlation
        for i in range(len(base_logprobs))
    ])
    return rho_per_item, rho_per_item.mean()

def partition_items_by_argmax(base_logprobs, aligned_logprobs):
    """
    Partition MMLU items into shared-argmax and changed-argmax subsets.
    H1 signature: reliability increase concentrated in shared-argmax items.
    Args:
        base_logprobs: (N, 4)
        aligned_logprobs: (N, 4)
    Returns:
        shared_mask: (N,) bool — True if base and aligned agree on argmax
        changed_mask: (N,) bool — True if argmax differs
    """
    base_argmax = np.argmax(base_logprobs, axis=1)
    aligned_argmax = np.argmax(aligned_logprobs, axis=1)
    shared_mask = (base_argmax == aligned_argmax)
    changed_mask = ~shared_mask
    return shared_mask, changed_mask

def compute_brier_reliability_subset(probs, labels, mask):
    """
    Compute Brier reliability for a subset of items.
    H1: reliability increase in shared-argmax > changed-argmax (confidence inflation).
    Args:
        probs: (N, 4) softmax probabilities
        labels: (N,) int — correct answer index (0-3)
        mask: (N,) bool — subset selection mask
    Returns:
        reliability: float — Brier reliability for subset
    """
    subset_probs = probs[mask]
    subset_labels = labels[mask]
    # One-hot encode labels
    onehot = np.eye(4)[subset_labels]
    brier_per_item = np.mean((subset_probs - onehot) ** 2, axis=1)
    return brier_per_item.mean()

# H3: TruthfulQA MC1 — alignment × alternative interaction
def compute_truthfulqa_ece_by_alignment(lm_eval_outputs_truthfulqa):
    """
    Compare ECE on TruthfulQA MC1 across alignment methods.
    H3 diagnosis: alignment method × distractor (alternative answer) interaction.
    """
    # Load per-item log-probs from lm_eval output files
    # Compute ECE per alignment method
    # Test if ECE increase is larger for models with more distractors exposed
    pass  # Implemented via calibration_analysis.py adapted for TruthfulQA
```

### Training Protocol

**No training required.** H-M3 is an analysis-only experiment.

**Compute Protocol:**
- **MMLU evaluation:** Reuse lm-eval outputs from H-E1 (0 new GPU-hours)
- **TruthfulQA MC1 evaluation:** lm-eval pass for all 9 Pythia models (if not cached)
  - Estimated compute: ~30 min per model on single GPU (817 items × 9 models)
- **Analysis compute:** scipy.stats.spearmanr + numpy argmax partitioning (CPU, seconds)

**Optimizer:** N/A (inference-only)
**Learning Rate:** N/A
**Batch Size:** lm-eval default (1 for log-prob evaluation)
**Epochs:** N/A (single forward pass evaluation)
**Loss:** N/A
**Seeds:** 1 (greedy decoding, deterministic)
**Framework:** lm-eval-harness v0.4.11 (same as H-E1)

**Inherited from H-E1 (Risk R1 active):**
- Use public fallback models (lomahony/Leogrin/usvsnsp) for aligned variants
- CUDA_VISIBLE_DEVICES=<empty_gpu> (single GPU, greedy decoding, temperature=1.0)
- Bootstrap CI: n=1000 samples for reliability confidence intervals

### Evaluation

**Primary Metrics:**

1. **Mean Spearman ρ (base vs aligned log-prob vectors)**
   - Computed per MMLU item over 4-option log-prob vector
   - Aggregated as mean across all items, per model pair (9 pairs)
   - H1 threshold: mean ρ ≥ 0.9
   - H2 threshold: mean ρ < 0.85
   - Range: 9 values (3 sizes × 3 alignment methods)

2. **Brier Reliability — Shared-Argmax Subset**
   - Brier reliability computed only for items where base and aligned agree on top-1 option
   - H1 signature: reliability_shared_aligned > reliability_shared_base
   - Cohen's d effect size for PPO (target ≥ 0.1)

3. **Brier Reliability — Changed-Argmax Subset**
   - Brier reliability for items where argmax differs (accuracy collapse items)
   - H2 check: if reliability_changed increases MORE than reliability_shared → H2 dominant

4. **TruthfulQA MC1 ECE (H3 diagnostic)**
   - ECE per alignment method on TruthfulQA MC1
   - H3 test: alignment × distractor-count interaction (does ECE increase scale with number of distractors?)

**Success Criteria:**
- **Primary (SHOULD_WORK gate):** Mean Spearman ρ ≥ 0.9 for all 9 alignment-base pairs
- **Secondary:** Brier reliability increases in shared-argmax subset with Cohen's d ≥ 0.1 for PPO

**Expected Baseline Performance (from H-E1/H-M2 results):**
- Base model ECE_base: 0.06–0.085 (confirmed H-M1)
- ΔBrier reliability: PPO > DPO > SFT direction confirmed (H-E1)
- Margin inflation: PPO 1.4b=0.394, 2.8b=0.253; 6.9b-PPO exception persists
- Expected ρ: High (≥ 0.9) based on H-M2 evidence that alignment inflates logit scale without reordering (margin inflation preserves rank)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: NLP multiple-choice evaluation (analysis)
- Library: scipy.stats (spearmanr), numpy (argmax), H-E1 calibration_analysis.py (Brier decomposition)
- Code:
  ```python
  from scipy.stats import spearmanr
  import numpy as np
  # Cohen's d
  def cohens_d(group1, group2):
      n1, n2 = len(group1), len(group2)
      pooled_std = np.sqrt(((n1-1)*np.var(group1, ddof=1) + (n2-1)*np.var(group2, ddof=1)) / (n1+n2-2))
      return (np.mean(group1) - np.mean(group2)) / pooled_std
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing mean Spearman ρ per alignment method × Pythia size

#### Additional Figures (LLM Autonomous)

1. **Spearman ρ Distribution (H1/H2 Discrimination)**
   - Violin plot or histogram of per-item ρ distribution for each alignment method
   - Annotate H1 threshold (ρ ≥ 0.9) and H2 threshold (ρ < 0.85) as vertical lines
   - Shows whether rank-ordering is preserved (H1) or disrupted (H2)

2. **Brier Reliability: Shared vs Changed Argmax Subsets**
   - Grouped bar chart: reliability_base vs reliability_aligned, separated by shared/changed argmax
   - 3 subplots (one per Pythia size) × 3 alignment methods
   - Cohen's d annotations for PPO condition

3. **Subset Size and Proportion**
   - Stacked bar: % shared-argmax vs changed-argmax items per model
   - Shows how much accuracy collapse (changed-argmax) exists across alignment methods

4. **TruthfulQA MC1 ECE Comparison (H3 diagnostic)**
   - Bar chart: ECE per alignment method on TruthfulQA MC1
   - Compare MMLU ECE vs TruthfulQA ECE side-by-side (framing susceptibility signal)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m3/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `mean_rho_aligned >= 0.9` (H1 confirmed) OR mechanism type identified (H2 or H3 if H1 fails)

**Note:** Unlike EXISTENCE hypotheses, H-M3 has a non-binary outcome. Any result (H1/H2/H3 identification) is scientifically valid — the mechanism discrimination itself is the contribution.

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

No relevant results found. Archon KB source (8b1c7f40739544a6) contains diffusion model and distributed training content; no calibration/RLHF content. 4 queries executed with similarity range 0.27–0.43.

### B. GitHub Implementations (Exa)

Exa MCP unavailable (HTTP 402 — Payment Required). Consistent with H-M1, H-M2 history.

**Alternative sources (prior validated implementations):**
- H-E1 `calibration_analysis.py`: Brier decomposition (reliability + resolution), ECE computation — **proven working**
- H-M2 `margin_analysis.py`: lm-eval log-prob extraction, pre-softmax margin computation — **proven working**
- scipy.stats.spearmanr: Standard Python scientific library (no external search needed)
- numpy.argmax: Standard; argmax partition = 1 line

### C. Code Analysis (Serena)

Not performed — H-M3 extends prior validated code. No complex new architecture requiring semantic analysis. Core additions:
- `compute_spearman_rho_per_item()`: ~5 lines, scipy.stats
- `partition_items_by_argmax()`: ~5 lines, numpy
- `compute_brier_reliability_subset()`: ~10 lines, numpy (standard Brier formula)
- TruthfulQA MC1 lm-eval pass: same pattern as H-E1 MMLU run

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Reports — H-E1, H-M1, H-M2

| Component | From | Details |
|-----------|------|---------|
| MMLU lm-eval outputs | H-E1 | 12 Pythia models, ~14k items each, cached |
| Brier decomposition | H-E1 | calibration_analysis.py, 15-bin ECE, bootstrap CI |
| Fallback models | H-E1 | Risk R1: lomahony/Leogrin/usvsnsp variants |
| Pre-softmax log-prob extraction | H-M2 | margin_analysis.py, lm-eval output parsing |
| CUDA_VISIBLE_DEVICES | H-E1 | Single GPU, greedy decoding |
| Bootstrap CI (n=1000) | H-E1 | Confidence interval protocol |

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (MMLU) | Prior hypothesis (H-E1) | H-E1 validation, cais/mmlu cached |
| Dataset (TruthfulQA MC1) | Phase 2A/2B design | 02b_verification_plan.md §1.3 |
| Model selection | Prior hypothesis (H-E1) | H-E1 validation, Risk R1 fallbacks |
| Spearman ρ pseudo-code | Standard library | scipy.stats.spearmanr documentation |
| Argmax partition | Standard library | numpy.argmax |
| Brier decomposition | Prior hypothesis (H-E1) | calibration_analysis.py (proven) |
| Evaluation metrics (ECE) | Phase 2B | 02b_verification_plan.md §2.2 H-M3 |
| Success criteria | Phase 2B | 02b_verification_plan.md §2.2 H-M3 |
| Training protocol (N/A) | Phase 2B | Analysis-only, 0 training steps |
| TruthfulQA H3 diagnostic | Phase 2B | 02b_verification_plan.md §2.2 H-M3 Step 5 |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-15T03:00:00Z

### Workflow History for This Hypothesis

- 2026-03-15T02:47:00Z: H-M2 Phase 4 PASS (SHOULD_WORK gate satisfied, 2/3 PPO sizes)
- 2026-03-15T02:53:03Z: H-M3 set to IN_PROGRESS (External loop starting Phase 2C → 3 → 4)
- 2026-03-15T03:00:00Z: Phase 2C experiment design IN_PROGRESS → COMPLETED

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (4 queries — no relevant results, KB is diffusion-focused), Exa (unavailable — 402), Serena (skipped — no new code)*
*All specifications grounded in prior validated implementations (H-E1/H-M2) and standard scipy/numpy libraries*
*Next Phase: Phase 3 - Implementation Planning*
