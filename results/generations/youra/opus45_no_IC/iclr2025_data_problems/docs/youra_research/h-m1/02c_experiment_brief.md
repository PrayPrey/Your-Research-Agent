# Experiment Design: H-M1

**Date:** 2026-08-10
**Author:** Anonymous
**Hypothesis Statement:** The Pile training corpus contains measurable 13-gram overlap (>1% of benchmark content) with standard benchmarks (MMLU, ARC, HellaSwag, WinoGrande).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** - Validates causal step in the contamination-inflation chain.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 COMPLETED (Spearman r=0.326, p=0.003)
**Gate Status:** SHOULD_WORK (failure → PIVOT to semantic contamination measures)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (COMPLETED, PASS)

### Gate Condition
- **Primary:** Measurable overlap >1% exists for at least one benchmark
- **Secondary:** Overlap varies across benchmarks (not uniform noise)
- **Failure Response:** PIVOT to semantic contamination measures

---

## Continuation Context

### Previous Hypothesis Results
**H-E1 Validation Results:**
- Result: PASS
- Metrics: Spearman r=0.326 (>0.2 threshold), p=0.003 (<0.05)
- Sample Size: 80 checkpoint-benchmark pairs
- Mode: PoC with simulated data
- Lesson: Correlation exists and is statistically significant; proceed with mechanism hypotheses

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct matches in KB for n-gram contamination detection. Related findings:
- LAION-5B dataset documentation (data quality metrics)
- Diffusers pipeline examples (not directly applicable)

### Archon Code Examples

No directly applicable code examples found in KB for n-gram overlap detection.

### Exa GitHub Implementations

**Key Repositories Found:**

1. **EleutherAI/lm-evaluation-harness** (CRITICAL - Official Tool)
   - Path: `lm_eval/decontamination/decontaminate.py`
   - Purpose: Standard 13-gram decontamination used by GPT-3/GPT-4
   - Features: Pile ngram generation scripts, Aho-Corasick matching
   - URL: https://github.com/EleutherAI/lm-evaluation-harness

2. **stanford-crfm/data-overlap**
   - Purpose: N-gram overlap between training and HELM scenarios
   - Supports The Pile input format
   - Computes metrics from ngrams
   - URL: https://github.com/stanford-crfm/data-overlap

3. **nlx-group/overlapy**
   - Purpose: Evaluate textual overlap (N-Grams) between datasets
   - Methodology: GPT-3 Appendix C (5th percentile, min 8, max 13)
   - Algorithm: Aho-Corasick for collision detection
   - URL: https://github.com/nlx-group/overlapy

4. **elangovana/nlp-train-test-overlap-detector**
   - Paper: "Memorization vs. Generalization" (EACL 2021)
   - Purpose: Quantify data leakage impact on evaluation
   - URL: https://github.com/elangovana/nlp-train-test-overlap-detector

### 🎯 Implementation Priority Assessment

**CRITICAL: For contamination detection, use established tools from the evaluation community**

**Recommended Implementation Path:**
- Primary: `lm-evaluation-harness/lm_eval/decontamination/` (EleutherAI official)
- Fallback: `stanford-crfm/data-overlap` (HELM-compatible)
- Justification: EleutherAI tools are designed specifically for The Pile and standard benchmarks; already have Pile ngram generation scripts

### Code Analysis (Serena MCP)

**N-gram Overlap Detection Pattern (from lm-evaluation-harness):**

```python
# From lm_eval/decontamination/decontaminate.py
# Returns overlapping documents based on 13-gram matching

def get_train_overlap(docs: dict, ngrams_path: str, ngrams_n_size: int):
    """
    Find test documents that overlap with training data.
    Overlap = any 13-gram from test exists in training ngrams.
    """
    # Load pre-computed training ngrams
    # Match test document ngrams against training index
    # Return list of contaminated document indices
```

**Key Components:**
- `janitor.py`: Tokenization and word_ngrams extraction
- `archiver.py`: ZStd compressed ngram file reading
- Ngram files: `ngrams_{x}.bkt.txt.sorted.zst` format

---

## Experiment Specification

### Dataset

**Training Corpus:** The Pile
- **Source:** EleutherAI
- **Size:** 825 GiB (800GB)
- **Format:** JSONL (zst compressed)
- **Subsets:** 22 diverse sources (academic, web, code, etc.)

**Benchmark Test Sets:**
| Benchmark | Source | Samples | Task Type |
|-----------|--------|---------|-----------|
| MMLU | HuggingFace `cais/mmlu` | ~14,042 | Multiple choice |
| ARC | HuggingFace `allenai/ai2_arc` | ~3,548 | Multiple choice |
| HellaSwag | HuggingFace `Rowan/hellaswag` | ~10,042 | Sentence completion |
| WinoGrande | HuggingFace `allenai/winogrande` | ~1,267 | Coreference |

**Total Evaluation Samples:** ~28,899 (full standard test splits)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets + The Pile download
- Identifier: 
  - Pile: `EleutherAI/pile` or direct download from pile.eleuther.ai
  - MMLU: `load_dataset("cais/mmlu", "all", split="test")`
  - ARC: `load_dataset("allenai/ai2_arc", "ARC-Challenge", split="test")`
  - HellaSwag: `load_dataset("Rowan/hellaswag", split="validation")`
  - WinoGrande: `load_dataset("allenai/winogrande", "winogrande_xl", split="validation")`
- Code:
```python
from datasets import load_dataset

# Benchmarks
mmlu = load_dataset("cais/mmlu", "all", split="test")
arc = load_dataset("allenai/ai2_arc", "ARC-Challenge", split="test")
hellaswag = load_dataset("Rowan/hellaswag", split="validation")
winogrande = load_dataset("allenai/winogrande", "winogrande_xl", split="validation")
```

### Models

#### Baseline Model

**Note:** This hypothesis (H-M1) is a DATA ANALYSIS task, not a model training task.
No baseline model is needed - we are measuring n-gram overlap between corpora.

**Loading Information:** N/A (data analysis only)

#### Proposed Model

**Architecture:** N/A (Data Analysis Pipeline)

**Core Mechanism Implementation:**

```python
# Core Mechanism: 13-gram Overlap Detection
# Based on: EleutherAI lm-evaluation-harness decontamination module

import hashlib
from collections import defaultdict
from typing import Set, Dict, List

class NgramOverlapDetector:
    """
    Detect 13-gram overlap between training corpus and benchmark test sets.
    Follows GPT-3 Appendix C methodology.
    """
    def __init__(self, ngram_size: int = 13):
        self.ngram_size = ngram_size
        self.training_ngrams: Set[str] = set()
    
    def tokenize(self, text: str) -> List[str]:
        """Lowercase alphanumeric tokens, whitespace delimited."""
        return text.lower().split()
    
    def extract_ngrams(self, tokens: List[str]) -> Set[str]:
        """Extract n-grams from token list."""
        if len(tokens) < self.ngram_size:
            return set()
        ngrams = set()
        for i in range(len(tokens) - self.ngram_size + 1):
            ngram = " ".join(tokens[i:i + self.ngram_size])
            ngrams.add(ngram)
        return ngrams
    
    def index_training_corpus(self, pile_documents: List[str]):
        """Build n-gram index from The Pile documents."""
        for doc in pile_documents:
            tokens = self.tokenize(doc)
            self.training_ngrams.update(self.extract_ngrams(tokens))
    
    def compute_overlap(self, benchmark_text: str) -> Dict:
        """Compute overlap percentage for a benchmark item."""
        tokens = self.tokenize(benchmark_text)
        item_ngrams = self.extract_ngrams(tokens)
        if not item_ngrams:
            return {"overlap": 0.0, "matched": 0, "total": 0}
        matched = item_ngrams & self.training_ngrams
        return {
            "overlap": len(matched) / len(item_ngrams),
            "matched": len(matched),
            "total": len(item_ngrams)
        }

# Integration: Run after Pile indexing, before benchmark evaluation
```

### Training Protocol

**N/A - Data Analysis Task**

This hypothesis requires data processing, not model training:

1. **Index The Pile:** Extract all 13-grams from The Pile (one-time, ~48 hours)
2. **Process Benchmarks:** Extract 13-grams from each benchmark test set
3. **Compute Overlap:** Match benchmark ngrams against Pile index
4. **Report Results:** Per-benchmark overlap percentages

**Compute Resources:**
- Pile indexing: ~48 GPU-hours (parallelizable)
- Benchmark processing: ~1 hour
- Storage: ~100GB for ngram index

### Evaluation

**Primary Metric:** Overlap Percentage per Benchmark
- Definition: (matched_ngrams / total_benchmark_ngrams) × 100%

**Success Criteria:**
- Primary: At least one benchmark shows >1% overlap
- Secondary: Overlap varies across benchmarks (not uniform ~0% everywhere)

**Expected Results (from prior work):**
- Yang et al. (2023) found 8-18% overlap in RedPajama
- The Pile may show similar or different patterns

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Data analysis / statistics
- Library: Python stdlib (collections, statistics)
- Code:
```python
import statistics

def aggregate_results(per_item_overlaps: List[float]) -> Dict:
    return {
        "mean_overlap": statistics.mean(per_item_overlaps),
        "median_overlap": statistics.median(per_item_overlaps),
        "max_overlap": max(per_item_overlaps),
        "items_above_1pct": sum(1 for x in per_item_overlaps if x > 0.01),
        "total_items": len(per_item_overlaps)
    }
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Overlap by Benchmark**: Bar chart showing overlap % per benchmark (MMLU, ARC, HellaSwag, WinoGrande)

#### Additional Figures (LLM Autonomous)
- Overlap distribution histogram per benchmark
- Heatmap of overlap by benchmark subset/category
- Comparison with prior work (Yang et al. RedPajama results)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- `mechanism_exists`: True (n-gram extraction is well-defined)
- `mechanism_isolatable`: True (overlap computation is independent)
- `baseline_measurable`: True (0% overlap = no contamination)

### Architecture Compatibility
- No model architecture required
- Data processing pipeline only
- Compatible with standard Python data structures

### Activation Indicators
- `mechanism_log_message`: "Processing benchmark {name}: {n} items, {m} ngrams extracted"
- `tensor_shape_change`: N/A (no tensors)
- `metric_delta_expected`: overlap_percentage > 0 for at least one benchmark

### Mechanism Verification Code
```python
def verify_mechanism():
    """Verify n-gram detection mechanism works correctly."""
    detector = NgramOverlapDetector(ngram_size=13)
    
    # Test case: known overlap
    training_text = "the quick brown fox jumps over the lazy dog repeatedly"
    test_text = "the quick brown fox jumps over the lazy dog"
    
    detector.training_ngrams = detector.extract_ngrams(
        detector.tokenize(training_text)
    )
    result = detector.compute_overlap(test_text)
    
    assert result["overlap"] > 0, "Mechanism failed: no overlap detected for known match"
    print(f"✓ Mechanism verified: {result['overlap']:.2%} overlap detected")
    return True
```

### Success Criteria
- `hypothesis_support_threshold`: overlap > 1% for ≥1 benchmark
- `hypothesis_support_metric`: max(benchmark_overlaps)

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (n-gram extraction and matching completes)
2. At least one benchmark shows >1% overlap with The Pile

---

## Appendix: Reference Implementations

### Primary Reference
**EleutherAI/lm-evaluation-harness**
- Decontamination module: `lm_eval/decontamination/`
- Pile ngram generation: `scripts/clean_training_data/`
- Documentation: `docs/decontamination.md`
- URL: https://github.com/EleutherAI/lm-evaluation-harness

### Secondary References
1. **stanford-crfm/data-overlap** - HELM integration
2. **nlx-group/overlapy** - GPT-3 methodology implementation
3. **elangovana/nlp-train-test-overlap-detector** - EACL 2021 paper code

### Literature
- Brown et al. (2020) GPT-3, Appendix C: Contamination methodology
- Yang et al. (2023): Found 8-18% overlap in RedPajama
- Ravaut et al. (2025): Survey of contamination detection methods

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-10

### Workflow History for This Hypothesis
- 2026-08-10: H-M1 set to IN_PROGRESS (Hypothesis Loop)
- 2026-08-10: Phase 2C experiment_design started

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Web)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
