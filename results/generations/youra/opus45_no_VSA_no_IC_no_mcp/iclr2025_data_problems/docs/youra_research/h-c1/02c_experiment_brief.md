# Experiment Design: H-C1

**Date:** 2026-08-28
**Author:** PrayPrey
**Hypothesis Statement:** CPDR-optimized curation parameters outperform RedPajama literature defaults by >1% on benchmark ensemble at 125M scale
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **COMPARISON (PoC) Template** - Validates that optimized parameters beat established baselines.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 (PASS), H-M1 (PASS), H-M2 (PASS), H-M3 (PASS)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-C1
- **Type:** COMPARISON
- **Prerequisites:** H-M3 (optimal balance point identified)

### Gate Condition
CPDR-optimized configuration achieves >1% improvement over RedPajama defaults on benchmark ensemble (HellaSwag, ARC-Easy, PIQA, WinoGrande).

---

## Continuation Context

This hypothesis builds on H-E1 through H-M3 which established:
1. Non-monotonic dose-response exists (H-E1)
2. Noise dilution mechanism confirmed (H-M1)
3. Quality-diversity tradeoff validated (H-M2)
4. Optimal perplexity threshold identified at ~p50 (H-M3)

### Previous Hypothesis Results (if applicable)
- H-M3 identified optimal perplexity threshold within p40-p60 range
- Peak benchmark performance at approximately p50 threshold
- Optimal deduplication at fuzzy_0.85 level

---

## Implementation Research Summary

### Archon Knowledge Base Findings

From prior hypothesis implementations in this project:
- GPT-2 125M training pipeline established in H-E1
- KenLM perplexity filtering implemented
- MinHash deduplication with configurable Jaccard threshold
- Benchmark evaluation using lm-evaluation-harness

### Archon Code Examples

```python
# From H-E1/H-M3 implementations
def apply_cpdr_config(dataset, ppl_threshold="p50", dedup_level="fuzzy_0.85"):
    filtered = perplexity_filter(dataset, threshold=ppl_threshold)
    deduped = minhash_dedup(filtered, jaccard=0.85)
    return deduped

def apply_redpajama_defaults(dataset):
    # RedPajama-v2 default: ~p30 perplexity, exact dedup
    filtered = perplexity_filter(dataset, threshold="p30")
    deduped = exact_dedup(filtered)
    return deduped
```

### Exa GitHub Implementations

- **lm-evaluation-harness** (EleutherAI): Standard benchmark evaluation framework
  - Source: github.com/EleutherAI/lm-evaluation-harness
  - Used for: HellaSwag, ARC-Easy, PIQA, WinoGrande evaluation
- **RedPajama-Data** (togethercomputer): Reference curation pipeline
  - Source: github.com/togethercomputer/RedPajama-Data
  - Used for: Baseline parameter configurations

### 🎯 Implementation Priority Assessment

**CRITICAL: Reuse existing codebase from H-E1/H-M3**

**Recommended Implementation Path:**
- Primary: Extend H-M3 training code with comparison logic
- Fallback: Standalone comparison script if refactoring needed
- Justification: H-M3 already has optimal params; just need head-to-head comparison

### Code Analysis (Serena MCP)

Key components from prior hypotheses:
- `train_gpt2.py`: Model training loop (reusable)
- `filter_data.py`: Perplexity filtering (reusable)
- `evaluate.py`: Benchmark evaluation (reusable)
- New: `compare_configs.py` for A/B comparison

---

## Experiment Specification

### Dataset

| Field | Value |
|-------|-------|
| **Name** | RedPajama-v2 (English subset) |
| **Type** | standard |
| **Source** | HuggingFace Hub |
| **Size** | 10B tokens per configuration |
| **Splits** | Train: 10B tokens, Val: held-out |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: togethercomputer/RedPajama-Data-v2
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("togethercomputer/RedPajama-Data-v2", 
                       "default", 
                       split="train",
                       streaming=True)
```

### Models

#### Baseline Model

| Field | Value |
|-------|-------|
| **Architecture** | GPT-2 125M |
| **Parameters** | 125M |
| **Source** | HuggingFace Transformers |
| **Config** | RedPajama default curation (p30 perplexity, exact dedup) |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers (train from scratch)
- Identifier: gpt2 config with 125M params
- Code:
```python
from transformers import GPT2Config, GPT2LMHeadModel
config = GPT2Config(n_embd=768, n_layer=12, n_head=12)
model = GPT2LMHeadModel(config)
```

#### Proposed Model

**Architecture:** GPT-2 125M with CPDR-optimized curation

**Core Mechanism Implementation:**

```python
def run_comparison_experiment(raw_dataset, seeds=[42, 43, 44]):
    """
    Compare CPDR-optimized vs RedPajama defaults.
    
    CPDR config: p50 perplexity threshold, fuzzy_0.85 dedup
    RedPajama config: p30 perplexity threshold, exact dedup
    """
    results = {"cpdr": [], "redpajama": []}
    
    for seed in seeds:
        # Prepare CPDR-optimized dataset
        cpdr_data = apply_perplexity_filter(raw_dataset, threshold="p50")
        cpdr_data = apply_minhash_dedup(cpdr_data, jaccard=0.85)
        
        # Prepare RedPajama-default dataset  
        rp_data = apply_perplexity_filter(raw_dataset, threshold="p30")
        rp_data = apply_exact_dedup(rp_data)
        
        # Train models (10B tokens each)
        cpdr_model = train_gpt2_125m(cpdr_data, tokens=10e9, seed=seed)
        rp_model = train_gpt2_125m(rp_data, tokens=10e9, seed=seed)
        
        # Evaluate on benchmark ensemble
        cpdr_score = evaluate_ensemble(cpdr_model, 
                                       tasks=["hellaswag", "arc_easy", 
                                              "piqa", "winogrande"])
        rp_score = evaluate_ensemble(rp_model,
                                     tasks=["hellaswag", "arc_easy",
                                            "piqa", "winogrande"])
        
        results["cpdr"].append(cpdr_score)
        results["redpajama"].append(rp_score)
    
    # Compute improvement
    cpdr_mean = np.mean(results["cpdr"])
    rp_mean = np.mean(results["redpajama"])
    improvement = cpdr_mean - rp_mean
    
    return {
        "cpdr_mean": cpdr_mean,
        "redpajama_mean": rp_mean,
        "improvement_pct": improvement * 100,
        "pass": improvement > 0.01  # >1% threshold
    }
```

### Training Protocol

| Parameter | Value |
|-----------|-------|
| **Optimizer** | AdamW |
| **Learning Rate** | 6e-4 with cosine decay |
| **Warmup** | 2000 steps |
| **Batch Size** | 512 (global) |
| **Tokens** | 10B per configuration |
| **Seeds** | 3 (42, 43, 44) |
| **Precision** | BF16 |

### Evaluation

| Metric | Description | Success Threshold |
|--------|-------------|-------------------|
| **Benchmark Ensemble** | Mean of (HellaSwag, ARC-Easy, PIQA, WinoGrande) | CPDR > RP + 1% |
| **Per-benchmark scores** | Individual task accuracy | Directional improvement |

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Multiple-choice QA
- Library: lm-evaluation-harness
- Code:
```python
from lm_eval import evaluator
results = evaluator.simple_evaluate(
    model=model,
    tasks=["hellaswag", "arc_easy", "piqa", "winogrande"],
    num_fewshot=0
)
ensemble_score = np.mean([results["results"][t]["acc"] 
                          for t in ["hellaswag", "arc_easy", "piqa", "winogrande"]])
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing CPDR vs RedPajama ensemble scores with error bars (3 seeds)

#### Additional Figures (LLM Autonomous)

1. **Per-benchmark breakdown**: Grouped bar chart showing individual benchmark scores
2. **Training curves**: Loss curves for both configurations
3. **Improvement waterfall**: Showing contribution of each benchmark to total improvement

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. CPDR ensemble score > RedPajama ensemble score + 1%

---

## Appendix: Reference Implementations

| Source | URL | Relevance |
|--------|-----|-----------|
| lm-evaluation-harness | github.com/EleutherAI/lm-evaluation-harness | Benchmark evaluation |
| RedPajama-Data | github.com/togethercomputer/RedPajama-Data | Baseline curation params |
| H-E1 implementation | h-e1/ (local) | Training pipeline |
| H-M3 implementation | h-m3/ (local) | Optimal params identified |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28T01:30:00Z

### Workflow History for This Hypothesis
- Created as COMPARISON hypothesis to validate P2 prediction from Phase 2A
- Prerequisites: H-E1, H-M1, H-M2, H-M3 (all PASS)
- Gate: SHOULD_WORK (>1% improvement expected based on H-M3 findings)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
