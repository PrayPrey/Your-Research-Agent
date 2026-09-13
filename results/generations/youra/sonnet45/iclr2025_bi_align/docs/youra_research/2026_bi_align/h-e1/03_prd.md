---
name: Product Requirements Document
type: prd
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
created_at: 2026-03-17
version: 1.0
stepsCompleted: ['requirements', 'data_spec', 'metrics', 'dependencies']
---

# Product Requirements Document: H-E1 Linguistic Marker Extraction

**Hypothesis:** Under HH-RLHF dataset conditions (161K preference pairs), if linguistic agency markers (modal verbs, hedging, alternative-framing) are extracted using standard NLP tools (spaCy, NLTK, regex), then these markers will demonstrate sufficient distributional variance (CV > 0.3) and measurement reliability across all three dataset splits.

**Gate Type:** MUST_WORK
**Prerequisites:** None (foundation hypothesis)

---

## Executive Summary

This PRD defines requirements for implementing a linguistic marker extraction and analysis system to validate the existence and measurability of agency-preserving linguistic features in RLHF preference data. The system will extract three types of linguistic markers (modal verbs, hedging language, alternative-framing phrases) from 161K HH-RLHF preference pairs and compute distributional statistics to determine if sufficient variance exists for downstream correlation analysis.

**Success Criteria:** Modal verb coefficient of variation (CV) > 0.3 AND extraction precision > 90%

---

## Problem Statement

Current RLHF evaluation focuses exclusively on AI-side metrics (helpfulness, harmlessness) with no computational operationalization of human agency preservation. Before testing whether linguistic markers correlate with preference outcomes (H-M-integrated), we must first establish that these markers:

1. Exist with sufficient distributional variance in RLHF data
2. Can be reliably extracted using computational methods
3. Show consistent measurement properties across dataset splits

**This is a measurement validation study, NOT a model training experiment.**

---

## Functional Requirements

### FR1: Dataset Loading and Preprocessing

**Priority:** P0 (Critical)

**Description:** Load HH-RLHF dataset from HuggingFace and prepare text for linguistic analysis.

**Acceptance Criteria:**
- Load all 3 splits: helpful-base (train), helpful-online (test), helpful-rejection-sampled
- Extract ~322K individual responses (161K chosen + 161K rejected)
- Remove special tokens (Human:, Assistant:) while preserving linguistic content
- Calculate word counts for per-100-words normalization
- Verify total sample count matches expected ~322K responses

**Data Specification:**
```python
from datasets import load_dataset

# Load splits
dataset_base = load_dataset("Anthropic/hh-rlhf", split="train")  # ~88K pairs
dataset_online = load_dataset("Anthropic/hh-rlhf", split="test")  # ~43K pairs
dataset_rs = load_dataset("Anthropic/hh-rlhf",
                          data_files="helpful-rejection-sampled/train.jsonl")  # ~30K pairs

# Access structure
sample = dataset_base[0]
chosen_text = sample['chosen']  # Human-preferred response
rejected_text = sample['rejected']  # Human-rejected response
prompt = sample['prompt']  # Conversation context
```

**Dependencies:**
- `datasets` library (HuggingFace)
- Internet connection for initial download
- ~2GB disk space for cached dataset

---

### FR2: Modal Verb Extraction

**Priority:** P0 (Critical)

**Description:** Extract modal verbs (can, could, may, might, should, would, etc.) from response text using spaCy POS tagging.

**Acceptance Criteria:**
- Detect all modal verbs via POS tag MD (Modal Auxiliary)
- Normalize counts to per-100-words frequency
- Handle edge cases (word_count = 0)
- Store per-sample frequencies for statistical analysis

**Implementation Specification:**
```python
import spacy

nlp = spacy.load("en_core_web_sm")

def extract_modal_verbs(text):
    doc = nlp(text)
    word_count = len([token for token in doc if token.is_alpha])
    modal_verbs = [token for token in doc if token.tag_ == 'MD']
    modal_freq = (len(modal_verbs) / word_count * 100) if word_count > 0 else 0
    return modal_freq
```

**Dependencies:**
- spaCy library (`pip install spacy`)
- English model: `python -m spacy download en_core_web_sm`

---

### FR3: Hedging Marker Extraction

**Priority:** P0 (Critical)

**Description:** Extract hedging language (perhaps, maybe, might, possibly, etc.) using custom lexicon-based matching.

**Acceptance Criteria:**
- Match hedging terms via case-insensitive word lookup
- Use comprehensive hedging lexicon (15+ terms)
- Normalize counts to per-100-words frequency
- Store per-sample frequencies for statistical analysis

**Implementation Specification:**
```python
HEDGING_MARKERS = {
    'perhaps', 'maybe', 'might', 'could', 'possibly',
    'probably', 'likely', 'seems', 'appears', 'suggests',
    'tend', 'often', 'sometimes', 'generally', 'typically'
}

def extract_hedging(text):
    text_lower = text.lower()
    words = text_lower.split()
    word_count = len([w for w in words if w.isalpha()])
    hedging_count = sum(1 for marker in HEDGING_MARKERS if marker in words)
    hedging_freq = (hedging_count / word_count * 100) if word_count > 0 else 0
    return hedging_freq
```

**Dependencies:**
- Standard Python libraries (no external dependencies)

---

### FR4: Alternative-Framing Phrase Extraction

**Priority:** P0 (Critical)

**Description:** Extract alternative-framing phrases ("you could", "one option", "alternatively") using regex pattern matching.

**Acceptance Criteria:**
- Match 5+ alternative-framing patterns
- Use case-insensitive regex with word boundaries
- Normalize counts to per-100-words frequency
- Store per-sample frequencies for statistical analysis

**Implementation Specification:**
```python
import re

ALT_PATTERNS = [
    r'\byou (could|might|may)\b',
    r'\b(one|another) (option|approach|alternative|way)\b',
    r'\balternatively\b',
    r'\bon the other hand\b',
    r'\byou (can|have) the option\b'
]

def extract_alternatives(text):
    word_count = len([w for w in text.split() if w.isalpha()])
    alt_count = sum(len(re.findall(pattern, text, re.IGNORECASE))
                    for pattern in ALT_PATTERNS)
    alt_freq = (alt_count / word_count * 100) if word_count > 0 else 0
    return alt_freq
```

**Dependencies:**
- Standard Python `re` library

---

### FR5: Statistical Analysis and Metrics Computation

**Priority:** P0 (Critical)

**Description:** Compute distributional statistics (mean, SD, CV) for all three marker types across all dataset splits.

**Acceptance Criteria:**
- Compute per-marker statistics: mean, standard deviation, coefficient of variation
- Perform per-split analysis for cross-validation
- Verify gate condition: Modal verb CV > 0.3
- Generate summary statistics table

**Implementation Specification:**
```python
import numpy as np
import pandas as pd

def compute_statistics(features):
    """
    Args:
        features: np.array of per-sample frequencies
    Returns:
        dict with mean, std, cv, min, max, median
    """
    return {
        'mean': np.mean(features),
        'std': np.std(features),
        'cv': np.std(features) / np.mean(features) if np.mean(features) > 0 else 0,
        'min': np.min(features),
        'max': np.max(features),
        'median': np.median(features)
    }

# Per-split validation
for split_name, split_data in splits.items():
    modal_stats = compute_statistics(split_data['modal_freq'])
    hedging_stats = compute_statistics(split_data['hedging_freq'])
    alt_stats = compute_statistics(split_data['alternative_freq'])
```

**Dependencies:**
- NumPy
- Pandas
- SciPy (optional, for advanced statistical tests)

---

### FR6: Extraction Precision Validation

**Priority:** P1 (High)

**Description:** Manual validation of extraction accuracy on 100-sample subset to verify precision > 90%.

**Acceptance Criteria:**
- Random sample 100 responses from dataset
- Human annotator manually counts modal verbs, hedging markers, alternatives
- Compute precision = (true positives) / (true positives + false positives)
- Compute recall = (true positives) / (true positives + false negatives)
- Generate validation report with per-marker accuracy

**Implementation Specification:**
```python
# Sample selection
validation_samples = random.sample(all_responses, 100)

# Manual annotation schema
validation_schema = {
    'sample_id': int,
    'text': str,
    'automated_modal_count': int,
    'manual_modal_count': int,
    'automated_hedging_count': int,
    'manual_hedging_count': int,
    'automated_alt_count': int,
    'manual_alt_count': int
}

# Precision calculation
precision = correct_extractions / (correct_extractions + false_positives)
recall = correct_extractions / (correct_extractions + false_negatives)
```

**Dependencies:**
- Human annotator (manual step)
- CSV file for validation data export

---

### FR7: Visualization Generation

**Priority:** P1 (High)

**Description:** Generate required and recommended visualizations for distributional analysis.

**Acceptance Criteria:**
- **MANDATORY:** Gate metrics comparison bar chart (target vs actual CV)
- Histogram of modal verb frequencies with mean/SD overlay
- Box plots by split for cross-validation
- Scatter plot: modal vs hedging frequencies (convergent validity)
- Summary statistics table
- Save all figures to `{hypothesis_folder}/figures/`

**Implementation Specification:**
```python
import matplotlib.pyplot as plt
import seaborn as sns

# Figure 1: Gate metrics (MANDATORY)
fig, ax = plt.subplots(1, 1, figsize=(8, 6))
metrics = ['Modal CV', 'Hedging CV', 'Alt CV', 'Precision']
targets = [0.3, 0.2, 0.2, 0.9]
actuals = [actual_modal_cv, actual_hedging_cv, actual_alt_cv, actual_precision]
# Bar chart implementation...
plt.savefig(f'{hypothesis_folder}/figures/gate_metrics.png', dpi=300)

# Figure 2: Distribution histogram
# Figure 3: Box plots by split
# Figure 4: Correlation scatter plot
```

**Dependencies:**
- Matplotlib
- Seaborn
- NumPy

---

### FR8: Results Reporting

**Priority:** P0 (Critical)

**Description:** Generate comprehensive results report with gate validation decision.

**Acceptance Criteria:**
- Summary statistics for all three marker types
- Per-split breakdown
- Gate condition evaluation (PASS/FAIL)
- Validation precision scores
- Figure references
- Save report to `{hypothesis_folder}/04_validation.md`

**Implementation Specification:**
```markdown
# H-E1 Validation Report

## Gate Condition Results

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Modal Verb CV | > 0.3 | 0.XX | PASS/FAIL |
| Extraction Precision | > 90% | XX% | PASS/FAIL |

**Gate Decision:** PASS/FAIL

## Distributional Statistics

### Modal Verbs
- Mean: X.XX per 100 words
- SD: X.XX
- CV: X.XX

[Additional statistics...]

## Cross-Split Validation
[Per-split results...]

## Figures
- Figure 1: Gate metrics comparison
- Figure 2: Distribution histogram
- Figure 3: Cross-split box plots
- Figure 4: Marker correlation
```

**Dependencies:**
- Python string formatting or Jinja2 templates

---

## Non-Functional Requirements

### NFR1: Performance

**Requirement:** Complete full dataset processing within 60 minutes on CPU.

**Rationale:** 322K texts with spaCy processing = ~30-60 min on modern CPU

**Acceptance Criteria:**
- Batch processing with progress logging
- Efficient text preprocessing (single pass)
- No GPU required

---

### NFR2: Reproducibility

**Requirement:** Deterministic extraction with fixed random seeds.

**Acceptance Criteria:**
- Set random seed for validation sample selection
- Document spaCy model version
- Pin all library versions in requirements.txt

**Implementation:**
```python
import random
import numpy as np

random.seed(42)
np.random.seed(42)
```

---

### NFR3: Code Organization (LIGHT Infrastructure)

**Requirement:** Minimal infrastructure appropriate for EXISTENCE hypothesis.

**Acceptance Criteria:**
- Single script or notebook implementation acceptable
- Hardcoded configuration or argparse CLI
- Simple print() statements + CSV logging sufficient
- Smoke test (sanity check) for validation
- No complex testing framework required

**Rationale:** LIGHT tier = minimal infrastructure (per task budget allocation)

---

### NFR4: Data Storage

**Requirement:** Store intermediate results for downstream analysis.

**Acceptance Criteria:**
- Save extracted features to CSV: `{hypothesis_folder}/h_e1_features.csv`
- Columns: sample_id, split, response_type (chosen/rejected), modal_freq, hedging_freq, alt_freq, word_count
- Save statistics to JSON: `{hypothesis_folder}/h_e1_statistics.json`

---

## Success Criteria

### Primary Success Criteria

1. **Modal Verb CV > 0.3** - Sufficient distributional variance for correlation analysis
2. **Extraction Precision > 90%** - Reliable automated measurement

**Gate Decision Logic:**
```python
if modal_cv > 0.3 and precision > 0.9:
    gate_result = "PASS"
else:
    gate_result = "FAIL"
```

### Secondary Success Criteria

- Hedging CV > 0.2 (convergent evidence)
- Alternative-framing CV > 0.2 (convergent evidence)
- Measurement consistency across splits (CVs within ±0.05)

---

## Dependencies and Environment

### Python Libraries

```txt
# Core dependencies
datasets>=2.14.0  # HuggingFace datasets
spacy>=3.5.0     # NLP processing
numpy>=1.24.0    # Statistical computation
pandas>=2.0.0    # Data manipulation
matplotlib>=3.7.0 # Visualization
seaborn>=0.12.0  # Statistical plots

# Optional
scipy>=1.10.0    # Advanced statistics
```

### External Resources

- **spaCy Model:** `en_core_web_sm` (download: `python -m spacy download en_core_web_sm`)
- **Dataset:** `Anthropic/hh-rlhf` (HuggingFace, auto-download)
- **Disk Space:** ~2GB for dataset cache + ~100MB for results
- **Runtime:** 30-60 minutes on CPU

### Hardware Requirements

- **CPU:** Modern multi-core processor (4+ cores recommended)
- **RAM:** 8GB minimum, 16GB recommended
- **GPU:** Not required
- **Storage:** 3GB free space

---

## Out of Scope

The following are explicitly OUT OF SCOPE for this hypothesis:

1. **Model Training:** No neural models - this is a measurement study
2. **Correlation Analysis:** Deferred to H-M-integrated hypothesis
3. **Causal Claims:** Only distributional measurement, no mechanism testing
4. **Other Datasets:** HH-RLHF only (generalization testing in future work)
5. **Advanced NLP:** No transformers, embeddings, or deep learning methods
6. **Baseline Comparison:** Not applicable (no competing measurement methods)

---

## Implementation Notes

### Experiment Type Classification

- **Type:** `linguistic_analysis` (measurement study)
- **NOT:** `model_training`, `baseline_comparison`, or `ablation_study`
- **Implication:** No model checkpoints, no training logs, no baseline repositories

### Task Budget Allocation

- **Total Tasks:** 15 max (LIGHT tier)
- **Epic Tasks:** 4-8 (data loading, extraction, statistics, visualization)
- **Infrastructure Level:** Minimal (hardcoded config, print logging, smoke test)

### Prerequisite Files

- **Input:** `02c_experiment_brief.md` (Phase 2C output)
- **Output:** `03_prd.md` (this file), `03_architecture.md`, `03_logic.md`, `03_config.md`, `03_tasks.yaml`

---

## Traceability Matrix

| Requirement | Source | Validation |
|-------------|--------|------------|
| HH-RLHF dataset | Phase 2C Section "Dataset" | FR1 |
| Modal verb extraction | Phase 2C Section "Proposed Model" | FR2 |
| Hedging extraction | Phase 2C Section "Proposed Model" | FR3 |
| Alternative-framing | Phase 2C Section "Proposed Model" | FR4 |
| CV > 0.3 gate | Phase 2C Section "Evaluation" | FR5 |
| Precision > 90% | Phase 2C Section "Evaluation" | FR6 |
| Visualizations | Phase 2C Section "Visualization Requirements" | FR7 |

---

*Generated for Phase 3 Implementation Planning | Hypothesis h-e1 | EXISTENCE (FOUNDATION) | Gate: MUST_WORK*
