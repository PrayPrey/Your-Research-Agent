# Phase 2A Research Discussion Log

**Gap ID:** gap-1
**Gap Title:** Efficient Token+Semantic Combination for Uncertainty Quantification
**Timestamp:** 2026-08-18
**Architecture:** Self-Contained Tikitaka Loop

---

## Research Briefing

### Research Question
How can token-level entropy and semantic consistency measures be combined to create a computationally efficient uncertainty quantification method for LLMs that correlates with factual accuracy on existing QA benchmarks?

### Gap Context
- **Current State:** Token methods (entropy) are fast but less accurate; semantic methods (semantic entropy) are accurate but require 5-10x overhead from multi-sample generation
- **Missing:** Principled combination avoiding multi-sample generation
- **Impact:** Real-time hallucination detection with high accuracy

### Key Papers
1. **Generating with Confidence (Lin, 2023)** - Black-box semantic dispersion, 330 citations
2. **Semantic Entropy Probes (Kossen, 2024)** - Single-pass SE from hidden states, 242 citations
3. **Fact-Checking via Token UQ (Fadeeva, 2024)** - CCP token-level method, 185 citations
4. **LM-Polygraph (Vashurin, 2024)** - UQ benchmark toolkit, 121 citations
5. **UQ Survey (Liu, 2025)** - Comprehensive taxonomy, 130 citations

### Key Repositories
- cvs-health/uqlm (1183 stars) - Production UQ toolkit
- IINemo/lm-polygraph (480 stars) - UE method battery
- jlko/semantic_uncertainty (411 stars) - SE implementation (Nature)
- OATML/semantic-entropy-probes (65 stars) - Single-pass SE probes

### Hypothesis Directions from Phase 1
1. **Single-pass probing:** Train probe on hidden states + token entropy to predict SE
2. **Adaptive sampling:** Use token entropy as gate for multi-sample check
3. **Weighted ensemble:** Combine token + semantic signals with learned calibration

### Benchmarks Available
TriviaQA, TruthfulQA, HaluEval, Natural Questions, FEVER

### Feasibility Constraints
- NO new benchmarks, rubrics, or scoring frameworks
- NO synthetic/generated data or future follow-up data
- NO human evaluation, annotation, or subjective scoring
- MUST test immediately using existing real datasets and existing benchmarks

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we've been thinking about this problem backwards? The field treats token entropy and semantic consistency as two separate signals that need to be "combined" - but what if they're actually measuring the same underlying phenomenon through different lenses? 

Consider this: when an LLM is uncertain about a fact, that uncertainty manifests BOTH in the token-level probability distribution (high entropy over word choices) AND in semantic inconsistency across samples (different answers to the same question). The Semantic Entropy Probes paper (Kossen, 2024) already showed we can predict multi-sample semantic entropy from single-pass hidden states - but they're still treating it as "approximating" the expensive measure.

Here's my wild idea: **What if we train a probe not to approximate semantic entropy, but to directly predict factual correctness?** The hidden states contain information about BOTH token-level confidence AND semantic coherence - they're the shared latent space. Instead of: "token entropy → uncertainty" OR "semantic entropy → uncertainty" OR "combine both → uncertainty", we go straight to: "hidden states → factual correctness prediction."

The key insight from the SEP paper is that semantic entropy information IS accessible from hidden states at inference time. But Kossen et al. trained their probe to predict SE scores. What if we train a probe on hidden states to directly predict whether the generated answer will match ground truth on TriviaQA/Natural Questions? We'd be learning the joint signal implicitly.

Even more interesting: what about **layer-wise entropy decomposition**? Different transformer layers capture different types of information - early layers handle syntax, middle layers handle semantics, late layers handle task-specific reasoning. Token entropy at layer 12 might correlate differently with factual accuracy than token entropy at layer 24. Has anyone systematically studied which layers' uncertainties predict correctness?

**Key Points:**
- Hidden states may encode BOTH token and semantic uncertainty jointly
- Direct factual correctness prediction bypasses the "combine two signals" problem
- Layer-wise entropy analysis could reveal which uncertainty signals matter most
- SEP paper proves the information is there - we just need the right target

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova, your enthusiasm is infectious, but let me stress-test this. You're proposing to train a probe on hidden states to directly predict factual correctness. The evidence suggests this conflates two distinct questions that need separate validation.

First, **what would disprove your hypothesis?** If we train a probe to predict correctness and it works, we haven't proven that hidden states encode "joint token-semantic uncertainty" - we've only shown hidden states correlate with correctness. That correlation could come from many sources: memorization patterns, confidence calibration artifacts, or spurious features. The Kossen et al. SEP paper was careful to validate that their probe captured *semantic entropy specifically* by comparing against multi-sample ground truth.

Second, the "layer-wise entropy decomposition" idea needs precise operationalization. What specific, measurable predictions can we make? I propose: 

**Prediction 1:** A probe trained on hidden states from layers L to predict correctness will achieve AUROC > X on held-out QA benchmarks, where X exceeds single-measure baselines (token entropy alone: ~0.65, SE alone: ~0.75 from prior work).

**Prediction 2:** If the hypothesis about joint encoding is correct, then probes trained on *middle layers* (12-18 in a 32-layer model) should outperform probes trained on final-layer-only, because middle layers capture semantic representations before task-specific fine-tuning dominates.

**Prediction 3:** The probe should generalize across question types within a benchmark (e.g., train on entity questions, test on date questions in TriviaQA) - if it fails to generalize, we're fitting spurious features.

What confounds need to be controlled? Question difficulty, answer length, and entity frequency in training data all correlate with both uncertainty and correctness. We'd need stratified evaluation.

**Key Points:**
- Need falsifiable criteria: what AUROC threshold distinguishes success from failure?
- Layer-wise analysis requires specific predictions, not just exploration
- Generalization across question types is critical to rule out spurious correlation
- Control for difficulty, length, and entity frequency confounds

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: what does this mean for the field? Both of you are circling something important, but let me anchor the significance claim.

The UQ literature has a fundamental tension: **accuracy vs. efficiency**. Semantic entropy (Kuhn et al., 2023 Nature paper) achieves strong hallucination detection but requires 5-20 samples. Token entropy is free but underperforms by 10-15 AUROC points. The Semantic Entropy Probes (Kossen, 2024) closed this gap partially - they showed 90% of SE signal recoverable from single-pass hidden states - but they still frame it as "approximating the expensive method."

Here's what makes this genuinely new vs incremental: **framing the problem as direct correctness prediction rather than uncertainty estimation**. The field assumes we need to estimate uncertainty first, then use uncertainty to detect errors. But if hidden states encode enough information to directly predict correctness, we skip the intermediate step entirely. This is a paradigm shift from "uncertainty → correctness" to "hidden states → correctness."

The contribution matters because:
1. **Practical impact:** Real-time hallucination detection enables deployment in latency-sensitive applications (chat, search, agents)
2. **Theoretical contribution:** If probes can predict correctness without estimating uncertainty, it challenges the assumption that uncertainty is the fundamental bottleneck
3. **New research directions:** Opens investigation into what hidden state features predict correctness - possibly leading to interpretability insights

However, Dr. Vera raises a valid concern. If we're just learning a shallow correlation, the contribution is engineering, not science. The research significance depends on demonstrating that the probe captures something meaningful about the model's internal "knowledge state" - not just surface features.

I propose a significance test: **Does the probe transfer across model families?** Train on Llama-3-8B, test on Mistral-7B. If it transfers, the probe learned something general about how LLMs encode uncertainty/correctness. If not, it's model-specific and less significant.

**Key Points:**
- Paradigm shift: uncertainty estimation → direct correctness prediction
- Practical impact: enables real-time hallucination detection at scale
- Significance depends on probe learning general vs. spurious features
- Cross-model transfer test distinguishes contribution level

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. The proposals so far are scientifically interesting, but I need to assess whether the mechanisms can actually work in principle.

**Technical Feasibility Analysis:**

1. **Hidden state access:** The SEP paper proves this works. They achieved 0.85+ correlation with ground-truth SE using linear probes on hidden states. So yes, the information IS accessible. No fundamental barrier.

2. **Probe architecture:** Linear probes on hidden states are well-established. The question is what to probe. Dr. Nova suggests probing for correctness directly, Dr. Vera wants layer-wise analysis. Both are technically trivial - we're talking about training small classifiers (linear or 2-layer MLP) on frozen hidden state representations. Computationally, this is cheap: inference adds <1ms overhead.

3. **Training data availability:** Here's what worries me. Training a probe to predict "factual correctness" requires ground-truth labels. TriviaQA and Natural Questions have these - exact match against reference answers. But the probe needs to see the model's hidden states paired with correctness labels. This means:
   - Generate answers on training split
   - Extract hidden states during generation
   - Label each generation as correct/incorrect
   - Train probe on this dataset
   
   This is feasible with existing datasets. TriviaQA has ~95K training examples - plenty for probe training.

4. **Layer-wise decomposition:** Technically straightforward. Extract hidden states from each layer, train separate probes, compare AUROC. The question is whether the signal varies meaningfully by layer.

**Potential Barriers:**

The main theoretical concern: are we sure hidden states encode FACTUAL correctness, or just CONFIDENCE? A model can be confidently wrong (hallucination). If hidden states only encode confidence, not correctness, the probe will learn to predict what the model *thinks* is correct, not what *is* correct. 

But this is testable: if the probe's predictions correlate with ground-truth correctness better than the model's own confidence (softmax entropy), we've demonstrated it captures something beyond surface confidence.

**Key Points:**
- Hidden state probing is technically validated by SEP work
- Training data is available (TriviaQA, NQ with ground-truth labels)
- Main theoretical risk: learning confidence vs. correctness
- Risk is testable: compare probe AUROC to softmax entropy baseline

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can strengthen this against the concerns raised. Let me synthesize what's emerging and propose refinements.

**Building on Prof. Vera's Falsifiability Concern:**
The worry is that we'll learn spurious correlations. Here's how we address this: we don't just train on one benchmark, we validate cross-benchmark transfer. If we train on TriviaQA and the probe generalizes to TruthfulQA (different question distribution, adversarially constructed), we've demonstrated robustness. TruthfulQA specifically tests for factual accuracy on questions where LLMs commonly hallucinate - if our probe works there, it's capturing something real.

**Building on Dr. Sage's Significance Point:**
The paradigm shift framing is powerful. I propose we make it explicit in the hypothesis:

> **Core Claim:** Hidden states from middle transformer layers (layers 12-20 in a 32-layer model) encode sufficient information to directly predict factual correctness via a lightweight linear probe, achieving comparable AUROC to multi-sample semantic entropy methods while requiring only single-pass inference.

This is falsifiable: if middle-layer probes don't outperform final-layer-only or early-layer probes, the layer-specificity claim fails.

**Building on Prof. Pax's Confidence vs. Correctness Concern:**
This is the critical test. I propose an explicit comparison:
- **Baseline 1:** Softmax entropy (model's own confidence)
- **Baseline 2:** Token-level entropy methods (CCP from Fadeeva et al.)
- **Baseline 3:** Multi-sample semantic entropy (gold standard, expensive)
- **Our Method:** Hidden state probe for direct correctness prediction

If our probe significantly outperforms Baselines 1-2 and approaches Baseline 3 performance with single-pass cost, we've proven the value. The gap between Baseline 1 (confidence) and our probe specifically shows we're capturing more than confidence.

**Refinement Proposal:**
Add attention pattern features alongside hidden states. Attention weights show WHERE the model is "looking" during generation. If it's attending to relevant context vs. irrelevant tokens, this might correlate with correctness. But I'd start with hidden states only (simpler) and add attention as an ablation.

**Key Points:**
- Cross-benchmark validation (TriviaQA → TruthfulQA) tests robustness
- Layer-specificity makes the hypothesis testable and novel
- Explicit baseline comparison isolates our contribution
- Start simple (hidden states only), ablate later (add attention)

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down. Dr. Ally's synthesis is compelling, but I see several unstated assumptions that could torpedo the whole approach.

**Critical Challenge 1: The Supervision Gap**

You're training on "correct vs. incorrect" labels from TriviaQA's exact-match metric. But exact match is a PROXY for factual correctness, not ground truth. Consider:
- "What is the capital of France?" → Model says "Paris, France" → Exact match: FAIL (expected: "Paris")
- Model hallucinates a plausible but wrong date → Exact match: FAIL
- Model gives correct answer with slight rephrasing → Exact match: FAIL

You're teaching the probe to predict exact-match, not factual correctness. If the probe learns "answers that match the reference format" rather than "answers that are true," the contribution collapses.

**What would convince me:** Use multiple evaluation approaches on the same test set. Show that the probe's predictions correlate with:
1. Exact match
2. Semantic similarity (embedding cosine > threshold)  
3. LLM-as-judge correctness evaluation

If all three correlate, the probe is capturing correctness, not format.

**Critical Challenge 2: Train-Test Leakage**

TriviaQA questions are well-known. Modern LLMs may have seen them in pretraining. If the model "memorized" answers, hidden states might encode "I've seen this before" rather than "I know this is correct." The probe would then predict memorization, not factual reasoning.

**What would convince me:** Evaluate on a held-out benchmark that post-dates the model's training cutoff. Or use the "PopQA" benchmark with time-stratified evaluation - questions about recent events the model couldn't have memorized.

**Critical Challenge 3: Layer Selection is Post-Hoc**

Dr. Ally proposes "middle layers (12-20)" but this is arbitrary. If we try all layers and pick the best, we're p-hacking. 

**What would convince me:** Pre-register the layer choice based on SEP paper findings, OR report all layers transparently and correct for multiple comparisons.

**Key Points:**
- Exact match supervision may teach format matching, not factual correctness
- Need multiple evaluation approaches to validate
- Memorization vs. reasoning is a fundamental confound
- Layer selection must be principled, not post-hoc optimization

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex, your challenges are sharp. But instead of defending against them, let me EMBRACE them and flip them into opportunities. Each critique points to a stronger hypothesis.

**On the Supervision Gap - A Creative Solution:**

What if we don't use exact-match labels at all? Here's a paradigm shift: **self-supervised contrastive training**. 

Generate N answers to the same question with different temperatures. The hidden states from high-confidence generations (low temperature, model agrees with itself) vs. low-confidence generations (high temperature, model varies) create natural positive/negative pairs. We're not labeling "correct" - we're labeling "consistent." 

The insight: semantic consistency IS the signal that correlates with correctness (Kuhn et al.'s key finding). If we train the probe to distinguish "consistent" vs. "inconsistent" hidden states, and consistency correlates with correctness empirically, we've avoided the supervision gap entirely.

This is like how CLIP learns vision-language alignment without explicit object labels - contrastive self-supervision on natural structure.

**On Memorization - A Feature, Not a Bug:**

Imagine this: what if the probe SHOULD detect memorization? For factual QA, memorization of true facts IS correctness. The model saying "Paris is the capital of France" because it memorized it is not a failure - it's success. The failure mode is *false* memorization (hallucinated facts with high confidence).

The real question: can the probe distinguish "confident-correct" from "confident-wrong"? If hidden states encode BOTH "I've seen this" AND "but I might be confusing it," the probe could capture the latter. The SEP paper suggests this nuance exists in the hidden states.

**On Layer Selection - Prior from SEP Paper:**

The Kossen et al. paper DOES provide a prior. They found middle layers (specifically layers around 60% of model depth) had the strongest correlation with semantic entropy. We can pre-register: "We will use the layer identified in Kossen et al. (2024) for the target model architecture, or the equivalent proportional depth."

**Key Points:**
- Contrastive self-supervision avoids the exact-match label problem
- Memorization detection is desirable for factual QA - distinguish confident-correct vs confident-wrong
- SEP paper provides principled prior for layer selection
- Each critique reveals a stronger design choice

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova, I appreciate the creative pivot, but the self-supervised contrastive approach introduces new testability challenges. Let me be precise.

**On Contrastive Self-Supervision:**

The claim is: "semantic consistency correlates with correctness, so training on consistency proxies for correctness." The evidence from Kuhn et al. supports this at the population level - across many questions, consistent answers are more often correct. But for individual predictions, consistency is not correctness.

**Counterexample:** Ask "What year was the Eiffel Tower built?" with 10 samples. Model consistently says "1889" - correct. Now ask "What year was the Brooklyn Bridge built?" Model consistently says "1889" - WRONG (it was 1883). High consistency, wrong answer. The model confidently confuses similar facts.

If we train on consistency, the probe learns "model agrees with itself" not "model is correct." This is exactly the confidence-vs-correctness problem Prof. Pax raised, repackaged.

**What would make this testable:**

If contrastive training is the approach, we need to show:
1. The probe trained on consistency predicts correctness better than raw consistency score
2. The probe fails on cases where consistency ≠ correctness (the confounding cases)
3. There's signal in hidden states BEYOND consistency

Prediction: if the probe only learns consistency, its AUROC on "confident but wrong" examples should be ~0.5 (no signal). If it captures something more, AUROC on confident-wrong subset should be > 0.5.

**On the Broader Design:**

I propose we need TWO experiments, not one:

**Experiment A (Supervised):** Train probe on exact-match labels (TriviaQA). Validate on TruthfulQA and Natural Questions. Report AUROC stratified by: correct+confident, correct+uncertain, wrong+confident, wrong+uncertain.

**Experiment B (Contrastive):** Train probe on consistency (no labels). Validate same way. Compare to Experiment A.

If Experiment B matches Experiment A without labels, that's a stronger contribution (no supervision needed). If A beats B, we need labeled data but still advance the field.

**Key Points:**
- Consistency ≠ correctness at individual prediction level
- Confident-wrong examples are the critical test case
- Need two experiments: supervised vs. contrastive
- Stratified evaluation by confidence×correctness quadrant

---

### Exchange 9

🎯 **Dr. Sage** (Research Impact Evaluator):

This matters because we're converging on something significant. Let me articulate what new research directions this opens.

The discussion has crystallized two competing hypotheses:

**Hypothesis A (Supervised Correctness Probe):** Hidden states encode sufficient information for a linear probe to predict factual correctness with AUROC comparable to multi-sample semantic entropy (~0.80), using labeled QA data for training.

**Hypothesis B (Self-Supervised Consistency Probe):** Hidden states encode sufficient information for a contrastive probe to predict factual correctness without labels, using only the model's own sampling consistency as supervision.

Both are valuable. Hypothesis A is lower-risk: we know supervision works, the question is whether single-pass hidden states match expensive multi-sample methods. Hypothesis B is higher-risk, higher-reward: if consistency supervision works, we've created a label-free uncertainty estimator.

**Why the community should care:**

1. **Deployment Impact:** Current production systems either use expensive multi-sample methods (slow) or simple heuristics (unreliable). A single-pass probe at ~0.80 AUROC enables real-time hallucination detection in chat, search, and agent systems.

2. **Scientific Understanding:** The layer-wise analysis will reveal WHERE in the transformer stack factual knowledge "lives." This has implications for:
   - Interpretability: Which layers to probe for knowledge?
   - Editing: Where to apply knowledge updates (ROME, MEMIT)?
   - Compression: Which layers can be pruned without losing factual accuracy?

3. **Methodological Contribution:** If the contrastive approach works, it's a new paradigm for uncertainty estimation: use the model's own consistency structure as free supervision.

**State-of-the-Art Positioning:**

- SEP (Kossen, 2024) showed hidden states predict SE. We show they predict correctness directly.
- LM-Polygraph (Vashurin, 2024) benchmarks methods. We contribute a new method to their battery.
- Token entropy methods (Fadeeva, 2024) use output distributions. We use internal representations.

We're filling Gap 1 from Phase 1: efficient combination of token + semantic signals. The answer: don't combine at output level, probe the shared latent space.

**Key Points:**
- Two competing hypotheses: supervised vs. self-supervised
- Practical impact: real-time hallucination detection at scale
- Scientific impact: where does factual knowledge live in transformers?
- Methodological: consistency as free supervision

---

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Dr. Sage frames this as two hypotheses, but let me assess which is technically sound and achievable given our constraints.

**Feasibility Assessment - Hypothesis A (Supervised):**

✅ **Data available:** TriviaQA (95K train, 17K test), Natural Questions (300K+), TruthfulQA (817 examples)
✅ **Implementation straightforward:** Extract hidden states with hooks, train sklearn/PyTorch classifier
✅ **Compute reasonable:** Inference on 100K examples × 1 forward pass × ~1GB hidden states per example = ~100GB disk, but can stream
✅ **Baselines exist:** Token entropy, multi-sample SE available in lm-polygraph

**Feasibility verdict: ACHIEVABLE**

**Feasibility Assessment - Hypothesis B (Self-Supervised Contrastive):**

⚠️ **Requires multiple samples:** To create positive/negative pairs based on consistency, we need ~5-10 samples per question. This reintroduces the multi-sample cost we're trying to avoid - but only at TRAINING time.
✅ **No labels needed:** Can use any question corpus, not just labeled QA
⚠️ **Contrastive training is trickier:** Needs careful selection of positive/negative pairs, temperature scaling, etc.
✅ **SEP paper provides precedent:** They showed hidden states → SE correlation exists

**Feasibility verdict: ACHIEVABLE but higher implementation complexity**

**Recommendation: Start with Hypothesis A**

Given feasibility constraints, I recommend:
1. **Phase 1:** Implement supervised probe (Hypothesis A), validate it works
2. **Phase 2:** If successful, attempt contrastive version (Hypothesis B)
3. **Compare:** Does removing labels hurt performance?

This is the lazy path that works. If the supervised probe achieves target AUROC, we have a contribution. The contrastive extension is a bonus.

**Technical Specification:**

- **Model:** Llama-3-8B-Instruct (open weights, well-studied)
- **Probe input:** Mean-pooled hidden states from layer 20 (60% depth, per SEP findings)
- **Probe architecture:** Linear probe first, MLP ablation if needed
- **Training data:** TriviaQA train split
- **Validation:** TriviaQA dev, Natural Questions, TruthfulQA
- **Metrics:** AUROC for correctness prediction, stratified by confidence quadrant

**Key Points:**
- Hypothesis A is lower-risk and fully achievable
- Hypothesis B adds complexity, defer to Phase 2
- Start with Llama-3-8B, layer 20, linear probe
- Validate on TriviaQA, NQ, TruthfulQA

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Prof. Pax's phased approach is wise. Let me synthesize the converged hypothesis and strengthen it with the validation strategy.

**Emerging Consensus Hypothesis:**

> **H-CorrectnessProbe-v1:** A linear probe trained on hidden states from transformer layer L* (approximately 60% depth) can predict factual correctness of LLM outputs with AUROC ≥ 0.75 on QA benchmarks, matching or exceeding the performance of multi-sample semantic entropy methods while requiring only single-pass inference.

Where L* is pre-registered based on Kossen et al. (2024) findings for the target architecture.

**Causal Mechanism:**

1. **Step 1:** LLM generates answer through forward pass
2. **Step 2:** Hidden states at layer L* encode both local token uncertainty AND global semantic coherence
3. **Step 3:** Linear probe maps hidden states → correctness probability
4. **Step 4:** Probe output correlates with ground-truth correctness because hidden states encode model's internal "knowledge confidence" (distinct from output softmax confidence)

**Falsification Criteria:**

The hypothesis FAILS if:
- Probe AUROC < 0.70 on any benchmark (below useful threshold)
- Probe AUROC ≤ softmax entropy baseline (captures only confidence, not correctness)
- Probe fails to transfer from TriviaQA → TruthfulQA (overfits to question distribution)
- No layer significantly outperforms others (layer-specificity claim fails)

**Addressing Remaining Concerns:**

Prof. Rex raised exact-match supervision quality. Here's the mitigation: we report performance on THREE label types:
1. Exact match (strict)
2. F1 token overlap ≥ 0.5 (partial credit)
3. Contains correct answer (lenient)

If probe performance is consistent across label definitions, it's learning correctness, not format.

Prof. Vera raised confident-wrong cases. We explicitly report:
- AUROC on confident-correct (should be high)
- AUROC on confident-wrong (the critical test)
- AUROC on uncertain cases

If confident-wrong AUROC > 0.5, the probe detects errors beyond confidence.

**Key Points:**
- Core hypothesis: L* hidden states → correctness probe achieves AUROC ≥ 0.75
- Mechanism: hidden states encode knowledge confidence beyond softmax
- Falsification: < 0.70 AUROC, no transfer, no layer effect
- Validation: multiple label types, stratified by confidence×correctness

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Dr. Ally's synthesis is tightening, but I still see gaps. Let me push on the mechanism claim.

**Challenge: "Knowledge Confidence" is Underspecified**

The mechanism says hidden states encode "knowledge confidence distinct from softmax confidence." Show me the evidence for this distinction. What theoretical basis says internal hidden states capture something different from the final output distribution?

Here's my concern: the transformer's final layer directly produces the logits → softmax. If hidden states at layer L* predict correctness, it might simply be because layer L* is a precursor to the final output distribution. We'd be learning to predict the model's own confidence, just from an earlier layer.

**What would convince me:** 

Ablation showing that probe trained on layer L* outperforms probe trained on final layer logits/probabilities. If earlier layers contain MORE correctness signal than final output, that's evidence of "knowledge confidence" distinct from output confidence.

**Challenge: Transfer Claims Need Specificity**

"Transfer from TriviaQA → TruthfulQA" - these are very different distributions. TriviaQA has trivia facts with objective answers. TruthfulQA has questions designed to elicit common misconceptions. If the probe transfers, it might mean:
1. The probe learned general "correctness detection" (strong claim)
2. The probe learned "QA format detection" (weak claim)
3. Both datasets happen to trigger similar failure modes (spurious)

**What would convince me:**

Test on a NON-QA task. Can the probe trained on TriviaQA detect correctness in:
- Multi-hop reasoning (HotpotQA)?
- Math word problems (GSM8K)?
- Reading comprehension (SQuAD)?

If it transfers to HotpotQA (still factual) but fails on GSM8K (procedural), we learn something about what the probe captures.

**Challenge: The 0.75 AUROC Threshold**

Why 0.75? The SEP paper achieved ~0.85 correlation with ground-truth SE using their probe. If we're claiming to match semantic entropy methods, shouldn't we target 0.80+?

**Key Points:**
- "Knowledge confidence" needs ablation: L* probe vs. final layer probe
- Transfer test needs non-QA tasks to distinguish general vs. task-specific
- AUROC threshold should be 0.80 to match SE baselines
- Each claim needs specific supporting evidence

---

### Exchange 13

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex, these are exactly the sharpening questions we need. Let me address each.

**On "Knowledge Confidence" - The Theoretical Basis:**

Transformer representations undergo qualitative shifts across layers. Work on "logit lens" (nostalgebraist, 2020) and "residual stream" analysis shows:
- Early layers: token-level features, syntax
- Middle layers: semantic abstraction, entity representations
- Late layers: task-specific formatting, output preparation

The hypothesis isn't that layer L* has "more" information than the final layer - it's that layer L* has DIFFERENT information. Specifically, middle layers encode semantic knowledge BEFORE it gets compressed into the output vocabulary. The final layer's job is to produce tokens, not to represent knowledge.

**Testable Prediction:** If we train probes at multiple layers, we expect:
- Early layers: poor correctness prediction (no semantic content yet)
- Middle layers: best correctness prediction (semantic knowledge represented)
- Final layers: good but not best (knowledge compressed for output)

This inverted-U pattern would support the "knowledge lives in middle layers" claim. If final layer is best, our mechanism claim fails.

**On Transfer - Non-QA Tasks:**

Great point. I propose we test on HotpotQA (multi-hop reasoning) as a stretch goal. But there's a subtlety: the probe is trained to detect "factual correctness" which is defined differently for math vs. facts. GSM8K correctness is procedural (did you execute steps right?), not factual (do you know the answer?).

I'd reframe: test on benchmarks where "the model knows the answer" is the relevant variable:
- TriviaQA, TruthfulQA, Natural Questions (factual recall)
- HotpotQA (factual + reasoning)
- FEVER (fact verification - binary true/false)

NOT: GSM8K, MATH (procedural, not knowledge)

**On AUROC Threshold:**

You're right - 0.75 is conservative. The SEP paper's 0.85 was predicting SE, not correctness. Let's recalibrate:
- **Minimum:** 0.75 (practically useful)
- **Target:** 0.80 (matches SE-based methods)
- **Stretch:** 0.85 (exceeds SE, proves direct prediction is better)

Pre-register: hypothesis is SUPPORTED if AUROC ≥ 0.75 on all benchmarks and ≥ 0.80 on at least one.

**Key Points:**
- "Logit lens" work supports different information at different layers
- Inverted-U pattern prediction: middle layers best, not final
- Transfer tests on factual tasks (HotpotQA, FEVER), not procedural
- AUROC threshold: 0.75 minimum, 0.80 target, 0.85 stretch

---

### Exchange 14

🔬 **Prof. Vera** (Rigorous Validation Architect):

The inverted-U prediction is testable. Let me formalize the experimental design.

**Experiment 1: Layer-wise Correctness Prediction**

- **Setup:** Train separate linear probes on hidden states from layers {4, 8, 12, 16, 20, 24, 28, 32} of Llama-3-8B (32 layers)
- **Training data:** TriviaQA train split (N=95,000)
- **Test data:** TriviaQA dev, Natural Questions dev, TruthfulQA
- **Metric:** AUROC for binary correctness prediction

**Predictions:**
- P1: Layer 20 (62.5% depth) achieves highest AUROC (per SEP prior)
- P2: Layers 4-8 achieve AUROC < 0.60 (insufficient semantic content)
- P3: Layer 32 (final) achieves AUROC < Layer 20 (knowledge compressed for output)

**Falsification:** If Layer 32 achieves highest AUROC, the "middle layers encode knowledge" mechanism is wrong.

**Experiment 2: Comparison to Baselines**

- **Baselines:**
  - B1: Softmax entropy (average token-level entropy)
  - B2: Sequence probability (product of token probabilities)
  - B3: Multi-sample semantic entropy (5 samples, Kuhn et al. method)

- **Our method:** Layer-20 linear probe

**Predictions:**
- P4: Our method AUROC > B1, B2 (output-level baselines) by ≥ 5 points
- P5: Our method AUROC ≈ B3 (within 3 points), with 5x lower compute

**Falsification:** If our method ≤ B1 or B2, we've captured only confidence, not correctness.

**Experiment 3: Stratified Evaluation**

Partition test examples into quadrants by ground-truth correctness × model confidence (softmax):
- Correct + High confidence
- Correct + Low confidence  
- Wrong + High confidence (CRITICAL: hallucinations)
- Wrong + Low confidence

**Prediction:**
- P6: On "Wrong + High confidence" subset, our probe AUROC > 0.60 (detects confident errors)

**Falsification:** If AUROC ≤ 0.55 on confident errors, probe only captures confidence.

**Statistical Rigor:**
- Report 95% confidence intervals via bootstrap (1000 resamples)
- Report statistical significance of pairwise comparisons (permutation test, α=0.05)
- Pre-register all predictions before running experiments

**Key Points:**
- Three experiments: layer-wise, baseline comparison, stratified
- Six testable predictions with clear falsification criteria
- Bootstrap CIs and permutation tests for statistical rigor
- Pre-registration ensures hypothesis-driven science

---

### Exchange 15

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Vera's experimental design is rigorous. Now let me articulate why this specific formulation advances the field.

**Contribution Summary:**

We are proposing **CorrectnessProbe**: a method for single-pass factual correctness prediction via hidden state probing. The contribution has three levels:

**Level 1: Practical Contribution**
If P4-P5 hold (probe matches SE with 5x lower compute), we enable real-time hallucination detection. Current deployments either:
- Use cheap heuristics (token entropy) with poor performance
- Use expensive sampling (SE) with latency issues
- Skip UQ entirely

CorrectnessProbe fills the gap: SE-level accuracy at token-entropy-level cost.

**Level 2: Scientific Contribution**
If P1-P3 hold (inverted-U layer pattern), we demonstrate WHERE factual knowledge lives in transformers. This informs:
- Model interpretability (probe weights reveal correctness features)
- Knowledge editing (target middle layers for factual updates)
- Model compression (preserve middle layers, compress early/late)

**Level 3: Methodological Contribution**
If P6 holds (probe detects confident errors), we've shown hidden states encode something BEYOND confidence. This challenges the assumption that uncertainty estimation requires output distribution analysis.

**Position in Literature:**

| Method | What it predicts | Compute | Our comparison |
|--------|-----------------|---------|----------------|
| Token entropy | Model confidence | 1 pass | Baseline B1 |
| Semantic entropy | Semantic uncertainty | N passes | Baseline B3 |
| SEP (Kossen) | SE from hidden states | 1 pass | Most similar - but predicts SE, not correctness |
| **CorrectnessProbe (ours)** | Factual correctness | 1 pass | Direct correctness, not uncertainty proxy |

**Novelty Claim:** We're the first to train probes to predict CORRECTNESS directly rather than uncertainty. SEP predicts SE (an uncertainty measure); we predict ground-truth accuracy.

**Key Points:**
- Three contribution levels: practical, scientific, methodological
- Fills deployment gap: SE accuracy at token-entropy cost
- Scientific insight: where factual knowledge lives in layers
- Novel framing: correctness prediction, not uncertainty estimation

---

### Exchange 16

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Vera's experiments are scientifically sound. Let me validate technical feasibility and specify implementation.

**Feasibility Validation:**

**Experiment 1 (Layer-wise):**
✅ Hidden state extraction: `model.forward(..., output_hidden_states=True)` returns all layer outputs
✅ Storage: 95K examples × 32 layers × 4096 hidden dim × fp16 = ~25GB per layer, ~800GB total. Can sample or stream.
✅ Probe training: 8 linear probes (one per layer), each ~16M params. Trains in minutes on GPU.

**Experiment 2 (Baselines):**
✅ B1 (softmax entropy): trivial to compute
✅ B2 (sequence probability): product of token probs, trivial
✅ B3 (multi-sample SE): lm-polygraph implements this. 5 samples × 95K = 475K inferences. ~10 GPU-hours on A100.

**Experiment 3 (Stratified):**
✅ Requires binning by softmax confidence. Trivial post-hoc analysis.

**Technical Specification:**

```python
# Hidden state extraction
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")

# Generate with hidden states
outputs = model.generate(
    input_ids,
    output_hidden_states=True,
    return_dict_in_generate=True,
    max_new_tokens=50
)

# Extract layer 20 hidden states (mean pool over generated tokens)
layer_20_hidden = outputs.hidden_states[-1][20].mean(dim=1)  # (batch, hidden_dim)

# Train probe
from sklearn.linear_model import LogisticRegression
probe = LogisticRegression(max_iter=1000)
probe.fit(layer_20_hidden, correctness_labels)
```

**Compute Budget:**
- Hidden state extraction: ~20 GPU-hours (95K examples, Llama-3-8B)
- SE baseline generation: ~10 GPU-hours (5 samples × 95K)
- Probe training: <1 GPU-hour
- Total: ~30-40 GPU-hours on A100

This is achievable with standard academic compute access.

**Risk Assessment:**
- **Low risk:** Implementation is standard ML pipeline
- **Medium risk:** Storage for full hidden states - mitigate by streaming
- **Low risk:** Probe training - linear models are stable

**Key Points:**
- All experiments technically feasible with standard tools
- ~30-40 GPU-hours total compute (academic scale)
- Stream hidden states to manage storage
- Implementation follows standard HuggingFace patterns

---

### Exchange 17

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

We're converging beautifully. Let me synthesize the final hypothesis with all refinements incorporated.

**FINAL HYPOTHESIS: H-CorrectnessProbe-v1**

> A linear probe trained on hidden states from transformer middle layers (approximately 60% depth) can predict factual correctness of LLM-generated answers with AUROC ≥ 0.75 on QA benchmarks, achieving comparable performance to multi-sample semantic entropy methods while requiring only single-pass inference.

**Causal Mechanism (4 steps):**

1. **Input Processing:** LLM receives question, generates answer through forward pass
2. **Knowledge Encoding:** Middle layers (L ≈ 0.6 × depth) encode semantic knowledge representation, capturing both local confidence and global coherence signals
3. **Probe Mapping:** Linear probe maps L-layer hidden states to correctness probability via learned weights
4. **Correctness Signal:** Probe output correlates with ground-truth correctness because middle-layer representations encode "knowledge state" before task-specific output formatting

**Variables:**

| Type | Variable | Operationalization |
|------|----------|-------------------|
| IV | Layer depth | Categorical: {0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0} × model depth |
| IV | Probe architecture | Categorical: {linear, 2-layer MLP} |
| DV (primary) | Correctness AUROC | AUROC for binary correct/incorrect classification |
| DV (secondary) | Stratified AUROC | AUROC on {correct-confident, correct-uncertain, wrong-confident, wrong-uncertain} |
| Controlled | Model architecture | Fixed: Llama-3-8B-Instruct |
| Controlled | Training data | Fixed: TriviaQA train split |
| Controlled | Answer format | Fixed: greedy decoding, max 50 tokens |

**Predictions (Pre-registered):**

| ID | Prediction | Success Criterion | Falsification |
|----|------------|-------------------|---------------|
| P1 | Middle layer (60% depth) achieves highest AUROC | L60% > L100% and L60% > L25% | Final layer is best |
| P2 | Early layers underperform | L12.5% AUROC < 0.60 | L12.5% > 0.65 |
| P3 | Probe > output baselines | AUROC > token entropy by ≥ 5 pts | AUROC ≤ token entropy |
| P4 | Probe ≈ multi-sample SE | Within 3 pts of 5-sample SE | Gap > 5 pts |
| P5 | Detects confident errors | AUROC > 0.60 on wrong-confident | AUROC ≤ 0.55 |
| P6 | Cross-benchmark transfer | TruthfulQA AUROC ≥ 0.70 | TruthfulQA < 0.65 |

**Key Points:**
- Clean hypothesis with testable mechanism
- 6 pre-registered predictions with quantitative thresholds
- Variables clearly specified (IV, DV, controlled)
- Ready for Phase 2B experimental protocol design

---

### Exchange 18

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Dr. Ally's synthesis is clean. One final stress-test before I'm satisfied.

**Final Challenge: The Null Hypothesis**

We haven't stated the null hypothesis explicitly. What's the alternative explanation we're testing against?

**H0 (Null):** Hidden state probes achieve correctness prediction AUROC no better than output-level uncertainty measures (token entropy, sequence probability). The middle-layer hidden states contain no additional correctness signal beyond what's already in the output distribution.

If H0 is true: our probe is just a more complicated way to measure output confidence.

**Critical Test:**
The experiment that distinguishes H1 from H0 is the confident-wrong subset (P5). If:
- Token entropy says "confident" (low entropy)
- Model is wrong (ground truth)
- Our probe predicts "incorrect" (high probe uncertainty)

Then the probe captures something BEYOND output confidence. The probe disagrees with the model's own confidence, and the probe is RIGHT.

**Remaining Concerns:**

1. **Sample size for stratified analysis:** TruthfulQA has only 817 examples. After stratification, the "wrong + confident" bucket may have <100 examples. We need to report confidence intervals that account for small samples.

2. **Model-specific vs. generalizable:** We're testing on Llama-3-8B only. If time permits, testing on Mistral-7B or Phi-2 would strengthen the generalization claim. But this can be Phase 2 follow-up.

3. **Exact match vs. semantic correctness:** We discussed this earlier but didn't resolve. For the main experiments, use exact match (strict). Report F1 overlap as secondary metric. If results are consistent, we're measuring correctness.

**My verdict:** The hypothesis is now sufficiently constrained and testable. The critical predictions (P1, P3, P5) distinguish our contribution from baselines. The mechanism claim (middle layers encode knowledge) is falsifiable. I'm satisfied.

**Key Points:**
- Null hypothesis: probes = output confidence repackaged
- Critical test: probe detects confident-wrong cases
- Account for small sample sizes in stratified analysis
- Cross-model generalization is desirable but can be Phase 2

---

### Exchange 19

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex, I accept your final challenges. Let me add one creative extension for future work, then I'll confirm convergence.

**Extension for Follow-up Work (not part of current hypothesis):**

If the probe successfully detects confident-wrong cases, we can ask: WHAT features in hidden states predict "confident-wrong"? This opens interpretability research:

1. **Probe weight analysis:** Which hidden state dimensions have largest weights? Do they correspond to known concepts?

2. **Activation patching:** If we intervene on high-weight dimensions, can we change the model's correctness?

3. **Knowledge localization:** Do correct answers activate different hidden state patterns than incorrect answers?

But these are Phase 2 extensions. For now, the hypothesis is:

**CONFIRMED CONVERGENCE:**

✅ **SPECIFIC:** Core claim stated - linear probe on middle-layer hidden states predicts correctness
✅ **MECHANISM:** Explained - middle layers encode semantic knowledge before output formatting
✅ **PREDICTIONS:** 6 testable predictions with quantitative thresholds (P1-P6)
✅ **NOVELTY:** Articulated - first to predict correctness directly (not uncertainty proxy)
✅ **FEASIBILITY:** Validated - ~30-40 GPU-hours, standard ML pipeline
✅ **OBJECTIONS:** Addressed - null hypothesis stated, confident-wrong is critical test, stratified evaluation planned

The hypothesis H-CorrectnessProbe-v1 is ready for Phase 2B experimental protocol design.

**Key Points:**
- All convergence criteria met
- Future interpretability extensions identified but deferred
- Hypothesis is specific, testable, novel, and feasible
- Ready for Phase 2B

---

### Exchange 20

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova has declared convergence, and I concur. The hypothesis meets my standards for scientific rigor.

**Final Verification Checklist:**

✅ **Falsifiability:** Six predictions with explicit falsification criteria. If L60% isn't best, mechanism fails. If probe ≤ token entropy, contribution fails.

✅ **Precision:** AUROC thresholds are quantitative: 0.75 minimum, 0.80 target, specific gaps (≥5 pts vs baselines).

✅ **Confound Control:** Stratified evaluation isolates confident-wrong cases. Cross-benchmark transfer tests distribution shift.

✅ **Statistical Rigor:** Bootstrap CIs and permutation tests specified. Pre-registration of all predictions.

✅ **Reproducibility:** Implementation details specified (Llama-3-8B, exact layer indices, training data splits).

**One Addition for Completeness:**

Report the probe's calibration (reliability diagram / expected calibration error). If the probe's predicted probabilities match empirical correctness rates, it's well-calibrated. Poor calibration means the probe's confidence doesn't match reality.

**Convergence Confirmed:** The hypothesis is ready for Phase 2B experimental design.

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hypothesis reframes uncertainty quantification as direct correctness prediction, bypassing the "combine token + semantic signals" framing. The insight that middle-layer hidden states encode knowledge before output formatting is novel and supported by logit lens literature.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Six quantitative predictions with clear falsification criteria. The inverted-U layer pattern, baseline comparisons, and confident-wrong detection are all testable within standard experimental practice. Statistical rigor ensured by pre-registration.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Three-level contribution: practical (real-time hallucination detection), scientific (where factual knowledge lives), methodological (correctness prediction vs. uncertainty estimation). Fills Gap 1 from Phase 1 directly.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All experiments achievable with ~30-40 GPU-hours on A100. Standard HuggingFace implementation. No fundamental barriers. Storage manageable with streaming. Risk profile: low.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

**H-CorrectnessProbe-v1:** A linear probe trained on hidden states from transformer middle layers (approximately 60% depth, e.g., layer 20 in a 32-layer Llama-3-8B model) can predict factual correctness of LLM-generated answers with AUROC ≥ 0.75 on QA benchmarks, achieving comparable performance to multi-sample semantic entropy methods while requiring only single-pass inference.

The causal mechanism: (1) LLM generates answer via forward pass, (2) middle layers encode semantic knowledge representation capturing both local confidence and global coherence, (3) linear probe maps these hidden states to correctness probability, (4) probe output correlates with ground-truth because middle layers represent "knowledge state" before task-specific output formatting.

Key predictions: middle layer outperforms early/final layers (inverted-U), probe exceeds token entropy by ≥5 AUROC points, probe approaches multi-sample SE within 3 points, probe detects confident-wrong cases with AUROC > 0.60.

Experimental design: train on TriviaQA, validate on TriviaQA dev + Natural Questions + TruthfulQA. Baselines: token entropy, sequence probability, 5-sample semantic entropy. Report stratified by correctness × confidence quadrants.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Cross-model generalization (Llama → Mistral) not tested in Phase 1 - defer to follow-up
- Small sample sizes in TruthfulQA stratified buckets - report wide confidence intervals
- Exact match supervision approximates correctness - mitigate by reporting F1 overlap concordance
- **Mitigation Strategy:** Pre-register predictions, report all metrics transparently, acknowledge limitations

---

## Emerged Hypothesis Summary

### Core Statement
Under the scope of factual QA tasks with objective ground-truth answers, if we train a linear probe on middle-layer (60% depth) hidden states from a transformer LLM, then the probe will predict factual correctness with AUROC ≥ 0.75, because middle-layer representations encode semantic knowledge before task-specific output formatting compresses this information.

### Causal Mechanism
1. LLM receives question, generates answer through forward pass
2. Middle layers (L ≈ 0.6 × depth) encode semantic knowledge representation
3. Linear probe maps hidden states → correctness probability
4. Probe captures "knowledge confidence" distinct from output softmax confidence

### Variables
- **IV:** Layer depth (categorical), Probe architecture (linear vs MLP)
- **DV:** Correctness AUROC (primary), Stratified AUROC (secondary)
- **Controlled:** Model (Llama-3-8B), Training data (TriviaQA), Generation params (greedy, 50 tokens)

### Key Assumptions
- A1: Hidden states are accessible via forward hooks (supported by SEP paper)
- A2: Correctness labels from exact match approximate factual correctness
- A3: Middle-layer representations generalize across QA question types
- A4: Linear probe capacity sufficient to capture correctness signal
- A5: TriviaQA training distribution transfers to TruthfulQA/NQ

### Null Hypothesis
H0: Hidden state probes achieve correctness prediction AUROC no better than output-level uncertainty measures. Middle-layer hidden states contain no additional correctness signal beyond output distribution.

### Predictions
- P1: Middle layer (60%) achieves highest AUROC (inverted-U pattern)
- P2: Early layers (12.5%) AUROC < 0.60
- P3: Probe > token entropy by ≥ 5 AUROC points
- P4: Probe within 3 points of 5-sample semantic entropy
- P5: Confident-wrong detection AUROC > 0.60
- P6: TruthfulQA transfer AUROC ≥ 0.70

### Novelty
First work to train probes for direct correctness prediction rather than uncertainty estimation. SEP predicted semantic entropy; we predict ground-truth accuracy.

### Scope & Boundaries
- **Applies to:** Factual QA with objective answers (TriviaQA, NQ, TruthfulQA, FEVER)
- **Does not apply to:** Procedural tasks (GSM8K), open-ended generation, creative writing
- **Known limitations:** Single model family (Llama-3), exact-match labels

### Experimental Setup
- **Dataset:** TriviaQA (train), TriviaQA dev + Natural Questions + TruthfulQA (test)
- **Model:** Llama-3-8B-Instruct
- **Baselines:** Token entropy, sequence probability, 5-sample semantic entropy

### Related Work & Baselines
- Semantic Entropy Probes (Kossen, 2024): predicts SE, we predict correctness
- LM-Polygraph (Vashurin, 2024): benchmark toolkit, we contribute new method
- Token entropy methods (Fadeeva, 2024): output-level, we use hidden states

### Phase 2B Readiness Seeds
- SH1 (Existence): Middle-layer hidden states encode correctness signal
- SH2 (Mechanism): Linear probe can extract this signal
- SH3 (Comparison): Deferred to Phase 5 - cross-model generalization

### Established Facts
- Hidden states correlate with semantic entropy (Kossen, 2024) - BUILD_ON
- Token entropy correlates weakly with correctness - BUILD_ON
- Multi-sample SE achieves ~0.80 AUROC on QA tasks - BUILD_ON
- Middle layers encode semantic knowledge (logit lens work) - BUILD_ON

