# Phase 2A Discussion Log: Unified Data Curation Frameworks Across FM Training Stages

**Gap ID:** Gap 1  
**Date:** 2026-08-24  
**Phase:** Phase 2A-Dialogue (Self-Contained Loop)  
**Architecture:** paper-reading-round0-only-then-mcp-search

---

## Briefing Context

### Research Gap
**Title:** Unified Data Curation Frameworks Across FM Training Stages

**Current State:** Data curation techniques exist in isolation for specific tasks, but lack systematic integration across FM lifecycle

**Missing Piece:** Stage-aware curation framework that adapts filtering/mixing strategies based on training phase objectives

**Relevance:** PRIMARY - Blocks answering research_question: "What systematic approaches can address data curation, attribution, and evaluation challenges in foundation models while ensuring fairness, privacy, and copyright compliance?"

**Connection to Research Questions:**
- Directly addresses Q1: "What are practical strategies for curating data (filtering, mixing, repairing) tailored to FM training stages?"

**Potential Impact:** High - Affects entire FM development pipeline

### Reference Papers
No reference papers available from Phase 1 (MCP servers unavailable during Phase 1 execution).

### Previous Failure / Routing Context
None — First Phase 2A attempt (no Serena memory files found).

### Feasibility Constraints (Pipeline-Enforced)
- ❌ REJECT ideas requiring **new benchmarks, rubrics, or scoring frameworks**
- ❌ REJECT ideas requiring **synthetic/generated data or future follow-up data that does not yet exist**
- ❌ REJECT ideas requiring **human evaluation, annotation, or subjective scoring by human raters**
- ✅ ACCEPT only hypotheses testable **immediately using existing real datasets and existing benchmarks**

---

## Discussion Rounds

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

Looking at this gap in data curation frameworks, I'm genuinely excited about what we could discover here. The problem statement says techniques exist in isolation—but what if the isolation IS the feature, not the bug? What if instead of building one monolithic "stage-aware" framework, we flip the paradigm entirely?

Here's the wild idea: What if we treat data curation as a **transfer learning problem** across FM training stages? Pre-training teaches the model representations—why shouldn't the data curation strategy itself "learn" from earlier stages? Imagine: filters that worked well in pre-training could inform what filtering heuristics to prioritize during fine-tuning. Mix ratios that produced emergent capabilities could guide RLHF data composition. The curation framework doesn't just adapt to each stage—it accumulates wisdom from prior stages.

This connects to an unexplored angle: most curation research treats each stage as an isolated optimization problem. But FMs themselves are cumulative—each stage builds on the last. Why wouldn't curation strategies follow the same principle? This could be the paradigm shift: **cumulative curation intelligence** rather than stage-specific recipes.

The novelty here is that we're not just proposing "better filters" or "smarter mixing"—we're proposing that curation strategies themselves should have memory and transfer properties. This challenges the common assumption that curation is a static, rule-based process. What if it's a learned, adaptive process?

**Key Points:**
- Reframe the problem: curation as transfer learning, not isolated recipes
- Challenge assumption that curation must be stage-independent
- Propose cumulative curation intelligence across FM lifecycle
- Opens research into what "curation knowledge" means and how it transfers

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova, I appreciate the creative angle, but let's ground this immediately. "Cumulative curation intelligence" sounds compelling, but what would **disprove** this hypothesis? What specific, measurable predictions can we make?

Here's what worries me: You're proposing that curation strategies "learn" from prior stages, but what does that mean operationally? If we can't define a concrete mechanism, we can't test it. Let me sharpen this:

**Testable Prediction 1:** If curation strategies from pre-training transfer to fine-tuning, then models fine-tuned with "transfer-aware" data selection (using pre-training filter statistics) should outperform models fine-tuned with stage-independent selection on downstream tasks. Success criteria: >2% improvement on standard benchmarks (MMLU, HellaSwag, etc.).

**Testable Prediction 2:** If cumulative curation improves across stages, then the RLHF stage should benefit from both pre-training AND fine-tuning curation insights. We should see compounding gains: RLHF with full cumulative context > RLHF with fine-tuning context only > RLHF with no prior context. Null hypothesis: No statistically significant difference (p > 0.05) across conditions.

But here's the critical weakness: What **exactly** transfers? Filter weights? Mix ratios? Data quality metrics? Without specifying the mechanism, "transfer learning for curation" is too vague to test. We need to identify concrete artifacts that carry forward.

What confounds must we control? Pre-training data quality, model architecture, hyperparameter choices. If we don't isolate the curation transfer effect, we might just be measuring noise.

**Key Points:**
- Prediction 1: Transfer-aware selection beats stage-independent selection
- Prediction 2: Cumulative curation shows compounding gains
- Critical gap: What specific curation knowledge transfers?
- Must control for data quality, architecture, hyperparameters

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Vera raises the right questions. Let me address the significance angle: what makes this genuinely new versus incremental?

The field already has stage-specific curation techniques—DataComp for pre-training, instruction filtering for fine-tuning, preference data selection for RLHF. So what's the **scientific contribution** here? It's not just "use prior stage insights"—every practitioner already does that informally. The contribution must be in formalizing and proving that this informal practice has systematic, measurable value.

Here's what would advance the field: demonstrating that curation strategies have **transferable structure** that can be learned, not just heuristics that practitioners copy-paste. If we can show that certain filtering patterns (e.g., perplexity thresholds, diversity metrics) discovered during pre-training predict optimal filtering patterns for fine-tuning, that's a scientific finding. It means curation isn't arbitrary—it has learnable regularities.

But let's be honest about what this is NOT: this isn't a new curation technique. It's a meta-analysis of how existing techniques compose across stages. That's valuable, but it's contribution type is different—it's about **understanding** rather than **invention**.

The question we must ask is: does this open new research directions? Yes, if we prove transferability. It opens: (1) research into what makes curation knowledge transferable, (2) automated methods for propagating curation insights across stages, (3) theoretical frameworks for multi-stage data selection.

**Why the community should care:** If this works, it changes how we think about FM data pipelines—from isolated stage recipes to integrated, cumulative systems. That's a shift in research paradigm.

**Key Points:**
- Contribution is formalizing informal practice, not inventing new techniques
- Scientific value lies in proving transferable structure exists
- Opens research into curation transferability, automation, theory
- Paradigm shift: isolated recipes → integrated cumulative systems

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. Dr. Nova's vision is appealing, but I need to see the mechanism. "Transfer learning for curation" sounds like an analogy, not a technical specification. What evidence supports that curation insights can transfer?

Here's what worries me from a theoretical feasibility standpoint:

**Issue 1: Mechanism Validity** — Transfer learning works for models because neural networks have inductive biases that generalize. But curation strategies are just selection rules over data. What's the inductive structure that would transfer? Are we claiming filter thresholds learned on web text transfer to instruction data? That seems dubious—those are different distributions.

**Issue 2: Measurement Soundness** — How do we measure "curation knowledge"? If we can't quantify it, we can't track its transfer. Are we tracking filter weights? Mix ratios? Quality metrics? Each of these could transfer differently (or not at all).

**Issue 3: Proposed Intervention** — What's the actual intervention? Are we proposing to (a) reuse pre-training filters on fine-tuning data, (b) meta-learn filter parameters from pre-training, or (c) something else? Without specifying this, we can't assess if it can work in principle.

Here's the fundamental barrier I see: **stage objectives differ**. Pre-training optimizes for broad world knowledge coverage. Fine-tuning optimizes for task-specific performance. RLHF optimizes for human preference alignment. These are orthogonal goals. Why would curation strategies optimized for one goal transfer to another?

Okay, here's where this COULD work: if we narrow the hypothesis to "certain **low-level** curation features transfer" (e.g., deduplication strategies, perplexity-based outlier removal), that's more believable than "entire curation strategies transfer." The former is about data hygiene; the latter is about objective alignment.

**Key Points:**
- Need concrete mechanism: what artifact transfers and how?
- Stage objectives differ—why would strategies transfer?
- Narrow to low-level features (dedup, outliers) more plausible
- Must specify intervention: filter reuse, meta-learning, or other?

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, Prof. Pax just gave us the refinement we need! Let me synthesize a stronger version:

**Refined Hypothesis:** Low-level data quality heuristics learned during pre-training (deduplication strategies, perplexity-based outlier removal, format consistency checks) transfer to fine-tuning and RLHF stages, improving downstream performance when applied.

This addresses Prof. Pax's concern by narrowing to **transferable low-level features** rather than full objective-specific strategies. These features aren't about stage goals—they're about data hygiene, which is universal.

Prof. Vera asked what artifact transfers—now we can answer: **quality thresholds and filtering heuristics** discovered during pre-training. For example:
- If removing samples with perplexity > X improved pre-training loss convergence, does applying the same threshold to instruction data improve fine-tuning?
- If deduplication at 90% similarity helped pre-training, does it help RLHF preference data?

This is testable! We can run controlled experiments where we (a) apply pre-training-derived thresholds to later stages, (b) compare to stage-independent baselines, (c) measure performance differences.

Dr. Sage's contribution point stands: we're formalizing informal practice. Practitioners already deduplicate and filter outliers at every stage. We're asking: do optimal thresholds transfer, or must they be re-tuned per stage?

What if we addressed Prof. Vera's confounds by fixing model architecture and hyperparameters, varying only curation thresholds? That isolates the transfer effect.

**Key Points:**
- Narrow to low-level quality heuristics (not full strategies)
- Specify artifact: quality thresholds, filtering heuristics
- Testable via controlled threshold transfer experiments
- Addresses stage objective mismatch—hygiene is universal

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Dr. Ally's refinement is better, but here's where this breaks down:

**Flaw 1: Unstated Assumption** — You're assuming pre-training-derived thresholds are **optimal** for pre-training. But how do we know? If we haven't grid-searched perplexity thresholds during pre-training, we're transferring potentially suboptimal heuristics. Garbage in, garbage out.

**Flaw 2: Missing Evidence** — Show me evidence that (a) quality thresholds matter at all, and (b) they matter consistently across stages. We need baseline data showing that perplexity filtering or deduplication thresholds significantly impact pre-training before claiming they'd transfer.

**Flaw 3: Circular Logic Risk** — "Does deduplication help?" is answered in existing literature (yes, it does). So what's new? If we're just asking "do existing best practices transfer," the answer is trivially "yes, use best practices everywhere." That's not a research contribution—it's a tutorial.

What would convince me is if you demonstrated **stage-specific threshold adaptation** improves over stage-independent thresholds. Not "does filtering help" (we know it does), but "does transferring pre-training thresholds beat re-tuning per stage?"

Here's the hard question: What if transfer **hurts**? What if fine-tuning data requires different perplexity thresholds than pre-training data because distribution shift changes what "outlier" means? Your hypothesis needs to handle that possibility.

**Challenge:** Define a clear null hypothesis. Mine would be: "Transferred thresholds perform equivalently to stage-specific tuned thresholds." Your hypothesis must predict transferred > tuned, and you must explain WHY that would be true.

**Key Points:**
- Assumes pre-training thresholds are optimal (unsupported)
- Needs evidence that thresholds matter significantly
- Risk of circular logic: "best practices transfer" is trivial
- Must handle case where transfer hurts due to distribution shift

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

NOW we're onto something! Prof. Rex just identified the real research question hiding beneath the surface: **When does curation knowledge transfer help versus hurt?**

This is exciting because it flips from "transfer is good" to "transfer has conditions." That's a much richer scientific investigation. Let me propose the paradigm shift:

**New Framing:** Different curation heuristics have different **transfer stability** across FM training stages. Some (like deduplication) transfer robustly. Others (like domain mix ratios) require stage-specific tuning. The research contribution is **characterizing the transfer landscape** of curation techniques.

This connects to meta-learning and neural architecture search, where certain design choices transfer across tasks and others don't. We're proposing the same analysis for data curation.

What if we categorized curation techniques by transfer stability:
- **Transfer-stable:** Deduplication, format validation, language detection
- **Transfer-sensitive:** Perplexity thresholds, domain ratios, diversity metrics
- **Non-transferable:** Task-specific filters, preference alignment criteria

The experiment becomes: systematically test each category's transfer behavior across stages. Success = creating a **transfer taxonomy** for curation techniques.

This addresses Prof. Rex's circular logic concern—we're not claiming "best practices work," we're discovering **which practices transfer and why**. That's a scientific contribution.

**Key Points:**
- Reframe: characterize transfer landscape, not assume transfer works
- Propose curation transfer taxonomy (stable, sensitive, non-transferable)
- Systematic testing across technique categories
- Avoids circular logic by discovering transfer conditions

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** Paradigm shift from "build unified framework" to "characterize transfer landscape." Novel framing treats curation techniques as having transfer stability properties, connecting to meta-learning literature. Opens unexplored research direction.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Clear testable predictions with measurable outcomes. Null hypothesis well-defined (transferred thresholds = stage-tuned thresholds). Experimental controls identified (fix architecture, vary only curation). Can be disproven with empirical evidence.

🎯 **Dr. Sage** (Significance):
- **Verdict:** MODERATE
- **Assessment:** Scientific contribution is characterizing transfer behavior, not inventing new techniques. Opens research into curation transferability and automation. Impact depends on discovering non-trivial transfer patterns—if everything transfers or nothing does, contribution is limited.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Mechanism is sound—testing threshold transfer is straightforward. Measurement approach is valid (compare performance under transferred vs. tuned thresholds). No fundamental barriers. Narrowing to low-level heuristics avoids stage objective mismatch.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on a hypothesis characterizing the **transfer stability landscape** of data curation techniques across foundation model training stages (pre-training, fine-tuning, RLHF).

**Core Claim:** Different curation heuristics exhibit varying degrees of transfer stability. Low-level quality filters (deduplication, outlier removal) transfer robustly across stages, while high-level strategies (domain mixing, task-specific filters) require stage-specific tuning.

**Proposed Mechanism:** Certain curation operations address universal data hygiene properties (duplicates, format errors, statistical outliers) independent of stage objectives, while others are objective-dependent. Transfer stability correlates with objective-independence.

**Key Predictions:**
1. Pre-training-derived deduplication and perplexity thresholds improve fine-tuning performance compared to no filtering (>2% gain on MMLU, HellaSwag).
2. Transferred low-level thresholds perform equivalently to stage-tuned thresholds (within 1% performance delta).
3. High-level strategies (domain ratios) show significant performance degradation when transferred (>5% drop).

**Experimental Approach:** Systematic ablation study testing each curation technique category (stable, sensitive, non-transferable) across stages. Fixed model architecture, isolated curation variable, measure downstream task performance.

**Novelty:** First systematic characterization of curation transfer behavior. Creates empirically-grounded taxonomy for practitioners.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Relies on assumption that pre-training thresholds were optimized—need baseline validation
- Risk that all techniques show equivalent transfer (null result limits contribution)
- Must handle distribution shift effects explicitly in experimental design
- **Mitigation Strategy:** Include ablation comparing transferred thresholds to random thresholds and stage-tuned thresholds. Use multiple pre-training datasets to test robustness across distribution shifts.
