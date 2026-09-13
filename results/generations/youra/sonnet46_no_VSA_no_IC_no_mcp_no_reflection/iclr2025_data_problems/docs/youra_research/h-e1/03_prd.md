# Product Requirements Document: H-E1

**stepsCompleted:** 1,2,3,4,5,6,7
**Hypothesis:** H-E1 (EXISTENCE PoC)
**Date:** 2026-08-31
**Author:** yoon303@ust.ac.kr
**Phase:** 3 — Implementation Planning

---

## 1. Executive Summary

This experiment validates whether corpus curation quality produces measurably different generalization balance between Pythia-6.9B (The Pile, minimal curation) and OLMo-7B (Dolma, quality-filtered) at a matched training scale of ~300B tokens. The experiment is evaluation-only: no training is performed. We run both models through lm-evaluation-harness on MMLU, HellaSwag, ARC-Easy, and ARC-Challenge, then compute two derived metrics (MMLU/HellaSwag ratio, ARC-Challenge/Easy delta) and test whether OLMo outperforms Pythia on both.

**Gate:** MUST_WORK. If H-E1 fails, H-M1 through H-M4 are blocked.

---

## 2. Problem Statement

Existing comparisons between Pythia and OLMo conflate parameter count differences, architecture differences, and training data differences. H-E1 isolates the corpus curation variable by:
1. Selecting intermediate checkpoints at matched token counts (~300B)
2. Using identical evaluation protocol (lm-evaluation-harness, standard shot configs)
3. Computing ratio/delta metrics that normalize for absolute performance level

The null hypothesis: `olmo_mmlu_hellaswag_ratio ≤ pythia_mmlu_hellaswag_ratio + 0.02`

---

## 3. Scope

**In scope:**
- Evaluate Pythia-6.9B @ step143000 and OLMo-7B-hf @ matched ~300B checkpoint
- Compute MMLU/HellaSwag ratio and ARC delta for both models
- Run bootstrap CI on ratio difference
- Generate all required figures

**Out of scope:**
- Training or fine-tuning any model
- Evaluating checkpoints other than the ~300B matched pair
- Modifying lm-evaluation-harness internals

---

## 4. Data Specification

### 4.1 Benchmark Datasets (Auto-Download)

| Dataset | Split | Size | Shot | Download |
|---------|-------|------|------|----------|
| MMLU | test | 14,042 questions, 57 subjects | 5-shot | auto (lm-eval) |
| HellaSwag | validation | 10,042 examples | 0-shot | auto (lm-eval) |
| ARC-Easy | test | 2,376 examples | 25-shot | auto (lm-eval) |
| ARC-Challenge | test | 1,172 examples | 25-shot | auto (lm-eval) |

**Total evaluation samples: ~27,632**
**No manual download required.** lm-evaluation-harness auto-downloads all datasets to `~/.cache/huggingface/datasets/`.

### 4.2 Model Checkpoints

| Model | HuggingFace ID | Revision | Approx Tokens |
|-------|----------------|----------|---------------|
| Pythia-6.9B | `EleutherAI/pythia-6.9b` | `step143000` | ~300B |
| OLMo-7B | `allenai/OLMo-7B-hf` | `step149531` (verify) | ~300B |

**Note:** OLMo revision must be verified at runtime using `huggingface_hub.list_repo_refs`. The step→token mapping uses OLMo's global batch size (~2M tokens/step).

---

## 5. Functional Requirements

### FR-1: Precondition Verification
- **FR-1.1:** Verify Pythia revision `step143000` exists on HuggingFace Hub
- **FR-1.2:** Verify OLMo matched revision exists and token count is within 10% of 300B
- **FR-1.3:** Run sanity check (single MMLU subject, 50-sample limit) on both models before full evaluation

### FR-2: Model Evaluation — Pythia-6.9B
- **FR-2.1:** Run lm-evaluation-harness on `EleutherAI/pythia-6.9b` @ `step143000`
- **FR-2.2:** Tasks: `mmlu` (5-shot), `hellaswag` (0-shot), `arc_easy` (25-shot), `arc_challenge` (25-shot)
- **FR-2.3:** Save full JSON results to `results/pythia-6.9b-300B/results.json`
- **FR-2.4:** Enable `--log_samples` for bootstrap resampling

### FR-3: Model Evaluation — OLMo-7B
- **FR-3.1:** Run lm-evaluation-harness on `allenai/OLMo-7B-hf` @ matched revision
- **FR-3.2:** Same tasks and shot configs as FR-2.2
- **FR-3.3:** Save full JSON results to `results/olmo-7b-300B/results.json`
- **FR-3.4:** Enable `--log_samples` for bootstrap resampling

### FR-4: Metric Computation
- **FR-4.1:** Compute `mmlu_hellaswag_ratio` = mean(MMLU subj acc) / HellaSwag acc for both models
- **FR-4.2:** Compute `arc_delta` = ARC-Challenge acc_norm - ARC-Easy acc for both models
- **FR-4.3:** Run bootstrap CI (n=1000 resamples of MMLU subjects) on ratio difference
- **FR-4.4:** Compute Cohen's d on ratio difference; compute one-sided p-value

### FR-5: Hypothesis Decision
- **FR-5.1:** Evaluate primary criterion: `olmo_ratio - pythia_ratio > 0.02` AND `p < 0.05` AND `Cohen's d > 0.2`
- **FR-5.2:** Evaluate secondary criterion: `olmo_arc_delta > pythia_arc_delta` (p < 0.10)
- **FR-5.3:** Output binary pass/fail with evidence summary

### FR-6: Visualization
- **FR-6.1:** Bar chart: MMLU, HellaSwag, ARC-Easy, ARC-Challenge absolute scores for both models
- **FR-6.2:** Bar chart with CI: MMLU/HellaSwag ratio and ARC delta for both models (primary gate metrics)
- **FR-6.3:** Heatmap: per-subject MMLU accuracy for both models (57 subjects × 2 models)
- **FR-6.4:** Bootstrap distribution histogram: ratio difference with threshold lines at 0 and 0.02
- **FR-6.5:** Save all figures to `docs/youra_research/h-e1/figures/`

---

## 6. Non-Functional Requirements

### 6.1 Reproducibility
- Fixed random seed: 42
- Pin lm-evaluation-harness version: `lm-eval==0.4.3` (or latest stable)
- All evaluation parameters logged to `results/eval_config.json`

### 6.2 Performance
- Target wall time: ≤ 4 hours per model on A100 80GB
- Use `--batch_size auto` for VRAM efficiency
- Sequential evaluation (Pythia first, then OLMo)

### 6.3 Hardware
- Minimum: 1× A100 80GB or 2× A40 48GB (for fp16 inference of 6.9B/7B models)
- OS: Linux, CUDA 11.8+

---

## 7. Dependencies

### 7.1 Python Packages

```
lm-eval==0.4.3
torch>=2.0.0
transformers>=4.40.0
huggingface_hub>=0.20.0
accelerate>=0.27.0
numpy>=1.24.0
scipy>=1.11.0
matplotlib>=3.7.0
seaborn>=0.12.0
pyyaml>=6.0
tqdm>=4.65.0
```

### 7.2 External Repositories (Reference Only)

| Repo | URL | Purpose |
|------|-----|---------|
| lm-evaluation-harness | https://github.com/EleutherAI/lm-evaluation-harness | Core evaluation framework |
| pythia | https://github.com/EleutherAI/pythia | Checkpoint step table |
| OLMo | https://github.com/allenai/OLMo | Training config for step→token mapping |

---

## 8. Success Criteria

| Criterion | Threshold | Type |
|-----------|-----------|------|
| Primary: ratio difference | > 0.02 absolute | MUST |
| Statistical: p-value | < 0.05 (one-sided bootstrap) | MUST |
| Effect size: Cohen's d | > 0.2 | MUST |
| Secondary: arc_delta direction | OLMo > Pythia | SHOULD |
| Code runs without error | Both evals complete | MUST |

**PoC Pass:** All MUST criteria met → H-E1 CONFIRMED → H-M1 through H-M4 unblocked.

---

## 9. Constraints

- Evaluation-only: no model training or fine-tuning
- Must use lm-evaluation-harness (not custom evaluation) for reproducibility
- Checkpoint selection must be within 10% of 300B tokens for both models
- All intermediate results must be saved for audit trail

---

## 10. Assumptions

- A5 (contamination): Dolma deduplication may have removed benchmark-adjacent content. This is noted as a confound but not controlled for in H-E1 (addressed in H-M hypotheses).
- Architecture differences (GPT-NeoX vs LLaMA-style) are treated as constant at this scale.
- lm-evaluation-harness produces reproducible results given fixed prompts and model weights.
