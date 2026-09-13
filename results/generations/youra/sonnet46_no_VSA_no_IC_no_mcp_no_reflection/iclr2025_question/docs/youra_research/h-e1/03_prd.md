---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7]
hypothesis: H-E1
type: EXISTENCE (PoC)
tier: LIGHT
date: 2026-08-31
author: yoon303@ust.ac.kr
---

# PRD: H-E1 — SMC-NLI Existence Proof on HaluEval QA

## 1. Executive Summary

H-E1 validates whether Semantic Mode Consistency via NLI (SMC-NLI) — computed as the fraction of (entailment + neutral) pairs among all pairwise NLI evaluations of N=10 stochastic samples from Llama-3-8B-Instruct — exhibits meaningful variation across HaluEval QA questions and achieves AUROC > 0.60 on binary hallucination labels. This is a pure inference-only PoC: no model training, no fine-tuning. Success unlocks the H-M* mechanism hypothesis chain.

**Gate:** MUST_WORK — AUROC > 0.60 on 1000 HaluEval questions (500 correct, 500 hallucinated).

---

## 2. Problem Statement

LLMs produce factual hallucinations that are difficult to detect without ground-truth access. Sampling-based consistency (SelfCheckGPT) detects hallucinations by checking whether repeated samples agree. The NLI variant uses a cross-encoder (DeBERTa-v3-large) to assess semantic consistency pairwise. H-E1 tests a pairwise aggregation scheme (fraction of entailment+neutral, not sentence-level contradiction) on HaluEval QA, a binary-labeled factual QA benchmark.

**Hypothesis:** Correct answers produce concentrated (high-consistency) samples; hallucinated answers produce spread (low-consistency) samples — detectable by SMC-NLI AUROC > 0.60.

---

## 3. Scope

**In scope:**
- Inference pipeline: Llama-3-8B-Instruct sampling (N=10 per question) at temperature=0.7
- SMC-NLI scorer: pairwise DeBERTa-v3-large NLI, question-prepended, fraction of (ent+neut)/45
- SMC-Embed robustness check: mean cosine similarity via all-mpnet-base-v2
- Evaluation: AUROC on 1000 HaluEval QA questions (binary labels)
- Mechanism verification: sanity check on 5 questions before full run

**Out of scope:**
- Model fine-tuning or training
- Datasets beyond HaluEval QA
- Ablation studies (deferred to H-M*)
- Multi-GPU or distributed inference

---

## 4. Data Specification

### 4.1 Primary Dataset: HaluEval QA

| Property | Value |
|----------|-------|
| Name | HaluEval QA |
| Source | GitHub: RUCAIBox/HaluEval (`data/qa_data.json`) |
| HuggingFace mirror | `pminervini/HaluEval` (split: `qa`) |
| Total size | 10,000 QA pairs (balanced 50/50) |
| Subset for H-E1 | 1,000 questions: 500 correct + 500 hallucinated (stratified, seed=42) |
| Fields | `question`, `right_answer`, `hallucinated_answer` |
| Label convention | `right_answer` → label=0 (non-hallucinated), `hallucinated_answer` → label=1 (hallucinated) |
| Download method | Manual (GitHub JSON) or HuggingFace `load_dataset` |

**Loading code:**
```python
# Option 1: Direct JSON
import json, requests
url = "https://raw.githubusercontent.com/RUCAIBox/HaluEval/main/data/qa_data.json"
data = json.loads(requests.get(url).text)

# Option 2: HuggingFace
from datasets import load_dataset
dataset = load_dataset("pminervini/HaluEval", "qa")
```

**Preprocessing:**
- Extract question + label from each entry (do NOT use provided answers — generate from Llama)
- Stratified sample: 500 correct + 500 hallucinated, seed=42
- No augmentation, no tokenization at data-prep stage

**Note:** PyG Planetoid and similar auto-download datasets are NOT used here. HaluEval requires explicit download.

### 4.2 No Static Baselines Dataset

H-E1 uses no held-out static dataset beyond HaluEval QA.

---

## 5. Functional Requirements

### FR-1: Data Preparation
- FR-1.1: Download HaluEval `qa_data.json` from GitHub or HuggingFace
- FR-1.2: Parse and stratified-sample 1000 questions (500 per class, seed=42)
- FR-1.3: Save processed dataset to `data/halueval_qa_1000.json`

### FR-2: LLM Sampling (Llama-3-8B-Instruct)
- FR-2.1: Load `meta-llama/Meta-Llama-3-8B-Instruct` via HuggingFace Transformers (float16, device_map="auto")
- FR-2.2: For each question, generate N=10 samples at temperature=0.7, top_p=0.9, max_new_tokens=50
- FR-2.3: Save all samples to `data/llama_samples.json` (for reproducibility)
- FR-2.4: Total inference: 1000 questions × 10 samples = 10,000 forward passes

### FR-3: SMC-NLI Scorer
- FR-3.1: Load `cross-encoder/nli-deberta-v3-large` (HuggingFace cross-encoder)
- FR-3.2: For each question, form all C(10,2)=45 pairwise combinations of sampled answers
- FR-3.3: Prepend question to each answer: `"Q: {question} A: {answer}"` (OOD mitigation)
- FR-3.4: Score each pair via NLI cross-encoder; extract P(entailment) + P(neutral) per pair
- FR-3.5: SMC-NLI = mean of (P(ent)+P(neut)) across 45 pairs for each question
- FR-3.6: Batch inference: batch_size=16 pairs; truncation=True, max_length=512
- FR-3.7: Label mapping: `contradiction=0, entailment=1, neutral=2`

### FR-4: SMC-Embed Robustness Check
- FR-4.1: Load `sentence-transformers/all-mpnet-base-v2`
- FR-4.2: For each question, embed all 10 samples; compute mean pairwise cosine similarity
- FR-4.3: SMC-Embed score = mean cosine similarity over C(10,2)=45 pairs

### FR-5: Mechanism Verification (Sanity Check)
- FR-5.1: Before full run, execute on 5 questions
- FR-5.2: Assert: `max(scores) - min(scores) > 0.01` (non-degenerate)
- FR-5.3: Assert: all scores in [0,1]
- FR-5.4: Log per-question scores and labels

### FR-6: Evaluation
- FR-6.1: Compute AUROC: `sklearn.metrics.roc_auc_score(labels, -np.array(smc_nli_scores))`
  (Note: negate SMC-NLI because high consistency → low hallucination)
- FR-6.2: Compute SMC-NLI distribution std; pass if std > 0.05
- FR-6.3: Compute SMC-Embed AUROC identically
- FR-6.4: Log per-question: question, label, smc_nli_score, smc_embed_score

### FR-7: Results & Visualization
- FR-7.1: Save results to `results/h-e1/results.json` (all per-question scores + labels + AUROCs)
- FR-7.2: Gate metrics bar chart: SMC-NLI AUROC vs. random baseline (0.50) vs. SMC-Embed AUROC
- FR-7.3: SMC-NLI score distribution histogram split by label (correct vs. hallucinated)
- FR-7.4: ROC curve: SMC-NLI and SMC-Embed on same plot
- FR-7.5: SMC-NLI vs SMC-Embed scatter plot (per-question correlation)
- FR-7.6: Save all figures to `docs/youra_research/h-e1/figures/`

---

## 6. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| Reproducibility | Fixed seed=42 for dataset sampling; deterministic NLI inference |
| Hardware | Single GPU ≥16GB VRAM (A100/V100/RTX 3090); float16 for LLM |
| Runtime | Total ≤ 2 hours on A100 (1.4h LLM + 6min NLI) |
| Data persistence | Intermediate outputs saved (samples, scores) for reruns without re-inference |
| Logging | Per-question mechanism log: `SMC-NLI score for question {i}: {score:.4f} | Label: {label}` |

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0
transformers>=4.40
sentence-transformers>=2.7
scikit-learn>=1.3
numpy>=1.24
requests>=2.31
datasets>=2.18
matplotlib>=3.7
scipy>=1.11
tqdm>=4.66
```

### 7.2 External Models (HuggingFace)

| Model | HF ID | Purpose |
|-------|-------|---------|
| Llama-3-8B-Instruct | `meta-llama/Meta-Llama-3-8B-Instruct` | Sample generator |
| DeBERTa NLI | `cross-encoder/nli-deberta-v3-large` | NLI cross-encoder |
| MPNet Embed | `sentence-transformers/all-mpnet-base-v2` | SMC-Embed scorer |

**Note:** `meta-llama/Meta-Llama-3-8B-Instruct` requires Llama license acceptance on HuggingFace.

### 7.3 External Repositories (Reference Only)

| Repo | URL | Use |
|------|-----|-----|
| SelfCheckGPT | github.com/potsawee/selfcheckgpt | NLI pattern reference |
| HaluEval | github.com/RUCAIBox/HaluEval | Dataset source |

---

## 8. Success Criteria

| Criterion | Target | Gate |
|-----------|--------|------|
| SMC-NLI AUROC | > 0.60 | MUST_WORK |
| SMC-NLI std | > 0.05 | Secondary (existence check) |
| Code runs without error | Yes | Required |
| Mechanism verification passed | Yes | Required |

**Failure routing:**
- If SMC-NLI AUROC < 0.60 but SMC-Embed AUROC > 0.60 → switch primary to SMC-Embed, continue to H-M1
- If both < 0.60 → PIVOT, reassess hypothesis chain

---

## 9. File Structure (Expected)

```
docs/youra_research/h-e1/
├── 02c_experiment_brief.md      (input — Phase 2C)
├── 03_prd.md                    (this file)
├── 03_architecture.md           (Phase 3 output)
├── 03_logic.md                  (Phase 3 output)
├── 03_config.md                 (Phase 3 output)
├── 03_tasks.yaml                (Phase 3 output)
└── figures/                     (Phase 4 output)

data/
├── halueval_qa_1000.json        (processed subset)
└── llama_samples.json           (10 samples per question)

results/h-e1/
└── results.json                 (scores + AUROCs)
```
