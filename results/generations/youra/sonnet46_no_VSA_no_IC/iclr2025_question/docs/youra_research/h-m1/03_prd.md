# Product Requirements Document: H-M1
# Token Distribution Peakedness Analysis for Hallucination Detection

**Hypothesis:** H-M1 (MECHANISM)
**Gate:** MUST_WORK
**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr
**Phase:** 3 — Implementation Planning
**Prerequisite:** H-E1 (COMPLETED, PASSED)

---

## 1. Executive Summary

H-M1 investigates whether hallucinated answers under frozen LLMs (LLaMA-2-7B, Mistral-7B-v0.1) exhibit significantly different token distribution peakedness compared to correct answers on recall-failure benchmarks (TriviaQA, NQ). Peakedness is defined as `max(|logprob|) / mean(|logprob|)` over answer tokens. The gate condition requires Mann-Whitney U p < 0.05 (any direction) for at least one model/dataset pair, establishing whether the peakedness signal is statistically meaningful for hallucination detection.

This experiment REUSES the H-E1 infrastructure (data loading, model loading, token log-prob extraction) and EXTENDS it with:
1. Peakedness ratio computation over extracted logprob sequences
2. Group comparison (hallucinated vs. correct) via Mann-Whitney U test
3. Direction reporting relative to H-M1 and arXiv:2312.14183 predictions
4. Visualization of peakedness distributions per dataset

---

## 2. Problem Statement

H-E1 established that aggregation function choice (min/mean/sum) measurably changes AUROC for hallucination detection on frozen LLMs. H-M1 investigates the underlying mechanism: does the shape of the token log-probability distribution (peakedness) differ between hallucinated and correct answers?

**Causal hypothesis (H-M1):** Recall failures produce one highly uncertain fact-token surrounded by high-probability function words → higher peakedness in hallucinated answers.

**Empirical prior (arXiv:2312.14183):** With Falcon-40B on TriviaQA, non-hallucinating answers show MORE peaked distributions. This inverts H-M1's prediction. The experiment is direction-agnostic — it reports the observed direction without assuming H-M1's causal story holds.

---

## 3. Scope

### In Scope
- Token log-prob extraction using frozen LLaMA-2-7B (and optionally Mistral-7B-v0.1)
- TriviaQA and NQ datasets via Farquhar 2023 splits (`jlko/semantic_uncertainty`)
- Peakedness ratio computation per answer sample
- Group-level Mann-Whitney U statistical test (hallucinated vs. correct)
- Distribution visualization (histograms, box plots, scatter vs AUROC)
- Reuse of H-E1 cached logprob files when available

### Out of Scope
- TruthfulQA (imitative falsehood, not a recall-failure benchmark)
- Fine-tuning or model modification
- New model architectures
- Real-time inference systems

---

## 4. Data Specification

### 4.1 Primary Datasets

| Dataset | Source | Split | Min Samples | Labels |
|---------|--------|-------|-------------|--------|
| TriviaQA | `jlko/semantic_uncertainty` HuggingFace | validation | ≥500 | Exact-match (Farquhar 2023) |
| NQ (Natural Questions) | `jlko/semantic_uncertainty` HuggingFace | validation | ≥500 | F1 ≥ 0.5 (Farquhar 2023) |

### 4.2 Data Loading Method

**Primary path:** Reuse H-E1 cached result files at `h-e1/results/scores_llama2_trivia_qa.npz` and `h-e1/results/scores_llama2_truthful_qa.npz`.

**Note on H-E1 results:** The `.npz` files contain aggregation scores. H-M1 needs the raw `logprobs` field per record. Check if H-E1 also cached raw records (list of dicts with `logprobs` key). If raw records unavailable → re-run inference using H-E1 data pipeline.

**Fallback loading (if raw records not cached):**
```python
from datasets import load_dataset
ds_trivia = load_dataset("jlko/semantic_uncertainty", "trivia_qa", split="validation")
ds_nq = load_dataset("jlko/semantic_uncertainty", "nq", split="validation")
```

### 4.3 Binary Label Criterion

- **Correct (label=1):** Exact-match ≥ 1 gold answer (TriviaQA) OR F1 ≥ 0.5 against gold (NQ)
- **Hallucinated (label=0):** Otherwise
- **Source:** Farquhar 2023 semantic_uncertainty pipeline (same as H-E1)

### 4.4 Data Handling

- No preprocessing beyond what H-E1 already applies
- No train/test split needed — this is analysis-only on existing benchmark splits
- Cache peakedness scores to `h-m1/results/` after computation

---

## 5. Functional Requirements

### FR-1: Logprob Reuse/Extraction Module

**Priority:** Critical (blocks all downstream computation)

The system MUST provide per-token log-probability sequences for each answer sample. Two paths:

**Path A (preferred):** Load raw H-E1 records from cache
```python
# Check for H-E1 raw record cache
h_e1_records = load_cached_records("h-e1/results/")
```

**Path B (fallback):** Re-run inference using H-E1 `inference.py`
- Same model config: `meta-llama/Llama-2-7b-hf`, float16, device_map="auto"
- Same generation: `do_sample=False`, `max_new_tokens=50`, `output_scores=True`
- Same prompt: `"Q: {question}\nA:"`
- Import directly: `from h_e1.inference import load_model, extract_token_logprobs`

**Acceptance Criterion:** Each sample has `logprobs: List[float]` (all ≤ 0.0) and `label: int` (0 or 1).

---

### FR-2: Peakedness Ratio Computation

**Priority:** Critical

Implement `compute_peakedness(token_logprobs: list[float]) -> float`:
```
peakedness = max(|logprobs|) / mean(|logprobs|)
```
- Input: List of per-token log-probs (negative floats, length ≥ 1)
- Edge case: if list is empty or mean = 0 → return 1.0
- Output: float ≥ 1.0 (ratio ≥ 1 always, since max ≥ mean for non-negative values)

Group computation:
```python
def analyze_group_peakedness(records):
    hallucinated = [compute_peakedness(r["logprobs"]) for r in records if r["label"] == 0]
    correct      = [compute_peakedness(r["logprobs"]) for r in records if r["label"] == 1]
    return {"hallucinated": hallucinated, "correct": correct}
```

**Acceptance Criterion:** Function produces peakedness ≥ 1.0 for all valid inputs; degenerate case handled.

---

### FR-3: Statistical Comparison (Mann-Whitney U)

**Priority:** Critical (gate condition)

Implement two-sided Mann-Whitney U test comparing hallucinated vs. correct peakedness distributions:
```python
from scipy.stats import mannwhitneyu
stat, p = mannwhitneyu(hallucinated, correct, alternative="two-sided")
direction = "hallucinated_higher" if mean(hallucinated) > mean(correct) else "correct_higher"
```

Report for each (model, dataset) pair:
- `p_value`: gate threshold p < 0.05
- `direction`: which group has higher mean peakedness
- `mean_hallucinated`, `mean_correct`: descriptive statistics
- `n_hallucinated`, `n_correct`: sample counts

**Acceptance Criterion:** p-values computed for all (model, dataset) pairs; direction documented.

---

### FR-4: Ablation — Per-Dataset Analysis

**Priority:** High

Run analysis separately for TriviaQA and NQ (do not pool). Report per-dataset results:
- TriviaQA (n≥500): Mann-Whitney U stat, p, direction
- NQ (n≥500): Mann-Whitney U stat, p, direction
- Combined: pooled analysis (secondary)

**Acceptance Criterion:** Separate statistical results for TriviaQA and NQ.

---

### FR-5: Ablation — Secondary Model (Mistral-7B)

**Priority:** Medium (gate requires only one model; secondary confirms cross-model generality)

Attempt Mistral-7B-v0.1 inference if GPU resources allow. Mistral crashed in H-E1 — attempt with smaller batch or CPU fallback. If unavailable, document and proceed.

**Acceptance Criterion:** Either Mistral results reported OR explicit "GPU unavailable" note in report.

---

### FR-6: Visualization

**Priority:** High

Generate and save to `h-m1/figures/`:

| Figure | Type | Content |
|--------|------|---------|
| `peakedness_bar_comparison.png` | Bar chart | Mean peakedness ± 95% CI for hallucinated vs. correct, by dataset (4 bars) — **MANDATORY gate figure** |
| `peakedness_kde_{dataset}.png` | KDE/histogram | Overlapping peakedness distributions per dataset |
| `peakedness_scatter_auroc.png` | Scatter | Peakedness ratio vs. H-E1 AUROC score per sample |
| `peakedness_boxplot.png` | Box plot | Peakedness by (dataset, label) — 4 boxes |

**Acceptance Criterion:** All 4 figures saved to `h-m1/figures/`; bar chart includes error bars.

---

### FR-7: Results Caching

**Priority:** High

Save computed peakedness scores and labels to `h-m1/results/`:
```
h-m1/results/
  peakedness_llama2_trivia_qa.npz   # peakedness, labels arrays
  peakedness_llama2_nq.npz
  peakedness_mistral_trivia_qa.npz  # if available
  peakedness_mistral_nq.npz         # if available
  results_summary.json              # all p-values, directions, means
```

**Acceptance Criterion:** Results loadable without re-running inference.

---

### FR-8: Experiment Report

**Priority:** High

Generate `h-m1/04_validation.md` (written by Phase 4 Coder after experiment runs):
- Gate result: PASS/FAIL with p-values
- Direction report: observed direction vs. H-M1 prediction vs. arXiv:2312.14183
- Per-dataset/model summary table
- Interpretation for downstream hypotheses (H-M2, H-M3)

---

## 6. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seed: 42 (same as H-E1)
- Deterministic inference: `do_sample=False`
- Cached results for rerun without GPU

### NFR-2: Resource Constraints
- GPU memory: LLaMA-2-7B requires ~14GB VRAM (float16)
- Disk: ~2GB for model cache; ~100MB for result files
- Runtime target: ≤ 2 hours for full run on single A100/H100

### NFR-3: Code Quality
- All functions type-annotated
- Edge cases guarded (empty logprobs, zero mean)
- Reuse H-E1 modules via import (no copy-paste)

### NFR-4: Statistical Validity
- Minimum 500 samples per dataset per model
- Two-sided test (direction determined empirically, not assumed)
- No multiple comparison correction needed (H-M1 requires only one significant pair)

---

## 7. Dependencies

### 7.1 Python Packages (H-E1 environment — no new packages needed)

| Package | Version | Purpose |
|---------|---------|---------|
| `torch` | ≥2.0 | Model inference |
| `transformers` | ≥4.35 | AutoModelForCausalLM, AutoTokenizer |
| `datasets` | ≥2.14 | HuggingFace dataset loading |
| `numpy` | ≥1.24 | Numerical computation |
| `scipy` | ≥1.10 | `mannwhitneyu` statistical test |
| `matplotlib` | ≥3.7 | Visualization |
| `seaborn` | ≥0.12 | KDE plots |
| `accelerate` | ≥0.21 | `device_map="auto"` |

**No new packages required** — all available in H-E1 environment.

### 7.2 Internal Dependencies (H-E1 Code Reuse)

| Module | Import Path | Used For |
|--------|-------------|---------|
| `data_loader` | `h-e1/code/data_loader.py` | Dataset loading, binary label scoring |
| `inference` | `h-e1/code/inference.py` | Model loading, token log-prob extraction |
| `config` | `h-e1/code/config.py` | MODELS dict, MAX_NEW_TOKENS |

**Reuse strategy:** Add `h-e1/code/` to sys.path and import directly, OR copy relevant functions with attribution.

### 7.3 External Data Sources

| Dataset | Access Method | Cache Location |
|---------|--------------|----------------|
| TriviaQA | `load_dataset("jlko/semantic_uncertainty", "trivia_qa")` | HuggingFace cache |
| NQ | `load_dataset("jlko/semantic_uncertainty", "nq")` | HuggingFace cache |
| H-E1 results | Direct file read | `h-e1/results/*.npz` |

---

## 8. Success Criteria

### Gate Condition (MUST_WORK)
- Mann-Whitney U test p < 0.05 for at least one (model, dataset) pair
- Any direction qualifies (hallucinated_higher OR correct_higher)
- Minimum 500 samples per group required for valid test

### Secondary Success
- Results consistent across both TriviaQA and NQ
- Results consistent across LLaMA-2-7B and Mistral-7B (if available)
- Direction matches or inverts H-M1 prediction — both outcomes are informative

### Quality Criteria
- All 4 figures generated
- Results cached to `h-m1/results/`
- Direction documented relative to both H-M1 prediction and arXiv:2312.14183

---

## 9. Failure Response

If gate fails (p ≥ 0.05 for all pairs):
- Route: EXPLORE/PIVOT per hypothesis-loop protocol
- Document: "Peakedness ratio does not significantly differ between hallucinated and correct answers at 7B scale"
- Implication: The proposed mechanism (single unknown fact-token) does not manifest as measurable peakedness difference — investigate alternative mechanisms (H-M2, H-M3)

---

*stepsCompleted: [PRD]*
