# Experiment Design: H-E1

**Date:** 2026-03-14
**Author:** Anonymous
**Hypothesis Statement:** Under controlled corpus conditions (Dolma v1.7 / DCLM-POOL, fixed demographic token set), if fastText quality filtering is applied at varying percentile cutoffs (10%, 30%, 50%, 70%, 90%) and compared against DoReMi domain reweighting on the same base corpus, then the conditional demographic association density H(occupation|demographic) will differ by ≥5% relative change between extreme configurations and will show a monotonic trend with filtering intensity, because fastText operates as a domain-demographic selector — Wikipedia-register quality proxy systematically includes/excludes text by demographic register distribution.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.
> **Note:** H-E1 is a corpus-only statistical analysis — no model training required.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** None required (first hypothesis in chain)
**Gate Status:** MUST_WORK — not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
MUST_WORK — If H(occupation|demographic) does not vary ≥5% across extreme filtering configurations, H-M1, H-M2, and H-M3 are blocked. Pipeline halts if gate fails.

---

## Continuation Context

This is the first hypothesis in the verification chain. No previous hypothesis context to inherit.

### Previous Hypothesis Results (if applicable)
None — H-E1 has no prerequisites. This is the Phase A corpus audit establishing the mediator variable.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

⚠️ **Archon MCP unavailable** (not registered in session). Per UNATTENDED mode protocol, limitations documented; web search used as compensating research.

**Key findings from web research (compensating for Archon):**

**Query 1: DCLM fastText Filtering Implementation**
- **Source:** mlfoundations/dclm (GitHub) — Official DCLM Repository
  - Corpus: DCLM-POOL = 240T unfiltered Common Crawl tokens (text extraction only via resiliparse)
  - fastText model: `mlfoundations/fasttext-oh-eli5` (HuggingFace) — binary classifier trained on OH-2.5 + r/ELI5
  - Filtering mechanism: Top-k percentile thresholding on classifier scores
  - Percentile threshold configuration is supported in the pipeline (global aggregation function with dynamic threshold)
  - **DCLM-RefinedWeb** = DCLM-Pool minus the OH2.5+ELI5 fastText filter → perfect controlled ablation baseline
  - Key insight: fastText at top-10% threshold contributes >6 percentage points MMLU gain vs. prior open corpus

**Query 2: DoReMi Domain Reweighting Implementation**
- **Source:** sangmichaelxie/doremi (GitHub, NeurIPS 2023) — Official DoReMi Repository
  - Method: Group DRO-based proxy model → domain weight optimization → resample training data
  - Domains treated as groups; weights updated via excess loss vs. reference model
  - Result: +6.5% few-shot downstream accuracy over The Pile default weights; 2.6x fewer steps
  - Key insight: domain identity is the observable proxy for demographic distribution shifts

**Query 3: Conditional Entropy / Co-occurrence Measurement**
- **Source:** pyitlib (MIT-licensed, Python/NumPy)
  - Provides `entropy_conditional()` for computing H(X|Y) directly from joint counts
  - Works on categorical data arrays — ideal for occupation/demographic token co-occurrences
- **Source:** scipy.stats.bootstrap
  - Standard bootstrap CI computation for 95% confidence intervals on entropy differences
  - BCa method recommended for skewed statistics
- **Source:** Bordia & Bowman (2019) — Co-Occurrence Bias Score
  - Established pattern for measuring co-occurrence of tokens with gendered words in corpus
  - Direct precedent for this experiment's demographic token measurement approach

**Query 4: WinoBias / Pythia Fairness Research**
- **Source:** EleutherAI/pythia (GitHub) — Pythia Suite
  - Designed specifically for controlled pretraining experiments
  - 154 intermediate checkpoints per model
  - Existing fairness work: modified pronoun frequency in last 7%/21% of training, measured on WinoBias
  - This confirms Pythia's suitability for the broader PCFH project (H-M2, H-M3)
  - Key insight for H-E1: corpus-level measurement is prerequisite to model training

### Archon Code Examples

⚠️ **Archon MCP unavailable** — code patterns derived from official repositories and Python libraries.

**Pattern 1: fastText Score Extraction (from DCLM pipeline)**
```python
# From mlfoundations/dclm baselines implementation
import fasttext
model = fasttext.load_model("fasttext-oh-eli5.bin")
def score_document(text: str) -> float:
    # Returns classifier probability score
    label, prob = model.predict(text.replace("\n", " "))
    return prob[0] if label[0] == "__label__hq" else 1.0 - prob[0]
```

**Pattern 2: Conditional Entropy from Co-occurrence (pyitlib)**
```python
import numpy as np
from pyitlib import discrete_random_variable as drv

# occupation_tokens: array of occupation labels per document
# demographic_tokens: array of demographic labels per document
H_conditional = drv.entropy_conditional(occupation_tokens, demographic_tokens)
```

**Pattern 3: Bootstrap CI (scipy)**
```python
from scipy import stats
def entropy_diff_statistic(config_a, config_b):
    return compute_entropy(config_a) - compute_entropy(config_b)
ci = stats.bootstrap((config_extreme_a, config_extreme_b),
                     entropy_diff_statistic, n_resamples=10000,
                     method='BCa', confidence_level=0.95)
```

### Exa GitHub Implementations

**Query 1: Official DCLM fastText Implementation**

**Repository 1:** `mlfoundations/dclm` (Primary — HIGHEST PRIORITY)
- **URL:** https://github.com/mlfoundations/dclm
- **Relevance:** Official implementation of fastText quality filtering on DCLM-POOL. Contains the exact filtering pipeline we need to replicate at different percentile thresholds.
- **Key Files:**
  - `baselines/` — Contains processing pipeline YAML configs and filtering scripts
  - `baselines/README.md` — Documents how to run fastText filtering
- **Filtering Config:** Percentile-based thresholding on classifier scores; configurable via pipeline YAML
- **fastText Model:** `mlfoundations/fasttext-oh-eli5` (HuggingFace)
- **Dataset:** DCLM-Pool (HuggingFace: `mlfoundations/dclm-baseline-1.0`)
- **Training Config:**
  - fastText: binary classifier on OH-2.5 + ELI5 data
  - Threshold: top-10% → DCLM-Baseline; variable percentile for H-E1

**Repository 2:** `sangmichaelxie/doremi` (Medium Priority)
- **URL:** https://github.com/sangmichaelxie/doremi
- **Relevance:** Official PyTorch implementation of DoReMi domain reweighting. Provides the comparison curation path.
- **Architecture:** Group DRO with small proxy model + reference model
- **Domain Handling:** 22 domains (The Pile); adaptable to Dolma subcorpora
- **Configuration:**
  - Proxy model: small LM (≈ 125M)
  - Reference model: same architecture pretrained on uniform mixture
  - Output: domain weight vector for resampling

**Serena Analysis Needed:** False — code from official repositories is clear; no complex custom layers.

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

H-E1 is a **novel measurement experiment** (not paper reproduction). Primary implementations are:
1. DCLM pipeline for fastText filtering at variable percentiles
2. DoReMi pipeline for domain reweighting comparison
3. Custom entropy measurement pipeline (standard NLP tools)

**Recommended Implementation Path:**
- Primary: DCLM official pipeline (`mlfoundations/dclm`) for fastText filtering; DoReMi official (`sangmichaelxie/doremi`) for domain reweighting
- Fallback: Custom fastText inference + percentile thresholding using `fasttext` Python library directly
- Justification: Official implementations ensure exact replication of the filtering conditions claimed in the Phase 2B verification plan. Using official code avoids implementation drift from the published methods.

### Code Analysis (Serena MCP)

*Skipped* — No complex code requiring Serena analysis. H-E1 uses standard NLP tools (fasttext, scipy, pyitlib, HuggingFace datasets) with well-documented APIs. Code from official repositories is sufficiently clear.

---

## Experiment Specification

### Dataset

**Name:** DCLM-POOL (primary sampling source) + Dolma v1.7 (reference)
**Type:** standard
**HuggingFace Source:**
- DCLM-POOL: `mlfoundations/dclm-baseline-1.0` (filtered) or raw DCLM-Pool
- Dolma v1.7: `allenai/dolma` (gated, requires HF access)

**Sample Size:** 10M documents from DCLM-POOL (per verification protocol)
- Sufficient for statistically meaningful H(occupation|demographic) estimates
- 10M × 6 configurations = 60M total document-configuration pairs

**Splits for H-E1:**
- No train/val/test split — this is a corpus measurement experiment
- 6 corpus subsets created by applying different filtering configurations to the same 10M document base sample:
  - FastText 10th percentile (top 90% documents by score)
  - FastText 30th percentile (top 70% documents)
  - FastText 50th percentile (top 50% documents)
  - FastText 70th percentile (top 30% documents)
  - FastText 90th percentile (top 10% documents — DCLM-Baseline equivalent)
  - DoReMi domain reweighting (reference comparison path)

**Preprocessing:**
- Text extraction already performed (resiliparse) in DCLM-Pool
- Tokenization: whitespace/NLTK word tokenization for co-occurrence measurement
- Demographic token set: fixed lexicon (see Evaluation section)
- Occupation token set: fixed lexicon from WinoBias occupation list (60 occupations)
- No text cleaning beyond DCLM's existing extraction

**Synthetic Data Check:** PASSED — DCLM-POOL is real Common Crawl data ✅

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `datasets` + DCLM pipeline
- Identifier: `mlfoundations/dclm-baseline-1.0` (for DCLM reference); custom sampling from DCLM-Pool for variable thresholds
- Code:
```python
from datasets import load_dataset
# Load DCLM baseline (top-10% fastText filtered)
dataset = load_dataset("mlfoundations/dclm-baseline-1.0", split="train", streaming=True)

# For variable thresholds: use DCLM pipeline with score-based percentile filtering
# Requires: mlfoundations/dclm repo + fasttext-oh-eli5 model
import fasttext
ft_model = fasttext.load_model("fasttext-oh-eli5.bin")
# Score documents, apply nth percentile threshold
```

### Models

#### Baseline Model

**Architecture:** No neural model — H-E1 is a **statistical corpus analysis experiment**

**Baseline "Model" = Unfiltered DCLM-POOL sample** (0th percentile — all documents)
- Establishes baseline H(occupation|demographic) before any filtering
- Provides reference entropy for computing relative change

**Comparison Configurations (6 total):**
| Config ID | Type | Threshold | Expected Corpus Size |
|-----------|------|-----------|---------------------|
| C0 | No filter (baseline) | 0th percentile | 10M docs |
| C1 | fastText | 10th percentile | ~9M docs |
| C2 | fastText | 30th percentile | ~7M docs |
| C3 | fastText | 50th percentile | ~5M docs |
| C4 | fastText | 70th percentile | ~3M docs |
| C5 | fastText | 90th percentile | ~1M docs |
| C6 | DoReMi | Domain reweighting | ~5M effective docs |

**Loading Information** (for Phase 4):
- Method: DCLM pipeline + fastText model
- Identifier: `mlfoundations/fasttext-oh-eli5` (HuggingFace)
- Code:
```python
# No model training needed — only fastText inference for filtering
import fasttext
model = fasttext.load_model("fasttext-oh-eli5.bin")  # ~100MB
# Score each document, sort by score, apply percentile cutoffs
scores = [score_document(model, doc) for doc in corpus_sample]
```

#### Proposed Model

**Architecture:** Proposed measurement = filtered corpus configurations (C1–C6) vs. baseline (C0)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Conditional Demographic Entropy Measurement
# Based on: Bordia & Bowman (2019), DCLM official pipeline, pyitlib
# H-E1: Measures H(occupation|demographic) across curation configurations

import numpy as np
from collections import defaultdict
import math

def compute_conditional_entropy(corpus_subset: list[str],
                                 occ_lexicon: set[str],
                                 demo_lexicon: set[str],
                                 window: int = 10) -> float:
    """
    Compute H(occupation | demographic) from corpus co-occurrences.
    Args:
        corpus_subset: list of documents (strings)
        occ_lexicon: occupation tokens (WinoBias 60 occupations)
        demo_lexicon: demographic tokens (gendered pronouns + demographic NEs)
        window: co-occurrence window size (tokens)
    Returns:
        H_occ_given_demo: conditional entropy (bits)
    """
    joint_counts = defaultdict(lambda: defaultdict(int))
    demo_counts = defaultdict(int)

    for doc in corpus_subset:
        tokens = doc.lower().split()
        for i, token in enumerate(tokens):
            if token in demo_lexicon:
                context = tokens[max(0, i-window):i+window+1]
                for occ in context:
                    if occ in occ_lexicon:
                        joint_counts[token][occ] += 1
                        demo_counts[token] += 1

    # Compute H(occupation | demographic) = -sum p(o,d) log p(o|d)
    H = 0.0
    total = sum(demo_counts.values())
    for demo, occ_dict in joint_counts.items():
        p_demo = demo_counts[demo] / total if total > 0 else 0
        H_occ_given_this_demo = 0.0
        n = demo_counts[demo]
        for occ, cnt in occ_dict.items():
            p_occ_given_demo = cnt / n if n > 0 else 0
            if p_occ_given_demo > 0:
                H_occ_given_this_demo -= p_occ_given_demo * math.log2(p_occ_given_demo)
        H += p_demo * H_occ_given_this_demo
    return H
```

### Training Protocol

**No model training required for H-E1.** This is a corpus measurement experiment.

**Computation Protocol:**

**Phase 1: Data Sampling and Filtering (per configuration)**
- Sample: 10M documents from DCLM-Pool (deterministic seed=42)
- Apply fastText scoring: `mlfoundations/fasttext-oh-eli5` model
- Apply percentile thresholds to create 5 fastText configurations
- Apply DoReMi reweighting to create 1 DoReMi configuration
- Save 6 corpus subsets as JSONL files

**Phase 2: Entropy Measurement**
- Load demographic token lexicon: gendered pronouns (he/she/his/her/him/they/their) + demographic NEs (race/nationality markers from WinoBias/BBQ)
- Load occupation lexicon: 60 occupations from WinoBias (e.g., nurse, engineer, lawyer, teacher)
- Co-occurrence window: 10 tokens (±5 from demographic token)
- Compute H(occupation|demographic) for each of 6 corpus subsets
- Compute joint counts matrix: (demographic × occupation) → count

**Phase 3: fastText Demographic Regression**
- Run OLS regression: fastText_score ~ demographic_token_frequency + demographic_occupation_density
- Compute R² and p-values for each coefficient
- This is diagnostic (not gate-critical)

**Phase 4: Statistical Testing**
- Compute relative entropy change: (H_C5 - H_C1) / H_C1 × 100%
- Bootstrap CI: scipy.stats.bootstrap, n_resamples=10,000, BCa method
- Test: bootstrap 95% CI of entropy difference excludes 0
- Spearman ρ: correlation of H values across 5 fastText configurations with percentile order

**Compute Resources:**
- No GPU required (corpus analysis only)
- RAM: ~32GB for 10M document processing
- Runtime: ~2–4 hours for full pipeline (dominated by fastText inference)
- Seeds: 1 (fixed, seed=42)

### Evaluation

**Primary Metric (MUST_WORK gate):**
- `relative_entropy_change`: (H_extreme_90pct - H_extreme_10pct) / H_extreme_10pct × 100%
- Target: ≥ 5% relative change

**Secondary Metrics (diagnostic):**
- `spearman_rho`: Spearman correlation of H values across 5 fastText configs with percentile order
- `r_squared_fasttext_demo`: R² of OLS regression of fastText scores on demographic features
- `h_fasttext_vs_doremi`: H(occ|demo) difference between DoReMi and matched fastText configs

**Success Criteria:**
- PoC PASS: relative_entropy_change ≥ 5% AND bootstrap 95% CI excludes 0
- PoC FAIL: relative_entropy_change < 5% OR CI includes 0

**Expected Values (from literature):**
- fastText is a quality proxy with known Wikipedia-register bias → expect H to decrease with stricter filtering (Wikipedia has more formal, less stereotyped demographic-occupation text)
- DoReMi reweights toward high-resource domains (Wikipedia, books) → expect similar but distinct H profile
- Expected relative change: 5–20% (based on known domain demographic distribution differences)

**Metrics Loading Information:**
- Task Type: Statistical corpus analysis (information-theoretic measurement)
- Library: `pyitlib` (entropy), `scipy.stats` (bootstrap, Spearman), `statsmodels` (OLS regression)
- Code:
```python
from pyitlib import discrete_random_variable as drv
from scipy import stats
import statsmodels.api as sm

# Conditional entropy
H = drv.entropy_conditional(occupation_labels, demographic_labels)

# Bootstrap CI
ci = stats.bootstrap((config_A_entropies, config_B_entropies),
                      lambda a, b: np.mean(a) - np.mean(b),
                      n_resamples=10000, method='BCa')

# Spearman correlation
rho, p_val = stats.spearmanr(percentile_cutoffs, entropy_values)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** Bar chart showing H(occ|demo) for each of 6 configurations (C1–C6) vs baseline C0, with bootstrap 95% CI error bars. Red dashed line at baseline. Caption: "Relative entropy change across fastText percentile cutoffs and DoReMi configuration."

#### Additional Figures (LLM Autonomous)

Based on the hypothesis structure and measurement design, the following additional figures are recommended for Phase 4:

1. **Monotonic Trend Plot:** Line plot of H(occ|demo) vs. fastText percentile cutoff (10%→90%), with DoReMi as separate point. Annotates whether trend is monotonic (Spearman ρ and p-value).

2. **Demographic Token Heatmap:** Co-occurrence heatmap (occupation × demographic token) for extreme configurations (C1 vs C5), showing which (occupation, demographic) pairs show largest absolute count change.

3. **fastText Score vs. Demographic Feature Scatter:** Scatter plot of fastText scores vs. per-document demographic-occupation density, with OLS regression line and R² annotation (diagnostic plot for assumption A5).

4. **Entropy Relative Change Visualization:** Horizontal bar chart of relative entropy change per configuration pair, with MUST_WORK 5% threshold line highlighted.

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Pipeline runs without error on 10M document sample
2. `relative_entropy_change ≥ 5%` (H_extreme_90pct vs H_extreme_10pct)
3. Bootstrap 95% CI excludes 0

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | Corpus co-occurrence matrix can be computed from DCLM-POOL documents | TRUE — standard NLP co-occurrence analysis |
| Mechanism Isolatable | Each filtering configuration produces independent corpus subset for isolated measurement | TRUE — 6 independent subsets |
| Baseline Measurable | Unfiltered corpus (C0) provides clean reference H(occ\|demo) measurement | TRUE — C0 = full 10M document sample |

### Architecture Compatibility Check

**This is a statistical corpus analysis pipeline** — no neural model architecture.

**Required Components:**
- fastText binary classifier model (`mlfoundations/fasttext-oh-eli5`)
- Python NLP libraries: `fasttext`, `datasets`, `pyitlib`, `scipy`, `statsmodels`, `numpy`
- Sufficient RAM for 10M document processing (~32GB)
- Access to DCLM-Pool data (HuggingFace gated)

**Incompatible Architectures:**
- N/A — pipeline is architecture-agnostic

> ⚠️ If DCLM-Pool access is unavailable, fall back to DCLM-Baseline-1.0 + DCLM-RefinedWeb comparison (C5 vs. C0 proxy using available filtered/unfiltered versions).

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "Processing configuration C{n}: {k}M docs after {p}th percentile filter" | corpus_filter.py:apply_filter() |
| Count Change | joint_counts matrix differs across configurations (non-identical H values) | entropy_measure.py:compute_joint_counts() |
| Metric Delta | H(occ\|demo) changes measurably across configurations (relative change > 0) | evaluate.py:compute_entropy_diff() |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(config_entropies: dict, results: dict) -> tuple[bool, dict]:
    """Verify that filtering mechanism produces measurable entropy variation."""
    h_vals = list(config_entropies.values())
    indicators = {
        "configs_processed": len(config_entropies) == 6,
        "entropies_differ": max(h_vals) - min(h_vals) > 0,
        "relative_change": abs(config_entropies['C5'] - config_entropies['C1'])
                           / config_entropies['C1'] * 100,
        "gate_passed": results.get("relative_entropy_change", 0) >= 5.0,
        "ci_excludes_zero": results.get("ci_low", 0) > 0
                             or results.get("ci_high", 0) < 0
    }
    success = (indicators["configs_processed"] and
               indicators["entropies_differ"] and
               indicators["gate_passed"])
    return success, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Zero entropy variation | max(H) - min(H) ≈ 0 across configs | FAIL: filtering has no demographic effect |
| < 5% relative change | relative_entropy_change < 5 | FAIL: MUST_WORK gate not satisfied |
| CI includes zero | bootstrap 95% CI spans 0 | FAIL: change not statistically reliable |
| Dataset access failure | HuggingFace download error | FALLBACK: use DCLM-Baseline vs. RefinedWeb as proxy |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Pipeline Completes | All 6 configs processed | Log check |
| Entropy Varies | H differs across configs | max(H) - min(H) > 0 |
| Hypothesis Supported | ≥5% relative change AND bootstrap CI excludes 0 | relative_entropy_change metric |

---

## Appendix: Reference Implementations

### A. Web Research Sources (Compensating for Archon MCP)

**Source A.1:** mlfoundations/dclm (GitHub)
- **URL:** https://github.com/mlfoundations/dclm
- **Query Used:** "DCLM-POOL sampling fastText percentile filtering Python script GitHub mlfoundations 2024"
- **Relevance:** Official DCLM pipeline with fastText classifier and percentile thresholding
- **Key Insights:**
  - fastText model `fasttext-oh-eli5` is the exact classifier used in DCLM-Baseline
  - Percentile-based dynamic threshold aggregation is a planned/available feature in pipeline
  - DCLM-RefinedWeb provides a controlled comparison without fastText filter
- **Used For:** Dataset loading, fastText filtering pipeline, corpus configuration design

**Source A.2:** sangmichaelxie/doremi (GitHub)
- **URL:** https://github.com/sangmichaelxie/doremi
- **Query Used:** "DoReMi domain reweighting pretraining data corpus conditional demographic association fairness GitHub"
- **Relevance:** Official DoReMi implementation for domain reweighting comparison path
- **Key Insights:**
  - Group DRO mechanism with proxy model + reference model
  - Output: domain weight vector for resampling training data
  - Can be applied to Dolma subcorpora domains
- **Used For:** DoReMi configuration (C6) design

**Source A.3:** Bordia & Bowman (2019) — Co-Occurrence Bias Score
- **Query Used:** "corpus demographic token co-occurrence analysis WinoBias BBQ fairness benchmark pretraining data measurement GitHub 2024"
- **Relevance:** Established co-occurrence measurement pattern for gender bias in corpora
- **Key Insights:**
  - Co-Occurrence Bias Score measures co-occurrence of tokens with gendered words
  - Standard window-based approach validated in prior fairness literature
- **Used For:** Core mechanism pseudo-code design, demographic token lexicon methodology

**Source A.4:** pyitlib (Python library)
- **URL:** https://pypi.org/project/pyitlib/
- **Query Used:** "conditional entropy H(occupation|demographic) pretraining corpus measurement co-occurrence Python implementation"
- **Relevance:** MIT-licensed library with `entropy_conditional()` for H(X|Y) computation
- **Used For:** Conditional entropy computation implementation

**Source A.5:** scipy.stats.bootstrap
- **URL:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html
- **Query Used:** "bootstrap confidence interval corpus entropy difference scipy Python implementation statistical test"
- **Relevance:** Standard bootstrap CI implementation with BCa method
- **Used For:** Statistical testing protocol (bootstrap 95% CI for ≥5% threshold check)

**Source A.6:** EleutherAI/pythia (GitHub)
- **URL:** https://github.com/EleutherAI/pythia
- **Query Used:** "Pythia suite pretraining controlled experiment demographic bias measurement logit margin probe GitHub EleutherAI"
- **Relevance:** Pythia suite used for downstream model training in H-M2/H-M3; existing fairness work confirms suitability
- **Used For:** Context for H-E1's role as pre-training diagnostic; Pythia model confirmed for H-M2+

### B. GitHub Implementations (Exa equivalent via web search)

**Repository 1:** `mlfoundations/dclm`
- **URL:** https://github.com/mlfoundations/dclm
- **Configuration Extracted:** fastText percentile filtering pipeline, DCLM-Pool access, `fasttext-oh-eli5` model
- **Used For:** Data loading, filtering configurations C1–C5

**Repository 2:** `sangmichaelxie/doremi`
- **URL:** https://github.com/sangmichaelxie/doremi
- **Configuration Extracted:** Group DRO domain reweighting on Dolma subcorpora
- **Used For:** DoReMi configuration C6

### C. Code Analysis (Serena)
Serena analysis: Not performed — code from official repositories was sufficiently clear; H-E1 uses standard Python NLP libraries with well-documented APIs. No complex custom model architecture to analyze.

### D. Previous Hypothesis Context
None — H-E1 is the first hypothesis in the verification chain.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection (DCLM-POOL) | Web Research | Source A.1 (mlfoundations/dclm) |
| fastText filtering pipeline | GitHub | Repo A.1 (mlfoundations/dclm) |
| Percentile threshold configurations | GitHub + Paper | A.1 + Phase 2B Section 2.2 |
| DoReMi comparison path | GitHub | Repo A.2 (sangmichaelxie/doremi) |
| Co-occurrence measurement | Academic Paper | A.3 (Bordia & Bowman 2019) |
| Conditional entropy computation | Library | A.4 (pyitlib) |
| Bootstrap CI methodology | Library | A.5 (scipy.stats.bootstrap) |
| Occupation lexicon (60 occupations) | Benchmark | WinoBias (Phase 2B Section 2.2) |
| Demographic token lexicon | Benchmark | WinoBias + BBQ (Phase 2B) |
| Evaluation metrics | Phase 2B | Section 2.2 Success Criteria |
| Pythia model (H-M2+) | GitHub | A.6 (EleutherAI/pythia) |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-14

### Workflow History for This Hypothesis
- 2026-03-14T00:00:00: H-E1 set to IN_PROGRESS (External loop starting Phase 2C → 3 → 4)
- 2026-03-14: Phase 2C experiment design IN_PROGRESS

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: WebSearch (Archon/Exa compensating — MCP unavailable in session)*
*All specifications grounded in researched implementations from official repositories*
*Next Phase: Phase 3 - Implementation Planning*
