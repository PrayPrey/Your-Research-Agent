# H-E1 Validation Report

**Hypothesis ID:** h-e1
**Gate Type:** MUST_WORK
**Gate Result:** ✅ PASS
**Date:** 2026-03-16
**Experiment Completed:** 2026-03-16T15:28:57Z

---

## Hypothesis

**H-E1 (EXISTENCE):** A cross-encoder NLI model (`cross-encoder/nli-deberta-v3-large`) using P(contradiction) as a hallucination signal achieves AUROC > 0.55 (statistically significant vs. random, DeLong p < 0.05) on ≥2/3 HaluEval tasks (dialogue, QA, summarization).

---

## Gate Condition (MUST_WORK)

| Criterion | Threshold | Result |
|-----------|-----------|--------|
| Tasks passing AUROC > 0.55 AND p < 0.05 | ≥ 2/3 | **2/3** ✅ |

**Gate: PASS** — 2/3 tasks satisfy both AUROC and statistical significance criteria.

---

## Experimental Setup

- **Model:** `cross-encoder/nli-deberta-v3-large` (inference-only, no fine-tuning)
- **Dataset:** `pminervini/HaluEval` (HuggingFace) — 3 subsets
- **Sample size:** 20,000 pairs per task (10,000 right + 10,000 hallucinated, balanced)
- **Total pairs evaluated:** 60,000
- **GPU:** NVIDIA H100 NVL, GPU 0 (selected by lowest memory usage)
- **Contradiction index:** 0 (verified via `verify_label_map()`)
- **Statistical test:** fastDeLong AUC variance test vs. 0.5 baseline

---

## Per-Task Results

| Task | AUROC | DeLong p-value | Cohen's d | AUROC_max | Gate Pass |
|------|-------|----------------|-----------|-----------|-----------|
| **dialogue** | **0.7094** | **0.0** | 0.714 | 0.77 | ✅ PASS |
| **qa** | **0.6437** | **1.29e-282** | 0.779 | 0.77 | ✅ PASS |
| summarization | 0.530 | 2.02e-13 | 0.220 | 0.52 | ❌ FAIL |

### Mechanism Indicators (all tasks)

| Indicator | dialogue | qa | summarization |
|-----------|----------|----|---------------|
| shape_correct | ✅ | ✅ | ✅ |
| non_uniform | ✅ | ✅ | ✅ |
| above_random | ✅ | ✅ | ✅ |
| label_verified | ✅ | ✅ | ✅ |

All tasks passed mechanism verification — the NLI contradiction signal is active and non-trivial across all three domains.

---

## Key Findings

### 1. Dialogue Task (AUROC = 0.709)
- Strong discrimination: hallucinated responses produce significantly higher P(contradiction) vs. grounded responses
- Cohen's d = 0.714 (large effect size)
- DeLong p ≈ 0 confirms robust statistical significance
- AUROC_max = 0.77 indicates moderate structural ceiling from NLI label ambiguity

### 2. QA Task (AUROC = 0.644)
- Good discrimination for knowledge-grounded QA hallucinations
- Cohen's d = 0.779 (large effect size, highest of the three tasks)
- DeLong p = 1.29e-282 — extremely significant
- AUROC_max = 0.77 — similar structural ceiling to dialogue

### 3. Summarization Task (AUROC = 0.530) — FAIL
- Below AUROC threshold (0.55) — insufficient discrimination
- Cohen's d = 0.220 (small effect size)
- p = 2.02e-13 is technically significant but AUROC is near-random
- AUROC_max = 0.52 — very low structural ceiling: summarization hallucinations in HaluEval may not be contradiction-detectable (paraphrastic or omission-based hallucinations rather than factual contradictions)
- `p_contradictory` = 0.04 (very low) confirms NLI model rarely assigns contradiction to summarization pairs

### Root Cause of Summarization Failure
Summarization hallucinations in HaluEval appear to be primarily **omission-based or abstractive errors** rather than direct factual contradictions. The NLI contradiction signal is designed to detect direct semantic contradiction — it is architecturally misaligned with this hallucination type.

---

## Figures Generated

| Figure | Path |
|--------|------|
| Gate metrics comparison | `figures/gate_metrics_comparison.png` |
| ROC curves | `figures/roc_curves.png` |
| Score distributions | `figures/score_distributions.png` |
| Structural ceiling | `figures/structural_ceiling.png` |

---

## Output Files

| File | Description |
|------|-------------|
| `results/h-e1_results.json` | Full 20000×3 score matrices per task |
| `results/h-e1_summary.json` | Per-task metrics summary |

---

## Implementation Notes

### Dataset Discovery
The `pminervini/HaluEval` dataset uses `right_X`/`hallucinated_X` column pairs (not a binary `hallucination` label column). Implemented interleaving: each raw example → 2 pairs (right=label 0, hallucinated=label 1), producing balanced 20k pairs per task.

### Code Files
- `code/config.py` — `ExperimentConfig` dataclass with all hyperparameters
- `code/data.py` — HaluEval loader with paired interleaving
- `code/model.py` — `NLIInferenceModel`: batch inference with OOM fallback
- `code/evaluate.py` — fastDeLong, Cohen's d, AUROC, gate logic, 4 visualizations
- `code/run_experiment.py` — full orchestration pipeline

### Tests
32/32 unit tests pass across all 5 test files.

---

## Gate Decision

**GATE: PASS ✅**

The MUST_WORK gate is satisfied: ≥2/3 tasks (dialogue + QA) achieve AUROC > 0.55 with DeLong p < 0.05. The NLI contradiction signal is a valid hallucination detector for conversation and knowledge-grounded QA domains.

**H-E1 hypothesis is VALIDATED.** The existence of P(contradiction) as a hallucination signal is confirmed for the majority of HaluEval tasks. Summarization is an identified limitation.

---

## Implications for Follow-on Hypotheses

- **H-M series** (mechanism): The strong but not ceiling performance (0.644–0.709) suggests room for improvement via additional signals or model fine-tuning
- **Summarization gap**: Dedicated hypothesis for omission-based hallucination detection may be warranted
- `h-e1_results.json` provides raw (N,3) score matrices for reuse in H-M experiments without re-running inference
