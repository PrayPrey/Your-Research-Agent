# Experiment Brief: H-E1 — Architecture-Family Δ*-Vector Profiles Exist and Are Reliable

**Hypothesis ID:** h-e1
**Phase:** 2C — Experiment Design
**Date:** 2026-07-29
**Status:** COMPLETED

---

## 1. Hypothesis Statement

Under scale-matched conditions (~110–250M parameters), transformer models grouped by architecture family (encoder-only, decoder-only, encoder-decoder) exhibit characteristic Δ*-vector profiles across AdvGLUE/ANLI/CheckList attack types showing greater within-family similarity than between-family similarity (permutation MANOVA η² > 0.15 in ≥50% of reliable attack categories), replicating across surrogate-diverse benchmark partitions.

**Gate:** MUST_WORK — failure routes to Phase 2A-Dialogue for hypothesis redesign.

---

## 2. Archon KB Research Summary

**[NOT_FOUND - ARCHON]** — Archon KB is focused on image generation / diffusion models. No adversarial NLP robustness cases found across all search levels (9 queries, 3 levels). All implementation patterns below are **[INFERRED]** from Exa/web search findings and general NLP knowledge.

---

## 3. Implementation Research Findings

### 3.1 Dataset Access

**AdvGLUE** — `AI-Secure/adv_glue` on HuggingFace Datasets Hub (CC BY-SA 4.0).
```python
from datasets import load_dataset
# Load each task separately
adv_sst2 = load_dataset('AI-Secure/adv_glue', 'adv_sst2')['validation']
adv_qqp  = load_dataset('AI-Secure/adv_glue', 'adv_qqp')['validation']
adv_mnli = load_dataset('AI-Secure/adv_glue', 'adv_mnli')['validation']
adv_qnli = load_dataset('AI-Secure/adv_glue', 'adv_qnli')['validation']
adv_rte  = load_dataset('AI-Secure/adv_glue', 'adv_rte')['validation']
```
AdvGLUE provides only a 'dev/validation' split publicly (~202 KB). The test set requires CodaLab submission. Dev set includes attack method annotations (with detailed annotations version from Jan 2024 release). Each example has `sentence`, `label`, `idx` fields; NLI tasks have `premise`, `hypothesis`.

**Important:** AdvGLUE dev set with detailed annotations (available from adversarialglue.github.io, March 2023 release) includes `method` field identifying attack type (C1–C11 categories + `glue` for benign). Use the annotated version for attack-type stratification.

**ANLI** — `facebook/anli` on HuggingFace Datasets Hub. Round 3 (R3) used as primary human-crafted NLI benchmark (test_r3: 1,200 examples; dev_r3: 1,200 examples).
```python
anli_r3_test = load_dataset('facebook/anli', split='test_r3')  # 1,200 examples
anli_r3_dev  = load_dataset('facebook/anli', split='dev_r3')   # 1,200 examples
```
Fields: `uid`, `premise`, `hypothesis`, `label` (0=entailment, 1=neutral, 2=contradiction), `reason`.

**CheckList** — The CheckList behavioral testing suite (Ribeiro et al., ACL 2020) provides test suites for NLP tasks. For this experiment, use CheckList's published test suite for sentiment (SST-2 equivalent) and NLI. CheckList test suites are loaded via the `checklist` Python package and contain MFT (Minimum Functionality Test), INV (Invariance), and DIR (Directional Expectation) tests across linguistic capabilities. Relevant capabilities for this study: negation, vocabulary, robustness (character perturbations), NER, temporal, and fairness.

Note: CheckList does not provide a standard HuggingFace dataset; test suites are `.pkl` files from the `marcotcr/checklist` GitHub repo or generated via `checklist.editor`. For this experiment, use CheckList's **released test suites** for SST-2 and NLI from the original ACL 2020 paper's data release.

### 3.2 Model Fine-tuning (GLUE)

Use HuggingFace `run_glue.py` standardized pipeline for all models.

```bash
python run_glue.py \
  --model_name_or_path <MODEL_HUB_ID> \
  --task_name <TASK> \
  --do_train --do_eval \
  --max_seq_length 128 \
  --per_device_train_batch_size 32 \
  --learning_rate 2e-5 \
  --num_train_epochs 3 \
  --seed 42 \
  --output_dir ./checkpoints/<MODEL>/<TASK>/
```

### 3.3 Attention Extraction

HuggingFace supports `output_attentions=True` for all target models.

```python
import torch
from transformers import AutoModel, AutoTokenizer

model = AutoModel.from_pretrained(model_path, output_attentions=True)
tokenizer = AutoTokenizer.from_pretrained(model_path)

with torch.no_grad():
    outputs = model(**tokenizer(text, return_tensors='pt'))
    # outputs.attentions: tuple of (batch, num_heads, seq_len, seq_len), one per layer
    # For encoder-decoder (T5, BART): outputs.encoder_attentions, outputs.decoder_attentions, outputs.cross_attentions
```

Attention concentration C on perturbed span:
```
C(x, span) = sum_{t in span} sum_{h} sum_{l} A_lh[:, t] / (|span| * num_heads * num_layers)
```

ΔC = C(adv_example, perturbed_span) − C(clean_example, same_span)

Perturbed span identification: use word-diff between clean and adversarial text (from AdvGLUE detailed annotation `method` + `original_sentence` fields). Fallback: compute token-level diff via difflib.

---

## 4. Experiment Specification

### 4.1 Models

| Model | Architecture Family | HuggingFace ID | Params | Role |
|-------|--------------------|--------------------|--------|------|
| BERT-base-uncased | encoder-only | `bert-base-uncased` | 110M | Primary |
| RoBERTa-base | encoder-only | `roberta-base` | 125M | Primary |
| ELECTRA-base-discriminator | encoder-only | `google/electra-base-discriminator` | 110M | Objective contrast |
| ALBERT-base-v2 | encoder-only | `albert-base-v2` | 12M (eff.) | Tokenizer contrast |
| GPT-2 | decoder-only | `gpt2` | 117M | Primary |
| OPT-125M | decoder-only | `facebook/opt-125m` | 125M | Primary |
| OPT-350M | decoder-only | `facebook/opt-350m` | 350M | Decoder family strengthen (R5 mitigation) |
| T5-base | encoder-decoder | `t5-base` | 220M | Primary |
| BART-base | encoder-decoder | `facebook/bart-base` | 139M | Primary |

**Total: 9 models** (4 encoder-only, 3 decoder-only, 2 encoder-decoder).

Note: ALBERT-base-v2 has 12M effective parameters but is scale-matched by design (same hidden dim 768, GLUE performance comparable to BERT-base). OPT-350M is slightly above 250M ceiling but acceptable given R5 risk of 2-member decoder family.

### 4.2 GLUE Fine-tuning Tasks

Fine-tune each model on: **SST-2, MNLI, QQP, QNLI, RTE** (5 tasks). These are the 5 tasks covered by AdvGLUE.

- For decoder-only (GPT-2, OPT): use classification head on last non-padding token; `--model_name_or_path gpt2` with padding_side='left'.
- For T5: use `AutoModelForSeq2SeqLM` with label verbalization ("positive"/"negative" etc.) or classification head on encoder pooled output. Prefer classification head for comparability.
- Fix random seed=42 across all models and tasks.

### 4.3 Adversarial Evaluation Datasets

#### Partition A — Word-level automatic (AdvGLUE C1–C5)

AdvGLUE detailed annotation dev set, filtered to `method` in:
- C1: TextFooler (word substitution via semantic similarity)
- C2: BERT-Attack (masked LM word substitution)
- C3: PWWS (word substitution via WordNet)
- C4: Genetic (genetic algorithm word-level)
- C5: SememePSO (sememe-based substitution)

Load from AdvGLUE detailed annotations dev.json. Expected counts per task: 15–60 examples per attack method (AdvGLUE Table 1 reports 200–500 per major category across all tasks; dev set is ~10% = 20–50 per method).

#### Partition B — Sentence-level automatic (AdvGLUE C6–C7)

- C6: StressTest (distraction-based, sentence-level)
- C7: CheckList automated perturbations (typos, punctuation, negation from AdvGLUE pipeline)

#### Partition C — Human-crafted (AdvGLUE C8–C11)

- C8–C11: Human-written adversarial examples from AdvGLUE human evaluation

**Surrogate-bias falsification test:** Partitions A+B are surrogate-generated (encoder-family models used as AdvGLUE surrogates). Partition C is human-crafted — fingerprint disappearing in C is the surrogate-bias failure signal.

#### ANLI-R3

Use `facebook/anli` test_r3 split (1,200 examples) for NLI evaluation. ANLI-R3 is human-crafted adversarial NLI (no encoder-family surrogate). Treat as additional Partition C-equivalent.

Models evaluated on ANLI-R3: all models fine-tuned on MNLI (used as NLI task proxy).

#### CheckList Test Suites

Load CheckList published test suites for SST-2 (sentiment) and NLI tasks. Use INV (invariance) and MFT (minimum functionality) test types. CheckList tests cover: negation, vocabulary, robustness, NER, temporal, coreference.

For SST-2 models: load `checklist/release_data/sentiment/` suite.
For NLI models (MNLI, RTE): load `checklist/release_data/nli/` suite.

Treat CheckList failures as a binary hit/miss per test case; compute accuracy per capability as Δ* proxy:
`Δ*_checklist = 1 − Acc_checklist` (since clean acc ≈ 1 for targeted MFT tests).

### 4.4 Δ*-Vector Construction

For each model m, compute Δ* per attack category k across all tasks:

```
Δ*(m, k) = (Acc_clean(m, k) − Acc_adv(m, k)) / Acc_clean(m, k)
```

Where:
- `Acc_clean(m, k)` = accuracy on the **original clean examples** corresponding to the adversarial examples in category k (matched pairs from AdvGLUE detailed annotations, which include original_sentence field)
- `Acc_adv(m, k)` = accuracy on adversarial examples in category k

Aggregate Δ* across tasks (SST-2, MNLI, QQP, QNLI, RTE) using macro-average per attack category.

**Δ*-vector for model m:** vector of Δ*(m, k) values across all reliable attack categories k.

### 4.5 Split-Half Reliability Filter

For each attack category k:
1. Randomly split examples into two halves (seed=42).
2. Compute Δ* on each half independently.
3. Compute split-half Pearson correlation r across models.
4. Retain category k if r ≥ 0.7 AND n_examples ≥ 50 (aggregated across all tasks).
5. Apply Spearman-Brown correction: r_corrected = 2r / (1 + r).

Repeat reliability estimation for AdvGLUE partitions A, B, C separately. Report number of reliable categories per partition.

If fewer than 3 attack categories pass in any partition, aggregate across related categories (e.g., merge C1–C5 word-level into single dimension).

### 4.6 Statistical Analysis

#### Step 1: Mixed-Effects Model

```
Δ*(m, k, task) ~ ArchFamily × AttackType + Objective + Tokenizer + CleanAccuracy + (1|Model)
```

- `ArchFamily`: encoder-only / decoder-only / encoder-decoder (3-level factor)
- `AttackType`: reliable attack categories (k) — word-level / sentence-level / human-crafted as grouping
- `Objective`: MLM / RTD / CLM / DAE (4-level covariate)
- `Tokenizer`: BPE / WordPiece / SentencePiece (3-level covariate)
- `CleanAccuracy`: continuous covariate
- `(1|Model)`: random intercept for model

Bootstrap 1,000 iterations (resample models with replacement). Report Architecture × AttackType interaction coefficient and 95% CI.

**Primary criterion:** Architecture × AttackType interaction p < 0.05 (bootstrap CI excludes zero).

Use `lme4` (R via `rpy2`) or `statsmodels` MixedLM (Python). For Python implementation:
```python
import statsmodels.formula.api as smf
model = smf.mixedlm(
    "delta_star ~ C(arch_family) * C(attack_type) + C(objective) + C(tokenizer) + clean_acc",
    data=df,
    groups=df["model_id"]
)
result = model.fit()
```

#### Step 2: Permutation MANOVA

For each reliable attack category k:
1. Construct per-model Δ* value: `delta_star[m, k]`.
2. Group models by architecture family.
3. Compute η² = SS_between / SS_total.
4. Permute architecture family labels 1,000 times; compute null η² distribution.
5. p-value = proportion of permuted η² ≥ observed η².

**Secondary criterion:** η² > 0.15 in ≥50% of reliable attack categories.

Use `scipy` / `numpy` for permutation test implementation.

#### Step 3: Surrogate-Diversity Replication

Fit mixed-effects model separately for each partition (A, B, C). Compare Architecture × AttackType interaction coefficients across partitions.

Replication criterion: interaction significant in ≥2/3 partitions (A, B, C).

### 4.7 Leave-One-Model-Out (LOMO) Classification

Train on Partition A+B (AdvGLUE automatic), test on Partition C (human-crafted):

1. For each fold (leave one model out):
   - Fit nearest-neighbor classifier (L2 distance in Δ*-vector space) or 1-vs-rest logistic regression on training models.
   - Predict architecture family for held-out model.
2. Compute cross-partition accuracy: train on A+B Δ*-vectors, predict on C Δ*-vectors.
3. Bootstrap 1,000 iterations (resample training models); compute 95% CI.

**Primary criterion:** ≥60% LOMO accuracy with 95% CI lower bound > 33% (3-class chance).

**Fallback (R5 mitigation):** If decoder-only within-family variance is too high (2 original models), binary classification (encoder-only vs. non-encoder-only) with ≥75% accuracy threshold.

```python
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import LeaveOneOut
import numpy as np

# delta_star_matrix: shape (n_models, n_reliable_categories)
# labels: architecture family per model

loo = LeaveOneOut()
preds = []
for train_idx, test_idx in loo.split(delta_star_matrix):
    clf = KNeighborsClassifier(n_neighbors=1, metric='euclidean')
    clf.fit(delta_star_matrix[train_idx], labels[train_idx])
    preds.append(clf.predict(delta_star_matrix[test_idx])[0])

accuracy = np.mean(np.array(preds) == labels)
```

---

## 5. Dataset Summary

| Dataset | Type | Access | Split Used | Size | Role |
|---------|------|--------|-----------|------|------|
| AdvGLUE (detailed annotations) | standard | HuggingFace `AI-Secure/adv_glue` + github adversarialglue.github.io | dev/validation | ~500 examples (all tasks) | Primary adversarial eval; partitions A, B, C |
| GLUE (clean) | standard | HuggingFace `glue` | train + validation | Standard | Fine-tuning + clean accuracy baseline |
| ANLI-R3 | standard | HuggingFace `facebook/anli` | test_r3, dev_r3 | 1,200 + 1,200 | Human-crafted NLI adversarial (Partition C-equivalent) |
| CheckList suites | programmatic-api | `marcotcr/checklist` GitHub release data | Test suites | Varies per capability | Behavioral testing (surrogate-free) |

**No synthetic data used.** All datasets are real, publicly available benchmarks.

---

## 6. Compute Requirements

| Phase | Models | Time Estimate | Hardware |
|-------|--------|---------------|----------|
| GLUE fine-tuning (5 tasks × 9 models) | 45 training runs | ~2–4 hrs per run (SST-2: 26min, MNLI: 2.5hr) ≈ 40–100 GPU-hrs | 1–4× A100/V100 |
| Adversarial evaluation (9 models × 3 datasets) | 27 eval runs | ~1–2 hrs total | 1× GPU |
| Attention extraction | 9 models × AdvGLUE | ~2–4 hrs | 1× GPU |
| Statistical analysis | — | <1 hr | CPU |

**Total:** ~50–110 GPU-hours. Parallelizable across tasks.

---

## 7. Failure Modes and Mitigations

| Risk | Detection | Response |
|------|-----------|----------|
| R2: AdvGLUE dev set too small per attack category (<50 examples) | Count n per method before reliability filter | Aggregate word-level C1–C5 into single dimension; supplement with ANLI-R3 |
| R5: Decoder family (3 models) still insufficient | Compute within-family CV; if CV > between-family | Report binary (encoder vs. non-encoder) classification as primary |
| R3: Fewer than 3 reliable attack categories | Split-half r < 0.7 for most categories | Lower threshold to r ≥ 0.6 and document; use task-level aggregation |
| R1: ELECTRA separates from BERT in Δ*-vector space | Compare ELECTRA position to BERT vs. RoBERTa | Reframe as objective-confound finding; retain descriptive Δ* claim |
| R4: AdvGLUE detailed annotation `method` field absent | Check dev.json structure before pipeline | Use word-diff via `difflib.ndiff` to approximate perturbed positions |

---

## 8. Output Artifacts

1. `checkpoints/<MODEL>/<TASK>/` — Fine-tuned model checkpoints per model × task
2. `results/delta_star_matrix.csv` — Δ*(model, attack_category) for all models and categories
3. `results/reliability_filter.json` — Split-half r per attack category; reliable vs. excluded
4. `results/mixed_effects_output.txt` — Mixed-effects model coefficients and bootstrap CIs
5. `results/permutation_manova.csv` — η² per reliable category with permutation p-values
6. `results/lomo_classification.json` — LOMO accuracy, 95% CI, per-partition results
7. `results/attention_concentration.csv` — ΔC per model × attack category (for H-M1 pipeline)

---

## 9. Implementation Plan (Step-by-Step)

### Step 1: Environment Setup (Day 1)
```bash
pip install transformers datasets evaluate accelerate scikit-learn statsmodels scipy numpy checklist
```

Clone AdvGLUE detailed annotation dev set from adversarialglue.github.io.

### Step 2: GLUE Fine-tuning (Days 1–7)
Run `run_glue.py` for all 9 models × 5 tasks. Parallelize across 4 GPUs.

Special handling:
- GPT-2 / OPT: add classification head, set `padding_side='left'`, use `gpt2` as base and add `num_labels` config.
- T5: use `AutoModelForSequenceClassification` with T5EncoderModel or T5ForConditionalGeneration with label verbalization.
- ALBERT: note parameter count is small (12M) but effective parameter count via parameter sharing is 125M equivalent.

### Step 3: Reliability Pre-check (Day 7)
Before full adversarial evaluation:
1. Load AdvGLUE detailed annotations.
2. Count examples per attack method per task.
3. Run split-half reliability on a 2-model subset.
4. If <5 categories pass, adjust aggregation strategy before committing full pipeline.

### Step 4: Adversarial Evaluation (Days 7–9)
Evaluate all 9 fine-tuned models on:
- AdvGLUE dev (all 5 tasks)
- ANLI-R3 (test_r3)
- CheckList suites (SST-2, NLI)

Compute Δ* per model × attack category. Save `delta_star_matrix.csv`.

### Step 5: Statistical Analysis (Days 9–10)
1. Apply reliability filter; retain reliable categories.
2. Fit mixed-effects model; bootstrap 1,000 iterations.
3. Run permutation MANOVA per reliable category.
4. Run LOMO classifier cross-partition evaluation.

### Step 6: Gate 1 Evaluation (Day 10)
Check H-E1 success criteria:
- Primary: Architecture × AttackType interaction p < 0.05
- Secondary: η² > 0.15 in ≥50% of reliable categories

If PASS → proceed to H-M1 (attention concentration extraction).
If FAIL → route to Phase 2A-Dialogue for hypothesis redesign.

---

## 10. Success Criteria Summary

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Primary (Architecture × AttackType interaction) | p < 0.05, bootstrap CI excludes zero | Mixed-effects model |
| Secondary (MANOVA effect size) | η² > 0.15 in ≥50% reliable categories | Permutation MANOVA |
| Replication (cross-partition) | Interaction significant in ≥2/3 partitions | Per-partition mixed-effects |
| Classification (LOMO) | ≥60% accuracy, 95% CI lower bound > 33% | Cross-partition LOMO |
| Reliability filter | r ≥ 0.7, n ≥ 50 per category | Split-half Pearson r |

**Gate decision: ANY failure of Primary criterion → STOP (MUST_WORK gate).**

---

## 11. Research Sources

- **AdvGLUE:** Wang et al. (NeurIPS 2021). `AI-Secure/adv_glue` on HuggingFace. CC BY-SA 4.0.
- **ANLI:** Nie et al. (ACL 2020). `facebook/anli` on HuggingFace. R3 test split.
- **CheckList:** Ribeiro et al. (ACL 2020). `marcotcr/checklist` GitHub. MIT License.
- **HuggingFace run_glue.py:** `huggingface/transformers/examples/pytorch/text-classification/run_glue.py`
- **Attention extraction:** `output_attentions=True` via HuggingFace Transformers API. Shape: (batch, num_heads, seq_len, seq_len) per layer.
- **Archon KB:** No relevant cases found (diffusion-model focused KB); all patterns inferred from Exa search.
