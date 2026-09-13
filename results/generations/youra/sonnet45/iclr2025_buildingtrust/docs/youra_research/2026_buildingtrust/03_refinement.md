# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-03-17T00:35:30Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: gap-1
- **Gap Title**: No Systematic Study of H2 Boundary-Shift Severity as Predictable Function of Pre-Alignment Model Properties
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 16

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 16

**Convergence Reason**: All 6 convergence criteria met. Prof. Rex's KL confound objection was the final blocker — resolved by including KL covariate in regression design.

### Key Insights
1. Pre-alignment confidence margin (top-1 minus top-2 log-prob) is a structural signal for alignment susceptibility — low-margin items are both epistemically fragile (Plaut et al.) and optimization-fragile
2. DPO's log-odds objective mechanistically predicts higher-variance argmax inversions at low margin than PPO's KL-constrained gradient — derived from first principles of the objective functions
3. The work extends Fan et al.'s pretraining→SFT correlation findings to pretraining→RLHF, with method-specific (PPO vs DPO) geometric signatures as the novel contribution
4. KL covariate control is essential to distinguish geometric structure from mere update magnitude

### Breakthrough Moments
- **Exchange 8 (Prof. Rex)**: Identified that model pairs need to be confirmed on HuggingFace — confirmed (tulu-2-base/dpo/ppo, Pythia variants). Shifted discussion to concrete falsifiability.
- **Exchange 13 (Prof. Rex → Prof. Vera)**: KL confound identification + resolution via covariate control. This transformed the hypothesis from correlational to mechanistic.
- **Exchange 11 (Dr. Ally)**: Derived the mechanism directly from PPO/DPO loss function forms — elevated from empirical observation to mechanistically grounded prediction.

---

## Final Hypothesis

### Title
Geometric Fingerprints of Alignment: Pre-Alignment Confidence Margin Predicts Alignment-Induced Argmax Instability with Method-Specific Signatures

### Hypothesis ID
H-MarginFlip-v1

### Core Claim
Under standard RLHF alignment (PPO and DPO) on LLMs of scale 1.4B–7B,
if pre-alignment confidence margin (top-1 minus top-2 log-probability on the base model MCQ items) is low,
then post-alignment argmax inversion probability is higher,
because DPO's log-odds optimization objective amplifies existing option-probability differences more directly than PPO's KL-penalized gradient, creating method-specific geometric fingerprints in how alignment restructures decision boundaries — detectable from the base model alone, surviving KL divergence control.

### Null Hypothesis (H0)
There is no significant difference in argmax inversion probability between low-margin and high-margin MCQ items after controlling for KL divergence between base and aligned models. The Margin × Method interaction term is zero.

### Mechanism (4-step causal chain)
1. **Base geometry**: Low-margin items represent near-boundary decisions; MSP encodes epistemic fragility (Plaut et al. R²=0.94 for correctness prediction)
2. **Structured perturbation**: Alignment injects axis-specific logit perturbations (Li et al. heterogeneous trustworthiness effects confirm non-isotropic structure)
3. **Method differentiation**: DPO amplifies log-odds differences directly; PPO's KL term globally constrains drift → DPO produces higher-variance perturbations near margin=0
4. **Inversion threshold**: Flip occurs when perturbation exceeds pre-margin; DPO reaches threshold more easily at low margin

---

## Predictions

### P1 (Primary): Margin Monotonically Predicts Flip Probability
- **Statement**: β₁ < 0 in logistic regression, p < 0.005 (Bonferroni), partial η² >= 0.06; cross-benchmark AUROC >= 0.75
- **Falsification**: β₁ >= 0 OR AUROC < 0.65 OR non-monotonic P(flip|margin quintile) curve

### P2: Method-Specific Interaction Survives KL Control
- **Statement**: Margin × Method interaction (β₃) in predicted direction after KL covariate included; odds ratio for 1-SD margin decrease >= 1.8 for DPO
- **Falsification**: β₃ = 0 after KL control OR DPO not steeper than PPO at low margin

### P3: Geometric Confirmation via Cosine Projection
- **Statement**: DPO logit deltas show higher cosine alignment with base decision axis (top1-top2 direction) at low-margin quintile than PPO
- **Falsification**: No significant difference in cosine alignment between PPO and DPO conditional on KL

---

## Novelty

### What's New
First empirical study connecting pre-alignment base model confidence geometry to post-alignment argmax stability, with mechanistically grounded method-specific predictions derived from PPO vs DPO objective functions.

### Extension from Prior Work
| Paper | What they studied | This work adds |
|-------|-------------------|----------------|
| Fan et al. [2026] | pretraining→SFT accuracy ranking transfer | pretraining→RLHF with PPO/DPO geometric signatures |
| Plaut et al. [2024] | MSP predicts model correctness | Margin predicts alignment-induced CHANGE in correctness |
| Li et al. [2024] | WHAT changes post-RLHF (trustworthiness dims) | WHICH ITEMS will change (pre-deployment prediction) |
| h-m3 | H2 exists (argmax redistribution confirmed) | WHEN/WHERE H2 is most severe (predictive framework) |

---

## Experimental Design

### Models
- Pythia-1.4B/6.9B base + TRL-aligned PPO/DPO variants (EleutherAI, HuggingFace Hub)
- Tulu-2-base + tulu-2-dpo-7b + tulu-2-ppo-7b (AllenAI) — matched PPO/DPO pair

### Datasets
- **Primary**: MMLU (57 categories, ~14K items, cais/mmlu)
- **Validation**: TruthfulQA (alignment-sensitive), ARC-Challenge (factual MCQ)

### Tools
- lm-evaluation-harness (log-prob extraction for 4-option MCQ)
- scipy.stats (logistic regression, AUROC, correlation)
- statsmodels (mixed-effects logistic regression)

### Key Statistical Tests
1. Mixed-effects logistic regression with KL covariate and Margin × Method interaction
2. Cross-benchmark AUROC (train on MMLU, eval on TruthfulQA/ARC)
3. Cosine projection test with bootstrap CIs
4. Segmented regression for capability threshold test (secondary)

---

## Limitations

1. **PPO hyperparameter sensitivity**: Results conditioned on specific batch size and advantage normalization settings used in available checkpoints
2. **Small model-pair N**: Cosine projection test has limited power at N=3-4 pairs per method — bootstrap CIs required
3. **Capability threshold claim**: Requires segmented regression to distinguish threshold from smooth scaling
4. **Scope**: Limited to 1.4B–7B scale; may not generalize to >70B models or RLHF methods beyond PPO/DPO

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | 16 exchanges, all 6 criteria met |
| **Clarity Verified** | Yes |
| **Hypothesis ID** | H-MarginFlip-v1 |
| **Phase 2B Ready** | Yes |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
*Pipeline: TEST_buildingtrust | Research Folder: 20260317_buildingtrust*
