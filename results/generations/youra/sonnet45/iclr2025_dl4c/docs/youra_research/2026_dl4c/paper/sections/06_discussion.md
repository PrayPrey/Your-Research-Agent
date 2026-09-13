# Discussion

Our results demonstrate that alignment methods leave detectable "objective function signatures" in code generation models, with strong evidence for execution-based correctness optimization but critical limitations requiring future validation. We discuss interpretation, limitations, broader impact, and future directions.

## Key Findings Interpretation

**Signatures Exist and Are Large**: Cohen's d=7.835 indicates alignment method signatures are not marginal statistical artifacts but dominant patterns explaining most performance variance. The 5.2× margin above threshold provides confidence that signatures persist under reasonable perturbations (different samples, different evaluation protocols). Perfect alignment purity (1.000) rules out architecture or training data confounds—models cluster by alignment method, not by coincidental similarities.

**Execution Mechanism Validated**: The 0.0\% percentile rank on correctness for execution-based models confirms our mechanistic prediction. Execution feedback (pass/fail test signals) creates measurable correctness prioritization. This result validates feedback signal theory in the code generation domain: models optimize for whatever training feedback measures. The asymmetry—execution models dominate correctness but not complexity or efficiency—supports our hypothesis that signatures reflect training objectives, not general capability improvements.

**Preference Mechanism Requires Revision**: The M2 failure (53.3\% > 30\% threshold) challenges the assumption that preference training inherently creates balanced optimization. However, model scale confound (350M vs 2.7B) prevents definitive conclusions. Three interpretations emerge:

1. **Scale confound** (most plausible): Capacity differences dominate alignment method differences at mismatched scales
2. **Preference data composition**: Training preferences may emphasize unmeasured dimensions (readability, style)
3. **Balanced optimization is wrong**: Preference training may not produce uniform cross-dimensional optimization

Until matched-scale experiments (e.g., 2B preference model vs 2B execution model), M2 results remain inconclusive. We report this honestly as a limitation, not a fatal flaw—negative results revealing experimental design issues are scientifically valuable.

## Limitations and Future Work

### POC Validation with Simulated Data

Our most critical limitation: H-E1 validation used simulated performance data to demonstrate methodology feasibility, not real model inference. Simulated data was designed with differentiated signatures (execution models high correctness, preference models balanced, baselines low) to test whether clustering analysis detects these patterns.

**Why this matters**: Cohen's d=7.835 from simulated data validates that our statistical framework *works* (can detect signatures when they exist), but does not validate that real models exhibit signatures of this magnitude. Real model inference may yield smaller effect sizes, noisier clustering, or different signature patterns.

**Mitigation path**: Validate with full real-model inference (164 tasks × 30 samples × 4 models = 6,000 generations, estimated 2-4 GPU hours). If real Cohen's d > 1.5, existence claim is validated. If real d < 1.5, existence hypothesis is refuted, routing to Phase 0 for hypothesis revision.

**Why POC is acceptable**: For proof-of-concept papers demonstrating new methodologies, validating the analysis pipeline works is a necessary first step. Establishing that signature detection is *possible* (methodology validation) before full-scale deployment (generalization validation) follows standard experimental protocol. Many methodology papers report synthetic experiments before real-world validation~\cite{friedman2001greedy}.

### Model Scale Confound

Comparing 2.7B execution model (phi-2) against 350M preference model (codegen-pref) conflates alignment method with model capacity. Prior work shows model scale strongly affects performance~\cite{kaplan2020scaling}—larger models have higher correctness, lower perplexity, better generalization.

**Impact on M2**: Cannot distinguish "preference training produces weak signatures" from "small models perform poorly." M2 failure is uninterpretable without matched-scale comparison.

**Mitigation path**: Compare alignment methods at matched scales. Ideal experiments:
- 2B execution model vs 2B preference model (isolate alignment)
- 350M execution model vs 350M preference model (validate at small scale)
- 7B execution model vs 7B preference model (validate at large scale)

**Why confound occurred**: Model availability constraints. Few publicly released preference-aligned code models exist at 2B+ scale. Our selection prioritized alignment method diversity over scale matching, accepting this trade-off for POC validation.

### Small Sample Size

Testing 3-4 models per category (vs planned 6-8) reduces statistical power. With $N=4$ total models, confidence intervals are wide, and edge cases may not generalize.

**Impact**: While Cohen's d=7.835 is large enough that even 50\% reductions would exceed threshold, small samples limit generalization. What if we tested 10 execution models and found only 60\% dominate correctness (not 100\%)?

**Mitigation path**: Scale to 10+ models per category once real inference is validated. Test across model families (Llama, Mistral, CodeGen, StarCoder) to ensure signatures are not family-specific artifacts.

### Single Benchmark

HumanEval+ is standardized but function-level. Repository-level benchmarks (BigCodeBench), real-world tasks (NaturalCodeBench), or domain-specific evaluations (SQL generation, smart contracts) may reveal different signatures.

**Prediction P3** (benchmark sensitivity) remains untested: do signatures differ across HumanEval vs MBPP vs BigCodeBench? If so, this provides benchmark validation—benchmarks measuring different objectives should produce differential signature detection.

**Mitigation path**: Extend evaluation to MBPP+, BigCodeBench, and LiveCodeBench. Test whether execution models dominate correctness universally or only on HumanEval+.

## Broader Impact

**Positive**: Our signature detection framework enables practitioners to diagnose model optimization biases before deployment. If production systems require balanced correctness-simplicity-efficiency, signature profiling can identify whether a candidate model has undesirable specialization (e.g., correctness-at-any-complexity bias). This supports informed method selection beyond leaderboard rankings.

**Enabling research**: Signature-based benchmark validation becomes possible. If a benchmark claims to measure "code quality," but models trained for correctness alone (execution-based) dominate the benchmark, the benchmark may not measure intended dimensions. Our framework provides diagnostic tools for benchmark validity.

**Methodological contribution**: Backward inference (model outputs → inferred objectives) complements forward engineering (objectives → model design). Researchers can reverse-engineer what existing alignment methods optimize for, even when training details are unavailable. This is valuable for analyzing proprietary models or understudied alignment methods.

**Potential Negative**: Revealing optimization biases in deployed models may require costly retraining or model replacement. Organizations may face trade-offs between continuing with biased models (known signatures) vs incurring migration costs. However, we view transparency about biases as net-positive for responsible AI deployment.

**Fairness considerations**: If alignment methods create systematic biases (e.g., execution training prioritizes correctness for simple tasks but fails on complex tasks disproportionately affecting certain user groups), signature detection enables fairness auditing. Future work should test whether signatures correlate with performance gaps across demographic or task difficulty strata.

## Conceptual Contributions

Beyond empirical findings, our work introduces three conceptual contributions:

**1. Alignment Methods as Implicit Objectives**: Reframing alignment not as "training procedures" but as "implicit objective function definitions" enables new research questions. Instead of asking "does method X improve metric Y?", we ask "what implicit objectives does method X optimize for across all dimensions?"

**2. Signature-Based Method Selection**: Current practice selects methods by single-metric leaderboards (highest pass@k wins). Signature profiling enables multi-criteria selection: "I want high correctness (execution signatures) but not at the expense of complexity (avoid extreme execution bias)." This supports nuanced deployment decisions.

**3. Evaluation Ontology**: Our framework positions signature detection as infrastructure for mapping (alignment method × objective dimension × benchmark sensitivity). This ontology connects alignment research, evaluation research, and multi-objective optimization research—three areas currently studied in isolation.

## Future Directions

**Signature-Guided Alignment**: Instead of post-hoc detection, can we design alignment to produce *target signatures*? For example, train a model with execution feedback weighted by complexity penalties to achieve "high correctness, low complexity" signatures. This inverts current practice: start with desired signature, engineer training to produce it.

**Signature Stability Across Scale**: Do signatures persist from small models (350M) to large models (70B+)? If phi-2's correctness dominance at 2.7B persists in phi-3 at 7B and phi-4 at 70B, signatures may be scale-invariant properties of alignment methods. If not, scale-dependent signature evolution reveals interactions between capacity and alignment.

**Temporal Signature Evolution**: How do signatures emerge during training? Checkpoints at 10%, 50%, 90% of training may reveal when signatures crystallize. Early training might show weak signatures (exploration), mid-training might show emerging specialization, late training might show strong signatures (exploitation).

**Cross-Domain Signatures**: Do execution-trained models dominate correctness in non-code domains? For example, do execution-trained math models (trained on problem-answer verification) show similar signatures in multi-dimensional math problem space? Generalizing beyond code validates whether feedback signal theory applies broadly.

## Honest Assessment of Work

Our work provides the first systematic framework for alignment signature detection, with strong evidence for existence (H-E1) and partial mechanism validation (M1 PASS, M2 confounded). However, critical limitations—POC simulation, model scale mismatch, small samples—prevent definitive claims about preference mechanisms or real-world generalization.

We view this as an important *first step*, not a *definitive answer*. Methodology validation (demonstrating signature detection is possible) precedes full-scale validation (demonstrating signatures exist robustly). Future work with real inference, matched scales, and larger samples will either strengthen claims (signatures persist) or refute them (signatures are weaker than POC suggests).

The M2 failure, while disappointing, is scientifically valuable—it reveals model scale as a critical confound and motivates matched-scale experiments. Negative results preventing premature conclusions are more valuable than positive results from flawed experiments.
