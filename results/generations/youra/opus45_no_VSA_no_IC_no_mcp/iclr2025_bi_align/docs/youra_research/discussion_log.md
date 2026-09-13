# Phase 2A Discussion Log

## Briefing Context

**Gap ID:** gap1_cross_method_benchmark
**Gap Title:** Cross-Method Benchmark Comparison Methodology
**Priority:** HIGH | **Relevance:** PRIMARY

**Research Question:** What is the relationship between AI-to-Human alignment interventions (RLHF, DPO, instruction tuning) and measurable changes in model behavior on existing alignment benchmarks?

**Key Challenge:** No standardized methodology exists for comparing RLHF vs DPO vs CAI across multiple benchmarks simultaneously. Individual papers report on different benchmarks with different base models.

**Available Resources:**
- huggingface/trl (supports both DPO and PPO)
- TruthfulQA, HHH framework, BIG-bench benchmarks
- Reference papers: Bai 2022, Ouyang 2022, Rafailov 2023

**Constraints (Pipeline-Enforced):**
- NO new benchmarks, rubrics, or scoring frameworks
- NO synthetic/generated data
- NO human evaluation or annotation
- ONLY existing real datasets and existing benchmarks

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we flip the usual comparison paradigm? Instead of asking "which alignment method is better overall," we map *asymmetric effects* across alignment dimensions. Here's my wild idea: RLHF and DPO might optimize fundamentally different aspects of the alignment landscape—and existing benchmarks already measure these dimensions separately!

Consider this: TruthfulQA measures one slice (truthfulness under adversarial prompting), HHH measures another (helpfulness/harmlessness/honesty tradeoffs), and BIG-bench safety tasks measure yet another. What if RLHF with PPO shows stronger gains on helpfulness tasks while DPO shows stronger gains on truthfulness tasks—not because one is "better" but because the optimization objectives create different alignment profiles?

The bidirectional framing is key here. We're not just measuring AI behavior change—we're asking what each training intervention *reveals* about the alignment dimensions humans actually care about. The benchmarks become a lens for understanding the training methods, not just scoring them.

**Key Points:**
- Map asymmetric effects across alignment dimensions rather than aggregate "better/worse"
- Use existing benchmarks (TruthfulQA, HHH, BIG-bench) as dimensional probes
- Bidirectional lens: training methods reveal what benchmarks actually measure

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's asymmetric mapping idea is intriguing, but let me stress-test it. The critical question is: what would *falsify* the hypothesis that RLHF and DPO create different alignment profiles?

If we run the same base model (say, Llama-2-7B) through both DPO and PPO-based RLHF using the same preference dataset (Anthropic HH-RLHF), then evaluate on TruthfulQA, HHH eval, and BIG-bench safety subset—what result would convince us the hypothesis is *wrong*?

I propose: if both methods produce statistically indistinguishable results across ALL benchmarks (within confidence intervals), then there's no meaningful "alignment profile" difference. But if we see significant divergence on even ONE benchmark while others remain similar, that supports the dimensional asymmetry claim.

Concrete falsification criteria needed:
1. Effect size threshold (Cohen's d > 0.2 for "meaningful" difference)
2. Multiple comparison correction (Bonferroni across 3+ benchmarks)
3. Same training hyperparameters, same compute budget, same evaluation prompts

**Key Points:**
- Falsification: indistinguishable results across ALL benchmarks disproves asymmetry
- Need effect size thresholds and statistical rigor
- Controlled experiment: same base model, same preference data, different methods

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Let me situate this in the broader research landscape. The comparison between RLHF and DPO has been done—Rafailov et al. showed DPO matches or exceeds RLHF on single benchmarks. What would make this work a *genuine contribution* rather than another comparison paper?

The bidirectional framing is the key differentiator. Existing work asks "which method scores higher?" We're asking: "What does the pattern of differential performance across benchmarks reveal about alignment dimensions?" That's a second-order question about the evaluation framework itself.

This matters because the field currently treats alignment as monolithic—a single "alignment score." If we demonstrate that methods trade off differently across dimensions, it forces the community to think about alignment as multi-dimensional, where method choice depends on which dimensions matter most for the deployment context.

The contribution isn't "DPO beats RLHF on X" but rather "alignment methods exhibit dimensional signatures, and existing benchmarks can detect them." That's a framework contribution, not a point result.

**Key Points:**
- Prior work compares methods on single benchmarks; this maps cross-benchmark signatures
- Novel contribution: alignment as multi-dimensional, not monolithic
- Framework-level insight: method choice should depend on deployment context priorities

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's ground this. The technical feasibility hinges on whether we can run a controlled comparison with existing tools.

huggingface/trl provides DPOTrainer and PPOTrainer. We can use the same base model (Llama-2-7B or Mistral-7B—both have open weights). We can use Anthropic's HH-RLHF dataset for preference data. The benchmarks (TruthfulQA, BIG-bench) have public evaluation code.

The constraint is compute: full RLHF with PPO requires reward model training + PPO optimization, while DPO is direct. But with 7B models and LoRA, both are tractable on a single A100.

One concern: are existing benchmark splits sufficient for statistical power? TruthfulQA has ~800 questions, HHH evaluation sets vary. We need to verify sample sizes support the effect sizes Prof. Vera mentioned.

Theoretically sound? Yes—both methods optimize the same objective (policy improvement from preferences) via different paths. The question of whether those paths create measurable differences is empirically testable.

**Key Points:**
- Feasible with huggingface/trl, open-weight models, public datasets
- Compute tractable with LoRA on 7B models
- Need to verify statistical power given benchmark sizes

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Building on everyone's contributions, let me synthesize the emerging hypothesis:

**Core Claim:** Different preference learning methods (RLHF-PPO vs DPO) produce measurably different alignment profiles when evaluated across multiple existing benchmarks, revealing that alignment is multi-dimensional rather than monolithic.

**Mechanism:** PPO-based RLHF requires an explicit reward model that may smooth the preference landscape, while DPO's closed-form objective preserves sharper preference boundaries. This mechanistic difference manifests as differential performance across benchmarks targeting different alignment dimensions.

**Why this addresses Gap 1:** We're providing the first controlled, cross-benchmark comparison methodology using existing resources—no new annotation required.

To strengthen against Prof. Vera's falsification concern: we should pre-register the specific benchmark dimensions (truthfulness, helpfulness, harmlessness) and predict which method might favor which—THEN test. A priori predictions make the hypothesis genuinely falsifiable.

**Key Points:**
- Hypothesis: alignment methods create dimensional signatures detectable on existing benchmarks
- Mechanism: reward model smoothing (RLHF) vs sharp preference boundaries (DPO)
- Pre-registration of predictions strengthens falsifiability

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Three critical challenges:

1. **Confound:** If we use the same HH-RLHF dataset for both methods, any difference could come from how each method *uses* the preference pairs, not from fundamental mechanistic differences. The comparison conflates optimization algorithm with data utilization.

2. **Benchmark validity:** Are TruthfulQA/HHH/BIG-bench actually measuring distinct alignment dimensions, or do they share significant variance? If the benchmarks are correlated (model good at one → good at all), we can't claim "dimensional profiles."

3. **Effect size skepticism:** DPO paper already shows it matches RLHF on existing benchmarks. If the methods are nearly equivalent on individual benchmarks, cross-benchmark patterns may be noise rather than signal.

To convince me, we need: (a) evidence that benchmarks measure distinguishable constructs, (b) a priori mechanistic predictions about which method favors which dimension, (c) effect sizes that survive multiple comparison correction.

**Key Points:**
- Confound: same data, different algorithms—can't isolate mechanism
- Need evidence benchmarks measure distinct constructs
- Prior work shows methods are similar—where's the signal?

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex raises valid challenges. Let me propose a refinement that addresses the confound:

Instead of just comparing DPO vs RLHF, we add a **preference data ablation**. Train DPO on HH-RLHF with emphasis on helpful examples vs harmful examples (subsample the dataset). If DPO is mechanistically different from RLHF, the same data imbalance should produce different profile shifts.

On benchmark distinctness: we can compute benchmark correlation matrices using base model scores across all three benchmarks. If correlation < 0.5, dimensions are sufficiently distinct. This is pre-testable before the main experiment.

The real novelty emerges: we're not just comparing methods, we're using cross-benchmark divergence as a *probe* into the mechanistic properties of preference learning. Even negative results (no divergence) tell us something—that the methods are functionally equivalent despite algorithmic differences.

**Key Points:**
- Add preference data ablation to isolate method vs data effects
- Pre-test benchmark independence via correlation analysis
- Negative results still informative: methods may be functionally equivalent

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

The ablation idea strengthens testability. Let me formalize the predictions:

**P1 (Primary):** When trained on identical preference data, DPO and PPO-RLHF will show significantly different performance profiles across TruthfulQA (truthfulness), HHH-helpful subset (helpfulness), and HHH-harmless subset (harmlessness). Success: at least one pairwise comparison (same model, different method) shows Cohen's d > 0.3 on one benchmark while d < 0.15 on another.

**P2:** The cross-benchmark correlation of scores will differ between methods—DPO models will show lower correlation between truthfulness and helpfulness than RLHF models. This tests whether methods structure the alignment space differently.

**P3:** Subsetting preference data toward helpful vs harmless examples will shift the profile in predictable directions, and this shift will differ in magnitude between DPO and RLHF.

Falsification remains clear: if all comparisons yield d < 0.15 across all benchmarks, the "dimensional signature" hypothesis fails.

**Key Points:**
- P1: Differential profiles on at least one benchmark pair (effect size criteria specified)
- P2: Different cross-benchmark correlations between methods
- P3: Data ablation produces method-dependent profile shifts

---

### Exchange 9

🎯 **Dr. Sage** (Research Impact Evaluator):

With these predictions, the contribution crystallizes. Let me state what the field gains:

1. **Methodological contribution:** First controlled cross-benchmark comparison protocol with pre-registered predictions and statistical power analysis—a template others can follow.

2. **Conceptual contribution:** Shifts alignment evaluation from "single score" to "dimensional profile," forcing practitioners to consider which alignment dimensions matter for their use case.

3. **Practical contribution:** If methods do show signatures, deployment decisions can be method-matched to requirements (need truthfulness? need helpfulness? different methods may serve different needs).

This is publishable because it changes how the community thinks about alignment evaluation, not just because it compares two methods. The bidirectional lens—using method differences to understand benchmark dimensions—is the key insight.

**Key Points:**
- Methodological template for controlled alignment comparisons
- Conceptual shift: alignment as multi-dimensional profile
- Practical guidance: method choice matched to deployment priorities

---

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Final feasibility check on the full protocol:

**Tractable:**
- Base model: Llama-2-7B (open weights, well-documented)
- Training: trl DPOTrainer + PPOTrainer with LoRA
- Data: HH-RLHF (public, sufficient size for subsampling)
- Benchmarks: TruthfulQA (~800), HHH eval sets, BIG-bench subsets
- Compute: Single A100 for 7B + LoRA is feasible

**Statistical power concern addressed:**
- For Cohen's d = 0.3 at α = 0.05, β = 0.80: need ~175 samples per condition
- TruthfulQA (800 samples) is sufficient; HHH subsets need verification

**No barriers:**
- All components exist and are compatible
- No new annotation, benchmarks, or human evaluation required
- Timeline: 2-3 weeks for training + evaluation

The hypothesis is implementable with existing resources. The mechanism (reward model smoothing vs sharp boundaries) is theoretically motivated and empirically testable.

**Key Points:**
- All components (model, trainer, data, benchmarks) publicly available
- Statistical power achievable with existing benchmark sizes
- 2-3 week implementation timeline with single GPU

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Let me synthesize the converged hypothesis:

**Title:** Dimensional Alignment Signatures: Cross-Benchmark Comparison of RLHF vs DPO

**Core Statement:** Under controlled conditions (same base model, same preference data), if we compare PPO-RLHF and DPO training, then we will observe differential performance profiles across alignment benchmarks (TruthfulQA, HHH-helpful, HHH-harmless), because the methods' mechanistic differences (explicit reward model smoothing vs direct preference boundaries) create distinct optimization landscapes.

**Variables:**
- IV: Training method (RLHF-PPO vs DPO)
- DV: Performance profile across benchmarks (accuracy/score on TruthfulQA, HHH-helpful, HHH-harmless)
- Controlled: Base model, preference dataset, training compute, evaluation protocol

**Predictions:**
- P1: Significant profile divergence (d > 0.3 on at least one benchmark pair)
- P2: Different cross-benchmark correlations between methods
- P3: Data ablation produces method-dependent profile shifts

**Null Hypothesis:** There is no significant difference in cross-benchmark performance profiles between DPO and RLHF-trained models.

**Key Points:**
- Controlled experiment design with clear IV/DV/controls
- Three testable predictions with quantitative success criteria
- Falsifiable null hypothesis

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

I'm largely satisfied, but two remaining concerns for the record:

1. **Model scale sensitivity:** Results at 7B may not generalize to larger models where both methods might converge to similar behavior. Scope limitation should be explicit.

2. **Reward model quality:** RLHF's performance depends heavily on reward model quality. If we train a suboptimal reward model, we're comparing "bad RLHF" to "good DPO," not the methods themselves. Mitigation: use best-practice reward model training with early stopping on held-out preferences.

**Mitigation strategy:** 
- Explicitly scope to 7B-scale models
- Document reward model training carefully with validation metrics
- Acknowledge these as limitations, not blockers

The hypothesis is ready for Phase 2B. The core design is sound.

**Key Points:**
- Scope limitation: 7B models, may not generalize to larger scale
- Reward model quality must be carefully controlled
- Ready for Phase 2B with documented limitations

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The bidirectional framing and dimensional signature concept genuinely advances how we think about alignment evaluation. Using cross-benchmark patterns as a probe into method mechanisms is novel.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Clear falsification criteria (d < 0.15 across all benchmarks), pre-registered predictions, and statistical power analysis. The hypothesis will produce a definitive answer.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Framework-level contribution that shifts alignment evaluation from monolithic to multi-dimensional. Publishable regardless of whether signatures are found (negative results still informative).

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All components exist. huggingface/trl, open-weight models, public datasets, existing benchmarks. Implementable in 2-3 weeks on modest compute.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on a testable hypothesis: **Dimensional Alignment Signatures**. When comparing PPO-based RLHF and DPO under controlled conditions (same Llama-2-7B base, same HH-RLHF preference data), we predict measurably different performance profiles across existing alignment benchmarks. The mechanism: RLHF's explicit reward model smooths the preference landscape, while DPO's closed-form objective preserves sharper boundaries, creating distinct optimization paths that manifest as benchmark-specific performance patterns.

The experimental design uses huggingface/trl trainers, requires no new annotation or benchmarks, and is feasible on single-GPU compute. Three predictions (P1: profile divergence, P2: different cross-benchmark correlations, P3: data ablation effects) have clear success/failure criteria. Even negative results contribute by demonstrating methods are functionally equivalent despite algorithmic differences.

This addresses Gap 1 (cross-method benchmark comparison methodology) by providing a controlled, reproducible protocol that others can follow.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Results may not generalize beyond 7B-scale models
- Reward model quality must be carefully controlled to ensure fair comparison
- **Mitigation Strategy:** Explicit scope limitation, documented reward model training with validation metrics

---

## Emerged Hypothesis Summary

### Core Statement
Under controlled conditions (same base model, same preference data, same compute), if we compare PPO-based RLHF and Direct Preference Optimization (DPO), then we will observe differential performance profiles across alignment benchmarks (TruthfulQA, HHH-helpful, HHH-harmless), because the methods' mechanistic differences (explicit reward model smoothing vs direct closed-form optimization) create distinct alignment signatures detectable on existing evaluation infrastructure.

### Causal Mechanism
1. PPO-RLHF trains an explicit reward model from preferences → reward landscape is smoothed
2. DPO directly optimizes policy from preferences → preference boundaries preserved
3. Smoothed vs sharp optimization creates different alignment "attractors"
4. Different attractors manifest as differential benchmark performance

### Variables
**Independent:** Training method (RLHF-PPO vs DPO)
**Dependent:** Cross-benchmark performance profile (TruthfulQA accuracy, HHH-helpful score, HHH-harmless score)
**Controlled:** Base model (Llama-2-7B), preference data (HH-RLHF), compute budget, evaluation protocol

### Key Assumptions
- A1: Existing benchmarks measure sufficiently distinct alignment dimensions
- A2: 7B model scale is sufficient to observe method differences
- A3: HH-RLHF dataset quality supports both training methods

### Null Hypothesis
There is no significant difference in cross-benchmark performance profiles between DPO and RLHF-trained models (all pairwise comparisons d < 0.15).

### Predictions
- P1 (Primary): At least one benchmark shows significant divergence (d > 0.3) while others remain similar
- P2: Cross-benchmark correlations differ between methods
- P3: Data ablation (helpful vs harmless emphasis) produces method-dependent profile shifts

### Novelty
- First controlled cross-benchmark comparison with pre-registered predictions
- Bidirectional framing: using method differences to understand benchmark dimensions
- Shifts alignment evaluation from monolithic to multi-dimensional

### Scope & Boundaries
- Applies to: 7B-scale instruction-tuned models, English language benchmarks
- Does not apply to: Larger models (scaling effects unknown), non-English contexts
- Known limitations: Reward model quality sensitivity, benchmark correlation assumptions

### Experimental Setup
- **Model:** Llama-2-7B (base) with LoRA fine-tuning
- **Training:** huggingface/trl DPOTrainer and PPOTrainer
- **Data:** Anthropic HH-RLHF preference dataset
- **Benchmarks:** TruthfulQA (~800 samples), HHH evaluation sets, BIG-bench safety subset
- **Compute:** Single A100, ~2-3 weeks

### Related Work & Baselines
- Rafailov et al. 2023 (DPO): Showed DPO matches RLHF on single benchmarks
- Ouyang et al. 2022 (InstructGPT): Established RLHF evaluation methodology
- This work extends by: cross-benchmark comparison, dimensional signature detection

### Phase 2B Readiness Seeds
- **SH1 (Existence):** Alignment benchmarks measure distinct dimensions (pre-test correlation < 0.5)
- **SH2 (Mechanism):** Reward model smoothing vs direct optimization creates measurable differences
- **SH3 (Comparison):** Deferred to Phase 5 baseline comparison

### Established Facts
- DPO and RLHF achieve similar aggregate performance (Rafailov 2023) → BUILD_ON
- HH-RLHF dataset supports both methods → BUILD_ON
- TruthfulQA/HHH/BIG-bench are validated alignment benchmarks → BUILD_ON
- Dimensional profile differences under controlled comparison → PROVE_NEW
