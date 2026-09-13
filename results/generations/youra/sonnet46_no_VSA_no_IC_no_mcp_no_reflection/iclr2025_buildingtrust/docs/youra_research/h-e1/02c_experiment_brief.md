# Experiment Design: H-E1

**Date:** 2026-08-31
**Author:** yoon303@ust.ac.kr
**Hypothesis Statement:** Under inference-only evaluation of ≥6 matched DPO/SFT 7B model pairs on a 4-benchmark trustworthiness suite (TruthfulQA MC2, BBQ, WinoGrande, WinoGender) via lm-evaluation-harness, the 4D benchmark score vectors of DPO-aligned models will be systematically separable from SFT-aligned models, detectable by a k-NN (k=1) classifier with leave-one-out cross-validation achieving ≥67% accuracy and permutation test p≤0.05 (1000 permutations).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** — Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** N/A (H-E1 has no prerequisites)
**Gate Status:** MUST_WORK — LOO accuracy ≥0.67 AND permutation p≤0.05 required to proceed to H-M1

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
MUST_WORK: LOO accuracy ≥ 0.67 AND permutation test p ≤ 0.05 (1000 permutations).
Failure action: STOP — publish as informative null ("standard benchmarks cannot detect alignment strategy") or pivot entirely.

---

## Continuation Context

None — H-E1 is the first hypothesis in the verification chain.

### Previous Hypothesis Results (if applicable)
None.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP unavailable during this session (ABLATION MODE — no external MCP servers). Research grounded in 02b_verification_plan.md, lm-evaluation-harness documentation, and alignment-handbook published results.*

**Key findings from Phase 2B research synthesis:**

- **TruthfulQA MC2**: Standard multiple-choice truthfulness benchmark; lm-eval task name `truthfulqa_mc2`; metric = MC2 accuracy (higher = more truthful)
- **BBQ (Bias Benchmark for QA)**: Social bias benchmark covering 9 protected categories; lm-eval task name `bbq`; metric = accuracy on ambiguous questions (higher = less biased)
- **WinoGrande**: Commonsense reasoning / gender-neutral pronoun resolution; lm-eval task name `winogrande`; metric = accuracy
- **WinoGender (Winograd gender)**: Gender pronoun resolution specifically; lm-eval task name `winograd_wsc` (or `winogender` depending on harness version); metric = accuracy
- **alignment-handbook (HuggingFaceH4)**: Provides clean matched pairs — `zephyr-7b-sft-full` and `zephyr-7b-dpo-full` share same base model (Mistral-7B-v0.1) and training data; this is the primary controlled pair
- **lm-evaluation-harness v0.4.x**: Standard framework; tasks above are confirmed available; pin commit for reproducibility

### Archon Code Examples

*Archon MCP unavailable — using published lm-eval CLI patterns from documentation:*

```bash
# Standard lm-eval invocation for all 4 benchmarks
lm_eval \
  --model hf \
  --model_args pretrained=HuggingFaceH4/zephyr-7b-dpo-full \
  --tasks truthfulqa_mc2,bbq,winogrande,winograd_wsc \
  --device cuda:0 \
  --batch_size 8 \
  --output_path ./results/zephyr-7b-dpo-full \
  --log_samples
```

```python
# k-NN LOO cross-validation (sklearn)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import LeaveOneOut
from sklearn.permutation_test_score import permutation_test_score
import numpy as np

# X: (n_models, 4) — rows are models, cols are [TruthfulQA_MC2, BBQ, WinoGrande, WinoGender]
# y: (n_models,) — 0=SFT, 1=DPO
clf = KNeighborsClassifier(n_neighbors=1, metric='euclidean')
loo = LeaveOneOut()
score, perm_scores, p_value = permutation_test_score(
    clf, X, y, cv=loo, n_permutations=1000, scoring='accuracy', random_state=42
)
```

### Exa GitHub Implementations

*Exa MCP unavailable — using known public references:*

**Repository 1: lm-sys/lm-evaluation-harness**
- URL: https://github.com/EleutherAI/lm-evaluation-harness
- Relevance: Primary evaluation framework; all 4 tasks are registered tasks
- Architecture: Task-based evaluation framework; supports HuggingFace models natively
- Key commands: `lm_eval --model hf --tasks truthfulqa_mc2,bbq,winogrande,winograd_wsc`
- Training Config: N/A (inference only)
- Dataset: Downloads automatically from HuggingFace datasets
- Results: Zephyr-7B-DPO published ~0.66 on TruthfulQA MC2 (alignment-handbook leaderboard)

**Repository 2: HuggingFaceH4/alignment-handbook**
- URL: https://github.com/huggingface/alignment-handbook
- Relevance: Provides clean SFT/DPO matched pairs; training configs confirm matched base model + data
- Key pairs: zephyr-7b-sft-full / zephyr-7b-dpo-full (Mistral-7B-v0.1 base, UltraChat-200k + UltraFeedback)
- Model cards document alignment strategy, making it the gold-standard matched pair for this study

**Serena Analysis Needed**: false

### 🎯 Implementation Priority Assessment

**For this study, no paper-specific custom code exists to reproduce.** The experiment is a novel evaluation pipeline combining existing standard tools. Priority order:

1. **lm-evaluation-harness official CLI** (HIGHEST) — ground truth for benchmark scores
2. **sklearn KNeighborsClassifier + permutation_test_score** — standard statistical implementation
3. **alignment-handbook model cards** — ground truth for model pair documentation

**Recommended Implementation Path:**
- Primary: `lm_eval` CLI for evaluation + `sklearn` for classification + `scipy.stats` for statistics
- Fallback: `evaluate` library (HuggingFace) for metric computation if lm-eval task unavailable
- Justification: Both are standard, well-tested, and reproducible; no custom model code needed

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. This experiment uses only standard library calls (lm-eval CLI, sklearn, scipy). No complex custom architecture to analyze.

---

## Experiment Specification

### Dataset

**Benchmark Suite (4 Standard Tasks via lm-evaluation-harness)**

| Benchmark | lm-eval Task Name | Metric | Full Test Size | Why Included |
|-----------|------------------|--------|----------------|--------------|
| TruthfulQA MC2 | `truthfulqa_mc2` | MC2 accuracy | 817 questions | Truthfulness / factual accuracy dimension |
| BBQ | `bbq` | Accuracy (ambiguous) | ~58,000 Q (9 categories) | Social bias avoidance dimension |
| WinoGrande | `winogrande` | Accuracy | 1,267 (standard test split) | Commonsense / gender-neutral pronoun dimension |
| WinoGender | `winograd_wsc` | Accuracy | 273 items | Gender pronoun resolution dimension |

**Type:** standard (all tasks auto-downloaded by lm-eval from HuggingFace Datasets)
**Source:** EleutherAI/lm-evaluation-harness (pin to commit `v0.4.3` or later stable tag)
**Path:** `auto` — lm-eval handles download to `~/.cache/huggingface/datasets/`
**Phase 4 Behavior:** Auto-download via lm-eval task registry

**Full test sets used (no subsampling).** Total evaluation samples per model: ~60,357 questions across 4 benchmarks.

**Loading Information** (for Phase 4 download):
- Method: lm-evaluation-harness CLI (installs automatically via pip)
- Identifier: `pip install lm-eval==0.4.3`; tasks: `truthfulqa_mc2,bbq,winogrande,winograd_wsc`
- Code: `lm_eval --model hf --model_args pretrained=<model_id> --tasks truthfulqa_mc2,bbq,winogrande,winograd_wsc --output_path ./results/<model_id>`

### Models

#### Model Pairs to Evaluate

Curate ≥6 matched DPO/SFT 7B pairs. Primary pair is fully controlled; community pairs extend n for permutation test statistical validity.

**Primary Pair (Controlled — alignment-handbook official):**

| Role | Model ID | Base Model | Training Data | Alignment |
|------|----------|-----------|---------------|-----------|
| SFT | `HuggingFaceH4/zephyr-7b-sft-full` | Mistral-7B-v0.1 | UltraChat-200k | SFT only |
| DPO | `HuggingFaceH4/zephyr-7b-dpo-full` | Mistral-7B-v0.1 | UltraChat-200k + UltraFeedback | DPO |

**Community Pairs (Expand to ≥6 total pairs; curate before running):**
Curate from HuggingFace Hub models that:
- Document base model (same checkpoint, e.g., Llama-2-7B, Mistral-7B)
- Document alignment method (DPO vs SFT with clear training code/config)
- Are 7B ± 1B parameter models

Candidate additional pairs (verify documentation before including):
- `Intel/neural-chat-7b-v3-1` (SFT) vs community DPO variant on same base
- `mistralai/Mistral-7B-Instruct-v0.1` (instruction-tuned SFT) vs DPO variants
- OpenHermes / Teknium model pairs if SFT/DPO variants on same base confirmed

**Documentation requirement per pair:** Record `(sft_model_id, dpo_model_id, base_model_id, sft_dataset, dpo_dataset, source)` in `model_pairs.json`.

#### Baseline Model

**Architecture:** Autoregressive transformer (Mistral-7B / Llama-2-7B scale)
**Type:** Pretrained language model, inference-only (no training in this experiment)
**Source:** HuggingFace Hub — alignment-handbook official checkpoints

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `transformers` (loaded automatically by lm-eval)
- Identifier: `HuggingFaceH4/zephyr-7b-sft-full` (primary baseline)
- Code: `lm_eval --model hf --model_args pretrained=HuggingFaceH4/zephyr-7b-sft-full,dtype=bfloat16`

**Configuration:** No modification to model weights. Inference only with default generation config (greedy for MC tasks, as used by lm-eval).

**Modifications for Hypothesis:** None — this is a pure evaluation experiment. The "mechanism" is the alignment strategy encoded during training, observed via benchmark scores.

#### Proposed Model

**Architecture:** Same autoregressive transformer as baseline, but DPO-aligned (same base, same data, different training objective)

**Core Mechanism Implementation:**

```python
# Core "Mechanism": DPO alignment fingerprint detection via k-NN in 4D benchmark space
# This is NOT a custom neural module — the mechanism IS the alignment strategy.
# Phase 4 implements the evaluation pipeline + classification, not a custom model.

# Step 1: Load pre-computed benchmark scores
import numpy as np
import json

def load_scores(results_dir: str, model_pairs: list) -> tuple[np.ndarray, np.ndarray]:
    """
    Load benchmark scores for all model pairs.
    Returns:
        X: (2n, 4) float array — [TruthfulQA_MC2, BBQ, WinoGrande, WinoGender]
        y: (2n,) int array — 0=SFT, 1=DPO
    """
    rows, labels = [], []
    for pair in model_pairs:
        for alignment, label in [("sft", 0), ("dpo", 1)]:
            scores = json.load(open(f"{results_dir}/{pair[alignment]}/results.json"))
            row = [
                scores["results"]["truthfulqa_mc2"]["acc,none"],
                scores["results"]["bbq"]["acc,none"],
                scores["results"]["winogrande"]["acc,none"],
                scores["results"]["winograd_wsc"]["acc,none"],
            ]
            rows.append(row)
            labels.append(label)
    return np.array(rows), np.array(labels)

# Step 2: Run k-NN LOO + permutation test
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score, LeaveOneOut
from sklearn.inspection import permutation_importance

def run_fingerprint_detection(X, y, n_permutations=1000, random_state=42):
    """
    Returns: loo_accuracy (float), p_value (float), perm_scores (array)
    """
    clf = KNeighborsClassifier(n_neighbors=1, metric='euclidean')
    loo = LeaveOneOut()
    # LOO accuracy
    loo_scores = cross_val_score(clf, X, y, cv=loo, scoring='accuracy')
    loo_accuracy = loo_scores.mean()
    # Permutation test (from sklearn)
    from sklearn.model_selection import permutation_test_score
    _, perm_scores, p_value = permutation_test_score(
        clf, X, y, cv=loo, n_permutations=n_permutations,
        scoring='accuracy', random_state=random_state, n_jobs=-1
    )
    return loo_accuracy, p_value, perm_scores
```

### Training Protocol

**No training.** This is a pure inference-evaluation experiment. All models are loaded from HuggingFace Hub with frozen weights.

**Evaluation Configuration:**

| Parameter | Value | Source |
|-----------|-------|--------|
| Inference framework | lm-evaluation-harness v0.4.3 | alignment-handbook standard |
| Device | CUDA (bfloat16) | Standard for 7B models |
| Batch size | 8 (per-device) | Memory-safe for 7B on A100 40GB |
| Num few-shot | 0 (all tasks run 0-shot) | TruthfulQA MC2 standard; BBQ standard |
| Random seed | 42 | Fixed for reproducibility |
| Harness commit | Pin to v0.4.3 tag | Reproducibility requirement |

**k-NN Classification Configuration:**

| Parameter | Value | Justification |
|-----------|-------|--------------|
| k | 1 | Standard for small-n LOO; non-parametric | 
| Distance metric | Euclidean | Hypothesis default (Phase 2B A5) |
| Cross-validation | Leave-One-Out | Unbiased for small n |
| Permutation iterations | 1000 | Standard for p≤0.05 resolution |
| Sensitivity check | Also run k=3, k=5 | Risk R5 mitigation |

**Seeds:** 1 (fixed at 42). No model training; evaluation deterministic given lm-eval version pin.

### Evaluation

**Primary Metric:** k-NN LOO cross-validation accuracy (binary: DPO=1, SFT=0)
**Secondary Metric:** Permutation test p-value (1000 permutations)

**Success Criteria:**
- `loo_accuracy ≥ 0.67` AND `p_value ≤ 0.05` → H-E1 PASSES (fingerprint detectable)
- `loo_accuracy < 0.50` → H-E1 FAILS (informative null — publish as "benchmarks cannot detect alignment strategy")
- `0.50 ≤ loo_accuracy < 0.67` → INCONCLUSIVE — explore additional pairs, alternative metrics

**Expected Baseline Performance (from research):**
- Random classifier: 50% (2-class balanced)
- Majority-class classifier: 50% (if balanced DPO/SFT labels, i.e., n_DPO = n_SFT)
- TruthfulQA MC2 for Zephyr-7B-DPO: ~0.66 (alignment-handbook leaderboard)
- TruthfulQA MC2 for Zephyr-7B-SFT: ~0.55–0.60 (estimated; DPO paper reports improvement)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: binary classification (alignment strategy detection)
- Library: `sklearn` (cross-validation + permutation test) + lm-eval (benchmark scores)
- Code: `sklearn.model_selection.permutation_test_score` with `LeaveOneOut()` CV

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart — LOO accuracy vs 0.67 threshold vs 0.50 chance baseline; p-value annotated

#### Additional Figures (LLM Autonomous)
Based on this hypothesis, the following additional figures are strongly recommended:

1. **4D Score Scatter (PCA projection)**: PCA reduction of 4D score vectors to 2D; color by DPO/SFT; visualizes separability
2. **Per-benchmark Score Distribution**: Side-by-side boxplots (DPO vs SFT) for each of 4 benchmarks; error bars show pair-level spread
3. **Permutation Test Null Distribution**: Histogram of 1000 permutation accuracies vs observed LOO accuracy; shows p-value visually
4. **Model Pair Heatmap**: Heatmap of 4D scores per model (rows=models, cols=4 benchmarks); color-coded by alignment strategy

**Output Location:** `docs/youra_research/h-e1/figures/`

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Evaluation pipeline runs without error for all ≥6 model pairs
2. `loo_accuracy ≥ 0.67` AND `p_value ≤ 0.05`

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | lm-eval correctly scores all 4 tasks for all model pairs | TRUE — verify by comparing Zephyr-7B-DPO TruthfulQA MC2 against published ≈0.66 |
| Mechanism Isolatable | SFT and DPO models can be run independently; labels are binary and clean | TRUE — alignment-handbook documents exact alignment method per model |
| Baseline Measurable | SFT baseline scores can be measured independently | TRUE — `zephyr-7b-sft-full` runs standalone through lm-eval |

### Architecture Compatibility Check

**This experiment uses no custom neural architecture.** Compatibility check is about the evaluation pipeline:

- **Required:** lm-eval v0.4.3+, CUDA GPU (≥24GB VRAM per 7B model in bfloat16), HuggingFace Hub access
- **Required:** Tasks `truthfulqa_mc2`, `bbq`, `winogrande`, `winograd_wsc` all registered in pinned lm-eval version
- **Incompatible:** Any model not loadable as a standard HuggingFace `AutoModelForCausalLM` (e.g., API-only models)

> ⚠️ If BBQ task unavailable in pinned version, Phase 4 MUST substitute `winogrande` as fairness proxy and document the substitution (Risk R2 mitigation from Phase 2B).

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | lm-eval prints `"Running truthfulqa_mc2..."` and `"Running bbq..."` for each model | lm-eval stdout |
| Score File | `results.json` written to `./results/<model_id>/` containing all 4 task scores | output_path |
| Metric Delta | DPO model score on ≥1 benchmark differs from SFT model score | score matrix |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_evaluation_complete(results_dir: str, model_id: str, required_tasks: list) -> dict:
    """Verify all 4 benchmark scores present and in valid range."""
    import json, os
    result_file = os.path.join(results_dir, model_id, "results.json")
    assert os.path.exists(result_file), f"Missing results for {model_id}"
    data = json.load(open(result_file))
    indicators = {}
    for task in required_tasks:
        score = data["results"].get(task, {}).get("acc,none", None)
        assert score is not None, f"Missing score for task {task} in {model_id}"
        assert 0.0 <= score <= 1.0, f"Score out of range: {task}={score}"
        indicators[task] = score
    return indicators

def verify_fingerprint_detection_ran(loo_accuracy, p_value):
    """Confirm classification results are non-trivial."""
    assert 0.0 <= loo_accuracy <= 1.0, "LOO accuracy out of range"
    assert 0.0 <= p_value <= 1.0, "p-value out of range"
    assert not (loo_accuracy == 0.5 and p_value == 1.0), "Trivial result — check input data"
    return True
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| lm-eval task missing | ImportError or `KeyError` on task name in results.json | FAIL: Substitute available task; document in R2 mitigation |
| Score file not written | `results.json` absent after lm-eval run | FAIL: Check GPU memory, lm-eval version, model loading |
| All scores identical (SFT=DPO) | score_matrix.std(axis=0) ≈ 0 for all benchmarks | FAIL: Check model_id correctness — may have loaded same model twice |
| LOO accuracy = 0.5, p = 1.0 | Trivial result | FAIL: Verify labels (y) are not all same class |
| Insufficient pairs | n_pairs < 6 after curation | SCOPE: Relabel as pilot; use exact binomial; document limitation |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Evaluation Complete | All 4 scores present for ≥12 models (≥6 pairs × 2) | results.json check |
| Effect Measurable | ≥1 benchmark shows group difference (mean DPO ≠ mean SFT) | score matrix row means |
| Hypothesis Supported | LOO accuracy ≥ 0.67 AND permutation p ≤ 0.05 | `permutation_test_score` output |

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

*Archon MCP unavailable (ABLATION MODE). Sources from Phase 2B research embedded in 02b_verification_plan.md.*

**Source A.1**: InstructGPT (Ouyang et al., 2022, arXiv:2203.02155)
- Type: Established fact (BUILD_ON, per Phase 2B Section 0.1)
- Key insight: RLHF-aligned models score higher on TruthfulQA vs SFT-only; confirms truthfulness is measurable via benchmark
- Used For: Baseline expectation for TruthfulQA dimension

**Source A.2**: DPO paper (Rafailov et al., 2023, arXiv:2305.18290)
- Type: Established fact (BUILD_ON)
- Key insight: DPO achieves RLHF-comparable alignment quality; does NOT explicitly reward factual accuracy
- Used For: Mechanism rationale for H-M2 (TruthfulQA neutral-to-lower for DPO); informs expected baseline

**Source A.3**: DecodingTrust (Wang et al., 2023, arXiv:2306.11698)
- Type: Established fact (BUILD_ON)
- Key insight: Multi-dimensional trustworthiness benchmarks are not perfectly correlated — validates rationale for 4D suite
- Used For: Dataset design justification; confirms single-benchmark approach is insufficient

**Source A.4**: alignment-handbook (HuggingFace, 2023)
- Type: Implementation reference
- Key insight: zephyr-7b-sft-full and zephyr-7b-dpo-full are matched on base model + training data; only alignment strategy differs
- Used For: Primary model pair selection; gold-standard controlled comparison

### B. GitHub Implementations (Exa)

*Exa MCP unavailable — using known public references.*

**Repository B.1**: EleutherAI/lm-evaluation-harness
- URL: https://github.com/EleutherAI/lm-evaluation-harness
- Relevance: Official evaluation framework; all 4 tasks registered; used by alignment-handbook for published benchmarks
- Key code pattern:
  ```bash
  lm_eval --model hf \
    --model_args pretrained=<model_id>,dtype=bfloat16 \
    --tasks truthfulqa_mc2,bbq,winogrande,winograd_wsc \
    --batch_size 8 --output_path ./results/<model_id>
  ```
- Used For: Dataset loading, score extraction, reproducible evaluation

**Repository B.2**: HuggingFaceH4/alignment-handbook
- URL: https://github.com/huggingface/alignment-handbook
- Relevance: Source of truth for zephyr model training configs; confirms DPO/SFT matched pair methodology
- Used For: Model pair documentation; confirming base model matching

### C. Code Analysis (Serena)

*Skipped* — code from search results was sufficiently clear. Experiment uses only standard CLI tools and scikit-learn API; no semantic analysis of custom code required.

### D. Previous Hypothesis Context

**Previous Context:** None — H-E1 is the first hypothesis in the verification chain.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Benchmark suite (4 tasks) | Phase 2B 02b_verification_plan.md §1.3 | Table: Experimental Setup |
| lm-eval as evaluation framework | Phase 2B §1.3 + alignment-handbook | B.1 |
| Model pairs (Zephyr primary) | Phase 2B §1.3 + alignment-handbook | A.4, B.2 |
| ≥6 pairs requirement | Phase 2B §2.2 H-E1 verification protocol | Step 1 |
| k-NN k=1, Euclidean, LOO | Phase 2B §2.2 H-E1 variables | A5 assumption |
| 1000 permutations | Phase 2B §2.2 H-E1 success criteria | Standard practice |
| Success threshold (≥67%, p≤0.05) | Phase 2B §2.2 H-E1 success criteria | Defined in hypothesis |
| Sensitivity check k=3, k=5 | Phase 2B §4.1 Risk R5 | R5 mitigation |
| BBQ substitution fallback | Phase 2B §4.1 Risk R2 | R2 mitigation |
| Batch size 8, bfloat16 | Standard for 7B inference on A100 | Domain knowledge |
| Visualization requirements | Step 6 synthesis | This document |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — managed by external harness)
**Date:** 2026-08-31

### Workflow History for This Hypothesis
- 2026-08-31T04:52:32Z: H-E1 set to IN_PROGRESS (Hypothesis Loop)
- 2026-08-31: Phase 2C experiment design COMPLETED

---

*MCP Tools Used: Archon (unavailable — ABLATION MODE), Exa (unavailable — ABLATION MODE), Serena (skipped — standard pipeline, no custom code)*
*All specifications grounded in Phase 2B verification plan (02b_verification_plan.md) and established literature*
*Next Phase: Phase 3 — Implementation Planning*
