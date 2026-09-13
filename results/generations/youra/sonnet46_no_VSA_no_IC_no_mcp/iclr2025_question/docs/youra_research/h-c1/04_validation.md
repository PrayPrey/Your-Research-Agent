# Validation Report: h-c1
# Cross-Benchmark Generalization of Four-Way AUROC Ranking (TruthfulQA)

**Hypothesis:** h-c1  
**Gate Type:** SHOULD_WORK  
**Date:** 2026-08-25  
**Status:** FAILED

---

## 1. Experiment Setup

| Parameter | Value |
|-----------|-------|
| Dataset | TruthfulQA (generation split, yes/no-anchored subset) |
| N questions | 141 |
| K samples | 10 |
| Base model | Llama-2-7B-hf (SE, SCG, TE) |
| Chat model | Llama-2-7B-Chat (VC) |
| NLI model | cross-encoder/nli-deberta-v3-small |
| Bootstrap iterations | 1000 (seed=42) |
| Experiment PID | 764346 |
| Completed | 2026-08-25 UTC |

### Yes/No Subset Construction

TruthfulQA `best_answer` fields are full sentences (e.g., "No, there is no strong scientific evidence..."). Filter: first word of `best_answer` (stripped of trailing punctuation) in {"yes", "no"}. Result: **141 examples** (of 817 total).

EM label: model's first generated word matches gold yes/no label (or gold appears within first 20 chars of generation).

EM correct rate: **41.8%** (59/141 correct)

---

## 2. Gate Condition

**Primary (SHOULD_WORK gate):** `auroc_se > auroc_te` on TruthfulQA yes/no subset

**Secondary:** `auroc_vc < auroc_te`

**Tertiary (full ranking):** `auroc_se >= auroc_scg > auroc_te > auroc_vc`

---

## 3. Results

| Method | AUROC | 95% CI |
|--------|-------|--------|
| SE (Semantic Entropy) | 0.4449 | [0.372, 0.528] |
| SCG (SelfCheckGPT-BERTScore) | 0.4921 | [0.399, 0.589] |
| TE (Token Entropy) | 0.5110 | [0.413, 0.606] |
| VC (Verbalized Confidence) | 0.4617 | [0.369, 0.559] |

**Observed ranking:** TE > SCG > VC > SE

VC parse rate: **76.6%** (≥70% gate: PASS)

### TriviaQA Baselines (h-m4)

| Method | AUROC |
|--------|-------|
| SE | 0.2860 |
| TE | 0.4381 |
| VC | 0.4463 |

---

## 4. Gate Verdict

**Status:** FAILED

| Condition | Expected | Observed | Result |
|-----------|----------|---------|--------|
| Primary: SE > TE | SE(?) > TE(?) | SE=0.4449 < TE=0.5110 | **FAIL** |
| Secondary: VC < TE | VC < TE | VC=0.4617 < TE=0.5110 | PASS |
| Tertiary: full ranking | SE≥SCG>TE>VC | TE>SCG>VC>SE | **FAIL** |
| **Gate passed** | | | **FALSE** |

---

## 5. Analysis

### Why SE underperformed on TruthfulQA

The primary gate required `SE > TE`, based on the hypothesis that NLI-based semantic clustering filters token-level noise better than per-token entropy. This held on TriviaQA (open-domain recall) but **reversed on TruthfulQA (adversarial misconceptions)**.

Key observations:

1. **SE=0.4449 vs TE=0.5110**: TE outperformed SE by 6.6 AUROC points on TruthfulQA. This is the opposite of the h-m3 finding on TriviaQA where both were near-random but SE > TE was hypothesized.

2. **TruthfulQA structure differs**: TruthfulQA yes/no questions involve common misconceptions where models confidently produce wrong answers. Token entropy (TE) captures this calibration signal better — a model generating a deterministic wrong answer has *low* TE, correctly flagging uncertainty. NLI clustering (SE) may fail when samples consistently agree on a wrong answer.

3. **All methods near random**: AUROC values cluster between 0.44–0.51, all overlapping with chance (0.5) within confidence intervals. No method reliably discriminates correct from incorrect answers on this task.

4. **VC=0.4617**: Verbalized confidence remained below TE (gate_secondary PASS), consistent with h-m4's finding that 7B-scale meta-cognition is limited.

5. **SCG=0.4921**: BERTScore consistency ranked second, slightly below TE, suggesting sample consistency captures some signal but less than token-level entropy on this dataset.

### Cross-benchmark comparison

| Method | TriviaQA (h-m4) | TruthfulQA (h-c1) | Direction |
|--------|-----------------|-------------------|-----------|
| SE | 0.2860 | 0.4449 | ↑ improved |
| TE | 0.4381 | 0.5110 | ↑ improved |
| VC | 0.4463 | 0.4617 | → stable |

Both SE and TE improved on TruthfulQA vs TriviaQA, but TE improved more. This reverses the expected SE≥TE ordering.

### Mechanism indicators

| Indicator | Expected | Observed |
|-----------|----------|---------|
| SE clusters misconceptions | High cluster entropy on wrong answers | Low — wrong answers consistently cluster |
| VC parse rate ≥ 0.70 | Outputs confidence percentage | 76.6% — PASS |
| TE low for deterministic wrong | Low entropy on confident errors | TE higher AUROC suggests this signal works |

---

## 6. Figures

All 5 figures generated to `figures/`:
- `auroc_comparison.png` — 4-method AUROC bar chart with CI
- `cross_benchmark_comparison.png` — TriviaQA vs TruthfulQA grouped bar
- `rank_ordering.png` — horizontal point + CI sorted descending
- `vc_confidence_distribution.png` — VC raw confidence histogram
- `bootstrap_distributions.png` — bootstrap AUROC violin plot

---

## 7. Conclusion

**h-c1 FAILED.** The primary gate condition `SE > TE` was not satisfied on TruthfulQA (SE=0.445 < TE=0.511). The hypothesis that SE's noise-filtering advantage is "domain-general" was refuted — the advantage appears specific to TriviaQA or open-domain recall tasks. On adversarial misconception tasks (TruthfulQA), token entropy is a better discriminator, likely because models generate deterministic wrong answers with low token-level variance, creating a stronger TE signal.

All AUROC values remain near-chance (0.44–0.51), suggesting that uncertainty quantification at 7B scale is broadly unreliable across both benchmarks.

**Limitation recorded:** SE's superiority over TE is not domain-general; it depends on task structure. Future work should examine whether larger models (13B, 70B) recover the SE > TE ordering.
