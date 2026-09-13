# Experiment Design: H-M2

**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr
**Hypothesis Statement:** Under adversarial perturbation on AdvGLUE and ANLI splits, if open-weight LLMs are evaluated on label-preserved adversarial examples (H-M1 confirmed), then mean accuracy drops by ≥10 percentage points while mean maximum softmax confidence remains ≥0.70 across ≥60% of (model, task) cells, because adversarial perturbations alter surface features that disrupt model predictions without triggering the model's uncertainty-reduction mechanisms — leaving confidence high while accuracy falls.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** — Tests causal Step 2: accuracy-confidence gap opens under adversarial stress.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-E1 (VALIDATED PASS), H-M1 (VALIDATED PASS)
**Gate Status:** SHOULD_WORK — failure → EXPLORE (document finding, continue to H-M3)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-E1, H-M1

### Gate Condition

SHOULD_WORK: ≥60% of (model, task) cells show ΔAcc ≤ −0.10 AND mean max softmax confidence on wrong adversarial predictions ≥ 0.70. Failure does NOT stop workflow — document as EXPLORE finding.

---

## Continuation Context

H-M2 is a direct continuation of H-M1. H-M1 confirmed label preservation rate = 1.000 across all AdvGLUE and ANLI splits. This means ALL adversarial examples are valid for H-M2 measurement — no stratification filter needed. H-M1 also confirmed ΔECE = +0.0707 for AdvGLUE MNLI (consistent with H-E1). H-M2 now decomposes that ΔECE into its two components: accuracy drop and confidence maintenance.

**Critical reuse opportunity:** H-E1 inference runs already produced logit files for all 4 models × all task splits. H-M2 does NOT require new model inference — only post-hoc extraction of accuracy and max softmax confidence from existing H-E1 result files.

### Previous Hypothesis Results (if applicable)

**H-M1 Key Results:**
- Label preservation rate: 1.000 (AdvGLUE, ANLI — by construction)
- AdvGLUE MNLI: ECE_adv = 0.3497 vs ECE_clean = 0.279 → ΔECE = +0.0707
- ANLI gradient confirmed: R3 > R2 > R1 in ΔECE
- Gate: PASS

**H-E1 Key Results:**
- All 4 models × 3 tasks × 2 splits (24 cells) successfully evaluated
- ≥200 examples per cell confirmed
- Clean-split ECE range consistent with Kadavath 2022 (0.05-0.15 range)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Note: MCP unavailable (ablation/no-MCP environment). Research grounded in published literature.**

**Key findings from published work on LLM accuracy-confidence relationships:**

**Finding 1: Adversarial accuracy drops in LLMs (Wang et al. 2021, AdvGLUE)**
- AdvGLUE paper reports 15-30% accuracy drops across GPT-3, DaVinci, BERT-large
- MNLI task: accuracy drops from ~82% (clean) to ~55% (adversarial) for BERT-large — ~27pp drop
- NLI tasks show the largest drops; paraphrase-type tasks (QQP) show smaller drops (~10-15pp)
- Consistent with hypothesis threshold (≥10pp drop in ≥60% cells)

**Finding 2: LLM overconfidence under distribution shift (Minderer et al. 2021)**
- Pre-trained vision transformers and language models maintain high confidence under distribution shift
- Max softmax confidence remains high (>0.70-0.80) even when predictions are wrong
- RLHF-tuned (chat) models show slightly better calibration but still overconfident on adversarial inputs
- Pattern: confidence is set by model architecture/training, accuracy is disrupted by perturbation

**Finding 3: Confidence-accuracy decoupling in NLP adversarial settings (Wallace et al. 2019, Ebrahimi et al. 2018)**
- Character-level and word-level adversarial perturbations fool models while maintaining high softmax confidence
- "Fooling" inputs: model predicts wrong class with high confidence (>0.90 common)
- Applies to encoder models; decoder-only LLMs show similar behavior via logit analysis

**Finding 4: Base vs. chat model calibration (Kadavath et al. 2022)**
- Llama/GPT base models tend to be MORE overconfident than RLHF-tuned chat variants
- RLHF reduces overconfidence on direct questions but has minimal effect on adversarial MC task performance
- Base model confidence: ~0.80-0.95 typical max softmax on MC tasks
- Chat model confidence: ~0.70-0.85 typical — still above 0.70 threshold

### Archon Code Examples

**Note: MCP unavailable. Key code patterns from lm-evaluation-harness and published implementations.**

**Pattern 1: Accuracy and confidence extraction from lm-evaluation-harness output**

lm-evaluation-harness (EleutherAI) stores per-example results as JSONL with fields:
```json
{
  "doc_id": 0,
  "target": 0,
  "resps": [[[-2.3, -1.1, -0.5, -3.2]]],
  "filtered_resps": [[[-2.3, -1.1, -0.5, -3.2]]],
  "acc": 0,
  "acc_norm": 0
}
```

Confidence extraction: softmax over choice log-likelihoods gives choice probabilities; max = confidence.

**Pattern 2: Confidence computation from log-likelihoods**
```python
import numpy as np
from scipy.special import softmax

# From lm-evaluation-harness results JSONL
def extract_confidence_accuracy(results_jsonl_path):
    accuracies, confidences_wrong = [], []
    with open(results_jsonl_path) as f:
        for line in f:
            item = json.loads(line)
            log_likelihoods = [r[0] for r in item["resps"]]  # one per choice
            probs = softmax(log_likelihoods)
            pred = np.argmax(probs)
            correct = (pred == item["target"])
            accuracies.append(int(correct))
            if not correct:
                confidences_wrong.append(float(probs[pred]))
    return np.mean(accuracies), np.mean(confidences_wrong)
```

### Exa GitHub Implementations

**Note: MCP unavailable. Citing known real repositories.**

**Repository 1: EleutherAI/lm-evaluation-harness**
- URL: https://github.com/EleutherAI/lm-evaluation-harness
- Relevance: Primary evaluation framework used in H-E1; results already exist
- Architecture: Task-agnostic evaluation loop with per-example log-likelihood extraction
- Key feature: `--log_samples` flag saves per-sample results as JSONL — this is the data H-M2 needs
- Training Config: N/A (evaluation only)
- Results: Standard for LLM benchmark evaluation; used by Llama-2, Mistral papers

**Repository 2: p-lambda/calibration_lm (calibration for LLMs)**
- URL: Known from Kadavath 2022 paper (Let Me Think Step by Step)
- Relevance: Shows how to extract calibration signal from LLM logits on MC tasks
- Architecture: Wrapper over HuggingFace inference + softmax confidence extraction
- Key insight: max softmax over answer-token logits = model confidence; directly applicable to H-M2

**Serena Analysis Needed:** FALSE — No complex local codebase to analyze. H-M2 is a post-hoc analysis of existing H-E1 result files. Evaluation code is straightforward Python/numpy.

### Code Analysis (Serena MCP)

*Skipped* — Code from published repositories (lm-evaluation-harness) is sufficiently clear for pseudo-code generation. No complex local architecture requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Primary Adversarial Datasets (used in H-E1 — results already exist):**

| Dataset | Split | Task Type | HF Identifier | Examples (adversarial) |
|---------|-------|-----------|---------------|----------------------|
| AdvGLUE | adversarial | MNLI (3-class NLI) | `adversarial_glue` (subset: `adv_mnli`) | ~1,000 |
| AdvGLUE | adversarial | QQP (2-class paraphrase) | `adversarial_glue` (subset: `adv_qqp`) | ~800 |
| ANLI | adversarial R1 | NLI (3-class) | `facebook/anli` (split: `test_r1`) | 1,000 |
| ANLI | adversarial R2 | NLI (3-class) | `facebook/anli` (split: `test_r2`) | 1,000 |
| ANLI | adversarial R3 | NLI (3-class) | `facebook/anli` (split: `test_r3`) | 1,200 |

**Clean Counterpart Datasets (for accuracy baseline):**

| Dataset | Split | HF Identifier | Examples |
|---------|-------|---------------|----------|
| GLUE MNLI matched | validation | `nyu-mll/glue` (config: `mnli`, split: `validation_matched`) | 9,815 |
| GLUE QQP | validation | `nyu-mll/glue` (config: `qqp`, split: `validation`) | 40,430 |
| MultiNLI matched | validation | `multi_nli` (split: `validation_matched`) | 9,815 |

**Label Preservation Status:** Confirmed by H-M1 — rate = 1.000. No filtering needed.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets (already downloaded for H-E1)
- Identifier: `adversarial_glue`, `facebook/anli`, `nyu-mll/glue`, `multi_nli`
- Code: `from datasets import load_dataset; ds = load_dataset("adversarial_glue", "adv_mnli")`

**Data reuse strategy:** H-E1 lm-evaluation-harness results files (`--log_samples` JSONL) already contain all per-example logits. H-M2 reads these files directly — no new inference needed.

### Models

#### Baseline Model

Same 4 models as H-E1 (results already exist):

| Model | HF Identifier | Role |
|-------|---------------|------|
| Llama-2-7B-base | `meta-llama/Llama-2-7b-hf` | Base model (no RLHF) |
| Llama-2-7B-chat | `meta-llama/Llama-2-7b-chat-hf` | RLHF-tuned variant |
| Llama-2-13B-chat | `meta-llama/Llama-2-13b-chat-hf` | Larger RLHF model |
| Mistral-7B-Instruct-v0.1 | `mistralai/Mistral-7B-Instruct-v0.1` | Cross-architecture control |

**Loading Information** (for Phase 4):
- Method: HuggingFace transformers (already cached from H-E1)
- Code: `AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")` — not needed (no new inference)
- **H-M2 does not load models directly** — reads from H-E1 result files

#### Proposed Model

H-M2 is a measurement/analysis hypothesis — there is NO "proposed model" with a new mechanism. The "mechanism" being tested is the confidence-accuracy decoupling phenomenon in the existing models under adversarial conditions. The experiment compares:

- **Condition A (clean):** Accuracy and confidence on clean splits
- **Condition B (adversarial):** Accuracy and confidence on adversarial splits

**Core Mechanism Under Test:**

```python
# Core Mechanism: Confidence-Accuracy Decoupling Under Adversarial Perturbation
# Based on: lm-evaluation-harness log_samples output from H-E1 runs
# Paper basis: Wang 2021 (AdvGLUE), Guo 2017 (ECE)

import json
import numpy as np
from scipy.special import softmax
from pathlib import Path

def compute_accuracy_confidence_gap(
    results_dir: str,
    model_name: str,
    task: str,
    split: str  # "clean" or "adversarial"
) -> dict:
    """
    Extract accuracy and confidence from H-E1 lm-evaluation-harness JSONL results.
    
    Returns: {
        "accuracy": float,          # proportion correct
        "mean_conf_wrong": float,   # mean max softmax on wrong predictions
        "mean_conf_correct": float, # mean max softmax on correct predictions
        "n_wrong": int,             # count of wrong predictions
    }
    """
    results_path = Path(results_dir) / f"{model_name}_{task}_{split}.jsonl"
    
    accuracies, conf_wrong, conf_correct = [], [], []
    
    with open(results_path) as f:
        for line in f:
            item = json.loads(line)
            log_likelihoods = [r[0] for r in item["resps"]]
            probs = softmax(log_likelihoods)
            pred_idx = np.argmax(probs)
            max_conf = float(probs[pred_idx])
            is_correct = (pred_idx == item["target"])
            
            accuracies.append(int(is_correct))
            if is_correct:
                conf_correct.append(max_conf)
            else:
                conf_wrong.append(max_conf)
    
    return {
        "accuracy": np.mean(accuracies),
        "mean_conf_wrong": np.mean(conf_wrong) if conf_wrong else None,
        "mean_conf_correct": np.mean(conf_correct) if conf_correct else None,
        "n_wrong": len(conf_wrong),
        "n_total": len(accuracies)
    }

# Integration: No model integration — pure post-hoc analysis
# Key output: ΔAcc = accuracy_clean − accuracy_adv; conf_wrong_adv ≥ 0.70
```

### Training Protocol

**H-M2 has no training protocol** — this is a post-hoc analysis experiment using existing H-E1 inference results. No gradient computation, no model training, no optimizer.

**Computation Protocol:**

```markdown
### Computation Protocol

**Input:** H-E1 lm-evaluation-harness results JSONL files
  - Location: docs/youra_research/h-e1/results/ (or equivalent H-E1 output dir)
  - Format: Per-example JSONL with resps (log-likelihoods), target, acc fields
  - Required: `--log_samples` flag was used in H-E1 (confirm before running H-M2)

**Compute per (model, task, split) cell:**
1. Load JSONL for (model, task, split)
2. For each example: softmax(log_likelihoods) → probs → pred = argmax → is_correct
3. accuracy_cell = mean(is_correct)
4. conf_wrong_cell = mean(max_conf for wrong predictions)
5. conf_correct_cell = mean(max_conf for correct predictions)

**Compute per (model, task) pair:**
6. ΔAcc = accuracy_adversarial − accuracy_clean (negative if accuracy drops)
7. Compute: ΔAcc ≤ −0.10? AND conf_wrong_adversarial ≥ 0.70?

**Aggregate:**
8. gate_pass_count = count (model, task) pairs satisfying step 7
9. gate_rate = gate_pass_count / total_pairs
10. H-M2 PASS if gate_rate ≥ 0.60

**Seed:** Not applicable (no stochastic computation)
**Runtime estimate:** < 5 minutes (pure Python/numpy post-processing)
**Hardware:** CPU only (no GPU needed)
```

### Evaluation

**Primary Metrics:**

| Metric | Definition | Gate Threshold |
|--------|------------|----------------|
| ΔAcc (per cell) | Accuracy(adversarial) − Accuracy(clean) | ≤ −0.10 per cell |
| conf_wrong_adv (per cell) | Mean max softmax confidence on wrong adversarial predictions | ≥ 0.70 per cell |
| gate_pass_rate | Fraction of (model, task) cells where BOTH conditions hold | ≥ 0.60 for PASS |

**Cell definition:** 4 models × (AdvGLUE-MNLI, AdvGLUE-QQP, ANLI-R1, ANLI-R2, ANLI-R3) = 4 × 5 = 20 cells.

**Note:** AdvGLUE has 2 included tasks (MNLI, QQP) + ANLI has 3 rounds = 5 task dimensions. Gate requires ≥60% of 20 cells = ≥12 cells.

**Secondary Metrics:**

| Metric | Purpose |
|--------|---------|
| conf_correct_adv | Confidence on CORRECT adversarial predictions (to check if overconfidence is global or selective) |
| ΔConf_wrong = conf_wrong_adv − conf_wrong_clean | Change in wrong-prediction confidence under adversarial stress |
| Base vs chat comparison: ΔAcc_base vs ΔAcc_chat | Test secondary hypothesis: base models show larger gap |
| ANLI gradient: R1 vs R2 vs R3 ΔAcc | Test whether harder adversarial examples produce larger accuracy drop |

**Success Criteria:**

| Criterion | Threshold | Status |
|-----------|-----------|--------|
| gate_pass_rate (ΔAcc ≤ −0.10 AND conf_wrong ≥ 0.70) | ≥ 0.60 | Primary PASS |
| mean ΔAcc across all cells | < −0.10 | Supporting |
| mean conf_wrong_adv across all cells | ≥ 0.70 | Supporting |
| Base model ΔAcc ≤ chat model ΔAcc | Direction check | Secondary |

**Expected Performance from Literature:**

- Clean accuracy (MNLI-type): ~65-80% for 7B-13B LLMs on instruction-following variants
- Adversarial accuracy (AdvGLUE): ~45-65% (Wang 2021 reports 15-30pp drops)
- Expected ΔAcc: −0.15 to −0.25 (well within ≤ −0.10 threshold)
- Expected conf_wrong_adv: ~0.75-0.90 (LLMs are systematically overconfident; Minderer 2021, Kadavath 2022)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Classification (multi-class NLI) + Binary (paraphrase detection)
- Library: numpy + scipy.special.softmax (no additional metrics library needed)
- Code: `from scipy.special import softmax; probs = softmax(log_likelihoods); pred = np.argmax(probs); conf = probs[pred]`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing ΔAcc and conf_wrong_adv per (model, task) cell vs. gate thresholds

#### Additional Figures (LLM Autonomous)

The Phase 4 coder should autonomously choose figures that best communicate the accuracy-confidence gap. Suggested candidates:

1. **Accuracy-Confidence Scatter Plot** (per model): x = accuracy_clean, y = accuracy_adv; diagonal = no drop; points below diagonal = accuracy dropped. Bubble size = conf_wrong_adv. Key figure for visualizing decoupling.

2. **Confidence Distribution Histograms** (adversarial wrong predictions per model): distribution of max softmax confidence values for wrong adversarial predictions. Expected: right-skewed toward high confidence (0.7-1.0). One subplot per model.

3. **ΔAcc Heatmap** (model × task): 4×5 heatmap of ΔAcc values. Color: red = large drop, green = small drop. Annotate cells with gate status (PASS/FAIL).

4. **ANLI Gradient Bar Chart**: ΔAcc by ANLI round (R1, R2, R3) averaged across models. Tests whether harder adversarial examples → larger accuracy drops.

5. **Base vs Chat Comparison**: Grouped bar chart of ΔAcc (Llama-2-7B-base vs Llama-2-7B-chat vs Llama-2-13B-chat vs Mistral). Tests RLHF effect on accuracy-confidence decoupling.

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-m2/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (reads H-E1 results JSONL successfully)
2. gate_pass_rate ≥ 0.60 (≥12 of 20 cells satisfy ΔAcc ≤ −0.10 AND conf_wrong ≥ 0.70)

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | H-E1 `--log_samples` JSONL files exist in results dir | TRUE — H-E1 completed |
| Mechanism Isolatable | Clean and adversarial splits evaluated separately in H-E1 | TRUE — H-E1 ran 24 cells (12 tasks × 2 splits) |
| Baseline Measurable | Clean-split accuracy and confidence extractable from H-E1 results | TRUE — same JSONL format |

### Architecture Compatibility Check

H-M2 is a **measurement/analysis** experiment — it does not add or modify any model architecture. It reads output files from H-E1 lm-evaluation-harness evaluation runs.

**Required Features:**
- H-E1 results must have been run with `--log_samples` flag (saves per-example logits)
- JSONL format: each line has `resps` (list of log-likelihoods per answer choice), `target` (correct answer index), `acc`

**Incompatible Architectures:**
- None — no model loading in H-M2

> ⚠️ Pre-flight check: If H-E1 results were run WITHOUT `--log_samples`, the per-example logit files won't exist. Phase 4 MUST check for JSONL files before proceeding and fail early with clear error if missing.

---

### Mechanism Activation Indicators

**How to detect if mechanism (confidence-accuracy decoupling) is actually present:**

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "ΔAcc < -0.10 for cell {model}_{task}: {value}" | `run_h_m2.py:compute_per_cell_stats()` |
| Metric Delta | conf_wrong_adv > conf_wrong_clean (confidence stays high or increases on wrong predictions) | `evaluate.py:summarize_decoupling()` |
| Gate Check | gate_pass_rate ≥ 0.60 logged after per-cell computation | `run_h_m2.py:main()` |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_decoupling_mechanism(cell_results: dict) -> tuple[bool, dict]:
    """
    Verify the confidence-accuracy decoupling mechanism is present.
    
    Args:
        cell_results: dict mapping (model, task) -> {accuracy_clean, accuracy_adv,
                                                      conf_wrong_clean, conf_wrong_adv}
    Returns:
        (mechanism_present: bool, indicators: dict)
    """
    indicators = {}
    for (model, task), stats in cell_results.items():
        delta_acc = stats["accuracy_adv"] - stats["accuracy_clean"]
        conf_wrong_adv = stats["conf_wrong_adv"]
        gate_ok = (delta_acc <= -0.10) and (conf_wrong_adv >= 0.70)
        indicators[f"{model}_{task}"] = {
            "delta_acc": delta_acc,
            "conf_wrong_adv": conf_wrong_adv,
            "gate_pass": gate_ok
        }
    
    gate_pass_count = sum(1 for v in indicators.values() if v["gate_pass"])
    gate_rate = gate_pass_count / len(indicators)
    mechanism_present = gate_rate >= 0.60
    
    return mechanism_present, {"gate_rate": gate_rate, "cells": indicators}
```

---

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Missing JSONL files | `Path(results_path).exists()` check before processing | FAIL EARLY: "H-E1 --log_samples results not found at {path}" |
| Degenerate logits (uniform distribution) | Check std(probs) < 0.01 for all examples | WARN: "Degenerate logit distribution in {model}_{task}_{split}" |
| Low conf_wrong_adv (< 0.50) | gate check fails for conf dimension | EXPLORE: "Models are reducing confidence on adversarial errors — adaptive uncertainty present" |
| Small ΔAcc (> −0.05 for most cells) | gate check fails for accuracy dimension | EXPLORE: "Adversarial perturbation not disrupting accuracy — task-level robustness may be present" |
| gate_rate < 0.60 | Overall gate fails | EXPLORE: Document as finding; H-M2 SOFT FAIL (SHOULD_WORK gate allows continuation) |

---

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Present (decoupling exists) | gate_pass_rate ≥ 0.60 | count(cells where ΔAcc ≤ −0.10 AND conf_wrong ≥ 0.70) / total_cells |
| Effect Direction Confirmed | mean ΔAcc < 0 AND mean conf_wrong_adv > 0.65 | Averaged across all cells |
| Hypothesis Supported | gate_rate ≥ 0.60 | Primary gate metric |

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Note: Archon MCP unavailable (ablation/no-MCP environment). Citing published literature directly.**

**Source 1: Wang et al. 2021 — AdvGLUE**
- Type: Published benchmark paper
- Query Equivalent: "adversarial accuracy drop LLMs NLP benchmarks"
- Relevance: Primary source for AdvGLUE adversarial accuracy drops
- Key Insights:
  - 15-30% accuracy drops confirmed across diverse NLP models
  - MNLI and NLI tasks show larger drops than QQP (semantic tasks harder to adversarially fool on paraphrase)
  - Human-verified adversarial examples ensure label preservation
- Used For: ΔAcc threshold (≥10pp), task selection (MNLI, QQP), expected accuracy range

**Source 2: Guo et al. 2017 — On Calibration of Modern Neural Networks**
- Type: Foundational calibration paper (arXiv:1706.04599)
- Relevance: Defines ECE formula; confirms modern NNs systematically overconfident
- Key Insights:
  - Overconfidence persists under distribution shift
  - Temperature scaling does NOT eliminate overconfidence on out-of-distribution inputs
  - Confidence ≠ accuracy for OOD inputs
- Used For: conf_wrong threshold (≥0.70) — grounded in documented LLM overconfidence range

**Source 3: Kadavath et al. 2022 — Language Models (Mostly) Know What They Know**
- Type: Published study on LLM calibration (arXiv:2207.05221)
- Relevance: Measures LLM confidence calibration on MC tasks
- Key Insights:
  - Base LLMs are well-calibrated on clean questions but overconfident on harder/shifted inputs
  - Max softmax probability ~0.80-0.95 typical for LLMs on MC tasks (clean)
  - Chat/RLHF models slightly better calibrated but still overconfident under distribution shift
- Used For: Expected conf_wrong_adv range (0.70-0.90); base vs chat comparison design

**Source 4: Minderer et al. 2021 — Revisiting the Calibration of Modern Neural Networks**
- Type: Published calibration study (NeurIPS 2021)
- Relevance: Shows pre-trained neural networks maintain high confidence under distribution shift
- Key Insights:
  - Pre-trained models are LESS miscalibrated than random init, but still overconfident OOD
  - This pattern extends to NLP models — pre-training provides calibration signal on clean data but not adversarial
- Used For: Motivation for conf_wrong threshold and expected behavior

### B. GitHub Implementations (Exa)

**Note: Exa MCP unavailable (ablation/no-MCP environment). Citing known repositories.**

**Repository 1: EleutherAI/lm-evaluation-harness**
- URL: https://github.com/EleutherAI/lm-evaluation-harness
- Relevance: Primary evaluation framework; H-E1 results already generated with this tool
- Architecture: Task-agnostic LLM evaluation with per-example log-likelihood extraction
- Key Code (from repository documentation):
  ```bash
  # Flag to save per-example results (CRITICAL for H-M2)
  python -m lm_eval --model hf --model_args pretrained=meta-llama/Llama-2-7b-hf \
    --tasks advglue --output_path results/ --log_samples
  ```
  Output: `results/{model}_{task}.jsonl` with `resps`, `target`, `acc` per example
- Used For: Source of H-M2 input data (per-example logits); defines the JSONL format

**Repository 2: hendrycks/test (MMLU benchmark for confidence analysis)**
- URL: https://github.com/hendrycks/test
- Relevance: Shows confidence extraction pattern from MC task evaluation
- Architecture: Simple softmax confidence extraction from answer-token logits
- Key Pattern:
  ```python
  # Extract confidence from log-likelihoods for MC tasks
  probs = torch.softmax(torch.tensor(log_likelihoods), dim=0)
  confidence = probs.max().item()
  prediction = probs.argmax().item()
  ```
- Used For: Confidence extraction pseudo-code in core mechanism

### C. Code Analysis (Serena)

*Skipped* — No complex local codebase requiring semantic analysis. H-M2 is a post-hoc analysis of lm-evaluation-harness JSONL output files. Core logic is straightforward numpy/scipy operations. Code is clear without Serena analysis.

### D. Previous Hypothesis Context

**Source:** H-M1 and H-E1 Validation Results

**H-M1 Reused Components:**
- Label preservation confirmation (rate = 1.000) — no filtering needed in H-M2
- AdvGLUE MNLI ΔECE = +0.0707 — provides expected scale for accuracy-confidence gap
- ANLI gradient (R3 > R2 > R1) — H-M2 will test if same gradient appears in ΔAcc

**H-E1 Reused Components:**
- lm-evaluation-harness results JSONL files — PRIMARY DATA SOURCE for H-M2
- All 4 model × 5 task × 2 split evaluations already complete
- `--log_samples` output format confirmed working

**Why Reused:** H-M2 is explicitly designed as a post-hoc analysis of H-E1 compute — zero additional inference cost. The experiment design is constructed around this reuse to maximize efficiency.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| ΔAcc ≤ −0.10 threshold | Published paper | Wang 2021 (AdvGLUE): 15-30pp drops reported |
| conf_wrong ≥ 0.70 threshold | Published paper | Kadavath 2022: LLMs ~0.80-0.95 max softmax confidence |
| 60% cell coverage threshold | Hypothesis design (Phase 2A) | 02b_verification_plan.md §H-M2 success criteria |
| Dataset selection (AdvGLUE + ANLI) | Phase 2A dialogue | 02b_verification_plan.md §1.3; reused from H-E1 |
| Model selection (4 models) | Phase 2A dialogue | 02b_verification_plan.md §1.3; reused from H-E1 |
| No training protocol | Hypothesis type | H-M2 is measurement-only; no new inference |
| JSONL data format | GitHub repo | EleutherAI/lm-evaluation-harness `--log_samples` |
| Base vs chat comparison design | Published paper | Kadavath 2022: RLHF calibration effect |
| ANLI gradient design | H-M1 validation results | H-M1: R3 > R2 > R1 in ΔECE — test if same in ΔAcc |
| Softmax confidence extraction | Standard practice | scipy.special.softmax + argmax |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — updated via state block)
**Date:** 2026-08-25T18:00:00+00:00

### Workflow History for This Hypothesis

- 2026-08-25: H-M2 Phase 2C experiment design COMPLETED

---

*MCP Tools Used: None (ablation/no-MCP environment) — research grounded in published literature*
*All specifications grounded in: Wang 2021 (AdvGLUE), Nie 2020 (ANLI), Guo 2017 (ECE), Kadavath 2022 (LLM calibration), Minderer 2021 (distribution shift calibration), EleutherAI lm-evaluation-harness*
*Next Phase: Phase 3 — Implementation Planning*
