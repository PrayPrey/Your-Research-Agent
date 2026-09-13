# 4. Experimental Setup

## 4.1 Research Questions

We design experiments to answer the following questions:

**RQ1:** Does step-local grounded DPO feedback (Condition A: Lean4 compiler errors) produce higher locality scores than permuted control (Condition P), confirming the oracle mechanism exists at the probability mass level? [Tests H-E1]

**RQ2:** Is the DPO pair construction protocol achieving 100% state alignment — ensuring conditions differ only in a_l content, not state distribution? [Tests H-M1]

**RQ3:** Does the oracle locality effect translate to greater hard-stratum pass@1 recovery for Condition A vs. Condition D, and does this advantage vary monotonically with α? [Tests H-M3, H-M4]

## 4.2 Datasets

We evaluate on two formal reasoning benchmarks, using only their **hard subsets** — problems where the cold-start SFT baseline achieves pass@1 < 20% across 16 rollouts.

**miniF2F Hard Subset**
- Source: Zheng et al. [2021]; HuggingFace: `Tonic/MiniF2F`
- Full benchmark: 488 problems (AMC/AIME/IMO + high-school/undergraduate mathematics) in Lean4 format
- Format: `{name, split, formal_statement, goal, header}` in Lean4 syntax
- Hard subset definition: Problems where BFS-Prover cold-start SFT achieves pass@1 < 20% across 16 rollouts
- *Why chosen*: miniF2F is the established benchmark for BFS-Prover (72.95%) — using it enables direct comparison with the system our design extends. The hard subset focuses evaluation where oracle guidance is most needed.

**Vericoding Hard Subset**
- Source: Bursuc et al. [2025]; arXiv:2509.22908
- Full benchmark: 12,504 formally verified code specifications across Lean/Verus/Dafny formalisms
- Filter: Lean4-compatible problems only (for LeanDojo compatibility)
- Hard subset definition: Same cold-start SFT protocol as miniF2F
- *Why chosen*: Vericoding tests cross-domain generalization — formally verified code synthesis rather than theorem proving. If the oracle mechanism is real, it should not be benchmark-specific.

| Dataset | Full Size | Format | Hard Subset (expected) |
|---------|-----------|--------|----------------------|
| miniF2F | 488 problems | Lean4 theorem proving | ~100–150 problems |
| Vericoding (Lean4 subset) | ~3,000 problems | Lean4 code verification | ~300–600 problems |

## 4.3 Baselines

The three DPO conditions serve as mutual baselines:

**Condition A — Step-Local Grounded (Proposed)**
- Rejected tactic a_l: Lean4 compiler-error-triggering tactic at proof state s
- Grounding: Full compiler error message (error type, location, violated constraint)
- *Why included*: Primary condition — tests the oracle hypothesis

**Condition B — Step-Local Ungrounded (Ablation)**
- Rejected tactic a_l: Failed-branch tactic at same proof state s, no compiler error information
- Grounding: None — tactic identity only
- *Why included*: Isolates the contribution of step-locality vs. semantic grounding; B vs. A tests grounding effect at fixed granularity

**Condition P — Permuted Control (Oracle Test)**
- Rejected tactic a_l: Tactic paired with shuffled/permuted compiler error message
- Grounding: Scrambled — error structure preserved, semantic content destroyed
- *Why included*: The key oracle/regularizer discriminator; P preserves DPO structure while destroying semantic content

All conditions use the same proof states, chosen tactics, and hyperparameters. This design ensures any locality score difference between A and P is attributable to semantic content alone.

## 4.4 Model

**Base model:** Qwen2.5-Math-7B with BFS-Prover cold-start SFT initialization
- HuggingFace: `ByteDance-Seed/BFS-Prover-V2-7B`
- Architecture: Decoder-only transformer, 7B parameters, bfloat16
- Role: (1) Frozen reference model π_ref for DPO; (2) Starting point for each condition's DPO fine-tune

*Why this model:* Qwen2.5-Math-7B is the exact model used in BFS-Prover, enabling direct comparison. The cold-start SFT checkpoint provides the hard subset definition via 16-rollout evaluation.

## 4.5 Implementation Details

**DPO Training Configuration:**

| Hyperparameter | Value | Source |
|----------------|-------|--------|
| DPO β | 10.0 | BFS-Prover [Xin et al., 2025] |
| Learning rate | 5e-6 → 5e-7 (linear decay) | BFS-Prover |
| Batch size | 16 | BFS-Prover |
| Epochs | 1 | Standard DPO practice |
| Optimizer | AdamW (wd=0.01, β=(0.9, 0.999)) | eric-mitchell/DPO |
| Mixed precision | bfloat16 | BFS-Prover |
| Seeds | 1 (PoC stage) | — |

**Loss function** (following eric-mitchell/direct-preference-optimization [Mitchell et al., 2023]):
```
L_DPO = -log σ(β · (log π_θ(a_w|s)/π_ref(a_w|s) - log π_θ(a_l|s)/π_ref(a_l|s)))
```
with `average_log_prob=False` (sum log-probabilities, not average, for variable-length tactic sequences).

**Infrastructure:** Single NVIDIA H100 GPU (80GB), CUDA 12.0+, Python 3.10+, `lean-dojo>=2.0.0`, `transformers>=4.40.0`.

**Pair construction:** LeanDojo `Dojo` context manager extracts (state, tactic, compiler_error) triples. State alignment verified via LeanDojo state IDs: pipeline aborts if any pair has s_w ≠ s_l.

## 4.6 Evaluation Metrics

**Primary metric (MUST_WORK gate for H-E1):**
- **Locality Score (LS):** Fraction of post-DPO probability mass shift concentrated on premise-consistent tactic categories, computed over all hard-subset failed proof states.
- Gate: LS_A > LS_P (one-sided t-test, p < 0.05)

**Secondary metrics:**
- LS_A > LS_B (grounded vs. ungrounded step-local comparison)
- Hard-stratum pass@1 at α ∈ {0.0, 0.5, 1.0} for Conditions A and D (H-M3, H-M4; future work)

**Statistical testing:** One-sided t-test via `scipy.stats.ttest_1samp(LS_A - LS_P, 0, alternative='greater')`. Significance threshold: p < 0.05.

**Compute budget:** ~2–4 hours per DPO condition on H100; ~6–12 hours total for 3 conditions.
