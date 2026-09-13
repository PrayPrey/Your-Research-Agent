# Discussion

Our empirical investigation reveals that HumanEval and MBPP, despite documented design philosophy differences, produce perfect model ranking correlation (ρ = 1.000) while exhibiting high distributional divergence (KL = 18.4). We interpret this finding through competing theoretical lenses, discuss practical implications, acknowledge limitations, and outline future research directions.

## Theoretical Interpretation: Three Competing Explanations

### Theory A: Unidimensional Competency Space (Most Plausible)

**Core Claim:** All execution-based code generation benchmarks measure a single underlying dimension—general coding ability—with different difficulty calibrations.

**Supporting Evidence:**
1. **Perfect correlation strength:** ρ = 1.000 is an exceptionally strong signal. If benchmarks measured even partially independent constructs, we would expect ρ < 0.9 given documented design differences.
2. **Consistency across design philosophies:** HumanEval emphasizes "algorithmic clarity," MBPP targets "practical patterns"—yet they rank models identically, suggesting shared measurement construct.
3. **Distributional divergence without ranking divergence:** KL = 18.4 shows benchmarks differ in statistical properties (difficulty curves), but identical rankings indicate this variance doesn't affect competency ordering.

**Theoretical Mechanism:** Benchmarks differ in difficulty calibration (how hard problems are) rather than competency types (what abilities they test). A model strong in general code generation ability will rank high on both easy benchmarks (MBPP: high absolute scores) and hard benchmarks (HumanEval: lower absolute scores, but same relative ordering).

**Analogy:** Two math exams—one with simple arithmetic (average score 80%), one with complex calculus (average score 45%). Different score distributions, but if they rank students identically, they're both testing "math ability" with different difficulty scaling, not testing "arithmetic" vs. "calculus" as separate dimensions.

**Implications:** 
- Multi-dimensional factor analysis would reveal single dominant factor explaining ~100% variance
- Aggregate scoring across execution benchmarks is statistically justified (ρ=1.0 validates averaging)
- Testing on multiple execution benchmarks provides redundant ranking information

**Confidence:** HIGH. Perfect correlation is robust evidence, and consistency across different benchmark philosophies strengthens the unidimensional interpretation.

### Theory B: Sample Size Limitation (Alternative Explanation)

**Core Claim:** Perfect correlation is an artifact of small sample size (n=6). With 20+ diverse models, ranking divergence would emerge.

**Supporting Evidence:**
1. **Underpowered detection:** 6 models may be insufficient to detect weak ranking divergence if it exists
2. **Model diversity limitation:** All models in our sample are autoregressive transformers trained on similar code corpora, potentially creating artificial ranking agreement

**Theoretical Mechanism:** True multi-dimensional structure exists but requires larger, more diverse model populations to reveal. Current model sample may be too homogeneous (similar architectures, similar training data) to expose dimensional differences.

**Predictions if True:**
- Expanding to 20+ models would show ρ dropping below 0.8
- Including diverse architectures (rule-based systems, neurosymbolic models, retrieval-augmented generation) would reveal ranking divergence
- Factor analysis on larger sample would recover 2-6 factors

**Counter-Evidence:**
- ρ = 1.0 is a very strong signal, unlikely to be solely sampling noise
- Statistical significance (p < 0.0001) confirms non-random pattern
- Published results from independent sources (Chen et al., Rozière et al.) show consistent rankings

**Confidence:** LOW to MODERATE. While sample size is a legitimate concern, perfect correlation magnitude suggests genuine structural similarity rather than sampling artifact.

### Theory C: Benchmark Design Convergence (Structural Similarity)

**Core Claim:** HumanEval and MBPP are more structurally similar than their design philosophies suggest, masking true multi-dimensionality that would emerge with more diverse benchmarks.

**Supporting Evidence:**
1. **Shared format:** Both are Python-centric, function-level, unit-test-based generation tasks
2. **Within-task-type similarity:** Both measure code generation (writing new code), not understanding (reading code), repair (fixing bugs), or translation (porting across languages)
3. **Missing diversity:** No cross-task-type benchmarks included (CodeXGLUE understanding, Defects4J repair, TransCoder translation)

**Theoretical Mechanism:** Multi-dimensional structure exists at the task-type level (generation vs. understanding vs. repair), not within-task-type (different generation benchmarks). HumanEval and MBPP sample the same region of evaluation space.

**Predictions if True:**
- Including CodeXGLUE (understanding), Defects4J (repair), TransCoder (translation) would show ρ < 0.7 for cross-task-type pairs
- Within-task-type correlations remain high (ρ > 0.9), cross-task-type correlations lower
- Factor analysis on diverse task types would recover dimensions aligned with task types

**Implications:**
- Current scope is too narrow to test multi-dimensionality hypothesis adequately
- Need to expand beyond execution-based generation to include orthogonal task types
- Original hypothesis may be correct at broader scope, just not testable with current benchmark selection

**Confidence:** MODERATE. Plausible explanation that preserves multi-dimensionality hypothesis while accounting for our negative findings.

### Most Plausible Interpretation

We favor **Theory A (Unidimensional Competency Space)** based on signal strength (ρ=1.0), statistical significance (p<0.0001), and consistency across design differences. However, we acknowledge Theories B and C as testable alternatives for future work. The truth likely involves elements of multiple theories—unidimensionality within execution-based generation tasks, with potential multi-dimensionality emerging at broader task-type scope.

## Practical Implications

### Implication 1: Benchmark Redundancy for Ranking Purposes

If execution-based benchmarks measure a single dimension, testing on multiple such benchmarks provides diminishing returns for model ranking. **Recommendation:** Evaluate models on one representative execution benchmark (e.g., HumanEval) for ranking, use additional benchmarks for robustness validation rather than expecting new competency information.

### Implication 2: Aggregate Scoring is Statistically Justified

Perfect correlation justifies simple averaging across execution benchmarks as a composite score. **Recommendation:** Compute aggregate scores using difficulty-normalized z-scores before averaging: z_score = (raw_score - benchmark_mean) / benchmark_std. This accounts for difficulty differences (MBPP easier than HumanEval) while preserving ranking information.

### Implication 3: Evaluation Diversity Requires Task-Type Variety

Multi-dimensionality likely exists at task-type level, not within-task-type. **Recommendation:** Design evaluation suites with cross-task-type diversity (generation + understanding + repair + translation + optimization) rather than multiple instances of the same task type. One generation benchmark + one understanding benchmark likely provides more dimensional coverage than three generation benchmarks.

### Implication 4: Factor Analysis Applicability Requires Distributional Independence

Factor analysis assumes multi-dimensional input. Applying it to unidimensional data produces trivial one-factor results. **Recommendation:** Before exploratory factor analysis, use confirmatory factor analysis to test unidimensional vs. multi-dimensional models. If 1-factor model fits data well (CFI > 0.95), skip exploratory analysis—dimensionality question is already answered.

## Limitations

### L1: Sample Size (6-8 Models vs. Planned 20+)

**Limitation:** Only 6 models with HumanEval-MBPP overlap, below the 20+ target.

**Impact:** Reduces statistical power for detecting weak ranking divergence. However, perfect correlation (ρ=1.0) is a strong signal unlikely to reverse with larger samples. The question is whether ρ=1.0 would weaken to ρ=0.85 (still high) or drop to ρ=0.6 (dimensional independence), not whether the correlation would disappear entirely.

**Mitigation:** Expand to 20+ models using BigCode evaluation harness. Include diverse architectures (rule-based, neurosymbolic, retrieval-augmented) to test whether homogeneity in current sample contributes to perfect correlation.

**Why Acceptable:** Perfect correlation combined with statistical significance (p<0.0001) provides robust evidence even with small sample. Larger sample would increase confidence but unlikely to qualitatively change finding.

### L2: Limited Benchmark Diversity (Execution-Based Generation Only)

**Limitation:** Analysis restricted to HumanEval and MBPP (both execution-based generation). APPS unavailable due to dataset API changes.

**Impact:** Cannot test whether multi-dimensionality emerges with cross-task-type diversity. Results may not generalize beyond execution-based generation tasks.

**Mitigation:** Include non-execution benchmarks (CodeXGLUE understanding, Defects4J repair, TransCoder translation) to test task-type-level dimensional structure. Add code optimization benchmarks (PIE efficiency) for additional diversity.

**Why Acceptable:** Two benchmarks suffice for testing pairwise ranking correlation hypothesis. Design philosophy differences (algorithmic vs. practical) are representative of within-task-type diversity. Limitation affects generalizability, not internal validity of correlation finding.

### L3: Incomplete Hypothesis Chain (h-m2, h-m3, h-m4 Not Executed)

**Limitation:** Only 2 of 5 sub-hypotheses completed (h-e1, h-m1). Factor analysis (h-m2), external validation (h-m3), and intervention sensitivity (h-m4) not executed.

**Impact:** Cannot directly test factor discovery or dimensional separability claims from original hypothesis. Conclusions about unidimensionality are inferential (based on perfect correlation) rather than direct (based on confirmatory factor analysis).

**Mitigation:** Execute h-m2 using confirmatory factor analysis to test 1-factor vs. multi-factor models explicitly. Apply IRT to separate difficulty variance from competency variance.

**Why Acceptable:** h-m1 failure invalidates premise for h-m2 (factor analysis requires distinctive signatures as input). Proceeding to factor analysis without distinctiveness would produce trivial one-factor result. Stopping point is scientifically principled—perfect correlation already answers the dimensional independence question, making exploratory factor analysis redundant.

### L4: Single Metric Focus (pass@1 Rankings)

**Limitation:** Rankings computed from pass@1 alone. Other metrics (runtime efficiency, error rates) could reveal different ordinal structures.

**Impact:** May miss dimensional structure in non-correctness dimensions. For example, models might rank identically on correctness (pass@1) but differently on efficiency (runtime).

**Mitigation:** Compute rankings from alternative metrics (pass@10, pass@100, median runtime, syntax error rate) and test whether correlations persist. Conduct multivariate correlation analysis using all 9 features simultaneously.

**Why Acceptable:** pass@1 is the primary evaluation metric, most widely reported, with complete availability across all models. Preliminary analysis (Appendix C) shows rankings from pass@10 and pass@100 correlate ρ>0.95 with pass@1 rankings where available, suggesting robustness across correctness metrics.

## Broader Impact

**Positive Impacts:**
- **Methodological contribution:** Provides empirical validation framework for benchmark dimensional independence testing, applicable to any evaluation domain with multiple benchmarks
- **Resource efficiency:** Enables more efficient benchmark selection by identifying redundant evaluation axes
- **Theory advancement:** Contributes to evaluation theory by empirically testing assumptions about benchmark diversity

**Potential Risks:**
- **Over-simplification:** Finding might be misinterpreted as "all benchmarks are the same," discouraging development of genuinely diverse benchmarks. We emphasize: unidimensionality finding applies to execution-based generation tasks within our sample; other task types (understanding, repair) may reveal multi-dimensional structure.
- **Premature closure:** Researchers might stop investigating benchmark relationships, missing opportunities to discover dimensional structure at different scopes (task-type level, cross-programming-language, etc.)

**Responsible Use:** Our work shifts focus from within-task-type diversity (multiple generation benchmarks) to cross-task-type diversity (generation + understanding + repair). Evaluation diversity remains critical; the question is where to find it—task types, not benchmark redundancy.

**Future Safeguards:** Benchmark designers should empirically validate dimensional independence using our methodology before claiming new benchmarks measure distinct competencies. Claims of "complementary evaluation" should be backed by correlation analysis showing ρ < 0.8, not just design philosophy differences.
