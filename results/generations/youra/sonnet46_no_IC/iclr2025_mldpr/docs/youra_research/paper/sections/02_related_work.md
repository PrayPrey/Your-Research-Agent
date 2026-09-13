# Related Work

Our contribution sits at the intersection of three bodies of work: the FAIR data principles and their operationalization, empirical studies of ML dataset adoption and metadata quality, and statistical methods for count-outcome regression in platform data. We review each in turn, demonstrating where existing work is insufficient and how our approach addresses those gaps.

## 2.1 FAIR Data Principles and Keyword Findability

The FAIR Guiding Principles [Wilkinson et al., 2016] established a widely adopted framework for scientific data management, organizing requirements around four properties: Findability (F), Accessibility (A), Interoperability (I), and Reusability (R). The F1 sub-principle — that data should be assigned globally unique and persistent identifiers and described with rich machine-actionable metadata — is the most directly operationalizable in the ML repository context via keyword tagging. With over 15,976 citations, the Wilkinson et al. framework has had substantial influence on repository design and dataset curation policy.

However, the FAIR literature has remained primarily normative. Papers describe what good metadata looks like and propose compliance checklists, but rarely measure the quantitative effect of specific FAIR F1 interventions on dataset adoption outcomes. The Croissant-RAI specification [Jain and Vanschoren, 2024] — developed in part by OpenML's founder — proposes machine-readable structured metadata for ML datasets and identifies keyword tags as a primary findability mechanism, but does not provide empirical IRR estimates. Similarly, Trišović et al. [2025] study automated FAIR compliance scoring but measure compliance richness rather than adoption outcomes. Our work fills this gap: we provide the first negative binomial regression IRR for keyword tag presence → ML task registration on a major ML platform.

## 2.2 ML Dataset Adoption and Metadata Quality

The closest empirical analogs to our work are studies relating dataset metadata to adoption or engagement on ML platforms.

Yang et al. [2024] study the relationship between documentation quality (dataset cards on HuggingFace) and dataset popularity, finding that richer documentation predicts higher download counts. This is a parallel finding — structured metadata presence predicts platform adoption — but differs from our study in three important ways: the platform (HuggingFace, a model-centric platform with different search mechanics), the metadata type (free-form dataset cards rather than keyword tags), and the adoption metric (download counts rather than ML task registrations). Critically, Yang et al. do not isolate keyword tagging as a specific FAIR F1 operand, nor do they account for overdispersion in the count outcome via negative binomial regression.

Lachmuth et al. [2025] study FAIR metadata compliance and dataset reuse in the BonaRes agricultural data repository, finding that compliance predicts reuse (measured as citations in papers). This provides cross-domain corroboration of the FAIR-adoption linkage, but in a domain-specific repository with different platform mechanics and a different adoption proxy. The tag-indexed search mechanism that characterizes OpenML does not directly apply to BonaRes's search architecture.

Oreamuno et al. [2023] survey documentation practices across ML datasets and find that poor tagging leads to poor discoverability — consistent with our finding — but do not provide regression estimates. Chapman et al. [2019] survey dataset search behavior and identify keywords as the primary mechanism researchers use to discover datasets, providing theoretical grounding for our FAIR F1 mechanism hypothesis. Afzal et al. [2020] propose a data readiness framework incorporating metadata richness but focus on quality assessment rather than adoption regression.

Orr and Crawford [2024] situate ML dataset metadata in sociological context, arguing that metadata reflects curatorial effort and community norms rather than purely technical properties — a perspective consistent with our finding that tagging behavior is bimodal (all-or-nothing) on OpenML.

**What is missing:** No prior study provides an NB-2 incidence rate ratio for keyword tag presence specifically → ML task adoption, with appropriate overdispersion testing, on an ML dataset repository. Existing work either uses different platforms, different metadata types, different adoption metrics, or lacks regression-based quantification with confound controls.

## 2.3 Negative Binomial Regression for Platform Adoption

Count data regression for platform adoption outcomes requires careful model selection. Standard Poisson regression assumes mean-variance equality; real-world count outcomes like task registrations exhibit overdispersion (variance >> mean). The Negative Binomial Type 2 (NB-2) model with loglike_method='nb2' appropriately accommodates this via a quadratic variance function [Cameron and Trivedi, 1986; 2013].

The Cameron-Trivedi Lagrange multiplier test (CT LR) provides a formal test of overdispersion, with the null hypothesis that Poisson suffices. In our setting, CT LR=7,356.36 far exceeds the critical value (χ²(1)=3.84), confirming NB-2 as the appropriate model family — a necessary condition for valid IRR inference that prior ML metadata studies have not explicitly verified. Cabansag and Ntegeka [2026] demonstrate the NB-2 IRR interpretation in a related count-on-count regression context, providing methodological precedent.

**Our positioning:** We combine the FAIR F1 operationalization from Wilkinson et al. [2016] with the empirical motivation from Yang et al. [2024] and Lachmuth et al. [2025], the keyword discovery mechanism from Chapman et al. [2019], the OpenML platform context from Vanschoren et al. [2014], and the NB-2 regression methodology — filling the gap that none of the above papers individually addressed.
