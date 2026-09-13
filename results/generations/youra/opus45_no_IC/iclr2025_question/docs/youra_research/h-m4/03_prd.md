# Product Requirements Document: H-M4

**Hypothesis:** Cross-cluster benchmark pairs show failed threshold transfer (AUROC degradation > 0.15)
**Date:** 2026-08-10
**Author:** Anonymous
**Type:** MECHANISM
**Tier:** FULL

---

## 1. Executive Summary

H-M4 validates that semantic entropy threshold transfer FAILS between benchmarks from different clusters. Combined with H-M3 (within-cluster transfer succeeds), this completes the transfer contrast demonstrating that clustering predicts transfer success.

**Success Criteria:** Mean cross-cluster AUROC degradation > 0.15

---

## 2. Problem Statement

### 2.1 Background
H-E1 established two benchmark clusters based on uncertainty distribution similarity:
- Cluster 1 (Factual Recall): trivia_qa, natural_questions, squad
- Cluster 2 (Entity/Claim): popqa, halueval_qa, fever

H-M3 showed within-cluster transfer succeeds (degradation ≤ 0.08). H-M4 must show cross-cluster transfer fails.

### 2.2 Hypothesis Under Test
Cross-cluster benchmark pairs show failed threshold transfer with AUROC degradation > 0.15.

### 2.3 Gate Condition
- **Type:** SHOULD_WORK
- **Pass:** Mean cross-cluster degradation > 0.15
- **Fail Action:** EXPLORE alternative distance metrics

---

## 3. Functional Requirements

### FR-1: Cross-Cluster Benchmark Loading
- Load trivia_qa (Cluster 1) as source benchmark
- Load popqa, halueval_qa (Cluster 2) as target benchmarks
- Sample size: 500+ samples per benchmark (full validation split)
- Use HuggingFace datasets API

### FR-2: Semantic Entropy Computation
- Generate 10 responses per query (temperature=1.0)
- Compute semantic entropy via bidirectional entailment clustering
- Use DeBERTa-v3-large-mnli for NLI

### FR-3: Threshold Calibration
- Calibrate threshold on source benchmark (70% calibration split)
- Use Youden criterion (maximize TPR-FPR)
- Target FPR: 0.1

### FR-4: Cross-Cluster Transfer Evaluation
- Apply frozen source threshold to target benchmark
- Compute AUROC on both source (30% held-out) and target (full set)
- Calculate degradation = source_auroc - target_auroc

### FR-5: Statistical Validation
- Compare cross-cluster degradation vs H-M3 within-cluster (Mann-Whitney U)
- Report 95% CI for mean degradation
- p < 0.05 required for significance

### FR-6: Figure Generation
- Gate metrics bar chart (degradation vs 0.15 threshold)
- H-M3 vs H-M4 degradation comparison box plot
- Per-pair degradation breakdown

---

## 4. Data Specification

### 4.1 Primary Datasets

| Dataset | Role | Source | Size | Auto-Download |
|---------|------|--------|------|---------------|
| trivia_qa | Source (Cluster 1) | HuggingFace | validation[:500] | Yes |
| popqa | Target (Cluster 2) | akariasai/PopQA | test[:500] | Yes |
| halueval | Target (Cluster 2) | pminervini/HaluEval | qa[:500] | Yes |

### 4.2 Loading Code
```python
from datasets import load_dataset

trivia = load_dataset("trivia_qa", "rc", split="validation[:500]")
popqa = load_dataset("akariasai/PopQA", split="test[:500]")
halueval = load_dataset("pminervini/HaluEval", "qa", split="data[:500]")
```

### 4.3 Preprocessing
- Extract question and answer fields
- Normalize answer format for correctness checking

---

## 5. Model Specification

### 5.1 LLM (Response Generation)
- **Model:** meta-llama/Llama-2-7b-chat-hf
- **Parameters:** temperature=1.0, max_tokens=256
- **Generations:** 10 per query

### 5.2 NLI (Semantic Clustering)
- **Model:** microsoft/deberta-v3-large-mnli
- **Usage:** Bidirectional entailment for clustering

---

## 6. Evaluation Metrics

### 6.1 Primary Metric
- **AUROC Degradation:** source_auroc - target_auroc
- **Success:** Mean degradation > 0.15

### 6.2 Secondary Metrics
- p-value (Mann-Whitney U vs H-M3)
- 95% CI for mean degradation
- Per-pair degradation breakdown

### 6.3 Metrics Implementation
```python
from sklearn.metrics import roc_auc_score
from scipy.stats import mannwhitneyu

auroc = roc_auc_score(labels, entropy_scores)
stat, p_value = mannwhitneyu(cross_degradations, within_degradations, alternative='greater')
```

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=2.0.0
transformers>=4.35.0
datasets>=2.14.0
scikit-learn>=1.3.0
scipy>=1.11.0
numpy>=1.24.0
matplotlib>=3.7.0
pyyaml>=6.0
```

### 7.2 Hardware Requirements
- GPU: 24GB+ VRAM (A100/A6000)
- RAM: 32GB+

### 7.3 External References
- H-M3 codebase (threshold transfer protocol)
- semantic-entropy-gate (calibration)
- spotify-research/bayesian-semantic-entropy

---

## 8. Non-Functional Requirements

### NFR-1: Code Reuse
- Reuse H-M3 codebase with minimal modifications
- Only change: pair selection (cross-cluster vs within-cluster)

### NFR-2: Reproducibility
- Fixed random seeds
- Deterministic sampling

### NFR-3: Performance
- Complete experiment in <4 hours on single GPU

---

## 9. Success Criteria Summary

| Criterion | Threshold | Priority |
|-----------|-----------|----------|
| Mean AUROC degradation | > 0.15 | MUST |
| p-value vs H-M3 | < 0.05 | SHOULD |
| All pairs tested | 2 minimum | MUST |
| Figures generated | 3 minimum | SHOULD |

---

## 10. Continuation Context

### From H-M3 (Prerequisite)
- Within-cluster degradation: 0.032 (threshold ≤ 0.08)
- Transfer protocol: calibrate on source → freeze → test on target
- Code location: h-m3/code/

### Key Adaptation
```python
# H-M3: Within-cluster
PAIRS = [("trivia_qa", "squad")]

# H-M4: Cross-cluster
PAIRS = [("trivia_qa", "popqa"), ("trivia_qa", "halueval_qa")]
```

---

*Generated by Phase 3 Implementation Planning*
*Source: h-m4/02c_experiment_brief.md*
