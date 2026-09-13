# Experiment Design: H-M2

**Date:** 2026-08-10
**Author:** PrayPrey
**Hypothesis Statement:** High-entropy tasks tolerate eviction better - stratified by entropy, high-entropy group shows higher accuracy retention under eviction
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **MECHANISM Hypothesis** - Testing entropy-eviction tolerance relationship

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M1 PASSED: F=38.05, p=2.92e-26, eta²=0.522)
**Gate Status:** SHOULD_WORK (p<0.05 for high-entropy eviction advantage)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (PASSED - entropy discriminates task domains)

### Gate Condition
High-entropy group shows significantly higher accuracy retention under eviction (p<0.05), with effect size Cohen's d > 0.5

---

## Continuation Context

### Previous Hypothesis Results (H-M1)

**PASSED** - Attention entropy discriminates task domains:
- F-statistic: 38.05 (between-domain variance ~38x within-domain)
- p-value: 2.92e-26 (extremely significant)
- eta-squared: 0.522 (52% variance explained by domain)
- Entropy matrix available: `h-m1/code/entropy_matrix.npy`
- Domain means available: `h-m1/code/domain_means.json`

**Reusable Components:**
- LongBench-v2 dataset (6 domains, 30 samples/domain = 180 total)
- Llama-2-7B model configuration
- Entropy extraction code and results
- Domain stratification (high/low entropy split by median)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: KV cache eviction attention entropy**
- Flash-Attention KV cache implementation patterns
- Paged KV cache with block_table support
- Cache sequence length tracking mechanisms

**Query 2: H2O implementation**
- flash_attn_with_kvcache function showing in-place KV updates
- Support for MQA/GQA attention patterns
- Window-based attention with cache_seqlens tracking

### Archon Code Examples

**Flash Attention KV Cache Pattern:**
```python
def flash_attn_with_kvcache(
    q, k_cache, v_cache,
    k=None, v=None,
    cache_seqlens: Optional[Union[int, torch.Tensor]] = None,
    block_table: Optional[torch.Tensor] = None,
    softmax_scale=None,
    causal=False,
    window_size=(-1, -1),
):
    # In-place update of k_cache, v_cache
    # Supports incremental decoding
```

### Exa GitHub Implementations

**Primary: FMInference/H2O (Official)**
- Repository: https://github.com/FMInference/H2O
- Stars: 518, Forks: 81
- NeurIPS'23 paper implementation
- Key insight: top 20% tokens capture ~85% attention mass
- Supports real KV dropping (not masking)
- Scripts: `scripts/summarization/eval.sh` for LongBench-style tasks

**Secondary: awslabs/keys_values**
- H2OKVCache class with per-batch eviction decisions
- Improvements over original: independent batch entry eviction
- Normalized cumulative scores option

**Tertiary: suhasramanand/kv-cache-compression**
- Research-quality implementation
- 50-87.5% compression with minimal quality degradation
- Comprehensive evaluation framework

### Implementation Priority Assessment

**CRITICAL: Use official FMInference/H2O implementation**

**Recommended Implementation Path:**
- Primary: FMInference/H2O repository (`h2o_hf/` directory)
- Fallback: awslabs/keys_values H2OKVCache class
- Justification: Official NeurIPS'23 implementation with proven LongBench evaluation

### Code Analysis (Serena MCP)

Not applicable - using external H2O implementation, not codebase analysis.

---

## Experiment Specification

### Dataset

**Name:** LongBench-v2 (subset from H-M1)
**Type:** standard
**Source:** THUDM/LongBench (HuggingFace)

**Configuration:**
- Domains: 6 (same as H-M1)
- Samples per domain: 30
- Total samples: 180
- Stratification: Median split by entropy (from H-M1 results)
  - High-entropy group: ~90 samples (domains with mean entropy > median)
  - Low-entropy group: ~90 samples (domains with mean entropy < median)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `THUDM/LongBench`
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("THUDM/LongBench", split="test")
# Filter to 6 domains, 30 samples each (same as H-M1)
```

### Models

#### Baseline Model

**Architecture:** Llama-2-7B (same as H-M1/H-E1)
**Source:** meta-llama/Llama-2-7b-hf
**Configuration:**
- 32 layers, 32 attention heads
- Full KV cache (no eviction) - accuracy upper bound
- Load with H2O framework for consistent evaluation

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers + H2O wrapper
- Identifier: `meta-llama/Llama-2-7b-hf`
- Code:
```python
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    torch_dtype=torch.float16,
    device_map="auto"
)
```

#### Proposed Model

**Architecture:** Llama-2-7B + H2O eviction

**Core Mechanism Implementation:**

```python
# H2O Eviction Mechanism for Entropy-Tolerance Test
# Based on: FMInference/H2O (NeurIPS'23)

class H2OEvictionExperiment:
    """
    Test entropy-eviction tolerance relationship.
    High-entropy tasks should tolerate eviction better.
    """
    def __init__(self, model, retention_ratio=0.4):
        self.model = model
        self.retention_ratio = retention_ratio  # 40% or 80%
        
    def run_with_eviction(self, input_ids, eviction_config):
        """
        Args:
            input_ids: (B, L) tokenized input
            eviction_config: {ratio: 0.4|0.8, method: 'h2o'}
        Returns:
            accuracy_retention: acc_evicted / acc_full
        """
        # Step 1: Compute full KV baseline accuracy
        full_output = self.model.generate(input_ids, use_cache=True)
        full_acc = self.evaluate(full_output)
        
        # Step 2: Apply H2O eviction (keep heavy hitters + recent)
        # heavy_ratio + recent_ratio = retention_ratio
        heavy_ratio = eviction_config['ratio'] * 0.5
        recent_ratio = eviction_config['ratio'] * 0.5
        
        evicted_output = self.model.generate(
            input_ids,
            use_cache=True,
            heavy_ratio=heavy_ratio,
            recent_ratio=recent_ratio
        )
        evicted_acc = self.evaluate(evicted_output)
        
        # Step 3: Compute retention
        return evicted_acc / full_acc if full_acc > 0 else 0
```

### Training Protocol

**No Training Required** - This is an inference-time evaluation experiment.

**Experiment Configuration:**
- Eviction configs: 40% retention, 80% retention
- Heavy:Recent split: 50:50 (standard H2O)
- Batch size: 1 (per-sample evaluation)
- Seeds: 1 (fixed for reproducibility)

**Source:** H2O paper default configurations

### Evaluation

**Primary Metrics:**
- Accuracy retention = (accuracy with eviction) / (accuracy without eviction)
- Per-group mean: mean retention for high-entropy vs low-entropy group

**Statistical Test:**
- Independent samples t-test comparing high-entropy vs low-entropy groups
- Alternative: Mann-Whitney U if non-normal distribution
- Effect size: Cohen's d

**Success Criteria:**
- Primary: High-entropy group retention > Low-entropy group retention (p<0.05)
- Secondary: Cohen's d > 0.5 (medium-large effect)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: hypothesis testing
- Library: scipy.stats
- Code:
```python
from scipy.stats import ttest_ind, mannwhitneyu
from numpy import mean, std

# t-test
t_stat, p_value = ttest_ind(high_entropy_retentions, low_entropy_retentions)

# Effect size
cohens_d = (mean(high_entropy_retentions) - mean(low_entropy_retentions)) / pooled_std
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: High vs Low entropy group accuracy retention bar chart with error bars

#### Additional Figures (LLM Autonomous)
- Box plot: Retention distribution by entropy group
- Scatter plot: Task entropy vs accuracy retention (correlation)
- Heatmap: Retention by domain and eviction ratio

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## PoC Success Check

**Gate Pass Condition:**
1. Code runs without error
2. p-value < 0.05 for high vs low entropy comparison
3. High-entropy mean retention > Low-entropy mean retention

**Failure Response:** EXPLORE (check if relationship is non-linear or threshold-based)

---

## Mechanism Verification Protocol

### Pre-conditions
- `mechanism_exists`: H2O eviction mechanism exists in FMInference/H2O
- `mechanism_isolatable`: Yes - eviction ratio is controllable parameter
- `baseline_measurable`: Yes - full KV accuracy is measurable baseline

### Architecture Compatibility
- H2O supports Llama-2 architecture
- Integration: Wrap model with H2O KVCache manager
- No model modification needed

### Activation Indicators
- `mechanism_log_message`: "H2O eviction active: keeping {ratio}% of KV cache"
- `tensor_shape_change`: KV cache size reduced to `retention_ratio * original_size`
- `metric_delta_expected`: Accuracy retention < 1.0 (some accuracy loss expected)

### Mechanism Verification Code
```python
def verify_h2o_mechanism(model, sample_input):
    # Verify eviction is actually happening
    full_kv_size = get_kv_cache_size(model, sample_input, eviction=False)
    evicted_kv_size = get_kv_cache_size(model, sample_input, eviction=True, ratio=0.4)
    
    assert evicted_kv_size < full_kv_size * 0.5, "Eviction not working"
    print(f"KV cache reduced: {full_kv_size} -> {evicted_kv_size}")
    return True
```

### Hypothesis Support Criteria
- `hypothesis_support_threshold`: p < 0.05
- `hypothesis_support_metric`: t-test p-value for high vs low entropy comparison

---

## Appendix: Reference Implementations

| Source | URL | Relevance |
|--------|-----|-----------|
| H2O (Official) | https://github.com/FMInference/H2O | Primary H2O implementation |
| awslabs/keys_values | https://github.com/awslabs/keys_values | H2OKVCache class |
| LongBench | https://github.com/THUDM/LongBench | Dataset source |
| KeyDiff paper | https://arxiv.org/html/2504.15364v1 | LongBench KV eviction evaluation |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-10T23:50:00+00:00

### Workflow History for This Hypothesis
- H-M1 PASSED (prerequisite): F=38.05, p=2.92e-26, eta²=0.522
- Entropy discriminates task domains - foundation for H-M2
- Domain-level entropy means available for stratification

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
