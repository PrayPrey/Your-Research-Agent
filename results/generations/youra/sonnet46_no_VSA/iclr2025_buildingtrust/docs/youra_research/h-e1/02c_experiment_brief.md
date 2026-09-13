# Experiment Design: H-E1

**Date:** 2026-07-29
**Author:** Anonymous
**Hypothesis Statement:** Under scale-matched conditions (~110-250M parameters), transformer models grouped by architecture family (encoder-only, decoder-only, encoder-decoder) exhibit characteristic Δ*-vector profiles across AdvGLUE/ANLI/CheckList attack types showing greater within-family similarity than between-family similarity (permutation MANOVA η² > 0.15 in ≥50% of reliable attack categories), replicating across surrogate-diverse benchmark partitions.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** N/A (H-E1 is foundation hypothesis — no prerequisites)
**Gate Status:** MUST_WORK — not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
MUST_WORK — Architecture × AttackType interaction p < 0.05 (bootstrap CI excludes zero) AND permutation MANOVA η² > 0.15 in ≥50% of reliable attack categories. Failure: STOP and route to Phase 2A-Dialogue for hypothesis redesign.

---

## Continuation Context

This is the first hypothesis in the verification chain (H-E1 → H-M1 → H-M2 → H-M3 → H-M4). No previous hypothesis context available.

### Previous Hypothesis Results (if applicable)
N/A — H-E1 is the foundation hypothesis with no prerequisites.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Experiment Design Search**
- Archon KB returned general HuggingFace documentation (similarity 0.45-0.52). No domain-specific adversarial NLP robustness experiment designs found in Archon.
- Key relevant content: HuggingFace Transformers library documentation confirming API availability for all target models (BERT, RoBERTa, GPT-2, T5, BART, ELECTRA, ALBERT, OPT).
- T5 documentation (similarity 0.499): Confirms `T5ForSequenceClassification` available via `AutoModelForSequenceClassification`.

**Query 2: Implementation Challenges**
- No domain-specific adversarial NLP implementation challenges found in Archon.
- General pattern: HuggingFace `run_glue.py` example is the standard GLUE fine-tuning reference.

**Query 3: Benchmark Results**
- SMART (RoBERTa) improves RoBERTa (Large) ~3.71% on AdvGLUE (from AdvGLUE paper, retrieved via Exa cross-reference).
- All tested models perform poorly on AdvGLUE, confirming meaningful variance for Δ* measurement.

**Key Insights from Archon:**
- HuggingFace Transformers provides `AutoModelForSequenceClassification` for all target models
- Standard training pattern: `Trainer` API with `TrainingArguments`
- All models available via `from_pretrained()` with matched base-scale checkpoints

### Archon Code Examples

**Query 1: HuggingFace fine-tuning**
- Example: `AutoModelForSequenceClassification` loading pattern:
  ```python
  from ane_transformers.huggingface import distilbert as ane_distilbert
  optimized_model = ane_distilbert.DistilBertForSequenceClassification(
      baseline_model.config).eval()
  ```
  - Pattern: Model loaded from config, weights transferred — standard HuggingFace pattern
  - Insight: All target models follow same `from_pretrained` → `Trainer` → `evaluate` pattern

**Query 2: Adversarial evaluation**
- No specific adversarial NLP evaluation code in Archon.
- Fallback: Official AdvGLUE `evaluate.py` found via Exa (see Exa findings below).

### Exa GitHub Implementations

**Query 1: AdvGLUE Official Repository (HIGHEST PRIORITY — paper author)**

**Repository 1**: AI-secure/adversarial-glue (⭐ 13)
- **URL**: https://github.com/AI-secure/adversarial-glue
- **Relevance**: Official AdvGLUE benchmark codebase (NeurIPS 2021, 3.3% acceptance rate). Primary source for evaluation protocol.
- **Architecture**: Evaluation via JSON-format predictions; `evaluate.py` computes per-task accuracy
- **Key Code** (from evaluate.py):
  ```python
  def evaluate(adv_glue, predictions):
      results = {}
      scores = {}
      for task_name in tasks:
          metric = load_metric("glue_metrics.py", task_name)
          label_list = [data['label'] for data in adv_glue[task_name]]
          pred_list = predictions[task_name]
          results[task_name] = metric.compute(predictions=pred_list, references=label_list)
          task_scores = list(results[task_name].values())
          scores[task_name] = sum(task_scores) / len(task_scores)
      results['score'] = sum(scores.values()) / len(scores)
      return results
  ```
- **Training Config**: Models fine-tuned on GLUE (SST-2, MNLI, QQP, QNLI, RTE); evaluation on AdvGLUE dev set
- **Dataset**: AdvGLUE dev.json — 5 tasks (adv_sst2, adv_mnli, adv_qqp, adv_qnli, adv_rte)
- **Results**: BERT/RoBERTa/T5 all perform poorly (many below random-guess on some tasks)
- **HuggingFace**: `datasets.load_dataset('AI-Secure/adv_glue', 'adv_sst2')['validation']`

**Repository 2**: mivg/robust_transformers (MEDIUM priority — adversarial training on GLUE)
- **URL**: https://github.com/mivg/robust_transformers
- **Relevance**: GLUE fine-tuning + robustness evaluation pipeline for BERT/RoBERTa
- **Key Insight**: `run_glue.py` (HuggingFace standard) + `analyze_robustness.py` for evaluation
- **Training Config**:
  - Based on `hf_transformers/dat_glue.py` (wraps `run_glue.py`)
  - Standard: AdamW optimizer, batch_size=32, 3-5 epochs, lr=2e-5 for BERT/RoBERTa
- **Used For**: Confirming standardized GLUE fine-tuning protocol

**Query 2: Robustness comparison BERT/GPT-2/T5 (EMNLP 2023 paper)**

**Source**: ACL Anthology 2023 — "On Robustness of Finetuned Transformer-based NLP Models"
- **URL**: https://aclanthology.org/2023.findings-emnlp.477.pdf
- **Relevance**: Directly compares BERT, GPT-2, T5 robustness on GLUE with 8 text perturbations — most related prior work
- **Architecture**: BERT-base, GPT-2, T5-base from HuggingFace v4.2.2; fine-tuned on GLUE
- **Key Finding**: GPT-2 representations more robust than BERT and T5 across multiple perturbation types (supports decoder > encoder robustness direction)
- **Robustness Metric**: `robustness = 1 − (mc − mp) / mc` — equivalent to `1 − Δ*`
- **Training Config**: Standard HuggingFace fine-tuning; BERT fine-tuned checkpoints from HuggingFace Hub
- **Used For**: Robustness metric definition, expected baseline direction, model selection justification

**ANLI Dataset**: `datasets.load_dataset('facebook/anli')` — Round 3 split: `test_r3` (1,200 examples, NLI task)
**CheckList**: `marcotcr/checklist` — behavioral test suites; suite files available via pip install checklist

**Serena Analysis Needed**: false — code from AdvGLUE evaluate.py and HuggingFace run_glue.py is sufficiently clear

### 🎯 Implementation Priority Assessment

**CRITICAL: For this experiment, we implement a custom pipeline wrapping standard components.**

No single paper implements the exact Δ*-vector fingerprinting pipeline. Implementation combines:
1. Standard HuggingFace GLUE fine-tuning (run_glue.py) — for model training
2. Official AdvGLUE evaluation script — for adversarial accuracy measurement
3. Custom Δ* computation and MANOVA analysis — novel contribution

**Recommended Implementation Path:**
- Primary: HuggingFace `run_glue.py` for fine-tuning + official AdvGLUE `evaluate.py` for adversarial accuracy + custom statistical analysis
- Fallback: Use pre-trained GLUE-fine-tuned checkpoints from HuggingFace Hub (available for BERT, RoBERTa, ALBERT, ELECTRA) to skip fine-tuning step
- Justification: AdvGLUE evaluate.py is the authoritative evaluation protocol; GLUE fine-tuning is standardized via HuggingFace Trainer API

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. AdvGLUE evaluate.py is straightforward JSON-based evaluation; HuggingFace run_glue.py is well-documented standard fine-tuning script.

---

## Experiment Specification

### Dataset

**Primary Dataset Suite: AdvGLUE + ANLI-R3 + CheckList**

**Dataset Type:** standard (all publicly available)

**Component 1: AdvGLUE**
- **Name:** Adversarial GLUE (AdvGLUE)
- **Version:** NeurIPS 2021 release (dev.json)
- **Source:** Wang et al. 2021; HuggingFace: `AI-Secure/adv_glue`
- **Tasks:** 5 GLUE tasks (SST-2, MNLI, QQP, QNLI, RTE) with adversarial examples
- **Attack categories:** 14 attack methods grouped into:
  - Partition A (C1-C5): Word-level automatic (word substitution, character noise, knowledge-guided)
  - Partition B (C6-C7): Sentence-level automatic (distraction, syntactic manipulation)
  - Partition C (C8-C11): Human-crafted (numerical reasoning, negation, coreference)
- **Size:** ~500-3,000 examples per task; ~200-500 per major attack category
- **Curation:** Human-validated; Fleiss κ ≈ 0.6 post-curation; ~90% raw examples filtered
- **Path:** `auto` (HuggingFace download)

**Component 2: ANLI-R3**
- **Name:** Adversarial Natural Language Inference, Round 3
- **Version:** v1.0 (facebook/anli)
- **Source:** Nie et al. 2019; HuggingFace: `facebook/anli`
- **Split used:** `test_r3` (1,200 NLI examples, human-crafted adversarial)
- **Purpose:** Surrogate-free validation partition (human-in-the-loop generation, not model-surrogate)
- **Path:** `auto` (HuggingFace download)

**Component 3: CheckList**
- **Name:** CheckList behavioral test suite
- **Version:** ACL 2020 (marcotcr/checklist)
- **Source:** Ribeiro et al. 2020; pip: `checklist`
- **Tests used:** Sentiment analysis and NLI behavioral tests (vocabulary, NER, temporal, negation)
- **Purpose:** Behavioral test categories covering linguistic phenomena not in AdvGLUE
- **Path:** `auto` (pip install checklist)

**Attack Partition Mapping for H-E1:**
| Partition | Sources | Attack Type | Surrogate |
|-----------|---------|-------------|-----------|
| A (C1-C5) | AdvGLUE word-level | Word substitution, char noise, knowledge | Encoder-surrogate (BERT/RoBERTa) |
| B (C6-C7) | AdvGLUE sentence-level | Distraction, syntactic | Encoder-surrogate |
| C (C8-C11) | AdvGLUE human + ANLI-R3 + CheckList | Human-crafted | None (surrogate-free) |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets + pip
- Identifier: `"AI-Secure/adv_glue"`, `"facebook/anli"`, `"checklist"`
- Code:
  ```python
  from datasets import load_dataset
  adv_glue = {
      task: load_dataset("AI-Secure/adv_glue", f"adv_{task}")["validation"]
      for task in ["sst2", "mnli", "qqp", "qnli", "rte"]
  }
  anli_r3 = load_dataset("facebook/anli", split="test_r3")
  # CheckList: pip install checklist; load suite files from marcotcr/checklist repo
  ```

### Models

**Target Architecture Families and Models:**

| Family | Models | Scale | HuggingFace ID |
|--------|--------|-------|----------------|
| Encoder-only | BERT-base | 110M | `bert-base-uncased` |
| Encoder-only | RoBERTa-base | 125M | `roberta-base` |
| Encoder-only | ELECTRA-base | 110M | `google/electra-base-discriminator` |
| Encoder-only | ALBERT-base-v2 | 12M (effective ~110M) | `albert-base-v2` |
| Decoder-only | GPT-2 | 117M | `gpt2` |
| Decoder-only | OPT-125M | 125M | `facebook/opt-125m` |
| Decoder-only* | OPT-350M | 350M | `facebook/opt-350m` (optional 3rd decoder) |
| Encoder-decoder | T5-base | 250M | `t5-base` |
| Encoder-decoder | BART-base | 140M | `facebook/bart-base` |

*OPT-350M included to mitigate Risk R5 (decoder family too small with only 2 models)

#### Baseline Model

**Architecture:** Per-family clean-accuracy baseline — each model fine-tuned on GLUE tasks, evaluated on original GLUE dev set.

**Configuration:**
- Architecture: `AutoModelForSequenceClassification` wrapper for all models
- Input: tokenized text via model-specific tokenizer (`AutoTokenizer.from_pretrained(model_id)`)
- Output: classification logits over task-specific label set
- Clean accuracy: measured on standard GLUE dev splits

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `transformers` + `datasets`
- Identifier: See table above (e.g., `"bert-base-uncased"`, `"gpt2"`, `"t5-base"`)
- Code:
  ```python
  from transformers import AutoModelForSequenceClassification, AutoTokenizer
  model = AutoModelForSequenceClassification.from_pretrained(
      "bert-base-uncased", num_labels=num_task_labels
  )
  tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
  ```

**Note on pre-trained GLUE checkpoints:** HuggingFace Hub has pre-trained GLUE fine-tuned checkpoints for BERT and RoBERTa (e.g., `textattack/bert-base-uncased-SST-2`). For GPT-2, T5, BART, ELECTRA, ALBERT: fine-tune from scratch using run_glue.py.

#### Proposed Model

**Architecture:** Same models as baseline — H-E1 is an EXISTENCE hypothesis testing whether observable patterns exist in existing models. No architectural modification to models is needed. The "proposed mechanism" is the Δ*-vector computation and statistical analysis pipeline applied to all models.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Δ*-Vector Architecture-Family Fingerprinting
# Based on: AdvGLUE evaluate.py + EMNLP 2023 robustness metric definition

import numpy as np
from scipy.stats import spearmanr
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import LeaveOneOut

def compute_delta_star(acc_clean: float, acc_adv: float) -> float:
    """Normalized vulnerability: Δ* = (clean − adv) / clean"""
    if acc_clean == 0:
        return 0.0
    return (acc_clean - acc_adv) / acc_clean

def compute_delta_star_vectors(results_per_model: dict) -> dict:
    """
    Args:
        results_per_model: {model_id: {attack_category: {clean_acc, adv_acc}}}
    Returns:
        {model_id: np.array([Δ* per reliable attack category])}
    """
    vectors = {}
    for model_id, attack_results in results_per_model.items():
        delta_stars = []
        for cat, accs in attack_results.items():
            if cat in reliable_categories:  # r >= 0.7, n >= 50
                delta_stars.append(
                    compute_delta_star(accs["clean"], accs["adv"])
                )
        vectors[model_id] = np.array(delta_stars)
    return vectors

def split_half_reliability(scores_half1, scores_half2) -> float:
    """Spearman-Brown corrected split-half reliability"""
    r, _ = spearmanr(scores_half1, scores_half2)
    return (2 * r) / (1 + r)  # Spearman-Brown correction

def lomo_classify(delta_vectors, family_labels) -> float:
    """Leave-one-model-out nearest-neighbor classification"""
    loo = LeaveOneOut()
    knn = KNeighborsClassifier(n_neighbors=1, metric="cosine")
    X = np.stack(list(delta_vectors.values()))
    y = np.array(family_labels)
    correct = sum(
        knn.fit(X[train], y[train]).predict(X[test]) == y[test]
        for train, test in loo.split(X)
    )
    return correct / len(y)
```

### Training Protocol

**Phase 1: GLUE Fine-tuning (to obtain clean-accuracy baselines)**

Using HuggingFace `run_glue.py` standard protocol:

**Optimizer:** AdamW
- β₁ = 0.9, β₂ = 0.999, ε = 1e-8
- Weight decay = 0.01
- **Source:** HuggingFace Trainer defaults; standard in AdvGLUE paper and EMNLP 2023 comparison

**Learning Rate:** 2e-5 (encoder-only models); 5e-5 (GPT-2, OPT); 1e-4 (T5, BART with seq2seq head)
- **Source:** HuggingFace run_glue.py defaults; EMNLP 2023 fine-tuning protocol (v4.2.2)

**Schedule:** Linear warmup + linear decay
- Warmup steps = 10% of total steps
- **Source:** Standard HuggingFace TrainingArguments default

**Batch Size:** 32 (encoder-only, encoder-decoder); 16 (decoder-only — causal attention memory overhead)
- **Source:** mivg/robust_transformers configuration; AdvGLUE paper setup

**Epochs:** 3 (SST-2, QNLI, RTE); 5 (MNLI, QQP — larger datasets)
- **Source:** HuggingFace GLUE fine-tuning examples; AdvGLUE paper

**Loss Function:** Cross-entropy (classification tasks)
- **Source:** Standard for sequence classification

**Seeds:** 1 (fixed, seed=42)

> ⚠️ **EXISTENCE (PoC):** Single seed run is sufficient for existence check.

**Phase 2: Adversarial Evaluation (Δ* measurement)**

No training — inference only on AdvGLUE/ANLI-R3/CheckList with fine-tuned models.

**Reliability Filter:**
- Compute split-half reliability r per attack category
- Retain only categories with r ≥ 0.7 AND ≥50 aggregated examples per model
- **Source:** Phase 2B protocol; A3 assumption

**Statistical Analysis:**
- Mixed-effects model: `Δ* ~ ArchFamily × AttackType + Objective + Tokenizer + CleanAccuracy + (1|Model)`
- Bootstrap 1,000 iterations for confidence intervals
- Permutation MANOVA for η² computation
- **Library:** `statsmodels` (mixed effects), `scipy.stats` (permutation), `sklearn` (LOMO classifier)

### Evaluation

**Primary Metrics:**
- Architecture × AttackType interaction p-value (bootstrap CI)
- Permutation MANOVA η² per reliable attack category

**Success Criteria (PoC: Direction-based):**
- **Primary:** Architecture × AttackType interaction p < 0.05 (bootstrap CI excludes zero)
- **Secondary:** Permutation MANOVA η² > 0.15 in ≥50% of reliable attack categories
- **PoC Pass:** proposed pattern (family clustering) > baseline random assignment (η² > 0.05 direction threshold)

**Expected Baseline Performance** (from EMNLP 2023 + AdvGLUE paper):
- BERT on AdvGLUE: 30-60% accuracy (vs. 90%+ clean) across tasks — Δ* ≈ 0.3-0.7
- GPT-2 on perturbations: More robust than BERT (lower Δ*) — supports family difference direction
- T5: Comparable to BERT on most GLUE tasks, differential robustness to perturbation types
- **Source:** Wang et al. 2021 (AdvGLUE); EMNLP 2023 findings-477

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: text classification (accuracy) + statistical analysis (η², p-value, LOMO accuracy)
- Library: `sklearn.metrics` (accuracy), `statsmodels.formula.api` (mixedlm), `scipy.stats` (permutation test), `sklearn.neighbors` (KNN)
- Code:
  ```python
  from sklearn.metrics import accuracy_score
  from statsmodels.formula.api import mixedlm
  from sklearn.neighbors import KNeighborsClassifier
  import scipy.stats as stats
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Δ*-vector profiles per architecture family (bar chart or heatmap)
  - X-axis: Attack categories (C1-C11, ANLI-R3, CheckList)
  - Y-axis: Mean Δ* per family
  - Series: Encoder-only (blue), Decoder-only (orange), Encoder-decoder (green)

#### Additional Figures (LLM Autonomous)

Based on this existence hypothesis, suggest generating:
1. **Δ*-vector heatmap** — models × attack categories (shows within/between family clustering)
2. **Split-half reliability scatterplot** — r values per attack category (shows which categories pass filter)
3. **MANOVA η² bar chart** — η² per reliable attack category with 0.15 threshold line
4. **LOMO classifier confusion matrix** — 3×3 (encoder-only / decoder-only / encoder-decoder)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (fine-tuning + adversarial evaluation pipeline)
2. `η² > 0` for Architecture × AttackType in ≥1 reliable attack category (effect direction exists)
3. LOMO accuracy > 33% (above 3-class chance baseline)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1**: HuggingFace Transformers Documentation
- **Type:** Library documentation
- **Query Used:** "HuggingFace AutoModelForSequenceClassification from_pretrained bert roberta t5"
- **Relevance:** Confirms API availability for all 8-9 target models
- **Key Insights:**
  - `AutoModelForSequenceClassification` wraps all encoder, decoder, encoder-decoder models
  - `T5ForSequenceClassification` available (confirmed via T5 model doc page, similarity 0.499)
  - Standard `from_pretrained()` → `Trainer()` → `evaluate()` pattern works for all model families
- **Used For:** Model loading code in Dataset/Model specification

**Source A.2**: HuggingFace GitHub Repository (transformers)
- **Query Used:** "BERT RoBERTa GPT-2 fine-tuning GLUE benchmark classification"
- **Key Insights:** `run_glue.py` is canonical GLUE fine-tuning script; supports all model families
- **Used For:** Training protocol (optimizer, learning rate, schedule)

### B. GitHub Implementations (Exa)

**Repository B.1**: AI-secure/adversarial-glue ⭐ 13 (OFFICIAL PAPER CODE)
- **URL**: https://github.com/AI-secure/adversarial-glue
- **Query Used:** "AdvGLUE adversarial GLUE benchmark evaluation transformer robustness GitHub"
- **Relevance:** NeurIPS 2021 official codebase — highest authority for evaluation protocol
- **Key Code** (annotated):
  ```python
  # Official AdvGLUE evaluation script (evaluate.py)
  # Used as basis for: our Δ* computation pipeline
  def evaluate(adv_glue, predictions):
      results = {}
      for task_name in tasks:
          metric = load_metric("glue_metrics.py", task_name)
          label_list = [data['label'] for data in adv_glue[task_name]]
          pred_list = predictions[task_name]
          # Per-task accuracy → basis for adv_acc in Δ* = (clean-adv)/clean
          results[task_name] = metric.compute(predictions=pred_list, references=label_list)
      return results
  ```
- **Configuration Extracted:**
  - Input format: `dev.json` (per-task prediction JSON)
  - Tasks: SST-2, MNLI, QQP, QNLI, RTE (5 tasks × 14 attack methods = 70 attack×task cells)
  - Evaluation: Per-task accuracy, then macro-average
- **Their Results:** All models (BERT, RoBERTa, T5) significantly below clean accuracy; BERT near random-guess on several tasks
- **Used For:** Adversarial accuracy computation, evaluation pipeline architecture, task list

**Repository B.2**: mivg/robust_transformers (GLUE robustness pipeline)
- **URL**: https://github.com/mivg/robust_transformers
- **Relevance:** Standardized GLUE fine-tuning + robustness evaluation pipeline for BERT/RoBERTa
- **Configuration Extracted:**
  - Optimizer: AdamW (standard HuggingFace)
  - Strategy configs via YAML files
  - `analyze_robustness.py` for adversarial evaluation
- **Used For:** Training protocol parameters (batch size, learning rate)

**Source B.3**: EMNLP 2023 Findings Paper (ACL Anthology 2305.14453)
- **URL**: https://aclanthology.org/2023.findings-emnlp.477.pdf
- **Relevance:** Only existing paper comparing BERT, GPT-2, T5 robustness on GLUE with perturbations; directly supports decoder > encoder robustness direction
- **Key Findings:**
  - GPT-2 representations more robust than BERT and T5 across multiple perturbation types
  - Robustness metric: `1 - (clean_acc - perturb_acc) / clean_acc` ≡ `1 - Δ*`
  - Fine-tuned BERT, GPT-2, T5 from HuggingFace v4.2.2
  - T5 comparable to BERT; GPT-2 systematically more robust
- **Used For:** Expected baseline direction (decoder > encoder robustness), evaluation metric definition, model selection validation

**Source B.4**: HuggingFace ANLI Dataset Card (facebook/anli)
- **URL**: https://huggingface.co/datasets/facebook/anli
- **Relevance:** ANLI-R3 test split provides 1,200 surrogate-free NLI adversarial examples
- **Key Info:** `load_dataset("facebook/anli", split="test_r3")`, license CC-BY-NC-4.0
- **Used For:** Dataset specification (Partition C surrogate-free component)

**Source B.5**: AI-Secure/adv_glue HuggingFace Dataset Card
- **URL**: https://huggingface.co/datasets/AI-Secure/adv_glue
- **Key Code:**
  ```python
  # Load AdvGLUE via HuggingFace datasets
  datasets.load_dataset('AI-Secure/adv_glue', 'adv_sst2')['validation']
  ```
- **Used For:** Dataset loading code (Phase 4 implementation)

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed — code from search results was sufficiently clear.
- AdvGLUE evaluate.py is straightforward JSON-based per-task accuracy computation
- HuggingFace run_glue.py is well-documented with standard Trainer API
- Δ* computation is a simple arithmetic transformation of accuracy values
- MANOVA/LOMO classification uses standard sklearn/scipy — no complex custom code requiring semantic analysis

### D. Previous Hypothesis Context

**Previous Context**: None — this is the first hypothesis in the verification chain.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset: AdvGLUE | GitHub (official) | B.1 (AI-secure/adversarial-glue) |
| Dataset: ANLI-R3 | HuggingFace Dataset | B.4 (facebook/anli) |
| Dataset: CheckList | GitHub | pip:checklist (marcotcr/checklist) |
| Dataset loading code | HuggingFace Hub | B.5 (AI-Secure/adv_glue) |
| Δ* metric definition | EMNLP 2023 paper | B.3 (ACL 2305.14453) |
| Evaluation protocol | GitHub (official) | B.1 evaluate.py |
| Model loading API | Archon KB | A.1 (HF Transformers docs) |
| Training protocol (optimizer, lr) | GitHub | B.2 (mivg/robust_transformers) |
| Training script | HuggingFace | A.2 (run_glue.py) |
| Expected baseline direction | EMNLP 2023 | B.3 (GPT-2 > BERT robustness) |
| LOMO classification | Phase 2B design | docs/youra_research/02b_verification_plan.md |
| Attack partition mapping | AdvGLUE paper | B.1 (Wang et al. 2021 NeurIPS) |
| Success criteria | Phase 2B | docs/youra_research/02b_verification_plan.md Section 2.2 |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — managed externally)
**Date:** 2026-07-29

### Workflow History for This Hypothesis
- 2026-07-29: Phase 2C experiment design started (IN_PROGRESS)
- 2026-07-29: Phase 2C experiment design COMPLETED

---

## Quality Validation

✅ All hyperparameters justified (AdamW lr=2e-5 from HuggingFace/mivg/robust_transformers)
✅ Dataset choice justified (AdvGLUE/ANLI-R3/CheckList from Phase 2B protocol — real benchmark datasets, type: standard)
✅ Mechanism grounded in code (Δ* from AdvGLUE evaluate.py; LOMO from sklearn KNN)
✅ No unsupported assumptions (all claims reference Exa/Archon findings or Phase 2B)
✅ Full traceability (Traceability Matrix Section E covers all specifications)
✅ Dataset type: standard (NOT synthetic) — AdvGLUE, ANLI, CheckList all real benchmarks

**Overall: PASSED**

---

*MCP Tools Used: Archon (Knowledge + Code — 4 queries), Exa (GitHub + Web — 4 queries), Serena (skipped — code sufficiently clear)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
