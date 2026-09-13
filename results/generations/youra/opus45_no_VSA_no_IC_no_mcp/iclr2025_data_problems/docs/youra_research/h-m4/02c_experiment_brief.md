# Experiment Design: H-M4

**Date:** 2026-08-28
**Author:** PrayPrey
**Hypothesis Statement:** Under optimal curation parameters identified at 125M scale, the same parameters at 1B scale preserve relative performance rankings
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M3 PASS)
**Gate Status:** SHOULD_WORK (in progress)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M4
- **Type:** MECHANISM
- **Prerequisites:** H-M3 (PASS - optimal threshold p44.5 identified)

### Gate Condition
Optimal threshold at 1B within ±20% of 125M optimum; CPDR-optimized outperforms defaults at both scales.

---

## Continuation Context

H-M3 validated optimal balance point at p44.5 (95% CI [p40, p50]) using synthetic data. H-M4 tests whether this optimal threshold transfers across model scales (125M → 1B).

### Previous Hypothesis Results (if applicable)
**H-M3 Results:**
- Optimal threshold: p44.5 (internal, not boundary)
- Best model: quadratic (confirmed dose-response curvature)
- 95% CI width: 10 percentile points (< 30 threshold)
- Limitation: Synthetic data used; real sweep data needed

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP unavailable - using established scaling laws literature:*

1. **Chinchilla Scaling Laws** (Hoffmann et al. 2022): Compute-optimal training shows consistent relative ordering across scales. 125M→1B transfer supported by 10:1 parameter ratio with matched effective compute.

2. **RedPajama Pipeline**: Uses fixed perplexity thresholds across model sizes. Default configuration applies same filtering regardless of target model scale.

3. **Data-Efficient LLM Training** (arXiv:2405.20541): Notes optimal thresholds may vary but relative rankings tend to preserve.

### Archon Code Examples

*MCP unavailable - standard implementations referenced:*

```python
# HuggingFace GPT-2 scaling patterns
from transformers import GPT2Config, GPT2LMHeadModel

# 125M config (standard GPT-2 small)
config_125m = GPT2Config(n_embd=768, n_layer=12, n_head=12)

# 1B config (GPT-2 XL scale)  
config_1b = GPT2Config(n_embd=1600, n_layer=48, n_head=25)
```

### Exa GitHub Implementations

*MCP unavailable - known repositories:*

1. **togethercomputer/RedPajama-Data**: Official RedPajama preprocessing scripts
2. **EleutherAI/gpt-neox**: Scale-aware training infrastructure
3. **huggingface/transformers**: Standard GPT-2 implementations at all scales

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

For scale transfer experiments, no single official implementation exists. Priority is compute-matched comparison using identical data pipelines.

**Recommended Implementation Path:**
- Primary: HuggingFace Transformers GPT-2 at both scales
- Fallback: GPT-NeoX for 1B+ if memory constrained
- Justification: Consistent architecture family enables clean comparison; HF ecosystem well-documented

### Code Analysis (Serena MCP)

*MCP unavailable - standard patterns:*

Scale transfer validation requires:
1. Identical tokenizer and data pipeline at both scales
2. Compute-matched training (not token-matched)
3. Consistent evaluation harness (lm-eval-harness)

---

## Experiment Specification

### Dataset

| Attribute | Value |
|-----------|-------|
| Name | RedPajama-Data-v2 (English subset) |
| Type | standard |
| Source | HuggingFace Hub: togethercomputer/RedPajama-Data-v2 |
| Split | train (filtered subsets) |
| Size | 10B tokens (125M) / 20B tokens (1B) - compute-matched |
| Preprocessing | KenLM 5-gram perplexity filtering at optimal threshold (p44.5 from H-M3) |
| Augmentation | None |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: togethercomputer/RedPajama-Data-v2
- Code:
```python
from datasets import load_dataset

# Load RedPajama-v2 English subset
dataset = load_dataset(
    "togethercomputer/RedPajama-Data-v2",
    name="sample",  # Use sample for initial testing
    languages=["en"],
    streaming=True
)
```

### Models

#### Baseline Model

| Attribute | Value |
|-----------|-------|
| Name | GPT-2 (125M and 1B scales) |
| Architecture | Decoder-only Transformer |
| Source | HuggingFace Transformers |
| Pretrained | No (train from scratch) |
| Config | Standard GPT-2 configurations |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers (config only, train from scratch)
- Identifier: gpt2 (125M), gpt2-xl config adapted to 1B
- Code:
```python
from transformers import GPT2Config, GPT2LMHeadModel

# 125M model
config_125m = GPT2Config(
    vocab_size=50257,
    n_positions=1024,
    n_embd=768,
    n_layer=12,
    n_head=12
)
model_125m = GPT2LMHeadModel(config_125m)

# 1B model (GPT-2 XL scale)
config_1b = GPT2Config(
    vocab_size=50257,
    n_positions=1024,
    n_embd=1600,
    n_layer=48,
    n_head=25
)
model_1b = GPT2LMHeadModel(config_1b)
```

#### Proposed Model

**Architecture:** GPT-2 at 125M and 1B scales with CPDR-optimized filtering

**Core Mechanism Implementation:**

```python
# Scale Transfer Validation Core Logic
# Tests whether optimal threshold transfers from 125M to 1B

def scale_transfer_experiment(
    optimal_threshold: float,  # From H-M3 (p44.5)
    default_threshold: float,  # RedPajama default
    scales: list = [125_000_000, 1_000_000_000],
    token_budget_125m: int = 10_000_000_000,
    benchmark_ensemble: list = ["hellaswag", "arc_easy", "piqa", "winogrande"]
):
    """
    Test scale-invariant optima hypothesis.
    
    Success criteria:
    1. Optimal threshold at 1B within ±20% of 125M optimum
    2. CPDR-optimized outperforms defaults at both scales
    """
    results = {}
    
    for scale in scales:
        # Compute-matched token budget
        # 1B needs ~2x tokens for same effective compute
        compute_ratio = scale / 125_000_000
        token_budget = int(token_budget_125m * (compute_ratio ** 0.5))
        
        # Train with optimal threshold
        score_optimal = train_and_evaluate(
            scale=scale,
            threshold=optimal_threshold,
            tokens=token_budget,
            benchmarks=benchmark_ensemble
        )
        
        # Train with default threshold
        score_default = train_and_evaluate(
            scale=scale,
            threshold=default_threshold,
            tokens=token_budget,
            benchmarks=benchmark_ensemble
        )
        
        results[scale] = {
            "optimal_score": score_optimal,
            "default_score": score_default,
            "improvement": score_optimal - score_default
        }
    
    # Validate scale transfer
    improvement_125m = results[125_000_000]["improvement"]
    improvement_1b = results[1_000_000_000]["improvement"]
    
    # Success: relative rankings preserved
    rankings_preserved = (
        (improvement_125m > 0 and improvement_1b > 0) or
        (improvement_125m < 0 and improvement_1b < 0)
    )
    
    # Optional: identify 1B-specific optimum via mini-sweep
    if not rankings_preserved:
        optimal_1b = run_mini_sweep(scale=1_000_000_000)
        threshold_delta = abs(optimal_1b - optimal_threshold) / optimal_threshold
        # Document as scale-specific finding if delta > 20%
    
    return results, rankings_preserved
```

### Training Protocol

| Parameter | 125M Model | 1B Model | Notes |
|-----------|------------|----------|-------|
| Optimizer | AdamW | AdamW | β1=0.9, β2=0.95 |
| Learning Rate | 6e-4 | 2e-4 | Lower for larger model |
| LR Schedule | Cosine with warmup | Cosine with warmup | 2000 warmup steps |
| Batch Size | 512K tokens | 2M tokens | Gradient accumulation |
| Epochs | 1 pass | 1 pass | Token budget determines |
| Tokens | 10B | 20B | Compute-matched |
| Loss | Cross-entropy | Cross-entropy | Standard LM loss |
| Weight Decay | 0.1 | 0.1 | AdamW default |
| Gradient Clip | 1.0 | 1.0 | Max norm |
| Mixed Precision | FP16 | BF16 | Memory efficiency |
| Seeds | 3 | 3 | Statistical validity |

### Evaluation

| Metric | Method | Success Threshold |
|--------|--------|-------------------|
| Benchmark Ensemble | PC1 of (HellaSwag, ARC-Easy, PIQA, WinoGrande) | Optimal > Default at both scales |
| Relative Improvement | (optimal - default) / default | Same sign at both scales |
| Threshold Transfer | |optimal_1B - optimal_125M| / optimal_125M | < 20% |

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Zero-shot evaluation
- Library: lm-eval-harness (EleutherAI)
- Code:
```python
# Using lm-eval-harness for evaluation
import lm_eval

results = lm_eval.simple_evaluate(
    model="hf",
    model_args=f"pretrained={model_path}",
    tasks=["hellaswag", "arc_easy", "piqa", "winogrande"],
    batch_size=16,
    device="cuda"
)

# Extract scores
scores = {
    task: results["results"][task]["acc,none"]
    for task in ["hellaswag", "arc_easy", "piqa", "winogrande"]
}

# Compute ensemble (PC1 or simple mean for PoC)
ensemble_score = sum(scores.values()) / len(scores)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

1. **Scale Transfer Plot**: Side-by-side bar chart showing improvement at 125M vs 1B scales
2. **Threshold Sensitivity**: Line plot showing performance vs threshold at both scales (if mini-sweep conducted)
3. **Per-Benchmark Breakdown**: Grouped bar chart showing individual benchmark scores at each scale

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Optimal threshold outperforms default at 125M scale
3. Optimal threshold outperforms default at 1B scale (rankings preserved)

**Quantitative Criteria (from 02b):**
- Primary: Optimal threshold at 1B within ±20% of 125M optimum
- Secondary: CPDR-optimized outperforms defaults at both scales

---

## Appendix: Reference Implementations

### Training Infrastructure

1. **HuggingFace Transformers**
   - URL: https://github.com/huggingface/transformers
   - Components: GPT2Config, GPT2LMHeadModel, Trainer
   - Adaptability: Direct use for both scales

2. **EleutherAI lm-eval-harness**
   - URL: https://github.com/EleutherAI/lm-evaluation-harness
   - Components: Zero-shot evaluation on HellaSwag, ARC, PIQA, WinoGrande
   - Adaptability: Standard evaluation harness

### Data Pipeline

1. **RedPajama-Data-v2**
   - URL: https://github.com/togethercomputer/RedPajama-Data
   - Components: Perplexity filtering scripts, deduplication
   - Adaptability: Apply threshold at p44.5 (optimal from H-M3)

2. **KenLM**
   - URL: https://github.com/kpu/kenlm
   - Components: 5-gram perplexity scoring
   - Adaptability: Score corpus for threshold filtering

### Scaling Reference

1. **Chinchilla Paper Implementation Patterns**
   - Source: Hoffmann et al. 2022 methodology
   - Key insight: Compute-optimal tokens scale sublinearly with parameters
   - Application: Token budget calculation for 1B model

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28T02:00:00Z

### Workflow History for This Hypothesis
- 2026-08-28: H-M3 completed (PASS), H-M4 initiated
- H-M4 builds on H-M3 optimal threshold (p44.5)
- Gate: SHOULD_WORK - failure documents scale-specific optima as finding

---

*MCP Tools Used: None available (Archon, Exa, Serena unavailable)*
*Specifications based on 02b_verification_plan and H-M3 results*
*Next Phase: Phase 3 - Implementation Planning*
