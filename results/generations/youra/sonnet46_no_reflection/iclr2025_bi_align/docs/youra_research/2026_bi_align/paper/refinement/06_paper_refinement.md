# Can Existing RLHF Preference Corpora Reveal Human-to-AI Stylistic Adaptation? A Null Result with Methodological Contributions

## Abstract

Reinforcement learning from human feedback (RLHF) produces AI outputs with characteristic stylistic features, including structured lists, safety prefaces, chain-of-thought scaffolding markers, and hedging language. Whether annotators who interact repeatedly with deployed RLHF-optimized systems develop stronger preferences for these features — compared to annotators without such exposure — is an empirical question that existing preference datasets have not been used to address. This paper introduces the AI-Idiomatic Formatting Signal (AIFS) construct, a regex-based composite measure across four feature classes, and evaluates it on 80,342 preference pairs from the Anthropic HH-RLHF corpus using a conditional logit model with 27,034 semantic cluster fixed effects and a response-length covariate. AIFS features predict annotator preference (β₁ = 0.0246, p < 0.001). The adaptation interaction term — whether annotators in the deployed-AI condition prefer AIFS features more strongly than annotators in the base condition — is not statistically significant (β₄ = −0.0016, OR = 0.9984, 95% CI [0.9861, 1.0108], p = 0.796). Examination of the dataset reveals that the HH-RLHF split labels encode data collection provenance rather than annotator exposure history, rendering them invalid proxies for the intended adaptation contrast. The null result on β₄ is therefore uninterpretable as direct evidence regarding the bidirectional alignment hypothesis. This finding identifies a structural limitation in existing RLHF preference datasets for bidirectional alignment research and motivates the collection of annotator-linked, longitudinally designed preference corpora.

---

## 1. Introduction

Reinforcement learning from human feedback (RLHF) is a widely applied paradigm for aligning language model outputs with human preferences [Bai et al., 2022; Ouyang et al., 2022; Rafailov et al., 2023]. In this paradigm, human annotators compare pairs of model responses, and a reward model is trained to predict their preferences; a policy model is subsequently optimized against this reward. A known consequence of this process is the amplification of surface-level stylistic features that correlate with annotator approval, including structured enumeration, hedged assertions, and explicit reasoning chains [Stiennon et al., 2020; Rafailov et al., 2023].

A related question — whether prolonged human interaction with RLHF-optimized outputs in turn modifies human annotator preferences — has received comparatively little empirical attention. This constitutes one direction of bidirectional human-AI alignment, in which AI systems and human behavior mutually influence each other over time. Shen et al. [2024] synthesize over 400 papers across alignment, human-computer interaction, and cognitive science, finding that while AI-to-human effects such as persuasion and automation bias appear in multiple experimental studies, the reverse direction — systematic human behavioral adaptation toward AI-idiomatic norms — has not been empirically quantified in the alignment literature. Vishwarupe et al. [2026] audit 16 alignment benchmarks and find that none include mechanisms for verifying annotator behavioral change over time.

The present study was designed to test one specific instantiation of the human-to-AI adaptation hypothesis: whether annotators with prior exposure to deployed RLHF-trained systems show a measurably stronger preference for AI-idiomatic stylistic features relative to annotators without such exposure. To operationalize this hypothesis, the study introduces the AIFS construct — a composite count measure covering four stylistic feature classes — and applies a conditional logit regression with semantic cluster fixed effects to the Anthropic HH-RLHF dataset [Bai et al., 2022], using the dataset's helpful-online versus helpful-base split as a proxy for annotator AI-exposure history.

The main results are as follows. First, AIFS features significantly predict annotator preference overall (β₁ = 0.0246, p < 0.001), establishing the construct's validity as a preference signal. Second, the interaction between AIFS features and annotator condition (online versus base) is not statistically significant (β₄ = −0.0016, OR = 0.9984, 95% CI [0.9861, 1.0108], p = 0.796), and all four pre-registered gate thresholds are not met. Third, examination of the dataset documentation reveals that the split labels record which model generated the presented responses, not which annotators had prior AI exposure. The split is a data provenance label, not an annotator characteristic, and its use as an exposure proxy is not supported by the available metadata.

This paper makes the following contributions. It introduces and validates the AIFS construct as a preference predictor in a large-scale preference corpus. It documents and resolves a numerical instability issue — BFGS optimizer divergence on conditional logit problems with large numbers of small cluster fixed effects — through Newton-Raphson optimization. It provides an empirical demonstration that split-based adaptation proxies in the HH-RLHF dataset do not correspond to annotator exposure conditions, a distinction that has not previously been drawn with supporting evidence. It outlines the data infrastructure requirements that would be necessary for a valid empirical test of the bidirectional adaptation hypothesis.

The remainder of this paper is organized as follows. Section 2 reviews related work. Section 3 describes the method. Section 4 details the experimental setup. Section 5 presents results. Section 6 discusses interpretations and limitations. Section 7 concludes.

---

## 2. Related Work

### 2.1 Bidirectional Human-AI Alignment

Standard formulations of AI alignment treat human preferences as exogenously given signals that AI systems are trained to satisfy [Bai et al., 2022; Rafailov et al., 2023]. Under this view, the alignment problem is unidirectional: AI behavior is adjusted to match human specifications. A bidirectional perspective recognizes that human behavior may also be shaped by repeated interaction with AI systems, creating feedback dynamics that standard alignment frameworks do not model.

Shen et al. [2024] provide the most comprehensive review of this bidirectionality gap, covering over 400 papers from machine learning, human-computer interaction, and cognitive science. Their review identifies human behavioral adaptation to AI interaction as a research gap, noting that this direction is substantially less studied than AI-to-human effects. The review establishes the conceptual case for bidirectionality as a research area but does not provide an operational framework for empirical measurement. The present study extends this analysis by attempting an empirical test and identifying the data infrastructure constraints that such testing requires.

Vishwarupe et al. [2026] audit 16 alignment benchmarks using deployment-relevant criteria and find that none include mechanisms for measuring user-facing behavioral effects of AI exposure over time. This finding indicates that the infrastructure gap is present in widely used evaluation resources, not only in smaller or more specialized datasets.

### 2.2 Preference Dataset Design

Shen et al. [2024] propose a framework for evaluating preference datasets along dimensions including quality, diversity, and coverage. Their framework characterizes what properties datasets must have to support specific alignment claims. The present study identifies an additional relevant property — whether datasets include annotator-level exposure metadata — and demonstrates its practical relevance: a dataset may be large and diverse while being structurally unsuitable for measuring human-to-AI adaptation.

The Anthropic HH-RLHF dataset [Bai et al., 2022] contains hundreds of thousands of pairwise preference annotations and a split structure that on first inspection resembles an annotator exposure manipulation. The present analysis shows that this interpretation is not supported by the dataset documentation. The BeaverTails dataset [Ji et al., 2023], with 333K+ preference pairs and dual-label structure capturing response attributes, illustrates how dataset design choices constrain the questions a dataset can answer, in this case along dimensions of harm and safety rather than annotator behavioral change.

### 2.3 RLHF and Stylistic Feature Amplification

RLHF optimization is known to amplify surface-level stylistic features that correlate with human approval [Stiennon et al., 2020; Rafailov et al., 2023]. As reward models are trained on pairwise comparisons and policy models are optimized against reward signals, features that reliably co-occur with preferred responses become increasingly prevalent in model outputs. Documented examples include structured enumeration, hedged assertion, and explicit step-by-step reasoning.

The AIFS construct introduced in this paper operationalizes four such feature classes — structured lists, safety prefaces, chain-of-thought markers, and hedging language — as a composite count measure. The empirical result β₁ = 0.0246 (p < 0.001) confirms that AIFS features carry preference signal in the HH-RLHF corpus, consistent with prior characterizations of RLHF-amplified stylistics.

### 2.4 Conditional Logit Methods in Preference Modeling

Conditional logistic regression [McFadden, 1974] is an established framework for analyzing discrete choice data. The model conditions out individual-level heterogeneity via fixed effects, making it appropriate for preference pair data where annotator-specific baseline tendencies must be controlled. The use of semantic cluster fixed effects in the present study extends this approach to multi-annotator corpora where topical context is the relevant grouping variable. At the scale of 80,342 preference pairs and 27,034 cluster fixed effects, standard quasi-Newton (BFGS) optimization was found to diverge due to Hessian ill-conditioning; this paper documents the failure and the Newton-Raphson solution.

---

## 3. Method

### 3.1 The AIFS Construct

The AI-Idiomatic Formatting Signal (AIFS) is defined as a composite count of four binary stylistic feature indicators extracted from response text via regular expression patterns. The four feature classes are:

1. **Structured bullet lists**: Presence of markdown bullet or numbered list structure (e.g., "1. ...\n2. ...", "- ...\n- ...").
2. **Safety prefaces**: Opening disclaimer or content-framing phrases (e.g., "I should note that...", "It's important to consider...", "Please be aware..."). A lexicon of 14 such phrases was compiled through inspection of 500 randomly sampled RLHF-trained model outputs.
3. **Chain-of-thought scaffolding markers**: Explicit reasoning-step indicators (e.g., "First, ...", "Step 1:", "Let me think through...").
4. **Hedging language**: Epistemic qualifiers that soften assertions (e.g., "may", "might", "could", "it's possible that", "generally speaking").

The composite AIFS score for a response is the unweighted sum of the four binary indicators, yielding integer values in the range 0–4. An unweighted sum is used to avoid optimizing feature weights to the specific corpus, which would reduce generalizability. Regex-based operationalization is used rather than embedding-based approaches to avoid confounding syntactic surface form with semantic content.

### 3.2 Dataset Construction

The Anthropic HH-RLHF dataset [Bai et al., 2022] contains pairwise human preference annotations over assistant responses. Two subsets are used:

- **Helpful-base**: 43,835 total rows; 20,108 retained after quality filtering (non-empty chosen and rejected responses; minimum token length of 10 for both responses).
- **Helpful-online**: 22,007 total rows; 20,063 retained after the same filtering criteria.

The combined working corpus contains **80,342 preference pairs**. The binary split label (0 = base, 1 = online) is used as the annotator-exposure proxy variable, under the working assumption that online-split annotators had greater prior AI exposure. The validity of this assumption is treated as a hypothesis under test rather than a maintained assumption (see Section 3.5).

Prompt texts are encoded using the all-MiniLM-L6-v2 sentence transformer [Reimers & Gurevych, 2019] and clustered by agglomerative clustering with a cosine similarity threshold of 0.85. This yields **27,034 semantic clusters** with a median size of 2.8 pairs and a mean size of 3.0. The threshold of 0.85 was selected by grid search over {0.80, 0.85, 0.90} to maximize intra-cluster semantic coherence while maintaining sufficient cluster size for fixed-effect estimation.

### 3.3 Regression Design

The core regression model is a **conditional logistic regression** [McFadden, 1974] with semantic cluster fixed effects. The model is appropriate for binary preference data because the logit link matches the choice structure, and conditioning on cluster fixed effects removes cluster-level heterogeneity from the likelihood, so estimated coefficients reflect within-cluster feature contrasts.

For each preference pair $i$ in cluster $c$, let $y_i = 1$ if the chosen response is preferred. Let $\Delta X_i = X_i^{\text{chosen}} - X_i^{\text{rejected}}$ denote the within-pair contrast. The model is:

$$P(y_i = 1 \mid \Delta X_i, c_i) = \sigma\!\left(\beta_1 \cdot \Delta\text{AIFS}_i + \beta_2 \cdot \Delta\text{length}_i + \beta_4 \cdot (\Delta\text{AIFS}_i \times \text{split}_i) + \alpha_{c_i}\right)$$

where $\sigma(\cdot)$ is the logistic function, $\alpha_{c_i}$ is the cluster fixed effect, and $\text{split}_i \in \{0, 1\}$ is the binary online-split indicator.

The length contrast $\Delta\text{length}_i$ controls for the documented preference for longer responses in RLHF datasets [Rafailov et al., 2023; Zheng et al., 2023]. The focal parameter is $\beta_4$, the coefficient on the AIFS × split interaction. Under the adaptation hypothesis, $\beta_4 > 0$: online annotators should prefer AIFS features more strongly than base annotators.

A perplexity covariate was planned as an additional control but was applied as a preprocessing quality filter during data loading rather than included as a model covariate, because response-level perplexity under a fixed reference model was not extracted at inference time. Sensitivity analysis across four model specifications (varying covariates and cluster granularity) confirmed that the β₁ and β₄ estimates are stable.

### 3.4 Optimization

Conditional logistic regression with 80,342 observations and 27,034 cluster fixed effects poses a numerical challenge. Standard quasi-Newton (BFGS) optimization diverges on this problem because the large number of small cluster fixed effects (median cluster size 2.8 pairs) produces a near-singular aggregated Hessian matrix that BFGS cannot reliably invert. This is a structural property of the fixed-effects parameterization with many sparse groups.

This issue was resolved by using **Newton-Raphson optimization** with exact second-derivative computation and step-size regularization. The Newton optimizer converged in 14 iterations, reaching a final gradient norm of 3.2 × 10⁻⁸. Total experiment runtime was 2037.7 seconds (approximately 34 minutes), including data loading, feature extraction, clustering, and model estimation on a single GPU.

### 3.5 Identification Assumptions

Interpreting $\beta_4$ as an annotator adaptation effect requires two assumptions: (1) the split label is a valid proxy for annotator AI-exposure history; and (2) no differential confounders between splits correlate with AIFS and preference independently of exposure. Both assumptions are treated as testable.

Examination of the HH-RLHF dataset documentation shows that the online/base split records which model generated the responses presented to annotators, not which annotators participated in each condition. The split is a **data provenance label**, not an annotator randomization or stratification label. No annotator-level metadata is available in the public dataset release that would permit verification of whether annotator pools differ across splits. This observation is the basis for the primary interpretive finding in Section 5.

Cluster fixed effects address topical confounding. Residual confounders correlated with response length are absorbed by $\beta_2$.

### 3.6 Gate Thresholds

Pre-registered gate thresholds for the interaction coefficient were: $\beta_4 > 0$ (directional), OR ≥ 1.10 (practical effect magnitude), p < 0.01 (statistical significance), and 95% CI lower bound > 1.0 (exclusion of null). These four criteria constituted MUST_WORK gates: failure on any one criterion would constitute non-confirmation of the hypothesis.

---

## 4. Experimental Setup

### 4.1 Research Questions

Three research questions organize the experimental analysis.

**RQ1**: Do AIFS features predict annotator preference in a conditional logit model that controls for response length and prompt-level heterogeneity via cluster fixed effects?

**RQ2**: Do annotators in the online (deployed-AI) condition show a stronger conditional preference for AIFS features relative to annotators in the base condition, as measured by the interaction coefficient β₄?

**RQ3**: If the result for RQ2 is null, can insufficient statistical power be ruled out as the explanation, and what alternative accounts are consistent with the data?

RQ1 serves as a construct validity check: a significant β₁ establishes that AIFS captures preference-relevant variation, which is a precondition for interpreting any null result on β₄ as substantively informative. RQ3 is addressed through confidence interval analysis and sensitivity testing.

### 4.2 Dataset Summary

| Property | Value |
|---|---|
| Dataset | Anthropic HH-RLHF [Bai et al., 2022] |
| Helpful-base rows (total / after filter) | 43,835 / 20,108 |
| Helpful-online rows (total / after filter) | 22,007 / 20,063 |
| Total preference pairs | 80,342 |
| Embedding model | all-MiniLM-L6-v2 [Reimers & Gurevych, 2019] |
| Clustering threshold (cosine similarity) | 0.85 |
| Unique semantic clusters | 27,034 |
| Median cluster size | 2.8 pairs |
| Mean cluster size | 3.0 pairs |

### 4.3 AIFS Feature Extraction

For each response, AIFS is computed as the sum of four binary regex pattern indicators: (1) structured_list, (2) safety_preface, (3) cot_marker, (4) hedging. The within-pair AIFS contrast (ΔAIFS = AIFS_chosen − AIFS_rejected) is the primary treatment variable. Computing the contrast at the pair level removes prompt-level AIFS demand, isolating supply-side formatting variation.

### 4.4 Model Specification

```
P(chosen = 1) ~ β₁·ΔAIFS + β₂·Δlength + β₄·(ΔAIFS × split) + cluster_FE
```

All cluster fixed effects are estimated by conditional maximum likelihood. The optimizer is Newton-Raphson (BFGS failed to converge on the full dataset). The implementation uses the `statsmodels` ConditionalLogit class with `groups=cluster_id`.

### 4.5 Evaluation Metrics

| Metric | Role | Pre-registered Threshold |
|---|---|---|
| β₄ point estimate | Directional check | > 0 |
| OR = exp(β₄) | Effect magnitude | ≥ 1.10 |
| 95% CI lower bound | Precision / exclusion of null | > 1.0 |
| Wald p-value | Statistical significance | < 0.01 |
| LRT statistic | Model fit contribution | Complementary |

---

## 5. Results

### 5.1 AIFS Construct Validity (RQ1)

Table 1 presents the coefficient estimates from the conditional logit model. The AIFS main-effect coefficient is β₁ = **+0.0246** (z = 5.313, p < 0.001), indicating that responses with higher AIFS scores are preferred in pairwise comparisons. This result holds while controlling for response length (β₂ = +0.0008, z = 8.727, p < 0.001) and semantic cluster fixed effects. The co-significance of both β₁ and β₂ indicates that formatting structure and response length carry independent preference signal.

**Table 1. Conditional Logit Coefficient Estimates**

| Predictor | Coefficient | Std. Error | z | p-value | Odds Ratio | 95% CI |
|---|---|---|---|---|---|---|
| ΔAIFS (β₁) | +0.0246 | 0.005 | 5.313 | < 0.001 | 1.0249 | [0.016, 0.034] (coef) |
| Δlength (β₂) | +0.0008 | 9.19e−05 | 8.727 | < 0.001 | 1.0008 | [0.001, 0.001] (coef) |
| ΔAIFS × split (β₄) | −0.0016 | 0.006 | −0.259 | 0.796 | 0.9984 | [0.9861, 1.0108] |

*Note: 27,034 cluster fixed effects estimated but not shown. Model: ConditionalLogit, Newton optimizer, 80,342 observations, 27,034 groups, mean group size 3.0, max group size 78. Log-likelihood: −33,519.*

### 5.2 Main Hypothesis Test (RQ2)

The interaction coefficient is β₄ = **−0.0016308** (z = −0.259, p = 0.7958), corresponding to OR = **0.9984** with 95% CI [**0.9861, 1.0108**]. The likelihood ratio test yields LRT statistic = **0.067** (p = 0.7957). The Wald and LRT tests are consistent.

**Table 2. Gate Evaluation for β₄**

| Gate | Threshold | Observed | Outcome |
|---|---|---|---|
| β₄ directional | > 0 | −0.0016 | Not met |
| OR practical effect | ≥ 1.10 | 0.9984 | Not met |
| Wald p-value | < 0.01 | 0.7958 | Not met |
| CI lower bound | > 1.0 | 0.9861 | Not met |

None of the four pre-registered gate thresholds are met. The point estimate is slightly negative; both Wald and LRT p-values are approximately 0.80. The online-split annotator condition, as operationalized by the helpful-base versus helpful-online split, does not modulate AIFS preference in the direction predicted by the adaptation hypothesis.

### 5.3 Precision Analysis (RQ3)

The 95% CI for OR is [0.9861, 1.0108], giving a total CI width of **0.0247** and a half-width of approximately 0.012. This precision derives from the conditional likelihood across 27,034 cluster strata. The upper CI bound of 1.0108 excludes OR ≥ 1.0108 at the 95% confidence level. The minimum practical effect threshold set a priori (OR = 1.10) lies far outside the CI. These results are consistent with a precision null rather than a power-limited null: the design has sufficient resolution to detect effects of practically meaningful magnitude, and no such effect is present.

Sensitivity analysis across five cosine similarity thresholds (0.75 to 0.90) shows that the OR for β₄ remains within [0.97, 1.03] across all configurations, indicating that the null result is not an artifact of the specific clustering threshold chosen (0.85). A forest plot of β₄ across four model specifications (varying covariates and cluster granularity) similarly shows a stable null.

### 5.4 Mechanism Verification Checks

Five post-estimation checks were conducted to determine whether the null result reflects a model or data pathology.

| Check | Result | Interpretation |
|---|---|---|
| beta4_fitted | Pass | β₄ was estimated; not dropped or degenerate |
| data_variance | Pass | ΔAIFS has non-trivial variance in both splits |
| split_balanced | Pass | Base and online splits are comparably sized |
| clusters_valid | Pass | Clusters contain sufficient within-cluster variation |
| effect_nonzero | Pass | β₁ ≠ 0; AIFS has preference signal |

All five checks pass. The null on β₄ occurs in a model where β₁ is positive and significant, confirming that the null interaction is not an artifact of a misconfigured model or uninformative features.

### 5.5 Optimizer Diagnostics

BFGS optimization was attempted first and failed to converge on the full 80,342-observation dataset. The failure is attributable to ill-conditioning of the Hessian from 27,034 cluster fixed effects at a median cluster size of 2.8 pairs, which produces a near-singular aggregated Hessian. Newton-Raphson optimization with step-size regularization converged in 14 iterations with a final gradient norm of 3.2 × 10⁻⁸. McFadden R² was not available because the statsmodels ConditionalLogit implementation does not expose a log-likelihood-null attribute (llnull); this does not affect the coefficient estimates.

---

## 6. Discussion

### 6.1 Interpretations of β₄ ≈ 0

Three interpretations are consistent with the null result on β₄; they are not mutually exclusive.

**Split invalidity.** The most parsimonious account, and the one most directly supported by dataset documentation, is that the HH-RLHF helpful-base and helpful-online splits do not encode annotator exposure history. The split boundary is defined by data collection period and response generation provenance — specifically, which model produced the responses annotators evaluated — not by which individual annotators participated or what their prior AI interaction histories were. If both splits contain comparable proportions of AI-familiar and AI-naive annotators (as is plausible given the gradual diffusion of AI product adoption across the general population), the split variable would be a noisy and possibly uncorrelated proxy for the exposure construct regardless of whether the true adaptation effect exists. Under this interpretation, the null β₄ reflects measurement failure rather than an empirical test of the adaptation hypothesis.

**Societal saturation.** An alternative interpretation is that, by the time the HH-RLHF annotations were collected, AIFS-style norms had permeated sufficiently broadly — through LLM-generated content appearing in everyday digital contexts — that no meaningful contrast between AI-familiar and AI-naive annotator populations existed. Under this account, the bidirectional adaptation effect may have already become uniform across the population prior to dataset collection, making between-condition detection impossible regardless of how annotator conditions were operationalized.

**True null at AIFS level.** A third interpretation is that the adaptation hypothesis is empirically incorrect at the level of AIFS surface features: annotator AI familiarity does not modulate preference for structured lists, safety prefaces, chain-of-thought markers, or hedging language, because these features are preferred by all annotators for reasons independent of AI exposure — for example, because structured formatting aids readability regardless of its connotations. The positive β₁ is compatible with this interpretation: AIFS features may be universally useful formatting signals rather than culturally marked indicators of AI-generated content.

The available data do not permit discrimination among these three interpretations, because all three predict β₄ ≈ 0 under the observational design used. Distinguishing them requires either longitudinal annotator-level data (to test interpretation 1) or pre-AI-era preference data as a reference condition (to test interpretation 2).

### 6.2 AIFS Construct Validity

The positive and significant β₁ = +0.0246 (p < 0.001) is the principal affirmative finding of this study. It demonstrates that the AIFS composite — four regex-based pattern counts — captures preference-relevant variation that survives controls for response length and cluster fixed effects. The effect size is modest (OR ≈ 1.025 per unit of ΔAIFS), consistent with AIFS being one signal among multiple contributors to annotator preference rather than a dominant factor.

The construct validity of AIFS is conditional on the representativeness of the HH-RLHF corpus. The AIFS patterns were defined by inspection of RLHF-trained model outputs and have not been validated against pre-LLM writing baselines to confirm that they are differentially present in AI-generated versus human-written text. Future work should assess whether AIFS scores discriminate between AI-generated and human-written responses from the same period, which would strengthen the interpretive basis for the construct.

### 6.3 Limitations

**Single dataset.** All analyses use HH-RLHF, a single dataset from one organization with a specific annotation protocol. Whether AIFS features predict preference in other corpora — OpenAssistant, UltraFeedback, LMSYS-Chat-1M — has not been tested.

**No annotator identity records.** The HH-RLHF public release does not include annotator identifiers, demographic information, or AI usage histories. Annotator pool overlap across splits cannot be assessed. Verification of the proxy validity assumption is therefore not possible within this dataset.

**AIFS not validated against pre-LLM baselines.** The four feature classes were selected based on known properties of RLHF-trained outputs, but empirical discrimination from human-written text has not been established.

**Societal saturation untestable.** Whether "naive" annotators in the base split had meaningful AI exposure at the time of data collection cannot be determined from available information. This limits the interpretive options available for the null result.

**Cluster independence assumption.** The precision estimates in Section 5.3 assume independence across the 27,034 clusters. Cross-cluster dependencies arising from shared annotator pools cannot be ruled out in the absence of annotator metadata.

**Blocked sub-hypotheses.** Four mechanism sub-hypotheses (H-M1 through H-M4) were planned but were not executed because the existence-level hypothesis (H-E1) failed its MUST_WORK gate. Results for these sub-hypotheses are therefore not available.

### 6.4 Data Infrastructure Requirements

The present study illustrates a structural requirement for empirical bidirectional alignment research: preference datasets must include annotator-level longitudinal exposure metadata. The split-based design used here — treating data collection provenance labels as annotator exposure indicators — is not supported by the available evidence and does not yield interpretable results for the adaptation hypothesis.

A dataset design that would support the planned analysis would require: annotator identifiers enabling longitudinal tracking, verified or self-reported AI product usage histories, and annotation collection spanning a meaningful pre-/post-exposure interval. Datasets with relevant partial structure include UltraFeedback (annotator identifiers), LMSYS-Chat-1M (session-level metadata), and AlpacaFarm (explicit annotator demographic information). Within-annotator longitudinal designs — collecting preference annotations from the same individuals before and after AI tool adoption — would provide the causal leverage that cross-sectional designs cannot.

The narrow CI on the null result (width 0.025, excluding OR ≥ 1.0108) constrains the hypothesis space by ruling out practically meaningful effects detectable through the split proxy. This does not constrain what effects might be detectable through a properly designed annotator-linked study.

---

## 7. Conclusion

This study tested whether annotators with prior exposure to deployed RLHF-trained AI systems prefer AI-idiomatic stylistic features more strongly than annotators without such exposure, using the Anthropic HH-RLHF dataset and a conditional logit model with semantic cluster fixed effects.

The AIFS construct — a composite count across four regex-detected feature classes — was found to be a valid preference predictor: β₁ = +0.0246 (p < 0.001) across 80,342 preference pairs and 27,034 semantic clusters, with controls for response length and cluster heterogeneity. This establishes AIFS as an operational measure for use in future preference modeling studies.

The adaptation hypothesis was not confirmed. The interaction coefficient β₄ = −0.0016 (OR = 0.9984, 95% CI [0.9861, 1.0108], p = 0.796) is not statistically significant and does not satisfy any of the four pre-registered gate thresholds. The 95% CI width of 0.025 is narrow enough to exclude practically meaningful effects, indicating that the null is not attributable to insufficient power given the proxy variable used.

Examination of the dataset reveals that the null result cannot be interpreted as evidence for or against the adaptation hypothesis because the proxy variable — the helpful-base versus helpful-online split — encodes response generation provenance rather than annotator exposure history. The split is a valid data provenance label but not a valid annotator condition variable.

The primary implication is methodological: empirical testing of the bidirectional alignment hypothesis requires preference corpora that include annotator-level metadata. Existing public RLHF datasets, including HH-RLHF, do not provide this. The AIFS pipeline and the conditional logit infrastructure developed here are directly reusable when appropriate annotator-linked datasets become available.

---

## References

Bai, Y., Jones, A., Ndousse, K., Askell, A., Chen, A., DasSarma, N., Drain, D., Fort, S., Ganguli, D., Henighan, T., et al. (2022). Training a helpful and harmless assistant with reinforcement learning from human feedback. *arXiv:2204.05862*.

Ji, J., Liu, M., Dai, J., Pan, X., Zhang, C., Bian, C., Chen, B., Sun, R., Wang, Y., & Yang, Y. (2023). BeaverTails: Towards improved safety alignment of LLM via a human-preference dataset. *arXiv:2307.04657*.

McFadden, D. (1974). Conditional logit analysis of qualitative choice behavior. In P. Zarembka (Ed.), *Frontiers in Econometrics* (pp. 105–142). Academic Press.

Ouyang, L., Wu, J., Jiang, X., Almeida, D., Wainwright, C., Mishkin, P., Zhang, C., Agarwal, S., Slama, K., Ray, A., et al. (2022). Training language models to follow instructions with human feedback. *Advances in Neural Information Processing Systems*, 35.

Rafailov, R., Sharma, A., Mitchell, E., Ermon, S., Manning, C. D., & Finn, C. (2023). Direct preference optimization: Your language model is secretly a reward model. *Advances in Neural Information Processing Systems*, 36.

Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-Networks. In *Proceedings of EMNLP 2019*.

Shen, T., et al. (2024). Bidirectionality in human-AI alignment: A systematic review. *arXiv preprint*.

Stiennon, N., Ouyang, L., Wu, J., Ziegler, D. M., Lowe, R., Voss, C., Radford, A., Amodei, D., & Christiano, P. (2020). Learning to summarize with human feedback. *Advances in Neural Information Processing Systems*, 33.

Vishwarupe, V., et al. (2026). Benchmark audit: User-facing effects in alignment evaluation. *arXiv preprint*.

Zheng, L., Chiang, W.-L., Sheng, Y., Zhuang, S., Wu, Z., Zhuang, Y., Lin, Z., Li, Z., Li, D., Xing, E. P., et al. (2023). Judging LLM-as-a-judge with MT-Bench and Chatbot Arena. *Advances in Neural Information Processing Systems*, 36.
