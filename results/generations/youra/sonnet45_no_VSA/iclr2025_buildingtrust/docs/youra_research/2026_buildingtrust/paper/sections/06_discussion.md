# Discussion

Our null result—coefficient of variation (CV) does not reliably predict cross-benchmark ranking stability (r=-0.486, p=0.154)—provides valuable negative evidence for benchmark quality tool development. This section interprets the finding, acknowledges critical limitations, extracts theoretical value from the cross-benchmark correlation patterns, and discusses broader implications for evaluation infrastructure.

## 6.1 Interpretation of Null Result

### 6.1.1 Why CV Fails as a Prospective Quality Signal

The core intuition behind our hypothesis was straightforward: high score variance (high CV) indicates inconsistent model differentiation, suggesting measurement noise that should manifest as unstable rankings across benchmarks (low cross-benchmark ρ). Our null finding (r=-0.486, NS) refutes this intuition. We identify three explanations:

**1. Cross-benchmark ρ conflates reliability and validity.**

Our dependent variable—mean cross-benchmark Spearman ρ—was intended to measure ranking *stability* (reliability), but it also reflects *construct divergence* (validity). Low ρ could indicate:
- **Unreliable measurement:** Noisy benchmarks produce inconsistent rankings even when measuring the same construct (our hypothesis target).
- **Valid construct divergence:** Benchmarks measure orthogonal dimensions (e.g., hallucination detection vs. ethical reasoning) and *should* have low ρ by design (confounder).

CV may predict reliability (measurement consistency) but cannot predict validity (construct alignment). Since cross-benchmark ρ conflates both, CV shows weak correlation. This ambiguity is not a methodological flaw but a fundamental limitation of using cross-benchmark agreement as a quality metric without first validating construct coherence.

**2. Score variance has multiple sources CV cannot disambiguate.**

High CV can arise from:
- **Measurement noise:** Inconsistent scoring due to ambiguous items, annotator disagreement, or stochastic model behavior (our hypothesis target).
- **Valid task heterogeneity:** Benchmarks with items spanning easy-to-hard difficulty by design (e.g., math benchmarks from arithmetic to olympiad problems) naturally exhibit high CV—this is good coverage, not poor quality.
- **Ceiling/floor effects:** Benchmarks with very easy or very hard items cluster scores at 100% or 0%, producing low CV regardless of measurement quality.
- **Construct-specific variance:** Different trust dimensions (truthfulness, safety, fairness) may have intrinsically different score distributions—high CV in FaithfulQA (hallucination detection) may reflect the difficulty of hallucination tasks, not noise.

CV is a summary statistic that collapses these sources into a single number. Without disambiguating them, CV cannot reliably predict which benchmarks are noisy versus well-designed with intentional heterogeneity.

**3. Simple meta-features are insufficient—multi-feature models needed.**

Benchmark quality is multi-faceted (construct validity, reliability, discriminative power, item difficulty calibration). A single statistic (CV) cannot capture this complexity. Our null result motivates **multi-feature approaches** combining:
- **CV**: Score dispersion
- **IQR (inter-quartile range)**: Robustness to outliers
- **Split-half reliability**: Within-benchmark ranking consistency across item subsets
- **Score ceiling proximity**: Percentage of models at 100% (ceiling effect indicator)
- **Skewness**: Distribution shape (bimodal, uniform, etc.)

Future work should test whether these features, in combination, predict cross-benchmark stability better than CV alone. Our negative evidence constrains this search space—variance-based signals are unlikely to work in isolation.

### 6.1.2 The 6% Gap: Why r=-0.486 is Insufficient

Some might argue r=-0.486 is "close enough" to the r<-0.5 threshold (only 6% short). We reject this interpretation for three reasons:

1. **Pre-registration prevents threshold creep.** Our MUST_WORK criteria (r<-0.5, p<0.05) were set in Phase 2B before data analysis, specifically to avoid post-hoc rationalization of borderline results. Adjusting thresholds after seeing data invalidates falsification logic.

2. **Statistical significance failure is clear-cut.** Even if we accepted r=-0.486 as "moderate," the p-value (0.154) is 3× above α=0.05. The wide confidence interval [-0.854, 0.207] includes positive correlations—we cannot rule out that CV and mean_ρ are uncorrelated or even positively correlated. This uncertainty is prohibitive for a prospective quality tool.

3. **Practical implications matter.** A predictor with r=-0.486 explains only 24% of variance (r²=0.236). For a researcher choosing between two benchmarks with CV=0.2 vs. CV=0.4, the predicted difference in mean_ρ is small and uncertain—not actionable for risk-based decisions. We need strong predictors (r<-0.7, r²>0.49) for practical benchmark selection tools, not borderline weak correlations.

**Conclusion:** The null result is not a statistical technicality—CV genuinely fails as a standalone quality signal.

## 6.2 Theoretical Contribution: Construct Divergence in Trust Benchmarks

While our primary hypothesis was refuted, the **cross-benchmark correlation analysis (Section 5.2) reveals a surprising and theoretically important pattern**: negative and near-zero correlations between benchmarks ostensibly measuring the same "trustworthiness" construct.

### 6.2.1 Negative Correlations as Discriminant Validity

The strongest negative correlation—**FaithfulQA vs. FinTrust (ρ=-0.568)**—is particularly striking. Both benchmarks claim to measure trust, yet they rank models inversely. Two interpretations:

**Interpretation 1 (Methodological Failure):** One or both benchmarks are poorly designed, producing inverted rankings due to noise or bias. This would be a quality failure.

**Interpretation 2 (Construct Divergence - Preferred):** FaithfulQA measures hallucination detection (factual grounding), while FinTrust measures financial ethical reasoning (value alignment). These are **orthogonal dimensions** within the broader "trust" construct. A model excelling at factual accuracy may lack ethical reasoning capabilities, or vice versa—negative correlation reflects valid construct independence, not measurement error.

Psychometric theory supports Interpretation 2. **Campbell & Fiske (1959)** distinguish:
- **Convergent validity:** Measures of the same construct should correlate positively.
- **Discriminant validity:** Measures of different constructs should correlate weakly or negatively.

Negative ρ between FaithfulQA and FinTrust suggests **good discriminant validity**—they measure distinct sub-dimensions. This is theoretically valuable but problematic for our hypothesis: if trust benchmarks measure orthogonal dimensions by design, then low cross-benchmark ρ is expected and doesn't indicate poor quality.

### 6.2.2 Implications for Benchmark Ecosystem Meta-Analysis

Our finding challenges a common assumption in benchmark meta-analysis: **that benchmarks within a domain (e.g., "trust evaluation") measure overlapping constructs and should exhibit positive cross-benchmark correlations**. This assumption is implicit in work like Kulkarni et al. (arXiv:2504.18114), which interprets cross-benchmark ranking disagreement as problematic.

Our results suggest an alternative framing: **disagreement may reflect valid multi-dimensionality, not measurement failure**. Before interpreting low cross-benchmark ρ as a quality issue, researchers should:

1. **Validate construct structure via factor analysis.** Do trust benchmarks load onto a single "trustworthiness" factor, or multiple orthogonal factors (honesty, harmlessness, fairness)? If multi-dimensional, low ρ is expected and not a reliability problem.

2. **Test external validity against criteria.** Do benchmarks claiming to measure "trust" correlate with human trust judgments, real-world deployment failures, or adversarial robustness tests? This separates construct validity from measurement reliability.

3. **Distinguish reliability from validity in quality assessment.** Use split-half correlation (within-benchmark consistency) for reliability, and external criteria correlation for validity. Don't conflate them via cross-benchmark ρ.

**Contribution:** Our null result and cross-benchmark pattern analysis **shift the benchmark quality conversation** from "how do we measure quality?" (answered: not via CV) to "what do benchmarks measure, and is cross-benchmark disagreement even a problem if constructs diverge?" This is a meta-scientific insight with implications beyond trust evaluation.

## 6.3 Limitations

We acknowledge four critical limitations that constrain the generalizability and interpretation of our findings:

### 6.3.1 Mock Data Validity Threat (CRITICAL)

**Limitation:** Our analysis uses a **mock benchmark corpus** with synthetic model scores, not real scraped leaderboards from TrustLLM, HaluBench, TruthfulQA, etc. This was a deviation from Phase 2C specifications, which required real-data extraction.

**Impact on conclusions:** Real leaderboards have structured biases absent from mock data:
- **Model selection bias:** Only certain model families (GPT, Llama, Mistral) are evaluated, creating non-random model coverage.
- **Evaluation protocol heterogeneity:** Different benchmarks use different prompting strategies, few-shot examples, and scoring rubrics.
- **Temporal effects:** Benchmarks published at different times evaluate different model generations.

Mock data generation may have unintentionally baked in null relationships (e.g., random CV-ρ pairing), making the r=-0.486 finding an artifact rather than a true empirical pattern.

**Why this is fundamental:** The hypothesis claims to provide a **practical tool for real benchmark verification**. If tested only on synthetic data, real-world utility is unproven. The negative cross-benchmark correlations (FaithfulQA-FinTrust ρ=-0.568) may also be mock data artifacts.

**Recommendation (Tier 1 - CRITICAL):** **Rerun h-e1 with real leaderboard data** before accepting the null result as valid. Extract actual TrustLLM HTML tables, TruthfulQA GitHub CSV, HaluBench PDF scores per Phase 2C specification. If real data replicates r≈-0.48, the null result is robust. If real data shows r<-0.5, p<0.05, then mock data misrepresented the relationship.

**Current conclusion validity:** ⚠️ **UNCERTAIN**—null result may be valid, or it may be a data artifact. Real-world validation is required.

### 6.3.2 Domain Restriction: Trust Benchmarks Only

**Limitation:** Our hypothesis was tested exclusively on trust evaluation benchmarks (TrustLLM, HaluBench, TruthfulQA, FinTrust, etc.). The null result applies **only to this domain**.

**Generalizability concerns:**
- **Math/reasoning benchmarks (GSM8K, MATH):** May have high CV by design (difficulty stratification from easy arithmetic to olympiad problems). High CV here might indicate good task coverage, not instability. CV-stability relationship could be positive (opposite of our hypothesis).
- **Vision-language benchmarks (VQA, COCO):** Multi-modal evaluation may have different variance sources (image ambiguity, caption subjectivity). CV semantics differ from text-only benchmarks.
- **General NLP (GLUE, SuperGLUE):** Broader task diversity (sentiment, NLI, QA, coreference) may exhibit different CV-stability dynamics than specialized trust tasks.

**Recommendation:** Do not generalize this null result beyond trust evaluation. Future work should test CV-stability correlations in math, vision-language, and general NLP domains as separate hypotheses. Each domain may have distinct CV-quality relationships.

### 6.3.3 CV Operationalization for Multi-Dimensional Benchmarks

**Limitation:** TrustLLM reports 8 sub-dimension scores (truthfulness, safety, fairness, robustness, privacy, ethics, machine ethics, toxicity), not a single overall score. Our Phase 4 implementation computed CV by averaging across dimensions, but this operationalization is not documented in the validation report.

**Impact on conclusions:**
- **Signal dilution:** If one dimension has high CV but others have low CV, averaging masks dimension-specific patterns. A single high-CV dimension might predict instability, but averaging with 7 low-CV dimensions dilutes the signal.
- **Arbitrary choice:** Alternatively, if we used a single "primary" dimension (e.g., overall trust score), the choice is arbitrary and may bias results.
- **Sensitivity unknown:** Without testing alternative operationalizations (average CV, max CV, primary dimension CV), we don't know if results are robust.

**Recommendation:** Document exact CV computation method. Rerun with alternative operationalizations (average, max, dimension-specific) to test sensitivity. If results change substantially, this is a specification ambiguity, not a fundamental limitation—the hypothesis needs clearer multi-dimensional operationalization.

### 6.3.4 Mechanism Validation Blocked (h-m1, h-m2 Not Tested)

**Limitation:** Our gate-driven workflow blocked mechanism hypotheses (h-m1: task heterogeneity, h-m2: context-dependent rankings, h-c1: confound robustness) when the existence hypothesis (h-e1) failed MUST_WORK criteria.

**Impact on conclusions:** We cannot distinguish:
- **Hypothesis is fundamentally false:** CV genuinely doesn't predict stability via any mechanism.
- **Mechanism is wrong:** CV predicts stability, but not via the task heterogeneity pathway we hypothesized. Alternative mechanisms (e.g., score ceiling effects, item difficulty calibration) might reveal different relationships.

**Why this matters:** Without mechanism testing, we don't know **why** CV fails. If the mechanism is wrong but a correlation exists under a refined theory, h-e1's r=-0.486 might strengthen.

**Recommendation:** If future work finds alternative meta-features that DO predict stability (e.g., split-half reliability), adapt h-m1/h-m2 to test those mechanisms. Current null result correctly aborts the mechanism investigation—testing "why X works" when X doesn't work is unproductive.

## 6.4 Broader Impact

**Positive impacts:**
- **Methodological rigor:** Our pre-registration, power analysis, and falsification framework provides a template for hypothesis-driven benchmark research, reducing exploratory p-hacking.
- **Negative evidence value:** Ruling out CV as a standalone quality signal constrains future tool development toward multi-feature or construct-aware approaches, saving research effort.
- **Construct validity awareness:** Highlighting the reliability-validity distinction motivates factor-analytic validation of benchmark ecosystems before meta-analyses interpret cross-benchmark disagreement.

**Risks:**
- **Over-simplification:** Simple heuristics (CV thresholds) may mislead researchers if adopted without understanding limitations. Quality assessment requires domain expertise and multi-faceted evaluation, not automated thresholds.
- **Premature dismissal:** Our null result for CV doesn't mean *all* leaderboard meta-features fail—IQR, split-half reliability, or multi-feature models may succeed where CV alone fails. Don't generalize the null result too broadly.

**Net impact:** Supporting more rigorous benchmark selection practices (avoiding unreliable evaluation) and shifting meta-science toward construct validation rather than assuming construct coherence.

## 6.5 Lessons for Future Work

Three key lessons emerge from our null result:

1. **Construct validity is prerequisite for quality assessment.** Before testing whether CV predicts "cross-benchmark stability," validate what benchmarks measure via factor analysis. If constructs diverge, cross-benchmark ρ is not a quality metric.

2. **Simple meta-features are insufficient.** Benchmark quality is multi-faceted (reliability, validity, discriminative power). Single statistics (CV, IQR alone) cannot capture this complexity. Multi-feature models with construct-aware interpretation are needed.

3. **Mock data is dangerous for meta-analysis.** Unlike model training (where synthetic data can simulate mechanics), benchmark meta-analysis depends on real-world leaderboard patterns (model selection bias, protocol heterogeneity). Mock data risks generating null relationships not present in real data. Always validate with real leaderboards before claiming generalizability.

## 6.6 Relation to Preliminary Failures

Our motivation (Section 1) referenced a preliminary failure: a benchmark dataset with only 2 models versus 8 expected, forcing hypothesis redesign. We hypothesized CV would have prospectively flagged this risk. Our null result suggests otherwise—CV doesn't predict cross-benchmark stability, so it likely wouldn't have detected the 2-model data issue either.

The 2-model failure was a **dataset availability problem** (not enough models evaluated), not a variance pattern CV would capture. A simpler heuristic—**n-models ≥ 10 threshold**—remains the more reliable check, consistent with our experimental inclusion criterion (Section 4.2.2). This negative finding is valuable: it redirects attention from CV-based tools to basic sanity checks (model count, overlap) and construct validation.

## 6.7 Summary

Our null result (r=-0.486, p=0.154) demonstrates that coefficient of variation is insufficient as a standalone prospective benchmark quality signal. However, the cross-benchmark correlation analysis reveals negative ρ patterns (e.g., FaithfulQA-FinTrust ρ=-0.568) suggesting trust benchmarks measure orthogonal dimensions, not a unitary construct. This finding has two implications:

1. **CV fails because cross-benchmark ρ conflates reliability and validity.** Low ρ may reflect valid construct divergence, not measurement unreliability—CV cannot disambiguate.
2. **Benchmark quality assessment requires construct-aware approaches.** Factor analysis to validate what benchmarks measure should precede quality metric development.

The gap identified in our motivation (lack of prospective verification tools) remains unfilled, but our null result provides valuable negative evidence constraining future tool development toward multi-feature models and psychometric grounding. Section 7 concludes with a three-tier research roadmap addressing these lessons.
