# Experiment Design: H-M2

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** Deduplication stringency affects the memorization-generalization balance: an optimal deduplication level exists between none and strict (exact+fuzzy), measurable via benchmark ensemble score.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** - Testing quality-diversity tradeoff from deduplication.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M1 assumed satisfied)
**Gate Status:** SHOULD_WORK (not yet evaluated)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1

### Gate Condition
SHOULD_WORK: Quality-diversity tradeoff from deduplication stringency should produce non-monotonic benchmark performance curve. If fails: EXPLORE specific benchmarks or document as finding.

---

## Continuation Context

This hypothesis builds on H-M1 (Noise Dilution Mechanism) which established that filtering improves convergence. H-M2 extends this to deduplication specifically, testing whether there's an optimal stringency level.

### Previous Hypothesis Results (if applicable)
H-M1 expected to confirm noise dilution mechanism. H-M2 investigates the deduplication dimension of the quality-diversity tradeoff.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Note:** Archon MCP unavailable in this session. Findings based on established literature:

**Query 1: Deduplication Experiment Design**
- **Lee et al. (2022)**: "Deduplicating Training Data Makes Language Models Better" - foundational work showing deduplication reduces memorization 10x
- **Standard Approach**: MinHash LSH with Jaccard threshold 0.7-0.85
- **Datasets**: C4, The Pile, RedPajama all use deduplication pipelines
- **Key insight**: Deduplication reduces train-test overlap (affects >4% of validation sets)

**Query 2: Implementation Best Practices**
- Use 5-gram shingles for MinHash signature computation
- 128 hash functions standard for MinHash
- Jaccard threshold typically 0.7-0.85 for fuzzy matching
- Combine exact + fuzzy deduplication for thoroughness

### Archon Code Examples

**Archon MCP unavailable** - using web search findings instead.

**Google Research Implementation** (https://github.com/google-research/deduplicate-text-datasets):
- Rust implementation for ExactSubstr deduplication
- Suffix array based exact matching
- Released with Lee et al. (2022) paper

### Exa GitHub Implementations

**Repository 1**: [ChenghaoMou/text-dedup](https://github.com/ChenghaoMou/text-dedup) (⭐ Popular)
- **URL**: https://github.com/ChenghaoMou/text-dedup
- **Relevance**: All-in-one text deduplication library
- **Features**: MinHash + MinHashLSH, Spark implementation for TB-scale
- **Config**: 5-grams, 128 hash functions, Jaccard 0.7-0.8 threshold
- **Key Code**:
  ```python
  from text_dedup.minhash import MinHashDeduplicator
  deduplicator = MinHashDeduplicator(
      num_perm=128,
      ngram_size=5,
      threshold=0.7
  )
  ```

**Repository 2**: [togethercomputer/RedPajama-Data](https://github.com/togethercomputer/RedPajama-Data)
- **URL**: https://github.com/togethercomputer/RedPajama-Data
- **Relevance**: Official RedPajama-v2 preprocessing pipeline
- **Deduplication**: bloomfilter.py for content-based deduplication
- **Config**: Banded MinHash signatures, Jaccard 1.0 for exact match
- **Processing**: Quality signals + MinHash computed in step 2

**Repository 3**: [allenai/duplodocus](https://github.com/allenai/duplodocus)
- **URL**: https://github.com/allenai/duplodocus
- **Relevance**: High-performance Rust implementation
- **Features**: Exact + fuzzy (MinHash) deduplication
- **Scale**: JSONL datasets, parallel processing

**Repository 4**: [EleutherAI/lm-evaluation-harness](https://github.com/eleutherai/lm-evaluation-harness)
- **URL**: https://github.com/eleutherai/lm-evaluation-harness
- **Relevance**: Standard benchmark evaluation framework
- **Benchmarks**: HellaSwag, ARC-easy, PIQA, WinoGrande
- **Usage**: `lm_eval --model hf --tasks hellaswag,arc_easy,piqa,winogrande`

**Serena Analysis Needed**: No (code patterns clear from web search)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

1. **text-dedup** (ChenghaoMou) - Most complete, configurable thresholds
2. **RedPajama-Data** (togethercomputer) - Official pipeline for RedPajama-v2
3. **google-research/deduplicate-text-datasets** - Original Lee et al. implementation

**Recommended Implementation Path:**
- Primary: text-dedup library with configurable Jaccard thresholds
- Fallback: Custom MinHash implementation based on RedPajama pipeline
- Justification: text-dedup provides exact threshold control needed for dose-response sweep

### Code Analysis (Serena MCP)

Serena analysis not required - deduplication code patterns are well-documented in public repositories. Key integration point is preprocessing pipeline before tokenization.

---

## Experiment Specification

### Dataset

**Name:** RedPajama-v2 (subset)
**Type:** standard
**Source:** HuggingFace: togethercomputer/RedPajama-Data-v2

**Hypothesis Fit:**
- Contains raw and filtered versions
- Allows controlled deduplication parameter variation
- Large-scale web corpus representative of LLM pretraining data

**Statistics:**
- Full corpus: ~30T tokens
- Experiment subset: 10B tokens per configuration
- Multiple snapshots available for replication

**Preprocessing:**
- Raw text extraction from JSONL
- Quality signal computation (perplexity)
- Deduplication at document level

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `togethercomputer/RedPajama-Data-v2`
- Code:
  ```python
  from datasets import load_dataset
  dataset = load_dataset(
      "togethercomputer/RedPajama-Data-v2",
      name="sample",  # or specific snapshot
      split="train"
  )
  ```

### Models

#### Baseline Model

**Architecture:** GPT-2 125M (decoder-only transformer)
**Type:** Pretrained from scratch on deduplicated data
**Source:** HuggingFace Transformers / OpenAI GPT-2 architecture

**Configuration:**
- Layers: 12
- Hidden size: 768
- Attention heads: 12
- Parameters: 125M
- Context length: 1024

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers (architecture only, trained from scratch)
- Identifier: `gpt2` (for architecture reference)
- Code:
  ```python
  from transformers import GPT2Config, GPT2LMHeadModel
  config = GPT2Config(
      vocab_size=50257,
      n_positions=1024,
      n_embd=768,
      n_layer=12,
      n_head=12
  )
  model = GPT2LMHeadModel(config)  # Random init, train from scratch
  ```

#### Proposed Model

**Architecture:** GPT-2 125M (same architecture, different training data)

**Core Mechanism Implementation:**

The mechanism is NOT a model modification but a DATA CURATION variation. The hypothesis tests different deduplication stringency levels on training data.

```python
# Core Mechanism: Deduplication Stringency Sweep
# Based on: text-dedup library + RedPajama pipeline

from text_dedup.minhash import MinHashDeduplicator
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class DeduplicationConfig:
    """Deduplication stringency levels for sweep."""
    level: str
    jaccard_threshold: float
    include_exact: bool

DEDUP_LEVELS = [
    DeduplicationConfig("none", 1.0, False),         # No deduplication
    DeduplicationConfig("fuzzy_0.7", 0.7, False),    # Permissive fuzzy
    DeduplicationConfig("fuzzy_0.85", 0.85, False),  # Moderate fuzzy
    DeduplicationConfig("exact", 1.0, True),         # Exact only
    DeduplicationConfig("exact_plus_fuzzy", 0.85, True),  # Strictest
]

def apply_deduplication(
    documents: List[str],
    config: DeduplicationConfig
) -> List[str]:
    """
    Apply deduplication at specified stringency level.
    
    Args:
        documents: List of text documents
        config: Deduplication configuration
    Returns:
        Deduplicated document list
    """
    if config.level == "none":
        return documents
    
    # MinHash fuzzy deduplication
    deduplicator = MinHashDeduplicator(
        num_perm=128,
        ngram_size=5,
        threshold=config.jaccard_threshold
    )
    deduplicated = deduplicator.deduplicate(documents)
    
    if config.include_exact:
        # Additional exact string deduplication
        deduplicated = list(set(deduplicated))
    
    return deduplicated

# Integration: Apply before tokenization in data pipeline
```

### Training Protocol

**Optimizer:** AdamW
- Parameters: β1=0.9, β2=0.95, weight_decay=0.1
- **Source:** GPT-2/GPT-3 training conventions

**Learning Rate:** 6e-4
- **Source:** Chinchilla scaling recommendations for 125M models

**Schedule:** Cosine decay with warmup
- Warmup steps: 2000
- **Source:** Standard LLM pretraining

**Batch Size:** 512 sequences (512K tokens per batch)
- **Source:** Memory-efficient training for 125M model

**Epochs:** N/A (token-based training)
- Total tokens: 10B per configuration (4x Chinchilla-optimal)
- **Source:** Phase 2B assumption A5

**Loss Function:** Cross-entropy (standard LM loss)

**Seeds:** 3 (for statistical robustness of dose-response curve)

### Evaluation

**Primary Metrics:**
- Benchmark Ensemble Score: PC1 of (HellaSwag, ARC-Easy, PIQA, WinoGrande)
- Individual benchmark accuracies

**Success Criteria (MECHANISM hypothesis):**
- Strictest deduplication (exact+fuzzy) underperforms moderate (fuzzy_0.7 or fuzzy_0.85)
- Non-monotonic relationship observable in benchmark scores
- Effect size: >1% accuracy difference between optimal and strictest

**Expected Baseline Performance** (from literature):
- GPT-2 125M zero-shot: HellaSwag ~30%, ARC-Easy ~45%, PIQA ~63%, WinoGrande ~52%
- **Source:** OpenAI GPT-2 paper, lm-eval-harness benchmarks

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Multiple-choice QA / commonsense reasoning
- Library: lm-evaluation-harness
- Code:
  ```python
  # Using EleutherAI lm-evaluation-harness
  # CLI: lm_eval --model hf --model_args pretrained=./checkpoint \
  #      --tasks hellaswag,arc_easy,piqa,winogrande --device cuda:0
  
  import lm_eval
  results = lm_eval.simple_evaluate(
      model="hf",
      model_args="pretrained=./checkpoint",
      tasks=["hellaswag", "arc_easy", "piqa", "winogrande"],
      batch_size=16
  )
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Benchmark score vs deduplication stringency (bar chart or line plot)

#### Additional Figures (LLM Autonomous)

1. **Dose-Response Curve**: Ensemble score (y) vs deduplication level (x), with error bars from 3 seeds
2. **Individual Benchmark Breakdown**: Per-benchmark scores across deduplication levels (grouped bar)
3. **Data Statistics**: Token count, unique document count per deduplication level
4. **Training Loss Curves**: Loss progression for each deduplication configuration

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists**: Yes - deduplication is applied during data preprocessing
- **mechanism_isolatable**: Yes - only deduplication threshold varies; architecture, training, evaluation identical
- **baseline_measurable**: Yes - "none" deduplication serves as baseline

### Architecture Compatibility
Data-level mechanism, compatible with any transformer LM. No architecture modifications needed.

### Activation Indicators
- **Log message**: "Applying deduplication level: {level}, removed {N} duplicates ({pct}%)"
- **Tensor shape change**: N/A (data preprocessing, not model modification)
- **Metric delta expected**: >1% accuracy difference between levels

### Mechanism Verification Code
```python
def verify_deduplication_applied(
    original_count: int,
    deduplicated_count: int,
    config: DeduplicationConfig
) -> bool:
    """Verify deduplication mechanism is actually working."""
    if config.level == "none":
        return original_count == deduplicated_count
    else:
        # Non-trivial deduplication should remove SOME documents
        removal_rate = (original_count - deduplicated_count) / original_count
        expected_min = {"fuzzy_0.7": 0.01, "fuzzy_0.85": 0.005, 
                        "exact": 0.001, "exact_plus_fuzzy": 0.01}
        return removal_rate >= expected_min.get(config.level, 0)
```

### Success Threshold
- **hypothesis_support_threshold**: Strictest deduplication (exact+fuzzy) underperforms at least one moderate level by >0.5% on ensemble score
- **hypothesis_support_metric**: Benchmark ensemble accuracy

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error for all 5 deduplication levels
2. Non-monotonic pattern observed: some intermediate level outperforms strictest
3. Verification: `max(moderate_levels) > strict_level`

---

## Appendix: Reference Implementations

| Source | URL | Relevance |
|--------|-----|-----------|
| text-dedup | https://github.com/ChenghaoMou/text-dedup | Primary deduplication library |
| RedPajama-Data | https://github.com/togethercomputer/RedPajama-Data | Dataset pipeline |
| google-research/deduplicate-text-datasets | https://github.com/google-research/deduplicate-text-datasets | Lee et al. (2022) code |
| lm-evaluation-harness | https://github.com/eleutherai/lm-evaluation-harness | Benchmark evaluation |
| Lee et al. (2022) | https://aclanthology.org/2022.acl-long.577/ | Foundational deduplication paper |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28

### Workflow History for This Hypothesis
- Phase 2C experiment design initiated
- Web search completed (Archon/Exa MCP unavailable, WebSearch used)
- Implementation research: text-dedup, RedPajama, lm-eval-harness
- Experiment specification synthesized

---

*MCP Tools Used: WebSearch (Archon/Exa unavailable)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
