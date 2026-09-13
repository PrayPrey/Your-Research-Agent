# Phase 2A Research Discussion Log

**Gap ID:** gap-1
**Gap Title:** No Empirical Testing of Bidirectional Alignment Signals in Training
**Date:** 2026-08-28
**Execution Mode:** UNATTENDED (Self-Play)

---

## Briefing Context

### Research Gap Summary
Existing RLHF implementations (trl, OpenRLHF) use single-objective reward models focused on helpfulness. Sun et al. 2024 provides theoretical bidirectional framework but no training methodology. No existing codebase combines IFEval-style controllability metrics as a training signal alongside helpfulness.

### Core Research Question
Do language models fine-tuned with bidirectional alignment signals (combining AI-to-human helpfulness AND human-to-AI controllability metrics) achieve better alignment benchmark scores than models using unidirectional RLHF alone?

### Available Papers
- Ouyang et al. 2022 - InstructGPT (RLHF baseline)
- Bai et al. 2022 - Constitutional AI (RLAIF)
- Zhou et al. 2023 - LIMA (minimal data)
- Askell et al. 2021 - HHH framework
- Sun et al. 2024 - Bidirectional Alignment Framework
- Zhou et al. 2023 - IFEval (instruction following benchmark)
- Rafailov et al. 2023 - DPO (reward-free alternative)

### Key Implementation Resources
- trl library (PPOTrainer, DPOTrainer)
- lm-evaluation-harness (IFEval, TruthfulQA, BBQ)
- AlpacaEval (helpfulness scoring)

### Feasibility Constraints (Pipeline-Enforced)
- Must use existing real datasets and existing benchmarks
- No new benchmarks, rubrics, or scoring frameworks
- No synthetic/generated data that doesn't exist yet
- No human evaluation or annotation required

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we approach bidirectional alignment not as two separate objectives competing for optimization bandwidth, but as a *single unified objective* where controllability IS a form of helpfulness? Consider: a model that perfectly follows instructions is inherently more helpful because it does what the user actually wants, not what it infers they might want.

The existing RLHF paradigm treats helpfulness as "produce good outputs" — but Sun et al.'s bidirectional framework suggests the Human→AI direction (controllability) is equally fundamental. What excites me is that IFEval already operationalizes this: instruction-following accuracy is a measurable proxy for "does the model respect human agency?"

Here's the paradigm shift I'm proposing: instead of R = α·R_helpfulness + β·R_controllability as separate signals, what if we train a UNIFIED reward model that scores responses on "aligned helpfulness" — defined as helpfulness CONDITIONAL on instruction adherence? A response that's helpful but ignores format constraints should score lower than a less elaborate response that follows instructions precisely.

The existing trl library supports custom reward models. We could train a reward model on preference pairs where annotators explicitly consider BOTH dimensions. Or — even simpler — we could use DPO with preference pairs constructed from IFEval-style instruction variations.

**Key Points:**
- Reframe bidirectional alignment as "conditional helpfulness" rather than competing objectives
- IFEval provides ready-made controllability operationalization
- DPO with instruction-aware preference pairs could avoid reward model complexity
- Cross-domain insight: control theory's "reference tracking" maps to instruction following

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's framing is provocative, but let me stress-test it. The claim that "controllability IS helpfulness" conflates two measurably distinct constructs. Consider: a model could score 95% on IFEval (high controllability) while producing factually incorrect content (low helpfulness on TruthfulQA). These dimensions CAN diverge.

The more rigorous question is: what specific, falsifiable prediction does the bidirectional hypothesis make? Let me propose one:

**H1:** Models fine-tuned with combined helpfulness+controllability signals will show IMPROVED performance on safety benchmarks (TruthfulQA, BBQ) compared to helpfulness-only baselines, because controllability enables users to steer models away from harmful outputs.

This is testable. The success criterion: statistically significant improvement (p < 0.05) on at least 2 of 3 safety benchmarks (TruthfulQA, BBQ, HHH-Eval) when comparing bidirectional vs unidirectional fine-tuning.

The falsification criterion: if bidirectional models show NO improvement or DEGRADATION on safety benchmarks despite improved IFEval scores, the "controllability enhances safety" mechanism is invalidated.

For experiment design, I propose: (1) Baseline: Standard RLHF with AlpacaEval-based reward, (2) Treatment: RLHF with combined AlpacaEval + IFEval-derived reward, (3) Same base model, same training compute, only reward signal differs.

**Key Points:**
- Helpfulness and controllability are measurably distinct — must test independently
- Falsifiable prediction: bidirectional training improves safety benchmarks
- Success criterion: p < 0.05 on 2+ safety benchmarks
- Control for compute budget and base model to isolate signal effect

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Vera's experimental design is sound, but let me address what makes this genuinely significant for the field. The question we must ask: is this a real contribution or incremental engineering?

I argue this IS significant because it tests a THEORETICAL claim (Sun et al. 2024's bidirectional framework) that has never been empirically validated. The field has implicitly assumed unidirectional alignment suffices. If bidirectional signals demonstrably improve outcomes, it reshapes how we think about alignment training.

The impact extends beyond benchmarks. If controllability-enhanced training produces models that are more steerable, this has implications for: (1) AI safety — users can course-correct more reliably, (2) personalization — models adapt to individual instruction styles, (3) deployment — operators can enforce behavior policies.

However, I share a concern: the field might dismiss this as "just adding another metric." To make impact, we need to show that the INTERACTION between signals produces emergent benefits — not just additive improvements. Specifically: does bidirectional training produce qualitatively different behavior patterns, or just marginally better numbers?

I propose adding a QUALITATIVE analysis alongside benchmarks: error analysis of failure modes. Do bidirectional models fail differently? Are their failures more recoverable through user intervention?

**Key Points:**
- Validates Sun et al. 2024's theoretical framework empirically — field-shaping potential
- Must demonstrate INTERACTION effects, not just additive improvements
- Qualitative error analysis needed alongside quantitative benchmarks
- Practical implications for safety, personalization, and deployment

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me ground this in technical reality. The core mechanism proposed is: combine IFEval-style controllability metrics with RLHF helpfulness signals. Is this scientifically sound?

**Mechanism Analysis:**

1. **IFEval as training signal:** IFEval produces pass/fail scores per instruction constraint (e.g., "response must be under 100 words", "must include exactly 3 bullet points"). These are DISCRETE, not differentiable. For RL training, we need a continuous reward. Solution: use constraint satisfaction RATE across a batch as the reward proxy. This is mathematically valid — it's the expected value of the binary constraint satisfaction.

2. **Reward combination:** R = α·R_helpfulness + β·R_controllability is standard multi-objective RL. The Pareto frontier exists and is well-characterized theoretically. No fundamental barrier here.

3. **Measurement validity:** AlpacaEval (helpfulness) uses GPT-4 as judge. IFEval uses rule-based constraint checking. Both are established methodologies. Combining them doesn't introduce measurement artifacts.

**Potential barrier:** If α and β weights are poorly tuned, we might see reward hacking — optimizing controllability at the expense of response quality. Mitigation: constrained optimization with minimum helpfulness threshold.

The mechanism is theoretically sound. The intervention CAN work in principle. The open question is DOES it work in practice, which is what the experiment tests.

**Key Points:**
- IFEval constraint satisfaction rate is valid continuous reward proxy
- Multi-objective RL with Pareto frontier is well-established
- No fundamental barriers — both measurement methods are proven
- Risk: reward hacking. Mitigation: constrained optimization

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Building on Prof. Pax's feasibility analysis and Prof. Vera's experimental design, let me synthesize a strengthened hypothesis.

**Refined Core Hypothesis:**

Under standard RLHF fine-tuning conditions, if we augment the helpfulness reward with IFEval-derived controllability signals (R_combined = α·R_AlpacaEval + β·R_IFEval_rate), then the resulting model will:
- (P1) Achieve higher IFEval scores than helpfulness-only baseline (primary)
- (P2) Maintain or improve AlpacaEval scores (no helpfulness degradation)
- (P3) Show improved safety benchmark performance (TruthfulQA, BBQ)

...because controllability training teaches the model to respect user constraints, which generalizes to respecting safety constraints.

**Addressing concerns raised:**

1. **Dr. Nova's unification concern:** We're NOT claiming controllability IS helpfulness. We're claiming they're complementary signals that, when combined, produce better-aligned models. The interaction hypothesis is: controllability provides a "safety net" that prevents helpfulness optimization from producing uncontrolled outputs.

2. **Dr. Sage's interaction effect:** P3 (safety improvement) specifically tests for interaction. If controllability training ONLY improved IFEval but not safety, we'd have additive effects. If safety improves beyond what helpfulness alone achieves, that's interaction.

3. **Prof. Pax's reward hacking:** We add an explicit constraint: R_AlpacaEval must remain above 0.8x baseline. This prevents controllability from dominating.

**Key Points:**
- Three testable predictions: P1 (controllability), P2 (helpfulness maintained), P3 (safety enhanced)
- Mechanism: controllability generalizes to respecting all constraints, including safety
- Safeguard: minimum helpfulness threshold prevents reward hacking

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good progress, but let me find the remaining weaknesses.

**Challenge 1: Confound — Training Data Overlap**
IFEval instructions are publicly available. If the fine-tuning data contains similar instruction patterns, we're not testing generalization — we're testing memorization. Mitigation needed: held-out instruction types not seen during training.

**Challenge 2: Mechanism Circularity**
The claim "controllability generalizes to safety constraints" assumes instruction-following and safety-following share underlying model capabilities. But safety constraints are often IMPLICIT (don't be harmful) while IFEval constraints are EXPLICIT (use exactly 3 bullets). Why would explicit constraint training help implicit constraint adherence?

**Challenge 3: Baseline Selection**
AlpacaEval-only RLHF is the proposed baseline. But InstructGPT-style RLHF already includes instruction-following in preference labels (annotators rate responses partly on whether they follow instructions). Is our baseline truly "helpfulness-only" or already implicitly bidirectional?

**Challenge 4: α/β Sensitivity**
The hypothesis assumes some optimal α/β exists. What if the Pareto frontier shows sharp trade-offs — controllability gains require proportional helpfulness losses? We need to report the FULL trade-off curve, not just one α/β point.

**What would convince me:**
1. Held-out instruction evaluation to prove generalization
2. Evidence that IFEval training improves IMPLICIT constraint following
3. Clearer baseline definition or ablation showing AlpacaEval alone doesn't include controllability
4. Full α/β sweep with Pareto frontier visualization

**Key Points:**
- Risk: IFEval instruction memorization — need held-out evaluation
- Mechanism gap: explicit→implicit constraint generalization needs justification
- Baseline ambiguity: AlpacaEval may already include implicit controllability
- Required: full trade-off curve, not single α/β configuration

---

### Exchange 7

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Prof. Rex raises critical points. Let me address each and refine the hypothesis.

**Response to Challenge 1 (Data Overlap):**
Valid concern. We'll split IFEval instructions: 70% for training signal computation, 30% held-out for evaluation. Additionally, we'll evaluate on AlpacaEval's instruction-following subset (different instruction distribution) to test generalization.

**Response to Challenge 2 (Explicit→Implicit Generalization):**
The mechanism hypothesis is: training on EXPLICIT constraints builds model capacity for constraint-following GENERALLY. Evidence from Constitutional AI suggests self-critique training (explicit safety checks) improves implicit harmlessness. We'll test this directly by measuring safety benchmarks BEFORE and AFTER controllability training.

**Response to Challenge 3 (Baseline Definition):**
Good catch. We'll use THREE baselines:
- B1: SFT-only (no RLHF) — pure instruction fine-tuning
- B2: RLHF with AlpacaEval reward — helpfulness focus
- B3: RLHF with custom "response quality" reward (excluding instruction adherence)

B3 is the cleanest "helpfulness-only" baseline. If B2 already includes implicit controllability, comparing against B3 isolates the signal.

**Response to Challenge 4 (α/β Sensitivity):**
Agreed. We'll run α/β sweep: α ∈ {0.2, 0.4, 0.6, 0.8}, β = 1-α. Report full Pareto frontier. Hypothesis succeeds if ANY point on frontier shows P1+P2+P3 improvements over best single-objective baseline.

**Final Refined Hypothesis:**

**H-BiAlign-v1:** Under standard fine-tuning conditions, adding IFEval-derived controllability signals to RLHF produces models that:
- P1: Score higher on held-out instruction-following (IFEval_test) than single-signal baselines
- P2: Maintain ≥95% of baseline AlpacaEval performance
- P3: Improve on ≥1 safety benchmark (TruthfulQA or BBQ) by ≥2 percentage points

**Mechanism:** Explicit constraint training builds general constraint-following capacity that transfers to implicit safety constraints.

**Null Hypothesis (H0):** There is no significant difference in held-out IFEval, AlpacaEval, or safety benchmark scores between bidirectional and unidirectional fine-tuned models.

**Key Points:**
- Held-out IFEval split (70/30) addresses memorization concern
- Three-baseline design isolates controllability signal
- Full α/β Pareto frontier will be reported
- Refined predictions with specific success criteria

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hypothesis tests Sun et al. 2024's theoretical framework empirically for the first time. The reframing of bidirectional alignment as "conditional helpfulness" with IFEval integration is genuinely novel. No prior work combines controllability metrics AS training signals — this opens a new research direction.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis has clear falsification criteria: if bidirectional models show no improvement on held-out IFEval, maintain <95% AlpacaEval performance, or fail to improve safety benchmarks, it's falsified. The three-baseline design with held-out evaluation enables clean causal inference.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** This validates a theoretical framework (Sun 2024) that could reshape alignment training paradigms. If successful, it demonstrates that "respecting user agency" (controllability) is trainable and improves overall alignment. Field-shaping implications for safety, personalization, and deployment.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All components exist: trl PPOTrainer, IFEval benchmark, AlpacaEval, TruthfulQA. IFEval constraint satisfaction rate is a valid continuous reward proxy. Multi-objective RLHF is well-established. No fundamental technical barriers — this is implementable with existing tooling.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on **H-BiAlign-v1**: a hypothesis that bidirectional alignment training — combining AI→Human helpfulness signals with Human→AI controllability signals — produces better-aligned models than unidirectional RLHF.

The core claim is: Under standard RLHF fine-tuning conditions, augmenting the reward with IFEval-derived controllability signals (R = α·R_AlpacaEval + β·R_IFEval_rate) yields models that (P1) score higher on held-out instruction-following, (P2) maintain ≥95% helpfulness, and (P3) improve on safety benchmarks.

The proposed mechanism is that explicit constraint training (IFEval-style) builds general constraint-following capacity that transfers to implicit safety constraints. This is testable by comparing safety benchmark performance before and after controllability training.

The experimental approach uses three baselines (SFT-only, AlpacaEval RLHF, quality-only RLHF) with a 70/30 IFEval train/test split to address memorization concerns. A full α/β Pareto frontier sweep will characterize the helpfulness-controllability trade-off.

Key innovation: treating IFEval constraint satisfaction rate as a differentiable reward signal, enabling controllability to be trained alongside helpfulness in a unified RLHF framework.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- The explicit→implicit constraint generalization mechanism is theorized but unproven. Safety benchmark improvement (P3) is the critical test.
- AlpacaEval may already capture some controllability implicitly. The B3 baseline (quality-only, excluding instruction adherence) is essential.
- α/β sensitivity could reveal sharp trade-offs. The Pareto frontier must be reported fully to avoid cherry-picking.
- **Mitigation Strategy:** Run all three baselines. Report full Pareto frontier. Include Constitutional AI-style analysis comparing explicit vs implicit constraint adherence.

