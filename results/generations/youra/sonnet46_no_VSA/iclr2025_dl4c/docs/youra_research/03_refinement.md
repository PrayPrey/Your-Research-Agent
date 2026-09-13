# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-02T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap-1
- **Gap Title**: No Source-Mix Ablation for Code-Specific SFT on Execution Benchmarks
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 16
- **Recursive Entry**: v4 (3 prior Phase 2A archives)

---

## Research Dialogue Context

**Participants**: Dr. Nova (Creative Novelty Explorer), Prof. Vera (Rigorous Validation Architect), Dr. Sage (Research Impact Evaluator), Prof. Pax (Feasibility & Reality Checker), Dr. Ally (Hypothesis Strengthening Champion), Prof. Rex (Hypothesis Stress-Test Master)

**Total Exchanges**: 16

**Convergence Reason**: Pre-registered, falsifiable validation of the distributional alignment hypothesis with explicit rank-order predictions, effect-size thresholds, and equal-mix structural control. All 6 convergence criteria met.

### Key Insights
1. **Source identity must be operationalized as a post-dedup, token-matched, format-normalized intervention** — "equal tokens" is insufficient; unique-problem count × repetition rate must also be matched.
2. **The equal-mix condition is a structural falsifier**, not just a baseline: if it dominates all single sources, diversity beats alignment; if intermediate, specialization-plasticity tradeoff confirmed.
3. **Statistical power is the critical constraint** given HumanEval's small test set (164 problems) — mixed-effects model with problem-level random effects is necessary.
4. **Pretraining co-exposure is the primary confound** — 1.3B vs 7B comparison is its diagnostic.
5. **The cross-benchmark inversion prediction** (LC vs MBPP swap across HumanEval+/MBPP+ benchmarks) is the single most novelty-proving finding if it appears.

### Breakthrough Moments
- **Exchange 6**: Dr. Ally's first complete H-D1 formulation integrating all confound controls
- **Exchange 8**: Prof. Rex's pre-registration of directional rank orderings — converted from descriptive to falsifiable
- **Exchange 12**: Final strengthened hypothesis with all confound mitigations and fully pre-specified P1/P2/P3
- **Exchange 15**: Dr. Sage's "geometry-aware specialization" framing — elevates from ablation to conceptual contribution

---

## Final Hypothesis

### Title
H-D1: Source-Alignment Hypothesis for Code SFT

### Core Claim

Under controlled conditions (post-dedup, problem-count matched, token-budget equalized, supervision-format normalized across all sources), if SFT training source identity is varied (HumanEval-only vs MBPP-only vs LeetCode-only vs Equal-mix), then pass@1 on held-out HumanEval+ and MBPP+ will differ significantly across conditions for DeepSeek-Coder at both 1.3B and 7B scales, **because training-benchmark distributional alignment (measured by code-embedding cosine similarity) governs post-pretraining SFT specialization**.

**Null Hypothesis**: All four source conditions produce pass@1 within ±1.5 pp of each other on both benchmarks at both model sizes.

### Mechanism

Three-step causal chain:

1. **Distributional divergence**: Different code sources (HumanEval-train, MBPP-train, LeetCode) define structurally distinct conditional distributions P_train(x,y) — measurable via code-embedding cosine similarity.

2. **SFT specialization**: Gradient updates directionally bias pretrained weights toward P_train, producing stylistic and structural representational specialization in the fine-tuned model.

3. **Alignment → performance**: The fine-tuned model's pass@1 on benchmark B is higher when P_train is distributionally closer to P_test(B) — the "closest distribution wins" principle.

**Key tension**: Pretraining co-exposure — LeetCode solutions are prevalent on GitHub and likely already encoded in DeepSeek-Coder's pretrained weights, potentially confounding SFT-driven alignment effects.

---

## Predictions

### P1 (Primary / MUST_WORK)
**Statement**: Source identity has a statistically significant main effect on pass@1 for at least one source-benchmark pair at 1.3B scale.
**Method**: Linear mixed-effects model (pass@1 ~ source_condition + (1|problem) + solution_length), Holm-Bonferroni correction.
**Success**: p < 0.05, ≥2.0 pp effect for ≥1 pairwise contrast at 1.3B, consistent direction ≥2/3 seeds.
**Falsification**: All pairwise contrasts within ±1.5 pp on both benchmarks at both scales.

### P2 (Cross-Benchmark Transfer / SHOULD_WORK)
**Statement**: Cross-benchmark transfer is asymmetric — HumanEval-only > MBPP-only on HumanEval+, and MBPP-only > HumanEval-only on MBPP+ (directional inversion), consistent ≥2/3 seeds.
**Pre-registered rank order**:
- HumanEval+: HumanEval-only > LeetCode-only > Equal-mix > MBPP-only
- MBPP+: MBPP-only > Equal-mix > LeetCode-only > HumanEval-only
**Falsification**: LeetCode-only dominates on BOTH benchmarks, suggesting diversity/difficulty rather than alignment drives performance.

### P3 (Mechanistic / COULD_WORK)
**Statement**: Spearman rank correlation between code-embedding distributional distance (train source → test benchmark) and pass@1 rank order is statistically significant via permutation test.
**Method**: CodeBERT or frozen DeepSeek embeddings; mean pairwise cosine similarity between training source and test benchmark; Spearman ρ; 10,000-shuffle permutation test.
**Success**: ρ > 0, p < 0.05 for ≥1 benchmark at ≥1 model size.
**Falsification**: ρ non-significant via permutation test for both benchmarks at both scales; OR pretraining similarity explains more variance than SFT-source similarity.

---

## Novelty

**Core novelty**: First controlled source-identity ablation for code SFT that simultaneously measures behavioral effects (pass@1 transfer matrix), validates the alignment mechanism (distributional distance correlation), and uses equal-mix as a structural falsifier for diversity vs alignment.

**Key differentiators from prior work**:
- DoReMi/DomainPilot/Chameleon: general LLM domain mixture (not code-specific, not source-identity isolation)
- Lv et al. (2025): data selection/quality within a single source (not source dataset identity ablation)
- Chen et al. (2024): atomic vs synthetic source types (not HumanEval vs MBPP vs LeetCode)
- DeepSeek-Coder, WizardCoder: use mixed sources, never isolate single-source conditions

**Novel empirical contribution**: 4-source × 2-benchmark × 2-model-size transfer matrix — does not exist in any prior work.

---

## Experimental Design

**Conditions**: 4 source conditions × 2 model sizes × 3 seeds = 24 SFT runs

| Condition | Source | Details |
|-----------|--------|---------|
| HumanEval-only | openai_humaneval train split | 164 problems post-dedup, ≥3 epochs |
| MBPP-only | google-research-datasets/mbpp train | 374 problems post-dedup, calibrated epochs |
| LeetCode-only | newfacade/LeetCodeDataset (Python-only) | Subsampled to match unique-problem count × repetition rate |
| Equal-mix | Equal proportion from HE+MBPP+LeetCode | Token-budget matched |

**Model sizes**: DeepSeek-Coder-1.3B-Base and 7B-Base

**Evaluation**: EvalPlus (HumanEval+ and MBPP+), greedy decoding (temperature=0)

**Pre-experiment steps**:
1. Dedup yield measurement per source (Gap 3 measurement)
2. Code-embedding distributional distance computation (P3 ground truth)
3. Supervision format normalization (standardized prompt template)

**Compute**: ~48 hours on 5× H100 NVL

---

## Limitations

1. **HumanEval training set is small** (164 problems) — limits diversity of HumanEval-only condition; saturation likely by epoch 3.
2. **Pretraining co-exposure** — LeetCode on GitHub likely in DeepSeek-Coder pretrained weights; 1.3B vs 7B comparison is the diagnostic.
3. **CodeContests excluded from primary analysis** — C++/Java/Python mix is a language confound; Python-only subset used or condition treated as supplementary.
4. **P3 statistical fragility** — Spearman ρ with n=4 sources is fragile to single rank swaps; permutation test + dual-encoder robustness check required.
5. **Scope**: Results apply to base models (not instruction-tuned), 1.3B-7B scale, Python-only code, execution-based evaluation only.

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Hypothesis ID** | H-D1 |
| **Discussion Convergence** | Exchange 16 — all 6 criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | CodeContests language confound (mitigated), pretraining co-exposure (probed by scale comparison) |
| **Phase 2B Readiness** | READY |

---

*Generated by Phase 2A Self-Contained Tikitaka Loop (UNATTENDED mode)*
*Recursive entry v4 — prior hypotheses H-E1 (FAIL: p_eff mismatch), h-m1 (FAIL: gradient clipping), H-E1 run 2 (PASS: gradient magnitude differential)*
*All prohibited approaches avoided: no RL, no gradient variance measurement, no Mann-Whitney on <50 steps, no human annotation*
