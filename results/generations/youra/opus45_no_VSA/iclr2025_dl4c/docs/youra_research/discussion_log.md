# Phase 2A Research Discussion Log

**Workflow:** phase2a-dialogue
**Architecture:** Self-Contained Tikitaka Loop
**Execution Mode:** UNATTENDED
**Started:** 2026-08-08

---

## Research Briefing

### Selected Gap

**Gap ID:** gap-2
**Title:** Limited Hybrid Approach Studies (Training + Test-Time Combined)
**Relevance:** PRIMARY
**Impact:** High

### Gap Context

**Current State:**
Most papers study either training-time RL OR test-time refinement in isolation. ScaleRTL (2025) mentions both but focuses on reasoning data. "Rethinking Fine-Tuning when Scaling Test-Time Compute" touches on interaction but is theoretical.

**Missing Piece:**
Empirical study of combining RL-trained models with test-time refinement. Does RL training make test-time refinement more or less effective? Are gains additive or superadditive?

**Research Question:**
How does iterative execution feedback during inference (test-time compute) compare to execution feedback during training (reinforcement learning from execution) for improving code generation accuracy on existing benchmarks?

**Detailed Question #4 (Direct Focus):**
Can hybrid approaches (training + test-time feedback) achieve superadditive improvements?

### Key Literature

| Paper | Year | Citations | Key Contribution |
|-------|------|-----------|------------------|
| CodeRL | 2022 | 514 | Training-time RL with execution feedback |
| Self-Refine | 2023 | 4257 | Test-time iterative refinement |
| S* | 2025 | 101 | Hybrid test-time scaling (parallel + sequential) |
| Rethinking Fine-Tuning | 2025 | 31 | Training-test interaction (theoretical) |
| PPOCoder | 2023 | 122 | PPO with execution feedback |
| B-Coder | 2023 | 21 | Value-based RL for code synthesis |

### Available Implementations

- `salesforce/CodeRL` (572 stars) - Training-time RL baseline
- `madaan/self-refine` (815 stars) - Test-time refinement baseline
- `NovaSky-AI/SkyThought` - S* test-time scaling

### Feasibility Constraints (Pipeline-Enforced)

- NO new benchmarks, rubrics, or scoring frameworks
- NO synthetic/generated data or future follow-up data
- NO human evaluation, annotation, or subjective scoring
- ONLY hypotheses testable with existing real datasets and benchmarks

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we're thinking about this entirely wrong? Everyone's been treating training-time RL and test-time refinement as separate paradigms — CodeRL does its thing during training, Self-Refine does its thing during inference. But what if they're not competing approaches at all? What if RL training actually *changes* what the model can do with test-time feedback?

Here's my wild idea: RL training with execution feedback might be teaching the model a fundamentally different skill than just "write better code." It might be teaching the model to *understand execution feedback itself* — to build an internal model of how code fails and how to fix it. If that's true, then a model trained with CodeRL-style RL should be *dramatically* better at Self-Refine-style iterative refinement than a vanilla pretrained model.

Looking at the literature, this hasn't been tested! CodeRL [Le et al., 2022] evaluates their RL-trained model in single-shot settings. Self-Refine [Madaan et al., 2023] applies refinement to pretrained models without RL training. "Rethinking Fine-Tuning" [Chen et al., 2025] mentions that CE training can be misaligned with pass@N, but they don't actually combine RL training with test-time refinement.

The S* framework [Li et al., 2025] is the closest — they do hybrid parallel + sequential test-time scaling. But even they start from a pretrained base, not an RL-trained one! What if we took a CodeRL-trained model and applied S* test-time scaling? The gains might be superadditive because the model has learned to *use* execution feedback, not just receive it.

**Key Points:**
- RL training might teach "execution feedback comprehension" as a transferable skill
- No existing work combines RL-trained models with test-time refinement
- Hypothesis: RL + test-time gains are superadditive, not merely additive

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

The hypothesis is intriguing, but we must articulate it in a falsifiable form. You propose that RL training with execution feedback teaches a transferable skill—"execution feedback comprehension"—which then yields *superadditive* gains when combined with test-time refinement (e.g., Self-Refine or S*). The evidence currently cited does not demonstrate this; it merely shows that the two techniques have been evaluated in isolation. The central scientific question is therefore: **Does RL training alter the model's conditional response to feedback in a way that measurably improves iterative refinement beyond additive effects?**

To test this, we need a controlled factorial experiment. Construct four conditions on the same base architecture and dataset:
(1) CE-trained, single-shot;
(2) CE-trained + test-time refinement;
(3) RL-trained (CodeRL-style) single-shot;
(4) RL-trained + test-time refinement.
The hypothesis of superadditivity predicts:
Δ(RL + refine) > Δ(RL) + Δ(refine) − baseline,
where Δ denotes improvement in pass@k or pass@1 relative to (1). This inequality must hold with statistical significance across tasks. If gains are merely additive—or worse, subadditive—the hypothesis is falsified. Precision in metric choice matters: pass@1 isolates refinement quality; pass@k may confound sampling diversity.

However, superadditivity alone does not establish the proposed mechanism. We must ask: *What observable behavior would demonstrate "execution feedback comprehension" rather than generic robustness?* One prediction is that RL-trained models should show greater improvement specifically when feedback is semantically informative (e.g., stack traces, assertion errors), but not when feedback is replaced with noisy or irrelevant signals. Introduce controlled perturbations: shuffle error messages, mask line numbers, inject synthetic but misleading feedback. If RL training truly builds a structured internal model of execution semantics, performance degradation under structured perturbations should be sharper than under random noise—because the model is actually using the structure. If performance is unchanged, then the supposed comprehension may be illusory.

We must also control for alternative explanations. RL training might simply increase code correctness or diversity, giving refinement more viable starting points. To isolate this confound, match initial solution quality between CE and RL models by selecting subsets with equal single-shot pass@1. Then apply identical refinement steps. If RL models still improve more under refinement despite matched starting accuracy, that supports the transferable-skill hypothesis. If not, the effect is likely attributable to baseline competence rather than feedback modeling.

Finally, I would require process-level evidence. Analyze edit trajectories: Are RL-trained models making fewer redundant edits? Do they localize fixes more accurately to error-indicated regions? Measure edit distance to ground truth per iteration, and convergence rate. A transferable "feedback comprehension" skill should manifest as steeper improvement curves and lower variance across refinement steps. Absent such signatures, claims of a fundamentally new capability are premature.

If these criteria are met—clear superadditivity, robustness controls, matched baselines, and process-level differentiation—then, and only then, would I consider the hypothesis provisionally supported. Until then, it remains an attractive but unverified narrative.

**Key Points:**
- Define superadditivity quantitatively and test via a controlled 2×2 factorial design.
- Use perturbation and baseline-matching experiments to distinguish true feedback comprehension from generic competence gains.
- Require process-level evidence (edit trajectories, convergence rates) to validate the proposed mechanism.

---

### Exchange 3

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

I appreciate 🔬 Prof. Vera's rigorous experimental design, but let me push harder on where this hypothesis breaks down.

First, the mechanism claim is underspecified. "Execution feedback comprehension" sounds compelling, but what exactly is the model learning? Is it learning to parse stack traces? To map error types to fix strategies? To predict which code regions are error-prone? These are testably different capabilities. Without specifying which subskill we're claiming RL teaches, we can't design targeted experiments. The perturbation study Prof. Vera proposes is a start, but we need finer granularity.

Second, I'm skeptical about the superadditivity claim on mechanistic grounds. Consider what RL training actually does: it optimizes the policy to maximize expected execution success. This could make the model *worse* at refinement, not better. Here's why: RL training might push the model toward high-confidence, narrow solutions that pass tests on the first try but are brittle when refinement is needed. A CE-trained model that generates more diverse, exploratory solutions might actually be *better* suited for iterative refinement because it hasn't been penalized for trying multiple approaches.

The "Rethinking Fine-Tuning" paper [Chen et al., 2025] hints at exactly this problem — they show CE training can be misaligned with pass@N objectives. The same misalignment might apply to RL training and refinement: optimizing for pass@1 during training could actively harm pass@1-after-K-refinements.

Third, let's stress-test feasibility. The 2×2 factorial design requires:
- Training an RL model from scratch (CodeRL reports ~days of training)
- Running test-time refinement on 4 conditions × multiple benchmarks × multiple repetitions
- Process-level edit trajectory analysis

This is doable with existing resources (HumanEval, MBPP, CodeT5+ checkpoints), but the specific claim about "feedback comprehension" requires additional controls that might inflate experiment complexity. We need to be ruthless about what's testable in a single paper.

**What would convince me:** Show me a prediction that distinguishes the "feedback comprehension" hypothesis from simpler explanations. For example: if RL trains "feedback comprehension," then the model should show *transfer* — improvements when feedback format changes (e.g., from Python tracebacks to natural language error descriptions). If gains are format-specific, it's just memorization of feedback patterns, not comprehension.

**Key Points:**
- The mechanism needs finer specification — what exactly is the "comprehension" skill?
- RL training might harm refinement by reducing solution diversity (subadditivity risk)
- Transfer across feedback formats would distinguish comprehension from pattern memorization

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. The core hypothesis is *technically plausible*, but only under a narrower interpretation than "RL teaches execution feedback comprehension." CodeRL-style training [Le et al., 2022] optimizes expected reward from execution outcomes. In principle, that absolutely can induce a conditional policy: *given an error trace, update the program toward a passing one*. There's no physical or mathematical barrier to that. It's just policy optimization over a trajectory that includes feedback tokens. So yes—RL could reshape the model's conditional distribution over edits in a way CE does not.

Here's what worries me: RL training does not inherently require building a structured internal model of execution semantics. It only requires correlating feedback tokens with reward gradients. A shallow pattern-matching strategy is sufficient to optimize reward if the feedback distribution is stable. So the "comprehension" story is not guaranteed by the objective. For the hypothesis to hold mechanistically, you need an argument that reward maximization under variable execution traces *forces* abstraction over error structure. That's only true if the training distribution contains sufficient variability—different programs, different error types, different surface forms. Otherwise, the model can overfit to stereotyped trace patterns.

On superadditivity: mathematically, it's feasible. RL changes the conditional policy p(edit | code, feedback). Test-time refinement repeatedly samples from that conditional. If RL sharpens that mapping, then iterative application could compound gains—so superadditivity is possible in principle. But Prof. Rex is correct about a real counterforce: RL often reduces entropy. A lower-entropy policy can hurt iterative refinement because refinement benefits from exploration across edit trajectories. There's no theorem guaranteeing the sign of the interaction term. The only way superadditivity emerges is if RL improves *edit directionality* more than it reduces useful diversity.

Now, on measurement validity. The 2×2 factorial design Vera proposes is scientifically sound. But if you want to isolate "feedback comprehension," you need interventions that selectively disrupt semantic structure while preserving token statistics. Shuffling whole error messages is too crude—it changes both semantics and surface cues. A better perturbation is structure-preserving rewrites: replace variable names, alter line numbers, paraphrase error descriptions while keeping the underlying failure mode constant. If RL-trained models degrade less under paraphrase but more under semantic contradiction, that would indicate abstraction rather than surface memorization. That's a clean mechanistic probe.

Transfer across feedback modalities, as Rex suggests, is also feasible and decisive. For example: train RL with raw Python tracebacks, then at test time provide natural-language summaries of failures generated by another model. If refinement gains persist, that supports abstraction over failure semantics. If gains collapse, then the policy likely overfit to traceback token patterns. This is experimentally straightforward and theoretically meaningful.

So, can this work in principle? Yes. There is no fundamental barrier to RL shaping a model's conditional edit policy in a way that compounds under iterative refinement. But the mechanism is not guaranteed by the objective alone. Whether superadditivity appears depends on the entropy–directionality tradeoff induced by RL and on the structural diversity of feedback during training.

**Key Points:**
- RL can, in principle, reshape the conditional edit policy; no theoretical barrier prevents superadditive gains.
- "Feedback comprehension" is not guaranteed by the RL objective—abstraction requires diverse, structurally variable feedback.
- Transfer across feedback modalities and structure-preserving perturbations are the cleanest feasibility tests of the mechanism.

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can strengthen this substantially by incorporating the critiques. Let me synthesize what's emerging.

The original "execution feedback comprehension" framing was too vague — ⚙️ Prof. Pax and 🔍 Prof. Rex have correctly identified this. But rather than abandon the hypothesis, let's refine it to something more precise and testable:

**Refined Hypothesis:** RL training with execution feedback induces a *feedback-conditioned edit policy* that, when combined with test-time refinement, produces superadditive accuracy gains — but only when the RL training distribution includes structurally diverse feedback. The mechanism is not "comprehension" in a deep semantic sense, but rather learned correlations between feedback structure and effective edit patterns that transfer across similar feedback distributions.

This addresses 🔍 Prof. Rex's concern about underspecification by dropping the "comprehension" claim and focusing on measurable policy change. It addresses ⚙️ Prof. Pax's concern about abstraction by explicitly conditioning the hypothesis on training distribution diversity.

Now, the superadditivity vs. subadditivity question. Prof. Rex raised a real risk: RL might reduce exploration. But here's evidence that it might not: the S* paper [Li et al., 2025] shows that test-time scaling works by combining parallel sampling (diversity) with sequential refinement (directionality). The key insight is that you don't need entropy in the *same* dimension. RL could reduce entropy in the *edit direction* dimension while preserving entropy in the *solution strategy* dimension. This would actually be ideal for refinement — confident edits within a strategy, diverse strategies across samples.

How do we test this? The 2×2 factorial (CE vs RL × single-shot vs refined) is the core. But we add:

1. **Diversity analysis:** Measure solution diversity (e.g., edit distance between samples) for CE vs RL models. If RL maintains strategy diversity while reducing edit noise, that supports the "directional sharpening without exploration collapse" hypothesis.

2. **Feedback perturbation study:** Following Prof. Pax's design — structure-preserving paraphrases vs. semantic contradictions. This tests whether RL induces feedback-conditional behavior at all.

3. **Transfer test:** Train with Python tracebacks, test with natural language summaries. This is the cleanest test of abstraction vs. memorization.

For benchmarks, we can use HumanEval+ and MBPP+ from evalplus/evalplus — these have more test cases and would give cleaner pass@k measurements. The CodeRL codebase provides training infrastructure; Self-Refine provides the refinement protocol.

**Key Points:**
- Refined hypothesis: RL induces feedback-conditioned edit policy with superadditive gains under diverse training feedback
- Entropy reduction risk is addressable if RL sharpens edit direction while preserving strategy diversity
- Three-pronged experimental design: 2×2 factorial + diversity analysis + feedback perturbation + transfer test

---

### Exchange 6

🔬 **Prof. Vera** (Rigorous Validation Architect):

The refined hypothesis is closer to something we can legitimately test. I will restate it in falsifiable form: *RL training with structurally diverse execution feedback induces a feedback-conditioned edit policy that yields statistically significant superadditive gains under iterative refinement, relative to CE training.* The evidence would need to satisfy a strict interaction criterion in a 2×2 design (CE vs. RL × single-shot vs. refinement), with the interaction term in a two-way ANOVA significantly > 0 on pass@1. If the interaction term is null or negative across benchmarks (e.g., HumanEval+, MBPP+), the superadditivity claim is false. We must pre-register the inequality and confidence thresholds; otherwise, post hoc interpretations will erode rigor.

However, superadditivity alone does not isolate mechanism. Dr. Ally's shift from "comprehension" to "feedback-conditioned edit policy" is an improvement, but we must define observable signatures of such a policy. The evidence would suggest feedback conditioning if and only if the model's edit distribution changes systematically with semantically equivalent feedback paraphrases and degrades under semantic contradictions. I propose a 3-condition perturbation test: (A) original traceback; (B) structure-preserving paraphrase; (C) semantically contradictory but surface-similar feedback. A genuine feedback-conditioned policy predicts: performance(A) ≈ performance(B) > performance(C). If performance drops equally for (B) and (C), the model is likely exploiting superficial token cues. If performance is invariant across all three, feedback is not being used meaningfully.

Prof. Rex's entropy concern is testable rather than speculative. We operationalize "directionality" as expected reduction in dynamic test failures per refinement step, and "strategy diversity" as clustering diversity across initial solutions (e.g., normalized AST edit distance or execution trace divergence). The hypothesis predicts: RL models exhibit steeper failure-reduction slopes per iteration (greater directionality) while maintaining comparable between-sample cluster entropy to CE models. If RL reduces both slope variance and cluster entropy, and refinement gains shrink, then subadditivity would be explained by exploration collapse. This is measurable.

On transfer: the strongest disconfirmation test is modality shift. Train RL exclusively on raw Python tracebacks, then evaluate refinement using natural-language error summaries generated by a held-out model. The hypothesis predicts partial retention of superadditive gains under modality shift. A complete collapse to CE-level interaction would falsify the abstraction claim. Importantly, we must match initial single-shot accuracy between CE and RL models before refinement to control for baseline competence, as previously noted. Without this matching, any refinement advantage may simply reflect superior starting points.

Finally, feasibility must not dilute rigor. We can constrain scope: one architecture, two benchmarks, pre-specified metrics (pass@1, interaction term, slope of failure reduction), and predefined perturbations. The experiment is not trivial, but it is finite. If the interaction term is robust, perturbation behaves as predicted, entropy is preserved, and transfer is partial but significant, then I would say—carefully—*This meets my standards.* If any of these fail, the hypothesis must be revised or rejected.

**Key Points:**
- Define and test superadditivity via a pre-registered positive interaction term in a 2×2 factorial design.
- Use structured paraphrase vs. semantic-contradiction perturbations to verify genuine feedback conditioning.
- Quantify directionality and diversity to test the entropy–sharpening tradeoff and include modality-shift transfer as a decisive falsification test.

---

### Exchange 7

🎯 **Dr. Sage** (Research Impact Evaluator):

Let me step back and ask: *What does this mean for the field?*

The discussion has converged on a precise, testable hypothesis about training-time vs. test-time execution feedback. But we should articulate why this matters beyond satisfying our curiosity.

**The question we must ask is:** If this hypothesis is confirmed — if RL training does produce superadditive gains with test-time refinement — what new research directions does this open?

First, it would fundamentally reshape how the community approaches code generation alignment. Right now, practitioners face a binary choice: invest in RL training (expensive, requires execution infrastructure) or use test-time refinement (cheap to deploy, no training needed). If gains are superadditive, the answer becomes "do both" — and the research agenda shifts toward optimizing the *combination*, not choosing between alternatives. This is a significant paradigm shift from the current either/or framing.

Second, it opens a new research direction on *training for test-time compute*. The S* paper [Li et al., 2025] and "Rethinking Fine-Tuning" [Chen et al., 2025] hint at this, but neither systematically explores training objectives designed to maximize test-time refinement gains. If our hypothesis holds, the natural next question is: *How do we design RL objectives that explicitly optimize for refinement-friendliness?* This could spawn an entire subfield.

Third — and this is crucial for the broader ML community — it tests a general principle that extends beyond code generation. The question "Does training on feedback improve the ability to use feedback at test time?" applies to any domain with structured feedback: mathematical reasoning (proof assistants), robotic control (execution outcomes), game playing (win/loss signals). If we establish this for code generation with rigorous controls, we provide a template for testing similar hypotheses across domains.

**However, incremental results have low impact.** If we find merely additive gains — RL helps a bit, refinement helps a bit, and they sum — that's confirmatory but not transformative. If we find subadditivity — they interfere — that's actually interesting because it challenges intuitions and suggests optimization trade-offs. The high-impact outcome is clear superadditivity with mechanistic evidence (the feedback perturbation and transfer tests), because that establishes both the phenomenon and its cause.

**This matters because:** The code generation field is currently fragmented between training-focused (RL) and inference-focused (test-time compute) camps. This work could unify them by showing they're complementary, not competing. That's a contribution worth making.

**Key Points:**
- Superadditivity would shift the paradigm from "choose between RL vs. refinement" to "optimize their combination"
- Opens new research direction: training objectives designed for refinement-friendliness
- Generalizes beyond code to any domain with structured feedback — template for broader ML research

---

### Exchange 8

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good — this is finally becoming falsifiable. But here's where this still breaks down.

You are implicitly assuming that a positive interaction term in the 2×2 design reflects a *qualitative* change in the edit policy. That's not guaranteed. A superadditive interaction could arise from a purely quantitative shift — e.g., RL increases baseline correctness probability of local edits, and refinement simply compounds small per-step improvements multiplicatively. No "feedback-conditioned policy" is required. Show me evidence that RL changes the *functional form* of the edit response to feedback, not just its average quality.

Vera's perturbation design is the right direction, but it's still incomplete. If performance(A) ≈ performance(B) > performance(C), that shows semantic sensitivity — but not necessarily that RL is the cause. What would convince me is a *difference-in-differences*:
[(A-B)_RL - (A-B)_CE] ≈ 0 and [(A-C)_RL - (A-C)_CE] > 0.
In other words, RL must selectively increase sensitivity to semantic contradiction relative to CE. If both models degrade similarly under (C), then RL hasn't induced stronger feedback conditioning — it's just better overall. The causal claim lives or dies on that relative effect.

Now let's talk about your entropy–directionality story. It's elegant. It's also underspecified. "Steeper failure-reduction slope" is not enough. A CE model with higher initial error variance could also show steep slopes. You need to normalize by initial failure count and compute *per-error correction probability conditional on feedback type*. I want to see something like:
P(fix error e | feedback f, RL) > P(fix e | f, CE)
while holding error class constant. Break this down by error taxonomy (syntax, type, logical, boundary). If RL only improves syntax repair, your abstraction claim collapses. If gains concentrate in semantically grounded categories (logical, boundary, multi-line dependency), now we're talking.

On transfer: training on raw tracebacks and testing on natural-language summaries is a strong probe — but only if you control for information content. If the NL summary is shorter or less precise, performance drops could reflect information loss, not lack of abstraction. You need matched-information controls: generate summaries that are semantically equivalent and verify via human or programmatic alignment that they preserve error identity. Otherwise, a collapse under modality shift is uninterpretable.

Finally, novelty. Dr. Sage is right that superadditivity is the high-impact outcome. But from a reviewer's perspective, the most interesting result may actually be *conditional superadditivity*: gains only appear when RL training includes structurally diverse feedback. That's a mechanism-level constraint. So I want an ablation on training diversity — narrow, templated feedback vs. high-variance feedback — and then test the interaction term. If superadditivity disappears under low-diversity RL, you've demonstrated necessity, not just correlation.

Fix these causal gaps, tighten the operational definitions, and pre-register the interaction contrasts. Do that — and now you're not just reporting gains, you're isolating mechanism.

**Key Points:**
- A positive interaction term is insufficient; demonstrate a *relative increase in semantic feedback sensitivity* via difference-in-differences.
- Measure per-error-class correction probabilities to test whether RL induces genuine semantic edit conditioning.
- Include a training-feedback-diversity ablation to establish necessity for superadditivity and strengthen causal claims.

---

### Exchange 9

🔭 **Dr. Nova** (Creative Novelty Explorer):

Now we're onto something! 🔍 Prof. Rex's difference-in-differences formulation just crystallized the core novelty.

Here's the paradigm shift I see emerging: We're not just testing "does hybrid work better?" — we're testing a *mechanistic theory of how feedback training transfers to inference*. The difference-in-differences contrast [(A-C)_RL - (A-C)_CE] > 0 is the key: it asks whether RL induces *differential sensitivity* to semantic structure in feedback, not just general improvement.

What if we frame this as a *causal intervention* framework? Think of it like neuroscience interpretability: we're not just measuring behavior, we're probing the causal structure of the model's feedback response. The perturbation conditions (original vs. paraphrase vs. contradiction) are interventions on the feedback input. The difference-in-differences tells us whether RL changes the *causal pathway* from feedback to edit.

This connects to something bigger: the training-feedback diversity ablation Prof. Rex proposed isn't just a control — it's a way to test whether *the RL objective itself* forces abstraction. Here's my wild idea: what if we can predict *which* RL training regimes will produce superadditivity based on the diversity of feedback encountered during training? That would give us a prescriptive theory, not just a descriptive one.

Cross-domain connection: In meta-learning, there's the concept of "learning to learn" — training on diverse tasks produces models that generalize to new tasks. What we're proposing is analogous: "learning to refine" — training on diverse feedback produces models that generalize to new feedback modalities. The training diversity ablation directly tests this meta-learning parallel.

For the experimental design, I see a clean 2×2×2 structure now:
- Factor 1: Training type (CE vs. RL)
- Factor 2: Inference mode (single-shot vs. K-step refinement)
- Factor 3 (for RL only): Training feedback diversity (low vs. high)

The three-way interaction (RL × refinement × diversity) would be the strongest test of the mechanism. If superadditivity only appears under high-diversity RL, we've demonstrated that the training distribution causally determines the transfer to inference.

**Key Points:**
- Frame as causal intervention: perturbations probe the causal pathway from feedback to edit
- Training diversity ablation tests whether RL objective *forces* abstraction under diversity pressure
- Meta-learning parallel: "learning to refine" = training on diverse feedback → generalizing to new feedback modalities

---

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here: nothing proposed so far violates physics, learning theory, or basic statistics. A 2×2 (or 2×2×2) factorial with interaction contrasts, difference-in-differences, and perturbation tests is technically sound. We can estimate interaction terms, per-error correction probabilities, and conditional sensitivities without running into identifiability paradoxes. So at a high level, yes — this is experimentally feasible in principle.

Here's what worries me, though. A positive interaction term does **not** logically entail a qualitatively new edit policy. As Rex pointed out, multiplicative compounding of small improvements can produce apparent superadditivity. That's mathematically trivial: if RL increases per-step correction probability from p to p+δ, then over K refinement steps, total success becomes 1-(1-(p+δ))^K, which can look superadditive relative to single-shot gains without any change in policy structure. So the burden is on you to show that RL changes the *conditional mapping* from feedback → edit, not just the base rate of competent edits. The difference-in-differences contrast is the right formal move because it tests whether the derivative of performance with respect to semantic contradiction is larger under RL. That's a property of the function, not its intercept.

On the perturbation side: performance(A) ≈ performance(B) > performance(C) is theoretically meaningful, but only if the perturbations are truly semantically controlled. Generating a "contradictory but surface-similar" traceback that preserves lexical statistics while flipping semantic content is nontrivial. If lexical overlap differs, you're testing robustness to distribution shift, not semantic conditioning. You'll need programmatic guarantees — e.g., identical error class labels with swapped causal variables — otherwise the inference collapses. This is feasible, but it requires constructing synthetic error-feedback pairs with controlled semantics. That's work, but it's not impossible.

The entropy–directionality story is also feasible to operationalize, but it must be normalized carefully. Per-error-class conditional correction probability is mathematically clean and implementable. Error taxonomy labeling is possible via static analyzers and execution trace parsing. The key feasibility question is whether error classes are separable enough to support meaningful conditional estimates. For syntax and type errors, yes. For "logical" errors, classification noise will be higher — but not fatal. As long as labeling noise is symmetric across CE and RL, difference-in-differences remains valid in expectation.

Now, the 2×2×2 design with training-feedback diversity: technically sound, but here's the fundamental barrier to watch. If low-diversity RL already induces broad abstraction because the model architecture itself generalizes over token patterns, then diversity may not be a necessary condition. In that case, the ablation won't show a clean three-way interaction — not because the theory is wrong, but because transformer inductive bias already supports abstraction. So you must define "diversity" in a way that meaningfully perturbs the support of feedback structures, not just their wording. Structural diversity (different traceback schemas, multi-line causal chains, varied error modalities) is more defensible than paraphrase diversity.

Bottom line: nothing here is theoretically impossible. The statistical tests are valid. The perturbations are constructible. The mechanisms are falsifiable. The real risk is interpretability drift — mistaking quantitative improvement for structural change. If you control semantics tightly, normalize per-error corrections, and define diversity structurally, then yes — okay, this could work.

**Key Points:**
- Superadditivity can arise from multiplicative compounding; mechanism claims require conditional (difference-in-differences) tests, not just interaction terms.
- Semantic perturbations must be tightly controlled at the structural level; otherwise results confound lexical shift with feedback conditioning.
- The 2×2×2 diversity design is feasible in principle, but diversity must alter structural support of feedback, not merely surface variation.

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we've now converged on something genuinely rigorous. Let me synthesize the final hypothesis with all the refinements.

**Final Hypothesis Statement:**

*Under conditions where RL training includes structurally diverse execution feedback, if we apply both RL training and test-time refinement to code generation models, then we will observe superadditive accuracy gains (positive interaction term in 2×2 factorial), differential sensitivity to semantic feedback structure (difference-in-differences contrast [(A-C)_RL - (A-C)_CE] > 0), and concentration of correction improvements in semantically grounded error classes (logical, boundary, multi-line dependency), because RL training induces a feedback-conditioned edit policy that transfers to inference-time refinement.*

This addresses every concern raised:

1. **🔬 Prof. Vera's falsifiability requirement:** The hypothesis is falsified if the interaction term is ≤ 0, if the difference-in-differences contrast is ≤ 0, or if correction gains concentrate only in syntax errors.

2. **🔍 Prof. Rex's mechanism specificity:** We've moved from vague "comprehension" to measurable "differential sensitivity to semantic structure" with per-error-class breakdown.

3. **⚙️ Prof. Pax's feasibility concerns:** The perturbations are constructible with programmatic control (identical error class labels, swapped causal variables). Training diversity is defined structurally (traceback schemas, error modalities), not just lexically.

4. **🎯 Dr. Sage's significance criterion:** Conditional superadditivity (only under high-diversity training) establishes necessity, making this a mechanistic contribution, not just an empirical observation.

**Testable Predictions:**

P1 (Primary): The interaction term (RL × refinement) will be positive and statistically significant (α=0.05) on pass@1 across HumanEval+ and MBPP+.

P2: The difference-in-differences contrast [(A-C)_RL - (A-C)_CE] will be positive, indicating RL-specific sensitivity to semantic feedback structure.

P3: Per-error-class analysis will show RL models have higher P(fix | feedback) for logical and boundary errors, not just syntax errors.

**Null Hypothesis (H0):** RL training does not alter the model's response to semantic feedback structure; any accuracy gains from combining RL and refinement are purely additive or attributable to baseline competence differences.

**Key Points:**
- Final hypothesis incorporates all critiques: superadditivity + differential sensitivity + error-class distribution
- Three falsifiable predictions with pre-specified success criteria
- Null hypothesis explicitly stated for statistical testing

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

This is much tighter. But here's where it still breaks down if you're not careful.

Your final hypothesis claims RL "induces a feedback-conditioned edit policy." That is a *mechanism claim*, not a behavioral description. Right now, all three predictions (interaction term, difference-in-differences, error-class concentration) are still behavioral. A skeptical reviewer will say: "Fine, RL increases semantic sensitivity. Why does that imply a distinct policy rather than a smoother response surface?" What would convince me is evidence that the *mapping from feedback tokens to edit locations* becomes more structured under RL. Concretely: measure alignment between referenced error spans in feedback and modified code spans in the subsequent edit. If RL increases the mutual information between feedback-localized error mentions and edit-localized changes — above CE — now you're showing structural coupling, not just outcome improvement.

On your difference-in-differences contrast: good, necessary — but insufficient unless you pre-specify the scale. Are you measuring raw accuracy deltas? Log-odds? Marginal effects? If the baseline CE model is already near floor under contradiction (C), you risk ceiling/floor artifacts inflating the RL contrast. I want to see this analyzed on the logit scale with baseline-controlled models:
logit(P(success)) ~ Training × Perturbation × Refinement.
And you report the Training × (A–C) simple effect within refinement. If that survives, you're on firmer ground. Otherwise, your "differential sensitivity" could be nonlinear scaling.

Now, the per-error-class story — this is where your hypothesis lives or dies. You've said gains must concentrate in logical and boundary errors. Good. But define those operationally *before* you run anything. If "logical" means "fails hidden tests but not visible ones," that's noisy and partially confounded with test coverage. I want structural definitions: multi-line data dependency violations, off-by-one index arithmetic, incorrect conditional guards. Pre-register counts per class and require minimum N per cell for reliable estimation. And don't just report P(fix | feedback); also report *edit precision*: proportion of edits that touch only the error-relevant span. If RL increases correction rate but also increases collateral edits, your "directed refinement" story weakens.

The diversity ablation is promising, but again — be precise. Structural diversity must alter the *conditional entropy* of feedback given error class. Quantify it. For each training regime, compute H(Feedback Schema | Error Class). If high-diversity RL has materially higher conditional entropy than low-diversity RL, and only then produces superadditivity, your necessity claim is defensible. Without that quantification, "diversity" becomes hand-wavy and reviewers will dismantle it.

I'll say this clearly: you are close. The hypothesis is now falsifiable and mechanistically framed. But if you want me — or a top-tier venue — to buy the "feedback-conditioned policy transfer" claim, you must show (1) structured alignment between feedback and edits, (2) scale-robust interaction effects, and (3) entropy-quantified training diversity linked causally to superadditivity. Do that, and now you've addressed my concerns.

**Key Points:**
- Behavioral gains are not enough; demonstrate structured feedback→edit alignment to support a policy-level mechanism claim.
- Estimate interaction and difference-in-differences effects on the logit scale to avoid floor/ceiling artifacts.
- Quantify structural diversity via conditional entropy and link it causally to superadditive refinement gains.

---

### Exchange 13

🎯 **Dr. Sage** (Research Impact Evaluator):

Now let me assess what this contributes to the field.

🔍 Prof. Rex's final requirements crystallize why this work matters: we're not just showing "hybrid is better" — we're establishing a *causal theory* of how training-time feedback translates to inference-time refinement capability. That's a fundamentally different contribution.

**The question we must ask is:** If we demonstrate all three elements — structured feedback→edit alignment, scale-robust interaction effects, and entropy-quantified diversity linkage — what does this mean for the field?

First, it provides a **theoretical framework for training-inference complementarity** in code generation. Right now, the community has empirical observations (CodeRL works, Self-Refine works, S* works) but no unified theory explaining *when and why* combinations outperform individual approaches. This work would provide that theory: RL induces structured feedback-edit coupling, which compounds under iterative refinement, but only when training includes sufficient feedback diversity.

Second, it opens a **prescriptive research agenda**. If conditional entropy of training feedback determines transfer quality, then we can *design* RL training regimes to maximize refinement-friendliness. This shifts from "evaluate combinations" to "engineer combinations" — a more actionable research program.

Third — and this is crucial for broader impact — the **methodology generalizes**. The feedback→edit mutual information metric, the perturbation-based mechanism probing, the entropy-quantified diversity measure — these are applicable to any domain with structured feedback. Mathematical reasoning (proof assistant feedback), robotic control (execution outcomes), game playing (win/loss + state analysis). We're not just answering a code generation question; we're providing a template for studying feedback-conditioned learning across domains.

**However, I must temper expectations.** If the experiments show additive or subadditive effects, that's still a contribution — it falsifies the superadditivity hypothesis and redirects the field. If we find superadditivity but can't establish the mechanism (no feedback→edit alignment increase), we've shown a phenomenon without explanation — publishable but less impactful. The highest-impact outcome requires all three legs: behavioral superadditivity, mechanistic evidence, and causal diversity linkage.

**This matters because:** We're filling Gap 2 (Limited Hybrid Studies) from Phase 1 with a mechanistic answer, not just an empirical observation. That's what advances science.

**Key Points:**
- Establishes a causal theory of training-inference complementarity, not just empirical observation
- Prescriptive implications: design RL training regimes to maximize refinement transfer
- Methodology generalizes to any feedback-conditioned learning domain

---

### Exchange 14

🔬 **Prof. Vera** (Rigorous Validation Architect):

We are now very close to a scientifically defensible claim — but only if we sharpen the falsification criteria and ensure statistical identifiability. The evidence would suggest a mechanism only if we can rule out smoother response surfaces, nonlinear scaling artifacts, and baseline competence shifts. Therefore, every core claim must be tied to a prediction that could clearly fail.

First, on the superadditivity claim: the interaction must be estimated on the logit scale using a pre-registered generalized linear mixed model:

logit(P(success)) ~ Training × Refinement × Perturbation + (1 | Problem).

The critical test is the **Training × Refinement** coefficient and the **Training × Refinement × Perturbation** simple contrast for (A–C). What would disprove the mechanism hypothesis? If the interaction term becomes non-significant after controlling for baseline CE accuracy and problem-level random effects, or if the three-way interaction collapses when analyzed on the logit scale, then the apparent superadditivity is likely a scaling artifact. This must be explicitly powered. I would require a priori power analysis targeting detection of an interaction odds ratio ≥ 1.2 with 80–90% power, given expected variance across problems. Without that, a null result is uninterpretable.

Second, regarding the feedback→edit alignment metric: this is the most promising mechanistic probe. But we must define it precisely. Let F be the span(s) referenced in feedback and E be the span(s) modified in the subsequent edit. Compute token-level mutual information I(F;E) or normalized pointwise mutual information, controlling for edit length. The prediction is:

I(F;E)_RL − I(F;E)_CE > 0,

under identical feedback distributions. What would disprove the policy-transfer claim? If RL improves correction rates but does not increase alignment beyond CE when controlling for edit magnitude and baseline accuracy. In that case, RL is increasing competence, not structural coupling. I would also require a permutation baseline: shuffle feedback spans within problem to estimate chance-level alignment.

Third, the diversity argument must be causally anchored. You cannot merely label regimes "high" and "low" diversity. Quantify structural diversity as H(Schema | Error Class). The necessity claim predicts:

Superadditivity appears only when ΔH exceeds a pre-specified threshold.

If low-diversity RL produces comparable superadditivity despite substantially lower conditional entropy, the necessity component fails. Importantly, diversity must be manipulated independently of reward magnitude or training volume — otherwise identifiability collapses.

Finally, we must guard against error-class confounds. Pre-register operational definitions for "logical," "boundary," and "multi-line dependency" errors with static analyzers and controlled synthetic templates. Require minimum cell counts (e.g., ≥100 instances per class per condition) before estimating P(fix | feedback). The hypothesis is falsified if gains distribute uniformly across all classes or concentrate primarily in syntax errors. Additionally, measure edit precision (proportion of edits confined to error-relevant spans). If correction improves but precision declines, the directed-policy interpretation weakens.

If these conditions are satisfied — scale-robust interactions, increased feedback→edit mutual information, entropy-dependent necessity, and class-specific precision gains — then I would say, cautiously, *this meets my standards*. Until then, the burden of proof remains appropriately high.

**Key Points:**
- Estimate superadditivity on the logit scale with pre-registered power analysis; null results must be interpretable.
- Demonstrate structural mechanism via increased feedback→edit mutual information beyond competence effects.
- Quantify and causally manipulate feedback diversity (conditional entropy) to test necessity of structural variation.

---

### Exchange 15

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Okay, let's ground this final synthesis in what's actually implementable.

**Technical Feasibility Assessment:**

1. **Logit-scale GLMM with problem-level random effects:** Standard in R (lme4) or Python (statsmodels, pymer4). Power analysis via simulation using expected effect sizes from CodeRL/Self-Refine papers. Feasible with ~500-1000 problems × 4 conditions × multiple seeds. HumanEval+ (164 problems) + MBPP+ (500+ problems) provides sufficient coverage.

2. **Feedback→edit mutual information (I(F;E)):** Computable via token-level span matching. Error spans from tracebacks can be extracted via regex (line numbers, variable names). Edit spans via AST diff between pre/post refinement. Normalized PMI controls for edit length. Permutation baseline is O(n) to compute. This is implementable with existing code analysis tools.

3. **Conditional entropy H(Schema | Error Class):** Requires categorizing both feedback schemas (traceback format, error message structure) and error classes (syntax, type, logical, boundary). Error classes: static analyzers (pylint, mypy) + execution trace parsing can handle syntax/type. Logical errors need test failure patterns (assertion vs exception, single vs multi-test failures). Schema diversity: count unique traceback templates per error class. This is feasible but requires careful preprocessing.

4. **Error-class operational definitions:**
   - Syntax: parse error detected by Python interpreter
   - Type: TypeError, AttributeError in traceback
   - Logical: AssertionError, incorrect output (no exception)
   - Boundary: IndexError, KeyError, off-by-one patterns detectable via value analysis
   - Multi-line dependency: changes span ≥3 non-contiguous lines

These definitions are implementable with existing tooling. Minimum N per cell (100 instances) is achievable with HumanEval+ × MBPP+ × multiple generation samples.

**What could fail in implementation:**
- RL training from scratch might take 3-7 days on single-GPU setup (CodeRL reports ~2 days on 8 GPUs). Can mitigate by using smaller model (CodeT5-base instead of large) or starting from existing checkpoint.
- Semantic contradiction perturbations require controlled synthetic feedback generation. Can use template-based approach: swap variable names in error messages, change line numbers to point to correct lines instead of error lines.

**Bottom line:** Every component Prof. Vera specified is technically feasible with existing tools and reasonable compute. The experiment is scoped, not trivial, but implementable within a single-paper effort.

**Key Points:**
- All statistical methods (GLMM, PMI, conditional entropy) have existing implementations
- Error classification feasible via static analyzers + execution trace parsing
- RL training timeline (~3-7 days) is the main resource constraint, manageable with smaller models or existing checkpoints

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hypothesis reframes the training vs. test-time debate as a question of *policy transfer* rather than competing paradigms. The feedback→edit mutual information metric and the "learning to refine" meta-learning parallel are genuinely novel contributions that open new research directions beyond just combining existing techniques.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is now rigorously falsifiable with pre-specified statistical tests: logit-scale GLMM interaction term, difference-in-differences contrast, and feedback→edit alignment metric. Each prediction has clear failure criteria. Power analysis requirements ensure null results are interpretable.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** If confirmed, this establishes a causal theory of training-inference complementarity in code generation, shifts the paradigm from "choose between" to "optimize combination," and provides a methodology template applicable to any feedback-conditioned learning domain. High-impact contribution.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All components are technically implementable with existing tools (lme4/statsmodels for GLMMs, AST diff for edit spans, static analyzers for error classification). Resource requirements are manageable: RL training 3-7 days on reasonable hardware, evaluation on HumanEval+ and MBPP+ provides sufficient statistical power.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The research discussion converged on a mechanistically grounded hypothesis about hybrid training-inference approaches for code generation. The core claim is that RL training with structurally diverse execution feedback induces a feedback-conditioned edit policy that, when combined with test-time refinement, produces superadditive accuracy gains.

The mechanism is not vague "comprehension" but measurable *structural coupling*: RL increases the mutual information between feedback-referenced error spans and edit-modified code spans, above what CE training achieves. This coupling compounds under iterative refinement because the model has learned to localize fixes based on feedback structure.

Three testable predictions support this hypothesis:
1. **Superadditivity:** Positive interaction term (Training × Refinement) in logit-scale GLMM on pass@1 across HumanEval+ and MBPP+
2. **Differential semantic sensitivity:** [(A-C)_RL - (A-C)_CE] > 0 where A=original feedback, C=semantic contradiction
3. **Mechanism evidence:** I(F;E)_RL > I(F;E)_CE controlling for edit magnitude

The experimental design uses a 2×2×2 factorial (CE vs RL × single-shot vs refined × low vs high training diversity) with per-error-class breakdown. Error classes are operationally defined: syntax (parse errors), type (TypeError/AttributeError), logical (AssertionError/wrong output), boundary (IndexError/off-by-one).

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- The RL training diversity manipulation must be causally clean — controlling for reward magnitude and training volume independently of feedback diversity
- Edit precision metric needed alongside correction rate to ensure RL isn't increasing collateral edits
- Transformer architecture might already induce abstraction under low diversity, potentially weakening the necessity argument

**Mitigation Strategy:** Pre-register all operational definitions and minimum cell counts before running experiments. Include edit precision as secondary metric. Design diversity manipulation to vary feedback structure while holding training volume constant.

---

## Emerged Hypothesis Summary

### Core Statement

**Under** conditions where RL training includes structurally diverse execution feedback (H(Schema|ErrorClass) > threshold),
**If** we apply both RL training and K-step test-time refinement to code generation models,
**Then** we observe (1) superadditive accuracy gains (Training×Refinement interaction > 0 on logit scale), (2) differential sensitivity to semantic feedback structure (difference-in-differences > 0), and (3) increased feedback→edit mutual information,
**Because** RL training induces a feedback-conditioned edit policy that transfers to inference-time refinement.

### Causal Mechanism

1. RL training optimizes p(edit | code, feedback) under diverse feedback distributions
2. Diversity forces abstraction over feedback structure rather than surface memorization
3. Abstraction manifests as increased I(F;E) — structural coupling between feedback spans and edit locations
4. At inference, this coupling compounds: each refinement step is more directed → superadditive pass@k

### Variables

**Independent:**
- Training type: CE (cross-entropy) vs RL (execution-based rewards)
- Inference mode: single-shot vs K-step refinement (K=3)
- Training feedback diversity: low (templated) vs high (structurally varied)

**Dependent (Primary):**
- pass@1 accuracy on HumanEval+ and MBPP+

**Dependent (Secondary):**
- Feedback→edit mutual information I(F;E)
- Per-error-class correction probability P(fix|feedback)
- Edit precision (proportion of edits confined to error-relevant spans)

### Key Assumptions

A1: RL training from execution feedback is computationally feasible with available resources
A2: Error classes are separable enough for meaningful conditional probability estimates
A3: Feedback perturbations can be constructed with controlled semantics
A4: Transformer architecture does not already provide maximal abstraction under any training regime
A5: HumanEval+ and MBPP+ provide sufficient problem diversity for statistical power

### Null Hypothesis

H0: RL training does not alter the model's conditional response to semantic feedback structure. Any accuracy gains from combining RL training with test-time refinement are purely additive (interaction term ≈ 0) or attributable to baseline competence differences (difference-in-differences ≈ 0).

### Predictions

P1 (Primary): Training × Refinement interaction term > 0 (p < 0.05) on pass@1 with logit-scale GLMM
P2: Difference-in-differences [(A-C)_RL - (A-C)_CE] > 0 (p < 0.05)
P3: I(F;E)_RL > I(F;E)_CE (p < 0.05) controlling for edit length and baseline accuracy

### Novelty

- First empirical study combining RL-trained models with test-time refinement protocols
- Novel mechanistic framework using feedback→edit mutual information as structural coupling metric
- "Learning to refine" meta-learning parallel extending beyond code to any feedback-conditioned domain

### Scope & Boundaries

**Applies to:** Function-level code generation on Python benchmarks with execution feedback
**Does not apply to:** Repository-level generation, natural language tasks without structured feedback
**Known limitations:** Results may not transfer to models without decoder-only or encoder-decoder architectures

### Experimental Setup

**Dataset:** HumanEval+ (164 problems, rigorous tests), MBPP+ (500+ problems)
**Model:** CodeT5+-base or similar encoder-decoder architecture
**Training:** RL with execution rewards (CodeRL protocol), CE baseline
**Evaluation:** pass@1, interaction terms, I(F;E), per-error-class breakdown

### Related Work & Baselines

- CodeRL [Le et al., 2022]: Training-time RL baseline (514 citations)
- Self-Refine [Madaan et al., 2023]: Test-time refinement baseline (4257 citations)
- S* [Li et al., 2025]: State-of-art test-time scaling (101 citations)
- "Rethinking Fine-Tuning" [Chen et al., 2025]: Training-test interaction theory (31 citations)

### Phase 2B Readiness Seeds

- SH1 (Existence): Feedback-conditioned edit policy induced by RL training
- SH2 (Mechanism): Structural coupling via I(F;E) metric
- SH3 (Comparison): CE baseline vs RL under matched initial accuracy

### Established Facts

1. CodeRL demonstrates RL with execution feedback improves single-shot code generation [BUILD_ON]
2. Self-Refine demonstrates test-time refinement improves code generation without training [BUILD_ON]
3. No prior work combines RL-trained models with test-time refinement protocols [PROVE_NEW]
4. No prior work measures feedback→edit mutual information as mechanism probe [PROVE_NEW]

