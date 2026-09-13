# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-26
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Independent-Controller Ablation)
- **Gap ID**: gap-1
- **Gap Title**: Lack of Controlled Multi-Benchmark Comparison of RLEF vs SFT Across Difficulty Levels
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 12

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 12

**Convergence Reason**: All 6 convergence criteria met at Exchange 12 (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights
1. Reframing the research question from "does RLEF work?" to "at what difficulty does execution feedback become irreplaceable?" unlocked the difficulty-scaling hypothesis (Exchange 1, Dr. Nova)
2. Scoping evaluation to correctness-only (no time limits) eliminates a fundamental confound and makes the experiment clean (Exchange 4, Prof. Pax)
3. Embedding reward formulation ablation into the controlled framework allows one experiment to address both Gap 1 and Gap 2 simultaneously (Exchange 5, Dr. Ally)
4. The mechanistic proxy test (non-zero reward fraction by difficulty, P3) provides a novel empirical handle with zero additional implementation cost

### Breakthrough Moments
- **Exchange 1**: "At what difficulty does execution feedback become irreplaceable?" — core reframe
- **Exchange 4**: Correctness-only scope — eliminates time-limit confound
- **Exchange 5**: Reward ablation embedded in same framework — two gaps, one experiment
- **Exchange 7**: 1.3B secondary model — simultaneously addresses SFT ceiling and model-scale concerns

---

## Final Hypothesis

### Title
**Difficulty-Scaled RLEF: Execution Feedback Advantage Grows with Benchmark Difficulty**

**Hypothesis ID:** H-DifficultyScaledRLEF-v1

### Core Claim
Under controlled fine-tuning conditions (fixed base model: DeepSeek-Coder-7B; fixed training data: APPS dataset; fixed evaluation: bigcode-evaluation-harness correctness-only), if a language model is trained with RLEF using fraction-of-tests-passing reward (versus SFT baseline), then the performance advantage of RLEF over SFT increases monotonically with benchmark difficulty from HumanEval (easy) → MBPP (medium-easy) → LiveCodeBench-Easy/Medium/Hard, because execution feedback enables non-zero gradient signal from partially-correct solutions at difficulty levels where SFT's fully-supervised objective receives zero gradient.

### Mechanism
1. **SFT signal void at hard difficulty**: At hard benchmarks (LiveCodeBench-Hard), APPS training data has sparse fully-correct solutions. SFT's next-token prediction objective receives near-zero gradient from hard problems with no correct training examples.
2. **RLEF partial-success gradient**: Even at hard difficulty, a 7B model generates partially-correct solutions (e.g., 3/5 tests pass). Fraction-of-tests reward assigns non-zero reward proportional to partial success, providing gradient signal where SFT has none.
3. **Incremental improvement path**: RLEF with fraction reward directly optimizes test-passing rate incrementally (2/5 → 3/5 → 4/5 → 5/5). This incremental path is absent in SFT's all-or-nothing objective.
4. **Difficulty-scaling consequence**: RLEF's gradient advantage grows as difficulty increases (SFT signal void grows; RLEF partial-success signal remains non-zero) → gap (Δ) widens with benchmark difficulty.

**Binary reward** is intermediate: provides some signal beyond SFT but loses the incremental structure that fraction reward preserves.

---

## Predictions

| ID | Statement | Falsification |
|----|-----------|---------------|
| **P1** (primary) | Δ(Fraction-RLEF, SFT) at LiveCodeBench ≥ 1.5× Δ at HumanEval (p < 0.05, bootstrap) | Δ_LiveCodeBench/Δ_HumanEval < 1.5 or not significant |
| **P2** | Fraction reward > Binary reward gap over SFT at hard benchmarks; no significant difference at easy benchmarks | No interaction effect between reward type and difficulty |
| **P3** | Non-zero reward fraction during RLEF training correlates with APPS problem difficulty | Non-zero reward fraction uniform across difficulty (RLEF has signal void at hard too) |
| **P4** | Directional pattern (gap widens with difficulty) holds for DeepSeek-Coder-1.3B | Pattern inverts at 1.3B scale |

---

## Novelty

**What's new:** First difficulty-stratified controlled comparison of RLEF vs SFT across the full difficulty spectrum (HumanEval → MBPP → LiveCodeBench) using a reproducible open-source pipeline. Prior work (CodeRL, PPOCoder, RLTF, RLEF-2024) each evaluates on subsets with different models/data/protocols — no controlled apples-to-apples comparison exists. RLEF-2024 provides the strongest evidence but uses a non-reproducible Meta internal model.

**Key differentiator:** Difficulty-stratified analysis + embedded reward formulation ablation + mechanistic proxy test + fully reproducible open-source pipeline (TRL + bigcode-harness + public DeepSeek-Coder weights).

---

## Experimental Design

| Component | Choice | Justification |
|-----------|--------|---------------|
| Base model | DeepSeek-Coder-7B-base (primary); 1.3B (sanity) | Public weights; code-specialized; not saturated at HumanEval from base |
| Training data | APPS dataset (~5000 Python problems with unit tests) | Public; spans easy-to-hard; provides both SFT targets and RLEF execution signals |
| Training methods | SFT baseline; RLEF-Binary (GRPO); RLEF-Fraction (GRPO) | Isolates training method effect; reward ablation embedded |
| Evaluation | bigcode-evaluation-harness correctness-only | Eliminates time-limit confound; covers all needed benchmarks |
| Benchmarks | HumanEval (easy, 164) + MBPP (medium-easy, 374) + LiveCodeBench-Q4 snapshot (medium/hard) | Full difficulty spectrum; contamination-free (LiveCodeBench temporal filtering) |
| Execution sandbox | Docker/subprocess with timeout for APPS test execution | Required for safe reward computation; existing solved pattern in TRL |

---

## Limitations

- Results scoped to 7B-scale models fine-tuned on APPS (explicitly stated; 1.3B sanity check added)
- Correctness-only evaluation — does not capture time complexity requirements of competitive programming
- APPS test quality variability (1-20 tests/problem) affects reward signal consistency
- LiveCodeBench-Hard may represent difficulty extrapolation beyond APPS training, not just generalization
- Single training dataset (APPS) — results may not generalize to models trained on different code corpora

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met at Exchange 12 of 12 |
| **Clarity Verified** | Yes |
| **Feasibility Confirmed** | Yes (TRL + APPS + bigcode-harness + public weights) |
| **Remaining Objections** | Non-blocking (problem-type distribution supplementary; threshold justification in paper) |

---

*Phase 2A Complete — Proceed to Phase 2B*
*Architecture: Self-Contained Tikitaka Loop (Independent-Controller Ablation)*
*All 6 personas participated across 12 exchanges*
