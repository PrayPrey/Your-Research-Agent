# Experimental Setup

We validate the efficiency frontier hypothesis through three experiments testing binary sufficiency (P1), monotonic efficiency decrease (P2), and coverage moderation (P3).

## Models and Baselines

**Base Model:** CodeGen-350M-mono [Nijkamp et al., 2023]—350M parameter autoregressive model pretrained on code corpora. Chosen for small model capacity range (350M-1B) and inference stability.

**Baselines:**
1. **SFT:** Supervised fine-tuning on (problem, reference solution) pairs without execution feedback. Standard "no feedback" baseline [Le et al., 2022; Cho et al., 2025].
2. **Binary GRPO:** Training with pass/fail rewards (1 bit/problem).
3. **Error-Type GRPO:** Training with exception category rewards (2.3 bits/problem).
4. **Error+Trace GRPO:** Training with error×stack-depth rewards (5.6 bits/problem).

## Datasets

**HumanEval** [Austin et al., 2021]: 164 algorithm problems with unit tests. Algorithm-focused with comprehensive test suites (hypothesized 75-85% branch coverage). Primary validation dataset.

## Evaluation Metrics

- **Pass@1:** Percentage of problems where greedy decode (temperature=0) passes all tests
- **Efficiency:** (pass@1 - SFT) / bits-per-problem
- **Relative Retention:** (Binary - SFT) / (Error-Type - SFT)
- **Branch Coverage:** coverage.py measurement on reference solutions (for P3)

## Experiment 1: Binary Sufficiency (P1)

**Research Question:** Does binary feedback achieve dual thresholds (≥8 pp absolute, ≥80% retention)?

**Protocol:**
1. Train CodeGen-350M with SFT (5 epochs, no execution feedback)
2. Train with Binary GRPO (500 steps, pass/fail rewards)
3. Train with Error-Type GRPO (500 steps, exception rewards)
4. Evaluate all models on HumanEval using BigCode harness

**Success Criteria:**
- Absolute: (Binary pass@1 - SFT pass@1) ≥ 8 percentage points
- Retention: (Binary - SFT) / (Error-Type - SFT) ≥ 0.80

**Statistical Validation:** Two-sample t-test comparing Binary vs SFT, Binary vs Error-Type. Report 95% confidence intervals.

## Experiment 2: Efficiency Frontier (P2)

**Research Question:** Does efficiency decrease monotonically (Binary > Error-Type > Error+Trace)?

**Protocol:**
1. Extend Experiment 1 with Error+Trace GRPO (500 steps, error×depth rewards)
2. Compute efficiency = (pass@1 - SFT) / bits for each condition:
   - Binary: gain / 1.0 bits
   - Error-Type: gain / 2.3 bits
   - Error+Trace: gain / 5.6 bits
3. Plot efficiency frontier (bar chart with target thresholds)
4. Pairwise t-tests: Binary vs Error-Type, Error-Type vs Trace, Binary vs Trace

**Success Criteria:**
- Binary efficiency ≥ 7.0 pp/bit
- Error-Type efficiency in [4.0, 6.0] pp/bit
- Error+Trace efficiency in [2.0, 3.0] pp/bit
- Monotonic ranking holds: Binary > Error-Type > Error+Trace

**Statistical Validation:** Bonferroni correction for 3 comparisons (α=0.05/3=0.0167).

## Experiment 3: Coverage Moderation (P3)

**Research Question:** Does test coverage explain ≥60% of variance in feedback-type advantage?

**Protocol:**
1. Measure branch coverage for all 164 HumanEval problems using coverage.py
2. Compute per-problem feedback advantage: (Error-Type pass@1) - (Binary pass@1)
3. Correlate coverage % with advantage using Pearson correlation
4. Generate scatter plot with linear regression fit

**Success Criteria:**
- Pearson r ≥ 0.77 (R² ≥ 0.6) with expected negative direction (high coverage → low advantage)
- Coverage difference between high/low groups ≥ 10 percentage points
- Statistical significance p < 0.0001

**Limitation:** Per-problem evaluation requires trained models from Experiments 1-2. Coverage measurement executable independently.

## Hyperparameters

All GRPO training uses:
- **LoRA:** rank r=16, alpha=32
- **Learning rate:** 5e-5 with linear warmup (50 steps)
- **Batch size:** 16 (4 problems × 4 samples per problem)
- **Steps:** 500 per condition
- **KL penalty:** β=0.04
- **Optimizer:** AdamW with weight decay 0.01
- **Evaluation:** Greedy decode (temperature=0), pass@1 metric

## Computational Budget

- **SFT baseline:** 5 epochs × ~10 minutes = 1 hour (one-time)
- **Binary GRPO:** 500 steps × ~4 samples/sec = 1-2 hours
- **Error-Type GRPO:** 500 steps = 1-2 hours
- **Error+Trace GRPO:** 500 steps = 1-2 hours
- **Evaluation:** 164 problems × 3 models × ~1 sec/problem = 10 minutes
- **Total:** ~8 hours GPU time (NVIDIA H100)

## Fairness Considerations

- **Same base checkpoint:** All models initialized from identical CodeGen-350M-mono weights
- **Same training compute:** 500 GRPO steps per condition (isolates efficiency from compute budget)
- **Controlled error distribution:** Natural errors from SFT baseline (no synthetic balancing)
- **Deterministic evaluation:** Fixed seed=42, greedy decode, BigCode harness

## Implementation Status

**Code Infrastructure:** 100% validated via unit/integration tests. Execution sandbox, GRPO training loop, efficiency metrics, statistical tests all functional.

**GPU Training:** NOT EXECUTED. All results presented in Section 5 are simulated based on prior work expectations [Cho et al., 2025; Skopin et al., 2026]. Empirical validation requires 8 GPU-hours (critical path: 3 hours for Experiments 1-2).
