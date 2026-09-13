# Product Requirements Document: H-M2

**Date:** 2026-08-21
**Hypothesis:** H-M2 — Min vs. Mean Log-Prob Aggregation Sensitivity Across Distribution Types
**Phase:** 3 — Implementation Planning
**Gate:** SHOULD_WORK

---

## 1. Objective

Verify that min log-prob achieves higher Spearman rank-order correlation with hallucination labels than mean log-prob on peaked-distribution benchmarks (TriviaQA, NQ-Open), while mean log-prob achieves higher rank-order correlation than min on flat-distribution benchmarks (TruthfulQA). This is a controlled ablation over the aggregation function applied to per-token log-prob sequences from frozen LLMs.

---

## 2. Background and Motivation

H-M1 confirmed that recall-failure hallucinations on TriviaQA produce significantly higher token distribution peakedness (p=0.0021) under LLaMA-2-7B. H-M2 tests the mechanistic consequence: if peaked distributions concentrate uncertainty at single fact-tokens, then the minimum log-prob (the single worst-case token) should be maximally sensitive to hallucination. Conversely, TruthfulQA features imitative falsehoods with uniformly high confidence — no single token peaks — so mean aggregation integrating across all tokens should outperform min.

This experiment directly precedes H-M3 (full AUROC-based aggregation comparison) and reuses the H-M1 inference pipeline to minimize compute.

---

## 3. Scope

### In Scope
- Token log-prob extraction via HuggingFace `model.generate(output_scores=True)` (greedy decode)
- Three aggregation functions: `min`, `mean`, `raw_sum`
- Two models: LLaMA-2-7B (primary), Mistral-7B-v0.1 (secondary replication)
- Three datasets: TriviaQA (400 samples, Farquhar 2023 split), NQ-Open (400 samples, Farquhar 2023 split), TruthfulQA (817 samples, full generation split)
- Spearman ρ with 95% bootstrap CI per (model, dataset, aggregation method)
- AUROC per (model, dataset, aggregation method) as secondary metric and H-M3 preview
- Figures: ρ differential bar chart (mandatory), scatter plot, AUROC heatmap, distribution overlays
- Reuse of H-M1 cached log-probs for LLaMA-2-7B on TriviaQA/NQ

### Out of Scope
- Fine-tuning or weight modification
- Sampling-based decoding (temperature > 0)
- Dataset beyond the three specified
- Any model beyond LLaMA-2-7B and Mistral-7B-v0.1

---

## 4. Functional Requirements

### FR-1: Inference Pipeline
- Load LLaMA-2-7B and Mistral-7B-v0.1 in fp16 via HuggingFace transformers
- Frozen weights: no gradient computation (`torch.no_grad()`)
- Greedy decode: `do_sample=False, temperature=None`
- Extract per-token log-probs via `output_scores=True, return_dict_in_generate=True`
- `max_new_tokens=20` (short-phrase regime per Farquhar 2023)
- Few-shot prompt format: 4-shot for TriviaQA/NQ (Farquhar 2023 format), 0-shot for TruthfulQA

### FR-2: Data Loading
- TriviaQA: `load_dataset("trivia_qa", "rc.nocontext", split="validation")`, apply Farquhar 2023 seed-fixed 400-sample selection
- NQ-Open: `load_dataset("nq_open", split="validation")`, apply Farquhar 2023 seed-fixed 400-sample selection
- TruthfulQA: `load_dataset("truthful_qa", "generation", split="validation")` — full 817 samples
- Binary correctness labels: exact-match/F1 against reference answers per Farquhar 2023

### FR-3: Aggregation Functions
- `min(token_logprobs)` — most uncertain single generated token
- `mean(token_logprobs)` — average uncertainty across generated tokens
- `raw_sum(token_logprobs)` — joint log-prob (length-dependent baseline)
- Sanity check: `min ≤ mean ≤ 0` for every sample

### FR-4: Statistical Analysis
- Spearman ρ via `scipy.stats.spearmanr(scores, labels)`
- 95% bootstrap CI via `scipy.stats.bootstrap` (n_resamples=1000, paired=True, percentile method)
- AUROC via `sklearn.metrics.roc_auc_score(labels, -scores)` (negated: lower score = more hallucinated)
- Report ρ differential: ρ(min) − ρ(mean) per (model, dataset) with CI

### FR-5: Gate Evaluation
- P1: ρ(min, TriviaQA) > ρ(mean, TriviaQA) for ≥1 model → PASS direction
- P2: ρ(mean, TruthfulQA) > ρ(min, TruthfulQA) for ≥1 model → PASS direction
- Both P1 and P2 must hold for gate PASS; partial pass documents narrowed claim

### FR-6: Figures
- **Mandatory:** ρ differential bar chart — ρ(min) − ρ(mean) per dataset per model, 95% CI error bars
- **Optional:** Spearman ρ scatter (min vs. mean values per dataset/model)
- **Optional:** AUROC heatmap (3 aggregations × 3 datasets × 2 models)
- **Optional:** Token log-prob distribution overlays (TriviaQA vs. TruthfulQA, hallucinated vs. correct)
- All figures saved to `h-m2/figures/`

### FR-7: Caching and Reuse
- Load H-M1 cached token log-probs for LLaMA-2-7B on TriviaQA/NQ if available (`h-m1/results/`)
- Cache all computed token log-probs to disk (numpy `.npy` or pickle) before aggregation
- Graceful fallback to re-inference if cache not found

### FR-8: Logging and Sanity Checks
- Per-sample log: `[H-M2] min={:.4f}, mean={:.4f}, sum={:.4f} for sample {i}`
- Activation check: assert `min ≤ mean ≤ 0` for first 10 samples
- Fail-fast: if ≥5% of samples have zero-length generated sequences, raise exception

---

## 5. Non-Functional Requirements

- **Reproducibility:** Fixed random seed (42) for all dataset sampling; deterministic greedy decode
- **Compute:** ≤4 GPU-hours total for new inference (TruthfulQA + Mistral on all three datasets)
- **Memory:** fp16 inference; 7B models require ≤16GB VRAM; `device_map="auto"` for multi-GPU
- **Code quality:** Single script (`run_hm2.py`) or modular scripts; results written to `h-m2/results/`
- **Portability:** No dependency on jlko/semantic_uncertainty codebase — use HuggingFace datasets directly; jlko/semantic_uncertainty used only as reference for split selection logic

---

## 6. Success Criteria

| Criterion | Threshold | Priority |
|-----------|-----------|----------|
| Code runs without error | 100% completion | MUST |
| P1: ρ(min, TriviaQA) > ρ(mean, TriviaQA) | ≥1 model | MUST (gate) |
| P2: ρ(mean, TruthfulQA) > ρ(min, TruthfulQA) | ≥1 model | MUST (gate) |
| NQ-Open P1 replication | ρ(min, NQ) > ρ(mean, NQ) | SHOULD |
| Mistral replication | P1+P2 on Mistral-7B-v0.1 | SHOULD |
| Mandatory figure generated | ρ differential bar chart | MUST |

---

## 7. Implementation Budget

- **Total budget:** 30 task-points
- **Environment setup:** 1 task
- **Data pipeline (loading + labels + caching):** 5 tasks
- **Inference pipeline (LLaMA-2-7B + Mistral):** 6 tasks
- **Aggregation + statistical analysis:** 5 tasks
- **Figures:** 4 tasks
- **Integration + validation:** 4 tasks
- **Results reporting:** 3 tasks
- **Buffer:** 2 tasks

---

## 8. Dependencies

- `transformers >= 4.35` (LLaMA-2-7B, Mistral-7B-v0.1 support)
- `datasets >= 2.14` (TriviaQA, NQ-Open, TruthfulQA)
- `torch >= 2.0` (fp16 inference)
- `scipy >= 1.11` (spearmanr, bootstrap)
- `scikit-learn >= 1.3` (roc_auc_score)
- `numpy >= 1.24`
- `matplotlib >= 3.7` (figures)
- HuggingFace Hub access for gated model `meta-llama/Llama-2-7b-hf`

---

## 9. Risks

| Risk | Mitigation |
|------|------------|
| Farquhar 2023 split exact reproducibility | Implement seed-fixed sampling to match 400-sample counts; document any minor deviation |
| LLaMA-2-7B gated model access | Verify HF token before launch; Mistral-7B-v0.1 is ungated fallback for primary |
| H-M1 cache format mismatch | Validate array shapes before reuse; re-run inference as fallback |
| TruthfulQA label ambiguity | Use standard `best_answer` field for binary label; document approach |
| Min == Mean edge case | Assert ≥2 generated tokens per sample; filter degenerate 1-token outputs |
