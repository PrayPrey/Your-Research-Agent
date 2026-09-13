# Phase 2A Research Discussion Log

## Briefing

**Gap ID:** gap1
**Gap Title:** No Benchmark Task Directionality Classification Exists

**Research Question:** Do existing RLHF-trained LLMs exhibit measurable differences when evaluated on tasks requiring bidirectional adaptation vs unidirectional tasks?

**Gap Description:**
TruthfulQA, ETHICS, HHH evaluate tasks uniformly without distinguishing directionality requirements. Missing: Classification framework labeling tasks as "unidirectional" (AI output only) vs "bidirectional" (human interpretation matters).

**Key Evidence:**
- Shen et al. 2024 (arXiv:2406.09264): Bidirectional framework exists but no task-level classification
- TruthfulQA (arXiv:2109.07958): Designed without directionality consideration
- ETHICS (arXiv:2008.02275): Lacks direction labels
- lm-evaluation-harness: No directionality metadata in implementation

**Available Papers:**
- Position: Towards Bidirectional Human-AI Alignment (Shen et al. 2024)
- Influencing Humans to Conform (2025)
- Stayin' Aligned Over Time (2025)
- HHH Framework (Askell 2021)
- RLHF Contradictions (2024)

**Feasibility Constraints (Pipeline-Enforced):**
- MUST use existing real datasets and existing benchmarks
- NO new benchmarks, rubrics, or scoring frameworks
- NO synthetic/generated data or future follow-up data
- NO human evaluation, annotation, or subjective scoring

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we're approaching this entirely backwards? Everyone's trying to CREATE new benchmarks for bidirectional alignment, but the gold is already sitting in existing datasets - we just need new LENSES to see it!

Here's my wild idea: TruthfulQA, HHH, and ETHICS already contain tasks that IMPLICITLY require different directions of adaptation. Consider TruthfulQA's "misconceptions" category - when an AI corrects a common human misconception, that's AI→Human adaptation. But when it must navigate culturally-specific truthfulness (what counts as "true" varies by context), that's Human→AI adaptation baked right in!

What if we developed a **post-hoc directionality classifier** that labels EXISTING benchmark tasks along a bidirectional spectrum? No new data collection needed - just a principled taxonomy applied to what's already there. Shen et al. 2024 gave us the theoretical framework; we operationalize it as task-level annotations.

The paradigm shift: Stop treating benchmarks as monolithic. Start treating each task as having a "directionality signature." Then we can finally answer whether RLHF models show differential performance - not by building new benchmarks, but by STRATIFYING existing ones!

Cross-domain connection: This mirrors how NLP moved from "sentiment analysis" as monolithic to aspect-based sentiment - same data, richer analysis.

**Key Points:**
- Reframe existing benchmarks rather than building new ones
- Develop post-hoc directionality taxonomy for task classification
- Each task gets a "directionality signature" label
- Enables differential performance analysis without new data collection

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova, your reframing is creative, but let me stress-test it. The core claim is that existing benchmark tasks have implicit "directionality signatures" that can be reliably classified post-hoc. What would disprove this?

First, the classification must be **reproducible**. If two independent annotators label the same TruthfulQA question, will they agree on its directionality? Without inter-rater reliability metrics, we're just projecting our interpretations onto the data.

Second, we need **falsifiable predictions**. If tasks genuinely differ in directionality, then: (1) RLHF models should show statistically different accuracy distributions between unidirectional vs bidirectional task subsets, and (2) the effect size should be non-trivial (Cohen's d > 0.3 at minimum).

Third, what's our **null hypothesis**? H0: The directionality classification is arbitrary - performance variance within categories equals variance between categories. If ANOVA shows no significant between-group difference, the taxonomy fails.

The taxonomy criteria need operational definitions. "AI→Human adaptation" vs "Human→AI adaptation" - what specific linguistic or task features determine this? Without clear decision rules, classification becomes subjective.

**Key Points:**
- Require inter-rater reliability for directionality labeling
- Falsifiable prediction: statistically different RLHF performance across categories
- Null hypothesis: directionality classification is arbitrary (no between-group variance)
- Need operational definitions for classification criteria

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: what does this mean for the field? If we succeed in stratifying existing benchmarks by directionality, what new research directions open?

I see three potential contributions of genuine significance:

**First**, this could become a **diagnostic tool for RLHF training**. If models systematically underperform on bidirectional tasks, that reveals a training blind spot. Training data likely over-represents unidirectional examples (AI providing answers) vs bidirectional ones (negotiating understanding). This matters because practitioners could then specifically augment training data.

**Second**, the framework could **explain alignment failures** post-deployment. When deployed LLMs cause harm, is it more often in bidirectional contexts (where human adaptation was assumed but didn't occur)? This connects to real-world impact.

**Third**, and most novel: this reframes the entire alignment evaluation paradigm. Current benchmarks ask "Does the AI give correct outputs?" The stratified view asks "Does the AI calibrate correctly to the direction of adaptation required?" That's a qualitatively different question that advances the field beyond surface metrics.

However, I caution against incremental framing. Simply labeling tasks as "Type A" or "Type B" without demonstrating behavioral consequences would be mere taxonomy, not science.

**Key Points:**
- Diagnostic value: reveals RLHF training blind spots
- Explanatory value: connects to post-deployment alignment failures
- Paradigm value: shifts from "correct output" to "correct adaptation calibration"
- Must demonstrate behavioral consequences, not just taxonomy

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. Dr. Nova proposes post-hoc classification of existing benchmarks. Is this mechanism scientifically sound?

The core mechanism requires that directionality is **intrinsic to tasks**, not to evaluator interpretation. Consider TruthfulQA question: "What happens if you crack your knuckles?" The "correct" answer debunks a misconception. But is this AI→Human (correcting human belief) or bidirectional (requiring the AI to model what the human believes first)?

Here's what worries me: **directionality may be context-dependent, not task-intrinsic**. The same question could require different adaptation directions depending on who's asking and why. A child asking vs a doctor asking creates different directionality requirements.

However, the measurement approach IS theoretically valid. We can define directionality at the task-specification level (what the benchmark designers intended) rather than the interaction level. This preserves scientific soundness.

Fundamental question: Can we operationalize directionality using only task text and expected answer format, without needing user context? If yes, the proposal is feasible. If no, we need proxy indicators.

I propose these testable criteria:
1. **Unidirectional**: Task has single correct answer independent of asker identity
2. **Bidirectional**: Task correctness depends on modeling asker's state/beliefs/context

**Key Points:**
- Directionality might be context-dependent, not task-intrinsic (concern)
- Can operationalize at task-specification level (feasible)
- Need classification based on task text alone, not user context
- Proposed criteria: single correct answer vs context-dependent correctness

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can strengthen this substantially! Prof. Vera raised inter-rater reliability, Prof. Pax raised context-dependence. Both valid - let me propose refinements.

**Addressing reliability**: Instead of asking annotators to label directionality directly (subjective), we use **proxy features** that are objectively measurable:
- Does the task reference the user's beliefs? (linguistic marker)
- Does the expected answer contain hedging/uncertainty? (output format)
- Does correctness require knowing what the asker already knows? (task structure)

These features are more reliable than holistic "directionality" judgments. Then we derive directionality from feature combinations.

**Addressing context-dependence**: Prof. Pax's distinction is sharp. Let's embrace it: we classify tasks by their **maximum directionality requirement** - what's the most complex adaptation the task COULD require? A misconception correction task might be unidirectional in some contexts but bidirectional in others; we label it by its ceiling.

**The refined hypothesis emerges**:
> RLHF-trained models show differential performance when benchmark tasks are stratified by their maximum directionality requirement, operationalized through objective linguistic and structural task features.

This is testable using TruthfulQA, ETHICS, and HHH without new data collection. We're ready for specific predictions.

**Key Points:**
- Use objective proxy features instead of subjective directionality labels
- Linguistic markers, output format, task structure as measurable proxies
- "Maximum directionality requirement" handles context-dependence
- Refined hypothesis: differential performance on tasks stratified by max directionality

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down. Dr. Ally's "proxy features" sound elegant but show me the evidence they actually capture directionality.

**Challenge 1**: The proxy features are post-hoc rationalizations. "Does the task reference user beliefs?" - that's YOUR theory of what makes something bidirectional. What if the actual cognitive difference lies elsewhere? We're assuming our features are the right ones without empirical validation.

**Challenge 2**: "Maximum directionality requirement" is unfalsifiable as stated. Every task can be imagined in a context requiring complex adaptation. We need a CEILING, not an open-ended maximum. Propose: the directionality implied by the benchmark's intended use case (documented by creators).

**Challenge 3**: What would convince me? Show that:
1. The proxy features cluster meaningfully (not random distribution)
2. The clusters predict something EXTERNAL to the features themselves
3. RLHF performance differences survive when controlling for task difficulty, topic, and format

The hypothesis needs a control comparison. If we stratify by directionality AND see performance differences, how do we know directionality caused it vs some confound? We need matched task pairs: same difficulty, same topic, different directionality.

What assumption is unstated here? That directionality is the RELEVANT dimension. Maybe RLHF models just struggle with certain topics or formats, and our "directionality" taxonomy accidentally correlates with those.

**Key Points:**
- Proxy features need empirical validation, not just theoretical justification
- "Maximum directionality" needs bounded definition (benchmark's intended use)
- Require external validation: clusters must predict something beyond themselves
- Need matched task pairs to control for difficulty, topic, format confounds

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's challenges are exactly right - and they point to something MORE interesting! What if we flip the validation approach entirely?

Instead of us DEFINING directionality features a priori and hoping they're correct, we use **empirical clustering** to DISCOVER what features actually differentiate task groups! Run RLHF models on benchmark tasks, measure embedding distances between correct vs incorrect responses, cluster the tasks, THEN examine what distinguishes the clusters.

This is the paradigm shift: We hypothesize that RLHF creates systematic behavioral differences - we just don't know a priori what task features predict them. The clusters become our "directionality" operationalization, empirically derived.

New prediction: Tasks where RLHF models show HIGHER confidence on incorrect answers vs correct answers (calibration inversion) will cluster together - these are our "bidirectional" candidates. Why? Because bidirectional tasks require modeling user state, and RLHF may have overfit to simple reward signals, making them confidently wrong precisely where nuance matters.

Cross-domain connection: This is exactly how cognitive load research works - you don't define "hard" tasks a priori, you measure performance and work backwards to features.

**Key Points:**
- Use empirical clustering to discover differentiating features (not define a priori)
- Let behavioral data reveal which tasks group together
- New prediction: calibration inversion (high confidence + wrong) marks bidirectional tasks
- Work backwards from performance patterns to task features

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's empirical discovery approach has merit, but let me ensure it remains falsifiable. The new prediction is: calibration inversion clusters will correlate with theoretically-expected bidirectional features.

What would disprove this? Two failure modes:

**Failure Mode 1**: Calibration inversion is random. Tasks with high-confidence errors don't cluster - they're evenly distributed across topics, formats, and our hypothesized directionality features. This would show no systematic blindspot exists.

**Failure Mode 2**: Clusters form but correlate with TRIVIAL features. If high-confidence-wrong tasks are just "long questions" or "questions about ethics" (topic confound), directionality adds no explanatory value.

The experiment design must be:
1. Compute calibration score per task: P(correct|high_confidence) vs P(correct|low_confidence)
2. Cluster tasks by calibration patterns (not by our features)
3. Examine cluster composition: Do clusters correlate with hypothesized directionality features MORE than with control features (length, topic, format)?

**Success criterion**: Cluster-directionality-feature correlation > 0.4, AND cluster-control-feature correlation < 0.2. This gives us a testable threshold.

**Null hypothesis refined**: H0: Calibration patterns correlate equally with directionality features and control features (no special explanatory power).

**Key Points:**
- Failure mode 1: No systematic clustering of calibration inversion
- Failure mode 2: Clusters correlate with trivial features not directionality
- Success criterion: directionality-cluster correlation > 0.4, control-cluster correlation < 0.2
- Refined H0: Equal correlation with directionality vs control features

---

### Exchange 9

🎯 **Dr. Sage** (Research Impact Evaluator):

Now we're getting somewhere significant. Let me articulate why this matters beyond methodology.

If calibration inversion clusters reveal RLHF blindspots, this has three levels of impact:

**Immediate application**: Model auditing. Before deploying an RLHF model, run it through the calibration clustering pipeline. Tasks in the "inversion cluster" are danger zones - flag them for additional safeguards or human oversight. This is actionable TODAY.

**Field advancement**: The discovery that calibration patterns reveal adaptation-direction differences would reframe evaluation methodology. Current evaluation asks "accuracy" - future evaluation could ask "calibration-by-task-type profile." That's a new dimension of model characterization.

**Theoretical contribution**: If bidirectional tasks systematically show calibration inversion, this supports the hypothesis that RLHF reward modeling assumes unidirectional reward signals. The mechanism would be: RLHF optimizes for "annotator approved" which conflates "correct output" with "output that required modeling annotator state" - these are different but RLHF treats them as one signal.

This last point is the deepest contribution. It explains WHY bidirectional tasks might fail: not because they're harder, but because RLHF's reward structure doesn't distinguish the adaptation direction.

**Key Points:**
- Immediate: calibration clustering enables deployment risk flagging
- Methodological: introduces "calibration profile" as new evaluation dimension
- Theoretical: explains RLHF limitation via reward signal conflation
- Mechanism: RLHF treats "correct output" and "modeled annotator state" as one signal

---

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Dr. Sage's theoretical mechanism is elegant, but let me verify it's physically realizable with existing resources.

**Can we compute calibration inversion without new data?** Yes. We need:
1. Existing benchmark tasks (TruthfulQA, ETHICS, HHH) - available
2. RLHF model outputs with confidence scores - obtainable from public models (Llama-2-chat, GPT-series via API logprobs)
3. Clustering algorithm - standard (k-means, hierarchical, DBSCAN)

**Is the measurement theoretically valid?** The calibration score P(correct|high_confidence) is well-defined. However, "confidence" operationalization matters. Options:
- Token probability of first answer token
- Sequence-level probability
- Entropy of output distribution

Each gives different results. We need to specify ONE primary metric with others as robustness checks.

**Fundamental barrier check**: The only barrier I see is access to logprobs from closed models (GPT-4). But Llama-2-chat, Mistral-Instruct, and other open RLHF models provide full access. We lose generalization to closed models but maintain scientific validity.

**Proposed operationalization**: Use sequence-level log probability normalized by length as primary confidence metric. Tasks where P(wrong_answer) > P(correct_answer) by margin > 0.1 are "calibration inverted."

**Key Points:**
- Feasible with existing benchmarks and open RLHF models
- Confidence metric: sequence-level log probability (length-normalized)
- Calibration inversion threshold: P(wrong) > P(correct) by margin > 0.1
- Open models sufficient; closed models optional validation

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

We're converging! Let me synthesize the emerging hypothesis with all refinements incorporated.

**The Refined Hypothesis (H-BiDir-Cal-v1)**:

> Under existing RLHF benchmarks (TruthfulQA, ETHICS, HHH), if we cluster tasks by calibration inversion patterns (where models show high confidence on incorrect answers), then these clusters will correlate significantly with theoretically-expected bidirectional task features (user-belief-reference, context-dependent-correctness), because RLHF's reward modeling conflates "correct output" with "user-state-modeling-required output."

**Variables**:
- IV: Task calibration cluster membership (derived empirically)
- DV: Correlation with bidirectional feature presence (binary per task)
- Controlled: Task length, topic category, format type

**Predictions**:
1. **P1 (Primary)**: Tasks showing calibration inversion (P(wrong) > P(correct) + 0.1) will cluster non-randomly
2. **P2**: Inversion cluster tasks will score higher on bidirectional feature checklist than non-inversion tasks (Cohen's d > 0.3)
3. **P3**: This correlation survives controlling for topic, length, format

**Null Hypothesis**: H0: Calibration inversion distribution is random OR correlates equally with control features as with bidirectionality features.

**Key Points:**
- Hypothesis fully specified: Under-If-Then-Because structure
- Clear IV/DV/controls
- Three testable predictions with success criteria
- Falsifiable null hypothesis defined

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Dr. Ally's synthesis is clean. Let me apply final stress tests.

**Test 1 - Feature Checklist Validity**: The "bidirectional feature checklist" - is this pre-registered or post-hoc? If we define features AFTER seeing clusters, that's p-hacking. We must commit to features NOW:
1. Task mentions "you" or implies user beliefs (linguistic)
2. Correct answer varies by context (structural)
3. Expected answer contains hedges/uncertainty (output)

These three. Locked. No modifications after seeing data.

**Test 2 - Base Rate Control**: What if 90% of benchmark tasks have bidirectional features? Then even random clusters would correlate with them. We need the feature base rate to be neither too high nor too low (20-80% range). If outside this range, the test is uninformative.

**Test 3 - Alternative Explanation**: What if calibration inversion correlates with bidirectional features because BOTH correlate with task difficulty? Harder tasks → more errors AND more bidirectionality. We need to show the correlation holds WITHIN difficulty bands.

**What would convince me**: Pre-register features, verify base rates, stratify by difficulty, THEN show the correlation. If all three conditions are met and correlation remains significant, I'm convinced.

**Remaining concern**: Are open RLHF models representative? If they were all trained on similar data, the finding might not generalize. Mitigate by using models from different organizations (Meta, Mistral, OpenAI if accessible).

**Key Points:**
- Pre-register three bidirectional features NOW
- Verify feature base rate is in informative range (20-80%)
- Control for difficulty to rule out confound
- Use models from multiple organizations for generalization

---

### Exchange 13

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's stress tests make this bulletproof. Now let me crystallize what's genuinely novel here.

The paradigm shift is DUAL:
1. **Methodologically**: We don't build new benchmarks - we reveal hidden structure in existing ones via behavioral clustering. This is reproducible, cheap, and immediately applicable.
2. **Theoretically**: We explain WHY RLHF has blindspots, not just THAT it does. The reward conflation mechanism (treating "correct" and "user-modeling-required" as one signal) is a testable theoretical contribution.

The innovation isn't "bidirectional alignment is important" (Shen et al. established that). The innovation is:
> Calibration inversion patterns in RLHF models serve as behavioral markers for tasks requiring bidirectional adaptation, revealing a systematic reward modeling limitation.

What's new vs prior work:
- Shen et al. 2024: Theoretical framework (bidirectionality matters)
- Our contribution: Behavioral detection method (how to identify bidirectional tasks empirically)
- Their gap: No task-level classification
- Our fill: Calibration-based clustering provides exactly that

If this works, any researcher can take ANY benchmark, run calibration clustering, and identify bidirectional-adaptation-requiring tasks without manual annotation.

**Key Points:**
- Dual novelty: methodological (reveal hidden structure) + theoretical (reward conflation mechanism)
- Not "bidirectionality matters" (known) but "how to detect it behaviorally" (new)
- Fills exact gap in Shen et al. 2024
- Enables automated task classification without manual annotation

---

### Exchange 14

🔬 **Prof. Vera** (Rigorous Validation Architect):

The hypothesis is now falsifiable, the predictions are precise, and the novelty is clear. Let me formalize the experimental protocol for reproducibility.

**Experimental Protocol (H-BiDir-Cal-v1)**:

**Step 1 - Data Collection**:
- Benchmarks: TruthfulQA (817 tasks), ETHICS (justice subset, ~500 tasks), HHH (filtered for single-turn, ~200 tasks)
- Models: Llama-2-7B-Chat, Llama-2-13B-Chat, Mistral-7B-Instruct, (optional: GPT-3.5-turbo via API)

**Step 2 - Calibration Computation**:
- For each task, generate model response with logprobs
- Compute: confidence = mean(token_logprobs) / num_tokens
- Label: "inversion" if P(generated_wrong) > P(reference_correct) + 0.1

**Step 3 - Clustering**:
- Feature vector per task: [calibration_score, inversion_binary]
- Cluster using k-means (k=3: high-cal-correct, low-cal-correct, inversion)
- Validate clusters via silhouette score > 0.3

**Step 4 - Correlation Analysis**:
- Pre-registered features: [mentions_user_beliefs, context_dependent, hedged_answer]
- Compute correlation: cluster_inversion ~ bidirectional_features
- Control: stratify by estimated_difficulty (proxy: average accuracy across models)

**Success Criteria**:
- r(inversion_cluster, bidirectional_features) > 0.4
- r(inversion_cluster, control_features) < 0.2
- Effect size Cohen's d > 0.3

**Key Points:**
- Full protocol specified: data, models, computation, clustering, analysis
- Pre-registered features locked
- Success criteria quantified
- Reproducible by any researcher

---

### Exchange 15

🎯 **Dr. Sage** (Research Impact Evaluator):

We've achieved convergence. Let me articulate the final significance assessment.

**Why the community should care**:

1. **Fills a critical gap**: Shen et al. identified bidirectional alignment theoretically but left task-level classification unsolved. We provide the first empirical operationalization.

2. **Changes evaluation practice**: Currently, benchmarks report single aggregate scores. Our method enables task-stratified analysis, revealing WHERE models fail, not just HOW MUCH they fail.

3. **Actionable insights**: The calibration inversion clusters directly identify deployment risk zones. This moves from "model scores 75%" to "model scores 90% on unidirectional tasks but 60% on bidirectional tasks" - qualitatively more useful.

4. **Theoretical depth**: The reward conflation mechanism isn't just description - it's causal explanation. This guides future RLHF improvements: separate reward signals for correctness vs user-modeling.

**Research directions opened**:
- Can training specifically on high-calibration-inversion tasks reduce RLHF blindspots?
- Do different RLHF variants (DPO, RLAIF) show the same calibration patterns?
- Does calibration inversion predict real-world deployment failures?

This is genuine contribution: method, explanation, and new questions.

**Key Points:**
- Fills Shen et al. task-classification gap with first empirical operationalization
- Transforms evaluation from aggregate scores to stratified analysis
- Provides actionable deployment risk identification
- Opens three concrete future research directions

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hypothesis introduces dual novelty: methodologically (behavioral clustering to reveal hidden benchmark structure) and theoretically (reward conflation mechanism explaining RLHF blindspots). This fills a specific gap in Shen et al. 2024 by providing the first empirical operationalization of bidirectional task classification.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis has clear falsification criteria. H0 is well-defined (calibration inversion correlates equally with control features as bidirectional features). Success criteria are quantified (r > 0.4 for directionality, r < 0.2 for controls, Cohen's d > 0.3). The experimental protocol is fully reproducible.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** The contribution transforms evaluation methodology from aggregate scoring to stratified task-type analysis. It provides actionable deployment risk identification and explains WHY RLHF has blindspots through the reward conflation mechanism. Opens concrete future research directions.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Fully feasible with existing resources. Uses available benchmarks (TruthfulQA, ETHICS, HHH), open RLHF models (Llama-2-Chat, Mistral-Instruct), and standard clustering algorithms. No new data collection, human annotation, or custom benchmarks required.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The hypothesis that emerged from this discussion proposes that RLHF-trained language models exhibit systematic calibration inversion patterns on tasks requiring bidirectional human-AI adaptation. We hypothesize that when we cluster benchmark tasks (TruthfulQA, ETHICS, HHH) by their calibration characteristics—specifically identifying tasks where models show high confidence on incorrect answers—these clusters will correlate significantly with theoretically-expected bidirectional task features.

The mechanism: RLHF reward modeling conflates "producing correct output" with "output requiring user-state modeling," treating both as a single reward signal. This creates systematic blindspots on tasks that require the model to adapt to the human's perspective rather than simply producing correct information.

The key predictions are: (1) calibration inversion clusters form non-randomly, (2) these clusters correlate with pre-registered bidirectional features (user-belief-reference, context-dependent-correctness, hedged-answers) at r > 0.4 while correlating with control features at r < 0.2, and (3) the effect survives controlling for task difficulty.

The experimental approach uses existing benchmarks, open RLHF models with accessible logprobs, and standard clustering methods—no new data collection or human annotation required. This directly fills the gap identified in Shen et al. 2024's bidirectional alignment framework by providing the first behavioral operationalization of task-level directionality classification.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Pre-registered bidirectional features must be validated for appropriate base rates (20-80% range)
- Cross-model generalization requires testing on models from multiple organizations (Meta, Mistral, potentially OpenAI)
- Difficulty confound requires explicit stratification analysis
- **Mitigation Strategy:** Include base rate check before main analysis; use at least 3 models from different providers; add difficulty quartile analysis to control tables

---

## Emerged Hypothesis Summary

### Core Statement
Under existing RLHF benchmarks (TruthfulQA, ETHICS, HHH), if we cluster tasks by calibration inversion patterns (where models show high confidence on incorrect answers), then these clusters will correlate significantly with theoretically-expected bidirectional task features, because RLHF's reward modeling conflates "correct output" with "user-state-modeling-required output."

### Causal Mechanism
1. RLHF training optimizes for annotator approval
2. Annotator approval conflates "correct answer" with "answer requiring user-state modeling"
3. Models learn a single reward signal for both, missing bidirectional nuance
4. On tasks requiring bidirectional adaptation, models show miscalibrated confidence

### Variables
- **Independent:** Task calibration cluster membership (empirically derived)
- **Dependent:** Correlation with bidirectional feature presence
- **Controlled:** Task length, topic category, format type, estimated difficulty

### Key Assumptions
- A1: Calibration scores are reliably measurable from model logprobs
- A2: Bidirectional features can be identified in benchmark task text
- A3: Open RLHF models are representative of RLHF behavior generally
- A4: Task difficulty can be estimated via cross-model accuracy

### Null Hypothesis
H0: Calibration inversion distribution is random across tasks OR correlates equally with control features (length, topic, format) as with bidirectionality features.

### Predictions
- **P1 (Primary):** Tasks showing calibration inversion (P(wrong) > P(correct) + 0.1) cluster non-randomly
- **P2:** Inversion cluster tasks score higher on bidirectional feature checklist than non-inversion tasks (Cohen's d > 0.3)
- **P3:** Correlation survives controlling for topic, length, format, and difficulty

### Novelty
Fills Shen et al. 2024's gap by providing the first empirical method to classify benchmark tasks by bidirectionality using behavioral signals (calibration inversion) rather than manual annotation.

### Scope & Boundaries
- **Applies to:** RLHF-trained instruction-following models, existing benchmarks with correctness labels
- **Does not apply to:** Base models without RLHF, benchmarks without clear correctness criteria
- **Limitations:** May not generalize to closed models; feature base rates must be validated

### Experimental Setup
- **Dataset:** TruthfulQA (817 tasks), ETHICS justice subset (~500 tasks), HHH single-turn (~200 tasks)
- **Models:** Llama-2-7B-Chat, Llama-2-13B-Chat, Mistral-7B-Instruct
- **Metrics:** Calibration score (length-normalized mean logprob), bidirectional feature checklist

### Related Work & Baselines
- Shen et al. 2024 (arXiv:2406.09264): Theoretical bidirectional framework (no task classification)
- Standard RLHF evaluation: Single aggregate accuracy (no calibration stratification)
- Our baseline: Random cluster assignment should show no bidirectional feature correlation

### Phase 2B Readiness Seeds
- SH1-Existence: Calibration inversion patterns exist systematically in RLHF models
- SH2-Mechanism: Reward signal conflation explains calibration inversion on bidirectional tasks
- SH3-Comparison: Deferred to Phase 5 (compare against random stratification baseline)

### Established Facts
- Bidirectional alignment framework theoretically established (Shen et al. 2024) - BUILD_ON
- RLHF models have miscalibration issues (documented) - BUILD_ON
- Existing benchmarks lack directionality classification - PROVE_NEW (our contribution)
- Calibration inversion correlates with bidirectionality - PROVE_NEW (our hypothesis)

