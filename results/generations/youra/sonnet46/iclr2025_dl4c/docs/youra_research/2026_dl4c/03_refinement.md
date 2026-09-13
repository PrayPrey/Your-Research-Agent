# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-03-15T16:00:00
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: gap-1
- **Gap Title**: Ratio vs Binary Reward Comparison Under Partial-Tractability GRPO Training
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15
- **Pipeline Project**: Anonymous Pipeline: Reward Signal Design for GRPO on Tractable Code Generation

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All 6 convergence criteria met — SPECIFIC core claim with Binomial variance model, MECHANISM (within-group heterogeneity → graded advantages), PREDICTIONS (3 pre-registered with statistical thresholds), NOVELTY (new GRPO variance amplification framing), FEASIBILITY (existing infrastructure confirmed), OBJECTIONS (all major criticisms addressed with pre-registered mitigations)

### Key Insights
- R_ratio's advantage is information-theoretic, not merely "non-zero gradients" — it increases within-group reward heterogeneity that GRPO's group-relative normalization exploits for graded policy learning
- The Binomial(T, q) analytic model proves E[Var(r_ratio)] > E[Var(r_binary)] for all T > 1 and 0 < q < 1 — the variance advantage sign is always positive in partial-tractability regime
- ZRF reduction is a dynamical training effect (policy learns to produce more partial solutions), NOT an instantaneous reward property — this distinction is critical for experimental design
- The prescreening gate serves dual purposes: (1) tractability confirmation (fraction(k_pass ≥ 1) ≥ 10%), and (2) variance condition validation (E[Var(r_ratio)] / E[Var(r_binary)] ≥ 1.5×)
- R_ratio must be defined as per-rollout test-case pass fraction (tests_passed_i / total_tests_i), not the rollout-level all-pass indicator

### Breakthrough Moments
- **Exchange 3 (Prof. Rex)**: Identified the critical distinction between rollout-level full-pass (k_pass in GRPO) and per-rollout test-case fraction — forced clarification of R_ratio definition
- **Exchange 7 (Dr. Ally)**: Synthesized the R_ratio redefinition as per-rollout test-case fraction — the key structural clarification enabling the variance amplification argument
- **Exchange 10 (Prof. Pax)**: Operationalized gradient SNR as Var(r_ratio)/Var(r_binary) proxy — making the 1.5× criterion computable from prescreening data
- **Exchange 15 (Prof. Pax)**: Derived the Binomial(T, q) closed-form model confirming analytical variance dominance — converting the hypothesis from empirical guess to analytic prediction

---

## Final Hypothesis

### Title
Prescreening-Gated R_ratio vs R_binary: Within-Group Variance Amplification in GRPO for APPS Introductory Problems

### Hypothesis ID
H-RatioReward-v1

### Core Claim
Under GRPO-based RLEF training on APPS introductory problems (difficulty=0) prescreened to S_term ∈ [0.3, 0.55] with Qwen2.5-Coder-7B-Instruct + SFT checkpoint (max_new_tokens=1024, temperature=0.8, G=8 rollouts per prompt):

**IF** the prescreening run confirms E[Var(r_ratio within group)] / E[Var(r_binary within group)] ≥ 1.5× AND within-group pass fraction distribution is non-degenerate,

**THEN** during GRPO training:
- (a) R_ratio will show earlier ZRF escape: ZRF_ratio(t*) < 0.8 × ZRF_binary(t*) for some t* in first 25% of training, with log-rank p < 0.05
- (b) Gradient SNR under R_ratio ≥ 1.5× that under R_binary in first 25% of training steps

**BECAUSE** R_ratio (defined as per-rollout fraction of test cases passed: r_i = tests_passed_i / total_tests_i) preserves within-group reward heterogeneity that R_binary clips to {0,1}, enabling GRPO's group-relative advantage normalization to produce informative graded policy gradients at training steps where rollouts have partial (but not full) test-case success.

### Null Hypothesis (H0)
There is no significant difference in ZRF trajectory (log-rank test p ≥ 0.05) or mean gradient SNR (ratio < 1.5×) between R_ratio and R_binary on the prescreened APPS introductory subset under identical GRPO hyperparameters. Any observed differences reduce to step-size scaling effects from the variance magnitude difference, not informational structure.

### Mechanism
1. **Step 1 — Variance Existence**: Prescreening confirms E[Var(r_ratio)] / E[Var(r_binary)] ≥ 1.5×. Analytically guaranteed by Binomial(T, q): E[Var(r_ratio)] = q(1-q) >> E[Var(r_binary)] = q^T(1-q^T) for typical APPS test-case counts T ∈ [5, 30] and q ∈ [0.3, 0.6].
2. **Step 2 — Graded Advantages**: R_ratio produces graded normalized advantages A_i within each GRPO group of G=8 rollouts (up to T distinct levels), vs near-binary on/off under R_binary.
3. **Step 3 — Gradient Covariance**: Graded advantages provide higher Cov(r_i, ||∇θ log π(o_i)||) — policy gradients are informative about which generation styles produce more test-case coverage.
4. **Step 4 — ZRF Escape**: Earlier policy differentiation toward partial solutions increases hazard rate of first full-pass rollout per problem, measurable as ZRF escape and gradient SNR improvement.

---

## Predictions

### P1 (Primary — Prescreening Gate)
- **Statement**: E[Var(r_ratio within group)] / E[Var(r_binary within group)] ≥ 1.5× on prescreened APPS introductory subset
- **Test**: Pass@8 inference on prescreened set; compute within-group variance ratio from rollout outputs
- **Success**: Ratio ≥ 1.5× across ≥80% of problem groups

### P2 (Primary — ZRF Escape)
- **Statement**: GRPO training with R_ratio shows earlier ZRF escape vs R_binary (log-rank p < 0.05)
- **Test**: 3 seeds × 2 conditions; log per-step ZRF; log-rank test on ZRF escape survival curves
- **Success**: Log-rank p < 0.05; ZRF_ratio(t*) < 0.8 × ZRF_binary(t*) for some t* in first 25%; 2/3 seeds consistent

### P3 (Secondary — Gradient SNR)
- **Statement**: Mean gradient SNR over first 25% of training ≥ 1.5× under R_ratio vs R_binary
- **Test**: Compute per-step SNR = |E[A_i]| / std(A_i) from GRPO training logs
- **Success**: Mean SNR(R_ratio) / Mean SNR(R_binary) ≥ 1.5× over first 25% of steps

---

## Novelty

The within-group variance amplification framing is new to the GRPO-for-code literature. Prior work (DRIVE, GHPO, PPOCoder, G2RPO-A) universally uses R_binary without examining whether within-group reward heterogeneity affects gradient quality. The analytical Binomial(T, q) model connecting reward function choice to variance advantage under GRPO normalization is a new theoretical contribution. The prescreening-gated R_ratio intervention is the minimal-overhead alternative to GHPO (requires oracle hints), DRIVE (requires curriculum scheduling), and PRLCoder (requires per-statement reward model).

---

## Experimental Design

- **Dataset**: APPS introductory (difficulty=0), prescreened to S_term ∈ [0.3, 0.55] via pass@8 inference
- **Model**: Qwen2.5-Coder-7B-Instruct + SFT checkpoint (h-e1/code/sft_checkpoint/)
- **Conditions**: R_ratio (per-rollout test-case fraction) vs R_binary (all-pass indicator)
- **Hyperparameters**: G=8 rollouts, max_new_tokens=1024, 3 seeds per condition, TRL v0.29.0 GRPOTrainer
- **Baselines**: R_binary GRPO (primary); PPOCoder 17.77% pass rate on APPS (field reference)
- **Analysis**: Log-rank test (ZRF survival curves), per-step gradient SNR comparison, prescreening variance ratio

---

## Limitations

- Test-case independence assumption (Binomial model) may not hold for all APPS problems; empirical validation required
- Claims explicitly scoped to first 25% of training steps; later dynamics are out of scope
- Single model (Qwen2.5-Coder-7B); generalizability to other models not claimed
- SFT checkpoint is model-specific; practitioners with different checkpoints must run their own prescreening

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | 15 exchanges; all 6 criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None blocking — test-case independence caveat and normalization concern pre-registered as diagnostic checks |
| **Phase 2B Ready** | YES |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
*Pipeline: Anonymous Pipeline: Reward Signal Design for GRPO on Tractable Code Generation*
*Hypothesis: H-RatioReward-v1*
