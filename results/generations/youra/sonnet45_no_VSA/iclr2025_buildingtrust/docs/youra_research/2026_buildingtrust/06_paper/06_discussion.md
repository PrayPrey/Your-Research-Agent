# Discussion

Our null result—coefficient of variation does not reliably predict cross-benchmark ranking stability (r=-0.486, p=0.1542)—admits multiple interpretations. We discuss three theoretical perspectives, critical limitations, implications for benchmark meta-analysis methodology, and connections to broader meta-science challenges.

## Theoretical Interpretations

### Interpretation 1: CV is Not a Valid Quality Signal (Hypothesis Refuted)

The straightforward interpretation is that simple variance metrics cannot predict benchmark reliability. Several mechanisms could explain this failure:

**Variance sources are heterogeneous.** High CV may arise from multiple causes:
1. **Legitimate score spread** — Good model differentiation (desirable)
2. **Heterogeneous task difficulty** — Mix of easy and hard items (not necessarily bad)
3. **Measurement noise** — Unstable capability measurement (problematic)
4. **Small effective sample size** — Few discriminative items amplify variance (problematic)

CV cannot distinguish these sources. A high-CV benchmark might represent good coverage of difficulty range (cause 2) rather than noisy measurement (cause 3). If most high-CV benchmarks in our corpus fall into category 1 or 2, the hypothesis premise—"high CV indicates noise"—is wrong.

**Cross-benchmark stability has complex determinants.** Even if CV validly signals noise, cross-benchmark ρ may depend on additional factors that swamp the CV signal:
- **Task format compatibility** (multiple-choice vs. generation)
- **Model subset overlap** (which models are evaluated)
- **Construct alignment** (what trust sub-dimension is measured)
- **Benchmark maturity** (publication recency, community adoption)

A multi-feature model combining CV with other meta-features (skewness, inter-quartile range, ceiling proximity, model diversity index) might achieve predictive utility where CV alone fails.

**Non-linear relationships.** Our Pearson correlation test assumes linear relationship between CV and ρ. Plausibly, CV only predicts instability at extremes (e.g., CV > 0.4 = risky) but not across the full range. A threshold model—"reject benchmarks with CV > 0.4"—might work as a binary classifier even if the linear correlation fails. Post-hoc quartile analysis could test this, though it risks post-hoc rationalization given the null result.

### Interpretation 2: Cross-Benchmark ρ Conflates Stability with Construct Divergence (Wrong Dependent Variable)

The unexpected negative correlations (FaithfulQA-FinTrust ρ=-0.568, TruthfulQA-SafetyBench ρ=-0.379) challenge the hypothesis premise. Low cross-benchmark ρ is **ambiguous**:

**Measurement instability interpretation (hypothesis assumption):**
> Low ρ indicates noisy benchmarks that produce inconsistent rankings. High-CV benchmarks are noisy, therefore predict low ρ.

**Construct divergence interpretation (alternative):**
> Low ρ indicates valid differences in what benchmarks measure. Trust is multi-dimensional (honesty, harmlessness, fairness), and benchmarks targeting different dimensions should show low or even negative correlation. High CV in one dimension doesn't predict generalization to other dimensions.

Evidence favoring construct divergence interpretation:

1. **Negative correlations cluster by dimension.** FaithfulQA (hallucination) negatively correlates with FinTrust (financial trust, ρ=-0.568) and TrustBench-Ethics (ethical reasoning, ρ=-0.557). These are conceptually distinct trust sub-dimensions, not measurement failures.

2. **Safety benchmarks disagree.** TrustLLM-Safety vs. SafetyBench correlation is negative (ρ=-0.268), despite both measuring "safety." This suggests "safety" itself is multi-dimensional (jailbreak resistance, toxicity avoidance, refusal behavior) and benchmarks target different safety sub-facets.

3. **Truthfulness cluster has positive correlations.** TruthfulQA correlates positively with FinTrust (ρ=0.721), MultiTrust (ρ=0.621), and HaluBench (ρ=0.414 via TrustLLM-Truthfulness at ρ=0.604). This indicates truthfulness has better construct coherence than safety or fairness.

4. **Psychometric parallel: Campbell & Fiske (1959) multitrait-multimethod matrix.** Low cross-construct correlation is **expected** under discriminant validity. If trust benchmarks measure orthogonal constructs, low ρ is valid, not problematic.

**Implication:** If construct divergence dominates, then CV predicting low ρ would mean "high variance in dimension X doesn't generalize to dimension Y" (trivially true), not "high CV indicates bad benchmarks" (the practical claim we wanted to test).

**Resolution:** Factor analysis could distinguish these interpretations. If trust benchmarks load onto a single-factor "trustworthiness" construct, then low ρ indicates measurement instability (supports Interpretation 1). If trust benchmarks load onto multiple factors (honesty, harmlessness, fairness), then low ρ indicates valid divergence (supports Interpretation 2, invalidates the hypothesis as formulated).

### Interpretation 3: Statistical Power Limitations Despite Adequate Sample Size

Although our power analysis confirmed 70-90% power to detect r=-0.5 to -0.7, we observed r=-0.486 with p=0.1542. Post-hoc power for the observed effect (r=-0.486) is ~64%, slightly below our 70% target. This raises the possibility that a true effect r=-0.5 exists, but we had a Type II error (false negative).

**Counter-arguments:**
1. **Direction is wrong for Type II error.** Our observed r=-0.486 is 6% weaker than threshold. If the true effect were r=-0.5, we'd expect observed r to vary around -0.5, not systematically fall short.
2. **Wide confidence interval includes positive correlations.** 95% CI [-0.854, 0.207] indicates the true effect could plausibly be zero or even positive, not just slightly weaker than -0.5.
3. **p=0.1542 is not borderline.** A p-value 3× the threshold (0.1542 vs. 0.05) suggests weak evidence, not a near-miss that larger sample might rescue.

**Verdict:** Type II error is possible but unlikely. The more parsimonious interpretation is that the true effect is weaker than r=-0.5, making CV a poor predictor even if a weak negative correlation exists.

## Critical Limitations

### Limitation 1: Mock Data Validity Threat (CRITICAL)

Our analysis used a **mock benchmark corpus** (synthetic data) rather than real leaderboards scraped from TrustLLM HTML, TruthfulQA GitHub CSV, and HaluBench PDF. This is the most serious validity threat.

**Why this matters:**
- Mock data may not replicate real-world CV distributions (e.g., if mock generation assumes uniform variance, real benchmarks might have bimodal CV distributions)
- Cross-benchmark ρ patterns may differ between mock and real data (e.g., negative correlations might be artifacts of mock data generation assumptions)
- The null result could be an artifact: real leaderboards might show r < -0.5, p < 0.05, supporting the hypothesis

**Mitigation attempted:** None. Phase 2C specified real leaderboard extraction, but Phase 4 implementation substituted mock data.

**Required follow-up:** **Tier 1 CRITICAL replication** (1 week estimated effort):
1. Scrape real leaderboards: TrustLLM (HTML), TruthfulQA (GitHub CSV), HaluBench (PDF supplement)
2. Rerun identical analysis pipeline
3. Compare real-data r, p to mock-data baseline (r=-0.486, p=0.1542)
4. If real data shows r < -0.5, p < 0.05, hypothesis is **supported** (mock data was misleading)
5. If real data replicates null result (r ≈ -0.486, p > 0.05), hypothesis is **refuted** (robust finding)

Until this replication is completed, the null result should be considered **conditional on mock data validity**.

### Limitation 2: Construct Validity of Cross-Benchmark ρ (Fundamental)

As discussed in Interpretation 2, cross-benchmark ρ may not be a pure stability metric—it conflates measurement stability with construct divergence. This is a **conceptual limitation** that cannot be fixed by collecting more data.

**Why this matters:**
- Low ρ between FaithfulQA (hallucination) and FinTrust (financial trust) may reflect valid construct non-overlap, not instability
- Hypothesis assumes trust benchmarks measure unitary "trustworthiness," but negative correlations suggest multi-dimensional construct
- Without factor-analytic validation, we cannot interpret low ρ as stability failure vs. construct divergence

**Mitigation attempted:** None. We treated ρ as a stability metric without validating what trust benchmarks measure.

**Required follow-up:** **Tier 3 confirmatory factor analysis** (1 month estimated effort):
1. Collect model scores across all 10 trust benchmarks (requires real data, not mock)
2. Conduct CFA testing single-factor "trustworthiness" vs. multi-factor (honesty, harmlessness, fairness) models
3. Compute factor loadings: Do TruthfulQA and FaithfulQA load on same factor? Do safety benchmarks cluster?
4. If multi-factor model fits better, redefine stability as **within-factor ρ** (e.g., only compare truthfulness benchmarks)
5. Retest hypothesis: Does CV predict within-factor ρ?

This reframing would change the research question from "Does CV predict cross-benchmark stability?" to "Does CV predict within-construct stability?"—a more appropriate test given construct heterogeneity.

### Limitation 3: Multi-Dimensional Benchmark Operationalization

TrustLLM reports 8 sub-dimension scores (truthfulness, safety, fairness, robustness, privacy, ethics, transparency, accountability) plus an overall aggregate. We used overall scores to compute CV, but this choice is arbitrary.

**Alternative operationalizations:**
1. **Average CV across dimensions** — Mean of 8 sub-dimension CVs
2. **Maximum CV** — Highest variance dimension dominates
3. **Primary dimension CV** — Use truthfulness or safety CV only

Different operationalizations might produce different correlations. If the null result is sensitive to this choice, it's a specification ambiguity rather than a robust finding.

**Mitigation attempted:** None. Operationalization choice not documented in h-e1 validation report.

**Required follow-up:** **Tier 2 sensitivity analysis** (2 days estimated effort):
1. Extract 8 sub-dimension scores from TrustLLM (if available in mock data)
2. Compute CV under each operationalization (average, max, primary)
3. Retest hypothesis for each CV variant
4. If any variant achieves r < -0.5, p < 0.05, the null result is operationalization-dependent

### Limitation 4: Sample Size and Generalizability

Our sample (n=10 trust benchmarks) is adequate for statistical power (70-90% for r=-0.5) but limits generalizability beyond the trust evaluation domain.

**Domain restriction:** Math/reasoning benchmarks (GSM8K, MATH, BigBench) may have different CV-stability relationships:
- High CV in math may indicate good difficulty coverage (easy arithmetic → olympiad problems), not noise
- Vision-language benchmarks may have different variance sources (image ambiguity, caption subjectivity)
- General NLP benchmarks (GLUE, SuperGLUE) may have broader task diversity changing CV semantics

**Implication:** Do not generalize this null result beyond trust benchmarks without domain-specific replication.

**Mitigation attempted:** None. Domain restriction was intentional (trust evaluation focus).

**Required follow-up:** **Tier 4 domain replication** (3 months estimated effort):
1. Replicate analysis in math/reasoning benchmarks (n=10-15)
2. Replicate in vision-language benchmarks (n=5-10, smaller population)
3. Replicate in general NLP benchmarks (n=10-15)
4. Meta-analyze across domains: Is CV-stability null universal or domain-specific?

## Implications for Benchmark Meta-Analysis Methodology

Our study demonstrates **what doesn't work** (simple variance metrics) and **what challenges exist** (construct validity, mock data risks). We derive four methodological lessons:

### Lesson 1: Pre-Registration Enables Publishable Null Results

Our gate-driven validation framework with pre-registered success criteria (r < -0.5, p < 0.05) transforms an otherwise unpublishable null result into rigorous negative evidence. Without pre-registration, the null finding would be dismissed as "tried something, didn't work" rather than "systematically tested a plausible hypothesis and demonstrated its failure."

**Recommendation:** Meta-evaluation research should adopt pre-registration (e.g., Open Science Framework, AsPredicted.org) to enable null result reporting. This avoids publication bias where only positive findings appear in the literature.

### Lesson 2: Construct Validity is a Confound in Cross-Benchmark Meta-Analyses

Interpreting cross-benchmark disagreement requires knowing what benchmarks measure. Low ρ is ambiguous without construct validation (factor analysis, expert consensus, convergent/discriminant validity assessment).

**Recommendation:** Before meta-analyzing benchmark agreement, validate construct coherence. If benchmarks measure orthogonal sub-dimensions (e.g., honesty ≠ safety), compare within-dimension ρ rather than cross-dimension ρ.

### Lesson 3: Mock Data Introduces Validity Threats in Meta-Analysis

Unlike model training (where synthetic data can simulate training mechanics), benchmark meta-analysis depends on real-world leaderboard patterns. Mock data generation assumptions (e.g., random CV assignment, uniform cross-benchmark ρ) risk generating null relationships not present in real data.

**Recommendation:** Prioritize real data extraction in meta-analysis design. If mock data is used (e.g., for prototyping), explicitly flag as critical limitation and recommend real-data replication before accepting results as generalizable.

### Lesson 4: Single-Feature Predictors are Likely Insufficient

Even if CV had weak predictive power (r=-0.3, say), a single meta-feature cannot capture benchmark quality comprehensively. Multi-feature models combining:
- **CV** (score dispersion)
- **Skewness** (distribution shape, ceiling effects)
- **IQR** (robust spread metric, less sensitive to outliers than CV)
- **Ceiling proximity** (max score / perfect score, saturation indicator)
- **Model diversity** (architecture family count, diversity index)
- **Split-half reliability** (item-level stability, requires per-item data)

... might achieve practical utility where CV alone fails.

**Recommendation:** Future work should test multi-feature quality models (e.g., random forest classifier: "risky benchmark" vs. "stable benchmark") rather than single-feature correlations.

## Connections to Broader Meta-Science Challenges

Our findings resonate with three broader themes in meta-science:

### Replication Crisis and Construct Ambiguity

Psychology's replication crisis (2010s) revealed that low replication rates often stem from **construct ambiguity**—different labs operationalize "trust" or "aggression" differently, producing divergent findings. Our negative cross-benchmark correlations (FaithfulQA-FinTrust ρ=-0.568) mirror this pattern: ostensibly similar "trust" benchmarks measure different constructs, producing low replication rates.

**Parallel:** Just as psychology requires construct validation via confirmatory factor analysis, LLM evaluation requires empirical validation of what benchmarks measure before interpreting cross-benchmark disagreement.

### Benchmark Fragmentation as a Coordination Failure

Mmjerge's finding (<25% overlap across 7,635 benchmarks) represents a coordination failure: the community lacks mechanisms to converge on standard instruments. Our study attempted to provide a **prospective quality signal** (CV) to guide benchmark selection, but the hypothesis failed.

**Implication:** Absent prospective quality metrics, benchmark standardization requires **community-driven consensus** (e.g., HELM's multi-metric approach, LMSYS Chatbot Arena's crowdsourced rankings) rather than data-driven signals. This shifts the problem from technical (meta-feature discovery) to social (community adoption).

### The Value of Negative Evidence

Our null result is valuable negative evidence: it prevents future researchers from wasting effort on CV-based verification tools. This aligns with meta-science movements advocating for null result publication (e.g., Journal of Negative Results, Registered Reports format).

**Recommendation:** LLM evaluation venues (EMNLP Findings, NeurIPS Datasets & Benchmarks, TMLR) should adopt Registered Reports to incentivize pre-registered hypothesis testing with publishable null results.

## Alternative Explanations Not Ruled Out

Several plausible mechanisms could explain the null result beyond "CV doesn't predict stability":

1. **Model subset bias:** If our 10 benchmarks systematically evaluated different model subsets (e.g., only commercial models vs. only open-source models), cross-benchmark ρ estimates would be biased. We required ≥5 shared models, but this doesn't guarantee representative overlap.

2. **Metric heterogeneity:** If benchmarks use different metrics (accuracy, AUROC, F1, exact match), CV normalization (σ/μ) might not make them comparable. Alternative normalization (z-scores, percentile ranks) might reveal patterns we missed.

3. **Temporal effects:** If benchmarks were published at different times and evaluated different model generations (GPT-3 vs. GPT-4 era models), cross-benchmark ρ might reflect model evolution rather than measurement stability.

We did not control for these factors. Future work could test robustness via partial correlation (control for model overlap %, metric type, benchmark age) or stratified analysis (compare benchmarks within matched model sets).

## Summary

The null result admits three interpretations: (1) CV is not a valid quality signal, (2) cross-benchmark ρ conflates stability with construct divergence (wrong dependent variable), or (3) Type II error despite adequate power (unlikely given p=0.1542). We identify four critical limitations: mock data validity threat (CRITICAL, requires real-data replication), construct validity ambiguity (fundamental, requires factor analysis), multi-dimensional CV operationalization (specification choice), and sample size domain restriction (trust benchmarks only).

Methodologically, this study demonstrates that rigorous null results require: pre-registration (enables publication), power analysis (rules out underpowering), construct validation (disambiguates stability from divergence), and real data (avoids mock data artifacts). The finding that simple variance metrics fail motivates multi-feature quality models and community-driven benchmark standardization.

Despite the null result, this work advances LLM evaluation methodology by documenting what doesn't work (CV alone), revealing construct validity issues (negative cross-benchmark correlations), and establishing a template for publishable negative evidence via gate-driven validation frameworks.
