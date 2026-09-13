---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7]
hypothesis_id: H-E1
phase: Phase 3
generated: 2026-08-25
author: yoon303@ust.ac.kr
---

# Product Requirements Document: H-E1
## Semantic Entropy vs Token Entropy — AUROC Comparison on TriviaQA/Llama-2-7B

---

## 1. Executive Summary

H-E1 is an EXISTENCE (PoC) experiment that asks: **does Semantic Entropy (SE) outperform Token Entropy (TE) by ≥ 0.05 AUROC on TriviaQA dev with Llama-2-7B?**

Both uncertainty methods are applied to the same Llama-2-7B model on the same N=98 TriviaQA dev questions (reused from h-e2-v2). SE clusters K=10 stochastic samples via NLI entailment; TE computes mean per-token Shannon entropy from a greedy-decode logit pass. AUROC is computed against binary EM correctness labels. Success = gap ≥ 0.05.

**Scope:** Minimal inference pipeline. No training. No architectural modification.

---

## 2. Problem Statement

Token entropy is a fast, single-pass uncertainty proxy but operates at the vocabulary-level surface, encoding paraphrase variation rather than semantic uncertainty. Semantic entropy addresses this by clustering semantically equivalent outputs before computing entropy. H-E1 verifies whether this semantic-level abstraction produces a meaningfully larger AUROC improvement (≥ 0.05) at the 7B scale, where prior work (h-e2-v2) observed only a directional gap (+0.029).

**Gate (MUST_WORK):** SE AUROC − TE AUROC ≥ 0.05 on N≥98, Llama-2-7B, K=10.

---

## 3. Functional Requirements

### FR-1: Data Loading
- Load TriviaQA dev split: `datasets.load_dataset("mandarjoshi/trivia_qa", "rc.nocontext", split="validation")`
- Load N=98 question indices from h-e2-v2 pilot (same random seed=42)
- If h-e2-v2 indices file missing: sample N=98 with seed=42 from full dev set

### FR-2: K=10 Sample Loading (Reuse from h-e2-v2)
- Load pre-generated K=10 stochastic samples from h-e2-v2 output directory
- Each sample entry: `{question_id, question, samples: [str × 10], log_probs: [float × 10]}`
- If h-e2-v2 samples missing: regenerate with `meta-llama/Llama-2-7b-hf`, temperature=0.7, max_new_tokens=50, top_p=1.0

### FR-3: Token Entropy Computation
- Load Llama-2-7B-hf in float16 on GPU
- For each question: single greedy-decode forward pass (temperature=0)
- Extract per-token logit distributions from `outputs.logits`
- Compute `TE = mean(-sum(p * log(p+1e-9), dim=-1))` over output tokens
- Output: `te_scores: list[float]` length N

### FR-4: Semantic Entropy Computation
- Load NLI model: `cross-encoder/nli-deberta-v3-large`
- For each question: apply bidirectional NLI entailment clustering to K=10 samples
- Cluster assignment via `get_semantic_ids()` (Kuhn et al. 2023 algorithm)
- Aggregate per-cluster log-probabilities via logsumexp
- Compute cluster-level Shannon entropy
- Output: `se_scores: list[float]` length N
- Log: `avg_clusters` per question for mechanism verification

### FR-5: EM Correctness Labels
- Evaluate each greedy-decode answer against TriviaQA gold alias list
- Standard EM normalization: lowercase, remove articles/punctuation
- Output: `correctness: list[int]` (1=correct, 0=incorrect)

### FR-6: AUROC Computation
- Compute `auroc_te = roc_auc_score(correctness, -np.array(te_scores))`
- Compute `auroc_se = roc_auc_score(correctness, -np.array(se_scores))`
- Bootstrap 1000 iterations (seed=42), stratified sampling
- Report mean AUROC + 95% CI [2.5%, 97.5%] for both
- Compute gap = auroc_se - auroc_te

### FR-7: Mechanism Verification
- Assert `avg_clusters > 1.5` (SE clustering is active)
- Assert `mean(te_scores) > 0.0` (TE extraction valid)
- Assert `len(set(correctness)) == 2` (both classes present)
- Assert `abs(gap) < 0.30` (sanity: large gap = computation error)

### FR-8: Extension Protocol (if gap in [0.03, 0.05])
- Sample N=500 questions from TriviaQA dev (seed=42, non-overlapping with N=98)
- Generate K=10 samples for new questions
- Recompute SE and TE; re-evaluate AUROC
- Report final gap at N=500

### FR-9: Results Export
- Save `results.json`: `{n_questions, auroc_te, auroc_se, gap, te_ci, se_ci, avg_clusters, correctness_rate}`
- Save `te_scores.npy`, `se_scores.npy`, `correctness.npy`

### FR-10: Visualization
- Figure 1 (REQUIRED): Bar chart — SE AUROC vs TE AUROC with 95% CI error bars and gap annotation
- Figure 2: ROC curves for SE and TE overlaid on same axes
- Figure 3: Uncertainty score distributions (violin, correct vs incorrect questions)
- Figure 4: Bootstrap AUROC distribution (histogram/violin)
- Save all figures to `docs/youra_research/h-e1/figures/`

### FR-11: Ablation Variants
- **FR-11a:** TE (token entropy, greedy decode) — baseline method
- **FR-11b:** SE (semantic entropy, K=10, DeBERTa NLI) — proposed method
- Both computed on identical questions with identical Llama-2-7B model

---

## 4. Data Specification

| Field | Value |
|-------|-------|
| Dataset | TriviaQA dev (open-domain split) |
| HuggingFace ID | `mandarjoshi/trivia_qa`, config `rc.nocontext` |
| Split | `validation` (full: 11,313 Q; pilot: N=98) |
| Pilot indices | From h-e2-v2, random seed=42 |
| Extension size | N=500 (if gap in [0.03, 0.05]) |
| Labels | Binary EM correctness (1=correct) |
| Answer normalization | TriviaQA standard EM (lowercase, remove articles/punct) |
| Expected EM accuracy | ~50-60% at Llama-2-7B on sampled subset |
| Download method | HuggingFace datasets (auto-download) |
| Preprocessing | None beyond EM normalization |
| Augmentation | None |

---

## 5. Model Specification

### Primary Model: Llama-2-7B-hf
| Field | Value |
|-------|-------|
| HuggingFace ID | `meta-llama/Llama-2-7b-hf` |
| Precision | float16 |
| Device | GPU (device_map="auto") |
| Access | Gated — requires HuggingFace token |
| Role | Both TE and SE computation |
| Already cached | Yes (h-e2-v2) |

### NLI Model: DeBERTa-large MNLI
| Field | Value |
|-------|-------|
| HuggingFace ID | `cross-encoder/nli-deberta-v3-large` |
| Role | Bidirectional entailment for SE clustering |
| Pipeline | `zero-shot-classification` |
| Device | GPU (device=0) |

---

## 6. Evaluation Metrics

| Metric | Description | Library |
|--------|-------------|---------|
| AUROC (primary) | Area under ROC curve, uncertainty vs EM label | sklearn |
| Bootstrap 95% CI | 1000 iterations, seed=42 | numpy |
| Gap | auroc_se - auroc_te | computed |
| ECE | Expected Calibration Error | secondary |
| Precision@20% abstain | Fraction correct in top-20% uncertain | secondary |

**Success Criteria:**
- PASS: gap ≥ 0.05
- EXTEND: gap in [0.03, 0.05] → run N=500
- FAIL: gap < 0.03 after N=500

---

## 7. Non-Functional Requirements

### NFR-1: Compute
- N=98 pilot: TE ~5 min, SE ~0 min (reuse), total ~10 min
- N=500 extension: ~1.5 hours total (new generation + NLI)
- Single A100 GPU sufficient

### NFR-2: Reproducibility
- All random seeds = 42 (generation, bootstrap, sampling)
- h-e2-v2 samples reused directly — zero generation cost, zero seed drift

### NFR-3: Code Quality (LIGHT tier)
- Argparse for CLI flags (no YAML config needed)
- Print + CSV logging (no WandB)
- Smoke test: run on N=5 questions before full N=98

---

## 8. Dependencies

### Python Packages
```
torch>=2.0
transformers>=4.35
datasets>=2.14
scikit-learn>=1.3
numpy>=1.24
matplotlib>=3.7
seaborn>=0.12
scipy>=1.11
```

### External Repositories (Reference Only)
- jlko/semantic_uncertainty (Kuhn et al. 2023) — algorithm reference; h-e2-v2 already adapted

### Gated Models
- `meta-llama/Llama-2-7b-hf` — requires HuggingFace token (`HF_TOKEN` env var)

---

## 9. Success Criteria

| Criterion | Threshold |
|-----------|-----------|
| Code runs without error | Required |
| SE AUROC > TE AUROC | Direction confirmed |
| SE AUROC − TE AUROC ≥ 0.05 | **GATE: MUST_WORK** |
| avg_clusters > 1.5 | Mechanism activated |
| Both AUROC > 0.5 | Above random |

---

## 10. Out of Scope

- Training or fine-tuning any model
- Architectural modification to Llama-2-7B
- Other models (e.g., Llama-2-13B, GPT)
- Other datasets (e.g., NaturalQuestions) — reserved for H-M hypotheses
- Verbalized confidence baseline — not required for H-E1 gate
