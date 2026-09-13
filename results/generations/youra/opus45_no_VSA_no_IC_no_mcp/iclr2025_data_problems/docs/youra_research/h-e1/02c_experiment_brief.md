# Experiment Design: H-E1

**Date:** 2026-08-28
**Author:** PrayPrey
**Hypothesis Statement:** At least one curation parameter (perplexity threshold or deduplication stringency) exhibits a non-monotonic (concave) dose-response relationship with benchmark ensemble score at 125M scale, with a measurable peak identifiable via polynomial regression.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites for H-E1)
**Gate Status:** MUST_WORK - Pending validation

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (root hypothesis)

### Gate Condition
Non-monotonic (quadratic or higher-order polynomial) model selected over linear model via AIC/BIC for at least one curation parameter dimension.

---

## Continuation Context

**First hypothesis in chain** - no previous results to inherit.

### Previous Hypothesis Results (if applicable)
N/A - This is the foundation hypothesis.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP unavailable - using Phase 2A/2B research context*

Key findings from Phase 2A research:
1. **KenLM 5-gram perplexity** is standard quality proxy (CCNet, C4, RedPajama pipelines)
2. **MinHash deduplication** with Jaccard threshold captures near-duplicates effectively
3. **Benchmark ensemble** (HellaSwag, ARC-Easy, PIQA, WinoGrande) reduces single-benchmark noise
4. **10B tokens** provides 4x Chinchilla-optimal for 125M scale (sufficient signal)

### Archon Code Examples

*MCP unavailable - using established implementations*

Reference implementations:
- **text-dedup** library for MinHash deduplication
- **KenLM** for perplexity scoring
- **lm-evaluation-harness** for benchmark evaluation
- **nanoGPT/minGPT** for efficient 125M training

### Exa GitHub Implementations

*MCP unavailable - using known repositories*

Relevant repositories:
1. **together-ai/RedPajama-Data** - Curation pipeline with perplexity filtering
2. **allenai/dolma** - Similar curation approach, documented thresholds
3. **EleutherAI/lm-evaluation-harness** - Standard benchmark suite
4. **karpathy/nanoGPT** - Efficient GPT-2 training reference

### 🎯 Implementation Priority Assessment

**CRITICAL: For dose-response study, prioritize established curation tools**

| Source | Priority | Rationale |
|--------|----------|-----------|
| RedPajama-v2 pipeline | P1 | Exact dataset with documented curation params |
| text-dedup library | P2 | Standard MinHash implementation |
| lm-evaluation-harness | P1 | Standard benchmark evaluation |

**Recommended Implementation Path:**
- Primary: Use RedPajama-v2 quality signals + custom threshold sweeps
- Fallback: Recompute perplexity/dedup from raw data using KenLM + text-dedup
- Justification: RedPajama-v2 includes precomputed quality signals, enabling efficient threshold sweeps without reprocessing

### Code Analysis (Serena MCP)

*MCP unavailable - proceeding with documented architecture*

Key architecture points from documentation:
- GPT-2 125M: 12 layers, 768 hidden, 12 heads
- Standard decoder-only transformer
- Training: AdamW, cosine LR schedule

---

## Experiment Specification

### Dataset

**Dataset**: RedPajama-v2 (English subset)
**Type**: standard (web corpus with quality signals)

**Dataset Details:**
- **Source**: togethercomputer/RedPajama-Data-v2
- **Total Size**: ~30T tokens (using 10B token samples per configuration)
- **Quality Signals Available**: 
  - `ccnet_perplexity` (KenLM 5-gram)
  - Near-duplicate markers
- **Splits**: 
  - Training: 10B tokens per parameter configuration
  - Validation: Held-out subset (0.1%)

**Preprocessing:**
- Tokenization: GPT-2 BPE tokenizer (50257 vocab)
- Sequence length: 1024 tokens
- Filtering: Apply perplexity threshold sweep

**Parameter Sweep Configurations:**
| Config ID | Perplexity Threshold | Dedup Level |
|-----------|---------------------|-------------|
| C0 | None (raw) | None |
| C1 | p10 (bottom 10% removed) | None |
| C2 | p20 | None |
| C3 | p30 | None |
| C4 | p40 | None |
| C5 | p50 | None |
| C6 | p60 | None |
| C7 | p70 | None |
| C8 | p80 | None |
| C9 | p90 (strict) | None |
| D0 | p50 (fixed) | None |
| D1 | p50 | fuzzy_0.7 |
| D2 | p50 | fuzzy_0.85 |
| D3 | p50 | exact |
| D4 | p50 | exact_plus_fuzzy |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: togethercomputer/RedPajama-Data-v2
- Code: 
```python
from datasets import load_dataset
dataset = load_dataset("togethercomputer/RedPajama-Data-v2", 
                       name="default", 
                       split="train",
                       streaming=True)
# Filter by perplexity threshold
filtered = dataset.filter(lambda x: x['ccnet_perplexity'] < threshold)
```

### Models

#### Baseline Model

**Architecture**: GPT-2 125M (decoder-only transformer)
**Type**: Transformer language model

**Configuration:**
- Layers: 12
- Hidden size: 768
- Attention heads: 12
- Parameters: ~125M
- Context length: 1024

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers (config only, train from scratch)
- Identifier: gpt2
- Code:
```python
from transformers import GPT2Config, GPT2LMHeadModel

config = GPT2Config(
    vocab_size=50257,
    n_positions=1024,
    n_embd=768,
    n_layer=12,
    n_head=12,
)
model = GPT2LMHeadModel(config)  # Random init, train from scratch
```

#### Proposed Model

**Architecture:** Same GPT-2 125M architecture across all configurations

**Note:** This is an EXISTENCE hypothesis testing data curation effects, not model architecture changes. The "proposed" condition is training on curated data vs raw data.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Data Curation Parameter Sweep
# Based on: RedPajama pipeline, CCNet methodology

def apply_perplexity_filter(dataset, threshold_percentile):
    """
    Filter dataset by perplexity threshold.
    
    Args:
        dataset: HuggingFace dataset with 'ccnet_perplexity' field
        threshold_percentile: int (0-100), remove bottom X% by quality
    Returns:
        Filtered dataset
    """
    # Compute threshold from percentile
    perplexities = [x['ccnet_perplexity'] for x in dataset]
    threshold = np.percentile(perplexities, threshold_percentile)
    
    # Filter: keep samples with perplexity < threshold (lower = better)
    filtered = dataset.filter(lambda x: x['ccnet_perplexity'] < threshold)
    return filtered

def apply_deduplication(dataset, stringency_level):
    """
    Apply MinHash deduplication with specified stringency.
    
    Args:
        dataset: HuggingFace dataset
        stringency_level: str ('none', 'fuzzy_0.7', 'fuzzy_0.85', 'exact', 'exact_plus_fuzzy')
    Returns:
        Deduplicated dataset
    """
    if stringency_level == 'none':
        return dataset
    
    # MinHash configuration based on stringency
    configs = {
        'fuzzy_0.7': {'threshold': 0.7, 'exact': False},
        'fuzzy_0.85': {'threshold': 0.85, 'exact': False},
        'exact': {'threshold': 1.0, 'exact': True},
        'exact_plus_fuzzy': {'threshold': 0.85, 'exact': True}
    }
    cfg = configs[stringency_level]
    
    # Apply deduplication (using text-dedup library)
    return deduplicate(dataset, **cfg)

# Experiment loop: vary one parameter at a time
```

### Training Protocol

**Optimizer**: AdamW
- Parameters: β1=0.9, β2=0.95, weight_decay=0.1
- Source: GPT-2/GPT-3 standard settings

**Learning Rate**: 6e-4 (peak)
- Source: Chinchilla scaling laws for 125M model

**Schedule**: Cosine decay with linear warmup
- Warmup: 2000 steps (~0.5% of training)
- Min LR: 6e-5 (10% of peak)
- Source: Standard LLM training practice

**Batch Size**: 512 sequences (524k tokens/batch)
- Source: Compute-efficient training literature

**Tokens**: 10B tokens per configuration
- Source: 4x Chinchilla-optimal (2.5B) for signal margin

**Loss Function**: Cross-entropy (next token prediction)

**Seeds**: 1 (fixed seed=42)

> ⚠️ **EXISTENCE (PoC)**: Single seed sufficient for direction detection.

### Evaluation

**Primary Metrics**:
- **Benchmark Ensemble Score**: PC1 of (HellaSwag, ARC-Easy, PIQA, WinoGrande)
- Individual benchmark accuracies for analysis

**Benchmark Details** (from lm-evaluation-harness):
| Benchmark | Type | Samples | Metric |
|-----------|------|---------|--------|
| HellaSwag | Commonsense | 10042 | acc_norm |
| ARC-Easy | Science QA | 2376 | acc |
| PIQA | Physical reasoning | 1838 | acc |
| WinoGrande | Coreference | 1267 | acc |

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: multiple-choice classification
- Library: lm-evaluation-harness
- Code:
```python
from lm_eval import evaluator
results = evaluator.simple_evaluate(
    model="hf",
    model_args=f"pretrained={model_path}",
    tasks=["hellaswag", "arc_easy", "piqa", "winogrande"],
    batch_size=32
)
```

**Analysis Protocol:**
1. Fit polynomial regression (linear, quadratic, cubic) to benchmark vs parameter curves
2. Select model via AIC/BIC
3. If quadratic/cubic selected: identify peak location
4. Report: peak location, confidence interval, effect size

**Success Criteria** (PoC: Direction-based):
- Primary: Quadratic or higher-order model selected over linear (ΔAIC < -2)
- Secondary: Peak identifiable within parameter range (not at boundary)

### Visualization Requirements

#### Required Figure (Mandatory)
- **Dose-Response Curve**: Benchmark ensemble score vs perplexity threshold (with polynomial fit)
- **Deduplication Effect**: Benchmark score vs deduplication stringency

#### Additional Figures (LLM Autonomous)
- Per-benchmark breakdown (4 subplots)
- AIC/BIC model comparison bar chart
- Training loss curves across configurations (if time permits)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error for all 15 configurations
2. Polynomial model selection indicates non-monotonic relationship (AIC prefers quadratic/cubic)
3. At least one parameter dimension shows peak within sweep range

**Mechanism Verification:**
- Pre-condition: RedPajama-v2 quality signals accessible
- Activation indicator: Different token distributions per threshold (log vocabulary coverage)
- Success metric: Quadratic coefficient significant in regression

---

## Appendix: Reference Implementations

### Primary References

1. **RedPajama-v2 Paper & Pipeline**
   - Together AI (2023)
   - Curation methodology, quality signals
   - https://github.com/togethercomputer/RedPajama-Data

2. **DataComp (Image Domain Precedent)**
   - Gadre et al. (2023)
   - Demonstrated dose-response optima exist for curation
   - Methodology transferable to text domain

3. **CCNet / perplexity filtering**
   - Wenzek et al. (2020)
   - KenLM perplexity as quality proxy
   - Standard in C4, RedPajama, Dolma

4. **lm-evaluation-harness**
   - EleutherAI
   - Standard benchmark evaluation
   - https://github.com/EleutherAI/lm-evaluation-harness

### Code Templates

**Perplexity Filtering** (from CCNet/RedPajama):
```python
# Filter by percentile threshold
threshold = np.percentile(perplexities, percentile)
filtered = [doc for doc in docs if doc.perplexity < threshold]
```

**MinHash Deduplication** (from text-dedup):
```python
from text_dedup.minhash import MinHashDeduplicator
dedup = MinHashDeduplicator(threshold=0.85, num_perm=128)
unique_docs = dedup.deduplicate(docs)
```

**Polynomial Regression + Model Selection**:
```python
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
import numpy as np

def fit_and_select(x, y):
    """Fit linear/quadratic/cubic, select via AIC."""
    results = []
    for degree in [1, 2, 3]:
        poly = PolynomialFeatures(degree)
        X_poly = poly.fit_transform(x.reshape(-1, 1))
        model = LinearRegression().fit(X_poly, y)
        y_pred = model.predict(X_poly)
        
        # AIC calculation
        n = len(y)
        k = degree + 1
        rss = np.sum((y - y_pred)**2)
        aic = n * np.log(rss/n) + 2*k
        
        results.append({'degree': degree, 'aic': aic, 'model': model})
    
    # Select model with lowest AIC
    best = min(results, key=lambda x: x['aic'])
    return best
```

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE - state in prompt)
**Date:** 2026-08-28

### Workflow History for This Hypothesis
- 2026-08-28: Phase 2C experiment design initiated
- Status: IN_PROGRESS

---

*MCP Tools Used: None available (ablation mode)*
*All specifications grounded in Phase 2A/2B research and established implementations*
*Next Phase: Phase 3 - Implementation Planning*
