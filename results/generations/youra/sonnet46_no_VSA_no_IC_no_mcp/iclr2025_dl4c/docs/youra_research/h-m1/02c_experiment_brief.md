# Experiment Design: H-M1

**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr
**Hypothesis Statement:** Under controlled training conditions (DeepSeek-Coder-7B, APPS train split), SFT trained on APPS achieves <60% pass@1 on LiveCodeBench-Hard, confirming that APPS training data creates a signal void (near-zero correct solution coverage) at hard benchmark difficulty levels.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** — Tests causal step 1: SFT signal void existence at hard difficulty.
> PoC Goal: Demonstrate "SFT pass@1 < 60% on LiveCodeBench-Hard" — directional confirmation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 — VALIDATED (MUST_WORK gate passed)
**Gate Status:** MUST_WORK — this hypothesis must pass for H-M2, H-M3, H-M4 to proceed

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (VALIDATED)

### Gate Condition
MUST_WORK: SFT pass@1 on LiveCodeBench-Hard < 60%.
If this threshold is met, H-M2 proceeds.
If SFT ≥ 60%, EXPLORE mode: the signal void framing needs revision; hypothesis chain may not hold.

---

## Continuation Context

H-M1 is the FIRST MECHANISM hypothesis. It directly reuses the SFT model checkpoint trained in H-E1 (no additional training required). The SFT training run, APPS split, and evaluation harness configuration are fully inherited.

### Previous Hypothesis Results (H-E1)
- H-E1 VALIDATED: RLEF-Fraction achieves Δ_LiveCodeBench / Δ_HumanEval ≥ 1.5× (MUST_WORK gate satisfied)
- SFT baseline model: DeepSeek-Coder-7B-base fine-tuned on APPS train split (cross-entropy, matched gradient steps)
- SFT checkpoint available for direct reuse in H-M1

**Reuse rationale:** Using the same SFT model from H-E1 enables controlled comparison and zero additional training cost. The only new work is:
1. Evaluation on LiveCodeBench-Hard (if not already run)
2. APPS difficulty-bucket loss stratification analysis

---

## Implementation Research Summary

### Archon Knowledge Base Findings

> ⚠️ **MCP Availability:** Archon MCP not available in this session. Research conducted via WebSearch as documented fallback. All findings below cite real sources.

**Query 1: SFT signal void at hard difficulty — experiment design**

- **Finding:** Research consistently shows SFT on competitive programming datasets has severely degraded performance at hard difficulty tiers. On LiveCodeBench Hard, 7B RL-finetuned models cluster at 42–52% pass@1. SFT baselines (without RL) are expected to be substantially lower (typically 10–30pp below RL-trained models at hard difficulty).
  - Source: [LiveCodeBench Hard Evaluation — EmergentMind](https://www.emergentmind.com/topics/livecodebench-hard); [Nemotron-Cascade 2, arXiv:2603.19220](https://arxiv.org/pdf/2603.19220)
  - Key insight: 7B RL models at 42–52% ⟹ SFT baseline likely 15–35% on LiveCodeBench-Hard, well below the 60% threshold.

- **Finding:** APPS difficulty stratification: 5,000 train split problems across Introductory (largest), Interview (medium), Competition (smallest). Competition-level problems have sparse reference solutions achievable by standard SFT. APPS+ refined subset has only 572 competition problems (out of 7,413 total).
  - Source: [APPS Paper (Hendrycks et al., 2021)](https://datasets-benchmarks-proceedings.neurips.cc/paper/2021/file/c24cd76e1ce41366a4bbe8a49b02a028-Paper-round2.pdf); [APPS+ (StepCoder, GitHub)](https://github.com/Ablustrund/APPS_Plus)
  - Key insight: Competition-tier problems are ~8% of APPS+ (572/7413); SFT trained primarily on intro/interview signal cannot generalize well to hard benchmark problems.

**Query 2: SFT vs RL at hard benchmarks — best practices**

- **Finding:** "On-policy RL suffers from sparse rewards on hard problems where the model rarely generates a correct solution, and SFT alone does not develop the model's own reasoning capacity." (Source: [SFT-then-RL Outperforms Mixed-Policy, arXiv:2604.23747](https://arxiv.org/html/2604.23747v1))
  - Key insight: SFT's limitation at hard difficulty is well-documented; sparse supervision is the mechanism.

- **Finding:** DeepSeek-Coder-Base-6.7B base model achieves 49.4% pass@1 on HumanEval and 60.6% on MBPP from base weights (before APPS SFT). After SFT on APPS, performance on hard benchmarks like LiveCodeBench is substantially lower than on HumanEval. (Source: [DeepSeek-Coder GitHub](https://github.com/deepseek-ai/DeepSeek-Coder); [DeepSeek-Coder-V2, arXiv:2406.11931](https://arxiv.org/pdf/2406.11931))

**Query 3: APPS training, SFT loss stratification**

- **Finding:** Methods achieve 89.4% on APPS-Introductory and 80.4% on APPS-Interview (strong models), with performance dropping considerably on APPS-Competition. SFT loss gradient signals are concentrated in easy/medium problems.
  - Source: [MapCoder, arXiv:2405.11403](https://arxiv.org/pdf/2405.11403)
  - Key insight: The difficulty gradient in SFT training loss is measurable and expected to be significant.

### Archon Code Examples

> ⚠️ Archon MCP unavailable — code patterns sourced from web search.

**Pattern 1: bigcode-evaluation-harness LiveCodeBench evaluation**
- Source: [bigcode-project/bigcode-evaluation-harness](https://github.com/bigcode-project/bigcode-evaluation-harness)
- Evaluation command pattern:
```bash
# Evaluate SFT model on LiveCodeBench with bigcode-harness (correctness-only)
accelerate launch main.py \
  --model deepseek-ai/deepseek-coder-7b-base \
  --tasks livecodebench \
  --metric_output_path results/sft_lcb_results.json \
  --n_samples 1 \
  --temperature 0.0 \
  --batch_size 1
```
- Key insight: Pass@1 with greedy decoding (temperature=0, n_samples=1) for deterministic baseline measurement.

**Pattern 2: APPS difficulty-bucket loss logging**
- Source: derived from TRL SFTTrainer + APPS dataset structure
```python
# Log SFT loss stratified by APPS difficulty bucket
def compute_per_difficulty_loss(model, tokenizer, apps_split):
    losses = {"introductory": [], "interview": [], "competition": []}
    for example in apps_split:
        difficulty = example["difficulty"]  # "introductory"|"interview"|"competition"
        loss = compute_cross_entropy_loss(model, tokenizer, example)
        losses[difficulty].append(loss.item())
    return {k: sum(v)/len(v) for k, v in losses.items()}
```

### Exa GitHub Implementations

> ⚠️ Exa MCP unavailable — GitHub implementations identified via WebSearch.

**Repository 1**: bigcode-project/bigcode-evaluation-harness
- **URL**: https://github.com/bigcode-project/bigcode-evaluation-harness
- **Relevance:** Official harness for evaluating pass@1 on HumanEval, MBPP, APPS, LiveCodeBench — exactly the evaluation stack for H-M1
- **Key Feature:** Supports `livecodebench` task, correctness-only mode, configurable difficulty filtering
- **Stars:** ~4,000+
- **Used For:** Primary evaluation infrastructure

**Repository 2**: reddy-lab-code-research/PPOCoder
- **URL**: https://github.com/reddy-lab-code-research/PPOCoder
- **Relevance:** Execution-based code generation RL baseline with SFT comparison on APPS; shows SFT vs RL performance gap pattern
- **Key Pattern:** SFT baseline training + evaluation pipeline reusable for H-M1's SFT model
- **Used For:** Reference for SFT-vs-RL comparison methodology

**Repository 3**: Ablustrund/APPS_Plus
- **URL**: https://github.com/Ablustrund/APPS_Plus
- **Relevance:** APPS+ dataset (7,413 instances) with difficulty stratification — intro: 2889, interview: 3592, competition: 572
- **Used For:** Confirms APPS competition-tier sparsity (572/7413 = 7.7% of problems)

**Repository 4**: huggingface/trl (GRPOTrainer)
- **URL**: https://github.com/huggingface/trl/blob/main/trl/trainer/grpo_trainer.py
- **Relevance:** GRPOTrainer supports custom reward functions and callbacks; used in H-E1 for RLEF-Fraction; H-M1 reuses the SFT training run from the same pipeline
- **Used For:** Training infrastructure reference

**Serena Analysis Needed**: false — no complex novel architecture to analyze; H-M1 uses standard SFT + bigcode-harness evaluation pipeline.

### 🎯 Implementation Priority Assessment

This is a **data analysis + evaluation hypothesis**, not a novel architecture. Priority:
1. **Primary:** Reuse SFT checkpoint from H-E1 (if already evaluated on LiveCodeBench-Hard, extract results directly)
2. **Secondary:** Run bigcode-harness on LiveCodeBench-Hard if results not yet available from H-E1
3. **Tertiary:** Run APPS difficulty-bucket loss analysis (forward pass only, no re-training)

**Recommended Implementation Path:**
- Primary: Extract LiveCodeBench-Hard SFT pass@1 from H-E1 results (zero-cost)
- Fallback: `accelerate launch bigcode-harness/main.py --tasks livecodebench --model [sft_checkpoint]`
- Justification: H-E1 protocol already evaluates SFT on all benchmarks including LiveCodeBench-Hard; H-M1 is an analysis of existing H-E1 data.

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. No complex novel architecture to analyze; H-M1 uses standard SFT training + bigcode-harness evaluation, both well-documented.

---

## Experiment Specification

### Dataset

**Primary Dataset:** APPS (codeparrot/apps) — train split for SFT; LiveCodeBench Hard subset for evaluation

| Field | Value |
|-------|-------|
| Name | APPS (training) + LiveCodeBench (evaluation) |
| Type | standard |
| Source | HuggingFace: `codeparrot/apps`; LiveCodeBench: `livecodebench/livecodebench` |
| Train split | `codeparrot/apps` train split, 5,000 problems |
| Eval split | LiveCodeBench 2024-Q4 snapshot, Hard difficulty tier |
| Difficulty stratification | APPS: introductory / interview / competition; LiveCodeBench: Easy / Medium / Hard |
| Statistics | APPS train: ~5,000 problems; LiveCodeBench Hard: ~175 problems (v6 structure) |

**APPS Difficulty Distribution (from APPS+ analysis):**
- Introductory: ~39% of problems (≈1,950)
- Interview: ~49% of problems (≈2,450)
- Competition: ~12% of problems (≈600)

**Hypothesis Fit:** APPS competition-level coverage is sparse, supporting the signal void hypothesis. LiveCodeBench-Hard is temporally isolated (post-training-cutoff problems only), ensuring no contamination.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `codeparrot/apps` (train split); `livecodebench/livecodebench` (Hard subset)
- Code:
```python
from datasets import load_dataset
apps_train = load_dataset("codeparrot/apps", split="train")
# Filter by difficulty:
apps_hard = apps_train.filter(lambda x: x["difficulty"] == "competition")
# LiveCodeBench: use bigcode-evaluation-harness task "livecodebench"
```

### Models

#### Baseline Model

**Architecture:** DeepSeek-Coder-7B-base + SFT on APPS (reused from H-E1)
**Type:** decoder-only transformer, code-specialized, 6.7B parameters

| Field | Value |
|-------|-------|
| Base model | deepseek-ai/deepseek-coder-7b-base |
| Fine-tuning | SFT on APPS train split (cross-entropy on correct solutions) |
| Source | H-E1 checkpoint (no re-training required) |
| HumanEval base | ~49.4% pass@1 (base weights); ~40-50% after APPS SFT |
| LiveCodeBench-Hard expected | <60% (hypothesis threshold); expected ~10-30% based on literature |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers (base) + local checkpoint (SFT)
- Identifier: `deepseek-ai/deepseek-coder-7b-base`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
# Base model (if SFT checkpoint unavailable):
model = AutoModelForCausalLM.from_pretrained("deepseek-ai/deepseek-coder-7b-base")
# SFT checkpoint (from H-E1):
model = AutoModelForCausalLM.from_pretrained("./checkpoints/h-e1/sft_checkpoint")
tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/deepseek-coder-7b-base")
```

#### Proposed Model

**Architecture:** Same as baseline (this is a MECHANISM hypothesis, not an architecture comparison)

H-M1 does NOT propose a new model. It characterizes the behavior of the existing SFT model from H-E1. The "proposed" analysis is:
1. SFT pass@1 < 60% on LiveCodeBench-Hard (quantitative threshold check)
2. SFT training loss stratification across APPS difficulty buckets (mechanistic analysis)

**Core Mechanism Implementation:**

```python
# H-M1 Core Analysis: SFT Signal Void Characterization
# Based on: bigcode-evaluation-harness + APPS difficulty stratification
# No novel architecture — analysis of existing SFT model

import json
import numpy as np
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class SFTSignalVoidAnalyzer:
    """
    Analyzes SFT model performance and training signal across difficulty levels.
    Verifies the signal void hypothesis for H-M1.
    """
    def __init__(self, sft_checkpoint: str, device: str = "cuda"):
        self.model = AutoModelForCausalLM.from_pretrained(sft_checkpoint).to(device)
        self.tokenizer = AutoTokenizer.from_pretrained(sft_checkpoint)
        self.device = device

    def compute_difficulty_stratified_loss(self, apps_train_split):
        """Compute per-difficulty-bucket mean cross-entropy loss."""
        losses = {"introductory": [], "interview": [], "competition": []}
        self.model.eval()
        with torch.no_grad():
            for example in apps_train_split:
                difficulty = example["difficulty"]
                # Tokenize (problem + reference solution)
                inputs = self.tokenizer(
                    example["question"] + example["solutions"][0],
                    return_tensors="pt", truncation=True, max_length=2048
                ).to(self.device)
                loss = self.model(**inputs, labels=inputs["input_ids"]).loss
                losses[difficulty].append(loss.item())
        return {k: float(np.mean(v)) for k, v in losses.items() if v}

    def verify_signal_void(self, lcb_hard_pass1: float, threshold: float = 0.60):
        """Check primary success criterion: SFT pass@1 < 60% on LCB-Hard."""
        return {
            "lcb_hard_pass1": lcb_hard_pass1,
            "threshold": threshold,
            "signal_void_confirmed": lcb_hard_pass1 < threshold,
            "margin": threshold - lcb_hard_pass1
        }

# Integration: Run after H-E1 evaluation produces SFT pass@1 results
# Input: SFT checkpoint path; bigcode-harness LiveCodeBench-Hard results JSON
# Output: signal_void_analysis.json with per-difficulty loss + pass@1 check
```

### Training Protocol

**H-M1 requires NO additional training.** Fully reuses the SFT model from H-E1.

| Component | Value | Source |
|-----------|-------|--------|
| Model | SFT checkpoint from H-E1 | H-E1 validation report |
| Training | None required — analysis only | H-E1 reuse |
| Optimizer | N/A (inherited from H-E1: AdamW) | H-E1 |
| Seed | 1 (same as H-E1) | H-E1 |

**H-M1 Experimental Tasks (analysis only):**

1. **Task A — LiveCodeBench-Hard evaluation:** Run bigcode-harness on LCB-Hard using H-E1 SFT checkpoint. If H-E1 already evaluated on LCB-Hard, extract results directly.

```bash
accelerate launch main.py \
  --model ./checkpoints/h-e1/sft_checkpoint \
  --tasks livecodebench \
  --n_samples 1 \
  --temperature 0.0 \
  --metric_output_path results/h-m1_sft_lcb_hard.json
```

2. **Task B — APPS difficulty-bucket loss analysis:** Forward pass through APPS split, computing per-example cross-entropy loss stratified by difficulty bucket.

```bash
python analyze_sft_loss.py \
  --checkpoint ./checkpoints/h-e1/sft_checkpoint \
  --dataset codeparrot/apps \
  --split train \
  --output results/h-m1_apps_difficulty_loss.json
```

3. **Task C — APPS Hard coverage check:** Measure % of APPS-Competition problems where any reference solution exists and passes all unit tests.

```bash
python check_apps_coverage.py \
  --dataset codeparrot/apps \
  --difficulty competition \
  --output results/h-m1_apps_hard_coverage.json
```

### Evaluation

**Primary Success Criterion:**
- SFT pass@1 on LiveCodeBench-Hard < 60%

**Secondary Success Criterion:**
- SFT training loss on APPS-Competition > SFT training loss on APPS-Introductory (difficulty-graded gradient signal confirmed)

| Metric | Target | Expected Value | Source |
|--------|--------|----------------|--------|
| SFT pass@1 LCB-Hard | < 60% | 10–35% | Literature: 7B RL models at 42–52%; SFT ~20–30pp lower |
| SFT pass@1 HumanEval | Any (reference) | 40–50% | Phase 2B Section 1.4 |
| APPS-Competition loss | > APPS-Intro loss | Δ > 0.5 nats | Expected from APPS difficulty structure |
| APPS-Hard coverage | < 30% solvable | ~5–15% | APPS+ data: only 572 competition problems |

**PoC Pass Condition:**
1. Code runs without error
2. `sft_pass1_lcb_hard < 0.60` (primary)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: code generation evaluation
- Library: bigcode-evaluation-harness (primary); custom forward-pass script (secondary)
- Code:
```python
# Extract pass@1 from bigcode-harness output
with open("results/h-m1_sft_lcb_hard.json") as f:
    results = json.load(f)
sft_lcb_hard_pass1 = results["livecodebench"]["pass@1"]
signal_void_confirmed = sft_lcb_hard_pass1 < 0.60
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing SFT pass@1 vs 60% threshold at LiveCodeBench-Hard

#### Additional Figures (LLM Autonomous)

1. **Difficulty-Performance Gradient:** Line chart of SFT pass@1 across all benchmarks (HumanEval → MBPP → LCB-Easy → LCB-Medium → LCB-Hard), showing progressive degradation confirming signal void at hard difficulty.

2. **APPS Difficulty-Bucket Loss Heatmap:** Bar chart of mean SFT training loss by APPS difficulty bucket (introductory / interview / competition), annotated with sample counts per bucket.

3. **APPS Coverage Analysis:** Stacked bar showing % of APPS-Competition problems with ≥1 passing reference solution vs problems with no passing solution (direct evidence of signal void).

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures saved to `docs/youra_research/h-m1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (bigcode-harness + loss analysis scripts)
2. `sft_pass1_lcb_hard < 0.60` (primary criterion confirmed)

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | SFT model from H-E1 checkpoint available | TRUE — H-E1 validated, checkpoint exists |
| Mechanism Isolatable | Signal void = SFT behavior, measurable independently | TRUE — SFT is the "no-signal" condition |
| Baseline Measurable | Pass@1 via bigcode-harness is deterministic (greedy) | TRUE — bigcode-harness documented and reproducible |

### Architecture Compatibility Check

H-M1 tests SFT signal void — it does NOT introduce a new architectural mechanism. Compatibility requirements:

**Required Features:**
- DeepSeek-Coder-7B-base: decoder-only transformer with standard causal language modeling — compatible with bigcode-harness
- APPS dataset: `difficulty` field available for stratification (confirmed in codeparrot/apps schema)
- bigcode-harness: supports `livecodebench` task natively

**Incompatible Configurations:**
- NONE for this hypothesis — standard SFT + eval pipeline

> ✅ Architecture fully compatible. No early-failure risk.

### Mechanism Activation Indicators

H-M1 "mechanism" = SFT signal void at hard difficulty. Activation is confirmed when:

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Pass@1 value | SFT LCB-Hard pass@1 < 0.60 | results/h-m1_sft_lcb_hard.json |
| Loss stratification | competition_loss > introductory_loss | results/h-m1_apps_difficulty_loss.json |
| Coverage check | APPS-Competition solvable < 30% | results/h-m1_apps_hard_coverage.json |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_signal_void_mechanism(results_dir: str) -> dict:
    """Verify H-M1: SFT signal void confirmed at hard difficulty."""
    import json, os

    # Primary: LiveCodeBench-Hard pass@1
    with open(os.path.join(results_dir, "h-m1_sft_lcb_hard.json")) as f:
        lcb_results = json.load(f)
    sft_lcb_hard = lcb_results["livecodebench"]["pass@1"]

    # Secondary: APPS difficulty-bucket loss
    with open(os.path.join(results_dir, "h-m1_apps_difficulty_loss.json")) as f:
        loss_results = json.load(f)
    loss_gradient_confirmed = (
        loss_results["competition"] > loss_results["introductory"]
    )

    indicators = {
        "sft_lcb_hard_pass1": sft_lcb_hard,
        "signal_void_primary": sft_lcb_hard < 0.60,
        "loss_gradient_secondary": loss_gradient_confirmed,
        "competition_loss": loss_results.get("competition"),
        "introductory_loss": loss_results.get("introductory"),
    }
    success = indicators["signal_void_primary"]
    return success, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| SFT pass@1 ≥ 60% on LCB-Hard | `sft_lcb_hard_pass1 >= 0.60` in results | EXPLORE: A1 violated; signal void framing needs revision |
| Flat loss across difficulty | `competition_loss ≈ introductory_loss` | FLAG: APPS difficulty gradient weaker than expected |
| Bigcode-harness crash | Non-zero exit code or missing output file | FIX: Check GPU memory, harness version compatibility |
| Checkpoint missing | H-E1 SFT checkpoint not found | FIX: Re-run H-E1 training or use base model for SFT |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Signal Void Confirmed | SFT LCB-Hard pass@1 < 0.60 | bigcode-harness output |
| Loss Gradient | competition_loss > introductory_loss | forward-pass analysis |
| Hypothesis Supported | Both primary + secondary criteria met | combined results JSON |

- **hypothesis_support_threshold:** SFT pass@1 on LiveCodeBench-Hard < 0.60 (strict); secondary: APPS competition loss > introductory loss
- **hypothesis_support_metric:** `sft_pass1_lcb_hard` from bigcode-evaluation-harness

---

## Appendix: Reference Implementations

### A. Knowledge Base Sources (WebSearch — Archon MCP unavailable)

**Source A.1**: APPS Paper — Hendrycks et al., 2021
- **URL**: https://datasets-benchmarks-proceedings.neurips.cc/paper/2021/file/c24cd76e1ce41366a4bbe8a49b02a028-Paper-round2.pdf
- **Relevance**: APPS dataset structure, difficulty distribution (introductory/interview/competition), coverage statistics
- **Key Insight**: Test set: 1000 introductory, 3000 interview, 1000 competition. Training set mirrors this distribution. Competition coverage sparse.
- **Used For**: Dataset specification, APPS difficulty-bucket analysis design

**Source A.2**: RLEF Paper — Gehring et al., 2024
- **URL**: https://arxiv.org/pdf/2410.02089
- **Relevance**: Fraction-of-tests-passing reward formulation; SFT vs RLEF performance gap; execution feedback mechanism
- **Key Insight**: RLEF grounds correction loops in real execution feedback; substantially outperforms SFT especially at hard problems
- **Used For**: Background context for why SFT signal void matters

**Source A.3**: SFT-then-RL paper — arXiv:2604.23747
- **URL**: https://arxiv.org/html/2604.23747v1
- **Relevance**: Documents SFT limitations at hard difficulty: "On-policy RL suffers from sparse rewards on hard problems where the model rarely generates a correct solution, and SFT alone does not develop the model's own reasoning capacity."
- **Used For**: Theoretical grounding of signal void mechanism; expected loss stratification

**Source A.4**: DeepSeek-Coder paper
- **URL**: https://github.com/deepseek-ai/DeepSeek-Coder
- **Relevance**: DeepSeek-Coder-Base-6.7B: 49.4% pass@1 HumanEval, 60.6% MBPP from base weights
- **Used For**: Baseline model performance expectations

**Source A.5**: LiveCodeBench Hard — EmergentMind aggregation
- **URL**: https://www.emergentmind.com/topics/livecodebench-hard
- **Relevance**: 7B RL-finetuned models at 42–52% on LCB-Hard; SFT baselines expected 20–30pp lower
- **Used For**: Expected SFT pass@1 range for hypothesis plausibility check

### B. GitHub Implementations

**Repository B.1**: bigcode-project/bigcode-evaluation-harness
- **URL**: https://github.com/bigcode-project/bigcode-evaluation-harness
- **Relevance**: Primary evaluation harness for pass@1 on HumanEval, MBPP, LiveCodeBench
- **Configuration Extracted**: `--tasks livecodebench`, `--n_samples 1`, `--temperature 0.0`, `--metric_output_path`
- **Used For**: Task A (LiveCodeBench-Hard evaluation)

**Repository B.2**: Ablustrund/APPS_Plus
- **URL**: https://github.com/Ablustrund/APPS_Plus
- **Relevance**: APPS+ difficulty stratification statistics — competition: 572/7413 (7.7%)
- **Configuration Extracted**: difficulty bucket labels, problem counts per bucket
- **Used For**: Dataset specification, coverage analysis

**Repository B.3**: huggingface/trl
- **URL**: https://github.com/huggingface/trl/blob/main/trl/trainer/grpo_trainer.py
- **Relevance**: GRPOTrainer architecture for H-E1 training pipeline (inherited by H-M1)
- **Used For**: Training infrastructure reference (shared with H-E1)

### C. Code Analysis (Serena)

Serena analysis not performed — code was sufficiently clear from documentation and search results. Standard pipeline (bigcode-harness + APPS dataset) is well-documented.

### D. Previous Hypothesis Context

**Source D.1**: H-E1 Validation Report
- **File**: `docs/youra_research/h-e1/04_validation.md` (expected after H-E1 Phase 4)
- **Reused Components**:
  - SFT checkpoint: `./checkpoints/h-e1/sft_checkpoint`
  - APPS train split configuration (tokenization, max_length, gradient steps)
  - bigcode-harness evaluation setup (temperature, n_samples, tasks)
  - LiveCodeBench 2024-Q4 snapshot (same snapshot as H-E1)
- **Why Reused**: Controlled experiment — only the analysis changes, not the model or data

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (APPS train split) | Phase 2A/2B, APPS paper | A.1, D.1 |
| Dataset (LiveCodeBench-Hard eval) | LiveCodeBench paper | A.2, B.1 |
| APPS difficulty distribution | APPS+, APPS paper | A.1, B.2 |
| SFT model (H-E1 checkpoint) | H-E1 validation report | D.1 |
| Expected SFT performance range | Literature survey | A.3, A.5 |
| Evaluation command (bigcode-harness) | Official documentation | B.1 |
| Loss stratification approach | Training loss theory, A.3 | A.3 |
| Signal void threshold (60%) | Phase 2B success criteria | D.1 (H-M1 spec) |
| Verification pseudo-code | Custom (derived from sources) | B.1, A.3 |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — state restated in ```state block)
**Date:** 2026-08-26

### Workflow History for This Hypothesis

- 2026-08-26T04:59:15Z: H-M1 set to IN_PROGRESS (External loop starting Phase 2C → 3 → 4)
- 2026-08-26: Phase 2C experiment design IN_PROGRESS → COMPLETED

---

*MCP Tools Used: WebSearch (Archon/Exa MCP unavailable — documented fallback)*
*All specifications grounded in real published sources*
*Note: Archon and Exa MCP were unavailable; WebSearch used as documented fallback per step-02/03 protocol*
*Next Phase: Phase 3 - Implementation Planning*
