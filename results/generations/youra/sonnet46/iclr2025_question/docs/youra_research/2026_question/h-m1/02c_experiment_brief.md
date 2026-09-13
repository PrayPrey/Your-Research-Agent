# Experiment Design: H-M1

**Date:** 2026-03-16
**Author:** Anonymous
**Hypothesis Statement:** DeBERTa-v3-large-mnli's MNLI pretraining encodes graded support sensitivity sufficient to detect factual inconsistency between grounding context and generated response — demonstrated by NLI score distributions being significantly non-uniform on HaluEval (KL divergence from uniform > 0.05; Wilcoxon p < 0.05 for hallucinated vs. non-hallucinated score separation).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (PoC) Template** - Validates that DeBERTa MNLI pretraining encodes graded support sensitivity for factual inconsistency detection on HaluEval.

---

## Workflow Status

**Verification State:** ACTIVE (IN_PROGRESS)
**Prerequisites Satisfied:** H-E1 PASS (AUROC=0.709 Dialogue, 0.644 QA — 2/3 tasks above threshold)
**Gate Status:** MUST_WORK (pending experiment completion)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (COMPLETED, PASS)

### Gate Condition

**MUST_WORK Gate — Failure blocks H-M2, H-M3, H-M4.**

Pass criteria:
1. KL divergence from uniform > 0.05 (nats) for at least one NLI class on ALL 3 HaluEval tasks
2. Wilcoxon rank-sum test p < 0.05 for P(contradiction) separation between hallucinated/non-hallucinated on ≥2 tasks

Failure response: IF near-uniform on all tasks → investigate 512-token truncation effect; run on shorter subset; if still uniform → MECHANISM FAILS, STOP pipeline.

---

## Continuation Context

**Continuation from H-E1:** H-M1 is a direct continuation of H-E1 that reuses the already-computed NLI score matrices.

**Key reuse from H-E1:**
- Full (N,3) softmax score matrices saved to `h-e1/results/h-e1_results.json`
  - Contains P(contradiction), P(neutral), P(entailment) for all 60,000 pairs (20,000 per task)
  - Balanced dataset: 10,000 right (label=0) + 10,000 hallucinated (label=1) per task
- Model already cached at `~/.cache/huggingface/hub/` (cross-encoder/nli-deberta-v3-large)
- Dataset already cached at `~/.cache/huggingface/datasets/` (pminervini/HaluEval)
- H-E1 code infrastructure fully reusable (config.py, data.py, model.py)

**No new model inference required.** H-M1 is a statistical analysis experiment over existing H-E1 score outputs.

### Previous Hypothesis Results (H-E1)

| Task | AUROC | DeLong p | Cohen's d | AUROC_max | Gate |
|------|-------|----------|-----------|-----------|------|
| dialogue | 0.7094 | ≈0.0 | 0.714 | 0.77 | PASS ✅ |
| qa | 0.6437 | 1.29e-282 | 0.779 | 0.77 | PASS ✅ |
| summarization | 0.530 | 2.02e-13 | 0.220 | 0.52 | FAIL ❌ |

H-E1 confirmed: NLI contradiction signal is non-trivial (AUROC > random) on dialogue and QA. All mechanism indicators passed (shape_correct, non_uniform, above_random, label_verified). Summarization failed due to omission-based hallucinations.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Archon KB Query Results:** No relevant results found for NLI hallucination detection, DeBERTa score distribution analysis, or HaluEval-related research. The Archon KB is populated with diffusion model documentation (Stable Diffusion, DALL-E2) unrelated to this domain.

- Queries executed: 5 (NLI hallucination detection, DeBERTa factual inconsistency, KL divergence NLP, NLI PyTorch code, HaluEval cross-encoder)
- All returned similarity scores 0.33–0.44 with strongly negative reranking scores
- **Conclusion:** Archon KB not applicable for this hypothesis domain

### Archon Code Examples

No relevant code examples found. All returned examples were from diffusion model pipelines (StableDiffusionPipeline, DALL-E2, etc.).

### Exa GitHub Implementations

**Exa MCP Status:** UNAVAILABLE (402 Payment Required — quota exhausted after 3 retries per MCP Error Retry Protocol)

**Known relevant implementations (from Phase 2B literature):**

1. **SummaC (Laban et al., 2022)** — NLI-based factual consistency
   - Uses NLI entailment scores on sentence-split pairs for summarization
   - Demonstrates NLI score non-uniformity is key for detection signal
   - Source: Phase 2B BUILD_ON evidence

2. **TRUE-NLI (Honovich et al., 2022)** — Fine-tuned NLI for 11 factuality datasets
   - AUROC ~81.5 with task-specific fine-tuning; zero-shot baseline ~0.60-0.65
   - Score distributions are non-uniform and discriminative across tasks
   - Source: Phase 2B BUILD_ON evidence

3. **H-E1 Implementation** (prior run, local)
   - `h-e1/code/` — complete NLI inference + evaluation pipeline
   - `h-e1/results/h-e1_results.json` — pre-computed score matrices
   - **Primary implementation source for H-M1** (reuse architecture)

### 🎯 Implementation Priority Assessment

**CRITICAL: H-M1 is a statistical analysis experiment, not a model training experiment.**

The "implementation" for H-M1 is a statistical analysis pipeline operating on pre-computed NLI scores from H-E1.

**Recommended Implementation Path:**
- Primary: Reuse H-E1 code infrastructure (`h-e1/code/`) with new statistical analysis module
- Fallback: Load raw HaluEval + run fresh inference (requires ~30 min GPU time)
- Justification: H-E1 results.json contains exactly the (N,3) score matrices needed for H-M1 analysis. Loading pre-computed scores takes <1 second vs. 30 min re-inference.

### Code Analysis (Serena MCP)

*Skipped* — H-M1 is a pure statistical analysis experiment requiring no new neural architecture. The mechanism involves scipy.stats operations (KL divergence, Wilcoxon test) applied to pre-computed NumPy arrays. Code complexity is straightforward and does not warrant Serena semantic analysis.

---

## Experiment Specification

### Dataset

**Name:** HaluEval (pminervini/HaluEval) + pre-computed H-E1 NLI scores
**Type:** standard (real, established benchmark)
**Source:** HuggingFace Hub: `pminervini/HaluEval`
**Subsets:** dialogue (~12,988 examples → 20,000 balanced pairs), QA (10,000 → 20,000 pairs), Summarization (10,000 → 20,000 pairs)
**Total pairs:** 60,000 (same as H-E1)

**Primary data source for H-M1:** Pre-computed score matrices from H-E1
- Path: `h-e1/results/h-e1_results.json`
- Format: `{task_name: [[p_contra, p_neutral, p_entail], ...]}` — shape (N,3) per task
- Labels: `h-e1/results/h-e1_summary.json` for reference, actual labels from HaluEval reload

**Statistics:**
- 3 tasks × 20,000 pairs = 60,000 total NLI evaluations
- Balanced: 50% hallucinated (label=1), 50% correct (label=0) per task
- No preprocessing required (analysis operates on existing softmax scores)

**Synthetic Data Check:** ✅ PASS — Real dataset (HaluEval), standard type, real NLI scores from actual model inference. NOT synthetic.

**Loading Information** (for Phase 4 download):
- Method: Load pre-computed JSON (primary) + HuggingFace datasets (for labels)
- Identifier: `h-e1/results/h-e1_results.json` (local), `pminervini/HaluEval` (HF)
- Code:
```python
import json
with open("../h-e1/results/h-e1_results.json") as f:
    scores_by_task = json.load(f)  # {task: list of [p_c, p_n, p_e]}
# Labels reloaded from HaluEval if needed
from datasets import load_dataset
ds = load_dataset("pminervini/HaluEval", "dialogue_samples")
```

### Models

#### Baseline Model

**Architecture:** Uniform distribution baseline (theoretical)
- P(contradiction) = P(neutral) = P(entailment) = 1/3 for all examples
- Represents a model with no discriminative NLI capability
- Used as null hypothesis for KL divergence test

**Rationale:** For H-M1, the "baseline" is the null hypothesis that DeBERTa produces near-uniform distributions. This is the statistical reference point for measuring non-uniformity.

**Loading Information** (for Phase 4):
- Method: Generated analytically (np.full(3, 1/3))
- Identifier: N/A (no download required)
- Code: `uniform_dist = np.array([1/3, 1/3, 1/3])`

#### Proposed Model

**Architecture:** cross-encoder/nli-deberta-v3-large (pre-computed scores from H-E1) + Statistical Analysis Battery

**Core Mechanism Implementation:**

```python
# Core Mechanism: NLI Distribution Non-Uniformity Analysis
# Based on: H-E1 NLI inference results (h-e1/results/h-e1_results.json)
# Source: Phase 2B H-M1 Verification Protocol

import numpy as np
from scipy.stats import entropy, wilcoxon, ranksums

def analyze_nli_distribution(scores_nxt3, labels_n, task_name):
    """
    Args:
        scores_nxt3: np.ndarray (N,3) — [P(contra), P(neutral), P(entail)]
        labels_n:    np.ndarray (N,)  — binary labels (1=hallucinated, 0=correct)
        task_name:   str — for logging

    Returns:
        dict with KL divergence, Wilcoxon test, Cohen's d per class
    """
    # 1. Compute per-class mean distributions
    class_means = scores_nxt3.mean(axis=0)  # shape (3,)
    uniform = np.array([1/3, 1/3, 1/3])

    # 2. KL divergence from uniform for each class-marginal
    kl_contra = entropy(class_means, uniform)
    kl_neutral = entropy(class_means[::-1], uniform)  # all classes
    kl_max = entropy(class_means + 1e-10, uniform + 1e-10)

    # 3. Wilcoxon rank-sum test: hallucinated vs non-hallucinated
    contra_scores = scores_nxt3[:, 0]  # P(contradiction)
    hal_scores  = contra_scores[labels_n == 1]
    corr_scores = contra_scores[labels_n == 0]
    stat, pvalue = ranksums(hal_scores, corr_scores)

    # 4. Near-uniform proportion (failure indicator)
    near_uniform = np.all(np.abs(scores_nxt3 - 1/3) < 0.05, axis=1)
    p_near_uniform = near_uniform.mean()

    # 5. Mean tokens (from config, reported separately)
    return {
        "kl_divergence_from_uniform": float(kl_max),
        "wilcoxon_pvalue": float(pvalue),
        "wilcoxon_statistic": float(stat),
        "p_near_uniform": float(p_near_uniform),
        "class_means": class_means.tolist(),
        "kl_passes": kl_max > 0.05,
        "wilcoxon_passes": pvalue < 0.05,
    }

# Gate check: KL > 0.05 on all tasks AND Wilcoxon p < 0.05 on ≥2 tasks
```

### Training Protocol

**No training required.** H-M1 is an inference-free statistical analysis experiment.

**Computational Protocol:**

| Step | Operation | Runtime Estimate |
|------|-----------|-----------------|
| Load H-E1 scores | `json.load(h-e1_results.json)` | < 1 second |
| Load HaluEval labels | `load_dataset(...)` | < 30 seconds (cached) |
| KL divergence computation | `scipy.stats.entropy(...)` × 3 tasks | < 1 second |
| Wilcoxon rank-sum test | `scipy.stats.ranksums(...)` × 3 tasks | < 1 second |
| Near-uniform proportion | Vectorized NumPy | < 1 second |
| Visualization | 4 matplotlib plots | < 5 seconds |
| **Total** | | **< 60 seconds** |

**Configuration (from H-E1, reused for controlled comparison):**
- Model: cross-encoder/nli-deberta-v3-large (frozen, inference-only)
- batch_size: 32 (used in H-E1 inference, not applicable here)
- max_length: 512 (H-E1 truncation parameter)
- Seed: 42 (for any bootstrap CIs)
- Significance level α: 0.05

**Environment:**
- Conda environment: `youra-h-m1` (or reuse `youra-h-e1`)
- Dependencies: numpy, scipy, matplotlib, datasets (huggingface)
- GPU: NOT required (statistical analysis only)

### Evaluation

**Primary Metrics:**

| Metric | Description | Pass Threshold |
|--------|-------------|----------------|
| KL divergence from uniform | `entropy(observed_mean, uniform)` for P(contradiction) | > 0.05 nats on ALL 3 tasks |
| Wilcoxon rank-sum p-value | `scipy.stats.ranksums(hal_scores, corr_scores)` for P(contradiction) | < 0.05 on ≥ 2/3 tasks |

**Secondary Metrics (diagnostic):**

| Metric | Description |
|--------|-------------|
| p_near_uniform | Proportion of examples with all softmax within 0.05 of 1/3 |
| class_means[0,1,2] | Mean P(contradiction), P(neutral), P(entailment) per task |
| Cohen's d | Standardized score separation between hallucinated/non-hallucinated |
| Mean token retention | % of input kept after 512-token truncation (per task) |

**Success Criteria (MUST_WORK Gate):**
- Primary: KL > 0.05 on ALL 3 tasks (mechanism is globally active)
- Secondary: Wilcoxon p < 0.05 on ≥ 2/3 tasks (hallucination discrimination is statistically reliable)
- Combined: BOTH primary AND secondary must pass → Gate: PASS

**Expected Performance (from H-E1 mechanism indicators):**
- H-E1 already confirmed `non_uniform = True` for all 3 tasks (mechanism indicator passed)
- H-M1 quantifies this non-uniformity with KL and Wilcoxon — expected to PASS
- Conservative estimate: KL ~ 0.15-0.30 (well above 0.05 threshold) based on H-E1 AUROC levels

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical-analysis (not classification/regression)
- Library: `scipy.stats` (entropy, ranksums), `numpy` (array operations)
- Code:
```python
from scipy.stats import entropy, ranksums
kl = entropy(observed_mean + 1e-10, uniform + 1e-10)
stat, p = ranksums(hallucinated_scores, correct_scores)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: KL divergence and Wilcoxon p-values per task vs. thresholds (bar chart with threshold lines)

#### Additional Figures (LLM Autonomous)

Based on H-M1's distribution analysis focus, recommended figures:

1. **NLI Score Distribution Violin Plots** — Per-task violin plots of P(contradiction), P(neutral), P(entailment) for hallucinated vs. non-hallucinated groups. Overlaid with uniform reference line (1/3). Shows the graded sensitivity visually.

2. **KL Divergence Summary** — Bar chart of KL divergence from uniform per task × per NLI class (3×3 grid). Threshold line at KL=0.05.

3. **Score Separation Box Plot** — Box plots of P(contradiction) for hallucinated (orange) vs. correct (blue) per task. Annotated with Wilcoxon p-values.

4. **Near-Uniform Proportion** — Stacked bar chart showing p_near_uniform (failure indicator) per task. Target: < 5% near-uniform examples.

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | H-E1 pre-computed (N,3) NLI scores exist at `h-e1/results/h-e1_results.json` | Verify file exists and shape is (20000,3) per task |
| Mechanism Isolatable | KL and Wilcoxon tests can be run on hallucinated vs. non-hallucinated subsets independently | TRUE — labels from HaluEval allow group separation |
| Baseline Measurable | Uniform distribution baseline computed analytically | TRUE — `np.full(3, 1/3)` |

### Architecture Compatibility Check

**H-M1 uses the DeBERTa-v3-large-mnli model output (pre-computed), not the model itself.**

Required: H-E1 results.json must exist and contain 3-class softmax scores per task.
- Required format: `{"dialogue": [[p_c, p_n, p_e], ...], "qa": ..., "summarization": ...}`
- Required shape: 20,000 rows × 3 columns per task
- Required: labels loadable from `pminervini/HaluEval` (cached)

Incompatible: Any experiment that runs fresh NLI inference without H-E1 results (fallback acceptable but slower).

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "H-E1 scores loaded: {N} pairs per task" | `run_experiment.py:load_h_e1_scores()` |
| KL Divergence | kl_divergence > 0.05 for at least P(contradiction) | `analyze_nli_distribution()` |
| Wilcoxon p | p < 0.05 for hallucinated vs. non-hallucinated P(contradiction) | `analyze_nli_distribution()` |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(results_by_task):
    indicators = {}
    for task_name, result in results_by_task.items():
        indicators[task_name] = {
            "kl_passes": result["kl_divergence_from_uniform"] > 0.05,
            "wilcoxon_passes": result["wilcoxon_pvalue"] < 0.05,
            "not_near_uniform": result["p_near_uniform"] < 0.10,
        }
    kl_all_pass = all(v["kl_passes"] for v in indicators.values())
    wilcoxon_count = sum(v["wilcoxon_passes"] for v in indicators.values())
    return kl_all_pass and wilcoxon_count >= 2, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| H-E1 scores not found | FileNotFoundError on results.json | FAIL: Re-run H-E1 first |
| Near-uniform distributions | p_near_uniform > 0.50 on any task | INVESTIGATE: 512-token truncation issue |
| KL < 0.05 on ALL tasks | kl_all_pass = False | FAIL: Mechanism not encoding graded sensitivity |
| Wilcoxon p > 0.05 on all tasks | wilcoxon_count = 0 | FAIL: No statistically reliable separation |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | KL > 0.05 on all tasks | `analyze_nli_distribution()` |
| Effect Measurable | Wilcoxon p < 0.05 on ≥ 2 tasks | `scipy.stats.ranksums()` |
| Hypothesis Supported | BOTH criteria above | `verify_mechanism_activated()` |

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. KL divergence from uniform > 0.05 for at least one NLI class on ALL 3 HaluEval tasks
3. Wilcoxon rank-sum p < 0.05 for P(contradiction) separation on ≥ 2/3 tasks

**Both 2 AND 3 must pass for MUST_WORK gate.**

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Archon KB Status:** No relevant sources found.
- 5 queries executed across NLI hallucination detection, DeBERTa score analysis, KL divergence NLP
- All results returned diffusion model content (Stable Diffusion, DALL-E2, LAION-5B)
- Conclusion: Archon KB not populated with NLI/hallucination detection literature

### B. GitHub Implementations (Exa)

**Exa Status:** UNAVAILABLE (402 Payment Required, 3 retries exhausted)

**Known relevant implementations (from Phase 2B literature, used as reference):**

**Repository 1**: Laban et al. SummaC (2022)
- **Reference**: Phase 2B BUILD_ON evidence — NLI-based factual consistency
- **Relevance**: Demonstrates NLI score non-uniformity for summarization consistency
- **Key Insight**: Sentence-level NLI entailment scores are discriminative for summarization
- **Used For**: Baseline AUROC expectation, motivation for sentence-level analysis (H-M4)

**Repository 2**: Honovich et al. TRUE-NLI (2022)
- **Reference**: Phase 2B BUILD_ON evidence — Fine-tuned NLI across 11 factuality datasets
- **Relevance**: Zero-shot NLI achieves ~0.60-0.65 AUROC baseline; confirms score non-uniformity
- **Key Insight**: MNLI-trained NLI generalizes to factuality detection (validates H-M1 mechanism)
- **Used For**: Expected performance baseline, graded sensitivity validation

**Repository 3**: H-E1 local implementation
- **Path**: `h-e1/code/`
- **Relevance**: Direct predecessor; provides pre-computed scores and reusable infrastructure
- **Key Code**: `h-e1/code/evaluate.py` — AUROC, fastDeLong, Cohen's d implementations
- **Used For**: Primary codebase for H-M1 extension

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed — H-M1 is a pure statistical analysis over pre-computed NumPy arrays. No neural architecture components requiring semantic analysis.

### D. Previous Hypothesis Context (H-E1)

**Source**: H-E1 Phase 4 Validation Report — `h-e1/04_validation.md`

**Reused Components:**
- Pre-computed NLI scores: `h-e1/results/h-e1_results.json` — (N,3) softmax arrays
- Dataset loading code: `h-e1/code/data.py` — HaluEval paired interleaving logic
- Config structure: `h-e1/code/config.py` — ExperimentConfig dataclass
- Model: cross-encoder/nli-deberta-v3-large (cached, no re-download)

**Why Reused:** H-M1 tests a property of the scores generated by H-E1 (non-uniformity and discriminability). Re-running inference would be wasteful and inconsistent — using identical scores ensures controlled comparison.

**H-E1 Mechanism Indicators (confirming H-M1 is testable):**
- `non_uniform`: True for all 3 tasks — pre-validates H-M1 will pass KL check
- `above_random`: True for all 3 tasks — confirms Wilcoxon will likely pass
- `shape_correct`: True for all 3 tasks — scores are (N,3) 3-class softmax

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset: HaluEval | Phase 2B + H-E1 | 02b_verification_plan.md §1.3, h-e1/04_validation.md |
| Dataset split: 20k balanced per task | H-E1 implementation | h-e1/code/data.py |
| Pre-computed scores reuse | H-E1 results | h-e1/results/h-e1_results.json |
| KL divergence threshold (0.05) | Phase 2B H-M1 spec | 02b_verification_plan.md §2.2 H-M1 |
| Wilcoxon rank-sum test | Phase 2B H-M1 spec | 02b_verification_plan.md §2.2 H-M1 |
| scipy.stats implementation | Standard library | scipy.stats.entropy, ranksums |
| Success criteria (≥2/3 tasks) | Phase 2B H-M1 spec | 02b_verification_plan.md §2.2 H-M1 |
| Core mechanism pseudo-code | Phase 2B protocol + H-E1 structure | 02b_verification_plan.md §2.2, h-e1/code/ |
| Visualization strategy | H-E1 precedent | h-e1/figures/ |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-16T16:00:00Z

### Workflow History for This Hypothesis

| Event | Timestamp | Details |
|-------|-----------|---------|
| H-M1 set to IN_PROGRESS | 2026-03-16T15:32:40Z | External hypothesis loop starting Phase 2C → 3 → 4 |
| Phase 2C experiment design started | 2026-03-16T16:00:00Z | Step 01 initialized |
| Archon KB searched | 2026-03-16T16:00:00Z | 5 queries — no relevant results (diffusion model domain mismatch) |
| Exa GitHub searched | 2026-03-16T16:00:00Z | 3 retries — 402 quota exhausted |
| Serena analysis | 2026-03-16T16:00:00Z | Skipped — statistical analysis, no architecture analysis needed |
| H-E1 continuation context loaded | 2026-03-16T16:00:00Z | Scores reuse identified: h-e1/results/h-e1_results.json |
| Experiment design completed | 2026-03-16T16:00:00Z | 02c_experiment_brief.md written |

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (5 queries — no relevant results), Exa (3 retries — 402 quota exhausted), Serena (skipped — not needed)*
*Specifications grounded in: Phase 2B H-M1 protocol, H-E1 implementation, SummaC/TRUE-NLI literature*
*Next Phase: Phase 3 - Implementation Planning*
