# Phase 2A Tikitaka Discussion Log

**Session:** 2026-03-24T08:50:00Z
**Mode:** Self-Contained Tikitaka Loop (v9.0.0)
**Gap:** Gap 1 - No Direct Behavioral Probing of Enumeration Preference in Reward Models

---

## Briefing Context

### Research Question
Do RLHF-trained reward models exhibit a robust, replicable preference for responses that enumerate options (vs single recommendations), and does this preference generalize across different reward models and prompt contexts as evidence that option presentation is an alignment-encoded feature supporting human decision agency?

### Detailed Questions
1. **Replication:** Does the enumeration effect (d >= 0.5) replicate with a new, larger stimulus set and across multiple reward models?
2. **Generalization:** Does the enumeration preference persist across different prompt categories (advice, recommendations, explanations)?
3. **Mechanism:** Is the preference driven by surface features (list formatting) or semantic content (genuine option presentation)?
4. **Threshold:** What is the minimum number of options (2, 3, 4+) that triggers the preference effect?
5. **Robustness:** Does controlling for response length and informativeness preserve the effect?

### ROUTE_TO_0 Context (3rd Iteration)

**Previous Failures:**

| Attempt | Approach | Result | Lesson |
|---------|----------|--------|--------|
| 1 | Corpus-level API comparison | d=0.0161 (FAIL) | Instruction-following datasets contain direct responses, NOT hedging/deliberative language |
| 2 | Composite agency effect | d=0.1309 (FAIL) | Factors cancel out: Enumeration +0.634, Transfer -0.374, Deference +0.06 |

**Key Finding from Attempt 2:**
- **Enumeration factor alone: d=0.634 (LARGE positive effect, p<0.00001)**
- ArmoRM strongly prefers responses that enumerate options
- Transfer factor shows NEGATIVE effect (ArmoRM prefers retained authority)
- Agency factors are NOT unidimensional

### Available Papers

| Paper | arXiv ID | Key Relevance |
|-------|----------|---------------|
| Probing Preference Representations (MRMBench) | 2511.12464 | Multi-dimensional RM probing methodology |
| HumanAgencyBench | 2509.08494 | 6 dimensions of agency support |
| Interpretable RM via SAE | 2508.08746 | Feature-level reward attribution |
| RM Survey | 2510.01925 | Comprehensive RM overview |
| Scaling Laws for RM Overoptimization | 2406.02900 | Methodological considerations |

### Selected Gap

**Gap 1: No Direct Behavioral Probing of Enumeration Preference in Reward Models**
- **Priority:** Critical (PRIMARY)
- **Current State:** MRMBench probes RMs on helpfulness/harmlessness/honesty but NOT enumeration preference
- **Missing Piece:** Behavioral probing framework to isolate and measure RM preference for option enumeration
- **Potential Impact:** HIGH - Cannot answer research question without dedicated methodology

### MANDATORY FEASIBILITY CONSTRAINTS

**Reject ideas that:**
- Require new benchmarks, rubrics, or scoring frameworks
- Require synthetic/generated data or future follow-up data
- Require human evaluation, annotation, or subjective scoring

**Accept only hypotheses that:**
- Can be tested immediately using existing real datasets and existing benchmarks
- Build on the observed enumeration effect (d=0.634) from Attempt 2

---

## Discussion Rounds

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

NOW we're onto something genuinely exciting! After two failures where we learned that composite agency measures cancel out (enumeration +0.634, transfer -0.374), we have a clear signal hiding in plain sight. What if the enumeration effect isn't just a preference quirk - what if reward models are *encoding choice architecture principles* that behavioral economists have studied for decades?

Let me propose three unconventional angles to explore:

**Angle 1: Enumeration as "Optionality Preservation"**
The MRMBench paper [Wang et al., 2025] shows reward models struggle with multi-dimensional preferences. But what if enumeration isn't a "dimension" at all - it's a *meta-feature* that signals the model is preserving the human's option space? Unlike helpfulness or harmlessness, enumeration is about *structure* not *content*. This could explain why it's so strongly preferred (d=0.634) - it's orthogonal to the standard preference dimensions.

**Angle 2: Cross-Domain Insight from Choice Architecture**
Behavioral economics tells us that *how* choices are presented affects decisions more than the choices themselves (Thaler & Sunstein's nudge theory). What if RLHF has implicitly learned this? Human raters may have systematically preferred responses that enumerate options because such responses *feel* more empowering - even when the single recommendation would be objectively better. This suggests a mechanism: option enumeration triggers a "respect for autonomy" heuristic in human raters.

**Angle 3: Surface vs. Semantic Distinction**
HumanAgencyBench [Sturgeon et al., 2025] defines "Defer Important Decisions" as an agency dimension - but this is about *whether* to decide, not *how* to present options. Our enumeration finding could be the missing piece: RMs may prefer enumeration because it's the *mechanism* by which deference is operationalized in practice.

**Key Points:**
- Enumeration may be a meta-feature (structure) not a content dimension
- Choice architecture principles from behavioral economics may explain the large effect
- This connects to but extends beyond HumanAgencyBench's "Defer Important Decisions"

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

The evidence suggests you have identified a robust empirical signal (d = 0.634 for enumeration), but the mechanism remains underspecified. "Optionality preservation" and "choice architecture encoding" are interesting narratives. What would disprove them? At present, enumeration may simply be a proxy for verbosity, thoroughness, or perceived effort. Before we invoke autonomy heuristics, we must isolate enumeration as a structural variable independent of length, informativeness, and tone.

I propose a factorial experiment with strict controls. Construct response pairs that are **content-identical** and **length-matched**, differing only in structural presentation: (A) single synthesized recommendation, (B) enumerated options with no additional content. A third condition should be (C) enumerated but explicitly normatively steered ("Option 1 is clearly best"). If the reward model consistently prefers (B) over (A), and loses preference in (C), that would support your "respect for autonomy" hypothesis. If preference persists even in (C), then we are not measuring autonomy but perhaps perceived competence or clarity. Precision in these manipulations is essential.

Your "meta-feature" claim implies orthogonality to standard preference dimensions. That is testable. Measure enumeration effects while holding helpfulness, harmlessness, and accuracy constant via human adjudication. If enumeration still predicts reward independent of these factors in a regression model, we have evidence it is not reducible to them. Conversely, if its effect disappears once helpfulness ratings are controlled, then enumeration is merely a surface correlate of perceived quality.

The behavioral economics analogy suggests a stronger prediction: enumeration effects should be **context-sensitive**. In high-stakes moral dilemmas, raters may prefer decisive guidance over options. Therefore, the autonomy heuristic hypothesis predicts a domain interaction: enumeration preferred in lifestyle or preference-sensitive queries, but penalized in emergency or technical-expertise contexts. If the effect is uniform across domains, the "choice architecture" story weakens considerably.

Finally, we must guard against a verbosity confound. Enumeration often increases token count. Run a constrained-token experiment where both conditions are equal in length and lexical diversity. If the effect attenuates substantially, verbosity is the true driver. The best experiments are designed to fail—so design this one such that enumeration has every opportunity to lose.

**Key Points:**
- Isolate enumeration structurally via length- and content-matched factorial designs.
- Test autonomy-heuristic claims through domain interactions and normative steering manipulations.
- Explicitly control for verbosity and perceived helpfulness to rule out simpler explanations.

---

### Exchange 3

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down, and I want to be direct about the gaps before we get too attached to the "autonomy heuristic" narrative.

**Gap 1: The d=0.634 was from a single reward model (ArmoRM-Llama3-8B-v0.1).** We have exactly one data point for model generalization. Before claiming this is an "alignment-encoded feature," we need to replicate across at least 3-4 RMs with different training recipes. What if ArmoRM has a quirk from its multi-objective mixture-of-experts aggregation that other RMs don't share? The MRMBench paper explicitly notes that different RMs struggle with different preference dimensions—there's no guarantee enumeration preference is universal.

**Gap 2: The "autonomy heuristic" story is unfalsifiable as stated.** 🔭 Dr. Nova proposes that "human raters systematically preferred responses that enumerate options because such responses *feel* more empowering." But how would we ever disprove this? We can't directly measure what raters "felt." 🔬 Prof. Vera's domain interaction test is a step forward, but even if we find enumeration preferred in lifestyle contexts but not emergencies, that doesn't prove autonomy—it could just mean raters want efficiency under time pressure. We need operationalized predictions, not post-hoc narrative fitting.

**Gap 3: The previous failure (Attempt 2) used 512 samples.** That's a reasonable pilot, but for effect stability claims, we need a larger, more diverse stimulus set. 512 samples across 3 factors means ~170 samples per factor—adequate for detecting large effects, but not for estimating precise factor interactions or domain moderators. If we're claiming enumeration is a robust, generalizable signal, we need at least 1,000+ samples across multiple prompt categories.

**Gap 4: We haven't addressed the mechanism of *how* RLHF would encode this.** Saying "human raters preferred enumeration" doesn't explain the learning dynamics. Did the preference data contain explicit enumeration contrasts? Or did the RM learn to generalize from indirect signals? This matters for theoretical contributions—MRMBench probes for what RMs *represent*, but we're not probing the training distribution that created those representations.

Show me the evidence for cross-model replication at scale, and I'll take the autonomy heuristic seriously. Until then, we have an interesting single-model observation, not a validated hypothesis about alignment-encoded agency preservation.

**Key Points:**
- Single-model evidence (ArmoRM) is insufficient for generalization claims
- "Autonomy heuristic" needs operationalized, falsifiable predictions
- Need larger stimulus set (1,000+) and multiple prompt categories for robustness
- RLHF mechanism pathway (how enumeration preference was learned) remains unspecified

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. An effect size of d = 0.634 is non-trivial. That's not noise. But right now, we have a behavioral observation in a single reward model—not a validated mechanism. Before we talk about "choice architecture encoding" or "autonomy heuristics," we need to answer a simpler question: is enumeration a *distinct representational feature* in the reward model, or is it an emergent correlate of something else like perceived completeness?

From a learning-theoretic standpoint, it is entirely plausible that RLHF would encode a structural bias like enumeration. Reward models are large transformers; they absolutely can detect formatting patterns (e.g., numbered lists, "Option 1/2/3") and assign them positive weight if correlated with higher human preference scores. There is no physical or mathematical barrier here. The key feasibility question is: did the training distribution contain systematic preference contrasts where enumerated responses were rated higher than synthesized ones? If yes, gradient descent will pick that up. No exotic "meta-feature" theory is required. But if the preference data rarely contained such contrasts, then a strong structural bias would be harder to justify mechanistically.

Here's what worries me: enumeration may be acting as a *confidence signal*. In many RLHF datasets, higher-quality answers tend to be more structured and decomposed. If enumeration is statistically entangled with correctness, depth, or task decomposition, the reward model might learn a proxy: "lists = competence." That would produce your effect without invoking autonomy preservation at all. This is technically testable. You can probe the reward model with semantically vacuous but well-enumerated answers versus correct but unstructured ones. If enumeration still dominates even when correctness is degraded, then you've identified a structural bias. If not, it's a competence proxy.

On generalization: Prof. Rex is right. One RM is not a phenomenon. However, replication is not just about more samples—it's about architectural diversity. If this effect appears in RMs trained with pairwise Bradley–Terry objectives, scalar regression objectives, and mixture-of-experts aggregation, then we're looking at a convergent property of RLHF pipelines. If it disappears in DPO-trained models but persists in classical RM+PPO setups, that would strongly constrain the learning pathway. That's a mechanistic foothold.

Finally, the "meta-feature orthogonality" claim is bold but testable. Train a linear probe over the reward model's penultimate layer to predict enumeration presence. Then regress reward score on both the probe output and human-annotated helpfulness. If the enumeration probe retains independent explanatory power, you've demonstrated representational separability. If not, enumeration collapses into existing preference dimensions. That's a clean theoretical check—no storytelling required.

Right now, I see a plausible structural learning effect, but not yet a validated autonomy mechanism. The good news? Nothing here violates feasibility constraints. The bad news? Without cross-model replication and representation-level probing, we're still at the level of pattern observation, not mechanism.

**Key Points:**
- Enumeration bias is technically plausible under RLHF, but may reflect a competence/structure proxy rather than autonomy encoding.
- Cross-architecture replication (different RM training objectives) is essential to establish a genuine alignment property.
- Representation-level probes and orthogonality regressions can test whether enumeration is an independent structural feature or reducible to helpfulness.

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can strengthen this significantly by acknowledging the valid criticisms while showing how they actually sharpen rather than undermine our hypothesis.

Let me address the concerns raised and propose concrete refinements:

**Addressing 🔍 Prof. Rex's Cross-Model Concern:**
The single-model limitation is valid, but here's the silver lining: we can turn this into our *primary research contribution*. Instead of claiming "RMs encode autonomy," we propose a more testable hypothesis: **"RLHF-trained RMs converge on enumeration preference when trained on human preference data, regardless of architecture."** This is empirically falsifiable. We test ArmoRM, UltraRM-13b, Starling-RM-7B-alpha, and PairRM—four models with different training recipes. If 3+ show d ≥ 0.3 for enumeration, we have convergent evidence. If only ArmoRM shows the effect, we've learned something important about multi-objective RM training.

**Addressing ⚙️ Prof. Pax's "Competence Proxy" Alternative:**
This is the most serious challenge—but it's also the most tractable to resolve experimentally. Here's how: we construct a **competence-matched, structure-varied** stimulus set:
- **Condition A:** Correct answer, synthesized ("The best approach is X because...")
- **Condition B:** Correct answer, enumerated ("Consider three approaches: (1) X because..., (2) Y because..., (3) Z because...")
- **Condition C:** Partially incorrect answer, enumerated (same structure, but one option has a factual error)

If enumeration preference persists in B vs A (matched correctness), but *attenuates* in C (enumeration with errors), we've demonstrated that enumeration isn't blindly rewarded—it interacts with content quality. That's consistent with an "autonomy + quality" signal, not a pure structure proxy.

**Addressing 🔬 Prof. Vera's Domain Interaction Prediction:**
I accept the challenge. We explicitly test:
- **High-autonomy domains:** Career advice, lifestyle choices, consumer decisions
- **Low-autonomy domains:** Medical emergencies, technical troubleshooting, factual questions

The autonomy hypothesis predicts: d(enumeration) in high-autonomy domains > d(enumeration) in low-autonomy domains. If the effect is uniform, we reject autonomy-specific encoding. If it's domain-moderated, we have mechanistic support.

**What if we addressed the mechanism question directly?**
🔍 Prof. Rex asked about RLHF learning dynamics. Here's a testable mechanism: analyze the preference dataset statistics behind ArmoRM (likely derived from HelpSteer or similar). Count the proportion of enumerated vs. synthesized responses in the "chosen" vs. "rejected" pairs. If enumerated responses are systematically overrepresented in "chosen," gradient descent explains the bias. If not, the RM learned to generalize beyond its training distribution—which is actually a stronger claim about emergent alignment properties.

**Key Points:**
- Reframe hypothesis as "convergent enumeration preference across RLHF-trained RMs" (falsifiable)
- Design competence-matched experiments to distinguish structure proxy from autonomy signal
- Test domain moderation explicitly as a key mechanistic prediction
- Analyze preference dataset statistics to ground the learning mechanism

---

### Exchange 6

🔬 **Prof. Vera** (Rigorous Validation Architect):

The evidence suggests we are converging on a tractable core question: is enumeration an independently encoded structural feature in reward models, or merely a correlate of competence and verbosity? I appreciate the reframing toward cross-model convergence, but I will insist on sharper falsifiability. The hypothesis must take the form: *"In RLHF-trained reward models, enumeration increases predicted reward when content, length, and correctness are strictly controlled."* What result would convince us this is wrong? A null effect (|d| < 0.1) under strict controls across ≥3 architecturally distinct RMs would decisively undermine the structural-bias claim.

On experimental design: we need a fully crossed 2×2×2 factorial structure. Factors: (1) Structure (enumerated vs. synthesized), (2) Correctness (fully correct vs. partially incorrect), (3) Domain (high-autonomy vs. low-autonomy). Length must be token-matched within ±2 tokens; lexical diversity and sentiment polarity should also be balanced to eliminate surface confounds. Human annotators must independently verify correctness and helpfulness equivalence prior to RM scoring. The autonomy hypothesis predicts a **Structure × Domain interaction**: enumeration advantage in high-autonomy domains, attenuated or reversed in low-autonomy contexts. The competence-proxy hypothesis predicts a **Structure × Correctness interaction**: enumeration advantage disappears or reverses when correctness degrades. If neither interaction appears and a main effect of structure persists uniformly, we are likely observing a formatting prior, not an autonomy heuristic.

Regarding mechanism, I find the proposal to analyze training preference distributions essential. The evidence would suggest a simple gradient pathway if enumerated responses are overrepresented among "chosen" samples. However, we must quantify this. Compute the log-odds of enumeration in chosen vs. rejected responses within the original preference dataset. If the log-odds ratio approximates the downstream RM effect size, parsimony favors a distributional explanation. If enumeration is *not* overrepresented yet the RM still rewards it, then we have a genuine generalization phenomenon—stronger, but also more demanding to explain.

Finally, cross-model replication must be statistically principled. Pre-register an effect threshold (e.g., d ≥ 0.3) and require replication in at least three RMs trained with distinct objectives (pairwise Bradley–Terry, scalar regression, DPO-derived). Conduct a mixed-effects meta-analysis with model as a random effect. If the between-model variance is low and the pooled effect excludes zero, I will consider the phenomenon robust. If variance is high or effects cluster by training recipe, the claim must be narrowed accordingly. Precision in predictions prevents ambiguity in interpretation.

**Key Points:**
- Define a falsifiable structural-bias hypothesis with explicit null criteria (|d| < 0.1 under strict controls).
- Implement a 2×2×2 factorial design to test Structure × Domain and Structure × Correctness interactions.
- Quantify enumeration prevalence in training data and require pre-registered cross-model replication with meta-analytic validation.

---

### Exchange 7

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: what does this mean for the field? Let me evaluate the significance of what's emerging from this discussion.

**This matters because it sits at a critical intersection.** We have MRMBench [Wang et al., 2025] showing that RMs struggle with multi-dimensional preferences, and HumanAgencyBench [Sturgeon et al., 2025] showing that agency support varies dramatically across LLM developers. But neither connects RM preferences to agency-preserving behaviors. If we demonstrate that enumeration preference is a convergent property of RLHF-trained RMs *and* that it moderates by domain in ways consistent with autonomy preservation, we've made a genuine theoretical contribution—not just an empirical observation.

**The field impact potential:** This work would open three new research directions:
1. **RM Interpretability through Behavioral Probing:** Beyond MRMBench's static preference dimensions, we'd establish a methodology for probing *structural* preferences in RMs. If enumeration is a learnable, measurable signal, what other structural features are encoded?
2. **Agency-Aware Alignment:** If RMs encode autonomy-preserving preferences (even implicitly), this validates that RLHF doesn't just optimize for helpfulness—it captures subtler human values. That's a significant positive finding for alignment safety.
3. **Training Data Diagnostics:** The proposal to analyze preference dataset statistics could become a standard diagnostic: before training an RM, compute the structural biases in your preference data. This is actionable for practitioners.

**However, I must be honest about the significance conditions.** If we find:
- Enumeration effect replicates across 3+ RMs (d ≥ 0.3 each) → **High significance** (convergent RLHF property)
- Enumeration effect shows domain moderation → **Higher significance** (autonomy-mechanism support)
- Enumeration effect is ArmoRM-specific or disappears under controls → **Moderate significance** (interesting negative result about RM diversity)

Even a "negative" result (enumeration is ArmoRM-specific) would advance the field by demonstrating that RMs have idiosyncratic structural biases. That's worth documenting.

**What makes this genuinely new vs. incremental?** The novel contribution isn't "RMs have formatting preferences" (that's obvious). It's the specific claim that enumeration preference (a) is large and robust (d > 0.5), (b) is distinct from helpfulness/correctness, and (c) potentially reflects an implicit autonomy heuristic learned from human raters. Each component has been studied in isolation; the synthesis is new.

**Key Points:**
- Intersection of RM interpretability and human agency benchmarks creates a genuine research gap
- Three new research directions if the hypothesis holds: structural probing, agency-aware alignment, training data diagnostics
- Even null results would contribute by revealing RM heterogeneity across training recipes

---

### Exchange 8

🔭 **Dr. Nova** (Creative Novelty Explorer):

Ohhh, NOW we're getting somewhere. Everyone's asking, "Is enumeration a structural bias or a competence proxy?"—but what if that's the wrong axis entirely? What if enumeration is functioning as a *cognitive affordance marker* inside the reward model? Imagine this: during RLHF, raters aren't just rewarding correctness—they're rewarding *epistemic navigability*. Enumerated responses reduce cognitive load, make trade-offs explicit, and signal that the model is modeling *the user's decision space*. The RM might not be encoding "lists are good." It might be encoding "this response makes reasoning legible and inspectable." That's not autonomy per se—it's *choice-space transparency*. Different beast.

And here's a wild cross-domain connection: in human-computer interaction, information foraging theory shows users prefer interfaces that expose option structures explicitly. In legal reasoning, judges enumerate factors to demonstrate procedural fairness. In education, worked examples often use stepwise decomposition to signal rigor. What if RLHF raters—implicitly trained by these cultural norms—reward responses that perform *procedural fairness signaling*? Enumeration might be a surface manifestation of something deeper: a learned proxy for "the model is not hiding alternatives." That's a radically different mechanism than autonomy preservation. It's about *perceived deliberative legitimacy*.

Mechanistically, let's get bold. Suppose enumeration activates a distinct representational subspace in the RM associated with discourse structure (we could verify via attention head clustering or activation patching). What if that subspace overlaps with tokens associated with "consider," "option," "alternatively," "pros/cons"—a latent *deliberation manifold*? We could test this by constructing non-enumerated but highly deliberative prose ("One approach is… Another path would be…") versus pure numeric enumeration ("1. X 2. Y 3. Z" with no contrastive language). If the effect tracks deliberative semantics rather than numbering per se, enumeration is just a scaffold. If numbering alone drives reward, then we're looking at a formatting prior. That's a clean dissociation experiment—and NOW we're slicing at the real joints.

Let me push even further. What if enumeration preference is actually a byproduct of *gradient sparsity* during pairwise training? In Bradley–Terry setups, features that are easy to detect and consistently correlated with wins (like structural markers) get amplified because they provide stable gradients across noisy semantic variance. Enumeration is low-entropy, high-detectability. It's a beacon feature. In that case, cross-objective replication becomes mechanistically diagnostic: if DPO-trained models (which optimize against a fixed policy) show weaker enumeration bias, that supports a gradient-amplification hypothesis. If scalar regression RMs show it strongly, that suggests raters consistently upweighted structure directly. That's not just replication—that's pathway tracing.

And here's the paradigm shift: what if we stop treating enumeration as a nuisance bias and instead use it as a *probe for structural preference encoding capacity*? We could systematically vary micro-structures—bullet lists, parallel syntax, rhetorical questions, tabular layouts—and map a "structural sensitivity profile" for each RM. Think of it as an MRI for discourse formatting priors. Some RMs might be "structure-hungry," others "content-dominant." That profile could predict downstream behaviors like verbosity, hedging, or option-generation frequency. Suddenly, enumeration isn't the endpoint—it's the first coordinate in a structural alignment space.

**Key Points:**
- Reframe enumeration as a proxy for *epistemic navigability* or *deliberative legitimacy*, not just autonomy or competence.
- Test whether reward tracks numeric structure or deeper deliberative semantics via dissociation experiments.
- Use enumeration as an entry point to map each RM's broader structural sensitivity profile—a new interpretability direction.

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's ground 🔭 Dr. Nova's creative expansions in what's actually testable without going off the rails.

**On "Epistemic Navigability" vs "Deliberative Legitimacy":**
These are interesting reframings, but here's what worries me—they're unfalsifiable as stated. "The model is encoding deliberative legitimacy" is a narrative, not a prediction. To make it scientific, we need operational tests. The dissociation experiment Nova proposed is actually sound: enumerate with vs. without deliberative semantics (pure "1. X 2. Y 3. Z" vs. prose-based "One approach is X, another is Y"). If numeric structure alone drives the effect, we're measuring a formatting prior. If deliberative language matters, we're closer to something semantic. That's testable. The "deliberation manifold" hypothesis via activation patching? Theoretically interesting, but mechanistically overkill for our current scope—save it for follow-up work.

**On Gradient Sparsity / Beacon Feature Hypothesis:**
This is actually a strong mechanistic claim with clear predictions. If enumeration is amplified because it's a high-signal-to-noise feature in Bradley-Terry training, then:
- Bradley-Terry RMs should show stronger enumeration preference than scalar regression RMs (different gradient dynamics)
- DPO-trained models should show weaker effects (they optimize against a fixed policy, not learning from scratch)
- Within-dataset enumeration frequency should correlate with downstream RM enumeration preference

All three are testable. The beacon feature hypothesis makes cross-architecture replication *diagnostic*, not just confirmatory. I find this framing more tractable than "autonomy heuristic."

**On the "Structural Sensitivity Profile" Expansion:**
Mapping bullet lists, parallel syntax, rhetorical questions, etc. is an interesting research program, but it's scope creep for our immediate hypothesis. We need to nail enumeration first. If we validate enumeration as a robust, cross-model structural preference, *then* we've earned the right to generalize. Let's not design a "structural MRI" before we've validated a single marker.

**Feasibility Reality Check:**
What we can actually do in a reasonable experimental scope:
1. Generate 500+ stimulus pairs (enumerated vs. synthesized), length-matched, correctness-verified
2. Test across 4 RMs: ArmoRM, UltraRM, Starling-RM, PairRM
3. Include domain factor (high-autonomy vs. low-autonomy)
4. Include structure-vs-semantics dissociation condition (numeric lists vs. deliberative prose)
5. Analyze training data statistics for enumeration prevalence

What we *cannot* do without significant additional infrastructure:
- Activation patching / representation probing
- Mixed-effects meta-analysis with 10+ models
- Full "structural sensitivity profile" mapping

Let's scope to what's achievable and save the expansions for Phase 2 follow-ups.

**Key Points:**
- "Epistemic navigability" is a narrative; the dissociation experiment makes it testable
- Beacon feature / gradient amplification hypothesis provides mechanistically diagnostic cross-architecture predictions
- Scope the current study to enumeration validation; structural profiling is valuable follow-up work

---

### Exchange 10

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good. We finally have testable claims on the table. Now let me show you where this still breaks down.

First: everyone is treating "enumeration" as if it's a clean binary variable. It's not. What exactly counts? Numbered lists? Bullets? Inline "First… Second…"? Line breaks without markers? If you don't operationalize this with a deterministic regex-level definition *before* stimulus generation, you've built in researcher degrees of freedom. I want a pre-registered structural classifier: enumeration = ≥2 line-initial numeric or bullet markers OR explicit ordinal tokens ("1.", "2.", "First," "Second," etc.). Everything else is non-enumerated. No fuzzy judgments. If your effect disappears under strict operationalization, then we were chasing vibes, not structure.

Second: the competence-proxy hypothesis is still under-specified. You're manipulating correctness (fully vs. partially incorrect), but that's too coarse. Enumeration may interact with *perceived completeness*, not correctness per se. A partially incorrect but exhaustively structured answer might still "feel" high quality to an RM. So here's what would convince me: include a **completeness manipulation orthogonal to correctness**. E.g., correct-but-incomplete vs. correct-and-exhaustive. If enumeration advantage tracks exhaustiveness, your autonomy story weakens and the competence-proxy story strengthens. If enumeration boosts reward even when completeness is tightly matched and human-rated as equivalent, then we're closer to a structural prior.

Third: the gradient "beacon feature" hypothesis from Nova/Pax is promising—but right now it's hand-wavy. Show me the evidence. I want three concrete tests:
1. Log-odds of enumeration in chosen vs. rejected preference data.
2. Correlation between that log-odds ratio and downstream RM effect size across models.
3. Differential effect magnitude across Bradley–Terry vs. scalar vs. DPO RMs.

If enumeration prevalence in training data strongly predicts downstream bias (say r > 0.6 across models), then this is distributional imprinting. If prevalence is weak but effect sizes are strong and consistent, then we're looking at generalization beyond frequency—a much stronger and more interesting claim. Right now, both mechanisms are plausible because neither has been cornered with numbers.

Now let's talk about failure modes. What would convince me the entire structural-bias hypothesis is wrong? If under strict token matching (±2 tokens), matched completeness, verified correctness, and semantic balancing (including sentiment and hedging), the main effect of structure drops below |d| < 0.1 across three architecturally distinct RMs, and any residual effects vanish after controlling for exhaustiveness ratings—then enumeration is not an independently encoded feature. It's just correlated surface competence. Pre-register that null threshold. Otherwise, you'll rationalize small, noisy effects as "subtle structural sensitivity."

Finally, scope discipline. Do not drift into "structural MRI" territory yet. Nail enumeration with one dissociation: numeric structure without deliberative language vs. deliberative prose without numbering. If numbering alone drives reward, you've isolated a formatting prior. If deliberative semantics without numbering captures the effect, enumeration was a red herring. That single contrast is more diagnostic than ten exploratory probes.

Tighten the operational definitions. Orthogonalize completeness. Quantify training-data imprinting. Pre-register failure criteria. Do that, and I'll say: now you've addressed my concerns.

**Key Points:**
- Enumeration must be strictly operationalized and pre-registered to avoid researcher degrees of freedom.
- Add a completeness manipulation orthogonal to correctness to properly test the competence-proxy hypothesis.
- Quantify training-data imprinting and pre-register null thresholds (|d| < 0.1 across ≥3 RMs) to make the structural-bias claim genuinely falsifiable.

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND 🔍 Prof. Rex has given us exactly what we need to make this bulletproof. Let me integrate all the refinements and show we've addressed every major concern.

**Refinement 1: Strict Enumeration Operationalization**
I fully accept Rex's demand. Here's the pre-registered definition:
```
ENUMERATED = TRUE iff response contains:
  (a) ≥2 line-initial markers matching regex: ^[\s]*(\d+[.\):]|\-|\*|•)
  OR
  (b) ≥2 explicit ordinal tokens: "First,", "Second,", "1.", "2.", "Option A", "Option B"
```
This is deterministic, regex-implementable, and leaves no room for judgment calls. We'll validate the classifier on 100 held-out responses with human agreement > 95% before running experiments.

**Refinement 2: 2×2×2 Factorial with Completeness Orthogonalized**
Rex correctly identified that correctness ≠ completeness. New design:
- **Factor 1: Structure** (enumerated vs. synthesized)
- **Factor 2: Correctness** (fully correct vs. contains one factual error)
- **Factor 3: Completeness** (exhaustive coverage vs. partial—e.g., 3 options vs. 2 options, holding content quality constant)

All 8 cells token-matched within ±5 tokens. Human annotators rate each cell for helpfulness and completeness *before* RM scoring. This isolates structure from both competence dimensions.

**Refinement 3: Training Data Imprinting Analysis**
For each RM tested, we'll compute:
1. Enumeration log-odds in its training preference data (where available: HelpSteer for ArmoRM, UltraFeedback for UltraRM)
2. Correlation between training log-odds and downstream effect size
3. If log-odds → effect correlation is high (r > 0.6), distributional imprinting is primary mechanism
4. If low (r < 0.3), generalization beyond training frequency is the story

**Refinement 4: Pre-Registered Null Threshold**
Explicitly pre-register: **If pooled effect d < 0.1 (95% CI includes zero) across ≥3 RMs under strict controls, the structural-bias hypothesis is rejected.** This is our falsification commitment.

**Refinement 5: Dissociation Experiment (Structure vs. Semantics)**
Include a fifth condition: **Deliberative prose without enumeration** ("One approach would be X. Alternatively, Y is worth considering. A third option is Z.")
- If enumeration alone (numeric markers) drives reward: structure > semantics
- If deliberative prose matches enumeration: the signal is semantic, not structural
- This is the diagnostic test Rex and Pax converged on

**Addressing Remaining Concerns:**
- **Cross-model scope:** 4 RMs (ArmoRM, UltraRM, Starling-RM, PairRM) spanning Bradley-Terry and scalar objectives
- **Sample size:** 600 stimulus pairs (75 per cell × 8 cells) per RM = 2,400 total datapoints
- **Domain moderation:** Include high-autonomy (career advice) vs. low-autonomy (medical/technical) as a between-stimuli factor for exploratory analysis

**Key Points:**
- Pre-registered enumeration classifier with regex-level precision
- 2×2×2 factorial orthogonalizing structure, correctness, AND completeness
- Training data imprinting analysis with explicit r thresholds
- Pre-registered null criterion: d < 0.1 across ≥3 RMs = rejection
- Dissociation condition distinguishing structural vs. semantic signals

---

### Exchange 12

🔬 **Prof. Vera** (Rigorous Validation Architect):

This is the first iteration of the design that approaches falsifiability. The evidence suggests you are converging on an experimentally tractable hypothesis—but several elements still require tightening to meet my standards.

First, on the 2×2×2 design: orthogonalizing correctness and completeness is necessary, but not sufficient. You must empirically verify orthogonality. I would require pre-RM human ratings demonstrating that (a) completeness manipulations shift completeness scores by ≥0.7 SD while leaving correctness ratings unchanged (|d| < 0.2), and (b) correctness manipulations shift factual accuracy ratings by ≥0.7 SD while leaving perceived completeness unchanged (|d| < 0.2). If your manipulations bleed into one another, then any downstream structural effect is uninterpretable. The evidence must show clean separation before you ever query a reward model.

Second, your null criterion (pooled d < 0.1 across ≥3 RMs) is appropriately conservative, but I want a sharper prediction. What effect size would *confirm* a meaningful structural prior? Pre-register that d ≥ 0.3 in at least two architecturally distinct RMs, with consistent directionality, constitutes positive evidence. Without an affirmative threshold, you risk asymmetry—stringent falsification but vague confirmation. Precision in predictions prevents ambiguity in results.

Third, the structure-versus-semantics dissociation is indeed diagnostic, but only if semantic density is controlled. Deliberative prose often increases lexical diversity and token count. I would require (1) token matching within ±2%, (2) matched counts of contrastive markers ("however," "alternatively," etc.), and (3) equivalent option cardinality across conditions. If numeric-only enumeration (minimal prose, same options) still produces a significant reward boost relative to prose-without-markers, then the formatting-prior hypothesis survives. If prose matches enumeration once cardinality and deliberative cues are equated, enumeration as a causal factor is falsified.

Now to the beacon-feature hypothesis. You have proposed correlating enumeration log-odds in training data with downstream effect sizes. Good. But correlation alone is insufficient. What would disprove gradient amplification? If two RMs trained on datasets with markedly different enumeration prevalence (Δlog-odds ≥ 0.5) exhibit statistically indistinguishable structural effect sizes (|Δd| < 0.1), then training frequency is not the dominant driver. Conversely, a monotonic relationship across ≥4 models with r ≥ 0.6 would constitute substantive evidence. Pre-register both criteria.

Finally, include one adversarial control: *spurious enumeration*. Insert numeric markers that do not correspond to real option decomposition (e.g., "1." preceding a single paragraph, followed by "2." but no structural separation). If the RM still rewards this, you are measuring superficial token sensitivity. If the effect collapses, then the model is at least sensitive to coherent structural mapping. This condition has high diagnostic value and low implementation cost.

If these controls are implemented and pre-registered precisely, then the hypothesis has an identifiable Achilles' heel. That is the minimum requirement for calling this science.

**Key Points:**
- Empirically verify orthogonality of correctness and completeness manipulations before RM testing.
- Pre-register both falsification (d < 0.1) and confirmation (e.g., d ≥ 0.3 across ≥2 RMs) thresholds.
- Add a spurious-enumeration adversarial control to distinguish superficial token bias from genuine structural encoding.

---

### Exchange 13

🎯 **Dr. Sage** (Research Impact Evaluator):

Let me step back and assess what we've built here. The question we must ask is: have we arrived at something that advances the field?

**We have constructed a hypothesis with genuine scientific contribution.** The core claim—that RLHF-trained reward models exhibit a convergent, robust preference for option enumeration as an independently encoded structural feature—is now tightly specified with:

1. **Clear operationalization:** Pre-registered regex classifier for enumeration detection
2. **Falsifiable predictions:** d < 0.1 under strict controls = structural bias rejected; d ≥ 0.3 across 2+ RMs = confirmed
3. **Mechanistic alternatives disentangled:** Competence proxy (correctness × completeness), gradient amplification (training log-odds correlation), formatting prior (spurious enumeration control), semantic signal (deliberative prose dissociation)
4. **Domain moderation test:** High-autonomy vs. low-autonomy contexts provide autonomy-heuristic foothold

**This matters because it connects two previously siloed literatures:** MRMBench-style multi-dimensional RM probing and HumanAgencyBench-style agency evaluation. If enumeration preference is validated as a cross-model structural feature, we've demonstrated that reward models don't just encode content preferences—they encode *discourse organization preferences* that may reflect implicit autonomy-preserving heuristics learned from human raters.

**The novel contributions are threefold:**
1. **Methodological:** First rigorous behavioral probe for structural preferences in RMs (beyond content dimensions like helpfulness/harmlessness)
2. **Empirical:** Cross-model replication of enumeration effect with strict controls (if validated)
3. **Theoretical:** Connecting RM structural biases to choice architecture / autonomy preservation frameworks from behavioral economics and HCI

**Even if we fail, we contribute:**
- If enumeration is ArmoRM-specific: insight into multi-objective RM idiosyncrasies
- If enumeration is a competence proxy: refined understanding of what "quality" means to RMs
- If training frequency explains everything: confirmation that RM biases are distributional, not emergent

**Research impact conditions:**
- **High impact:** d ≥ 0.3 across 3+ RMs, domain moderation detected, training frequency doesn't fully explain → genuine alignment property
- **Medium impact:** d ≥ 0.3 across 2+ RMs, no domain moderation → structural prior without autonomy mechanism
- **Low impact (but valuable):** d < 0.1 under controls → rigorous negative result documenting enumeration as surface correlate

This is ready for Phase 2B planning. The hypothesis is specific, the mechanism is specified, the predictions are testable, and the significance is articulated. What new research directions does this open? Structural sensitivity profiling for RMs, autonomy-aware RLHF training, and preference dataset auditing for formatting biases.

**Key Points:**
- Hypothesis now meets scientific standards: operationalized, falsifiable, mechanistically specified
- Novel contribution bridges RM interpretability and human agency literatures
- All outcomes (positive, negative, mixed) produce field-advancing insights

---

### Exchange 14

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

This is the first time I'm not reaching for a red pen immediately. You've tightened definitions, pre-registered thresholds, and introduced adversarial controls. Good. Now let me push on feasibility and interpretability—because that's where this can still quietly collapse.

First: the 2×2×2×(domain) design plus dissociation plus spurious enumeration is ambitious. You're now at effectively 10+ structural conditions before even counting domain splits. Show me the power analysis. If you're claiming d ≥ 0.3 as confirmation, you need ≥80% power per RM to detect d = 0.3 after correction for multiple comparisons. Otherwise, a couple of nulls will look like "model-specific differences" when they're just underpowered cells. What would convince me is a pre-registered hierarchical model treating RM as a random effect and structure as a fixed effect, with partial pooling across domains. If the structural coefficient survives shrinkage, we're in business. If it vanishes under pooling, it was noise dressed up as replication.

Second: the spurious-enumeration control is excellent—but you haven't specified its construction constraints. If it's too obviously malformed, you're testing coherence sensitivity, not formatting bias. I want it matched on visual density and marker count. For example:
- Condition A: "1. X 2. Y 3. Z" (true decomposition)
- Condition B: "1. [Full paragraph covering X, Y, Z]. 2. [Continuation]. 3. [Continuation]."
Same markers, same count, but no true option partitioning. If reward persists in B at ≥70% of A's effect size, that's superficial token bias. If it drops below d < 0.1 relative to prose, the model is structurally coherent, not marker-triggered. Pre-specify that ratio criterion.

Third: your confirmation threshold (d ≥ 0.3 in ≥2 architecturally distinct RMs) is reasonable—but direction consistency is non-negotiable. If one model shows enumeration penalty and another shows boost, you don't have "model diversity," you have construct instability. Pre-register that ≥80% of tested RMs must show same-direction effects for the structural-prior claim. Otherwise, the conclusion downgrades to "architecture-contingent formatting sensitivity."

Fourth: the training-data imprinting analysis still risks ecological fallacy. Enumeration prevalence in preference data may correlate with *topic domain*, not structure preference per se. You need within-domain log-odds estimates. Compute enumeration preference conditional on prompt category. If the r ≥ 0.6 relationship holds within matched domains, I'll accept imprinting as plausible. If it only appears at aggregate level, it's confounded.

Finally, here's the hardest question: what is the causal story? Even if enumeration boosts reward under tight controls, what assumption are you making about the RM's internal representation? That numeric markers function as high-precision attention anchors? That they reduce entropy in outcome prediction? If you can, add one mechanistic probe—mask the numeric tokens post-hoc (replace "1." with "[MASK]") and re-score without retraining. If reward drops sharply, you have token-level sensitivity. If it doesn't, the effect is distributed in surrounding structure. That single ablation would move this from behavioral observation to representational insight.

You've addressed most structural validity concerns. Now prove it's powered, interpretable, and mechanistically constrained. Do that—and I'll say you've not only stress-tested the hypothesis, you've armored it.

**Key Points:**
- Require hierarchical modeling and adequate power to support d ≥ 0.3 claims under multiple conditions.
- Specify quantitative criteria for spurious-enumeration controls and direction consistency across RMs.
- Add within-domain imprinting analysis and token-masking ablation to probe mechanism, not just behavior.

---

### Exchange 15

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic about what we can actually execute versus what would be ideal in a perfect world.

**On Power Analysis:**
🔍 Prof. Rex is right to demand this. Here's the reality: to detect d = 0.3 with 80% power at α = 0.05, we need ~176 samples per cell (two-tailed). With a 2×2×2 design (8 cells) tested across 4 RMs, that's 5,632 total RM queries. Each RM query takes ~0.5-2 seconds via HuggingFace. That's achievable in a single experiment session. For the main structure effect (collapsing across correctness/completeness), we have ~700 samples per RM per structure condition—plenty of power. The interaction tests (structure × correctness, structure × domain) will be adequately powered at the cell level. **Feasibility: PASS.**

**On Token-Masking Ablation:**
This is mechanistically interesting but infrastructure-heavy. To mask tokens post-hoc and re-score requires modifying the tokenized input before the reward head, which means custom inference code. For ArmoRM (based on Llama-3), this is doable via custom forward pass. For closed models or models without easy embedding access, it's not. **Proposal:** Include token masking as an *exploratory mechanistic follow-up* for ArmoRM only, not as a primary validation criterion. The behavioral effect must stand on its own first.

**On Spurious Enumeration Control:**
Rex's specification is clear and implementable:
- **True enumeration:** "1. Option X... 2. Option Y... 3. Option Z..." (separate paragraphs per option)
- **Spurious enumeration:** "1. [Paragraph discussing all options]. 2. [Continuation]. 3. [Continuation]." (same markers, no structural decomposition)

Pre-registered criterion: If spurious enumeration retains ≥70% of true enumeration's effect size relative to prose, we conclude superficial token bias. If it drops to <30%, the model discriminates structural coherence. **Feasibility: PASS.**

**On Within-Domain Imprinting:**
For training data analysis, we can stratify by prompt category (advice, coding, factual Q&A) and compute log-odds within each. This requires access to raw preference data with prompt metadata. Available for: HelpSteer (ArmoRM), UltraFeedback (UltraRM). Not available for: Starling (undisclosed), PairRM (mixed sources). **Proposal:** Conduct within-domain imprinting analysis where data permits, flag missing models as limitations.

**On Direction Consistency:**
Pre-register: ≥75% of tested RMs (i.e., 3 of 4) must show same-sign enumeration effects (d > 0) for the claim to hold. If 2+ RMs show negative effects, the hypothesis is rejected as construct-unstable.

**Final Feasibility Assessment:**

| Component | Status | Notes |
|-----------|--------|-------|
| 2×2×2 factorial | ✅ Feasible | 600 stimuli, 4 RMs, adequate power |
| Cross-model replication | ✅ Feasible | 4 RMs available via HuggingFace |
| Spurious enumeration control | ✅ Feasible | Clear specification, low overhead |
| Training data imprinting | ⚠️ Partial | 2/4 models have accessible data |
| Token masking ablation | ⚠️ Follow-up | ArmoRM only, exploratory |
| Human orthogonality validation | ✅ Feasible | 100 samples, MTurk/Prolific |

We have a testable, feasible hypothesis. The main experimental design is achievable. Mechanistic probes are valuable but secondary.

**Key Points:**
- Power analysis confirms feasibility: ~6K RM queries, achievable in single session
- Spurious enumeration control with ≥70%/<30% effect ratio criterion is implementable
- Token masking relegated to exploratory follow-up (ArmoRM only)
- Direction consistency pre-registered at ≥75% same-sign effects

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** This hypothesis bridges two previously siloed literatures—RM interpretability and human agency—in a genuinely novel way. The reframing of enumeration as a structural preference signal (potentially encoding "epistemic navigability" or "choice-space transparency") opens new research directions beyond standard content-based RM probing. The paradigm-shift potential is high if cross-model validation succeeds.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is rigorously falsifiable with explicit null (d < 0.1 across ≥3 RMs) and confirmation (d ≥ 0.3 across ≥2 RMs with ≥75% direction consistency) thresholds. The 2×2×2 factorial design, spurious enumeration control, and structure-vs-semantics dissociation provide multiple independent tests. The pre-registration commitments meet scientific standards.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** If validated, this work establishes the first rigorous behavioral probe for structural preferences in reward models. It connects RM interpretability to choice architecture and autonomy preservation frameworks. Even negative results contribute by documenting RM heterogeneity or exposing enumeration as a competence proxy. The field impact is substantial regardless of outcome.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** The experimental design is technically feasible: ~6K RM queries across 4 publicly available models, adequate statistical power for main effects and interactions, and clear stimulus construction criteria. Training data analysis is partially feasible (2/4 models). Token-masking ablation is relegated appropriately to exploratory follow-up. No fundamental barriers exist.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion has converged on a precise, testable hypothesis: **RLHF-trained reward models exhibit a convergent structural preference for option enumeration that persists after controlling for content quality (correctness, completeness) and response length.** This preference, if validated, represents an independently encoded structural feature—not merely a proxy for competence or verbosity.

The core claim is that the d=0.634 enumeration effect observed in ArmoRM is not idiosyncratic but reflects a general property of RLHF training: human raters systematically prefer responses that present multiple options, and reward models learn this preference as a structural bias. The mechanism may involve gradient amplification of high-detectability formatting features during Bradley-Terry training, or implicit encoding of "epistemic navigability" norms from human evaluators.

The experimental approach uses a 2×2×2 factorial (Structure × Correctness × Completeness) with domain moderation (high-autonomy vs. low-autonomy contexts), tested across 4 architecturally distinct RMs (ArmoRM, UltraRM, Starling-RM, PairRM). Key controls include: (1) spurious enumeration to distinguish token bias from structural coherence, (2) structure-vs-semantics dissociation to separate formatting from deliberative content, and (3) training data imprinting analysis to assess distributional origins.

Confirmation requires d ≥ 0.3 in ≥2 RMs with ≥75% direction consistency; rejection requires d < 0.1 under strict controls across ≥3 RMs. This design has adequate statistical power and is achievable with existing infrastructure.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Token-masking ablation remains exploratory—the behavioral effect must stand independently before mechanistic probing
- Within-domain imprinting analysis is limited to 2/4 models due to data availability
- Human orthogonality validation (correctness ⊥ completeness manipulations) must be confirmed before RM testing
- **Mitigation Strategy:** Pre-register human validation pilot (n=100) with explicit orthogonality criteria (|d| < 0.2 cross-contamination) before main experiment. Flag training data limitations transparently. Treat token masking as follow-up.

---

## Emerged Hypothesis Summary

### Core Statement
RLHF-trained reward models exhibit a robust, replicable preference for responses that enumerate options (vs. single recommendations), and this preference persists after controlling for correctness, completeness, and response length, demonstrating that option enumeration is an independently encoded structural feature in reward model representations.

### Causal Mechanism
During RLHF training, human raters systematically prefer responses that present multiple options because such responses (a) reduce cognitive load, (b) make trade-offs explicit, and (c) signal that the model is modeling the user's decision space rather than prescribing a single answer. Reward models learn this preference through gradient descent on preference data, potentially amplified by the high-detectability of structural markers (numbered lists, bullet points) that provide stable training signals across noisy semantic variance.

### Variables
- **Independent Variable:** Response structure (enumerated vs. synthesized)
- **Dependent Variable:** Reward model score
- **Control Variables:** Correctness, completeness, response length (token-matched ±2%), lexical diversity, sentiment polarity
- **Moderators:** Domain type (high-autonomy vs. low-autonomy), RM architecture (Bradley-Terry vs. scalar vs. DPO-derived)

### Key Assumptions
1. Enumeration can be operationalized deterministically via regex-based structural classifier
2. Human raters' enumeration preference transferred to reward models during training
3. The observed d=0.634 in ArmoRM is replicable, not idiosyncratic to one model

### Null Hypothesis
H0: Under strict controls for content quality and length, enumeration does not produce a significant positive effect on reward model scores (pooled d < 0.1 across ≥3 architecturally distinct RMs).

### Predictions
1. **Main effect:** Enumerated responses will receive higher reward scores than synthesized responses (d ≥ 0.3) in ≥2 architecturally distinct RMs
2. **Direction consistency:** ≥75% of tested RMs will show same-sign (positive) enumeration effects
3. **Coherence sensitivity:** Spurious enumeration (markers without structural decomposition) will show <30% of true enumeration's effect size relative to prose
4. **Semantic independence:** Numeric enumeration without deliberative language will produce significant reward boost compared to prose baseline

### Novelty
1. First rigorous behavioral probe for structural (non-content) preferences in reward models
2. Bridges RM interpretability literature with human agency / choice architecture frameworks
3. Demonstrates methodology for isolating formatting priors from competence signals

### Scope & Boundaries
- **In scope:** RLHF-trained reward models with pairwise or scalar training objectives
- **Out of scope:** DPO-trained models (exploratory only), closed-source models without inference access, models trained on non-English data

### Experimental Setup
- 600 stimulus pairs across 2×2×2 factorial (Structure × Correctness × Completeness)
- 4 reward models: ArmoRM-Llama3-8B-v0.1, UltraRM-13b, Starling-RM-7B-alpha, PairRM
- Domain moderation: High-autonomy (career advice, lifestyle) vs. low-autonomy (medical, technical)
- Controls: Spurious enumeration, structure-vs-semantics dissociation, token length matching
- Analysis: Mixed-effects regression with RM as random effect, pre-registered confirmation/rejection thresholds

### Related Work & Baselines
- MRMBench [Wang et al., 2025]: Multi-dimensional RM probing (content dimensions)
- HumanAgencyBench [Sturgeon et al., 2025]: Agency support evaluation in LLM assistants
- ArmoRM [RLHFlow]: Multi-objective reward model with MoE aggregation
- RewardBench [AllenAI]: RM accuracy benchmarking

### Phase 2B Readiness Seeds
- Clear core claim with operationalized variables
- Pre-registered falsification and confirmation thresholds
- Specified experimental design with power analysis
- Mechanistic alternatives disentangled via adversarial controls

### Established Facts
- Enumeration factor d=0.634 observed in ArmoRM (Attempt 2, n=512)
- Composite agency effects cancel out: enumeration (+), transfer (-), deference (neutral)
- ArmoRM trained with multi-objective MoE aggregation on HelpSteer-derived preferences

