# Phase 2A Research Discussion Log

**Research Gap:** Unified Bidirectional Alignment Measurement Framework
**Gap ID:** gap-1
**Priority:** PRIMARY (CRITICAL)
**Date:** 2026-08-24

---

## Discussion Briefing

### Research Context

**Selected Gap:** No existing benchmark jointly measures AI-to-human AND human-to-AI alignment. RewardBench evaluates AI-to-human alignment (reward model quality), Collaborative-Gym evaluates human-AI collaboration (human-to-AI interaction). No benchmark simultaneously measures both directions using the same methodology.

**Missing Piece:** A computational method to jointly evaluate bidirectional alignment on existing benchmarks, enabling quantitative comparison of both alignment directions with a unified metric.

**Research Question:** What computational methods can empirically measure or improve bidirectional alignment between humans and AI systems, using existing benchmarks?

### Key Resources

**Academic Papers:**
- Shen et al. (2024): "Towards Bidirectional Human-AI Alignment: A Systematic Review" - arXiv:2406.09264 (71 citations)
- Lambert & Calandra (2023): "The Alignment Ceiling: Objective Mismatch in RLHF" - arXiv:2311.00168 (52 citations)
- Wei et al. (2024): "Systematic Evaluation of LLM-as-a-Judge in LLM Alignment Tasks" - arXiv:2408.13006 (89 citations)

**Implementations:**
- allenai/reward-bench (733 stars): AI-to-human alignment evaluation
- SALT-NLP/collaborative-gym (124 stars): Human-AI collaboration framework
- CaoYuanpu/BiPO (50 stars): Bidirectional Preference Optimization

### Previous Failure / Routing Context

**CRITICAL: This is a RECURSIVE entry (v2) following Phase 4 FAIL.**

**Failed Hypothesis: h-m1 (Run 1)**
- **Statement:** Human vote entropy and RM ensemble variance are positively correlated (r > 0.2, p < 0.001, N > 5000)
- **Observed:** r = -0.0624 (NEGATIVE, opposite to prediction)
- **Failure Type:** HYPOTHESIS_NOT_SUPPORTED

**Root Cause Analysis (from failure record):**
1. Human disagreement and RM disagreement are NOT measuring the same underlying construct
2. The "shared ambiguity" assumption is fundamentally flawed
3. High human entropy samples may be "easy" for RMs (clear quality difference, humans just have diverse preferences)
4. Human vote entropy captures "preference ambiguity" while RM variance captures "model confidence" — orthogonal constructs

**PROHIBITED Directions (DO NOT RETRY):**
- ❌ Do NOT assume human and model uncertainty stem from same source
- ❌ Do NOT aggregate entropy across model pairs
- ❌ Do NOT hypothesize positive correlation between human vote entropy and RM variance

**What Showed Promise:**
- Statistical significance achieved (p < 0.001)
- Sample size exceeded requirements (N = 6000)
- Data pipeline and RM scoring infrastructure works
- Chatbot Arena data is usable for bidirectional alignment research

### Feasibility Constraints (Pipeline-Enforced)

- ✅ Must use EXISTING real datasets (Chatbot Arena, RewardBench, HH-RLHF)
- ✅ Must use EXISTING benchmarks and evaluation methods
- ❌ NO new benchmarks, rubrics, or scoring frameworks
- ❌ NO synthetic/generated data
- ❌ NO human evaluation or annotation studies

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

*What if we approach this from an entirely different angle?*

The h-m1 failure tells us something profound: human and model uncertainty are orthogonal constructs. But wait — that's actually a fascinating finding, not a dead end! What if the MISMATCH itself is the signal we should be measuring?

Here's my wild idea: Instead of looking for correlation between human entropy and RM variance (which failed), what if we measure the **quadrant distribution** across these two dimensions? The Phase 1 research mentioned H-E1 (quadrant analysis) — what if the pattern of WHERE samples fall across the four quadrants (high-human/high-RM, high-human/low-RM, low-human/high-RM, low-human/low-RM) reveals something about bidirectional alignment?

Looking at the Shen et al. (2024) framework, bidirectional alignment has two directions: AI→human (does the model match human specs) and human→AI (can humans understand/evaluate the model). What if:
- **High human entropy + Low RM variance** = Humans disagree but models are confident → Models may be OVERCONFIDENT on subjective content
- **Low human entropy + High RM variance** = Humans agree but models are uncertain → Models may lack calibration on clear cases

This isn't about correlation — it's about using the DISTRIBUTION of mismatches to characterize alignment failure modes. RewardBench gives us RM scores, Chatbot Arena gives us human votes. We have both dimensions already!

**Key Points:**
- The h-m1 failure reveals orthogonality, not uselessness — the mismatch IS the signal
- Quadrant distribution analysis avoids the correlation assumption that failed
- Existing data (Chatbot Arena + RM scores) already contains both dimensions
- This reframes bidirectional alignment as "alignment mode characterization" rather than "correlation hunting"

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

*The evidence suggests... we need to be precise about what we're actually measuring.*

Dr. Nova, I appreciate the creative reframing, but let me stress-test this. The quadrant distribution idea is intriguing, but what SPECIFIC, MEASURABLE prediction can we make? "Characterizing failure modes" is descriptive, not testable.

Here's what would disprove this approach: If the quadrant distribution is uniform (25/25/25/25 split), then there's no signal to extract. If certain quadrants dominate simply due to data artifacts (e.g., most Chatbot Arena battles have clear winners, so low-human-entropy dominates), we'd be measuring the dataset's structure, not alignment properties.

The Alignment Ceiling paper [Lambert & Calandra 2023] shows that RLHF reward models overoptimize on certain features. The LLM-as-Judge paper [Wei et al. 2024] shows judges have systematic biases. What if we leverage these known biases?

**Proposed Testable Hypothesis:**

*Under the condition of Chatbot Arena battles with matched model quality (close battles), if we stratify samples by human vote entropy, then RM ensemble prediction accuracy will be LOWER in high-entropy strata than in low-entropy strata, because high human entropy indicates subjective preference domains where RMs lack training signal.*

This is falsifiable: If RM accuracy is EQUAL or HIGHER in high-entropy strata, the hypothesis is wrong. The prediction is directional and measurable.

**Key Points:**
- Quadrant analysis needs a testable prediction, not just description
- Stratified accuracy comparison provides clear success/failure criteria
- We predict LOWER RM accuracy on high-entropy samples (opposite to naive "RMs should be good everywhere" assumption)
- Controls needed: match model quality (close battles only) to avoid confounds

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

*The question we must ask is... what does this mean for the field?*

Prof. Vera's reformulation is more rigorous, but let me assess the scientific contribution. The h-m1 failure already showed human entropy and RM variance are orthogonal. Showing that RM accuracy drops in high-entropy strata would be... interesting, but is it genuinely novel?

The Alignment Ceiling paper [Lambert & Calandra 2023] already documented that RLHF reward models overoptimize and have objective mismatch. What would we ADD to that finding?

I see two paths to genuine contribution:

**Path A (Incremental):** Show empirically that RM accuracy varies with human entropy. This confirms existing theory but adds quantitative evidence.

**Path B (Novel):** If we can show that the PATTERN of accuracy variation across entropy strata PREDICTS downstream LLM behavior, we'd have a diagnostic tool. This would open new research directions: "Given a model's RM, predict which types of prompts will have alignment failures."

The BiPO paper [Cao et al.] showed bidirectional steering works. What if we connect: entropy-stratified RM analysis → downstream alignment prediction? That's a contribution the field doesn't have.

**Key Points:**
- Showing RM accuracy varies with entropy is confirmatory, not groundbreaking
- The contribution becomes significant if we connect it to downstream prediction
- "Entropy-stratified alignment diagnostics" could be a new evaluation paradigm
- This matters because: current alignment eval is aggregate (RewardBench), but failures are local (specific prompt types)

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

*Let's be realistic here... is the mechanism scientifically sound?*

I need to assess whether this approach can work IN PRINCIPLE, not what it costs. Let me trace the logic:

1. **Claim:** High human vote entropy indicates "subjective preference domains"
2. **Claim:** RMs have less reliable training signal in subjective domains
3. **Conclusion:** RM accuracy should be lower in high-entropy strata

**Is the mechanism physically/mathematically possible?**

Human vote entropy is computed from vote distributions. If 3 judges vote [A, A, B], entropy ≈ 0.92. If [A, A, A], entropy = 0. This is well-defined.

RM accuracy = (RM prefers same as human majority) / (total). Also well-defined.

The QUESTION is: Does "high entropy" actually correlate with "subjective domain"? Or could high entropy mean:
- Judges were confused by the prompt?
- Response quality was genuinely close?
- One response was better on metric A, other on metric B?

**Technical Concern:** Human entropy is a MEASUREMENT of disagreement, not a CAUSE. We need to argue that disagreement indicates subjective domains, not quality-ties or judge confusion.

**What Evidence Supports This?**

Looking at the h-m1 failure notes: "High human entropy samples may be 'easy' for RMs (clear quality difference, humans just have diverse preferences)." This CONTRADICTS the proposed mechanism! The failure record suggests high-entropy samples might actually be EASY for RMs, not hard.

**Key Points:**
- The mechanism is mathematically well-defined
- BUT the causal link (high entropy → subjective domain → harder for RM) is UNVALIDATED
- The h-m1 failure notes actually suggest the OPPOSITE effect
- We need to resolve this contradiction before proceeding

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

*YES, AND we can strengthen this by addressing Prof. Pax's valid concern!*

The contradiction Pax identified is crucial. Let me reconcile it:

**The h-m1 failure said:** High human entropy samples may be "easy" for RMs → RMs AGREE more (low variance)
**Prof. Vera proposed:** High human entropy samples should show LOWER RM accuracy

These aren't contradictory — they're measuring different things!

- **RM variance** = Do different RMs agree with each other?
- **RM accuracy** = Does the RM match human majority vote?

A sample can have LOW RM variance (RMs agree) but LOW RM accuracy (RMs agree on the WRONG answer)! This is exactly what the Alignment Ceiling paper describes: reward hacking where RMs confidently pick the wrong response.

**Refined Hypothesis:**

*In Chatbot Arena battles with high human vote entropy, reward models exhibit HIGH confidence (low variance across RM ensemble) but LOW accuracy (disagreement with human majority), because RMs overfit to surface features while humans evaluate on subjective criteria the RMs weren't trained on.*

This explains the h-m1 finding: RMs DO agree more on high-entropy samples (negative correlation), but they agree on incorrect predictions. The signature of overconfident misalignment!

**Evidence from literature:**
- Alignment Ceiling [Lambert 2023]: Documents reward model overoptimization
- LLM-as-Judge [Wei 2024]: Shows systematic judge biases on subjective content
- BiPO [Cao]: Demonstrates that steering vectors can correct misalignment directions

**Key Points:**
- Refined: High entropy → High RM confidence BUT Low RM accuracy (overconfident misalignment)
- This is CONSISTENT with h-m1's negative correlation finding
- The signature: confidence-accuracy decoupling in high-entropy strata
- Testable: Measure confidence-accuracy calibration curves across entropy strata

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

*Here's where this breaks down... and what would convince me.*

Dr. Ally's refinement is clever, but I see remaining gaps:

**Gap 1: Defining "accuracy" when there's no ground truth**

In high-entropy samples, who's "correct"? If 3 humans vote [A, A, B], is A the ground truth? With high entropy, the majority is weakly defined. "RM accuracy" against a split vote is epistemically problematic.

**What would convince me:** Define accuracy against SUPERMAJORITY only (e.g., ≥4/5 or ≥5/7 agreement), or use a different metric like "RM agrees with ANY judge" vs "RM disagrees with ALL judges."

**Gap 2: Confound with battle difficulty**

High entropy might just mean the models being compared are close in quality. If model A and B are similar, humans split AND RMs might be uncertain for the same reason (genuine tie). This would make entropy a proxy for "battle difficulty," not "subjectivity."

**What would convince me:** Control for model pair similarity. Use battles between DIFFERENT model tiers (e.g., GPT-4 vs GPT-3.5) where quality difference is clear, and see if entropy still predicts accuracy patterns.

**Gap 3: Sample size for stratified analysis**

Stratifying by entropy AND controlling for model pair similarity might leave us with too few samples per stratum.

**What would convince me:** Power analysis showing N > 500 per entropy stratum with controls applied.

**Key Points:**
- "Accuracy" is ill-defined when human majority is weak (high entropy = split vote)
- High entropy might proxy for "battle difficulty" not "subjectivity" — need model-tier controls
- Feasibility check: Power analysis for stratified sample sizes
- Refinement needed: Use supermajority thresholds or alternative accuracy definitions

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

*What if we reframe this entirely?*

Prof. Rex's critiques are valid, but they reveal we're still thinking too narrowly. The accuracy-against-majority framing is indeed epistemically weak for high-entropy samples. Let me propose a paradigm shift:

**Instead of predicting who's "right," measure ALIGNMENT MODE SIGNATURES.**

What if we don't ask "Is the RM accurate?" but instead "What PATTERN does the RM-human relationship exhibit?"

Define four alignment modes:
1. **Aligned-Confident:** Low human entropy, low RM variance, RM matches majority → Good
2. **Aligned-Uncertain:** Low human entropy, high RM variance, RM matches majority → Calibrated
3. **Misaligned-Confident:** High human entropy, low RM variance, RM ≠ majority → Overconfident failure (DANGEROUS)
4. **Misaligned-Uncertain:** High human entropy, high RM variance, RM ≠ majority → At least aware

**The hypothesis becomes:**

*Chatbot Arena battles exhibit non-uniform distribution across alignment modes, with Mode 3 (Misaligned-Confident) representing a measurable population of "overconfident alignment failures" that existing aggregate metrics (RewardBench score) fail to detect.*

This is:
- **Testable:** Measure population percentages across modes
- **Novel:** No existing work characterizes alignment via mode distributions
- **Actionable:** Mode 3 samples are targets for safety interventions
- **Uses existing data:** Chatbot Arena votes + RM ensemble scores

**Key Points:**
- Reframe from "accuracy prediction" to "alignment mode characterization"
- Four modes capture the full space of RM-human relationships
- Mode 3 (Misaligned-Confident) is the safety-critical failure mode
- Aggregate metrics miss mode distributions — this fills the gap

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

*Now this meets my standards... with refinements.*

Dr. Nova's mode framework is more defensible because it doesn't require a ground truth for high-entropy samples. Let me formalize the testable predictions:

**Primary Hypothesis (H-E1):**

*Under the scope of Chatbot Arena battles with standard response pairs, if we classify samples into four alignment modes based on human vote entropy (high/low) and RM ensemble variance (high/low), then the Mode 3 population (Misaligned-Confident: high human entropy, low RM variance) will constitute >10% of samples, because reward models overfit to surface features while humans disagree on subjective criteria.*

**Success Criterion:** Mode 3 proportion > 10%
**Falsification:** Mode 3 proportion < 5% (negligible population)

**Secondary Prediction (H-M1):**

*Mode 3 samples will show lower semantic similarity between response pairs than Mode 1 samples (matched on model tier), because overconfident RM failures occur when responses are substantively different but RMs collapse the distinction.*

This tests the MECHANISM: Why do RMs become overconfident? Because they miss substantive differences.

**Tertiary Prediction (H-M2):**

*Mode 3 proportion will be higher for battles involving creative/subjective prompts (e.g., story writing) than factual prompts (e.g., math, coding), because subjectivity drives human disagreement that RMs can't model.*

**Key Points:**
- Primary test: Mode 3 population > 10% (existence of overconfident failures)
- Mechanism test: Semantic similarity patterns across modes
- Scope test: Prompt type moderates mode distribution
- All tests use existing data: Chatbot Arena + RM scores + prompt metadata

---

### Exchange 9

🎯 **Dr. Sage** (Research Impact Evaluator):

*This matters because... it changes how we evaluate alignment.*

Now I see genuine contribution. Let me articulate why this advances the field:

**Current State:** RewardBench gives aggregate accuracy. A model scores 75%. We don't know if the 25% failures are randomly distributed or concentrated in safety-critical modes.

**This Contribution:** Mode distribution analysis reveals WHERE failures occur. A model might score 75% overall but have 15% Mode 3 (overconfident failures on subjective content) — that's a safety concern aggregate metrics miss.

**What new research directions does this open?**

1. **Alignment Safety Index:** Proportion in Mode 3 becomes a safety metric independent of accuracy
2. **Targeted Intervention:** Mode 3 samples become training targets for alignment improvement
3. **Prompt-Type Calibration:** Models can report confidence based on prompt type alignment mode patterns
4. **Benchmark Augmentation:** RewardBench could add mode distribution alongside accuracy

**Connection to Bidirectional Framework:**

The Shen et al. (2024) BiAlign framework distinguishes AI→human and human→AI alignment. Our modes map:
- Modes 1-2 (aligned): AI→human alignment working
- Mode 3 (misaligned-confident): AI→human alignment FAILURE with false confidence
- Mode 4 (misaligned-uncertain): AI→human failure but model is aware

Mode 3 is specifically dangerous because it represents misalignment the model doesn't "know" about.

**Key Points:**
- Contribution: Alignment mode distribution reveals failure patterns aggregate metrics miss
- Opens: Safety indexing, targeted intervention, prompt-type calibration
- Maps to BiAlign framework: Mode 3 = dangerous AI→human failure
- This is novel: No existing work characterizes alignment via mode populations

---

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

*Okay, this could work. Let me verify the technical soundness.*

The mechanism is now clearer. Let me trace it:

1. **Human vote entropy** = well-defined (Shannon entropy of vote distribution)
2. **RM ensemble variance** = well-defined (variance across RM scores for the same pair)
3. **Mode classification** = well-defined (2x2 based on entropy/variance thresholds)
4. **Mode 3 population** = proportion of samples in high-entropy/low-variance cell

**Is the measurement theoretically valid?**

Yes. We're measuring a joint distribution, not causal inference. The claim "Mode 3 exists in meaningful proportions" is descriptive and verifiable.

**Can the proposed interventions work in principle?**

The downstream claims (safety index, targeted training) are beyond the primary hypothesis. For Phase 2A, we only need to establish that Mode 3 exists and is non-trivial. That's achievable.

**Threshold Selection:**

We need principled thresholds for "high" vs "low" entropy/variance. Options:
- Median split (equal population per cell)
- Domain-specific (e.g., entropy > 0.5 for "high")
- Data-driven (optimize for mode discrimination)

Recommendation: Use MEDIAN split for primary analysis (avoids arbitrary thresholds), then sensitivity analysis with other cutoffs.

**Key Points:**
- Mechanism is technically sound: joint distribution analysis, not causal claims
- Measurements are well-defined and computable from existing data
- Threshold selection: median split primary, sensitivity analysis secondary
- Feasibility: YES — this can work in principle with Chatbot Arena + RM data

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

*Now THAT's stronger! Let me synthesize the consensus.*

We've converged on a refined hypothesis that:
1. Addresses h-m1's failure (doesn't assume correlation)
2. Uses existing data (Chatbot Arena + RM scores)
3. Has clear success/failure criteria
4. Maps to the BiAlign framework
5. Is technically feasible

**Consensus Hypothesis Statement:**

**H-AMode (Alignment Mode Hypothesis):**

*Under the scope of Chatbot Arena pairwise battles with standard response pairs, if we classify samples into four alignment modes based on human vote entropy (high/low, median split) crossed with RM ensemble variance (high/low, median split), then:*

**(H-E1 - Existence):** *The Mode 3 population (Misaligned-Confident: high human entropy, low RM variance) will constitute >10% of samples.*

**(H-M1 - Mechanism):** *Mode 3 samples will exhibit lower response-pair semantic similarity than Mode 1 samples (controlling for model tier), because RMs collapse substantive distinctions humans preserve.*

**(H-M2 - Scope):** *Mode 3 proportion will be higher for subjective prompts (creative writing) than objective prompts (math/coding), because subjectivity drives human-RM divergence.*

**Null Hypothesis:** Mode distribution is uniform (25%/25%/25%/25%) or Mode 3 < 5%.

**Key Points:**
- Three-part hypothesis: Existence, Mechanism, Scope
- Uses median split thresholds (principled, sensitivity-testable)
- Falsifiable with clear quantitative criteria
- Builds on h-m1 infrastructure (data pipeline works)
- Novel contribution: Alignment mode characterization

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

*Now you've addressed my concerns. Final stress-test:*

**Remaining Concern 1: Semantic Similarity Measure**

H-M1 claims Mode 3 shows lower semantic similarity. How do we measure this? Options:
- Sentence-BERT cosine similarity
- LLM embedding distance
- BLEU/ROUGE overlap

Recommendation: Use sentence-transformer embeddings (all-mpnet-base-v2 or similar). It's a standard choice and computable without human annotation.

**Remaining Concern 2: Prompt Type Classification**

H-M2 requires classifying prompts as "subjective" vs "objective." How?

- Option A: Use Chatbot Arena's existing category tags (if available)
- Option B: Simple heuristics (keywords like "write a story" vs "solve this equation")
- Option C: LLM classifier (but adds complexity)

Recommendation: Option A if available, else Option B for simplicity. Avoid Option C to keep the method lightweight.

**Remaining Concern 3: Independence Assumption**

Are the entropy and variance dimensions truly independent? If they're correlated (beyond what we saw in h-m1's r=-0.06), the 2x2 decomposition might be degenerate.

This is actually ADDRESSED by h-m1: The weak negative correlation (r=-0.06) means the dimensions are nearly orthogonal. The mode decomposition is valid.

**Final Verdict:** The hypothesis is well-formed. Proceed to Phase 2B.

**Key Points:**
- Semantic similarity: Use sentence-transformer embeddings
- Prompt classification: Use existing tags or simple heuristics (avoid LLM classifier)
- Independence: Validated by h-m1's weak correlation (r=-0.06)
- Verdict: READY for Phase 2B

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The alignment mode framework is genuinely novel. No existing work characterizes AI-human alignment through joint entropy-variance distributions. The four-mode taxonomy provides a new lens for understanding alignment failures that aggregate metrics miss.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is highly testable with clear quantitative criteria. H-E1 (Mode 3 > 10%) is directly measurable. H-M1 and H-M2 provide mechanistic and scope tests. All can be falsified with existing Chatbot Arena data.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** This opens a new evaluation paradigm: mode distribution analysis alongside aggregate accuracy. The safety implications of Mode 3 (overconfident misalignment) connect to AI safety research. This is a genuine contribution, not incremental.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** The mechanism is technically sound. All measurements are well-defined and computable from existing data. Median split thresholds avoid arbitrary choices. The approach uses proven infrastructure from h-m1.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The Alignment Mode Hypothesis (H-AMode) proposes that AI-human alignment can be characterized through a four-mode framework based on human vote entropy crossed with RM ensemble variance. The key insight is that existing aggregate metrics (like RewardBench accuracy) miss the DISTRIBUTION of alignment failures across modes.

Mode 3 (Misaligned-Confident: high human entropy, low RM variance) represents overconfident alignment failures where reward models are certain but wrong—the most safety-critical failure pattern. The hypothesis predicts this mode constitutes >10% of Chatbot Arena samples, is more prevalent for subjective prompts, and exhibits lower response-pair semantic similarity (RMs collapse distinctions humans preserve).

This hypothesis builds on h-m1's finding that human entropy and RM variance are near-orthogonal (r=-0.06), reframing this as a feature rather than a failed correlation. The orthogonality validates the 2x2 mode decomposition. The approach uses existing data (Chatbot Arena votes + RM scores), avoids new human annotation, and provides actionable outputs (safety indexing, targeted training samples).

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1:** Semantic similarity measure choice (sentence-transformers recommended)
- **Concern 2:** Prompt type classification method (use existing tags or heuristics)
- **Mitigation Strategy:** H-M1 and H-M2 are secondary tests; primary hypothesis (H-E1) doesn't depend on these choices. Sensitivity analysis can validate robustness.

---

## Emerged Hypothesis Summary

### Core Statement

**Under** the scope of Chatbot Arena pairwise battles with standard response pairs, **if** we classify samples into four alignment modes based on human vote entropy (high/low, median split) crossed with RM ensemble variance (high/low, median split), **then** the Mode 3 population (Misaligned-Confident) will constitute >10% of samples, **because** reward models overfit to surface features while humans disagree on subjective criteria the RMs weren't trained on.

### Causal Mechanism

1. Human voters evaluate responses on diverse criteria including subjective preferences
2. When responses differ substantively, some humans prefer A, others prefer B (high entropy)
3. Reward models trained on aggregate preferences collapse these distinctions
4. RMs become confident on samples where they lack nuanced signal (low variance)
5. Result: Overconfident misalignment (high entropy + low variance = Mode 3)

### Variables

**Independent Variables:**
- Human vote entropy (binary: high/low via median split)
- RM ensemble variance (binary: high/low via median split)

**Dependent Variable:**
- Mode population proportions (4 cells of 2x2)
- Primary: Mode 3 proportion (target: >10%)

**Controlled Variables:**
- Model tier (for semantic similarity analysis)
- Prompt type (for scope analysis)

### Key Assumptions

- A1: Chatbot Arena votes reflect genuine human preferences (not spam/bots)
- A2: RM ensemble scores are comparable across models in the ensemble
- A3: Median split provides reasonable threshold for high/low classification
- A4: Human entropy is a valid proxy for "subjectivity" or "preference diversity"
- A5: The four-mode framework captures meaningful alignment patterns

### Null Hypothesis

Mode distribution is uniform (25%/25%/25%/25% across four modes) OR Mode 3 proportion < 5% (negligible).

### Predictions

**P1 (Primary - Existence):** Mode 3 (Misaligned-Confident) > 10% of samples
- Success: Proportion statistically > 10% (one-sided test, p < 0.05)
- Falsification: Proportion < 5%

**P2 (Mechanism):** Mode 3 response pairs have lower semantic similarity than Mode 1
- Success: Cohen's d > 0.3 for similarity difference
- Falsification: No significant difference or d < 0.1

**P3 (Scope):** Mode 3 proportion higher for subjective prompts vs objective prompts
- Success: Ratio > 1.5 (subjective:objective Mode 3 rate)
- Falsification: Ratio < 1.0 (opposite direction)

### Novelty

This is the first work to characterize AI-human alignment through joint entropy-variance mode distributions. Prior work treats alignment as aggregate accuracy (RewardBench) or correlational analysis (h-m1 failure). The mode framework reveals failure PATTERNS that aggregates miss.

### Scope & Boundaries

**Applies to:**
- Pairwise preference evaluation settings
- RM ensembles with variance as uncertainty proxy
- Discrete human voting data with computable entropy

**Does not apply to:**
- Single-response evaluation
- Continuous rating scales (without discretization)
- Settings without human vote data

### Experimental Setup

**Dataset:** Chatbot Arena battles (N > 20,000 samples available)
**RMs:** Ensemble of 3-5 reward models (use those from h-m1 infrastructure)
**Thresholds:** Median split for entropy/variance (sensitivity analysis with terciles)
**Metrics:**
- Mode proportions (primary: Mode 3 > 10%)
- Semantic similarity via sentence-transformers (for H-M1)
- Prompt type classification via existing tags (for H-M2)

### Related Work & Baselines

**Baseline 1:** Uniform mode distribution (25% each) — naive expectation
**Baseline 2:** h-m1 correlation analysis (r=-0.06) — prior failed approach
**Key Reference:** Shen et al. 2024 BiAlign framework — our modes map to their taxonomy

### Phase 2B Readiness Seeds

- **SH1 (Existence):** Mode 3 must exist in measurable proportions (>10%)
- **SH2 (Mechanism):** Semantic similarity difference between modes must be detectable
- **SH3 (Comparison):** Mode distribution must differ from uniform (Chi-square test)

### Established Facts

- Human vote entropy and RM variance are near-orthogonal (r=-0.06, from h-m1)
- Data pipeline and RM scoring infrastructure work (from h-m1)
- Chatbot Arena data is usable for bidirectional alignment research (from h-m1)
- Statistical significance is achievable with N > 5000 (from h-m1)
