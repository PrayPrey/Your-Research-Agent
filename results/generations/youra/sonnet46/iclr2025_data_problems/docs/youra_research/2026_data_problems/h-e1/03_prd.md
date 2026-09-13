# Product Requirements Document: H-E1
# Conditional Demographic Association Density Measurement Pipeline

**Hypothesis ID:** H-E1
**Hypothesis Type:** EXISTENCE (PoC)
**Generated:** 2026-03-14
**Phase:** 3 - Implementation Planning
**Source:** 02c_experiment_brief.md

---

## Frontmatter

```yaml
stepsCompleted:
  - Executive Summary
  - Problem Statement
  - Functional Requirements
  - Non-Functional Requirements
  - Data Specification
  - Dependencies
  - Success Criteria
```

---

## 1. Executive Summary

H-E1 is a **corpus-only statistical analysis experiment** testing whether different data curation strategies applied to the same base corpus produce measurably different conditional demographic association densities, H(occupation|demographic). No model training is required.

**Core Question:** Does fastText quality filtering at varying percentile cutoffs produce statistically significant monotonic variation in H(occupation|demographic) compared to DoReMi domain reweighting?

**Gate:** MUST_WORK — if H(occupation|demographic) does not vary ≥5% between extreme filtering configurations with bootstrap 95% CI excluding 0, the downstream hypothesis chain (H-M1, H-M2, H-M3) is blocked.

---

## 2. Problem Statement

### 2.1 Background

The Path-Dependent Curation Fairness Hypothesis (PCFH) postulates that different data curation paths — applied to the same base corpus — create differential conditional demographic association densities that propagate into model fairness outcomes. H-E1 is the prerequisite existence check: does the mediator variable H(occupation|demographic) differ measurably across curation configurations?

### 2.2 Hypothesis Statement

Under controlled corpus conditions (DCLM-POOL / Dolma v1.7, fixed demographic token set), if fastText quality filtering is applied at varying percentile cutoffs (10%, 30%, 50%, 70%, 90%) and compared against DoReMi domain reweighting on the same base corpus, then H(occupation|demographic) will differ by ≥5% relative change between extreme configurations and will show a monotonic trend with filtering intensity.

### 2.3 Why This Experiment

fastText operates as a Wikipedia-register quality proxy — it preferentially includes/excludes documents by their demographic register distribution. This creates differential conditional associations that must be measured before attributing downstream model fairness differences to curation choices.

---

## 3. Functional Requirements

### FR-1: Data Sampling and Corpus Creation

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.1 | Sample 10M documents from DCLM-POOL using deterministic seed=42 | Must Have |
| FR-1.2 | Score all 10M documents using `mlfoundations/fasttext-oh-eli5` model | Must Have |
| FR-1.3 | Apply 5 fastText percentile threshold filters to create corpus subsets C1–C5 | Must Have |
| FR-1.4 | Apply DoReMi domain reweighting to create corpus subset C6 | Must Have |
| FR-1.5 | Save baseline unfiltered corpus C0 (all 10M docs) | Must Have |
| FR-1.6 | Save all 7 corpus subsets (C0–C6) as JSONL files | Must Have |

**Configuration C0–C6:**

| Config ID | Type | Threshold | Expected Size |
|-----------|------|-----------|--------------|
| C0 | No filter (baseline) | 0th percentile | ~10M docs |
| C1 | fastText | 10th percentile | ~9M docs |
| C2 | fastText | 30th percentile | ~7M docs |
| C3 | fastText | 50th percentile | ~5M docs |
| C4 | fastText | 70th percentile | ~3M docs |
| C5 | fastText | 90th percentile | ~1M docs |
| C6 | DoReMi | Domain reweighting | ~5M effective docs |

### FR-2: Lexicon Definition

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.1 | Define demographic token lexicon: gendered pronouns (he/she/his/her/him/they/their) + demographic NEs from WinoBias/BBQ | Must Have |
| FR-2.2 | Define occupation token lexicon: 60 occupations from WinoBias (nurse, engineer, lawyer, teacher, etc.) | Must Have |
| FR-2.3 | Lexicons must be fixed and identical across all configurations | Must Have |

### FR-3: Entropy Measurement

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.1 | For each corpus subset C0–C6, compute co-occurrence joint counts (demographic × occupation) using window size=10 | Must Have |
| FR-3.2 | Compute H(occupation|demographic) from joint counts for each configuration | Must Have |
| FR-3.3 | Use `pyitlib.discrete_random_variable.entropy_conditional()` for entropy computation | Must Have |
| FR-3.4 | Document corpus size (token count) for each configuration | Should Have |

### FR-4: Statistical Analysis

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-4.1 | Compute relative entropy change: (H_C5 - H_C1) / H_C1 × 100% | Must Have |
| FR-4.2 | Compute bootstrap 95% CI via `scipy.stats.bootstrap`, n_resamples=10,000, BCa method | Must Have |
| FR-4.3 | Compute Spearman ρ across 5 fastText configurations (percentile vs. H value) | Must Have |
| FR-4.4 | Run OLS regression: fastText_score ~ demographic_token_frequency (diagnostic, not gate-critical) | Should Have |

### FR-5: Visualization

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-5.1 | Generate gate metrics bar chart: H(occ|demo) per configuration with bootstrap 95% CI error bars | Must Have |
| FR-5.2 | Generate monotonic trend plot: H value vs. fastText percentile cutoff (C1–C5) + DoReMi (C6) | Should Have |
| FR-5.3 | Generate demographic token heatmap: occupation × demographic for C1 vs. C5 | Should Have |
| FR-5.4 | Generate entropy relative change horizontal bar chart with MUST_WORK 5% threshold line | Should Have |
| FR-5.5 | Save all figures to `h-e1/figures/` directory | Must Have |

### FR-6: Reporting

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-6.1 | Output `results.json` with all computed metrics | Must Have |
| FR-6.2 | Output `04_validation.md` with gate result and key findings | Must Have |
| FR-6.3 | Include mechanism activation verification output | Must Have |

---

## 4. Data Specification

### 4.1 Primary Dataset

**Name:** DCLM-POOL
**Source:** HuggingFace — `mlfoundations/dclm-baseline-1.0` (filtered reference) + raw DCLM-Pool
**Access:** HuggingFace datasets (may require HF access token for gated variants)
**Sample Size:** 10M documents (deterministic seed=42)
**Format:** JSONL (text field)

**Manual Download Required:** YES — DCLM-POOL requires HuggingFace access
```python
from datasets import load_dataset
dataset = load_dataset("mlfoundations/dclm-baseline-1.0", split="train", streaming=True)
# For variable thresholds: requires mlfoundations/dclm pipeline + fasttext-oh-eli5 model
```

**Fallback (if DCLM-Pool gated access unavailable):**
- Use `mlfoundations/dclm-baseline-1.0` as C5 (top-10% equivalent)
- Use `DCLM-RefinedWeb` (DCLM-Pool minus fastText filter) as C0 proxy
- Compare these 2 endpoints as existence check

### 4.2 Reference Dataset

**Name:** Dolma v1.7
**Source:** HuggingFace — `allenai/dolma` (gated)
**Use:** Reference comparison; secondary to DCLM-POOL for H-E1

### 4.3 Supporting Models (Not Neural Models)

**Name:** fasttext-oh-eli5
**Source:** HuggingFace — `mlfoundations/fasttext-oh-eli5`
**Type:** Binary fastText classifier (~100MB)
**Use:** Document quality scoring for percentile threshold filtering

**Name:** DoReMi proxy model
**Source:** `sangmichaelxie/doremi` (GitHub)
**Type:** Small reference LM for domain weight estimation
**Use:** C6 domain reweighting configuration

### 4.4 Lexicon Files

**Demographic token lexicon:**
- Gendered pronouns: he, she, his, her, him, they, their, them
- Demographic NEs: race/nationality markers from WinoBias/BBQ annotation guidelines
- Total: ~30–50 tokens

**Occupation lexicon:**
- Source: WinoBias occupation list (60 occupations)
- Examples: nurse, engineer, lawyer, teacher, doctor, housekeeper, receptionist, janitor, carpenter, electrician
- Total: 60 tokens

---

## 5. Evaluation Metrics

### 5.1 Primary Gate Metric (MUST_WORK)

| Metric | Definition | Gate Threshold |
|--------|-----------|----------------|
| `relative_entropy_change` | (H_C5 - H_C1) / H_C1 × 100% | ≥ 5% |
| `ci_excludes_zero` | Bootstrap 95% BCa CI does not contain 0 | True |

**PASS condition:** `relative_entropy_change ≥ 5%` AND `ci_excludes_zero = True`

### 5.2 Secondary Metrics (Diagnostic)

| Metric | Definition | Expected |
|--------|-----------|----------|
| `spearman_rho` | Spearman ρ(percentile, H) across C1–C5 | Monotonic (ρ ≠ 0) |
| `r_squared_fasttext_demo` | R² of OLS regression | Positive |
| `h_fasttext_vs_doremi` | H(C6_DoReMi) vs matched fastText config | Different |
| `entropy_values` | H(occ|demo) for each C0–C6 | Distinct values |

---

## 6. Success Criteria

### 6.1 PoC PASS

1. All 6 filtering configurations (C1–C6) processed without error
2. `relative_entropy_change ≥ 5%`
3. Bootstrap 95% CI excludes 0

### 6.2 PoC FAIL

- `relative_entropy_change < 5%` OR CI includes 0
- Pipeline execution error on ≥1 configuration
- Entropy values are identical across configurations (max(H) - min(H) ≈ 0)

---

## 7. Dependencies

### 7.1 Python Packages

```
# Core
datasets>=2.14.0          # HuggingFace datasets loading
fasttext>=0.9.2           # fastText model inference
numpy>=1.24.0             # Array operations
scipy>=1.11.0             # Bootstrap CI, Spearman correlation
statsmodels>=0.14.0       # OLS regression

# Entropy computation
pyitlib>=0.2.2            # Conditional entropy H(X|Y)

# Visualization
matplotlib>=3.7.0         # Figure generation
seaborn>=0.12.0           # Heatmap visualization

# Utilities
pyyaml>=6.0               # YAML reading/writing
tqdm>=4.65.0              # Progress bars
jsonlines>=3.1.0          # JSONL file I/O
huggingface-hub>=0.17.0   # Model and dataset downloads
```

### 7.2 External Repositories (Reference)

| Repository | URL | Purpose |
|------------|-----|---------|
| DCLM | github.com/mlfoundations/dclm | fastText filtering pipeline |
| DoReMi | github.com/sangmichaelxie/doremi | Domain reweighting implementation |

### 7.3 Hardware Requirements

- **GPU:** Not required (corpus analysis only)
- **RAM:** ≥ 32GB for 10M document processing
- **Storage:** ~50GB for corpus subsets
- **Runtime:** ~2–4 hours (dominated by fastText inference on 10M docs)

### 7.4 HuggingFace Access

- Requires HF account with access to `mlfoundations/dclm-baseline-1.0`
- Requires `fasttext-oh-eli5` model download (~100MB)
- Optional: Dolma v1.7 (`allenai/dolma`, gated)

---

## 8. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| NFR-1 | Deterministic results (seed=42 throughout) |
| NFR-2 | All intermediate results saved to disk for reproducibility |
| NFR-3 | Progress logging for each configuration processing step |
| NFR-4 | Fallback mechanism when DCLM-Pool gated access unavailable |
| NFR-5 | Memory-efficient streaming for 10M document processing |
| NFR-6 | Output in `h-e1/` directory structure |

---

## 9. Architecture Constraints

- **No model training** — H-E1 is statistical corpus analysis only
- **Single-threaded safe** — corpus processing may be parallelized per configuration but serial is acceptable
- **No GPU** — all computation is CPU-based
- **Minimal file structure:** `corpus_filter.py`, `entropy_measure.py`, `statistical_tests.py`, `visualize.py`, `run_experiment.py`, `config.py`

---

*Generated by Phase 3 Implementation Planning*
*Source: 02c_experiment_brief.md (Phase 2C COMPLETED)*
*BMAD PRD workflow unavailable — generated inline per UNATTENDED compensating protocol*
