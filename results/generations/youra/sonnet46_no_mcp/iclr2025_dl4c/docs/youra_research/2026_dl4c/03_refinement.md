# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-05-02T00:00:00
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: gap-1
- **Gap Title**: No Systematic Evidence on Training Data Difficulty Composition Effects on Execution-Feedback GRPO Gains
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All 6 criteria met at exchange 15 — SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS

### Key Insights
- The H-M1 failure (reward density collapse at repo level) is the generative insight: the same mechanism applies at function level when problem difficulty is mismatched to model capability at training time.
- Reward density (binary: degenerate/non-degenerate step) and reward entropy (H(p) of G=8 reward distribution per batch) together characterize gradient signal quality. Entropy captures the "Goldilocks zone" where ≈4/8 completions succeed, maximizing GRPO advantage informativeness.
- The easy-ceiling concern is genuine: HumanEval+/MBPP+ are closer in distribution to APPS tiers 0-2 than tiers 3-4. Easy-only vs. curriculum comparison is left empirically open; the key directional prediction is curriculum ≥ uniform only.
- Prof. Rex's mediation circularity concern resolved by time-series correlation: checkpoint reward density at step T predicts pass@1 gain from T to T+500, not just cross-condition comparison.

### Breakthrough Moments
- **Exchange 2 (Prof. Vera)**: Separating static curriculum (primary IV, testable) from dynamic difficulty selection (separate hypothesis) — keeps the ablation clean and answerable.
- **Exchange 6 (Prof. Rex)**: Identifying reward density mediation circularity — resolved by time-series approach, strengthening the mechanistic claim.
- **Exchange 9 (Dr. Sage)**: Reframing from "ablation study" to "three-level contribution" (empirical + mechanistic + practical guidance) — elevates significance from incremental to principled.

---

## Final Hypothesis

### Title
Difficulty-Stratified Curriculum GRPO: Reward Density Mediation in Execution-Feedback Code LLM Training

### Hypothesis ID
**H-CurriculumGRPO-v1**

### Core Claim
Under DeepSeek-Coder-7B + GRPO with unit-test execution reward on APPS+CodeContests,
**if** training data is ordered easy→hard by APPS difficulty tiers (fixed split: steps 0–2500 from tiers 0–2, steps 2501–5000 from tiers 3–4),
**then** final pass@1 on HumanEval+ and MBPP+ is significantly higher than uniform random sampling from the same dataset,
**because** easy problems during early training maintain higher reward density (fraction of non-degenerate GRPO steps), producing informative group-relative advantage estimates and more effective policy gradient updates.

**Null hypothesis (H0):** No significant difference in final pass@1 between easy-only, hard-only, uniform, and easy→hard curriculum conditions at equal compute budget (5000 gradient steps).

### Mechanism
Three-step causal chain:

1. **Difficulty composition → Reward density**: Hard problems early in training cause all G=8 completions to fail → GRPO advantage std=0 → zero gradient (mathematically guaranteed by A_i = (r_i − mean)/std). Easy problems → some completions pass → informative advantages.

2. **Reward density → Gradient quality**: Higher reward density = more non-degenerate steps = larger cumulative policy update. Reward entropy H(p) of the G=8 reward distribution peaks at ≈4/8 successes (the "Goldilocks zone"), measuring gradient informativeness directly.

3. **Gradient quality → Benchmark performance**: More effective early policy updates generalize to function-level benchmarks (HumanEval+, MBPP+), producing higher final pass@1. Instantiates Bengio et al. 2009 curriculum theory in GRPO execution-feedback RL — the first such instantiation.

---

## Predictions

| ID | Type | Statement | Success Criterion | Falsification |
|----|------|-----------|------------------|---------------|
| **P1** | Primary | Curriculum achieves ≥2pp higher HumanEval+ pass@1 than uniform | McNemar's p<0.05 (one-tailed), ≥2pp absolute | Curriculum ≤ uniform+2pp or p≥0.05 |
| **P2** | Mechanism | Curriculum reward density > uniform (steps 0–2500); checkpoint reward density predicts subsequent pass@1 gain | Pearson r>0.5 for checkpoint reward density vs. subsequent gain | Reward density not higher early, or r≤0.5 |
| **P3** | Transfer | Curriculum outperforms uniform on APPS test split | One-tailed p<0.05 | No significant difference on APPS test split |

**Support levels:** STRONG = P1+P2 | PARTIAL = P1 only | FALSIFIED = P1 fails

**Compute efficiency (Q5):** Curriculum advantage at step 2500 ≥ advantage at step 5000 (measured free via mid-training checkpoints).

---

## Novelty

**What's new:**
- First systematic ablation of training data difficulty composition for execution-feedback GRPO code training
- First measurement of reward density/entropy stratified by difficulty condition with time-series mediation analysis
- First instantiation of Bengio et al. 2009 curriculum learning theory in GRPO execution-feedback RL

**Differentiation from prior work:**
- CodeRL (Le 2022): uses APPS but uniform sampling only; no difficulty stratification
- RLEF (Gehring 2024): execution-feedback RL but no difficulty curriculum analysis
- DeepSeek-R1 (2025): GRPO at scale but fixed training mix; reward density not measured per difficulty
- Bengio 2009: general curriculum theory, not instantiated in execution-feedback RL

**Practical guidance derived:** Select training problems where model's current solve rate ≈ 10–40% (the reward-informative Goldilocks zone). Model-agnostic if P2 (reward density mediation) holds.

---

## Experimental Design

**Conditions (4):**
| Condition | Sampling Strategy |
|-----------|------------------|
| easy-only | APPS tiers 0–2 only, all 5000 steps |
| hard-only | APPS tiers 3–4 only, all 5000 steps |
| uniform | Random sampling across all tiers, proportional to dataset |
| easy→hard | Tiers 0–2 steps 0–2500; tiers 3–4 steps 2501–5000 (fixed split) |

**Model:** DeepSeek-Coder-7B-base
**Framework:** TRL GRPOTrainer, G=8, 5000 gradient steps, single A100 80GB
**Primary eval:** HumanEval+ (164), MBPP+ (378) via EvalPlus harness
**Secondary eval:** APPS test split, LiveCodeBench (same checkpoints, zero additional training)
**Diagnostics:** Reward density + reward entropy at 10 checkpoints (every 500 steps)
**Statistics:** McNemar's test (P1, P3), Pearson correlation (P2)
**Compute:** ~9 GPU-days total (4 × ~14h per condition)

---

## Limitations

1. **Distribution shift**: APPS training domain (competitive programming) ≠ HumanEval+/MBPP+ eval domain (general function-level Python). Mitigated by Q4 APPS test split (within-domain) secondary evaluation.
2. **Fixed split is a simplification**: 50/50 easy/hard split at step 2500 is the primary operationalization; optimal split ratio unexplored.
3. **Single model size**: Results at 7B parameter scale only; reward density sweet spot generalization to other model sizes is future work.
4. **Static labels**: APPS tiers are static human labels; model's actual solve rate per tier changes during training and may diverge from labels.
5. **Easy-only outcome is open**: HumanEval+ proximity to APPS tiers 0–2 means easy-only may outperform or match uniform; not a predicted ordering.

---

## Decision

| Item | Status |
|------|--------|
| **Hypothesis ID** | H-CurriculumGRPO-v1 |
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met at exchange 15 (15 exchanges, all personas) |
| **Clarity Verified** | Yes |
| **Novelty Verdict** | STRONG (Dr. Nova) |
| **Falsifiability Verdict** | STRONG (Prof. Vera) |
| **Significance Verdict** | STRONG (Dr. Sage) |
| **Feasibility Verdict** | STRONG (Prof. Pax) |
| **Remaining Objections** | Distribution shift (mitigated), easy-only outcome (open), model-size generalization (future work) |
| **Phase 2B Ready** | YES |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
*Gap: gap-1 | Exchanges: 15 | Personas: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex*
