# Research Proposal: Privacy Compliance Argumentation Framework: Mapping Differential Privacy Parameters to GDPR Principles

## 1. Introduction

### 1.1 Background

The proliferation of machine learning (ML) systems trained on large-scale datasets has created unprecedented challenges at the intersection of technical privacy guarantees and regulatory compliance. Organizations deploying ML models in the European Union must navigate the General Data Protection Regulation (GDPR), which establishes qualitative principles such as data minimization (Article 5(1)(c)), purpose limitation (Article 5(1)(b)), and storage limitation (Article 5(1)(e)). Simultaneously, differential privacy (DP) has emerged as the gold standard for providing mathematically rigorous privacy guarantees, characterized by parameters $\varepsilon$ (privacy budget) and $\delta$ (failure probability).

Despite significant advances in both domains, a critical gap persists: there exists no systematic methodology to translate DP's quantitative guarantees into GDPR's qualitative compliance requirements. Practitioners currently rely on ad-hoc expert judgment when arguing that a differentially private ML model satisfies regulatory obligations. This disconnect creates substantial legal uncertainty, as organizations cannot demonstrate with formal rigor how their technical privacy measures align with regulatory expectations.

The tension between these paradigms is well-documented. Cummings and Desai (2018) advocate differential privacy as a preferred method for GDPR-compliant machine learning, yet Khalid (2023) demonstrates that formal privacy definitions for GDPR lack quantitative DP mapping. The GDPR is intentionally principle-based and qualitative, while DP provides mathematical guarantees that are inherently quantitative. This epistemological divide has hindered responsible AI deployment in regulated jurisdictions.

### 1.2 Research Objectives

This research proposes the **Privacy Compliance Argumentation Framework (PCAF)**, which introduces **Privacy Compliance Indicators (PCIs)** that formally map DP parameters to GDPR principles through information-theoretic bounds. The primary objectives are:

1. **Develop a formal mapping methodology** that translates $\varepsilon/\delta$ parameters into three PCIs corresponding to data minimization (PCI-DM), purpose limitation (PCI-PL), and storage limitation (PCI-SL).

2. **Establish context-sensitive threshold recommendations** with confidence intervals across three data sensitivity profiles (Low/Medium/High) aligned with GDPR Article 9 categories.

3. **Generate structured compliance arguments** that provide auditable, quantified reasoning for regulatory review while explicitly acknowledging interpretive uncertainties.

4. **Validate the framework** through expert evaluation, targeting $\geq 70\%$ acceptance rate for generated compliance arguments among privacy law specialists.

### 1.3 Research Significance

This research addresses a fundamental barrier to responsible AI deployment in regulated environments. By providing systematic methods to bridge technical privacy budgets and regulatory language, PCAF enables:

- **Auditable compliance reasoning**: Organizations can demonstrate how specific $\varepsilon$ values support GDPR principle adherence with quantified uncertainty.
- **Reduced legal uncertainty**: Practitioners gain structured guidance rather than relying on informal recommendations.
- **Interdisciplinary dialogue**: The framework creates a common vocabulary for technical and legal stakeholders.
- **Scalable compliance assessment**: Automated PCI computation enables efficient evaluation across multiple deployment scenarios.

Importantly, PCAF explicitly provides "argumentation support" rather than certification, acknowledging the inherently interpretive nature of legal compliance while maintaining scientific rigor about uncertainties.

---

## 2. Methodology

### 2.1 Theoretical Foundation

#### 2.1.1 Differential Privacy Preliminaries

A randomized mechanism $\mathcal{M}$ satisfies $(\varepsilon, \delta)$-differential privacy if for all adjacent datasets $D, D'$ differing in one record and all measurable sets $S$:

$$\Pr[\mathcal{M}(D) \in S] \leq e^{\varepsilon} \cdot \Pr[\mathcal{M}(D') \in S] + \delta$$

The privacy budget $\varepsilon$ bounds the log-likelihood ratio of outputs, while $\delta$ represents the probability of privacy failure. For ML training, DP-SGD (Abadi et al., 2016) provides per-iteration privacy guarantees composed via the moments accountant:

$$\varepsilon_{\text{total}} = \sqrt{2T \log(1/\delta)} \cdot \sigma^{-1} + T/(e^{\sigma^2/2} - 1)$$

where $T$ is the number of training iterations and $\sigma$ is the noise multiplier.

#### 2.1.2 Information-Theoretic Interpretation

The core insight enabling PCI construction is that $\varepsilon$ directly bounds the information gain an adversary can obtain about any individual record. Specifically, for any prior distribution $\pi$ over individual participation and posterior $\pi'$ after observing mechanism output:

$$D_{\text{KL}}(\pi' \| \pi) \leq \varepsilon$$

This information-theoretic bound provides the foundation for translating DP guarantees into GDPR-aligned metrics.

### 2.2 Privacy Compliance Indicators (PCIs)

We define three PCIs that operationalize GDPR principles through information-theoretic bounds derived from DP parameters.

#### 2.2.1 PCI-DM: Data Minimization Indicator

GDPR Article 5(1)(c) requires that personal data be "adequate, relevant and limited to what is necessary." We operationalize this through the information gain bound:

$$\text{PCI-DM}(\varepsilon, s) = 1 - \frac{\min(\varepsilon, \varepsilon_{\max}(s))}{\varepsilon_{\max}(s)}$$

where $s \in \{\text{Low}, \text{Medium}, \text{High}\}$ denotes the data sensitivity level and $\varepsilon_{\max}(s)$ represents the maximum acceptable privacy budget for sensitivity level $s$. Based on NIST SP 800-226 guidelines and Li et al. (2021) practical ranges:

$$\varepsilon_{\max}(s) = \begin{cases} 8.0 & \text{if } s = \text{Low} \\ 4.0 & \text{if } s = \text{Medium} \\ 1.0 & \text{if } s = \text{High} \end{cases}$$

PCI-DM $\in [0, 1]$ where higher values indicate stronger data minimization alignment.

#### 2.2.2 PCI-PL: Purpose Limitation Indicator

GDPR Article 5(1)(b) requires data collection for "specified, explicit and legitimate purposes." We operationalize this through membership inference attack success probability bounds. For an $(\varepsilon, \delta)$-DP mechanism, the advantage of any membership inference adversary is bounded by:

$$\text{Adv}_{\text{MI}} \leq e^{\varepsilon} - 1 + \delta$$

We define:

$$\text{PCI-PL}(\varepsilon, \delta) = 1 - \min\left(1, \frac{e^{\varepsilon} - 1 + \delta}{\tau_{\text{PL}}}\right)$$

where $\tau_{\text{PL}} = 0.5$ represents the threshold above which purpose limitation is considered violated (adversary gains significant advantage for unauthorized inference).

#### 2.2.3 PCI-SL: Storage Limitation Indicator

GDPR Article 5(1)(e) requires data be "kept for no longer than is necessary." For ML models, this relates to temporal privacy budget accumulation under composition. For $k$ queries or model updates:

$$\varepsilon_{\text{composed}} = \sqrt{2k \log(1/\delta)} \cdot \varepsilon$$

We define:

$$\text{PCI-SL}(\varepsilon, k, T_{\max}) = 1 - \frac{\min(\varepsilon_{\text{composed}}, \varepsilon_{\max})}{\varepsilon_{\max}} \cdot \frac{k}{T_{\max}}$$

where $T_{\max}$ represents the maximum intended retention period in query/update units.

### 2.3 Threshold Recommendation Engine

The threshold recommendation engine aggregates PCI scores with sensitivity-level context to produce $\varepsilon$ ranges rather than point estimates.

#### 2.3.1 Aggregate PCI Score

$$\text{PCI}_{\text{agg}}(\varepsilon, \delta, s, k) = w_{\text{DM}} \cdot \text{PCI-DM} + w_{\text{PL}} \cdot \text{PCI-PL} + w_{\text{SL}} \cdot \text{PCI-SL}$$

where weights $w_{\text{DM}}, w_{\text{PL}}, w_{\text{SL}}$ are calibrated per sensitivity profile:

| Sensitivity | $w_{\text{DM}}$ | $w_{\text{PL}}$ | $w_{\text{SL}}$ |
|-------------|-----------------|-----------------|-----------------|
| Low         | 0.4             | 0.3             | 0.3             |
| Medium      | 0.35            | 0.35            | 0.3             |
| High        | 0.3             | 0.4             | 0.3             |

#### 2.3.2 Confidence Interval Generation

For a target compliance threshold $\theta$ (default $\theta = 0.7$), we compute the recommended $\varepsilon$ range:

$$[\varepsilon_{\min}, \varepsilon_{\max}] = \{\varepsilon : \text{PCI}_{\text{agg}}(\varepsilon) \geq \theta \pm \sigma_{\theta}\}$$

where $\sigma_{\theta}$ represents uncertainty derived from regulatory interpretation variance, estimated from EDPB guidance document analysis.

### 2.4 Compliance Argument Generation

Following Buscemi (2025) methodology for AI Act verification, we generate structured compliance arguments with the following components:

1. **Claim**: Statement of GDPR principle compliance
2. **Evidence**: PCI scores with mathematical derivation
3. **Warrant**: Information-theoretic justification linking DP to GDPR
4. **Backing**: References to EDPB guidance and enforcement precedents
5. **Qualifier**: Confidence level and explicit limitations
6. **Rebuttal**: Conditions under which the argument may not hold

### 2.5 Experimental Design

#### 2.5.1 Data Collection

**Synthetic Compliance Scenarios**: We construct 90 compliance scenarios (30 per sensitivity level) covering:
- Model types: Classification, regression, generative (LLMs)
- Training methods: DP-SGD, federated learning with DP, fine-tuning
- $\varepsilon$ values: Logarithmically spaced in $[0.1, 10]$
- $\delta$ values: $\{10^{-5}, 10^{-6}, 10^{-7}\}$

**EDPB Guidance Corpus**: Systematic analysis of European Data Protection Board guidance documents and Data Protection Authority enforcement decisions to extract implicit threshold patterns.

#### 2.5.2 Expert Panel Composition

We recruit a panel of $n \geq 6$ privacy law experts with:
- GDPR specialization (minimum 3 years practice)
- Experience with technology company compliance
- Geographic diversity across EU member states

#### 2.5.3 Validation Protocol

**Phase 1: PCI Decomposition Validation**
- Present experts with 30 scenarios (10 per sensitivity level)
- Experts independently assess GDPR principle alignment on 5-point Likert scale
- Compare expert ratings with PCI scores using Spearman correlation

**Phase 2: Compliance Argument Evaluation**
- Generate PCAF compliance arguments for 60 scenarios
- Generate baseline arguments using ad-hoc $\varepsilon$ selection (current practice)
- Experts evaluate arguments on:
  - Regulatory sufficiency (binary: acceptable/not acceptable)
  - Argumentation completeness (0-1 scale)
  - Practical utility (5-point Likert)
- Randomized presentation order, blinded to generation method

**Phase 3: Threshold Calibration**
- Compare PCAF threshold recommendations against EDPB implicit guidance
- Measure alignment using Cohen's $\kappa$

#### 2.5.4 Evaluation Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| Expert Acceptance Rate | Proportion of arguments rated "acceptable" | $\geq 70\%$ |
| PCI-Expert Correlation | Spearman $\rho$ between PCI scores and expert ratings | $\rho \geq 0.6$ |
| Argumentation Completeness | Proportion of required elements present | $\geq 0.8$ |
| Threshold Alignment | Cohen's $\kappa$ with EDPB guidance | $\kappa \geq 0.6$ |
| Inter-rater Reliability | Krippendorff's $\alpha$ among experts | $\alpha \geq 0.6$ |

#### 2.5.5 Statistical Analysis

**Primary Analysis**: One-sample proportion test for expert acceptance rate:
- $H_0$: Acceptance rate $\leq 0.5$ (no better than chance)
- $H_1$: Acceptance rate $\geq 0.7$
- Power analysis: $n = 60$ scenarios provides 90% power at $\alpha = 0.05$

**Comparative Analysis**: McNemar's test comparing PCAF vs. baseline acceptance rates within expert-scenario pairs.

**Mechanism Validation**: Structural equation modeling to test the 5-step causal chain:

$$\varepsilon/\delta \xrightarrow{\beta_1} \text{Info Bounds} \xrightarrow{\beta_2} \text{PCIs} \xrightarrow{\beta_3} \text{Thresholds} \xrightarrow{\beta_4} \text{Arguments} \xrightarrow{\beta_5} \text{Validation}$$

#### 2.5.6 Falsification Criteria

The hypothesis will be **rejected** if any of the following occur:
1. Expert acceptance rate $< 50\%$
2. PCI decomposition accuracy $< 60\%$ across all three indicators
3. $\geq 30\%$ of recommended $\varepsilon$ ranges contradict EDPB implicit guidance
4. Inter-rater reliability (Krippendorff's $\alpha$) $< 0.6$
5. $\geq 50\%$ of real-world use cases fall outside the three sensitivity profiles

---

## 3. Expected Outcomes

### 3.1 Primary Deliverables

1. **PCAF Framework Specification**: Complete mathematical formalization of PCIs with calibrated parameters for three sensitivity profiles.

2. **Threshold Recommendation Tables**: Validated $\varepsilon$ ranges with 95% confidence intervals for Low/Medium/High sensitivity categories across training, inference, and fine-tuning use cases.

3. **Compliance Argument Templates**: Structured templates following Buscemi methodology with explicit uncertainty quantification.

4. **Validation Results**: Empirical evidence demonstrating $\geq 70\%$ expert acceptance rate and mechanism validity.

### 3.2 Scientific Contributions

- **Novel theoretical contribution**: First formal mapping between DP parameters and GDPR principles through information-theoretic bounds.
- **Methodological contribution**: Systematic approach to translating quantitative privacy guarantees into qualitative regulatory compliance arguments.
- **Empirical contribution**: Expert-validated thresholds providing evidence-based guidance for practitioners.

### 3.3 Anticipated Limitations

1. **Interpretive nature**: PCAF provides argumentation support, not legal certification; expert review remains necessary.
2. **Regulatory evolution**: GDPR interpretation evolves; thresholds require periodic recalibration.
3. **Jurisdiction specificity**: Initial validation focuses on GDPR; extension to CCPA, LGPD requires additional work.

---

## 4. Impact

### 4.1 Practical Impact

PCAF directly addresses the operational challenge faced by organizations deploying differentially private ML models in GDPR-regulated jurisdictions. By providing:

- **Actionable guidance**: Practitioners receive specific $\varepsilon$ recommendations rather than vague "lower is better" advice.
- **Audit trails**: Generated compliance arguments create documentation for regulatory review.
- **Risk quantification**: Confidence intervals enable informed decision-making about privacy-utility tradeoffs.

### 4.2 Regulatory Impact

The framework facilitates dialogue between technical and legal communities by:

- **Establishing common vocabulary**: PCIs translate technical parameters into regulatory concepts.
- **Supporting enforcement**: Regulators gain tools to evaluate DP claims systematically.
- **Informing guidance development**: Empirical threshold validation can inform future EDPB recommendations.

### 4.3 Research Impact

PCAF opens new research directions at the intersection of privacy-preserving ML and regulatory compliance:

- **Extension to other regulations**: Methodology can be adapted for CCPA, LGPD, and emerging AI regulations.
- **Dynamic compliance monitoring**: Real-time PCI computation for deployed systems.
- **Automated compliance verification**: Integration with ML pipelines for continuous compliance assessment.

### 4.4 Broader Societal Impact

By reducing barriers to responsible AI deployment, PCAF contributes to:

- **Increased adoption of privacy-preserving techniques**: Organizations gain confidence that DP investments translate to regulatory compliance.
- **Enhanced data subject protection**: Systematic compliance argumentation strengthens accountability.
- **Innovation in regulated sectors**: Healthcare, finance, and government can deploy ML with clearer compliance pathways.

---
