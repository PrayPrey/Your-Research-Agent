# Phase 2A Research Discussion Log

**Gap ID:** gap-1-cross-benchmark-correlation
**Gap Title:** No Systematic Cross-Benchmark Correlation Study
**Timestamp:** 2026-08-24
**Architecture:** Self-Play Tikitaka Loop (Independent Controller Ablation)

---

## Discussion Briefing

### Research Gap Context

**Current State:** Individual benchmarks (TruthfulQA, HaluEval, FactScore) evaluated in isolation. BenchBench (2024) examines benchmark agreement methodology but not specific truthfulness benchmark correlations.

**Missing Piece:** Empirical study computing Spearman/Pearson correlations between TruthfulQA (MC1/MC2), HaluEval (detection accuracy), and FactScore (precision) on the same model population.

**Primary Research Question:** How do existing truthfulness and reliability benchmarks (e.g., TruthfulQA, HaluEval, FactScore) correlate with each other and with downstream task performance?

### Key Evidence from Phase 1

1. **BenchBench (Perlitz et al., 2024):** Studies benchmark agreement but not truthfulness-specific correlations
2. **Ailem et al. (2024):** Shows non-random correlation in model performance — methodology applicable
3. **"The Moving Target" (Fan et al., 2026):** Audits TruthfulQA across model versions but not cross-benchmark
4. **"Benchmarks Are Not Monolithic" (Siedler & Sassoon, 2026):** Sample-level heterogeneity in MMLU, TruthfulQA, HellaSwag

### Implementation Resources

- **EleutherAI/lm-evaluation-harness** (13.7k★): Unified framework for running TruthfulQA, MMLU, HellaSwag on same models
- **sylinrl/TruthfulQA** (927★): Official benchmark with 817 questions across 38 categories
- **RUCAIBox/HaluEval** (595★): 35K samples with task categories
- **shmsw25/FActScore** (442★): Atomic fact decomposition and verification

### Feasibility Constraints (Pipeline-Enforced)

- ✅ Uses EXISTING benchmarks only (TruthfulQA, HaluEval, FactScore, MMLU, HellaSwag)
- ✅ No new benchmarks, rubrics, or scoring frameworks required
- ✅ No synthetic/generated data required
- ✅ No human evaluation or annotation required
- ✅ Can be tested immediately with existing model outputs

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we're looking at this benchmark correlation question from entirely the wrong angle? Everyone's been evaluating these benchmarks in isolation, treating them as independent measurements of "truthfulness" — but what if they're actually measuring fundamentally different cognitive phenomena?

Here's what excites me: TruthfulQA specifically targets *misconceptions* that humans commonly hold and models often learn from training data. HaluEval focuses on *generation failures* where models confabulate details. FactScore measures *atomic factual precision* in long-form text. These aren't three views of the same underlying trait — they might be three entirely different failure modes!

What if instead of asking "do these benchmarks correlate?", we ask "what latent structure explains their divergence?" Imagine this: we could discover that models have independent "truthfulness axes" — one for resisting popular misconceptions, another for generation coherence, another for factual recall. That would be far more interesting than finding they're all highly correlated!

The lm-evaluation-harness gives us something powerful: we can run all these benchmarks on the *same* model population. BenchBench showed benchmark agreement isn't guaranteed — let's embrace that! Factor analysis or principal component analysis on benchmark scores might reveal whether we have one "general truthfulness" factor or multiple independent dimensions.

**Key Points:**
- These benchmarks may measure fundamentally different cognitive phenomena, not one "truthfulness" trait
- Divergence patterns could be more informative than correlation strength
- Factor analysis on benchmark scores could reveal latent truthfulness dimensions
- Cross-domain insight: cognitive psychology's multi-factor models could apply to LLM evaluation

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises an intriguing possibility, but let me apply some methodological rigor here. Before we get excited about "multiple truthfulness axes," we need to establish what would actually constitute evidence for or against this claim.

The evidence suggests we need to be very careful about what "correlation" means in this context. Ailem et al. (2024) showed that non-random correlations exist *within* benchmark test prompts — models that succeed on certain prompts tend to succeed on related ones. This confounds any naive correlation analysis across benchmarks.

What would disprove a multi-factor hypothesis? If we find that TruthfulQA, HaluEval, and FactScore scores all load onto a single principal component explaining >80% of variance across a diverse model population, that would suggest a general truthfulness factor. Conversely, if we find 3+ orthogonal components each primarily associated with one benchmark type, that supports Dr. Nova's multi-axis theory.

Here's my concern: benchmark scores are aggregates. TruthfulQA MC1 vs MC2 already show different patterns. HaluEval varies by task (QA vs dialogue vs summarization). FactScore depends on retrieval quality. We need sub-score analysis, not just headline numbers.

**Specific, measurable prediction:** On a model population of N≥20 diverse architectures, if truthfulness is multi-dimensional, inter-benchmark correlations (TruthfulQA-MC1 vs HaluEval-QA vs FactScore) should be r < 0.5, while intra-benchmark correlations (TruthfulQA-MC1 vs TruthfulQA-MC2) should be r > 0.7.

**Key Points:**
- Need to distinguish intra-benchmark vs inter-benchmark correlation patterns
- Aggregate scores obscure sub-task heterogeneity — need fine-grained analysis
- Clear falsification criterion: if inter-benchmark r > 0.7, single-factor model wins
- Confound: Ailem et al.'s within-benchmark prompt correlations must be controlled

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: why does this matter for the field? Both Dr. Nova and Prof. Vera are circling something important, but let me connect this to broader research impact.

Currently, the ML community treats benchmark scores as interchangeable proxies for "trustworthiness." Model cards report TruthfulQA *or* FactScore *or* hallucination metrics, implying they measure similar qualities. If Dr. Nova is right that these are orthogonal dimensions, this fundamentally changes how we should evaluate and select models.

This matters because: deployment decisions are made on incomplete information. A model scoring 85% on TruthfulQA might still hallucinate catastrophically in long-form generation (FactScore domain). A model with excellent FactScore might fail on popular misconceptions (TruthfulQA domain). Understanding the correlation structure tells practitioners *which benchmarks to prioritize* for their specific use case.

What makes this genuinely new vs incremental? Prior work (BenchBench, Ailem et al.) established that benchmarks *can* disagree but didn't map the disagreement structure for truthfulness specifically. "The Moving Target" showed score drift within benchmarks but not cross-benchmark patterns. We'd be the first to provide an empirical correlation matrix with factor structure for truthfulness benchmarks.

The research direction this opens: if we find multiple orthogonal truthfulness dimensions, future work can ask "which training interventions improve which dimensions?" — a far more targeted approach than optimizing a single aggregate score.

**Key Points:**
- High practical impact: deployment decisions currently assume benchmark interchangeability
- Novel contribution: first empirical correlation matrix with factor structure for truthfulness benchmarks
- Opens new research direction: dimension-specific training interventions
- Addresses ICLR Workshop scope directly: "Metrics, benchmarks, and evaluation of trustworthy LLMs"

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. I've heard exciting ideas about multi-factor models and factor analysis, but what evidence supports that this is technically achievable with existing infrastructure?

The lm-evaluation-harness is our key enabler. I've verified: it supports TruthfulQA (MC1, MC2, generation), MMLU, HellaSwag, and WinoGrande out of the box. HaluEval and FactScore require custom integration but have published evaluation code. Running all benchmarks on N=20+ models is computationally tractable — a few GPU-days, not months.

Here's what worries me about the factor analysis approach: benchmark scores aren't normalized on the same scale. TruthfulQA MC1 is accuracy (0-1), FactScore is precision (0-1 but differently calibrated), HaluEval is detection accuracy. Before any correlation analysis, we need score standardization. Z-scores within each benchmark? Percentile ranks across models? The choice affects results.

Is the measurement approach theoretically valid? Yes, with caveats. Pearson correlation assumes linear relationships; Spearman is safer for ordinal relationships between rankings. Factor analysis assumes continuous, normally-distributed data — benchmark scores may violate this. We might need to use Item Response Theory (IRT) models instead, treating each benchmark question as an item.

**Technical feasibility assessment:**
- Model population: Use Open LLM Leaderboard models (50+ already evaluated on TruthfulQA, MMLU)
- Additional evaluation: Run HaluEval, FactScore on same models (~2-3 GPU-days)
- Analysis: Standard correlation matrix + PCA/factor analysis, with IRT as robustness check
- Fundamental barrier: None. This is achievable within weeks, not months.

**Key Points:**
- lm-evaluation-harness provides unified evaluation for most benchmarks
- Score normalization is critical — must address before correlation analysis
- Factor analysis assumptions may not hold; IRT models as alternative
- No fundamental barriers: computationally tractable, methodologically sound

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can strengthen this emerging hypothesis substantially! I see convergence forming around a testable core claim. Let me synthesize and refine.

Prof. Vera demanded falsifiable predictions — we can deliver. Prof. Pax confirmed technical feasibility. Dr. Sage identified the impact. Now let me propose the refined hypothesis:

**Core Claim:** Existing truthfulness benchmarks (TruthfulQA, HaluEval, FactScore) measure partially independent dimensions of LLM reliability, evidenced by moderate-to-low inter-benchmark correlations (r < 0.6) despite high intra-benchmark consistency (r > 0.7), with distinct correlation patterns to downstream task performance (MMLU, HellaSwag).

**Mechanism:** Different benchmarks target different failure modes — misconception resistance (TruthfulQA), generation coherence (HaluEval), and factual precision (FactScore) — which correspond to different model capabilities (knowledge retrieval, generation control, fact verification).

**Testable Predictions:**
1. **P1 (Primary):** Inter-benchmark correlations (TruthfulQA-MC1 vs HaluEval vs FactScore) will be r < 0.6 across N≥30 models
2. **P2:** Intra-benchmark correlations (TruthfulQA-MC1 vs MC2, HaluEval-QA vs HaluEval-Summarization) will be r > 0.7
3. **P3:** Factor analysis will reveal 2-3 orthogonal components, not a single "truthfulness" factor

What evidence supports this claim? Ailem et al. showed benchmark heterogeneity exists. BenchBench showed benchmarks can disagree. "Benchmarks Are Not Monolithic" found sample-level heterogeneity. The pattern suggests multi-dimensionality, though no one has quantified it for truthfulness specifically.

**Key Points:**
- Refined hypothesis with Under-If-Then-Because structure ready
- Three specific, falsifiable predictions with numerical thresholds
- Mechanism explains WHY different benchmarks might diverge
- Evidence base from Phase 1 supports multi-dimensionality hypothesis

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down. Dr. Ally has synthesized nicely, but I need to stress-test before we declare convergence.

**Challenge 1: Model population confound.** If we only evaluate models from similar architectures (all decoder-only transformers), we might find spurious correlations from architecture rather than truthfulness properties. What would convince me: include instruction-tuned vs base, different scales (7B to 70B), different training approaches (RLHF vs DPO vs SFT).

**Challenge 2: The r < 0.6 threshold is arbitrary.** Why 0.6 and not 0.5 or 0.7? What's the theoretical basis? Show me evidence for where "moderate correlation" ends and "high correlation" begins. Otherwise, you're setting yourself up to confirm whatever you find.

**Challenge 3: FactScore is not directly comparable.** FactScore requires long-form generation + retrieval verification. TruthfulQA uses multiple choice. HaluEval uses binary classification. You're comparing apples, oranges, and bananas. How do you account for format-induced variance?

**What would convince me:**
- Pre-register correlation thresholds based on prior benchmark correlation studies (what's typical r between unrelated benchmarks?)
- Include format-controlled analysis: compare generation-based metrics only, then MC-based only
- Demonstrate robustness across model families, not just one architecture type

**Remaining concern:** Even if you find low inter-benchmark correlations, that might just mean these benchmarks are noisy measurements, not that they measure different constructs. You need convergent validity evidence too.

**Key Points:**
- Model population must be diverse (architecture, scale, training) to avoid spurious correlations
- Threshold of r < 0.6 needs theoretical justification, not arbitrary selection
- Format differences (MC vs generation vs binary) confound cross-benchmark comparison
- Low correlation could indicate noise, not multi-dimensionality — need convergent validity

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's challenges are exactly what makes this research exciting! Let me address them with creative solutions.

**On model diversity:** We can turn this from a confound into a research question! What if we find that architecture type predicts *which* truthfulness dimension a model excels at? Instruction-tuned models might dominate TruthfulQA (explicit knowledge) while base models might show different FactScore patterns. The heterogeneity becomes a feature, not a bug.

**On threshold selection:** Here's a paradigm shift — instead of pre-specifying r < 0.6, we use *relative* thresholds. Compare inter-benchmark correlations to a reference: correlations between known-unrelated benchmarks (e.g., MMLU-Physics vs HaluEval) should be ~0. If TruthfulQA-HaluEval correlations are significantly higher than unrelated-benchmark correlations but significantly lower than intra-benchmark correlations, we've established a meaningful middle ground.

**On format confound:** Clever solution — use generation-based versions of all benchmarks where available. TruthfulQA has a generation mode. HaluEval is generation-based. FactScore is generation-based. For the MC-only analysis, TruthfulQA-MC vs MMLU (also MC) gives format-controlled comparison.

**On convergent validity:** If dimensions are real, they should predict different failure patterns. P4 (new prediction): Models scoring low on TruthfulQA but high on FactScore should show *different* error types than vice versa. Qualitative error analysis confirms construct validity.

**Key Points:**
- Architecture heterogeneity becomes a research question, not a confound
- Relative thresholds (vs unrelated benchmarks) solve arbitrary cutoff problem
- Format-controlled analyses possible: generation-only and MC-only subsets
- Error type analysis provides convergent validity for multi-dimensionality claim

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's creative solutions address Prof. Rex's concerns constructively. Let me formalize the experimental design.

**Revised Experimental Protocol:**

1. **Model Population (N≥30):**
   - 10 base models (varied architectures: Llama, Mistral, Falcon, Phi, Qwen)
   - 10 instruction-tuned variants
   - 10 scaled variants (7B, 13B, 70B where available)
   - Requirement: Each model runs ALL benchmarks to enable correlation analysis

2. **Benchmarks & Modes:**
   - TruthfulQA: MC1, MC2, Generation
   - HaluEval: QA subset, Summarization subset (generation-based)
   - FactScore: Standard (generation + retrieval)
   - Controls: MMLU (knowledge), HellaSwag (reasoning)

3. **Analysis Plan:**
   - Primary: Spearman correlation matrix (robust to non-normality)
   - Secondary: PCA/Factor analysis with oblique rotation (allows correlated factors)
   - Robustness: IRT models treating items as binary outcomes
   - Validity: Error type clustering by low-high benchmark combinations

4. **Pre-registered Thresholds:**
   - "Unrelated benchmark baseline": r between MMLU-Physics and HaluEval-Summarization (expected ~0.2)
   - "Low correlation": r ≤ baseline + 0.2
   - "High correlation": r ≥ 0.7 (intra-benchmark typical)
   - "Moderate": between low and high

**Falsification criteria remain:** If all inter-benchmark rs > 0.7, single-factor model wins. If factor analysis shows one component explains >80% variance, multi-dimensionality rejected.

**Key Points:**
- Pre-registered threshold based on unrelated-benchmark baseline
- 30+ model population with architecture/scale/training diversity
- Both generation-based and MC-based analysis tracks
- Factor analysis with oblique rotation allows partial correlation between dimensions

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Vera's protocol is thorough. Let me verify technical feasibility of the full design.

**Computational Requirements:**
- TruthfulQA (all modes): ~2 hours per model on A100
- HaluEval (2 subsets): ~4 hours per model
- FactScore: ~6 hours per model (includes generation + retrieval verification)
- MMLU, HellaSwag: ~1 hour per model
- **Total per model: ~13 hours × 30 models = 390 GPU-hours (~16 GPU-days)**

This is tractable for any academic lab with cluster access. Commercial API evaluation would cost ~$300-500 total.

**Data availability check:**
- TruthfulQA: Public, 817 questions ✓
- HaluEval: Public, 35K samples ✓
- FactScore: Requires generation + Wikipedia retrieval ✓
- MMLU: Public ✓
- HellaSwag: Public ✓
- Open LLM Leaderboard: Pre-computed scores for many models (partial shortcut) ✓

**Implementation path:**
1. Use lm-evaluation-harness for TruthfulQA, MMLU, HellaSwag
2. Adapt HaluEval evaluation scripts (published)
3. Use FactScore PyPI package
4. Aggregate scores → correlation/factor analysis in Python (scipy, factor_analyzer)

**No fundamental barriers.** This is a weeks-to-month project, not a multi-year effort.

**Key Points:**
- ~400 GPU-hours total — tractable for academic lab
- All datasets publicly available
- Partial shortcut: leverage Open LLM Leaderboard pre-computed scores
- Standard Python tools sufficient for analysis (scipy, factor_analyzer)

---

### Exchange 10

🎯 **Dr. Sage** (Research Impact Evaluator):

The experimental design has converged to something rigorous and feasible. Let me assess the final contribution.

**What makes this genuinely new:**
1. First systematic correlation study specifically for truthfulness benchmarks
2. First factor structure analysis revealing dimensionality of "truthfulness" as measured
3. First empirical evidence for/against benchmark interchangeability assumption

**How this advances the field:**
- Practitioners get evidence-based guidance on which benchmarks to use when
- Researchers understand what each benchmark actually measures
- Future benchmark design can target underserved dimensions
- Training researchers can target specific truthfulness dimensions

**Positioning vs state-of-the-art:**
- BenchBench: Meta-benchmark methodology → We apply to truthfulness specifically
- Ailem et al.: Prompt-level correlations → We do model-level cross-benchmark correlations
- "Moving Target": Score drift → We do snapshot correlation structure
- "Not Monolithic": Sample heterogeneity → We do benchmark heterogeneity

**Publication-ready impact:**
- Fits ICLR Workshop on Building Trust directly
- Addresses "Metrics, benchmarks, and evaluation" scope item explicitly
- Provides actionable recommendations for model deployment decisions

**Key Points:**
- Three-fold novel contribution: correlation study, factor structure, interchangeability evidence
- Directly advances benchmark understanding for the field
- Practitioner impact: evidence-based benchmark selection guidance
- Clear venue fit: ICLR Workshop on Building Trust in Language Models

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

We have convergence. Let me synthesize the final refined hypothesis addressing all concerns raised.

**Final Hypothesis Statement:**

**Under** evaluation of N≥30 diverse LLMs (varied architecture, scale, training) on truthfulness benchmarks, **if** TruthfulQA, HaluEval, and FactScore measure partially independent reliability dimensions, **then** inter-benchmark correlations will be moderate (r between unrelated-benchmark baseline and 0.7) while intra-benchmark correlations remain high (r > 0.7), and factor analysis will reveal 2-3 components rather than a single factor, **because** these benchmarks target distinct failure modes: misconception resistance, generation coherence, and factual precision respectively.

**Null Hypothesis (H0):** There is no significant difference in correlation structure — all truthfulness benchmarks measure the same underlying construct, with inter-benchmark r > 0.7 and single-factor solution explaining >80% variance.

**Validated Predictions:**
- P1: Inter-benchmark r in moderate range (> baseline, < 0.7)
- P2: Intra-benchmark r > 0.7
- P3: 2-3 factor solution, not single factor
- P4: Error type clustering by benchmark performance pattern

**All Concerns Addressed:**
- Prof. Rex's model diversity → 30+ models across architectures/scales/training
- Prof. Rex's threshold arbitrariness → Baseline-relative thresholds
- Prof. Rex's format confound → Generation-only and MC-only analysis tracks
- Prof. Rex's convergent validity → Error type clustering analysis

**Key Points:**
- Complete Under-If-Then-Because hypothesis with mechanism
- Pre-registered thresholds based on unrelated-benchmark baseline
- Four testable predictions with clear success criteria
- All major objections addressed with specific solutions

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

I'm satisfied. The refinements address my concerns.

**What convinced me:**
1. Baseline-relative thresholds instead of arbitrary cutoffs
2. Model diversity requirements built into design
3. Format-controlled analysis tracks
4. Error clustering for convergent validity

**Remaining minor concern:** FactScore depends on retrieval quality, which varies. Recommend using same retrieval corpus for all models (e.g., Wikipedia snapshot date fixed). Not a blocker, just implementation detail.

**Final assessment:** This hypothesis is testable, falsifiable, and addresses a genuine gap. The experimental design is rigorous enough for peer review. If results confirm multi-dimensionality, it's a significant contribution. If results show single-factor, that's also valuable — confirms benchmark interchangeability assumption.

Either outcome advances the field.

**Key Points:**
- Concerns addressed — hypothesis is rigorous
- Minor implementation note: fix FactScore retrieval corpus
- Win-win: either outcome is publishable and useful
- Ready for Phase 2B verification protocol design

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The multi-dimensional truthfulness hypothesis represents a genuine paradigm shift from treating benchmarks as interchangeable. The creative reframing — asking what latent structure explains divergence rather than just measuring correlation — opens new research directions for dimension-specific interventions.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis has clear, pre-registered falsification criteria: if inter-benchmark r > 0.7 and single-factor solution explains >80% variance, multi-dimensionality is rejected. The experimental protocol specifies exact model populations, benchmarks, and analysis methods required for replication.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** This is the first empirical study of truthfulness benchmark correlation structure. The practical impact is immediate — deployment decisions currently assume benchmark interchangeability without evidence. Either confirming or refuting this assumption advances the field.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** ~400 GPU-hours total across 30 models. All datasets public. Infrastructure exists (lm-evaluation-harness, FactScore package). Standard analysis tools sufficient. No fundamental barriers — this is a months-scale project achievable by any ML lab.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The research discussion has converged on testing whether existing truthfulness benchmarks (TruthfulQA, HaluEval, FactScore) measure partially independent reliability dimensions. The core claim is that these benchmarks target distinct failure modes — misconception resistance, generation coherence, and factual precision — which should manifest as moderate inter-benchmark correlations (above unrelated-benchmark baseline but below 0.7) with high intra-benchmark consistency (r > 0.7).

The proposed mechanism explains why different benchmarks might diverge: they tap different model capabilities (knowledge retrieval vs generation control vs fact verification). Factor analysis on scores from N≥30 diverse models should reveal 2-3 components rather than a single "truthfulness" factor.

The experimental approach uses lm-evaluation-harness to run all benchmarks on the same model population, ensuring direct comparability. Format-controlled analyses (generation-only, MC-only) address format confounds. Error type clustering provides convergent validity.

Either outcome is valuable: confirming multi-dimensionality guides practitioners to select benchmarks matching their use case; confirming single-factor validates treating benchmarks as interchangeable. Both advance benchmark understanding for the field.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- FactScore retrieval corpus should be fixed (same Wikipedia snapshot) across all models
- Consider adding confidence intervals on correlation estimates given finite model sample
- **Mitigation Strategy:** Pre-register retrieval corpus date; bootstrap confidence intervals for correlations

---

## Emerged Hypothesis Summary

### Core Statement
Under evaluation of N≥30 diverse LLMs on truthfulness benchmarks, if TruthfulQA, HaluEval, and FactScore measure partially independent reliability dimensions, then inter-benchmark correlations will be moderate (r between baseline and 0.7) while intra-benchmark correlations remain high (r > 0.7), and factor analysis will reveal 2-3 components rather than a single factor, because these benchmarks target distinct failure modes.

### Causal Mechanism
1. TruthfulQA tests resistance to popular misconceptions → requires knowledge retrieval + misconception detection
2. HaluEval tests generation coherence → requires generation control + consistency maintenance
3. FactScore tests atomic factual precision → requires fact verification + retrieval accuracy
4. Different benchmarks tap different capabilities → partially independent performance

### Variables
**Independent Variable:** Benchmark type (TruthfulQA, HaluEval, FactScore)
**Dependent Variable:** Model performance score on each benchmark
**Control Variables:** Model architecture, scale, training approach

### Key Assumptions
- A1: Benchmark scores are reliable measurements (low noise)
- A2: Model population is representative of LLM landscape
- A3: Factor analysis assumptions approximately hold for benchmark scores
- A4: Format differences don't dominate over construct differences

### Null Hypothesis
All truthfulness benchmarks measure the same underlying construct, with inter-benchmark r > 0.7 and single-factor solution explaining >80% variance.

### Predictions
- P1 (Primary): Inter-benchmark correlations in moderate range (> baseline, < 0.7)
- P2: Intra-benchmark correlations > 0.7
- P3: Factor analysis reveals 2-3 components, not single factor
- P4: Error type clustering distinguishes benchmark performance patterns

### Novelty
First empirical correlation and factor structure study for truthfulness benchmarks specifically. Prior work (BenchBench, Ailem et al.) established methodology but not truthfulness-specific application.

### Scope & Boundaries
Applies to: Current generation LLMs (decoder-only transformers, 7B-70B scale), established truthfulness benchmarks
Does not apply to: Multimodal models, non-English benchmarks, proprietary closed-source models without API access

### Experimental Setup
- **Dataset:** TruthfulQA (817 questions), HaluEval (35K samples), FactScore (generation + retrieval), MMLU, HellaSwag
- **Model Population:** 30+ diverse models from Open LLM Leaderboard
- **Analysis:** Spearman correlation matrix, PCA with oblique rotation, IRT robustness check

### Related Work & Baselines
- BenchBench (Perlitz et al., 2024): Meta-benchmark methodology
- Ailem et al. (2024): Prompt-level correlation patterns
- "The Moving Target" (Fan et al., 2026): Score drift analysis
- "Benchmarks Are Not Monolithic" (Siedler & Sassoon, 2026): Sample-level heterogeneity

### Phase 2B Readiness Seeds
- SH-1 (Existence): Moderate inter-benchmark correlations exist
- SH-2 (Mechanism): Different failure modes underlie different benchmarks
- SH-3 (Comparison): Multi-factor solution vs single-factor (deferred to Phase 5 baseline)

### Established Facts
- Benchmark agreement is not guaranteed (BenchBench, 2024)
- Non-random correlations exist within benchmarks (Ailem et al., 2024)
- TruthfulQA, HaluEval, FactScore use different evaluation paradigms
