---
hypothesis_title: "Formal Feedback as Local Logical Oracle: Mechanistic Study of Step-Local vs. Episode-Level Signals in LLM Formal Reasoning"
date: "2026-05-20"
hypothesis_id: "H-FormalFeedbackOracle-v1"
confidence_level: 0.78
total_hypothesis_count: 6
stepsCompleted: ["step-00-init-environment", "step-01-init-parsing", "step-02-input-hypothesis", "step-03-hypothesis-generation", "step-04-hypothesis-inventory", "step-05-risk-analysis", "step-06-dependency-graph", "step-07-timeline-planning", "step-08-dialectical-analysis", "step-09-summary", "step-10-finalize"]
status: complete
completedAt: "2026-05-20T07:45:00"
---

# Verification Plan: Formal Feedback as Local Logical Oracle

**Date:** 2026-05-20
**Hypothesis ID:** H-FormalFeedbackOracle-v1
**Confidence:** 0.78
**Total Hypotheses:** 6

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under fixed search geometry (BFS with length normalization α, fixed expansion width and tactic budget) and high formalization fidelity (≥85% audit threshold), if LLM policy training uses semantically grounded step-local formal feedback signals (Lean4 compiler errors or Z3 SMT counterexamples via DSL bridge) as DPO negative examples, then correctness recovery on hard benchmark instances (cold-start SFT baseline pass rate <20%) will be significantly greater (≥10pp, non-overlapping 95% CIs) compared to episode-level or semantically ungrounded feedback, because step-local grounded signals function as "local logical oracles" — providing state-specific semantic information that directs the policy toward formally valid continuations — rather than as "policy regularizers" that sharpen any policy regardless of semantic content.

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in hard-stratum pass@1 between semantically grounded step-local feedback and episode-level or ungrounded feedback conditions under fixed search geometry and DPO training (i.e., all feedback conditions produce equivalent correctness recovery on hard instances).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | miniF2F + Vericoding (hard subsets) (standard) | miniF2F provides the theorem proving domain where BFS-Prover was validated (72.95%); Vericoding provides 12,504 formally verified code specs across Lean/Verus/Dafny for cross-formalism testing. Both have large hard subsets (cold-start SFT <20%) without requiring new benchmark creation. |
| **Model** | Qwen2.5-Math-7B (cold-start SFT initialized) | Exactly the model used in BFS-Prover, allowing direct comparison and reuse of BFS infrastructure. 7B scale is tractable on A100 GPUs. |

**Dataset Details:**
- Source: miniF2F: Zheng et al. 2021; Vericoding: Bursuc et al. 2025 (arXiv 2509.22908)
- Path: Standard benchmark — available via LeanDojo for miniF2F; Vericoding from arXiv

**Model Details:**
- Type: Causal LLM fine-tuned for mathematical reasoning
- Source: Open-source; BFS-Prover cold-start SFT checkpoint available

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| BFS-Prover (step-local Lean4 compiler feedback + DPO) | 72.95% | miniF2F |
| PropertyGPT (static analysis feedback, inference-time loop) | 80% recall | Certora audited projects |
| Proof of Thought (Z3 SMT via JSON DSL) | 81.55% win rate | StrategyQA, Reddit-OSHA |
| STP self-play [Dong & Ma 2025] | 65% | miniF2F |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Formalization fidelity ≥85%: T_i ⊢ Q_i extractions faithfully represent natural-language intent | MATH-VF >90% SimpleMath coverage; LeanDojo returns structured compiler states | Semantic grounding confounded with artifacts; restrict claims to high-fidelity quartile |
| A2 | State-aligned pair construction for episode-level conditions: a_l drawn from same proof state as a_w | LeanDojo gym returns all tactic candidates at each state | Episode-level conditions test misaligned negatives; 2×2 design confounded |
| A3 | Hard subset well-populated: sufficient hard problems exist for statistical power | Vericoding 12,504 specs; miniF2F ~27% overall baseline (many hard problems) | Insufficient power; widen threshold to <30% or pool benchmarks |
| A4 | Tactic taxonomy for locality scoring pre-specified from LeanDojo error categories before experiments | LeanDojo provides structured error categories (type errors, undefined names, tactic failures) | Post-hoc taxonomy introduces circularity; fall back to binary locality measure |
| A5 | BFS α acts as proxy for search depth bias; oracle advantage largest at α=0 | BFS-Prover ablations show α sensitivity; α=0 produces shortest-path bias | α-interaction absent; oracle/regularizer distinction may still hold via locality prediction |

### 1.6 Research Gap & Novelty

**Gap:** No prior comparative study of formal feedback signal types exists on the same LLM and benchmark. Each paper (BFS-Prover, PropertyGPT, Proof of Thought) uses exactly one feedback type; cross-signal comparison is the identified research gap.

**Novelty:** The "local logical oracle vs. policy regularizer" framing is genuinely novel — no prior work has explicitly distinguished these two causal mechanisms for formal feedback in LLM systems. The 2×2 factorial (granularity × semantic groundedness) is a new experimental design. The α-interaction prediction turns the BFS search geometry parameter into a mechanistic probe. This work unifies PropertyGPT, Proof of Thought, and BFS-Prover under a single testable causal mechanism.

**Scope Reduction:** 50% — three BUILD_ON facts treated as established baselines; only PROVE_NEW claims generate hypotheses.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | NOT_STARTED |
| H-M4 | MECHANISM | SHOULD_WORK | H-M3 | NOT_STARTED |
| H-C1 | CONDITION | SHOULD_WORK | H-M4 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Oracle Signal Existence — Locality Score Superiority**

**Type:** EXISTENCE
**Statement:** Under fixed BFS geometry and ≥85% formalization fidelity, if LLM policy uses step-local grounded feedback (condition A: Lean4 compiler errors) as DPO negatives, then post-DPO locality score (fraction of probability mass on premise-consistent tactics) will be significantly higher than the permutation control (shuffled error messages) and condition B (ungrounded step-local), because semantic content of the formal feedback directly encodes the violated constraint.

**Rationale:** Before testing hard-stratum recovery (performance outcome), we must verify that the oracle mechanism produces a measurable signal-level effect. If locality score does not differ from shuffled control, the oracle mechanism is absent and subsequent mechanism hypotheses are moot.

**Variables:**
- IV: Feedback Signal Type — Condition A (Lean4 compiler errors) vs. Condition B (failed-branch tactics) vs. permutation control
- DV: Locality Score — fraction of post-DPO probability mass increase on premise-consistent tactics per LeanDojo taxonomy
- CV: Base LLM (Qwen2.5-Math-7B), BFS geometry, DPO hyperparams, hard subset definition

**Verification Protocol:**
1. Run cold-start SFT on Qwen2.5-Math-7B; define frozen hard subset (pass@1 < 20%).
2. Construct DPO pairs: condition A uses Lean4 compiler error a_l; condition B uses same-state failed-branch tactic a_l; permutation control shuffles error messages.
3. Train 1-epoch DPO (β=10) for each condition; evaluate on full miniF2F and Vericoding hard subsets.
4. Compute locality score: post-DPO mass shift toward LeanDojo-taxonomy premise-consistent tactic category at each failed state.
5. Statistical test: one-sided t-test locality(A) > locality(permutation), p < 0.05, across 3 seeds.

**Success Criteria:**
- Primary: Locality score condition A > permutation control (p < 0.05)
- Secondary: Locality score condition A > condition B

**Gate:**
- Type: MUST_WORK
- If Fail: Oracle mechanism absent → H-M hypotheses re-evaluated; may PIVOT to regularizer framing

**Dependencies:** None (foundation)

**Source:** Phase 2A Section 5 (sh1_existence), Prediction P3

---
**H-M1: Step-Local Grounded Encoding Creates State-Aligned Contrastive Supervision**

**Type:** MECHANISM (Causal Step 1→2)
**Statement:** Under fixed BFS geometry, if step-local grounded rejection from the formal verifier (Lean4 compiler error at state s with violated constraint) is encoded as DPO negative a_l at the same proof state s, then this creates state-aligned contrastive supervision pairing the violated constraint with the specific policy decision that caused it, because the LeanDojo gym interface returns error-tagged tactic candidates at each proof state.

**Rationale:** This hypothesis verifies that the DPO pair construction protocol successfully creates state-aligned pairs — the prerequisite for the oracle function. If pair construction fails state alignment, the mechanism collapses to episode-level signal regardless of feedback type.

**Variables:**
- IV: Pair construction protocol (state-aligned grounded vs. misaligned episode-level)
- DV: State alignment rate — fraction of DPO pairs where a_w and a_l are from identical proof state s
- CV: LeanDojo interface, BFS search tree structure

**Verification Protocol:**
1. Run BFS rollouts on miniF2F training set using LeanDojo gym interface.
2. Construct DPO pairs for condition A: extract Lean4 compiler error a_l at same state s as winning tactic a_w.
3. Verify state alignment: confirm (s_w == s_l) for 100% of pairs via LeanDojo state IDs.
4. Pre-specify episode-level pair construction for condition C: sample failed same-state tactic as proxy for Z3 episode signal.
5. Confirm pair construction pre-specification documented before any training runs.

**Success Criteria:**
- Primary: State alignment rate = 100% for condition A pairs
- Secondary: Pre-specification of condition C pair construction protocol documented before experiments

**Gate:**
- Type: MUST_WORK
- If Fail: State alignment broken → DPO encoding equivalent to episode-level; fundamental design flaw

**Dependencies:** H-E1

**Source:** Phase 2A Section 1.3 Causal Step 2, Assumption A2

---
**H-M2: DPO Training With Grounded Negatives Produces Oracle Mass Shift (Not Diffuse Regularizer)**

**Type:** MECHANISM (Causal Step 3)
**Statement:** Under fixed BFS geometry and DPO training with state-aligned grounded negatives (condition A), the post-DPO probability mass increase at each failed state concentrates specifically on tactics consistent with violated premises (oracle function), rather than diffusing across all tactics (regularizer function), because state-aligned contrastive supervision provides tighter gradient signal than episode-level failure.

**Rationale:** This is the core mechanistic test distinguishing oracle from regularizer. The locality score from H-E1 establishes existence; H-M2 establishes the directionality and specificity of the mass shift mechanism under DPO training conditions.

**Variables:**
- IV: DPO training condition (A: grounded vs. D: ungrounded)
- DV: Repair Information Density (RID) — KL(p_{θ+}(·|s) ‖ p_θ(·|s)); Locality Score distribution
- CV: BFS geometry, DPO hyperparams, same proof states across conditions

**Verification Protocol:**
1. After DPO training for conditions A and D, compute RID (KL divergence) at each failed state in hard subset.
2. Compute locality score for each condition: fraction of KL mass on LeanDojo premise-consistent category.
3. Compare locality score distribution: condition A vs. condition D vs. permutation control.
4. Report Cohen's d for locality(A) − locality(D).
5. Evaluate on both miniF2F and Vericoding hard subsets (all hard-stratum problems).

**Success Criteria:**
- Primary: Locality score condition A > condition D (p < 0.05, Cohen's d > 0.2)
- Secondary: RID condition A > RID condition D (mass shift larger and more focused)

**Gate:**
- Type: SHOULD_WORK
- If Fail: Document as boundary condition; oracle may operate at inference time (Experiment A) even if DPO mechanism is regularizer

**Dependencies:** H-M1

**Source:** Phase 2A Section 1.3 Causal Step 3, Prediction P3

---
**H-M3: Oracle Mass Shift Produces Hard-Stratum Pass@1 Recovery**

**Type:** MECHANISM (Causal Step 3 → outcome)
**Statement:** Under fixed BFS geometry and DPO training, the oracle mass shift (from H-M2) translates into significantly greater hard-stratum pass@1 recovery for condition A (step-local grounded) compared to condition D (episode-level ungrounded), with ≥10pp difference and non-overlapping 95% CIs, because improved local guidance at each failed proof state increases the probability of finding valid continuations.

**Rationale:** H-M2 tests the mechanistic signal; H-M3 tests that the signal translates to task performance on the primary benchmark outcome. This is the central performance prediction (P1) and the primary quantitative success criterion for the verification plan.

**Variables:**
- IV: Feedback condition (A vs. B vs. C vs. D) × DPO training (on/off)
- DV: Hard-stratum pass@1 on miniF2F and Vericoding (full hard subsets, cold-start SFT < 20%)
- CV: α fixed per sub-experiment, base LLM, BFS infrastructure

**Verification Protocol:**
1. Evaluate all 4 feedback conditions × DPO-on setting on full miniF2F hard subset and full Vericoding hard subset.
2. Compute Δ(A−D) for hard-stratum pass@1 across 3 random seeds.
3. Compute 95% CIs via bootstrap; test non-overlap condition.
4. Run Experiment A (frozen policy, no DPO) as inference-time control.
5. Report results stratified by benchmark (miniF2F / Vericoding) and by formalization fidelity quartile.

**Success Criteria:**
- Primary: Δ(A−D) ≥ 10pp with non-overlapping 95% CIs across 3 seeds, DPO-on
- Secondary: Condition A > condition B > condition D in performance ranking

**Gate:**
- Type: SHOULD_WORK
- If Fail: If Δ < 2pp, core hypothesis rejected; if 2pp ≤ Δ < 10pp, partial support with scope reduction

**Dependencies:** H-M2

**Source:** Phase 2A Section 1.3 Causal Step 3, Prediction P1

---
**H-M4: α-Interaction — Oracle Advantage Maximized Under Length-Averse BFS (α=0)**

**Type:** MECHANISM (Causal Step 4)
**Statement:** Under DPO training with step-local grounded feedback (condition A), the hard-stratum pass@1 advantage over episode-level ungrounded (condition D) is maximized at α=0.0 (length-averse BFS) and decreases monotonically as α→1.0 (length-neutral BFS), because local oracle guidance provides greatest benefit when search is most biased against deep proofs.

**Rationale:** This is the most discriminating mechanistic test — only the oracle mechanism predicts α-dependent advantage. A regularizer would produce uniform gains across α settings. The α-interaction prediction uniquely distinguishes the oracle hypothesis from all alternative explanations.

**Variables:**
- IV: Length normalization α ∈ {0.0, 0.5, 1.0} × Feedback condition (A vs. D)
- DV: Δ(A−D) hard-stratum pass@1 at each α level
- CV: DPO hyperparams, base LLM, hard subset definition, BFS expansion width

**Verification Protocol:**
1. Train DPO models for conditions A and D at each α ∈ {0.0, 0.5, 1.0} (6 DPO training runs × 3 seeds = 18 runs).
2. Evaluate hard-stratum pass@1 for each α × condition combination on full miniF2F and Vericoding hard subsets.
3. Compute Δ(A−D) at each α level; test monotonicity: Δ|α=0 > Δ|α=0.5 > Δ|α=1.0.
4. Compute Cohen's d for the α × feedback interaction effect.
5. Pre-registered failure threshold: Cohen's d < 0.3 = no interaction support.

**Success Criteria:**
- Primary: Monotonic α-interaction — Δ(A−D)|α=0 > Δ(A−D)|α=0.5 > Δ(A−D)|α=1.0
- Secondary: Cohen's d ≥ 0.3 for the interaction effect

**Gate:**
- Type: SHOULD_WORK
- If Fail: Oracle mechanism not compensating for search bias; report as boundary condition; H-M2/H-M3 may still support oracle at fixed α

**Dependencies:** H-M3

**Source:** Phase 2A Section 1.3 Causal Step 4, Prediction P2

---
**H-C1: Formalization Fidelity Threshold — Oracle Mechanism Requires ≥85% Fidelity**

**Type:** CONDITION
**Statement:** The oracle advantage of step-local grounded feedback (condition A over D) is contingent on formalization fidelity ≥85%: within the high-fidelity quartile (Q4: ≥90%), the oracle advantage holds as predicted; within the low-fidelity quartile (Q1: <70%), the advantage disappears or is significantly reduced, because low fidelity confounds semantic grounding with formalization artifacts.

**Rationale:** The 85% fidelity threshold is a key boundary condition determining scope of claims. Verifying fidelity-stratified results converts a potential confound into a feature and enables precise scope statements: "our results hold for high-fidelity formal verification settings."

**Variables:**
- IV: Formalization fidelity quartile (Q1: <70%, Q2: 70-79%, Q3: 80-89%, Q4: ≥90%)
- DV: Δ(A−D) hard-stratum pass@1 within each fidelity quartile
- CV: α=0.0 (maximum oracle condition), DPO-on, base LLM

**Verification Protocol:**
1. Run formalization fidelity audit: 200-step random sample per benchmark, two annotators, Cohen's κ ≥ 0.7.
2. Stratify all hard-subset problems into fidelity quartiles based on audit results.
3. Compute Δ(A−D) separately within each quartile for DPO-on, α=0.0 condition.
4. Test whether Δ(A−D) in Q4 significantly exceeds Δ(A−D) in Q1 (one-sided t-test, p < 0.05).
5. Report scope restriction: if overall fidelity < 85%, restrict main claims to Q3+Q4 only.

**Success Criteria:**
- Primary: Δ(A−D) in Q4 significantly greater than in Q1 (p < 0.05)
- Secondary: Monotonic fidelity-advantage relationship across Q1→Q4

**Gate:**
- Type: SHOULD_WORK
- If Fail: Fidelity threshold effect absent; oracle mechanism more robust than expected; report as positive finding (wider applicability)

**Dependencies:** H-M4

**Source:** Phase 2A Section 1.5 Scope, Assumption A1

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4 → H-C1
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Locality score A > permutation control (p<0.05) | STOP — reassess entire hypothesis |
| H-M1 | MUST_WORK | State alignment rate = 100%; pair construction pre-specified | STOP — fundamental design flaw |
| H-M2 | SHOULD_WORK | Locality score A > D (p<0.05, Cohen's d >0.2) | Document limitation; continue to H-M3 |
| H-M3 | SHOULD_WORK | Δ(A−D) ≥ 10pp, non-overlapping 95% CIs, DPO-on | If Δ<2pp: reject; if 2-10pp: partial support |
| H-M4 | SHOULD_WORK | Monotonic α-interaction, Cohen's d ≥ 0.3 | Document as boundary condition; continue |
| H-C1 | SHOULD_WORK | Δ(A−D) Q4 > Q1 (p<0.05) | Wider applicability — report as positive finding |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Core Mechanisms | H-M1, H-M2, H-M3, H-M4 | 5 weeks (H-M1: 2wk, H-M2-4: 1wk each) |
| Phase 2.5: Conditions | H-C1 | 1 week |

**Total Duration:** 8 weeks

---

## 4. Risk Analysis

### 4.1 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: Formalization fidelity <85% | A1 | H-E1, H-M2, H-M3, H-C1 | High |
| R2: Episode-level pair construction state misalignment | A2 | H-M1, H-M2, H-M3, H-M4 | Critical |
| R3: Hard subset too small for statistical power | A3 | H-M3, H-M4, H-C1 | High |
| R4: Post-hoc tactic taxonomy construction | A4 | H-E1, H-M2 | High |
| R5: α-interaction absent or non-monotonic | A5 | H-M4 | Medium |
| R6: Compute budget overrun (36 DPO runs × 3 seeds) | Infrastructure | All | Medium |

### 4.2 Mitigation Strategies

**R1: Formalization Fidelity Below Threshold**
- Source: A1 — fidelity ≥85% required for valid semantic grounding manipulation
- Affected: H-E1, H-M2, H-M3, H-C1
- Severity: High | Likelihood: Medium
- Prevention: Run 200-sample fidelity audit BEFORE any training; confirm κ ≥ 0.7 between two annotators
- Detection: Monitor fidelity score per benchmark; flag if overall rate drops below 90%
- Response: SCOPE — restrict analysis to high-fidelity quartile (Q3+Q4); adjust scope claims accordingly
- Early Warning: Pilot fidelity check on 50-sample subset before full audit

**R2: Episode-Level Pair Construction Confound (CRITICAL)**
- Source: A2 — condition C (Z3 SMT) must use same-state aligned pairs
- Affected: H-M1, H-M2, H-M3, H-M4
- Severity: Critical | Likelihood: Medium (without pre-specification)
- Prevention: Pre-specify condition C protocol in writing BEFORE any BFS rollout; use LeanDojo same-state failed-branch tactic as proxy for Z3 episode failure
- Detection: Verify state IDs (s_w == s_l) for 100% of condition C pairs post-construction
- Response: PIVOT — if alignment fails, treat condition C as "misaligned episode-level" and report as separate analysis; 2×2 design degrades to 3-condition comparison
- Early Warning: State alignment check during pair construction pipeline

**R3: Hard Subset Insufficient Size**
- Source: A3 — cold-start SFT may solve too many problems (hard tail too small)
- Affected: H-M3, H-M4, H-C1
- Severity: High | Likelihood: Low (Vericoding large)
- Prevention: Pre-compute hard subset size before training; require ≥200 instances per benchmark
- Detection: Count problems with SFT-only pass@1 < 20% after cold-start SFT run
- Response: SCOPE — widen threshold to <30% OR pool miniF2F + Vericoding hard subsets; adjust success criteria proportionally
- Early Warning: Check Vericoding per-formalism baselines (Lean/Verus/Dafny separately)

**R4: Post-Hoc Tactic Taxonomy Circularity**
- Source: A4 — locality score requires pre-specified taxonomy
- Affected: H-E1, H-M2
- Severity: High | Likelihood: Low (LeanDojo has structured categories)
- Prevention: Document complete tactic taxonomy from LeanDojo error categories before any experiment; pre-register with collaborator or timestamp
- Detection: Verify taxonomy was finalized before first training run (timestamp check)
- Response: PIVOT to coarser binary locality measure (correct tactic class vs. all others) if fine-grained taxonomy insufficient
- Early Warning: Review LeanDojo error category documentation before fidelity audit

**R5: α-Interaction Absent**
- Source: A5 — BFS α as search-depth-bias proxy may not modulate oracle advantage
- Affected: H-M4 only
- Severity: Medium | Likelihood: Medium
- Prevention: Pre-register failure threshold (Cohen's d < 0.3 = null) before data collection
- Detection: Compute Cohen's d for α × feedback interaction effect post-hoc
- Response: EXPLORE — report null α-interaction as boundary condition finding; oracle/regularizer distinction still supported by H-M2/H-M3 locality results; narrows but does not invalidate claims
- Early Warning: Check α sensitivity in pilot BFS rollouts before full DPO training

**R6: Compute Budget Overrun**
- Source: Infrastructure — 36 DPO + 36 inference runs × A100 GPU time
- Affected: All hypotheses (timeline risk)
- Severity: Medium | Likelihood: Medium
- Prevention: Checkpoint every training run; pilot with α=0 only, 2 conditions before full factorial
- Detection: Monitor GPU hours after pilot completion; project total before committing to full sweep
- Response: SCOPE — reduce to 2×2 (drop α=0.5 intermediate) if budget constrained; H-M4 uses α={0.0, 1.0} only

### 4.3 Risk Summary

| ID | Risk | Source | Severity | Affected | Mitigation Summary |
|----|------|--------|----------|----------|--------------------|
| R1 | Fidelity <85% | A1 | High | H-E1, H-M2, H-M3, H-C1 | Pre-audit; scope restriction to Q3+Q4 |
| R2 | Pair construction misalignment | A2 | **Critical** | H-M1–H-M4 | Pre-specify condition C protocol; state ID verification |
| R3 | Hard subset too small | A3 | High | H-M3, H-M4, H-C1 | Pre-compute size; widen threshold fallback |
| R4 | Taxonomy post-hoc | A4 | High | H-E1, H-M2 | Pre-register taxonomy before any experiment |
| R5 | α-interaction absent | A5 | Medium | H-M4 | Pre-register null threshold; report as boundary condition |
| R6 | Compute overrun | Infra | Medium | All | Pilot sweep; checkpointing; α reduction fallback |

Critical Risks: 1 (R2)
High Risks: 3 (R1, R3, R4)
Medium Risks: 2 (R5, R6)
Low Risks: 0

**Pre-Experiment Protocol (mandatory before any DPO training):**
1. Run 200-sample fidelity audit; confirm ≥85% and κ ≥ 0.7
2. Pre-specify and document condition C pair construction protocol in writing
3. Pre-register tactic taxonomy from LeanDojo error categories
4. Pre-compute cold-start SFT hard subset size; confirm ≥200 instances

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)
```
═══════════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 6 Hypotheses
═══════════════════════════════════════════════════════════════

[Level 0 - Root: Foundation]
    H-E1  (EXISTENCE — no prerequisites)
    Gate: MUST_WORK | Failure: STOP entire pipeline
         │
         ▼
[Level 1 - Core Mechanism Entry]
    H-M1  (MECHANISM — state-aligned pair construction)
    ← depends on: H-E1
    Gate: MUST_WORK | Failure: STOP — design flaw
         │
         ▼
[Level 2 - Oracle Mass Shift]
    H-M2  (MECHANISM — oracle vs. regularizer DPO shift)
    ← depends on: H-M1
    Gate: SHOULD_WORK | Failure: document, continue
         │
         ▼
[Level 3 - Performance Outcome]
    H-M3  (MECHANISM — hard-stratum pass@1 recovery ≥10pp)
    ← depends on: H-M2
    Gate: SHOULD_WORK | Failure: Δ<2pp → reject; 2-10pp → partial
         │
         ▼
[Level 4 - Discriminating Mechanistic Test]
    H-M4  (MECHANISM — α-interaction, oracle compensates bias)
    ← depends on: H-M3
    Gate: SHOULD_WORK | Failure: boundary condition, continue
         │
         ▼
[Level 5 - Condition Boundary]
    H-C1  (CONDITION — fidelity threshold ≥85% required)
    ← depends on: H-M4
    Gate: SHOULD_WORK | Failure: wider applicability (positive)
         │
         ▼
    [PHASE 2B COMPLETE → Phase 5 Baseline Comparison]

═══════════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4 → H-C1
All hypotheses sequential (no parallelization)
═══════════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type | Phase |
|-------|-----------|---------------|-----------|-------|
| 0 | H-E1 | None | MUST_WORK | Phase 1: Foundation |
| 1 | H-M1 | H-E1 | MUST_WORK | Phase 2: Mechanisms |
| 2 | H-M2 | H-M1 | SHOULD_WORK | Phase 2: Mechanisms |
| 3 | H-M3 | H-M2 | SHOULD_WORK | Phase 2: Mechanisms |
| 4 | H-M4 | H-M3 | SHOULD_WORK | Phase 2: Mechanisms |
| 5 | H-C1 | H-M4 | SHOULD_WORK | Phase 2.5: Conditions |

**Gate Rules:**
- Gate 1 (H-E1 MUST_WORK): Failure → STOP, reassess hypothesis from scratch
- Gate 2 (H-M1 MUST_WORK): Failure → STOP, fundamental pair construction flaw
- Gates 3-5 (H-M2–H-M4 SHOULD_WORK): Failure → document limitation, continue
- Gate 6 (H-C1 SHOULD_WORK): Failure → report as wider applicability finding

### 5.3 Gantt Timeline
```
═══════════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE — 6 Hypotheses | 8 Weeks Total
═══════════════════════════════════════════════════════════════════════════
Phase / Hypothesis  │ W1-2    │ W3-4    │ W5      │ W6      │ W7      │ W8
────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼────
PRE-EXPERIMENT SETUP (mandatory before Week 1 training)
  Fidelity audit    │ ████    │         │         │         │         │
  Pair proto spec   │ ████    │         │         │         │         │
  Taxonomy register │ ████    │         │         │         │         │
  Hard subset count │ ████    │         │         │         │         │
────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼────
PHASE 1: Foundation
  H-E1 (locality)  │ ████████│         │         │         │         │
  [Gate 1 ◆]       │         │ ◆       │         │         │         │
────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼────
PHASE 2: Mechanisms
  H-M1 (alignment) │         │ ████████│         │         │         │
  H-M2 (oracle shift│         │         │ ████    │         │         │
  H-M3 (pass@1 10pp│         │         │         │ ████    │         │
  H-M4 (α-interact)│         │         │         │         │ ████    │
  [Gate 2 ◆ (H-M1)]│         │         │ ◆       │         │         │
────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼────
PHASE 2.5: Conditions
  H-C1 (fidelity   │         │         │         │         │         │ ████
   threshold)      │         │         │         │         │         │
  [Gate 2.5 ◆]     │         │         │         │         │         │    ◆
────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼────
═══════════════════════════════════════════════════════════════════════════
Legend: ████ = Active work  | ◆ = Gate decision point
Total Duration: 8 weeks  | Critical Path: 8 weeks  | Slack: 0 weeks
Note: Pre-experiment setup runs in parallel with Week 1 H-E1 setup tasks
═══════════════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3 → H-M4 → H-C1

**Total Duration:** 8 weeks
- Formula: 2 (H-E1) + 2 (H-M1) + 1 (H-M2) + 1 (H-M3) + 1 (H-M4) + 1 (H-C1) = 8 weeks
- Slack Available: 0 weeks (all sequential)
- Pre-experiment setup: ~3 days (parallel with Week 1 environment setup)

**Bottleneck:** H-M1 (2 weeks) — requires cold-start SFT replication, LeanDojo rollouts, pair construction for all 4 conditions before DPO training can begin.

**Early-Stop Checkpoints:**
- End of Week 2: H-E1 locality score result → Gate 1 decision
- End of Week 4: H-M1 state alignment verification → Gate 2 decision
- If Gate 1 or Gate 2 fails: STOP pipeline, save 4-6 weeks of compute

### 5.5 Resource Summary

**Total Hypotheses:** 6
- Existence: 1 (H-E1)
- Mechanism: 4 (H-M1–H-M4)
- Condition: 1 (H-C1)

**Verification Phases:** 3
1. Foundation — H-E1 (2 weeks)
2. Mechanisms — H-M1 through H-M4 (5 weeks)
3. Conditions — H-C1 (1 week)

**Compute Estimate:**
- Cold-start SFT: 1 run × ~24 GPU-hours = 24 GPU-hours
- Experiment A (inference-time, 4 conditions × 3 α × 3 seeds): ~108 GPU-hours
- Experiment B DPO (4 conditions × 3 α × 3 seeds = 36 runs × ~12 GPU-hours): ~432 GPU-hours
- Fidelity audit + locality scoring: ~20 GPU-hours
- **Total estimate: ~584 GPU-hours (A100)**

**Pilot Recommendation:** Run α=0 only, conditions A vs. D, 1 seed first (~30 GPU-hours) to validate pipeline before full factorial.

### 5.6 Execution Order

**Step 1 (Pre-experiment, Week 1):** Complete 4-item pre-experiment protocol (fidelity audit, condition C protocol, taxonomy, hard subset count)
**Step 2 (Week 1-2):** Run cold-start SFT on Qwen2.5-Math-7B; define frozen hard subset
**Step 3 (Week 1-2):** Execute H-E1 — Experiment B, conditions A vs. B vs. permutation, α=0; compute locality score
**Step 4 (End Week 2):** Evaluate Gate 1 — if locality score A > permutation (p<0.05): PROCEED; else STOP
**Step 5 (Week 3-4):** Execute H-M1 — verify state alignment for all 4 condition pair constructions; pilot DPO run
**Step 6 (End Week 4):** Evaluate Gate 2 — if state alignment = 100%: PROCEED; else STOP
**Step 7 (Week 5):** Execute H-M2 — full DPO training conditions A and D at α=0; compute RID and locality scores
**Step 8 (Week 6):** Execute H-M3 — evaluate hard-stratum pass@1 across all 4 conditions × DPO on/off × α={0, 0.5, 1.0}
**Step 9 (Week 7):** Execute H-M4 — compute α-interaction Δ(A−D) across α levels; Cohen's d
**Step 10 (Week 8):** Execute H-C1 — stratify results by fidelity quartile; compute fidelity-stratified Δ(A−D)
**Final:** Aggregate results → Phase 5 Baseline Comparison

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Semantically grounded step-local formal feedback (Lean4 compiler errors, Z3 SMT counterexamples) functions as a "local logical oracle" in LLM DPO training, producing significantly greater hard-stratum correctness recovery (≥10pp) compared to episode-level or ungrounded feedback, because state-specific semantic information directs the policy toward formally valid continuations rather than diffusely sharpening it.

**Supporting Evidence:**
1. Formal verifiers return step-local grounded rejections with location + violated constraint (BFS-Prover/LeanDojo evidence [Xin et al. 2025])
2. State-aligned DPO pairs associate violated constraints with specific policy decisions that caused them
3. Three independent prior systems all show oracle-direction effects: PropertyGPT 87% vs 63%, Proof of Thought 0% vs 14.6% errors, BFS-Prover 72.95% miniF2F

**Strengths:**
- Convergent evidence across 3 independent systems with different architectures
- α-interaction is a unique prediction — no competing hypothesis predicts α-dependent advantage
- Locality score + permutation control cleanly isolates semantic content contribution
- Pre-registered failure thresholds prevent post-hoc reinterpretation

**Expected Outcomes:**
- P1: Δ(A−D) ≥ 10pp, non-overlapping 95% CIs, DPO-on
- P2: Monotonic α-interaction, Cohen's d ≥ 0.3
- P3: Locality score A > permutation control (p < 0.05)

### 6.2 Antithesis

**Null Hypothesis (H0):** There is no significant difference in hard-stratum pass@1 between semantically grounded step-local feedback and episode-level or ungrounded feedback — all conditions produce equivalent correctness recovery because DPO functions as a policy regularizer regardless of negative example semantic content.

**Counter-Arguments:**
1. DPO effect may be dominated by contrastive structure (any a_w vs a_l at same state) rather than semantic content of a_l — regularizer is parsimonious
2. Prior systems never performed the controlled ablation; success may attribute to repair loop structure, not feedback semantics
3. Assumption violations (A1 fidelity, A4 taxonomy) could confound IV manipulation and collapse conditions

**Conditions Under Which H0 Would Be Supported:**
- If Δ(A−D) < 2pp across all α settings under DPO-on (pre-registered rejection threshold)
- If locality score condition A ≈ permutation control (semantic content not the active ingredient)
- If α-interaction Cohen's d < 0.3 (regularizer predicts uniform gains across α)

**Weakness of Antithesis:**
- Regularizer hypothesis cannot explain Experiment A (frozen policy) oracle-direction effects in PropertyGPT and Proof of Thought — no DPO involved
- Three independent systems with different feedback mechanisms all point in oracle direction

### 6.3 Synthesis

The verification plan resolves the oracle/regularizer dialectic through sequential hypothesis testing with pre-registered discriminating predictions. This is not a compromise but a resolution — the 6-hypothesis chain provides three independent, non-redundant empirical tests:

**Resolution Path:**
1. **H-E1 (Existence):** Establishes oracle signal (locality score) before performance claims — cleanest semantic content test
2. **H-M2 (Oracle shift):** Tests mass shift mechanism independently of performance outcome
3. **H-M3 (Performance):** Tests primary prediction P1 with pre-registered 2pp rejection threshold
4. **H-M4 (α-interaction):** Tests uniquely discriminating prediction — only oracle predicts α-dependent advantage
5. **Experiment A vs B:** Disentangles inference-time vs. training-time oracle operation (addresses DPO confound concern)

**Three Publishable Outcome Scenarios:**
1. **Full Oracle Support:** All gates pass → oracle mechanism confirmed, scope claims broadly supported
2. **Partial Support:** H-M2/H-M3 pass but H-M4 null → oracle exists but α not the modulator; narrows claims
3. **Regularizer Support:** H-M3 Δ<2pp → H0 confirmed; first controlled evidence that DPO structure, not semantics, drives improvement

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Oracle signal measurable via locality score | May be confounded by DPO structure | H-E1: locality vs. permutation control |
| Mechanism | State-aligned grounding shifts mass to premise-consistent tactics | DPO effect is diffuse (regularizer) | H-M2: RID + locality score distribution |
| Performance | ≥10pp hard-stratum advantage | All conditions equivalent | H-M3: Δ(A−D) with 2pp rejection threshold |
| Discriminability | α-interaction uniquely identifies oracle | No search geometry modulation | H-M4: monotonic interaction, Cohen's d≥0.3 |
| Scope | Results apply broadly at ≥85% fidelity | Fidelity confound limits scope | H-C1: fidelity-stratified analysis |

**Overall Robustness Score:** High
- Three non-redundant discriminating tests make false confirmation unlikely
- Pre-registered rejection thresholds make false support of antithesis detectable
- Experiment A/B design addresses DPO confound concern

**Confidence in Verification Plan:** 0.85 (synthesis confidence) — plan is well-designed to resolve the dialectic regardless of outcome direction

---

## 7. Executive Summary & Appendices

### 7.1 Executive Summary

**Main Hypothesis:** H-FormalFeedbackOracle-v1 — Semantically grounded step-local formal feedback as "local logical oracle" producing ≥10pp hard-stratum pass@1 recovery vs. episode-level/ungrounded feedback
- ID: H-FormalFeedbackOracle-v1 | Confidence: 0.78 | Mode: Incremental (50% scope reduction)

**Verification Structure:**
- Sub-Hypotheses: 6 total — H-E1 (existence), H-M1–H-M4 (mechanism chain), H-C1 (condition)
- Phases: 3 phases over 8 weeks | Gates: 2 MUST_WORK (H-E1, H-M1), 4 SHOULD_WORK
- Datasets: Full miniF2F hard subset + full Vericoding hard subset (cold-start SFT <20%)
- Model: Qwen2.5-Math-7B (BFS-Prover cold-start SFT)

**Risk Assessment:** High (2 critical pre-experiment protocol items)
- Critical: R2 condition C pair construction must be pre-specified before any training
- High: R1 fidelity audit ≥85% gates all experiments; R3 hard subset size; R4 taxonomy pre-registration

**Immediate Action:** Complete 4-item pre-experiment protocol, then begin Phase 1 with H-E1

### 7.2 Final Summary & Conclusions

**Key Achievements:**
- 6 hypotheses across 3 phases with clear dependency chain and gate conditions
- H0 fully addressed: three independent discriminating tests (locality, performance, α-interaction)
- Scope reduction: 50% — three BUILD_ON facts skipped, only PROVE_NEW claims tested
- Pre-registered failure thresholds prevent post-hoc reinterpretation

**Verification Execution Order:**

**Pre-Experiment (before Week 1):**
- Fidelity audit (200-step sample, two annotators, κ≥0.7)
- Condition C pair construction protocol pre-specification
- Tactic taxonomy pre-registration from LeanDojo categories
- Hard subset size verification (require ≥200 instances)

**Phase 1: Foundation (Weeks 1-2)**
- H-E1: Locality score — condition A vs. B vs. permutation control
- Gate 1 (MUST_WORK): locality(A) > permutation (p<0.05) → PROCEED; else STOP

**Phase 2: Core Mechanisms (Weeks 3-7)**
- H-M1: State alignment verification + pilot DPO run (Weeks 3-4)
- Gate 2 (MUST_WORK): 100% state alignment → PROCEED; else STOP
- H-M2: RID + locality score under full DPO (Week 5)
- H-M3: Hard-stratum pass@1 across all conditions × α (Week 6)
- H-M4: α-interaction monotonicity + Cohen's d (Week 7)

**Phase 2.5: Conditions (Week 8)**
- H-C1: Fidelity-stratified Δ(A−D) analysis

**Critical Decision Points:**
1. **Gate 1 (end Week 2):** H-E1 locality test → PASS: proceed | FAIL: stop, reassess
2. **Gate 2 (end Week 4):** H-M1 alignment check → PASS: proceed | FAIL: stop, design flaw
3. **H-M3 result (Week 6):** Δ<2pp → reject oracle; 2-10pp → partial; ≥10pp → full support

**Open Questions:**
- Does the oracle effect hold for Vericoding Verus/Dafny formalisms in addition to Lean?
- Does the inference-time oracle effect (Experiment A, frozen policy) match the training-time effect (Experiment B, DPO)?
- What is the minimum formalization fidelity threshold below which the oracle mechanism breaks down?

**Recommendations:**
1. **Immediate:** Complete 4-item pre-experiment protocol before any GPU usage
2. **Pilot:** Run α=0 only, conditions A vs. D, 1 seed (~30 GPU-hours) before full factorial
3. **Compute:** Reserve ~600 GPU-hours (A100); checkpoint every run against preemption
4. **Publication strategy:** All three outcome scenarios (full/partial/null) produce publishable contributions to VerifAI workshop

### 7.3 Appendices

**A. Phase 2A Reference**
- Source: `03_refinement.yaml` (H-FormalFeedbackOracle-v1, schema v10.0.0)
- Discussion: 15 exchanges, 6 agents, convergence at all 6 criteria
- Established Facts skipped (BUILD_ON): 3 claims (50% scope reduction)

**B. MCP Tool Usage Summary**
- Total MCP calls: 4 (3 × scientificmethod, 1 × collaborativereasoning, 1 × structuredargumentation)
- scientificmethod: H-E1 hypothesis+experiment, H-M-chain hypothesis+experiment, H-C1 hypothesis
- collaborativereasoning: Risk analysis expert panel (3 personas, 7 contributions)
- structuredargumentation: Thesis + Antithesis + Synthesis dialectical chain

**C. Established Facts Registry (BUILD_ON — not re-tested)**
1. Formal verification feedback loops improve LLM correctness over no-feedback baselines (BFS-Prover, PropertyGPT, Proof of Thought)
2. Step-local formal feedback enables DPO preference training (BFS-Prover DPO pairs)
3. Iterative inference-time repair loops improve quality without retraining (PropertyGPT 87% vs 63%, Proof of Thought 0% vs 14.6%)

---

*Generated by YouRA Phase 2B (v7.7.0) | 2026-05-20*
