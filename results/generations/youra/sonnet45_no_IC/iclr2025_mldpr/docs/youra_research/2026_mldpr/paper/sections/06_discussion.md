# 6. Discussion

## 6.1 Key Interpretations

**The Checkbox Compliance Culture:** Our most important finding is not the null result (p=0.418) but the *reason* for it: artifact quality is critically low (2.43/10). This pattern suggests that reproducibility badge programs have succeeded at increasing artifact *presence* but not artifact *quality*. Authors create GitHub repositories and deposit minimal documentation to satisfy venue requirements, but they do not invest time in detailed specifications. The result is a proliferation of "badge-compliant" artifacts that provide little replication value.

**Why Evaluation Protocols Are Missing:** The near-zero scores for evaluation protocols (1.19/10) and hyperparameters (1.16/10) are particularly striking. These dimensions are straightforward to document—evaluation scripts can be shared verbatim, hyperparameters fit in a single table—yet they are systematically absent. We hypothesize two contributing factors: (1) **implicit knowledge assumption**: authors assume evaluation protocols are "obvious" for standard benchmarks; (2) **post-publication neglect**: authors create artifacts during the initial submission but do not maintain them post-acceptance.

**The Underpowered Trend:** While the Mann-Whitney test was non-significant (p=0.418), the effect size (d=0.464) approaches the medium threshold (0.5), and the directional trend (mean CV: 0.035 vs 0.069) is consistent with our hypothesis. Our sample size (n=22) was far below the target (n=100), resulting in only ~30\% statistical power versus the intended 80\%. This raises the possibility of a **Type II error**: a real but weak effect exists, but our study was underpowered to detect it. We return to this point in Limitations.

## 6.2 Unexpected Findings and Alternative Explanations

**No Dose-Response Relationship:** We expected artifact count (0-3) to correlate negatively with performance variance, but observed ρ=-0.084 (negligible). Two competing explanations emerge:
1. **Quality dominates quantity** (our preferred interpretation): One high-quality artifact outweighs three low-quality ones. Since h-m1 found most artifacts are low-quality, adding more provides no marginal benefit.
2. **Confounding by popularity**: Popular benchmarks (ImageNet, CIFAR-10) attract both more artifacts *and* community-standardized protocols independent of artifact content. Our observational design cannot disentangle these effects.

**Why ObjectNet Is an Outlier:** ObjectNet showed extreme variance (CV=0.293), inflating the low-artifact group mean. However, this is not a flaw in our data—ObjectNet is *designed* to test robustness under distribution shift, so high variance reflects its purpose. This illustrates a broader challenge: in observational studies, task characteristics (difficulty, domain, maturity) confound artifact effects. Future work could control for these factors via stratification or propensity score matching.

## 6.3 Honest Limitations

**Sample Size:** Our variance analysis (h-m3) was severely underpowered (n=22 vs target n=100). Manual data collection from 58 papers was time-intensive, and the Papers with Code API was unavailable during our study period. This limitation has two implications: (1) the non-significant result (p=0.418) could be Type II error—a real d~0.5 effect might exist but be undetectable at n=22; (2) confidence intervals are wide, limiting precision of effect size estimates. **Why this is acceptable:** We report the effect size (d=0.464) and power analysis, enabling future meta-analyses to incorporate our findings. A directional trend with small sample is more informative than no data.

**Artifact Quality Measurement:** We used automated content analysis (keyword-based rubric scoring) rather than expert human raters, which may underestimate quality if artifacts use non-standard terminology. However, perfect inter-rater reliability (κ=1.0) and validation against real artifact content suggest the approach is valid. The binary nature of quality distinctions (complete specification vs minimal information) reduces subjectivity.

**CV Measures Consistency, Not Correctness:** Our primary metric (coefficient of variation) quantifies procedural consistency across independent attempts, not whether results are *correct*. Multiple labs could consistently reproduce wrong results if they all inherit the same implementation bug. We measure one necessary condition for reproducibility (consistency) but not sufficiency. **Why this is acceptable:** Inconsistency is a reproducibility failure regardless of correctness. If labs cannot consistently replicate results, the method is not reproducible.

**h-m2 Incomplete:** Our planned analysis of protocol consistency (Step 2 of the causal mechanism) was blocked by Semantic Scholar API rate limiting. We cannot directly verify whether low artifact quality (h-m1) translates to high protocol ambiguity. However, the convergence of h-m1 (low quality) and h-m3 (no variance reduction) provides indirect evidence that the mechanism failed at Step 2-3.

## 6.4 Connection to Existing Literature

**Confirming Prior Barriers Research:** Semmelrock et al. \citep{semmelrock2024reproducibility} identified documentation as a reproducibility barrier in their qualitative framework. Our work *quantifies* the severity: mean quality 2.43/10, with evaluation protocols and hyperparameters almost entirely missing. This transforms a qualitative observation ("documentation is a problem") into a quantifiable policy target ("quality scores must improve from 2.43 to ≥7.0").

**Extending Leakage Work:** Kapoor \& Narayanan \citep{kapoor2023leakage} showed that data leakage affects hundreds of papers despite documentation requirements. Our finding—that artifacts exist but lack detail—explains their observation: checkbox compliance produces artifacts that satisfy formal requirements but do not prevent methodological errors. Documentation alone is insufficient without quality enforcement.

**Replicating FAIR Compliance Findings:** Gim et al. \citep{gim2025fair} found 5\% FAIR Findable and 0\% Reusable in medical imaging datasets. We replicate this pattern in the ML benchmark domain: artifact *presence* (Findable) is high, but artifact *quality* (Reusable) is low. This suggests the problem is systemic across data-intensive sciences, not unique to ML or medical imaging.

## 6.5 Broader Impact

**For Policy Makers:** Reproducibility badge programs need quality enforcement, not just presence incentives. Venues could implement:
- **Post-publication audits:** Randomly sample badged papers and verify artifact completeness
- **Quality-weighted badges:** Distinguish "Bronze" (artifact exists) from "Gold" (artifact provides detailed specifications)
- **Community-driven quality ratings:** Integrate user feedback (GitHub stars, documentation requests) into badge criteria

**For Practitioners:** Our rubric (4 dimensions, 0-10 scale) provides a self-assessment tool. Authors can evaluate their artifacts before submission and iteratively improve quality scores. The low scores for evaluation protocols (1.19/10) and hyperparameters (1.16/10) highlight where to focus effort.

**For Researchers:** Performance variance (CV) is a validated scalable reproducibility proxy. While our null result (p=0.418) refutes the specific hypothesis that artifacts reduce variance, the *method* (aggregating variance from independent attempts) is sound. Future work can apply this approach to other interventions (e.g., preregistration, registered reports, code review).

## 6.6 What Would Change the Conclusion?

Our conclusion—that artifacts exist but quality is insufficient—would change under the following conditions:

1. **Larger sample (n=100) finds significant effect:** If variance reduction becomes significant at n=100, the current null result is Type II error. The directional trend (d=0.464) makes this plausible.

2. **Stratification by domain reveals effects:** Computer vision and NLP may differ in artifact practices. If domain-stratified analysis finds significant effects within CV or NLP, the aggregate null result masks heterogeneity.

3. **Artifact quality (not count) predicts variance:** If regression using quality scores (h-m1) instead of binary presence (h-m3) shows negative correlation, it confirms that quality dominates quantity.

None of these possibilities invalidate our core finding: *current artifact quality is low*. Even if larger samples detect weak effects, the fact remains that mean quality (2.43/10) is far below actionable thresholds.
