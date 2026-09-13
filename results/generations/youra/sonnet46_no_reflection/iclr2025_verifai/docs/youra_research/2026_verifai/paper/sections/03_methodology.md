# 3. Methodology

Our experimental design is built around one question: does the *semantic content* of formal feedback drive LLM improvement, or is it merely the *structure* of contrastive DPO supervision? We call these the oracle and regularizer hypotheses respectively, and we design a 3-condition experiment whose results can discriminate between them.

## 3.1 The Oracle/Regularizer Distinction

**Rationale for the distinction.** When a Lean4 compiler rejects a tactic at proof state *s* with the message "type mismatch: expected `Nat`, got `Int`", this message carries semantic content: the violated type constraint, the location of the error, and an implicit pointer toward premise-consistent alternatives. Under the oracle hypothesis, a DPO model trained on this rejection concentrates probability mass on tactics that address type consistency — the feedback *directs* the policy. Under the regularizer hypothesis, the DPO update diffusely sharpens the policy regardless of the error message content — the feedback merely *constrains* the policy away from the rejected tactic.

**Why this matters.** If the oracle hypothesis holds, feedback quality (semantic specificity) is the critical design dimension. If the regularizer hypothesis holds, feedback diversity (number and variety of negative examples) is more important. These lead to opposite design conclusions for future systems.

**Why prior work cannot discriminate.** Every existing system uses a single feedback condition. BFS-Prover uses only Lean4 compiler errors; ablating against semantically ungrounded same-state negatives would require a separate experimental run that has never been performed. We design and execute this comparison.

## 3.2 Three-Condition DPO Design

We build on the BFS-Prover framework [Xin et al., 2025], using Qwen2.5-Math-7B initialized from the BFS-Prover cold-start SFT checkpoint. All three conditions share:
- The same base model (frozen π_ref)
- The same proof states (hard subset: cold-start SFT pass@1 < 20%)
- The same chosen tactics (a_w) at each state
- The same DPO hyperparameters (β=10, lr 5e-6→5e-7, 1-epoch)

The conditions differ only in the rejected tactic (a_l):

| Condition | Name | a_l content | Semantic grounding |
|-----------|------|-------------|-------------------|
| **A** | Step-local Grounded | Lean4 compiler-error-triggering tactic at state *s* | Full: error type, location, violated constraint |
| **B** | Step-local Ungrounded | Failed-branch tactic at same state *s* (no error message) | None: failed tactic identity only |
| **P** | Permuted Control | Tactic paired with shuffled/permuted compiler error message | Scrambled: structure preserved, semantics destroyed |

This design allows clean attribution: A vs. P isolates the contribution of *coherent semantic content* (both have compiler error messages, only A has consistent ones); A vs. B isolates the contribution of *semantic grounding itself* (both are step-local, only A is grounded).

**State alignment.** A critical implementation requirement: for all three conditions, the chosen tactic a_w and rejected tactic a_l must come from the *same* proof state *s* (100% state alignment). Misalignment would confound the 2×2 factorial, turning conditions B and P into episode-level signals. We verify state alignment via LeanDojo state IDs and abort if any pair violates the invariant.

## 3.3 The Locality Score Metric

We introduce the **locality score (LS)** as a mechanistic probe for oracle function:

$$\text{LS} = \frac{\sum_s \left[ P_{\text{post}}(\text{premise-consistent} \mid s) - P_{\text{pre}}(\text{premise-consistent} \mid s) \right]}{\sum_s \sum_t \left| P_{\text{post}}(t \mid s) - P_{\text{pre}}(t \mid s) \right|}$$

where:
- *P_pre* is the frozen reference policy (BFS-Prover SFT checkpoint)
- *P_post* is the DPO-trained policy for this condition
- **premise-consistent** denotes tactics in the tactic category that addresses the specific violated constraint at state *s*, as determined by the pre-specified tactic taxonomy

The locality score measures what fraction of the post-DPO probability mass *shift* concentrates on tactics that address the specific error at each failed state. An oracle produces LS >> 0 (focused shift); a regularizer produces LS ≈ 0 (diffuse shift).

**Tactic taxonomy (pre-specified).** To prevent post-hoc circularity, we pre-specify the tactic category taxonomy from LeanDojo error categories before any training:
- **type_error**: `type mismatch`, `application type mismatch`
- **undefined_name**: `unknown identifier`, `unknown tactic`
- **tactic_failure**: `tactic failed`, `simp made no progress`

For each failed proof state, the error category is assigned from this taxonomy before DPO training begins.

**Gate condition.** The oracle hypothesis predicts LS_A > LS_P (grounded condition produces higher locality than permuted control), tested via one-sided t-test at p < 0.05. This is the MUST_WORK gate for hypothesis H-E1.

## 3.4 The α-Interaction Prediction

BFS-Prover's length normalization parameter α controls search depth bias:

$$\text{score}(s_L) = \frac{\sum_t \log p(a_t \mid s_t)}{L^\alpha}$$

At α=0, the scoring function is length-averse (shorter proof paths are preferred regardless of tactic probability). At α=1, the scoring is length-neutral. Under the oracle hypothesis, step-local grounded feedback provides greatest benefit at α=0, because local oracle guidance compensates for the search depth bias that would otherwise prevent deep proofs from being explored.

The α-interaction prediction is: Δ(A−D)|_{α=0} > Δ(A−D)|_{α=0.5} > Δ(A−D)|_{α=1.0}

This prediction is uniquely attributable to the oracle mechanism: a regularizer would produce uniform gains across α settings (since it does not interact with search geometry). We sweep α ∈ {0.0, 0.5, 1.0} as part of hypotheses H-M3 and H-M4, providing a discriminating test beyond the locality score.

## 3.5 Hypothesis Chain

The full verification plan decomposes the oracle hypothesis into a 6-hypothesis chain:

- **H-E1 (Existence, MUST_WORK):** LS_A > LS_P — oracle signal exists at the probability mass level
- **H-M1 (Mechanism, MUST_WORK):** State alignment = 100% — pair construction creates valid state-aligned supervision
- **H-M2 (Mechanism, SHOULD_WORK):** LS_A > LS_D, Cohen's d > 0.2 — oracle mass shift is specific, not diffuse
- **H-M3 (Mechanism, SHOULD_WORK):** Δ(A−D) ≥ 10pp, non-overlapping 95% CIs — mass shift translates to task performance
- **H-M4 (Mechanism, SHOULD_WORK):** Monotonic α-interaction, Cohen's d ≥ 0.3 — oracle compensates for search geometry
- **H-C1 (Condition, SHOULD_WORK):** Fidelity-stratified Δ(A−D): Q4 > Q1 — oracle requires ≥85% formalization fidelity

Phase 4 execution targets H-E1 (the foundation gate). H-M1 through H-C1 are staged for subsequent runs contingent on H-E1 passing.

## 3.6 Formalization Fidelity Requirement

The semantic grounding manipulation in Condition A is valid only if the LeanDojo-extracted proof state triples (state, tactic, compiler_error) faithfully represent the natural-language reasoning intent (Assumption A1). We operationalize this as a formalization fidelity audit: a 200-step random sample scored by two independent annotators, with Cohen's κ ≥ 0.7 required and overall fidelity ≥ 85% required before any training begins. The high-fidelity quartile (Q4: ≥90%) serves as the primary analysis domain; results are reported separately for Q1 (<70%) as a scope boundary test.
