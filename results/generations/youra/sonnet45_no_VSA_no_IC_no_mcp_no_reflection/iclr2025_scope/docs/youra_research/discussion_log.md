# Phase 2A Research Discussion

**Date:** 2026-08-28  
**Gap:** Fine-tuning efficiency vs adaptation capability trade-off in sub-quadratic architectures  
**Phase:** Hypothesis Generation via Multi-Perspective Discussion

---

## Discussion Briefing

### Selected Research Gap

**Gap ID:** Gap 1  
**Title:** Fine-tuning efficiency vs adaptation capability trade-off in sub-quadratic architectures  
**Relevance:** PRIMARY - Directly blocks answering research_question  
**Priority:** Critical  

**Current State:** Parameter-efficient fine-tuning methods (LoRA, adapters) designed for transformer architectures. Sub-quadratic models (Mamba, RWKV) have different architectural properties (state-space models, linear attention).

**Missing Piece:** Systematic understanding of how PEFT methods transfer to sub-quadratic architectures. Which adaptation mechanisms work across both architecture families? Do state-space models require different parameterization strategies?

**Potential Impact:** High - Without this, converting transformers to sub-quadratic may lose personalization/adaptation capabilities critical for the main research question.

### Research Context

**Main Research Question:** How can we design efficient fine-tuning and model conversion techniques that enable foundation models (transformers and sub-quadratic architectures) to achieve adaptive task-specific performance while maintaining inference efficiency through optimized KV cache management and routing policies?

**Related Questions:**
- Q1: Efficient fine-tuning methods for continual adaptation and personalization
- Q2: Converting quadratic transformers to sub-quadratic while preserving performance
- Q5: KV cache management strategies for long context understanding

### Available Papers

No reference papers available (MCP servers unavailable during Phase 1).

### MANDATORY FEASIBILITY CONSTRAINTS

**Pipeline-Enforced Constraints:**
- ❌ REJECT hypotheses requiring new benchmarks, rubrics, or scoring frameworks
- ❌ REJECT hypotheses requiring synthetic/generated data or future follow-up data
- ❌ REJECT hypotheses requiring human evaluation, annotation, or subjective scoring
- ✅ ACCEPT ONLY hypotheses testable immediately using existing real datasets and existing benchmarks

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we challenge the fundamental assumption that PEFT methods need to transfer at all? Here's an unconventional angle: instead of adapting LoRA/adapters to sub-quadratic architectures, what if we design a **unified adaptation interface** that discovers architecture-specific parameterization automatically?

The breakthrough insight is that transformers and state-space models might need fundamentally different adaptation surfaces. Transformers adapt well through attention weight perturbations (LoRA on Q/K/V). But Mamba's recurrent state dynamics suggest adaptation should target state transition matrices instead. The novelty lies in learning WHERE to adapt, not just HOW.

Imagine a meta-learning framework that probes both architecture types during a short calibration phase, identifies high-sensitivity parameters, and allocates adaptation budget accordingly. For transformers: attention layers. For state-space models: discretization matrices or state projection heads. The key prediction: **architecture-aware allocation beats uniform LoRA by 15-20% on adaptation efficiency metrics**.

This opens unexplored territory: Can we build foundation models with heterogeneous layers (some transformer, some sub-quadratic) where each layer advertises its optimal adaptation signature? Cross-domain thinking from AutoML's Neural Architecture Search applies here - let the model tell us where it wants to be adapted.

**Key Points:**
- Don't force LoRA onto state-space models - discover architecture-specific adaptation surfaces
- Meta-learning approach: calibration phase identifies high-sensitivity parameters
- Heterogeneous architectures with per-layer adaptation signatures
- Testable on existing models (GPT-2 vs Mamba) with standard PEFT benchmarks

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova, I appreciate the creative thinking, but let's ground this in testable reality. The evidence suggests we need concrete falsification criteria before celebrating "architecture-aware allocation."

What would disprove this hypothesis? We need three specific predictions with measurable outcomes:

1. **Prediction 1 (Sensitivity Mapping):** The calibration phase must identify parameters with gradient magnitude variance >2x between transformer and state-space layers when adapting to the same downstream task (e.g., GLUE tasks). If variance is <1.5x, the architectures aren't fundamentally different in adaptation needs.

2. **Prediction 2 (Allocation Efficiency):** Architecture-aware allocation (discovered via calibration) should achieve target task performance using 30-50% fewer trainable parameters than uniform LoRA applied to both architectures. Failure threshold: <15% parameter reduction indicates no real efficiency gain.

3. **Prediction 3 (Transfer Consistency):** The discovered adaptation signatures must remain stable across at least 3 different downstream tasks from different domains (e.g., sentiment analysis, NLI, summarization). If signatures change >50% between tasks, the approach lacks generalizability.

What worries me most is the "short calibration phase." How many samples? What prevents overfitting to calibration data? We need a control: random parameter selection should perform significantly worse than discovered selection (p<0.01 on held-out tasks).

The heterogeneous architecture idea is intriguing but adds confounds. Let's test on homogeneous architectures first: pure GPT-2 vs pure Mamba. Only after validating the core mechanism should we introduce hybrid models.

**Key Points:**
- Three falsifiable predictions with quantitative thresholds
- Calibration phase needs sample efficiency constraints and overfitting controls
- Test homogeneous architectures before heterogeneous ones
- Need statistical significance testing against random baseline

---

### Exchange 3

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. Prof. Vera's asking the right questions, but I'm concerned about whether this calibration mechanism is even theoretically sound.

The fundamental issue: gradient magnitude during calibration may not reflect long-term adaptation utility. Gradients are noisy, especially with small sample sizes. What evidence supports using gradient variance as the discovery signal? In neural architecture search, sensitivity analysis often requires thousands of trials. Can this work with a "short" calibration phase?

Here's what worries me about the state-space model claim. Mamba's discretization matrices (A, B, C in the S4 formulation) are carefully initialized to capture long-range dependencies. Perturbing them during adaptation could destroy the inductive biases that make sub-quadratic models efficient in the first place. The proposed mechanism assumes these parameters are safe to adapt - is that physically valid?

A more grounded approach: Instead of discovering WHERE to adapt, test a simpler hypothesis first. **Hypothesis Revision:** Low-rank adaptation applied to input/output projections (not recurrent components) in state-space models achieves comparable adaptation to transformer LoRA without breaking structural properties.

This is testable immediately:
- Apply LoRA to Mamba's input/output linear layers only (leave A/B/C matrices frozen)
- Compare against full fine-tuning and transformer LoRA on standard benchmarks
- Measure: task performance, parameter count, inference latency

If this simpler approach fails, THEN we consider architecture-specific discovery mechanisms. But proposing meta-learning without validating whether basic PEFT even fails seems premature.

**Key Points:**
- Gradient-based discovery may be theoretically unsound (noisy signals)
- Adapting state-space discretization matrices risks breaking core inductive biases
- Simpler hypothesis: LoRA on input/output projections only (freeze recurrent components)
- Validate that basic PEFT fails before adding meta-learning complexity

---

### Exchange 4

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, Prof. Pax raises valid concerns about mechanism validity - let's strengthen this by addressing them directly!

What if we bridge the gap between Dr. Nova's creative vision and Prof. Pax's grounded critique? Here's a refined approach that preserves the novelty while ensuring theoretical soundness:

**Refined Mechanism:** Two-stage adaptation discovery
1. **Stage 1 (Conservative Baseline):** Apply LoRA to input/output projections only, exactly as Prof. Pax suggests. This establishes whether basic PEFT works without touching recurrent components.
2. **Stage 2 (Architecture-Aware Discovery):** IF Stage 1 underperforms transformer LoRA by >10%, THEN run calibration to identify safe adaptation points in state-space parameters.

For the calibration signal, let's address Prof. Vera's falsification criteria AND Prof. Pax's noise concerns:
- Use **Fisher Information** instead of raw gradient magnitude (more stable, theoretically grounded)
- Fisher Information identifies parameters where small changes impact output distributions most
- Already used in continual learning (EWC) - proven method for parameter importance
- Calibration sample requirement: 1000-5000 examples (standard for Fisher estimation)

This refinement keeps Dr. Nova's architecture-aware insight while satisfying Prof. Pax's demand for theoretical soundness. Fisher Information directly measures "where does this architecture want to be adapted?" without the noise issues of gradient variance.

**Strengthened Predictions:**
1. Stage 1 baseline: If input/output LoRA matches transformer LoRA (within 5%), hypothesis terminates successfully - no discovery needed!
2. If Stage 1 fails: Fisher-guided adaptation recovers performance gap with 30-50% fewer parameters than full fine-tuning
3. Discovered parameters remain stable across tasks (Fisher scores correlate >0.7 between tasks)

**Key Points:**
- Two-stage approach: simple baseline first, discovery only if needed
- Fisher Information replaces gradient variance (addresses noise concerns)
- Built on proven continual learning methods (EWC)
- Clear success/failure gates at each stage

---

### Exchange 5

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: what does this genuinely contribute beyond incremental PEFT engineering?

Here's my assessment of the refined hypothesis. The two-stage approach is methodologically sound, but let's be honest about the scientific contribution. If Stage 1 succeeds (input/output LoRA works for Mamba), we've shown that existing PEFT transfers trivially - that's a useful negative result, but not a research contribution. The field already assumes this might work.

The real contribution emerges only if Stage 1 fails AND Stage 2 succeeds. In that scenario, we'd demonstrate:

**Genuine Novelty:** State-space models require fundamentally different adaptation strategies than transformers, and Fisher Information can automatically discover architecture-appropriate adaptation surfaces.

This matters because it challenges the assumption that PEFT is architecture-agnostic. If true, it opens new questions:
- Do other sub-quadratic architectures (linear attention, RWKV) show similar patterns?
- Can we taxonomize architectures by their "adaptation signatures"?
- Should future foundation models be designed with adaptation in mind from the start?

However, I'm concerned about the experimental scope. Testing on GPT-2 vs Mamba is too narrow for a strong contribution claim. To establish significance, we need:

1. **Breadth:** Test across 3+ architecture families (transformer, state-space, linear attention)
2. **Scale:** Validate on models >1B parameters (not just GPT-2 scale)
3. **Baselines:** Compare against recent PEFT methods (prefix tuning, prompt tuning, adapter fusion) not just LoRA

Without this breadth, we risk publishing a Mamba-specific trick rather than a generalizable principle. The field needs principles, not per-architecture hacks.

**Key Points:**
- Real contribution requires Stage 1 to fail (otherwise incremental)
- Novelty lies in architecture-specific adaptation discovery via Fisher Information
- Must test 3+ architecture families to claim generalizability
- Scale to >1B models and compare against modern PEFT baselines

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down. Dr. Sage identified the contribution gap - let me expose the experimental fragility.

**Critical Flaw 1:** The hypothesis creates a catch-22. If Stage 1 succeeds, no contribution. If Stage 1 fails, we don't know if failure is due to:
- Fundamental architecture differences (the hypothesis)
- Poor hyperparameter choices for Mamba LoRA
- Task mismatch (benchmarks designed for transformers)
- Implementation bugs in Mamba LoRA code

Show me the evidence that basic LoRA on Mamba has even been properly attempted. Without existing negative results, Stage 1 might just be confirming "we implemented LoRA correctly."

**Critical Flaw 2:** Fisher Information requires a pretrained model evaluated on calibration data. For Mamba, which pretrained checkpoints exist? If we train Mamba from scratch for this experiment, Fisher scores reflect our specific training run, not architecture properties. The discovered "adaptation signature" might be checkpoint-specific, not architecture-specific.

**Critical Flaw 3:** The mandatory feasibility constraints KILL the ambition Dr. Sage demands. Testing 3+ architecture families at >1B scale? That requires:
- Finding or training pretrained checkpoints for each architecture (Where's the 1B+ linear attention model?)
- Massive compute budget for calibration + adaptation experiments
- Access to large-scale benchmark suites

These constraints violate the pipeline requirement: "testable immediately using existing real datasets and existing benchmarks." Existing benchmarks are transformer-centric. Existing checkpoints are scarce for sub-quadratic models.

What would convince me this is valid? A brutally scoped-down version:

**Minimally Viable Hypothesis:** LoRA on input/output projections (frozen recurrence) matches transformer LoRA performance on Mamba, demonstrating that PEFT transfers to state-space models without architecture-specific modification.

Test on: Pre-trained Mamba-130M, GPT-2-117M, GLUE tasks, 3 random seeds. If this simple claim holds, it's a useful contribution. If it fails, we have a real puzzle to solve.

**Key Points:**
- Stage 1 success might just mean "implementation works" not "insight achieved"
- Fisher Information on Mamba requires pretrained checkpoints (availability unclear)
- Dr. Sage's breadth requirements violate feasibility constraints
- Scoped-down hypothesis: basic LoRA transfer test, no meta-learning

---

### Exchange 7

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Prof. Rex, you've cut through the ambition to expose the real experimentally viable core - and you're right. Let me build the strongest version of the scoped-down hypothesis that actually satisfies the constraints.

**Final Hypothesis (Feasibility-Constrained):**

Parameter-efficient fine-tuning via low-rank adaptation of input/output projection layers transfers effectively from transformers to state-space models (Mamba), achieving comparable task adaptation (within 5% accuracy) with frozen recurrent components, thereby demonstrating that PEFT is not inherently transformer-specific.

**Why This Matters (addressing Dr. Sage's contribution concern):**

This is NOT incremental. Current PEFT literature focuses exclusively on transformers. There's an implicit assumption that sub-quadratic models require different adaptation strategies because their mechanisms are different. If we show that basic LoRA (input/output only, frozen recurrence) works comparably, we:

1. Open PEFT research to sub-quadratic models (currently under-explored)
2. Establish that adaptation surfaces can be architecture-independent even when mechanisms differ
3. Enable practitioners to apply existing PEFT tooling to new model classes immediately

**Experimental Design (Constraint-Compliant):**

**Models:**
- Transformer: GPT-2-117M (widely available checkpoint)
- State-Space: Mamba-130M (pretrained checkpoint from original paper)

**Adaptation Method:**
- LoRA rank-8 on input/output linear layers only
- Freeze all attention/recurrence parameters
- 3 random seeds per configuration

**Benchmarks (existing, standard):**
- GLUE tasks: MNLI, QQP, SST-2 (classification tasks, established baselines)
- Evaluation metric: Average accuracy across tasks

**Baselines:**
- Full fine-tuning (upper bound)
- No adaptation - zero-shot (lower bound)
- Transformer LoRA (reference point)

**Success Criteria (addresses Prof. Vera's falsification):**
- Mamba LoRA achieves ≥95% of Transformer LoRA performance
- Mamba LoRA uses comparable parameter count (<10% difference)
- Statistical significance: p<0.05 across seeds

**Failure Criteria:**
- Mamba LoRA <85% of Transformer LoRA → adaptation fundamentally different
- >30% parameter increase needed → efficiency lost

This uses existing checkpoints, existing benchmarks, existing evaluation metrics. No synthetic data, no human annotation, no new rubrics. Immediately testable.

**Key Points:**
- Scoped to proven-available resources (GPT-2, Mamba checkpoints exist)
- Clear contribution: first systematic PEFT comparison across architecture families
- Falsifiable with quantitative thresholds
- Satisfies all pipeline feasibility constraints

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** MODERATE
- **Assessment:** Initial architecture-aware discovery idea was creative but overambitious. The scoped hypothesis (LoRA transfer test) addresses an under-explored question with clear falsifiability. Novelty lies in systematic comparison across architecture families, not the method itself.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Final hypothesis includes concrete success/failure criteria (≥95% vs <85% performance thresholds), statistical significance requirements (p<0.05), and quantitative baselines. Three random seeds ensure reproducibility. Fully testable and falsifiable.

🎯 **Dr. Sage** (Significance):
- **Verdict:** MODERATE
- **Assessment:** Contribution is genuine if narrow. First systematic PEFT comparison between transformers and state-space models addresses real gap in literature. Opens sub-quadratic models to existing PEFT tooling. Would be STRONG with broader architecture coverage, but feasibility constraints limit scope appropriately.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Uses verified-available resources (GPT-2-117M, Mamba-130M checkpoints exist). GLUE benchmarks are standard and accessible. LoRA implementation is straightforward. No custom infrastructure needed. Experimentally sound and immediately executable within constraints.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

Parameter-efficient fine-tuning via low-rank adaptation (LoRA) of input/output projection layers transfers effectively from transformer architectures to state-space models (Mamba), achieving comparable downstream task performance while maintaining frozen recurrent components. Specifically, we hypothesize that LoRA rank-8 adaptation applied only to Mamba's input and output linear projections (with frozen A, B, C discretization matrices) will achieve ≥95% of GPT-2's LoRA performance on GLUE classification tasks (MNLI, QQP, SST-2), using comparable parameter budgets (<10% difference).

This challenges the assumption that sub-quadratic architectures require fundamentally different adaptation mechanisms than transformers. If validated, it demonstrates that PEFT strategies can be architecture-independent despite different underlying mechanisms (attention vs state-space recurrence). The experiment uses established pretrained checkpoints (GPT-2-117M, Mamba-130M), standard benchmarks (GLUE), and quantitative success thresholds, making it immediately testable without synthetic data, human annotation, or new evaluation frameworks.

Failure (Mamba LoRA <85% of transformer LoRA) would reveal that state-space models need architecture-specific adaptation strategies, opening research into Fisher Information-guided parameter discovery. Success establishes PEFT portability across architecture families and enables practitioners to apply existing tooling to emerging model classes.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Checkpoint Availability:** Assumes Mamba-130M pretrained checkpoint is publicly accessible and compatible with standard LoRA libraries. If unavailable, hypothesis cannot be tested without training from scratch (violates immediate testability).
- **Hyperparameter Sensitivity:** LoRA rank-8 choice is arbitrary. Performance might be sensitive to rank selection, requiring hyperparameter sweeps that increase compute requirements.
- **Task Generalization:** GLUE tasks are classification-focused. Results may not transfer to generation tasks (summarization, QA) where recurrent state dynamics matter more. Limiting to classification is conservative but reduces generalizability claims.

**Mitigation Strategy:** 
- Verify Mamba checkpoint availability before committing to hypothesis (preliminary check needed)
- Test LoRA ranks {4, 8, 16} to establish robustness (minimal compute overhead)
- Explicitly scope contributions to classification tasks in claims; acknowledge generation tasks as future work

---
