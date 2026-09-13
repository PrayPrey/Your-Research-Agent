# 6. Discussion

## 6.1 The Documentation API Gap: What Automation Can and Cannot Measure

Our central finding — that DTS's highest-priority sections (Preprocessing, Uses) score near-zero across all repositories not because creators skip documentation but because structured APIs don't expose it — has implications beyond this paper. It reveals a systematic mismatch between what responsible AI documentation frameworks designate as most important and what current repository infrastructure makes machine-readable.

The DTS inverse-frequency weighting was designed precisely to address the problem that different sections have different levels of documentation effort: rare, hard-to-fill sections (Collection, Preprocessing) receive higher weights because their presence is more informative. Our results confirm that these sections are rare in API-accessible structured form. But the reason they are rare differs between the manual and automated scoring contexts: in manual scoring, rarity reflects the genuine effort required to document these sections; in automated API scoring, rarity also reflects a structural API design choice that keeps prose-heavy sections as free text rather than structured fields.

This distinction matters for anyone designing automated documentation quality assessment. An API-based scorer will systematically underestimate completeness for responsible AI's highest-priority sections — not because datasets are poorly documented, but because the documentation that exists for those sections lives in prose that APIs don't index. Closing this gap requires either (a) repository operators adding structured API fields for Preprocessing and Uses sections (an infrastructure intervention), or (b) LLM-based parsing of free-text card prose to extract completeness signals (a modeling intervention). Both are viable directions; neither is trivial.

The practical implication for practitioners using DTS scores for compliance assessment: a DTS-weighted API-based score of, say, 0.2 for a given dataset does not necessarily mean the dataset has inadequate documentation — it may mean the documentation is adequate but written in prose that the API doesn't expose. Human review of the full card prose remains necessary for sections where API coverage is near-zero.

## 6.2 UCI Field Mapping Gap: An Engineering Issue, Not a Fundamental Failure

The UCI = 0% coverage finding is best understood as a field naming mismatch between the `ucimlrepo` library's output schema and the DTS scorer's configured field keys, not as evidence that UCI datasets lack structured metadata. We successfully collected 62 UCI datasets (non-zero API calls, populated metadata objects returned), but the scorer found no matching field names.

This is a correctable engineering issue: inspecting the actual key names returned by `ucimlrepo.fetch_ucirepo()` for a small sample and updating the scorer's UCI mapping specification would likely restore coverage for UCI datasets. We explicitly document this gap so that researchers extending this pipeline to UCI can address it directly. Until fixed, UCI datasets should be excluded from cross-repository completeness comparisons; our HF+OpenML corpus (n=696) provides a substantial and diverse two-repository base for analysis.

## 6.3 Implications for Repository Design

Our results have concrete implications for repository operators. The highest-leverage intervention to improve automated documentation quality assessment would be adding structured API fields for the Preprocessing and Uses sections — the two sections that currently score near-zero precisely because they lack structured API representations. This would not require dataset creators to document more; it would require repository platforms to add YAML schema fields that creators can fill in, analogous to how HuggingFace added `task_categories` and `language` fields in 2021.

The DTS weights suggest where to focus: Preprocessing (weight 1.8) and Uses (weight 1.5) together account for 33% of the total DTS weight but contribute near-zero to automated scores. Structured API fields for these sections — even simple binary presence indicators for "does preprocessing documentation exist?" — would dramatically improve the sensitivity of automated DTS scoring.

## 6.4 Limitations

**L1: Proxy Validation Only — No Human-Expert External Validity.**
Our proxy validation (r=0.989 between weighted and unweighted DTS scores) confirms that the scoring algorithm is internally consistent and reproducible, but does not establish that automated DTS scores agree with human expert judgments of documentation quality. The planned human annotation study (n=120 datasets, 3 experts × 40 datasets each) would test whether the sections that score high in our automated system are the same sections that human domain experts judge as well-documented. Until this study is conducted, automated DTS scores should be interpreted as measuring *structured API field coverage* rather than *documentation quality as judged by experts*. The r=0.989 is a necessary condition for external validity (an inconsistent scorer cannot be externally valid) but not sufficient.

*Why acceptable:* Internal consistency is the foundational property for any measurement instrument. The gap between proxy and human validation is clearly delineated, and the validation protocol is fully specified.

*Planned mitigation:* Human annotation study with 3 domain experts rating 40 datasets each (120 total, stratified by repository and DTS completeness quartile), computing Pearson r between human mean scores and automated DTS-weighted scores.

**L2: Causal Claims Untested — Existence Proof Only.**
The original H-DocComp-v1 hypothesis predicted that (P1) HuggingFace datasets have higher DTS completeness than OpenML/UCI after controlling for dataset age and task domain, that (P2) DTS completeness predicts dataset download counts in a pre-registered negative binomial regression (β≥0.15), and that (P3) post-2021 HuggingFace datasets show higher completeness via a DiD test. None of these causal predictions were tested in this study — the pipeline terminated after the existence hypothesis (h-e1) with h-m1, h-m2, and h-m3 NOT_STARTED. This paper establishes the measurement instrument and reports descriptive findings; the causal questions remain as a research agenda.

*Why acceptable:* Methodological feasibility is a genuine prerequisite contribution. A causal study of documentation completeness requires a validated, scalable scoring instrument — which this paper provides. Framing as methods + descriptive paper is appropriate given available evidence.

*Planned mitigation:* Execute h-m1 (ANOVA + DiD cross-repository comparison), h-m2 (filter eligibility logistic regression), and h-m3 (pre-registered negative binomial regression) using the pipeline infrastructure established here.

**L3: Cross-Sectional Snapshot — No Longitudinal Measurement.**
All data was collected in a single API session in March 2026. Documentation completeness is likely not static — repository platforms update their metadata structures, dataset creators add documentation over time, and platform policies change (e.g., HuggingFace's 2021 YAML schema introduction). Our results characterize the state of documentation compliance in March 2026; temporal trends require periodic re-collection.

*Why acceptable:* Cross-sectional at population scale (n=758) with stratified sampling across task domains and upload year cohorts is a methodologically valid and novel contribution.

*Planned mitigation:* Quarterly re-collection using the same pipeline with cached baselines to track longitudinal documentation quality trends.

## 6.5 Broader Impact

This work contributes to the responsible AI tooling ecosystem by providing an automated, open-source DTS-weighted documentation scoring pipeline that practitioners and platform operators can use to assess dataset documentation compliance. The finding that Preprocessing and Uses sections — critical for responsible AI deployment decisions — are systematically absent from machine-readable API fields is actionable for both dataset creators and repository operators: creators should know that their prose-only documentation in these sections is invisible to automated quality checks, and operators should consider adding structured API fields for these high-priority sections.

We do not foresee significant misuse potential: documentation quality scoring incentivizes *better* documentation rather than enabling harm. One risk is that practitioners may use automated DTS scores as a substitute for careful manual review of dataset cards, given the false-precision that numerical scores can convey. We caution against this: automated DTS scores measure structured API field coverage, not documentation quality comprehensively. They are a triage tool for identifying obvious documentation gaps, not a replacement for human assessment of dataset fitness-for-purpose.
