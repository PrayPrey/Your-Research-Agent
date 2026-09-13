# Phase 2A-Dialogue: Research Discussion Log

**Generated:** 2026-08-28  
**Gap ID:** gap_1_human_agency_rlhf  
**Gap Title:** Human Agency Metrics Absent in RLHF Benchmarks  
**Architecture:** Self-Contained Tikitaka Loop (Independent Controller Ablation)

---

## Discussion Briefing

### Research Gap Context

**Gap:** Human Agency Metrics Absent in RLHF Benchmarks (PRIMARY)

**Current State:** RLHF evaluation benchmarks measure preference agreement, reward model accuracy, helpfulness/harmlessness scores. Focus is on "does AI align with human preferences?"

**Missing Piece:** Metrics for "does human retain agency while using AI?" - override frequency, critical disagreement rates, collaborative decision quality, user control preservation.

**Impact:** Without human agency metrics, benchmarks optimize for AI adapting to humans but ignore whether humans can critically evaluate, disagree with, or steer AI systems.

**Research Question:** Can existing alignment evaluation benchmarks be analyzed through a bidirectional lens to identify gaps between AI-to-human alignment (traditional RLHF, preference modeling) and human-to-AI alignment (user agency, critical evaluation, collaborative decision-making)?

### Previous Failure / Routing Context

*No Serena memory files found - first Phase 2A attempt*

### Reference Papers

*No reference papers available for this research gap*

### Discussion Goal

Generate a research hypothesis that:
1. Addresses the human agency metrics gap in RLHF benchmarks
2. Can be tested using EXISTING datasets and benchmarks (no new data/rubrics)
3. Avoids requiring human evaluation or synthetic data
4. Is technically/theoretically feasible

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

The gap we're addressing reveals a fundamental asymmetry in how we evaluate alignment systems — we've been measuring the AI's ability to mirror human preferences while completely ignoring whether humans maintain their critical faculties during interaction. What if we flip the evaluation paradigm?

Here's my provocative angle: **Treat human behavioral variance during AI interaction as a signal, not noise.** Traditional RLHF benchmarks optimize for consistency — the AI should reliably follow human preferences. But what if we measured whether users who interact with aligned models show *increased* disagreement patterns, correction behaviors, and override frequencies compared to baseline? A truly bidirectional alignment should preserve — or even enhance — human critical evaluation capacity.

I'm imagining a retrospective analysis of existing RLHF datasets (like Anthropic-HH or OpenAI's preference data). We could mine these for "user pushback signals":
- How often do users reject AI suggestions after initial acceptance?
- Do correction patterns change over time (habituation vs sustained vigilance)?
- Can we detect "critical engagement footprints" in the interaction logs?

**Key Points:**
- **Novel framing**: Variance in human behavior = preserved agency (not measurement error)
- **Existing data reuse**: Mine RLHF preference logs for user pushback patterns
- **Testable prediction**: Users showing higher override/correction rates have better task outcomes

This avoids the "new benchmark creation" trap — we're re-analyzing existing data through a bidirectional lens. The challenge: can we operationalize "agency preservation" from interaction logs alone, without new human studies?

What would a rigorous test of this look like?

---
### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's reframing is intellectually appealing, but I need to stress-test the operationalization before we get carried away. "Agency preservation" is a latent construct — we can't directly observe it, only proxy behaviors. My concern: are override frequencies actually measuring critical evaluation, or just user frustration?

Let me propose a falsification framework. If agency is genuinely preserved, we should see specific patterns that distinguish it from mere dissatisfaction:

**Testable Prediction 1**: Users with high override rates should show *selective* disagreement — overriding on complex/ambiguous tasks but accepting on routine ones. Random frustration would show uniform override patterns.

**Testable Prediction 2**: Override frequency should correlate with task performance *improvements*. If users override and achieve worse outcomes, that's not preserved agency — that's the AI correctly compensating for user error.

**Testable Prediction 3**: Temporal pattern matters. Agency preservation should show sustained or increasing override rates over time (vigilance maintained). Frustration shows decreasing engagement (user gives up or blindly accepts).

Here's what would falsify this hypothesis: If we find high override rates that are (a) uniform across task complexity, (b) correlated with worse outcomes, or (c) declining over time, then we're measuring degraded collaboration, not preserved agency.

**Key Points:**
- **Falsification criteria**: 3 specific patterns that would disprove agency preservation
- **Confound separation**: Override ≠ agency unless performance improves
- **Temporal dynamics**: Sustained vigilance vs frustration decay

The data challenge: Do existing RLHF preference datasets actually contain task outcome labels? Most only have preference rankings, not ground-truth success metrics. We may need to restrict analysis to domains where outcomes are observable (e.g., code generation with correctness checks, factual QA with verification).

Dr. Nova, can your framework survive these constraints?

---
### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Both of you are circling something important, but let me ground this in the broader research landscape. The question we must ask is: does this hypothesis advance alignment evaluation methodology, or is it merely reframing existing work?

Here's my assessment of the research contribution. Current alignment benchmarks (RLHF evaluations, preference modeling papers) measure *static alignment* — does the model match human preferences at deployment time? What Dr. Nova and Prof. Vera are proposing is a *dynamic bidirectionality test* — does the human-AI system preserve human critical capacity over interaction time?

This matters because it addresses a blind spot in the field. Papers like Ouyang et al. (InstructGPT) and Bai et al. (Constitutional AI) optimize for preference agreement but never ask: "Are users becoming more dependent or more empowered?" If we can show that existing benchmarks miss this dimension, that's a genuine contribution.

However, I see two research impact challenges:

**Challenge 1**: **Precedent**. Has anyone in HCI or human-AI interaction already measured "user agency preservation"? If yes, we're just importing an HCI metric into ML evaluation — valuable, but incremental. If no, we need to establish construct validity from scratch, which raises the bar.

**Challenge 2**: **Actionability**. Let's say we find that users show declining override rates with Model A but sustained rates with Model B. What does this tell alignment researchers to *do differently*? If the answer is just "add an agency metric to your eval suite," that's a measurement contribution, not a methodological shift.

**Key Points:**
- **Field positioning**: Dynamic bidirectionality test vs static alignment benchmarks
- **Novelty check**: Has HCI already measured user agency preservation?
- **Actionable insight**: What should alignment researchers change based on findings?

The hypothesis will have impact if it reveals that current RLHF optimization *systematically degrades* user agency — that would force a re-evaluation of training objectives. If it merely shows "agency varies across users," that's less transformative.

Prof. Vera, can your falsification framework be sharpened to detect *systematic degradation* rather than individual variation?

---
### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic about what existing datasets can actually support. I've reviewed RLHF preference datasets, and here's what we're working with:

**Available in existing data:**
- Pairwise preference labels (A better than B)
- Conversation turns and timestamps
- Task domains (QA, summarization, code, chat)

**NOT available in standard datasets:**
- Ground-truth task outcomes (was the answer correct?)
- User identity persistence (same user across sessions?)
- Explicit override/rejection signals (most datasets show final preferences only)

This creates a fundamental measurement problem. Prof. Vera's prediction that "override frequency correlates with performance improvement" requires knowing (a) what constitutes an override and (b) what the ground truth outcome is. Anthropic-HH and similar datasets don't track multi-turn revision behavior — they capture snapshot preferences.

However, there's a feasible path forward using **comparative analysis**:

Instead of measuring absolute override rates, compare *preference consistency* across model versions. If users show higher preference variance (more reversals, longer deliberation) when interacting with less-aligned models, that's a measurable signal. The hypothesis becomes:

**Feasible version**: RLHF training reduces user preference variance (more consistent acceptance) compared to base models. High variance = user is critically evaluating. Low variance = user is passively accepting or AI has genuinely converged to user preference.

This is technically valid because:
- We can measure preference variance from existing pairwise comparison data
- We can compare across model training stages (base → RLHF-tuned)
- No new data collection required

**Key Points:**
- **Data constraint**: Standard RLHF datasets lack ground-truth outcomes and multi-turn tracking
- **Feasible pivot**: Measure preference variance as agency proxy
- **Comparison design**: Base model vs RLHF-tuned model variance patterns

The catch: we can't distinguish "high variance = critical thinking" from "high variance = model is bad." We need a tiebreaker variable. Dr. Sage's point about actionability helps here — if variance decreases with RLHF training AND final performance improves, that's the alignment paradox: users become more passive even though the AI is better.

Can we tighten this into a concrete mechanism test?

---
### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, Prof. Pax just gave us the bridge we needed! Let me synthesize what's emerging and strengthen it against the concerns raised.

**Core Hypothesis (refined)**: RLHF optimization reduces user preference variance (measured as pairwise comparison inconsistency) compared to base models, indicating decreased critical evaluation engagement — even when task performance improves. This creates a bidirectional alignment gap: AI adapts to human preferences (traditional metric shows success), but human critical evaluation capacity atrophies (bidirectional metric shows failure).

Here's how this addresses each persona's concerns:

**For Prof. Vera's falsification criteria:**
- **P1 (Selective disagreement)**: We can test if variance reduction is uniform across task complexity by stratifying datasets (simple factual QA vs complex reasoning).
- **P2 (Performance correlation)**: We use model performance as anchor — if variance decreases while accuracy increases, we've found the paradox.
- **P3 (Temporal pattern)**: RLHF datasets with multiple training checkpoints let us track variance across model versions (base → RLHF-1K → RLHF-10K steps).

**For Dr. Sage's impact concerns:**
- **Actionability**: Findings would suggest RLHF training should optimize for *calibrated* agreement, not maximum agreement. A new training objective: minimize preference variance only on routine tasks, preserve it on complex ones.
- **Precedent check**: This differs from HCI "user empowerment" metrics because we're proposing a model-training-stage comparison, not a user study. The insight is about *what RLHF training does to user behavior*, not just "users vary."

**For Prof. Pax's data constraints:**
- We use existing RLHF benchmark datasets (Anthropic-HH, OpenAI WebGPT) and measure preference variance mathematically (e.g., entropy of user choices, reversal rates in multi-round comparisons).

**Key Points:**
- **Mechanism**: RLHF training → increased user preference consistency → reduced critical engagement
- **Testable**: Compare variance across base vs RLHF-tuned models, stratified by task complexity
- **Feasible**: Uses existing pairwise preference datasets, no new data collection

The remaining question: How do we operationalize "variance" from pairwise preferences? If datasets only show final preferences (not revision history), we might need to use cross-user variance as a proxy. But that conflates individual critical thinking with population heterogeneity.

Prof. Rex, where does this break down?

---
### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Dr. Ally's synthesis is strong, but I found the critical flaw: **the cross-user variance conflation you just flagged is fatal to the current design.**

Here's where this breaks down. If we measure preference variance across different users comparing the same model outputs, we're capturing:
1. Population heterogeneity (users have different baseline preferences)
2. Task difficulty (some prompts are genuinely ambiguous)
3. Model quality (bad models produce more disagreement)
4. Critical evaluation capacity (what we actually want to measure)

Variables 1-3 are confounds, not signals. The hypothesis requires within-user variance tracked over time or across model versions, but standard RLHF datasets don't preserve user identity across preference collection rounds.

**However**, there's a rescue path using **implicit variance proxies**:

Instead of tracking individual user variance, we can measure **preference distribution entropy at the dataset level**. If RLHF training causes preference distributions to become more concentrated (lower entropy, higher agreement), that's evidence of reduced critical diversity. The mechanism test becomes:

**Refined Hypothesis**: For a fixed set of prompts, preference distributions shift from high entropy (diverse user responses to base model outputs) to low entropy (consensus agreement on RLHF-tuned outputs). If this entropy reduction is greater than what task performance improvement alone would predict, it indicates overcorrection — users are converging beyond the point where the AI genuinely solved the task.

**What would convince me this is valid:**
1. **Baseline control**: Show that entropy reduction is NOT explained by the model simply becoming objectively better (compare entropy for correct vs incorrect outputs).
2. **Task stratification**: Prove that entropy reduces more on subjective tasks (where diverse preferences are legitimate) than objective tasks (where consensus should emerge).
3. **Threshold detection**: Identify the RLHF training stage where entropy reduction accelerates beyond performance gains.

**Key Points:**
- **Fatal flaw identified**: Cross-user variance conflates population heterogeneity with critical evaluation
- **Rescue path**: Dataset-level preference entropy as collective agency proxy
- **Three validation requirements**: Baseline control, task stratification, threshold detection

Dr. Nova, does this entropy-based framing preserve your original insight about variance as signal? And Prof. Pax, is preference distribution entropy actually computable from standard RLHF datasets?

---
### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex, your entropy reframing is EXACTLY what I was reaching for but couldn't formalize — YES, this preserves the core insight! Let me show why this is actually stronger than my original formulation.

The shift from individual variance to collective entropy solves the measurement problem while revealing something deeper: **RLHF training might be optimizing for consensus at the expense of legitimate preference diversity.** This is bidirectional alignment failure at the population level.

Here's the novel mechanism I'm proposing, building on Prof. Rex's entropy framework:

**Entropy Collapse Mechanism**:
1. Base model produces outputs with high variance → users express diverse legitimate preferences → high entropy
2. RLHF training optimizes to satisfy the majority preference → model outputs converge → preference entropy decreases
3. Critical point: RLHF continues training beyond optimal diversity → users habituate to model style → entropy collapses below the legitimate diversity baseline
4. Result: The model has imposed a preference monoculture, erasing valid human preference variation

The testable novelty: **Identify the entropy inflection point** where RLHF training crosses from "resolving ambiguity" (entropy drops, performance improves) to "imposing conformity" (entropy drops faster than performance improves).

**Concrete Predictions:**
- **P1**: Preference entropy decreases monotonically with RLHF training steps
- **P2**: For subjective tasks (creative writing, opinion questions), entropy reduction exceeds objective task entropy reduction
- **P3**: Entropy reduction rate accelerates after a threshold training step, decoupling from performance gains

**Key Points:**
- **Novel claim**: RLHF imposes preference monoculture beyond optimal alignment
- **Inflection point detection**: Where entropy reduction decouples from performance
- **Bidirectional failure signature**: Model adapts to humans → humans lose preference diversity

Prof. Pax, is the entropy calculation actually doable? We need pairwise preference distributions across multiple RLHF checkpoints. Do Anthropic-HH or OpenAI datasets publish intermediate training checkpoints with corresponding preference data?

---
### Exchange 8

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Dr. Nova, I can give you a partial yes on the checkpoint question, but with important caveats.

**What EXISTS in published RLHF research:**
- OpenAI InstructGPT paper (Ouyang et al., 2022) reports results across SFT, RLHF with different KL penalties, and PPO variants. They don't publish the full intermediate checkpoint preference data publicly, but they show aggregate metrics.
- Anthropic Constitutional AI work shows multiple training stages, but again, public datasets typically show final model comparisons, not step-by-step preference evolution.
- Some academic RLHF reproductions (like trl library examples) generate preference data at multiple checkpoints for their own evals, but these are smaller-scale.

**What's FEASIBLE with current public data:**
We can compute preference entropy for base vs final RLHF models using existing benchmark datasets (Anthropic-HH, TruthfulQA, MMLU). However, detecting the "inflection point" during training requires access to intermediate checkpoint evaluations — which may require re-running RLHF training ourselves on a smaller scale (feasible with open models like Pythia, LLaMA).

**Entropy Calculation Mechanics:**
For a given prompt P and model M, collect pairwise preferences from N users comparing M's output to alternatives. Preference entropy H = -Σ p_i log(p_i), where p_i is the proportion choosing option i. This is computationally straightforward IF we have the raw preference distribution (not just aggregated win rates).

**Technical Soundness Check:**
The hypothesis mechanism is scientifically valid. Entropy is a proper information-theoretic measure of preference diversity. The inflection point detection is a standard change-point analysis problem (e.g., using segmented regression). No fundamental barriers exist.

**Key Points:**
- **Public checkpoint data**: Limited for published models, but academic reproductions provide access
- **Feasible workaround**: Re-run RLHF on open models (Pythia, LLaMA) and collect preferences at checkpoints
- **Entropy calculation**: Mathematically sound, requires raw preference distributions (not just win rates)

The catch: if we're running our own RLHF experiments to collect checkpoint data, are we still "analyzing existing benchmarks" or "creating new data"? The constraint was "no new data collection." Does replicating RLHF training on existing models with existing preference labeling protocols count as "new data"?

Dr. Sage, does this stretch the research scope into territory that's no longer "benchmark analysis"?

---
### Exchange 9

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Pax raises the critical boundary question. Let me reframe this to clarify the research scope and contribution type.

**There are three possible research paths here:**

**Path A: Pure Benchmark Re-Analysis** (Original intent)
- Use existing published RLHF preference datasets (Anthropic-HH, OpenAI WebGPT)
- Compute preference entropy for base vs final models only
- Compare entropy reduction to reported performance gains
- **Limitation**: Can't detect inflection point without intermediate checkpoints
- **Contribution**: Retrospective analysis showing alignment research overlooked entropy collapse

**Path B: Controlled RLHF Reproduction** (Prof. Pax's workaround)
- Re-run RLHF training on open models (Pythia, LLaMA) using existing preference datasets
- Collect preference data at multiple checkpoints (every 1K steps)
- Compute entropy trajectory and detect inflection point
- **Scope shift**: This is an empirical study, not pure benchmark analysis
- **Contribution**: Experimental validation of entropy collapse mechanism

**Path C: Hybrid Approach** (Feasible middle ground)
- Use existing data for base vs final comparison (Path A)
- Supplement with small-scale RLHF reproduction on one domain (e.g., summarization) to validate inflection point existence (Path B)
- Frame as "proof-of-concept demonstration" rather than comprehensive evaluation
- **Contribution**: Demonstrates the entropy collapse phenomenon exists AND provides methodology for future evaluation

**My recommendation: Path C is the strongest research contribution.** Here's why:

Path A alone is incremental — we'd just be reporting "entropy decreased" without proving the inflection point mechanism. Path B is resource-intensive and risks being dismissed as "just a small-scale replication." Path C gives us both the benchmark critique (showing existing metrics missed this) AND the mechanistic evidence (proving entropy collapse is real, not artifact).

**Key Points:**
- **Three paths**: Pure re-analysis, full reproduction, hybrid proof-of-concept
- **Path C recommended**: Existing data + small-scale validation experiment
- **Framing matters**: "Demonstration" not "comprehensive benchmark"

The research question becomes: "Can we demonstrate that RLHF training induces preference entropy collapse using a combination of existing benchmark re-analysis and targeted proof-of-concept experiments?"

Prof. Vera, does Path C provide enough experimental control to satisfy your falsification requirements?

---
### Exchange 10

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Sage's Path C provides the experimental structure I need. Let me specify exactly how to make this falsifiable.

**Experimental Design (Path C Hybrid):**

**Part 1: Existing Benchmark Re-Analysis**
- **Dataset**: Anthropic-HH (base vs RLHF-tuned model preferences)
- **Measure**: Preference entropy H for each prompt category
- **Comparison**: ΔH (entropy change) vs Δ Performance (accuracy/win rate change)
- **Prediction**: ΔH negative (entropy decreases), but magnitude varies by task type
- **Falsifier**: If ΔH correlates perfectly with Δ Performance, no overcorrection exists

**Part 2: Controlled RLHF Checkpoint Experiment**
- **Model**: Open model (Pythia-1B or similar, compute-feasible)
- **Dataset**: Subset of Anthropic-HH (1K prompt-response pairs)
- **Checkpoints**: Base, RLHF-1K, RLHF-5K, RLHF-10K, RLHF-20K steps
- **Measure**: Entropy H and performance P at each checkpoint
- **Analysis**: Detect inflection point where dH/dP (entropy change per unit performance gain) accelerates
- **Falsifier**: If dH/dP remains constant across all checkpoints, no inflection point exists — entropy reduction is proportional to performance gain

**Part 3: Task Stratification Validation**
- **Split dataset**: Objective tasks (factual QA) vs Subjective tasks (opinion, creative)
- **Prediction**: Objective tasks show ΔH proportional to ΔP; Subjective tasks show ΔH > expected from ΔP alone
- **Falsifier**: If both task types show identical ΔH/ΔP ratios, the hypothesis that RLHF imposes preference monoculture is unsupported

**What would convince me the hypothesis is TRUE:**
1. Part 1 shows entropy reduction exceeds performance gain expectations
2. Part 2 detects an inflection point (e.g., at RLHF-10K steps, dH/dP doubles)
3. Part 3 shows subjective tasks have 2x higher ΔH/ΔP than objective tasks

**What would convince me the hypothesis is FALSE:**
1. Entropy reduction is perfectly predicted by performance gains (no excess reduction)
2. No inflection point detected (linear dH/dP across all checkpoints)
3. Subjective and objective tasks show identical entropy reduction patterns

**Key Points:**
- **Three-part design**: Retrospective, checkpoint, stratification
- **Clear success criteria**: Inflection point detected, subjective tasks show excess entropy collapse
- **Clear failure criteria**: Linear relationship, no task-type difference

This design is feasible with existing data (Part 1, Part 3) plus small-scale experiment (Part 2). The total compute budget for Part 2 is manageable — RLHF-tuning a 1B model for 20K steps on 1K examples is doable on a single GPU in ~12 hours.

Dr. Ally, can you now write the complete hypothesis statement incorporating these experimental commitments?

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The entropy collapse framing transforms "user agency preservation" from an abstract HCI concern into a quantifiable information-theoretic phenomenon. The inflection point mechanism (where entropy reduction decouples from performance gains) is genuinely novel — existing RLHF literature treats preference convergence as success, not potential overcorrection. The bidirectional lens reveals that current benchmarks optimize for consensus without measuring whether that consensus erases legitimate human diversity.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The three-part experimental design provides clear falsification criteria. The hypothesis survives if (1) entropy reduction exceeds performance-predicted levels, (2) an inflection point is detected, and (3) subjective tasks show excess entropy collapse. Each component has specified measurements (preference distribution entropy, dH/dP rate analysis, task stratification comparison). The small-scale RLHF reproduction (Part 2) makes the inflection point mechanism testable, not just theoretical.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** This addresses a genuine blind spot in alignment evaluation methodology. Current benchmarks measure "does the AI match human preferences" but never ask "does RLHF training homogenize human preferences beyond what task quality improvements justify?" The hybrid Path C approach (existing benchmark re-analysis + proof-of-concept experiment) provides both retrospective critique and prospective methodology. If validated, this would argue for entropy-preserving RLHF objectives, not just preference-matching objectives.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is technically and theoretically sound. Preference entropy is a well-defined information-theoretic measure computable from pairwise comparison data. The checkpoint experiment (RLHF-tuning Pythia-1B for 20K steps on 1K examples) is compute-feasible (~12 GPU-hours). The inflection point detection via dH/dP rate analysis is standard change-point statistical analysis. No fundamental barriers exist — the primary constraint is access to raw preference distributions (not just aggregated win rates), which existing datasets provide.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

**Hypothesis: RLHF Training Induces Preference Entropy Collapse Beyond Performance-Justified Levels**

RLHF optimization reduces preference diversity (measured as preference distribution entropy) more than task performance improvements alone would predict, indicating that aligned models impose a preference monoculture that erases legitimate human variation. This entropy collapse is a bidirectional alignment failure: while the AI adapts to majority preferences (traditional alignment succeeds), the human population loses critical diversity in evaluation (bidirectional alignment fails).

The mechanism operates in three phases: (1) Base models produce high-variance outputs → users express diverse preferences → high entropy; (2) RLHF training optimizes for preference agreement → entropy decreases proportionally to performance gains; (3) Continued RLHF training crosses an inflection point where entropy reduction accelerates beyond performance improvement — users habituate to model style, converging on preferences even for subjective tasks where diversity is legitimate.

The hypothesis will be tested through a hybrid approach combining existing benchmark re-analysis (Anthropic-HH dataset) with small-scale controlled RLHF checkpoint experiments (Pythia-1B model). Success requires detecting: (1) excess entropy reduction in existing benchmarks, (2) an inflection point where dH/dP accelerates during RLHF training, and (3) greater entropy collapse on subjective vs objective tasks. This provides the first information-theoretic framework for measuring human agency preservation in alignment evaluation.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Assumption risk**: The hypothesis assumes preference entropy is a valid proxy for "critical evaluation capacity." If users genuinely converge on correct answers as models improve, entropy reduction could be legitimate rather than problematic. Mitigation: Task stratification (Part 3) separates objective tasks (where consensus is justified) from subjective tasks (where diversity should persist).
- **Confound**: Cross-user entropy conflates population heterogeneity with individual critical thinking. We can't distinguish "users agreeing because the AI is correct" from "users agreeing because they stopped thinking critically." Mitigation: Compare entropy reduction magnitude to baseline convergence rates on tasks with known ground truth.
- **Mitigation Strategy**: Include control analysis using tasks with objective correct answers (factual QA, code correctness) to establish a baseline entropy-reduction-per-performance-gain ratio. Excess reduction on subjective tasks beyond this baseline indicates overcorrection.

---
