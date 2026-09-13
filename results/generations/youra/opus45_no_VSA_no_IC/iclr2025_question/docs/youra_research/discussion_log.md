# Phase 2A Discussion Log

## Briefing Context

**Research Gap:** Single-Pass vs Multi-Sample Parity (P1)
- Current: Semantic Entropy (SE) requires 5-10 samples; SEPs claim near-parity with single-pass
- Missing: Systematic comparison across LLM families on standard benchmarks
- Impact: Enables practical deployment of hallucination detection

**Key Papers:**
- Detecting hallucinations using semantic entropy (Nature 2024, 1615 citations)
- Semantic Entropy Probes (2024, 247 citations) - single-pass via hidden state probes
- Token-Level UQ Fact-Checking CCP (2024, 186 citations)
- UQLM Framework (2025, 22 citations) - ensemble black/white-box scorers

**Key Implementations:**
- cvs-health/uqlm (1183 stars) - Comprehensive UQ toolkit
- IINemo/lm-polygraph (480 stars) - UE method battery
- jlko/semantic_uncertainty (411 stars) - Nature paper code
- OATML/semantic-entropy-probes (65 stars) - Single-pass SEPs

**Benchmarks:** TruthfulQA (817 questions), TriviaQA (~11K questions), HaluEval

**Feasibility Constraints (Pipeline-Enforced):**
- MUST use existing real datasets and existing benchmarks
- NO new benchmarks, rubrics, or scoring frameworks
- NO synthetic/generated data or future follow-up data
- NO human evaluation or subjective scoring by human raters

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What excites me here is the efficiency paradox! The Nature paper showed semantic entropy works brilliantly but costs 5-10x compute. SEPs claim they can match this with a single pass by probing hidden states. But here's what I find fascinating — nobody has systematically checked if this single-pass magic generalizes across model families.

What if the real question isn't "can we match multi-sample accuracy?" but rather "what are we actually measuring when we probe hidden states?" The SEP authors assume hidden states encode uncertainty about meaning, but what if different architectures encode this differently? Llama might use layer 15, Mistral might use layer 22, Qwen might spread it across attention heads.

Here's a wild thought: instead of training separate probes per model, what if we could find universal "uncertainty signatures" that transfer? The ICR_Probe work (ACL 2025) hints at cross-layer dynamics being important. What if uncertainty isn't localized to a single layer but emerges from specific layer-to-layer transitions?

**Key Points:**
- SEPs assume universal hidden-state uncertainty encoding — untested across model families
- Cross-layer dynamics (ICR_Probe) suggest uncertainty may be distributed, not localized
- Opportunity: Find transferable uncertainty signatures instead of per-model probes

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises intriguing possibilities, but let me inject some scientific rigor here. Before we chase transferable signatures, we need to establish clear baselines.

The fundamental question is: what does "near-parity" actually mean? The SEP paper reports competitive AUROC, but on which benchmarks? Under what conditions? With what model sizes? If we're going to claim single-pass methods match multi-sample, we need a precise experimental protocol.

I propose we define success criteria upfront: Single-pass method achieves AUROC within 0.03 of multi-sample semantic entropy on TruthfulQA, across at least 3 model families (Llama, Mistral, Qwen). This gives us a falsifiable prediction.

What would disprove this hypothesis? If single-pass methods consistently underperform by >0.05 AUROC, or if performance varies wildly across model families (standard deviation >0.1), then the "near-parity" claim fails. We need to design for failure, not confirmation.

**Key Points:**
- "Near-parity" needs precise operational definition: AUROC within 0.03
- Cross-model validation essential: test Llama, Mistral, Qwen families
- Falsification criterion: >0.05 gap or >0.1 std deviation across families kills the hypothesis

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question I must ask is: why does this matter for the field? Let me assess the significance.

If we can prove single-pass methods achieve parity with multi-sample semantic entropy, the contribution is clear: we unlock practical deployment of hallucination detection. Current systems avoid real-time UQ because 5-10 forward passes per query is untenable at scale. A validated single-pass approach changes the economics entirely.

But here's where I push back slightly on Prof. Vera's framing. The field impact isn't just about AUROC parity — it's about the efficiency-accuracy Pareto frontier. Even if single-pass achieves 0.72 AUROC vs multi-sample's 0.78, that 5-10x speedup might be worth the trade-off for many applications.

The deeper scientific question is: what does cross-model generalization tell us about how LLMs represent uncertainty? If probes transfer, it suggests uncertainty is a fundamental property of transformer representations, not an architectural quirk. That's a finding with theoretical implications beyond the immediate application.

**Key Points:**
- Primary impact: unlock practical real-time hallucination detection deployment
- Efficiency-accuracy trade-off matters as much as raw parity
- Transferability finding would have theoretical implications about transformer representations

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me ground this discussion in what's actually achievable with existing resources.

The good news: all the pieces exist. TruthfulQA has ground truth (817 questions, multiple-choice format). The semantic_uncertainty codebase implements multi-sample SE. The semantic-entropy-probes repo implements single-pass SEPs. lm-polygraph provides additional UE methods for comparison.

The mechanism is theoretically sound: hidden states in transformers encode rich semantic information (established by probing literature since 2019). The question of whether they encode *uncertainty* about that information is empirically testable without inventing new methods.

What concerns me is scope creep. Dr. Nova's "universal signatures" idea is fascinating but risks turning this into a massive undertaking. For a hypothesis we can actually test with existing benchmarks and code: compare AUROC of (1) multi-sample SE, (2) single-pass SEPs, (3) token-level entropy baseline across 3 model families on TruthfulQA. That's achievable.

Cross-model probe transfer is a secondary hypothesis — test it only after establishing the primary comparison.

**Key Points:**
- All components exist: benchmarks (TruthfulQA), codebases (semantic_uncertainty, SEPs, lm-polygraph)
- Mechanism is theoretically grounded in established probing literature
- Scope control: primary comparison first, transfer experiments second

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Let me synthesize what's emerging here and strengthen it into a testable hypothesis.

I hear Prof. Vera's call for rigor and Prof. Pax's scope control. Here's how we bridge them: our core claim is that hidden-state probes (SEPs) can match multi-sample semantic entropy performance on hallucination detection within established benchmarks, and this holds across multiple LLM families.

The mechanism: transformer hidden states encode not just semantic content but also the model's uncertainty about that content. This uncertainty manifests as geometric properties (directions, distances) that linear probes can detect. The SEP paper showed this works for specific models — we're testing generalizability.

I propose we frame this as: "Under standard QA evaluation conditions (TruthfulQA), if we apply trained hidden-state probes to detect hallucinations, then we achieve AUROC within 0.05 of multi-sample semantic entropy, because hidden states encode extractable uncertainty signals that are consistent across model architectures."

This is testable today with existing code and benchmarks. Dr. Nova's transfer hypothesis becomes a secondary prediction: if probes trained on Model A achieve >80% of their original AUROC on Model B without retraining, that suggests universal uncertainty encoding.

**Key Points:**
- Core hypothesis: SEPs match SE within AUROC 0.05 across LLM families
- Mechanism: hidden states encode extractable uncertainty signals
- Primary test: TruthfulQA, 3 model families, existing codebases
- Secondary prediction: cross-model probe transfer at >80% performance retention

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Dr. Ally's synthesis is tighter, but let me stress-test it.

First concern: the AUROC 0.05 threshold. Where does this come from? If multi-sample SE achieves 0.85 AUROC, is 0.80 for single-pass truly "parity"? I want to see confidence intervals. With 817 TruthfulQA questions, our statistical power determines whether 0.05 is a meaningful threshold or noise.

Second concern: hidden assumption about probe training data. SEPs are trained on specific datasets — what if they're fitting to dataset artifacts rather than genuine uncertainty? We need a held-out test: train probes on TriviaQA, evaluate on TruthfulQA. If performance drops catastrophically, the probes aren't detecting uncertainty, they're overfitting.

Third concern: what counts as "across model families"? Llama-2-7B vs Llama-2-70B is the same family but different scale. Llama-2 vs Llama-3 is same company, different architecture. We need to define family clearly: at minimum, Llama, Mistral, Qwen from different organizations.

The hypothesis survives if: (1) cross-dataset generalization holds, (2) cross-family (different organization) performance gap ≤0.05 AUROC, (3) confidence intervals are tight enough that 0.05 is distinguishable from noise.

**Key Points:**
- Statistical power concern: is 0.05 AUROC distinguishable from noise on 817 questions?
- Overfitting risk: train-on-TriviaQA, test-on-TruthfulQA cross-dataset check needed
- "Family" definition: different organizations (Meta, Mistral AI, Alibaba), not just different sizes

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's challenges are sharp, and they actually point to something exciting! The overfitting concern — train on TriviaQA, test on TruthfulQA — isn't just a validity check. It's the key experiment!

If probes trained on TriviaQA transfer to TruthfulQA, we've shown uncertainty signals are task-invariant. If they also transfer across model families, we've shown they're architecture-invariant. These aren't just controls — they're the main findings!

Here's my refined pitch: the novelty isn't "single-pass matches multi-sample" (incremental). The novelty is "uncertainty representations are universal across tasks and architectures." That's a claim about the fundamental nature of transformer computation.

The practical implication: train one probe on Llama/TriviaQA, deploy it on Mistral/TruthfulQA with minimal degradation. That's not just efficiency — it's zero-shot uncertainty estimation for any model.

**Key Points:**
- Cross-dataset and cross-model transfer aren't just validity checks — they're the core finding
- Novelty reframe: uncertainty representations are universal (task and architecture invariant)
- Practical payoff: zero-shot uncertainty estimation for arbitrary models

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova, I appreciate the enthusiasm, but let's not overreach. "Universal uncertainty representations" is a much stronger claim than "single-pass matches multi-sample."

Let me propose a staged hypothesis structure:

**H1 (Primary):** Within-model single-pass SEPs match multi-sample SE within AUROC 0.05 on TruthfulQA across 3 model families. This is the baseline claim.

**H2 (Secondary):** Cross-dataset transfer: Probes trained on TriviaQA achieve AUROC >0.70 on TruthfulQA (same model). This tests task invariance.

**H3 (Tertiary):** Cross-model transfer: Probes from Model A achieve AUROC within 0.10 of probes trained directly on Model B. This tests architecture invariance.

The statistical design: with 817 TruthfulQA questions, we can detect AUROC differences of ~0.05 with 80% power at α=0.05. This sets our threshold. We use bootstrap confidence intervals rather than assuming normality.

What falsifies each level:
- H1 fails if any family shows gap >0.10 AUROC
- H2 fails if cross-dataset AUROC <0.60
- H3 fails if cross-model gap >0.15 AUROC

This staged approach lets us claim what we can support with evidence.

**Key Points:**
- Staged hypothesis structure: H1 (within-model), H2 (cross-dataset), H3 (cross-model)
- Statistical grounding: 817 questions → 0.05 AUROC detectable with 80% power
- Clear falsification criteria at each level
- Bootstrap CIs for robust inference

---

### Exchange 9

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Vera's staged structure is methodologically sound. Let me assess significance at each level.

**H1 confirmed:** Incremental but publishable. "SEPs generalize across model families" extends the original SEP paper. Venue: solid workshop or short paper.

**H1 + H2 confirmed:** Meaningful contribution. "Uncertainty probes are task-invariant" suggests hidden states encode something fundamental about model confidence. Venue: main conference.

**H1 + H2 + H3 confirmed:** This changes the conversation. "Universal uncertainty representations in transformers" is a finding about the architecture class, not just a practical tool. Venue: top conference or Nature-adjacent journal.

The field needs this. Current practice is: every deployment retrains probes for their specific model and task. If H3 holds, we publish one probe and everyone uses it. That's a paradigm shift in practical UQ for LLMs.

Even if only H1 holds, we've validated existing claims with rigorous cross-family testing. That's valuable — the SEP paper tested limited model families.

**Key Points:**
- H1 alone: incremental validation, workshop-level
- H1+H2: meaningful finding about task invariance, conference-level
- H1+H2+H3: paradigm shift — universal probes, top venue
- Even H1 validation has value given limited cross-family testing in prior work

---

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

The staged hypothesis is scientifically sound. Let me confirm feasibility for each level.

**H1 Feasibility:** HIGH. semantic-entropy-probes codebase exists. Run it on Llama-3-8B, Mistral-7B, Qwen-2-7B. TruthfulQA is ready. This is 1-2 weeks of compute on a single A100.

**H2 Feasibility:** HIGH. Same probes, different eval set. Train on TriviaQA (11K questions, more training signal), eval on TruthfulQA. No new code needed.

**H3 Feasibility:** MEDIUM. Cross-model probing requires checking if hidden state dimensions match (they won't for different model sizes). We'd need to either: (a) stick to same-size models (all 7B), or (b) learn a projection layer. Option (a) is cleaner for the core hypothesis.

**Datasets:** TruthfulQA (ground truth: correct/incorrect answers), TriviaQA (answer span matching). Both are existing benchmarks with no human evaluation needed. This satisfies the pipeline constraints.

**Models:** Llama-3-8B-Instruct, Mistral-7B-Instruct-v0.2, Qwen-2-7B-Instruct — all open-weight, all roughly same size for H3 comparability.

**Key Points:**
- H1 and H2: HIGH feasibility, existing code, 1-2 weeks compute
- H3: MEDIUM feasibility, requires same-size models for clean comparison
- All datasets have ground truth — no human evaluation required
- Specific models identified: Llama-3-8B, Mistral-7B, Qwen-2-7B

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

We've converged on something strong. Let me state the final synthesis.

**Core Hypothesis Statement:**
Under standard QA evaluation conditions (TruthfulQA benchmark), if we apply hidden-state uncertainty probes (SEPs) to detect hallucinations, then single-pass detection achieves AUROC within 0.05 of multi-sample semantic entropy across multiple LLM families (Llama-3, Mistral, Qwen-2), because transformer hidden states encode extractable uncertainty signals that generalize across architectures.

**Causal Mechanism:**
1. LLMs encode semantic uncertainty in hidden state geometry (established by SEP paper)
2. Linear probes can extract this uncertainty signal (demonstrated within-model)
3. Uncertainty encoding is consistent across model families (to be tested)
4. Therefore single-pass probing matches multi-sample estimation efficiency

**Testable Predictions:**
- P1: SEPs achieve AUROC within 0.05 of multi-sample SE on all 3 model families
- P2: Probes trained on TriviaQA achieve AUROC >0.70 on TruthfulQA (cross-dataset)
- P3: Probes transfer across model families with AUROC gap <0.10 (cross-model)

**Experimental Setup:**
- Models: Llama-3-8B, Mistral-7B, Qwen-2-7B (same scale, different orgs)
- Benchmarks: TruthfulQA (eval), TriviaQA (training for P2/P3)
- Metrics: AUROC with bootstrap 95% CI
- Baseline: multi-sample semantic entropy (5 samples)

This is immediately testable with existing code, models, and benchmarks.

**Key Points:**
- Under-If-Then-Because structure complete
- Three falsifiable predictions with clear thresholds
- All components exist: models, benchmarks, codebases
- Satisfies pipeline constraints: no new benchmarks, no human eval

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Dr. Ally's synthesis is solid. Final stress-test before I sign off.

**Remaining Concern 1:** Layer selection. SEPs require choosing which hidden layer to probe. The original paper found optimal layers vary by model. Our comparison must use the same layer-selection procedure across families (e.g., validation-set tuning) to avoid cherry-picking.

**Remaining Concern 2:** Confidence intervals on the 0.05 threshold. With 817 TruthfulQA questions and bootstrap, confirm we can actually distinguish 0.80 from 0.85 AUROC. Run a power analysis simulation before committing to this threshold.

**Remaining Concern 3:** What if one family fails but two pass? Pre-register the decision rule. I propose: H1 holds if 2/3 families show gap ≤0.05 AND no family shows gap >0.10. This allows one partial failure.

**Mitigation Strategy:** All three concerns are addressable in experimental design before running:
- Standardize layer selection via held-out validation
- Pre-compute statistical power for thresholds
- Pre-register 2/3 success criterion

With these mitigations, I'm satisfied. The hypothesis is testable, falsifiable, and achievable.

**Key Points:**
- Layer selection must be standardized across families (validation-set tuning)
- Pre-compute power analysis for 0.05 threshold distinguishability
- Pre-register decision rule: 2/3 families at ≤0.05, none >0.10
- All concerns addressable in experimental design

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The staged hypothesis structure preserves meaningful novelty. While H1 alone is incremental, the progression to H2 (task invariance) and H3 (architecture invariance) represents genuine scientific advancement. The potential finding of "universal uncertainty representations" would reshape practical UQ deployment. Cross-family generalization testing extends prior work significantly.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Clear falsification criteria exist at each hypothesis level. AUROC thresholds (0.05, 0.10, 0.15) are operationally defined with statistical grounding (817 questions, bootstrap CIs, 80% power). The staged structure allows partial results without total failure. Pre-registration of decision rules (2/3 families) further strengthens rigor.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** The hypothesis addresses a real practical problem (deployment efficiency) while potentially yielding theoretical insights (universal representations). Even minimal success (H1 only) validates cross-family generalization. Maximum success (H1+H2+H3) would be paradigm-shifting for practical LLM uncertainty estimation. The efficiency-accuracy trade-off framing ensures relevance even with partial parity.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All components exist and are accessible. Models are open-weight and similarly sized. Benchmarks have ground truth requiring no human evaluation. Existing codebases (semantic-entropy-probes, semantic_uncertainty) provide implementation. Compute requirements are modest (single A100, 1-2 weeks). The hypothesis is achievable with existing resources and satisfies pipeline constraints.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion has converged on a testable hypothesis about single-pass uncertainty estimation for LLM hallucination detection. Our core claim is that hidden-state probes (Semantic Entropy Probes) can match multi-sample semantic entropy performance within 0.05 AUROC across multiple LLM families. This matters because it would unlock practical real-time hallucination detection currently blocked by the 5-10x compute overhead of multi-sample methods.

The mechanism is grounded in established probing literature: transformer hidden states encode semantic content, and we hypothesize they also encode uncertainty about that content in a consistent way across architectures. Three testable predictions structure our verification: within-model parity (P1), cross-dataset transfer (P2), and cross-model transfer (P3). Each has clear success criteria and falsification thresholds.

The experimental design uses existing benchmarks (TruthfulQA, TriviaQA), existing models (Llama-3-8B, Mistral-7B, Qwen-2-7B), and existing codebases. No new benchmarks, no human evaluation, no synthetic data — this satisfies all pipeline constraints for immediate testability.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Layer selection procedure must be standardized across families to avoid cherry-picking
- Power analysis needed to confirm 0.05 threshold is distinguishable with 817 samples
- Decision rule for partial success (2/3 families) should be pre-registered
- **Mitigation Strategy:** Address all three in experimental design phase before execution. These are protocol concerns, not fundamental barriers.

---

## Emerged Hypothesis Summary

### Core Statement
Under standard QA evaluation conditions (TruthfulQA benchmark), if we apply hidden-state uncertainty probes (SEPs) to detect hallucinations, then single-pass detection achieves AUROC within 0.05 of multi-sample semantic entropy across multiple LLM families (Llama-3, Mistral, Qwen-2), because transformer hidden states encode extractable uncertainty signals that generalize across architectures.

### Causal Mechanism
1. LLMs encode semantic uncertainty in hidden state geometry during forward pass
2. This uncertainty manifests as geometric properties detectable by linear probes
3. The encoding is consistent across model families (architectural invariance hypothesis)
4. Single-pass probing therefore matches multi-sample estimation accuracy

### Variables
**Independent Variable:** Detection method (multi-sample SE vs single-pass SEP)
**Dependent Variable:** Hallucination detection AUROC on TruthfulQA
**Controlled Variables:** Model size (~7B), benchmark, probe training procedure, layer selection method

### Key Assumptions
- A1: Hidden states encode uncertainty, not just content (supported by SEP paper)
- A2: Linear probes suffice to extract uncertainty signals (demonstrated in prior work)
- A3: Uncertainty encoding is architecture-invariant (to be tested)
- A4: TruthfulQA is representative of hallucination detection tasks
- A5: Same-size models are comparable across families

### Null Hypothesis
There is no significant difference (<0.05 AUROC) between single-pass SEP performance and multi-sample SE performance on hallucination detection across LLM families. Alternative: the gap exceeds 0.05 AUROC for at least 2/3 families.

### Predictions
- P1 (Primary): SEPs achieve AUROC within 0.05 of multi-sample SE on Llama-3, Mistral, Qwen-2 individually
- P2: Probes trained on TriviaQA achieve AUROC >0.70 when evaluated on TruthfulQA
- P3: Probes transfer across model families with performance gap <0.10 AUROC

### Novelty
Extends SEP validation to cross-family generalization (not tested in original paper). If H3 holds, demonstrates universal uncertainty representations — a finding about transformer architecture class, not just a practical tool.

### Scope & Boundaries
**Applies to:** Instruction-tuned LLMs in 7-8B parameter range, short-form QA tasks
**Does not apply to:** Base models (no instruction tuning), very large models (70B+), long-form generation, multi-turn dialogue
**Known limitations:** Layer selection is model-specific, probe training requires some labeled data

### Experimental Setup
- Models: Llama-3-8B-Instruct, Mistral-7B-Instruct-v0.2, Qwen-2-7B-Instruct
- Eval Benchmark: TruthfulQA (817 questions)
- Training Benchmark: TriviaQA (~11K questions) for P2/P3
- Baseline: Multi-sample semantic entropy (5 samples)
- Metric: AUROC with bootstrap 95% confidence intervals

### Related Work & Baselines
- Multi-sample Semantic Entropy (Nature 2024): SOTA but expensive, AUROC 0.75-0.90
- Semantic Entropy Probes (2024): Single-pass, claims competitive AUROC
- Token-level entropy: Simple baseline, AUROC 0.52-0.65
- UQLM ensemble: Best overall, but uses multiple methods

### Phase 2B Readiness Seeds
- SH1 (Existence): Uncertainty is encoded in hidden states extractable by probes
- SH2 (Mechanism): Consistent encoding across model families
- SH3 (Comparison): Deferred to Phase 5 (baseline comparison with UQLM ensemble)

### Established Facts
- Semantic entropy detects hallucinations (Nature 2024) — BUILD_ON
- Hidden states encode semantic information (probing literature) — BUILD_ON
- SEPs work within single models (original paper) — BUILD_ON
- Cross-family generalization unproven — PROVE_NEW
