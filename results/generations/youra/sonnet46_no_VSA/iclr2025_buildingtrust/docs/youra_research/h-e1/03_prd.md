# Product Requirements Document: H-E1

**Hypothesis:** H-E1 — Transformer Architecture Family Δ*-Vector Fingerprinting (EXISTENCE)
**Date:** 2026-07-29
**Author:** Anonymous
**Phase:** Phase 3 Implementation Planning
**Tier:** LIGHT (EXISTENCE hypothesis, ≤15 tasks)

---

## 1. Executive Summary

This PRD specifies implementation requirements for H-E1, an EXISTENCE hypothesis testing whether transformer models grouped by architecture family (encoder-only, decoder-only, encoder-decoder) exhibit characteristic Δ*-vector profiles across adversarial attack types, with greater within-family similarity than between-family similarity. The experiment combines standard HuggingFace GLUE fine-tuning with custom Δ* computation and statistical analysis (permutation MANOVA, LOMO classification).

**Gate Condition:** Architecture × AttackType interaction p < 0.05 (bootstrap CI) AND permutation MANOVA η² > 0.15 in ≥50% of reliable attack categories.

---

## 2. Problem Statement

Transformer architecture families differ in pretraining objectives and attention mechanisms. Whether these differences produce characteristic robustness signatures (Δ*-vector profiles) across adversarial attack types is unknown. H-E1 tests for existence of this pattern using 8-9 scale-matched models across 3 families evaluated on AdvGLUE/ANLI-R3/CheckList adversarial benchmarks.

---

## 3. Scope

**In Scope:**
- GLUE fine-tuning pipeline for 8-9 transformer models
- Adversarial evaluation on AdvGLUE (5 tasks × 14 attack categories), ANLI-R3 (1,200 examples), CheckList behavioral tests
- Δ*-vector computation per model per attack category
- Statistical analysis: mixed-effects model, permutation MANOVA, bootstrap CI, LOMO classifier
- Reliability filtering (split-half r≥0.7, n≥50)
- Required visualizations (Δ* heatmap, reliability scatterplot, MANOVA η² bar chart, LOMO confusion matrix)

**Out of Scope:**
- Novel model architectures (existing checkpoints only)
- Multi-seed experiments (single seed=42 for PoC)
- Hyperparameter search
- Phase 5 baseline repository comparison (separate phase)

---

## 4. Data Specification

### 4.1 Primary Datasets

| Dataset | Source | Split | Size | Download |
|---------|--------|-------|------|----------|
| AdvGLUE | `AI-Secure/adv_glue` (HuggingFace) | validation per task | ~500-3000/task | Auto (HF datasets) |
| ANLI-R3 | `facebook/anli` (HuggingFace) | test_r3 | 1,200 | Auto (HF datasets) |
| CheckList | `marcotcr/checklist` (pip) | behavioral suites | Variable | Auto (pip install) |
| GLUE (clean) | `glue` (HuggingFace) | validation per task | Standard splits | Auto (HF datasets) |

All datasets are auto-download — no manual download tasks required.

### 4.2 Attack Partition Mapping

| Partition | Source | Attack Type | Surrogate |
|-----------|--------|-------------|-----------|
| A (C1-C5) | AdvGLUE word-level | Word substitution, char noise, knowledge-guided | Encoder-surrogate |
| B (C6-C7) | AdvGLUE sentence-level | Distraction, syntactic manipulation | Encoder-surrogate |
| C (C8-C11) | AdvGLUE human + ANLI-R3 + CheckList | Human-crafted | Surrogate-free |

### 4.3 Data Loading Code

```python
from datasets import load_dataset

# AdvGLUE
adv_glue = {
    task: load_dataset("AI-Secure/adv_glue", f"adv_{task}")["validation"]
    for task in ["sst2", "mnli", "qqp", "qnli", "rte"]
}

# GLUE clean baselines
glue_clean = {
    task: load_dataset("glue", task)["validation"]
    for task in ["sst2", "mnli", "qqp", "qnli", "rte"]
}

# ANLI-R3
anli_r3 = load_dataset("facebook/anli", split="test_r3")

# CheckList: pip install checklist; load suite files
```

---

## 5. Model Specification

### 5.1 Target Models

| Family | Model | Scale | HuggingFace ID | Priority |
|--------|-------|-------|----------------|----------|
| Encoder-only | BERT-base | 110M | `bert-base-uncased` | Required |
| Encoder-only | RoBERTa-base | 125M | `roberta-base` | Required |
| Encoder-only | ELECTRA-base | 110M | `google/electra-base-discriminator` | Required |
| Encoder-only | ALBERT-base-v2 | ~110M | `albert-base-v2` | Required |
| Decoder-only | GPT-2 | 117M | `gpt2` | Required |
| Decoder-only | OPT-125M | 125M | `facebook/opt-125m` | Required |
| Decoder-only | OPT-350M | 350M | `facebook/opt-350m` | Optional (risk mitigation) |
| Encoder-decoder | T5-base | 250M | `t5-base` | Required |
| Encoder-decoder | BART-base | 140M | `facebook/bart-base` | Required |

### 5.2 Model Loading

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer

model = AutoModelForSequenceClassification.from_pretrained(
    model_id, num_labels=num_task_labels
)
tokenizer = AutoTokenizer.from_pretrained(model_id)
```

**Note:** Pre-trained GLUE checkpoints available for BERT/RoBERTa (e.g., `textattack/bert-base-uncased-SST-2`). GPT-2, T5, BART, ELECTRA, ALBERT require fine-tuning from scratch.

---

## 6. Functional Requirements

### FR-1: Environment Setup
- Install all required Python packages (transformers, datasets, scipy, statsmodels, sklearn, checklist)
- Verify GPU availability

### FR-2: GLUE Fine-tuning Pipeline
- Fine-tune all 8-9 models on 5 GLUE tasks using HuggingFace Trainer API
- Standard protocol: AdamW optimizer, lr=2e-5 (encoder) / 5e-5 (decoder) / 1e-4 (enc-dec), batch=32/16, 3-5 epochs
- Save fine-tuned checkpoints per model per task
- Record clean accuracy on GLUE validation splits

### FR-3: Adversarial Evaluation
- Evaluate all fine-tuned models on AdvGLUE (5 tasks × 14 attack categories)
- Evaluate relevant models on ANLI-R3 (NLI task)
- Evaluate models on CheckList behavioral test suites
- Record per-model per-attack-category adversarial accuracy

### FR-4: Δ*-Vector Computation
- Compute Δ* = (clean_acc − adv_acc) / clean_acc per model per attack category
- Apply reliability filter: retain categories with split-half r ≥ 0.7 AND n ≥ 50
- Construct Δ*-vector per model over reliable categories

### FR-5: Statistical Analysis
- Mixed-effects model: `Δ* ~ ArchFamily × AttackType + Objective + Tokenizer + CleanAccuracy + (1|Model)` via statsmodels
- Bootstrap 1,000 iterations for confidence intervals on interaction effect
- Permutation MANOVA: compute η² per reliable attack category
- LOMO classifier: leave-one-model-out nearest-neighbor (cosine, k=1) on Δ*-vectors

### FR-6: Visualization
- Gate Metrics Comparison: Δ*-vector profiles per architecture family (bar/heatmap)
- Δ*-vector heatmap: models × attack categories
- Split-half reliability scatterplot: r per attack category
- MANOVA η² bar chart with 0.15 threshold line
- LOMO classifier confusion matrix (3×3)
- Save all figures to `h-e1/figures/`

### FR-7: Results Persistence
- Save all results to `h-e1/results/` (JSON format)
- Save fine-tuned checkpoints to `h-e1/checkpoints/`

---

## 7. Non-Functional Requirements

### 7.1 Performance
- Full pipeline should complete within available compute budget (GPU required for fine-tuning)
- Fallback: Use pre-trained GLUE checkpoints from HuggingFace Hub for BERT/RoBERTa to skip fine-tuning

### 7.2 Reproducibility
- Fixed seed=42 for all random operations
- Single-seed run (PoC mode)
- All results reproducible given same checkpoints

### 7.3 Code Quality
- Modular design: separate modules for data loading, fine-tuning, evaluation, analysis, visualization
- Each module independently runnable
- Clear logging at each stage

---

## 8. Dependencies

### 8.1 Python Packages

```
transformers>=4.35.0
datasets>=2.14.0
torch>=2.0.0
scipy>=1.11.0
statsmodels>=0.14.0
scikit-learn>=1.3.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
checklist>=0.0.11
pandas>=2.0.0
accelerate>=0.24.0
```

### 8.2 External References

- Official AdvGLUE evaluation script: https://github.com/AI-secure/adversarial-glue (evaluate.py)
- HuggingFace GLUE fine-tuning: run_glue.py (standard HF script)
- EMNLP 2023 robustness metric: ACL Anthology 2305.14453

### 8.3 Hardware
- GPU strongly recommended for fine-tuning (8-9 models × 5 tasks)
- CPU-only possible for analysis pipeline only (using pre-trained checkpoints)

---

## 9. Success Criteria

### 9.1 PoC Pass Conditions
1. Code runs without error (full pipeline: fine-tuning → adversarial evaluation → statistical analysis)
2. η² > 0 for Architecture × AttackType in ≥1 reliable attack category (effect direction exists)
3. LOMO accuracy > 33% (above 3-class chance baseline)

### 9.2 Full Gate Conditions
- Architecture × AttackType interaction p < 0.05 (bootstrap CI excludes zero)
- Permutation MANOVA η² > 0.15 in ≥50% of reliable attack categories

---

## 10. File Structure

```
h-e1/
├── 02c_experiment_brief.md    (input)
├── 03_prd.md                  (this file)
├── 03_architecture.md         (architecture design)
├── 03_logic.md                (API signatures)
├── 03_config.md               (configuration)
├── 03_tasks.yaml              (implementation tasks)
├── code/                      (implementation)
│   ├── data_loader.py
│   ├── fine_tuner.py
│   ├── evaluator.py
│   ├── delta_star.py
│   ├── statistical_analysis.py
│   ├── visualizer.py
│   └── run_experiment.py
├── checkpoints/               (fine-tuned model checkpoints)
├── results/                   (JSON result files)
└── figures/                   (output visualizations)
```

---

## 11. Phase 2C Completeness Check

| Phase 2C Item | PRD Section | Status |
|---------------|-------------|--------|
| Baseline models (all 8-9) | FR-2, Section 5.1 | ✅ |
| AdvGLUE dataset (all 5 tasks, 14 attack categories) | Section 4.1-4.2 | ✅ |
| ANLI-R3 dataset | Section 4.1 | ✅ |
| CheckList dataset | Section 4.1 | ✅ |
| Δ* metric computation | FR-4 | ✅ |
| Reliability filter | FR-4 | ✅ |
| Mixed-effects model | FR-5 | ✅ |
| Bootstrap CI | FR-5 | ✅ |
| Permutation MANOVA η² | FR-5 | ✅ |
| LOMO classifier | FR-5 | ✅ |
| Required visualizations | FR-6 | ✅ |
| Ablation variants | N/A (EXISTENCE) | ✅ |

**Phase 2C completeness: PASSED — all items captured in PRD.**
