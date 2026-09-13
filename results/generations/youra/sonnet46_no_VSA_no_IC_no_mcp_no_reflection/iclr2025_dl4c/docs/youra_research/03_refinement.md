# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-31T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Independent Controller Ablation)
- **Gap ID**: gap-1
- **Gap Title**: No Systematic Ablation of Reward Signal Granularity in RLEF for Code LLMs
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 6

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 6 (all 6 personas participated exactly once; Dr. Ally and Prof. Rex provided Final Assessments)

**Convergence Reason**: All 6 convergence criteria met after 6 exchanges — SPECIFIC claim, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS with mitigations

### Key Insights
- Training-evaluation reward alignment is the central mechanistic principle — not just reward density
- GRPO's group normalization may partially solve binary reward sparsity, making the mechanism claim more nuanced than "ratio = denser = better"
- APPS's native multi-test-case structure enables ratio reward computation without any dataset modification
- LiveCodeBench's contamination resistance makes it the ideal OOD discriminator for reward hacking detection

### Breakthrough Moments
- Prof. Vera's separation of "signal density mechanism" from "policy target shift mechanism" — these produce separable predictions that can be independently falsified
- Dr. Ally's synthesis of "training-evaluation alignment" as the unifying principle — elevates the contribution from empirical comparison to mechanistic claim
- Prof. Rex's GRPO group normalization objection — sharpens the mechanism claim and adds gradient norm monitoring as a critical diagnostic

---

## Final Hypothesis

### Title
Reward Granularity vs. Generalization in RLEF for Code LLMs: The Training-Evaluation Alignment Hypothesis

### Hypothesis ID
H-RewardGranularity-v1

### Core Claim
Under RLEF post-training with GRPO on APPS training data for 7B-class code LLMs, if reward signal granularity is increased from binary (0/1) to ratio (k/n passing tests) to output-similarity (continuous token overlap), then in-distribution performance (HumanEval, MBPP) increases with granularity while out-of-distribution generalization (LiveCodeBench) shows a non-monotonic pattern and SWE-bench-lite transfer favors binary reward over ratio/similarity, **because training-evaluation reward alignment — not just reward density — determines cross-benchmark generalization**.

### Mechanism
Three-step causal chain:
1. **Gradient density**: Ratio reward provides non-zero signal for partially-correct solutions in GRPO, enabling better differentiation within all-failing completion groups (binary collapses this to 0 gradient)
2. **Policy target shift**: Binary reward optimizes P(all-pass); ratio optimizes E[coverage]. Models trained with ratio learn partial-solution strategies that may not achieve full binary pass
3. **Alignment penalty**: Ratio-trained models, with partial-solution strategies, underperform on binary-evaluated benchmarks (LiveCodeBench, SWE-bench-lite) — training-evaluation mismatch

---

## Predictions

| ID | Statement | Success Criterion | Primary |
|----|-----------|-------------------|---------|
| P1 | Ratio reward achieves ≥3pp higher HumanEval pass@1 than binary reward | pass@1(ratio) - pass@1(binary) ≥ 0.03 (95% bootstrap CI > 0) | Yes |
| P2 | HumanEval-LiveCodeBench gain gap is larger for ratio-trained models | (HumanEval_gain - LCB_gain)_ratio > same for binary | No |
| P3 | Binary reward transfers equal or better to SWE-bench-lite than ratio/similarity | resolve_rate(binary) ≥ resolve_rate(ratio) at pass@3 | No |

---

## Novelty

**What's new**: First controlled ablation of reward signal granularity in RLEF for code LLMs. All prior work (CodeRL, PPOCoder, RLEF/Gehring, DAPO) uses binary reward exclusively — reward formulation within RLEF has never been systematically varied.

**How it differs**:
- Prior RLEF work: compares RLEF vs. SFT (training paradigm comparison, not reward comparison)
- This work: compares reward variants within RLEF (binary vs. ratio vs. similarity) + proposes training-evaluation alignment as the explanatory mechanism
- Novel design principle: reward format should match downstream evaluation metric, generalizable beyond code RLEF

---

## Experimental Design

**Model**: DeepSeek-Coder-6.7B-instruct (primary); StarCoder2-7B (secondary)

**Training**: GRPO on APPS dataset, 1000 steps, 3 reward conditions (binary / ratio / similarity)
- APPS pre-screening: problems with ≥5 non-redundant test cases only
- Ratio reward capped at 10 test cases per problem (stability)
- Similarity reward: mean token-level F1 per test case, averaged over all test cases

**Evaluation**:
- HumanEval (164 problems): pass@1, checkpoint every 200 steps
- MBPP (374 problems): pass@1, final evaluation
- LiveCodeBench (post-2023 problems): relative improvement = RLEF gain over SFT baseline
- SWE-bench-lite (300 issues): pass@3, Docker-isolated, final evaluation only

**Diagnostic**: Gradient norm monitoring per step (to verify mechanism Step 1)

---

## Limitations
- Primary experiment: one model scale (7B) — findings may not directly generalize to 1B or 70B
- APPS test case quality variable — pre-screening required; reduces usable training problems
- SWE-bench-lite: n=300 limits statistical power; pass@3 and bootstrap CIs partially mitigate
- All Phase 1 paper references are [INFERRED] — arXiv IDs should be verified before experiment design finalization

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met after 6 exchanges |
| **Clarity Verified** | Yes |
| **Remaining Objections** | 2 (with mitigations: gradient monitoring, APPS pre-screening) |
| **Phase 2B Ready** | Yes |

---

*Phase: 2A — Research Dialogue*  
*Next: Phase 2B — Experiment Planning*  
*Architecture: Self-Contained Tikitaka Loop (Independent Controller Ablation — no_IC session variant)*
