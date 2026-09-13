# Phase 2B: Verification Plan
# H-D1 — Source-Alignment Hypothesis for Code SFT
# Generated: 2026-08-02

---

## Main Hypothesis

**H-D1**: Under controlled conditions (post-dedup, problem-count matched, token-budget equalized, supervision-format normalized), SFT training source identity (HumanEval-only / MBPP-only / LeetCode-only / Equal-mix) produces statistically significant and directionally consistent differences in pass@1 on held-out HumanEval+ and MBPP+ for DeepSeek-Coder at both 1.3B and 7B scales, because training-benchmark distributional alignment (measured by code-embedding cosine similarity) governs post-pretraining SFT specialization.

**Null (H0)**: All four source conditions produce pass@1 within ±1.5 pp of each other on both benchmarks at both model sizes.

---

## Sub-Hypothesis Inventory

| ID | Type | Gate | Status | Prerequisites | Prediction |
|----|------|------|--------|---------------|------------|
| H-E1 | EXISTENCE | MUST_WORK | READY | none | Source code-embedding distributions are measurably distinct (pairwise cosine similarity < 0.95) |
| H-E2 | EXISTENCE | MUST_WORK | READY | none | Source identity produces ≥2.0 pp effect on pass@1 at 1.3B, p < 0.05 mixed-effects (P1) |
| H-M1 | MECHANISM | SHOULD_WORK | NOT_STARTED | H-E2 | HE-only > MBPP-only on HumanEval+, MBPP-only > HE-only on MBPP+ (P2 inversion) |
| H-M2 | MECHANISM | SHOULD_WORK | NOT_STARTED | H-E1, H-E2 | Spearman ρ(embedding distance, pass@1 rank) significant via permutation test (P3) |
| H-C1 | CONDITION | SHOULD_WORK | NOT_STARTED | H-E2 | Source effect attenuated at 7B vs 1.3B (pretraining co-exposure probe) |

---

## Dependency DAG

```
H-E1 (embedding distances, pre-exp)
  │
  └──────────────────────────────→ H-M2 (P3 Spearman ρ)
                                           ▲
H-E2 (P1: source effect at 1.3B) ─────────┘
  │
  ├──→ H-M1 (P2: cross-benchmark inversion)
  │
  └──→ H-C1 (scale interaction: 7B attenuation)
```

H-E1 and H-E2 are independent (parallel execution). H-M1, H-M2, H-C1 require H-E2 VALIDATED.

---

## Sub-Hypothesis Specifications

### H-E1 — Embedding Distance Pre-Experiment (MUST_WORK)

**Statement**: The four SFT training sources (HumanEval-train, MBPP-train, LeetCode, Equal-mix) produce measurably distinct code-embedding distributions, confirmed by pairwise mean cosine similarity < 0.95 between each training source and each test benchmark using CodeBERT and all-MiniLM-L6-v2 encoders.

**Why this matters**: If source distributions are indistinguishable in embedding space, the distributional alignment mechanism (P3) is untestable. This is a prerequisite check, not a training experiment.

**Experiment**:
- Encode all problems in each training source and both test benchmarks (HumanEval+, MBPP+) using CodeBERT (`microsoft/codebert-base`) and all-MiniLM-L6-v2
- Compute mean pairwise cosine similarity between each training source and each test benchmark
- Compute pairwise similarity between all training source pairs
- Report 4×2 similarity matrix (4 sources × 2 test benchmarks) per encoder

**Success criterion**: At least one source-benchmark pair shows pairwise cosine similarity < 0.95 (distributions are non-identical). Expected: all pairs well below 0.95 given structural differences between HumanEval doctest style, MBPP utility problems, and LeetCode competitive problems.

**Falsification**: All pairwise cosine similarities > 0.95 — encoders cannot distinguish sources.

**Compute**: Negligible — embedding inference only, no training.

---

### H-E2 — Source Effect Existence at 1.3B (MUST_WORK)

**Statement**: SFT training source identity produces a statistically significant main effect on pass@1 for at least one source-benchmark pair at 1.3B scale, with minimum effect size ≥2.0 absolute percentage points (mixed-effects model p < 0.05, Holm-Bonferroni corrected, direction consistent across ≥2/3 seeds).

**Why this matters**: This is P1 — the core empirical claim. Without a measurable source effect, the alignment mechanism claim collapses and H-M1/H-M2 are uninformative.

**Experiment**:
- Pre-experiment: measure dedup yield per source (all-MiniLM-L6-v2, cosine sim > 0.95 vs HumanEval+ and MBPP+ test sets)
- Construct post-dedup, problem-count-matched, token-budget-equalized training sets for all 4 conditions
- Apply standardized supervision format (uniform prompt template across all sources)
- Run 4 conditions × 1.3B × 3 seeds = 12 SFT runs via TRL SFTTrainer
- Evaluate all 12 checkpoints on HumanEval+ (164 problems) and MBPP+ (374 problems) via EvalPlus (greedy, temperature=0)
- Fit: `pass@1 ~ source_condition + solution_length + (1|problem)` per benchmark
- Pairwise contrasts with Holm-Bonferroni correction

**Success criterion**: Fixed effect of source_condition p < 0.05, minimum pairwise contrast ≥2.0 pp for ≥1 pair, consistent direction across ≥2/3 seeds.

**Falsification**: All pairwise contrasts within ±1.5 pp on both benchmarks across all seeds.

**Compute**: 12 SFT runs on 1.3B model. ~24 compute-hours on 5× H100 (1.3B only portion).

---

### H-M1 — Cross-Benchmark Inversion P2 (SHOULD_WORK)

**Statement**: HumanEval-only training outperforms MBPP-only on HumanEval+, and MBPP-only training outperforms HumanEval-only on MBPP+, consistent across ≥2/3 seeds at 1.3B scale, confirming same-source specialization advantage.

**Prerequisites**: H-E2 VALIDATED.

**Why this matters**: The inversion pattern is the single most compelling evidence for the alignment mechanism. A model that simply learns "more code" would not show this pattern — it requires source-specific representational specialization.

**Experiment**: Re-uses H-E2 experimental data. Additional analysis:
- Extract HumanEval-only vs MBPP-only pass@1 on HumanEval+ and MBPP+ from H-E2 runs
- Check rank order: HE-only > MBPP-only on HumanEval+, MBPP-only > HE-only on MBPP+
- Check inversion across ≥2/3 seeds
- Additional check: LeetCode-only vs MBPP-only inversion

**Success criterion**: Both inversions present in ≥2/3 seeds at 1.3B.

**Falsification**: One or both inversions absent — LeetCode-only dominates both benchmarks (diversity > alignment) or Equal-mix dominates.

**Compute**: Zero additional training. Analysis only.

---

### H-M2 — Distributional Alignment Mechanism P3 (SHOULD_WORK)

**Statement**: Spearman rank correlation between code-embedding mean pairwise cosine similarity (training source → test benchmark) and pass@1 rank order across source conditions is statistically significant via permutation test (10,000 shuffles, p < 0.05) for at least one benchmark at at least one model size.

**Prerequisites**: H-E1 VALIDATED (provides embedding distances), H-E2 VALIDATED (provides pass@1 ranks).

**Why this matters**: P3 is the mechanistic contribution distinguishing H-D1 from a purely descriptive ablation study. Confirms that embedding-space alignment predicts behavioral outcomes.

**Experiment**:
- From H-E1: use pre-computed mean pairwise cosine similarity between each training source and each test benchmark (CodeBERT and all-MiniLM-L6-v2)
- From H-E2 (and H-C1): collect pass@1 per source condition per benchmark per model size
- Rank conditions by embedding distance (closer = higher rank)
- Rank conditions by pass@1 (higher pass@1 = higher rank)
- Compute Spearman ρ between ranks
- Permutation test: shuffle source-condition labels 10,000 times, recompute ρ, check whether observed ρ exceeds 95th percentile
- Dual-encoder robustness check: repeat with CodeBERT and all-MiniLM-L6-v2; require concordance

**Success criterion**: Observed Spearman ρ > 0 with permutation test p < 0.05 for ≥1 benchmark at ≥1 model size, confirmed by both encoders.

**Falsification**: ρ ≤ 0 or permutation p ≥ 0.05 for both benchmarks at both model sizes; or pretraining-source similarity predicts pass@1 better than SFT-source similarity.

**Compute**: Negligible — statistical analysis of H-E1 + H-E2 + H-C1 data.

---

### H-C1 — Scale Attenuation at 7B (SHOULD_WORK)

**Statement**: The SFT source identity effect on pass@1 is attenuated at 7B scale relative to 1.3B (smaller between-condition pass@1 variance at 7B), consistent with larger pretraining coverage reducing the marginal SFT-source alignment signal.

**Prerequisites**: H-E2 VALIDATED.

**Why this matters**: Probes the pretraining co-exposure confound. If LeetCode-only gains diminish at 7B, this supports pretraining co-exposure as a confound at 1.3B. If effects persist at 7B, the SFT distributional alignment mechanism is robust across scale.

**Experiment**:
- Run 4 conditions × 7B × 3 seeds = 12 SFT runs via TRL SFTTrainer (same design as H-E2 but 7B)
- Evaluate on HumanEval+ and MBPP+ via EvalPlus
- Compare between-condition variance (η² from mixed-effects model) at 7B vs 1.3B
- Check whether LeetCode-only advantage on HumanEval+ is attenuated at 7B

**Success criterion**: Between-condition effect size (η² or Cohen's f) is smaller at 7B than 1.3B for at least one benchmark.

**Falsification**: Between-condition variance is equal or larger at 7B — scale does not attenuate source effects.

**Compute**: 12 SFT runs on 7B model. ~24 compute-hours on 5× H100 (7B portion).

---

## Risk Register

| Risk | Affected | Severity | Mitigation |
|------|----------|----------|------------|
| HumanEval-only has 164 train problems — low diversity may fail to produce signal | H-E2 | HIGH | Match tokens via repetition (≥3 epochs); report learning curves |
| n=3 seeds underpowered for 164-problem binomial (SE ~3.7%) | H-E2, H-M1 | HIGH | Mixed-effects model with problem-level random effects; paired bootstrap supplement |
| P3 Spearman ρ fragile with n=4 rank positions | H-M2 | HIGH | 10K permutation test; dual-encoder robustness; report ρ for both encoders |
| Dedup removes large LeetCode fraction (contamination overlap) | H-E1, H-E2 | MEDIUM | Measure retention rate pre-experiment; adjust subsampling accordingly |
| Pretraining co-exposure inflates LeetCode-only gains | H-E2, H-C1 | MEDIUM | 1.3B vs 7B comparison; compare pretrain vs SFT similarity as predictor |
| MBPP I/O examples vs HumanEval docstrings create format confound | H-E2 | MEDIUM | Standardized prompt template applied before any training run |
| Equal-mix confounds diversity with alignment | H-M1, H-M2 | MEDIUM | Treat Equal-mix as falsifier; if it dominates → diversity > alignment (publishable null) |
| CodeContests language mix (C++/Java/Python) | — | LOW | Excluded from main conditions; may add Python-only subset as supplementary |

---

## Timeline

| Day | Task | Sub-hypotheses |
|-----|------|----------------|
| 0.0–0.5 | Pre-exp: dedup yield measurement + embedding distances (H-E1) | H-E1 |
| 0.5–1.0 | Token-budget matching, training set construction (all 4 conditions) | H-E2, H-C1 |
| 1.0–3.0 | 12 SFT runs: 4 conditions × 1.3B × 3 seeds | H-E2 |
| 1.0–3.0 | 12 SFT runs: 4 conditions × 7B × 3 seeds (parallel) | H-C1 |
| 3.0–3.5 | EvalPlus evaluation on all 24 checkpoints | H-E2, H-M1, H-C1 |
| 3.5–3.75 | Mixed-effects analysis + Holm-Bonferroni (P1/P2) | H-E2, H-M1 |
| 3.75–4.0 | Permutation test for P3 Spearman ρ | H-M2 |
| 4.0 | Scale attenuation analysis (η² comparison) | H-C1 |

**Total**: ~4 days on 5× H100 (~48 compute-hours).

---

## Dialectical Analysis

**Thesis**: SFT distributional alignment governs specialization. Training on HumanEval-style problems creates representations aligned with HumanEval+ test distribution, producing measurably higher pass@1 on that benchmark relative to MBPP- or LeetCode-trained models.

**Antithesis**: Diversity beats alignment. Equal-mix, by exposing the model to more structural variety, may generalize better than any single-source condition. The pretraining effect already saturates alignment signals at 7B, making SFT-source identity irrelevant at that scale.

**Synthesis**: The experimental design captures both. If Equal-mix dominates → diversity > alignment (P2/P3 falsified but P1 still positive and independently publishable). If same-source conditions dominate on native benchmarks → alignment wins for specialized SFT. The 1.3B vs 7B comparison separates pretraining co-exposure from SFT-driven effects. The transfer matrix (4×2×2) is a reusable empirical resource regardless of which mechanism dominates.

---

## Gate Summary

| Sub-hypothesis | Gate | Failure consequence |
|----------------|------|---------------------|
| H-E1 | MUST_WORK | H-M2 blocked; P3 cannot be tested |
| H-E2 | MUST_WORK | H-M1, H-M2, H-C1 all blocked; pipeline routes to Phase 0 if FAIL, Phase 2A-Dialogue if PARTIAL |
| H-M1 | SHOULD_WORK | Does not block Phase 5; partial result noted |
| H-M2 | SHOULD_WORK | Does not block Phase 5; mechanistic claim weakened |
| H-C1 | SHOULD_WORK | Does not block Phase 5; confound probe inconclusive |
