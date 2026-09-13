# Phase 2C Experiment Brief: h-c1

## Hypothesis

**ID**: h-c1  
**Type**: CONDITION  
**Gate**: SHOULD_WORK  
**Statement**: Scaling law α estimate is consistent (within 0.15) across single-hop (SQuAD-v2) and multi-hop (HotpotQA) QA tasks

## Prerequisites

- **h-e1**: VALIDATED (PASS) - Established scaling exponent methodology on SQuAD-v2
- **Continuation**: Reuses h-e1 infrastructure, adds HotpotQA for cross-task comparison

---

## Experimental Design

### Overview

Replicate h-e1's LoRA rank scaling analysis on HotpotQA (multi-hop QA), then compare the fitted α exponent against h-e1's SQuAD-v2 result. Pass if |α_squad - α_hotpot| ≤ 0.15.

### Models (Reused from h-e1)

| Model | N (params) | log₁₀(N) | HuggingFace ID |
|-------|------------|----------|----------------|
| Pythia-1B | 1.0×10⁹ | 9.00 | EleutherAI/pythia-1b |
| Pythia-2.8B | 2.8×10⁹ | 9.45 | EleutherAI/pythia-2.8b |
| Pythia-6.9B | 6.9×10⁹ | 9.84 | EleutherAI/pythia-6.9b |
| Pythia-12B | 1.2×10¹⁰ | 10.08 | EleutherAI/pythia-12b |

### Datasets

#### Dataset 1: SQuAD-v2 (from h-e1)
- **Type**: standard (single-hop extractive QA)
- **Size**: Train 130,319 / Val 11,873
- **Metric**: F1 score
- **Loading**: `load_dataset("squad_v2")`
- **Result**: α_squad from h-e1 validation

#### Dataset 2: HotpotQA (NEW)
- **Type**: standard (multi-hop QA)
- **Size**: Train 90,447 / Val 7,405 (distractor setting)
- **Metric**: F1 score + Supporting Facts F1
- **Loading**: `load_dataset("hotpotqa/hotpot_qa", "distractor")`
- **Rationale**: Multi-hop reasoning tests if α varies with reasoning complexity

**Data Loading Code**:
```python
from datasets import load_dataset

# SQuAD-v2 (reuse h-e1)
squad = load_dataset("squad_v2")

# HotpotQA (new)
hotpot = load_dataset("hotpotqa/hotpot_qa", "distractor")
# Train: 90,447, Val: 7,405
```

### LoRA Configuration (Reused from h-e1)

- **Ranks to sweep**: [4, 8, 16, 32, 64, 128]
- **Target modules**: ["query_key_value"]
- **LoRA alpha**: 2×rank (rsLoRA scaling: α/√r)
- **Dropout**: 0.05

### Training Protocol (Reused from h-e1)

- **Epochs**: 3
- **Learning rate**: 1e-4 (AdamW)
- **Batch size**: 8 (effective 32 via gradient accumulation)
- **Warmup**: 100 steps
- **Scheduler**: linear decay
- **Seeds**: 3

**Total runs (HotpotQA only)**: 4 models × 6 ranks × 3 seeds = 72 training runs

### Evaluation Metrics

**Primary Metrics**:
- HotpotQA Answer F1 (main gate metric)
- Supporting Facts F1 (secondary, multi-hop indicator)

**Evaluation Code**:
```python
from datasets import load_metric

# Official HotpotQA evaluation
def evaluate_hotpot(predictions, references):
    em, f1 = 0, 0
    for pred, ref in zip(predictions, references):
        # Exact match and F1 on answer span
        em += exact_match(pred, ref)
        f1 += compute_f1(pred, ref)
    return {"em": em/len(predictions), "f1": f1/len(predictions)}
```

### Statistical Analysis

**Per-dataset analysis** (same as h-e1):
```
log(r_opt) = α·log(N) + log(c)
```

**Cross-task comparison**:
```python
# From h-e1: α_squad, ci_squad_low, ci_squad_high
# From h-c1: α_hotpot, ci_hotpot_low, ci_hotpot_high

difference = abs(alpha_squad - alpha_hotpot)
pass_condition = difference <= 0.15
```

**CI estimation**: Bootstrap (B=1000) for each dataset

### Pass Criteria

1. HotpotQA α point estimate in (0, 1) - sanity check
2. |α_squad - α_hotpot| ≤ 0.15 - cross-task consistency
3. 95% CIs overlap (secondary indicator)

### Core Mechanism Pseudo-code

```python
# Cross-Task Scaling Consistency Analysis
# Based on h-e1 methodology + HotpotQA extension

def run_cross_task_comparison():
    # 1. Load h-e1 results (SQuAD-v2)
    alpha_squad = load_h_e1_results()["alpha"]
    ci_squad = load_h_e1_results()["alpha_ci"]
    
    # 2. Run HotpotQA rank sweep (same as h-e1)
    results_hotpot = []
    for model in PYTHIA_MODELS:
        for rank in [4, 8, 16, 32, 64, 128]:
            for seed in [42, 43, 44]:
                f1 = train_and_eval_lora(
                    model=model,
                    dataset="hotpotqa",
                    rank=rank,
                    seed=seed
                )
                results_hotpot.append((model, rank, seed, f1))
    
    # 3. Find optimal ranks per model
    r_opt_hotpot = find_optimal_ranks(results_hotpot)
    
    # 4. Fit scaling law
    alpha_hotpot, ci_hotpot = fit_scaling_law(r_opt_hotpot)
    
    # 5. Compare across tasks
    difference = abs(alpha_squad - alpha_hotpot)
    return {
        "pass": difference <= 0.15,
        "alpha_squad": alpha_squad,
        "alpha_hotpot": alpha_hotpot,
        "difference": difference
    }
```

### Ablation Studies (CONDITION type)

| Variant | Purpose |
|---------|---------|
| Full validation set | Primary (7,405 samples) |
| Distractor vs fullwiki | Check if IR noise affects α |
| Bridge vs comparison Qs | Check if question type affects α |

### Visualization Requirements

#### Required Figure (Mandatory)
- **Dual scaling plot**: log(r_opt) vs log(N) for both datasets, with fit lines and CI bands
- **Difference bar**: |α_squad - α_hotpot| with 0.15 threshold line

#### Additional Figures
- Per-model rank-F1 curves (both datasets overlaid)
- Bootstrap α distribution comparison

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: LoRA rank scaling QA tasks**
- rsLoRA paper (arXiv:2312.03732): α/√r scaling prevents gradient collapse at high ranks
- Scaling follows square-root law: optimal α scales as √r
- Used for: LoRA configuration

**Query 2: Multi-hop reasoning HotpotQA**
- HotpotQA requires finding/reasoning over multiple documents
- 113K QA pairs, sentence-level supporting facts
- Used for: Dataset selection rationale

### Archon Code Examples

**PEFT LoRA Configuration**:
```python
from peft import LoraConfig, TaskType, get_peft_model

peft_config = LoraConfig(
    r=16,
    lora_alpha=32,  # 2×rank per rsLoRA
    task_type=TaskType.QUESTION_ANS,
    target_modules=["query_key_value"]
)
model = get_peft_model(model, peft_config)
```

### Exa GitHub Implementations

**Repository 1**: uygarkurt/LoRA-BERT-For-Question-Answering
- LoRA fine-tuning on SQuAD with PEFT
- Training loop reference

**Repository 2**: hotpotqa/hotpot (official)
- Baseline model code
- Evaluation script: `hotpot_evaluate_v1.py`
- Data download pipeline

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear (standard PEFT + HuggingFace patterns)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

| Source | Query | Used For |
|--------|-------|----------|
| rsLoRA paper | "LoRA rank scaling" | α/√r scaling factor |
| HotpotQA paper | "multi-hop reasoning" | Dataset rationale |
| PEFT docs | "LoRA PEFT HuggingFace" | Code examples |

### B. GitHub Implementations (Exa)

| Repository | Stars | Used For |
|------------|-------|----------|
| hotpotqa/hotpot | Official | Evaluation script |
| huggingface/peft | High | LoRA implementation |
| uygarkurt/LoRA-BERT-QA | Medium | Training pattern |

### C. Previous Hypothesis Context

**Source**: h-e1 validation (PASS)
- Reused: Pythia models, LoRA config, rank sweep, training protocol
- New: HotpotQA dataset, cross-task comparison logic

---

## Computational Budget

| Component | GPU-hours (A100) |
|-----------|------------------|
| HotpotQA sweep (72 runs) | ~78h |
| Analysis | ~1h |
| **Total (h-c1 only)** | ~79h |

*Note: h-e1 results already computed*

---

## Validation Checklist

- [x] Real datasets (SQuAD-v2, HotpotQA - standard benchmarks)
- [x] Statistically meaningful samples (7,405+ validation examples)
- [x] Clear pass/fail criteria (|Δα| ≤ 0.15)
- [x] Reproducible (reuses h-e1 methodology)
- [x] Builds on validated prerequisite (h-e1 PASS)

---

*Generated: 2026-08-24*
*Phase 2C complete for h-c1*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
