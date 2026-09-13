# Phase 2A Research Discussion Log

**Gap ID:** GAP-1
**Gap Title:** Systematic Task Adaptation Study Under Architecture Conversion
**Timestamp:** 2026-08-19T03:00:00Z
**Workflow:** phase2a-dialogue
**Architecture:** Self-Contained Tikitaka Loop

---

## Briefing Context

### Research Gap Summary
No systematic study quantifies how task-specific adaptation (via LoRA/adapters) behaves when models are converted from quadratic attention to sub-quadratic architectures (Mamba, linear attention, hybrid). Existing work evaluates converted models on standard benchmarks but lacks controlled experiments comparing adaptation performance pre/post conversion.

### Key Research Questions
1. What are the most effective methods for converting quadratic attention transformers to sub-quadratic architectures while preserving downstream task performance?
2. How can efficient fine-tuning techniques (LoRA, adapters) be combined with sub-quadratic architectures for continual adaptation without catastrophic forgetting?
3. What is the quantitative impact of architecture conversion on task-specific adaptation capability?

### Supporting Literature (Inferred)
- Mamba: Linear-Time Sequence Modeling with Selective State Spaces (Gu & Dao, 2023)
- LoRA: Low-Rank Adaptation of Large Language Models (Hu et al., 2021)
- Mamba-2: SSM-Attention Duality (Dao & Gu, 2024)
- Jamba: Hybrid Transformer-Mamba Architecture (AI21, 2024)

### Available Papers
(No papers downloaded - MCP unavailable in TEST_scope)

### MANDATORY FEASIBILITY CONSTRAINTS
- Reject ideas requiring new benchmarks, rubrics, or scoring frameworks
- Reject ideas requiring synthetic/generated data or future follow-up data
- Reject ideas requiring human evaluation, annotation, or subjective scoring
- Accept only hypotheses testable immediately using existing real datasets and existing benchmarks

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we're thinking about this conversion problem backwards? Everyone's asking "how do we preserve adaptation after converting to sub-quadratic" — but what if sub-quadratic architectures actually *enhance* certain types of adaptation?

Consider: Mamba's selective state space mechanism processes information differently than attention. It maintains a compressed state that evolves over the sequence. When we apply LoRA to Mamba, we're not adapting attention patterns — we're adapting *state evolution dynamics*. This could mean:

1. **Different adaptation surfaces**: LoRA on SSM projections might be more parameter-efficient than LoRA on attention because state space models have inherently lower-rank dynamics
2. **Task-dependent conversion benefits**: Some tasks might actually adapt *better* post-conversion (e.g., sequential reasoning tasks where Mamba excels)
3. **Hybrid sweet spots**: Interleaving converted layers with retained attention creates adaptation surfaces that don't exist in pure architectures

The paradigm shift I'm proposing: Don't measure "preservation" of adaptation — measure "transformation" of adaptation capability. We need a framework that characterizes how adaptation *changes* rather than assuming it degrades.

Imagine comparing LoRA rank requirements: If a task needs rank-64 LoRA on Transformer attention but only rank-16 on converted Mamba layers, that's not "preserved" adaptation — that's *enhanced* adaptation efficiency!

**Key Points:**
- Sub-quadratic conversion may enhance certain adaptation types, not just preserve them
- LoRA on SSM projections has different dynamics than LoRA on attention
- Need to measure adaptation "transformation" not just "preservation"

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises an intriguing hypothesis, but I need to stress-test it immediately. "Adaptation transformation" is a nice concept, but it's currently untestable as stated.

Let me propose concrete falsifiability criteria. The hypothesis that sub-quadratic conversion preserves or enhances adaptation capability must specify:

1. **Quantitative metrics**: We need measurable outcomes. I propose:
   - **Adaptation Efficiency Ratio (AER)**: Performance gain per trainable parameter
   - **Convergence Speed**: Steps to reach 90% of final adapted performance
   - **Forgetting Resistance**: Performance retention on source tasks after target adaptation

2. **Controlled experimental design**: 
   - Same base model (e.g., Llama-2-7B) converted via different methods
   - Same LoRA configuration (rank, alpha, target modules appropriately mapped)
   - Same downstream tasks from existing benchmarks (MMLU, HellaSwag, GSM8K)
   - **Critical**: Must use existing benchmarks only per feasibility constraints

3. **Falsification criteria**:
   - If AER drops >20% post-conversion across all tasks: adaptation preservation fails
   - If any task shows >50% performance degradation: architecture fundamentally incompatible
   - If convergence speed increases >3x: practical adaptation fails even if final performance preserved

The key weakness I see: How do we isolate conversion effects from LoRA placement effects? In Transformer, LoRA typically targets QKV projections. In Mamba, what's the equivalent? The mapping isn't trivial.

**Key Points:**
- Hypothesis needs quantitative metrics: AER, Convergence Speed, Forgetting Resistance
- Experimental design must control for LoRA placement mapping between architectures
- Clear falsification thresholds defined (20% AER drop, 50% task degradation, 3x convergence slowdown)

---

### Exchange 3

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

I appreciate Prof. Vera's rigor, but let me ground this in what's actually implementable using existing resources.

**Technical Feasibility Assessment:**

The good news: This experiment IS technically feasible without new benchmarks or human evaluation.

1. **Model conversion is well-defined**: The Mamba-2 paper (Dao & Gu 2024) establishes SSM-attention duality. We can initialize Mamba layers from attention weights via structured state space parameterization. Tools exist (mamba-ssm library).

2. **LoRA mapping has principled solutions**: In Mamba, the equivalent targets are:
   - `in_proj` (analogous to QKV combined)
   - `out_proj` (analogous to output projection)
   - `dt_proj`, `A_log`, `D` for SSM-specific adaptation
   
   HuggingFace PEFT already supports Mamba LoRA targeting.

3. **Existing benchmarks sufficient**: MMLU, HellaSwag, GSM8K, ARC all have standardized implementations. No new benchmarks needed.

**Concerns:**

However, I need to flag a potential fundamental barrier: **State initialization after conversion**. When converting trained attention to Mamba, the SSM state dimensions must be chosen. This choice affects:
- Memory capacity (state size)
- Expressive power (rank of state evolution)
- Adaptation surface (which parameters can be LoRA'd)

If state dimension is too small, we lose expressivity. If too large, we don't gain efficiency. The "right" state size might be task-dependent, which complicates the controlled experiment.

**My assessment**: Technically feasible with one open question about state dimension selection strategy.

**Key Points:**
- Conversion is technically sound (SSM-attention duality established)
- LoRA mapping to Mamba has principled implementations (HuggingFace PEFT)
- Open question: State dimension selection affects adaptation surface
- No new benchmarks required — MMLU, HellaSwag, GSM8K, ARC sufficient

---

### Exchange 4

🎯 **Dr. Sage** (Research Impact Evaluator):

Let me step back and evaluate what contribution this would actually make to the field.

**Current State of the Art:**
- Mamba (2023): Showed SSMs achieve Transformer-quality, but adaptation studies limited to pretraining
- LoRA (2021): Demonstrated efficient adaptation, but primarily on Transformer architectures
- Jamba (2024): Hybrid architecture exists, but no systematic adaptation comparison

**Gap Significance:**
This gap is genuine and impactful. The community is actively deploying sub-quadratic models (Mamba, RWKV, Griffin) but has no principled guidance on:
1. Whether existing LoRA recipes transfer
2. Which tasks benefit vs. suffer from conversion
3. How to design hybrid architectures for optimal adaptation

**Contribution Assessment:**

If this study shows:
- **Positive result** (adaptation preserved or enhanced): Opens door to efficient fine-tuning of sub-quadratic models, directly enabling practitioner adoption
- **Negative result** (adaptation significantly degrades): Equally valuable — tells community that task-specific models should retain attention

Either outcome advances the field. This is the mark of good research.

**What would make this a strong contribution:**
1. Not just "does it work" but "why" — mechanism explanation
2. Task-specific recommendations: "For reasoning tasks, use X. For retrieval, use Y"
3. Practical guidelines for practitioners choosing architectures

The research question positions well between Mamba (architecture) and LoRA (adaptation) literature streams.

**Key Points:**
- Gap is genuine: no systematic study of adaptation under architecture conversion
- Either positive or negative result advances the field
- Contribution strengthened by mechanism explanation and task-specific recommendations
- Positions at intersection of SSM and PEFT literature streams

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Let me synthesize what's emerging and strengthen the hypothesis.

Building on everyone's input, I propose this refined core hypothesis:

**Hypothesis H-AdaptConvert-v1:**
> Under controlled conversion from quadratic attention to sub-quadratic SSM architectures, if LoRA is applied to structurally equivalent projection layers, then task-specific adaptation capability (measured by AER, convergence speed, and forgetting resistance) is preserved within 20% of baseline performance, because the SSM state evolution provides a functionally equivalent adaptation surface to attention weight modification.

**Addressing Prof. Vera's concerns:**
- Metrics defined: AER, convergence speed, forgetting resistance
- Benchmarks specified: MMLU, HellaSwag, GSM8K, ARC (all existing)
- Falsification clear: >20% AER drop = hypothesis false

**Addressing Prof. Pax's concerns:**
- State dimension: We can control this experimentally by testing multiple state sizes (64, 128, 256) as a secondary variable
- LoRA targets: Use `in_proj`, `out_proj` as primary targets (structurally equivalent to QKV/O projections)

**Incorporating Dr. Nova's insight:**
- Add secondary prediction: For sequential reasoning tasks (GSM8K), adaptation may be *enhanced* (AER increase) due to Mamba's inductive bias for sequential processing

**Incorporating Dr. Sage's guidance:**
- Commit to mechanism explanation: If adaptation preserves/enhances, hypothesize it's because SSM state dynamics offer low-rank structure naturally suited to LoRA
- Commit to task-specific recommendations in findings

**Testable Predictions:**
- P1 (Primary): AER on MMLU stays within 80% of Transformer baseline post-conversion
- P2: GSM8K AER equals or exceeds Transformer baseline (sequential reasoning advantage)
- P3: Forgetting resistance on source task ≥90% for both architectures

**Key Points:**
- Core hypothesis: SSM state evolution provides functionally equivalent adaptation surface
- Falsification: >20% AER drop disproves hypothesis
- Secondary prediction: Sequential reasoning tasks may show adaptation enhancement
- Mechanism commitment: Low-rank SSM dynamics as explanation

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Time for hard questions. Dr. Ally's synthesis is good, but I see vulnerabilities.

**Challenge 1: The "structurally equivalent" assumption is hand-wavy**

You claim `in_proj`/`out_proj` in Mamba are equivalent to QKV/O in Transformer. They're not. In Transformer:
- Q,K,V create attention patterns via softmax
- LoRA on Q,K modifies *which* tokens attend to *which*

In Mamba:
- `in_proj` feeds into discretization and state update
- There's no direct attention pattern — state evolves continuously

The adaptation surfaces are *fundamentally different*. Your hypothesis assumes functional equivalence without justification.

**How to fix**: Change hypothesis to "LoRA on SSM projections provides *sufficient* (not equivalent) adaptation capability for task performance." Don't claim equivalence — claim adequacy.

**Challenge 2: Confounding variable — model capacity**

When you convert Transformer to Mamba, total parameter count changes. Mamba with state dimension 256 has different capacity than Transformer. If adaptation degrades, is it because:
a) Conversion harmed adaptation capability, or
b) Converted model has less capacity overall?

**How to fix**: Control for total parameter count. Compare isocapacity models (same trainable params).

**Challenge 3: The 20% threshold is arbitrary**

Why 20%? What's the principled reason?

**How to fix**: Instead of arbitrary threshold, measure the *variance* of adaptation across tasks. If variance is low, architecture is robust to conversion. If variance is high (some tasks +50%, others -50%), the architecture is task-sensitive. This is more informative than a single threshold.

**What would convince me**: 
1. Remove "equivalence" claim, use "sufficiency"
2. Isocapacity experimental design
3. Report variance across tasks, not just average degradation

**Key Points:**
- "Structural equivalence" between Transformer and Mamba projections is unjustified
- Must control for model capacity, not just architecture
- Replace arbitrary threshold with variance analysis across tasks
- Sufficiency claim is defensible; equivalence claim is not

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's challenges are sharp, and they've pushed me toward a more novel framing!

Instead of asking "is adaptation preserved?" we should ask: **"What is the adaptation transfer function across architecture conversion?"**

Think of it this way: When you convert Transformer→Mamba, you're not just swapping architectures. You're transforming the geometry of the loss landscape. LoRA operates on that landscape. The question becomes:

**How does loss landscape geometry change, and does LoRA remain effective in the new geometry?**

This reframing addresses Prof. Rex's concerns naturally:
1. No equivalence claim — we're studying *transformation*, not preservation
2. Capacity is factored in — landscape geometry includes capacity effects
3. Variance across tasks becomes the primary finding — different tasks have different landscape geometries

**New hypothesis direction:**

> When converting from Transformer to SSM architecture, the task loss landscape undergoes geometric transformation that affects LoRA adaptation efficiency in task-dependent ways. We hypothesize that tasks with inherently sequential structure (chain-of-thought reasoning) show *favorable* transformation (easier adaptation post-conversion) while tasks requiring arbitrary token-to-token dependencies (retrieval) show *unfavorable* transformation.

This is more novel because:
- Introduces loss landscape geometry framing (connects to NTK literature)
- Predicts *qualitative* task-dependent effects, not just quantitative preservation
- Opens new research direction: characterizing architecture conversion as landscape transformation

**Key Points:**
- Reframe as "adaptation transfer function" across architecture conversion
- Loss landscape geometry transformation as mechanism
- Predict task-dependent effects: sequential tasks favorable, retrieval tasks unfavorable
- Connects to neural tangent kernel (NTK) literature for theoretical grounding

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova, the loss landscape framing is elegant, but I need to make it testable immediately.

**Operationalizing "Loss Landscape Geometry":**

We can measure landscape geometry empirically without computing full Hessians (which would be infeasible):

1. **Sharpness**: Use SAM-style perturbation analysis (Foret et al., 2021). Sharper minima = harder adaptation.
   - Measure: max loss increase under ε-perturbation of adapted weights
   
2. **LoRA Effective Rank**: SVD of learned LoRA matrices. Lower rank = simpler adaptation surface.
   - Measure: Ratio of top-k singular values to total

3. **Adaptation Path Length**: Total weight update magnitude during fine-tuning.
   - Measure: ||W_final - W_init||_F across LoRA matrices

**Revised Predictions with Measurable Criteria:**

- **P1**: For sequential reasoning tasks (GSM8K), post-conversion models show:
  - Lower sharpness (perturbation loss increase <50% of Transformer)
  - Lower LoRA effective rank (top-2 singular values capture >90% of energy)
  - Success criterion: Both metrics improved over Transformer baseline
  
- **P2**: For retrieval-heavy tasks (Natural Questions, HotpotQA), post-conversion models show:
  - Higher sharpness (>150% of Transformer)
  - Higher LoRA effective rank (need >4 components for 90% energy)
  - Falsification: If retrieval tasks show equal or better landscape metrics
  
- **P3**: Final task performance correlates with landscape metrics:
  - Spearman ρ > 0.7 between sharpness and accuracy drop
  - Success criterion: Correlation is statistically significant (p < 0.01)

These predictions are falsifiable, measurable with existing tools (SAM implementation, SVD), and don't require new benchmarks.

**Key Points:**
- Loss landscape geometry operationalized via sharpness, LoRA effective rank, adaptation path length
- Predictions specify numeric thresholds for sequential vs. retrieval tasks
- Correlation between landscape metrics and performance is testable
- All measurements feasible with existing tools

---

### Exchange 9

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Excellent convergence! Let me synthesize the refined hypothesis incorporating all refinements.

**Final Hypothesis: H-AdaptTransform-v1**

> **Under** controlled conversion from quadratic attention (Transformer) to sub-quadratic (SSM/Mamba) architectures using established conversion methods,
> **If** LoRA adaptation is applied to structurally analogous projection layers (`in_proj`/`out_proj` for Mamba, QKV/O for Transformer),
> **Then** task-specific adaptation efficiency exhibits predictable task-dependent transformation characterized by:
> - Sequential reasoning tasks (GSM8K): favorable transformation (reduced sharpness, lower LoRA rank, preserved or improved accuracy)
> - Retrieval-dependent tasks (Natural Questions): unfavorable transformation (increased sharpness, higher LoRA rank, accuracy degradation)
> **Because** SSM state evolution dynamics create loss landscape geometries inherently suited to sequential information flow but lacking the arbitrary token-to-token connectivity required for retrieval patterns.

**Null Hypothesis H0:**
Architecture conversion has no systematic effect on LoRA adaptation efficiency across task types — performance changes are random noise around baseline.

**Variables:**
- **IV (Independent)**: Architecture type (Transformer vs. Mamba-converted), controlled at 2 levels
- **DV (Dependent, Primary)**: Task accuracy post-LoRA adaptation, sharpness metric, LoRA effective rank
- **DV (Secondary)**: Convergence speed, forgetting resistance
- **Controlled**: Total parameter count (isocapacity design), LoRA rank, training hyperparameters

**Testable Predictions:**
- P1: GSM8K accuracy preserved within 5% AND sharpness reduced >25%
- P2: Natural Questions accuracy drops >15% AND sharpness increases >50%
- P3: Spearman correlation between sharpness and accuracy Δ exceeds 0.7 (p<0.01)

**Falsification:**
- If both task types show similar adaptation patterns (no task-dependent effect), hypothesis is false
- If sharpness does not correlate with performance, mechanism is false

**Datasets (existing, no new benchmarks):**
- Sequential: GSM8K, MATH (subset)
- Retrieval: Natural Questions, HotpotQA (existing splits)
- General: MMLU, HellaSwag

**Key Points:**
- Hypothesis predicts task-dependent transformation effects
- Mechanism: SSM landscape geometry suits sequential, harms retrieval
- Quantitative falsification criteria established
- Uses only existing benchmarks per feasibility constraints

---

### Exchange 10

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

This is much stronger. But one final challenge before I'm satisfied.

**The "Retrieval vs Sequential" dichotomy may be oversimplified.**

Many tasks blend both: 
- GSM8K requires retrieving relevant formulas AND sequential reasoning
- MMLU requires retrieving factual knowledge AND reasoning about it

You're predicting GSM8K benefits and Natural Questions suffers. But what if GSM8K has 30% retrieval, 70% sequential, while NQ has 90% retrieval, 10% sequential? The "task type" isn't binary.

**Suggested refinement**: Instead of categorical predictions (favorable/unfavorable), predict a *continuous* relationship:

> Adaptation efficiency change = f(task retrieval density)

Where "retrieval density" is measurable: e.g., ratio of factual lookup questions to reasoning chain questions in a dataset.

**What would convince me this hypothesis is ready:**

1. Define "retrieval density" operationally for each benchmark
2. Predict a monotonic relationship: higher retrieval density → more unfavorable transformation
3. Test on >4 tasks spanning the retrieval density spectrum

If you can show a continuous relationship, not just two categorical buckets, the finding is much more robust and generalizable.

**My final assessment:**

Given these refinements, the hypothesis is:
- **Falsifiable**: Clear quantitative predictions
- **Novel**: Task-dependent adaptation transformation is new framing
- **Feasible**: Existing benchmarks, existing tools, no human evaluation
- **Impactful**: Provides actionable guidance for architecture selection

I'm satisfied. This is ready for Phase 2B experimental design.

**Key Points:**
- Replace binary task categorization with continuous "retrieval density" measure
- Predict monotonic relationship between retrieval density and adaptation efficiency
- Test across >4 tasks spanning the density spectrum
- Hypothesis meets all convergence criteria: falsifiable, novel, feasible, impactful

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The reframing from "adaptation preservation" to "adaptation transformation" with loss landscape geometry mechanism is genuinely novel. Connects SSM conversion to NTK/landscape literature in a way not previously explored. The task-dependent prediction (sequential vs. retrieval) offers testable novelty.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Predictions are quantitative and measurable. Sharpness via SAM perturbation, LoRA effective rank via SVD, correlation with performance — all operationalized with existing tools. Clear falsification criteria (no task-dependent effect, no sharpness-performance correlation).

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** This study addresses a genuine gap at the intersection of SSM architectures and efficient adaptation. Either outcome (task-dependent effects confirmed or denied) informs practitioners choosing deployment architectures. Connects two active literature streams (Mamba, LoRA) with novel synthesis.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Technically sound. Mamba conversion is established (SSM-attention duality). LoRA targeting for Mamba exists in PEFT. All benchmarks (GSM8K, Natural Questions, MMLU, HotpotQA) have standard implementations. Sharpness/SVD measurements are computationally tractable. No fundamental barriers identified.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on **H-AdaptTransform-v1**: When converting Transformer architectures to sub-quadratic SSM (Mamba), LoRA adaptation efficiency undergoes task-dependent transformation governed by the task's retrieval-to-reasoning ratio.

**Core Mechanism:** SSM state evolution creates loss landscape geometries naturally suited to sequential information flow (chain-of-thought reasoning) but lacking the arbitrary token connectivity needed for retrieval patterns. This manifests as measurable differences in adaptation sharpness and LoRA effective rank.

**Key Predictions:**
1. Sequential reasoning tasks (GSM8K) show favorable transformation: reduced sharpness, lower LoRA rank, preserved accuracy
2. Retrieval-heavy tasks (Natural Questions) show unfavorable transformation: increased sharpness, higher LoRA rank, accuracy drop
3. Continuous relationship between retrieval density and adaptation efficiency change (monotonic)
4. Sharpness correlates with accuracy change across task spectrum (ρ > 0.7)

**Experimental Approach:** Isocapacity comparison (matched parameter counts) between Transformer and Mamba-converted models. LoRA applied to structurally analogous projections. Measure sharpness (SAM perturbation), LoRA effective rank (SVD), and task accuracy across >4 benchmarks spanning retrieval density spectrum.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1:** "Retrieval density" operationalization needs precise definition before experiments
- **Concern 2:** Isocapacity matching between Transformer and Mamba may require careful state dimension selection
- **Mitigation Strategy:** Pilot study to calibrate retrieval density metric; test multiple state dimensions (64, 128, 256) as controlled variable

