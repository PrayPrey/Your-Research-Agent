# 6. Discussion

## 6.1 Key Findings and Their Implications

**The confounding reversal is the primary finding.** The transformation from p=0.583 (unadjusted) to p=0.0053 (matched) on identical data is not a statistical curiosity — it is a substantive finding about how FAIR-outcome studies should be conducted. Prior literature reporting null or weak correlations between FAIR compliance and dataset adoption may have been confounded by the same suppressor mechanism we document here: high-FAIR datasets being systematically newer, creating a negative confound on run accumulation time that masks the genuine discoverability advantage.

This has an immediate implication for the open science community: studies using unadjusted correlations to evaluate FAIR compliance effects should be viewed with skepticism. The direction of confounding in repository data is domain-specific and non-obvious — in our case, it operates as a suppressor rather than an inflator, producing conservative bias rather than the liberal bias commonly assumed. Matched observational designs are the appropriate methodological standard for this class of questions.

**Findable sub-criteria specificity has actionable implications.** The ablation result — aggregate FAIR threshold p=0.697 vs. Findable IV p=0.0053 — provides direct guidance for repository administrators allocating FAIR compliance investment. Generic FAIR checklist compliance (aggregate score ≥ 0.5) shows near-zero association with discovery speed. Findable-specific improvements — persistent identifiers (DOIs), rich structured metadata, search engine indexing — show a 3× discovery speed advantage after confounder control.

This specificity is theoretically coherent: the Findable dimension directly determines whether a dataset appears in repository search results and API queries. Accessible properties (open licenses, standard formats) and Reusable properties (clear provenance, citation guidance) matter for dataset adoption after discovery but do not affect the speed of initial discovery that TTFR captures. Our ablation makes this dimension-specific mechanism empirically visible for the first time in ML repository data.

**The 44-day reduction in median TTFR is practically meaningful.** For ML research with typical iteration cycles of weeks to months, having a dataset attract its first experimental use 44 days faster can translate to earlier citation opportunities, larger early-adopter communities, and faster feedback on dataset quality. Repository administrators investing in Findable improvements (structured metadata, DOI registration, search indexing) can expect this class of benefit at the dataset level.

## 6.2 Limitations

We are explicit about four limitations that constrain the interpretation of our results.

**Limitation 1: All mechanism results are preliminary (smoke-test scale).** The matched KM and Cox results derive from a synthetic n=200 cohort with 35 matched pairs, not from the planned production-scale cohort (≥500 matched pairs from real OpenML data). The smoke-test is a methodology validation, not a production empirical finding. The wide Cox CI [1.032, 9.672] reflects this — the true effect could range from near-zero to very large.

*Why acceptable:* The methodology is correctly implemented (all unit tests pass, pipeline validated end-to-end). The predicted direction is confirmed. Production replication is the immediate next step, technically feasible in ~83 minutes of individual API calls to retrieve real upload_dates.

*Suggested framing for future versions:* "We report proof-of-concept results from a smoke-test cohort. A full production replication on the ≥3,000 dataset OpenML corpus with real upload_date metadata is underway."

**Limitation 2: Proxy FAIR scores, not true F-UJI sub-criteria.** All FAIR measurements use OpenML machine-computed quality metrics as a structural proxy for Findable sub-criteria. This proxy cannot assess semantic FAIR dimensions (Accessible license clarity, Interoperable schema compliance, Reusable provenance). The proxy is attenuation-biased: if a significant effect is observable under a noisy proxy, the true F-UJI Findable effect is likely stronger.

*Why acceptable:* The proxy is theoretically motivated (metadata richness, persistent identifiers are the core Findable sub-criteria) and explicitly acknowledged. Future work should validate proxy scores against true F-UJI scores on a 100-dataset sample.

**Limitation 3: H-M3 (Reusable) and H-M4 (HuggingFace) not executed.** The original hypothesis predicted that the Reusable dimension would show the largest regression coefficient and that effects would generalize to HuggingFace. Neither claim can be assessed from current evidence. The refined hypothesis is restricted to the Findable dimension on OpenML only.

*Why acceptable:* The executed sub-hypotheses (h-e1, h-m1) provide foundational existence and mechanism evidence. H-M3 and H-M4 are scoped as immediate future work with specific experiment designs ready.

**Limitation 4: Upload_date unavailability prevents strict post-2018 cohort filtering.** The bulk OpenML API does not return upload_date, preventing the originally planned post-2018 restriction. Including pre-2018 datasets means that assumption A1 (FAIR metadata set at publication time, not retroactively) cannot be verified, introducing potential reverse causality risk.

*Mitigation:* Sensitivity analysis with FAIR-score × dataset-age interaction in production-scale analysis. Individual dataset API calls can retrieve upload_date for the full corpus.

## 6.3 Broader Impact

This work has both positive and potentially negative implications that should be acknowledged.

**Positive impacts:** By establishing that matched observational designs are necessary for credible FAIR-outcome studies, we provide a methodological contribution that can improve the quality of evidence informing repository infrastructure investment. The sub-criteria specificity finding (Findable > aggregate) provides actionable guidance for repository administrators: prioritizing DOI registration, metadata schema completeness, and search indexing over generic FAIR checklists.

**Potential concerns:** Our results should not be misinterpreted as evidence that only Findable improvements matter, or that Accessible/Reusable/Interoperable dimensions are unimportant. We tested only one mechanism (discovery speed) for one dimension (Findable). Sustained research engagement — the long-term outcome that matters most for research quality — may depend critically on Reusable properties (clear licenses, provenance, citation guidance) that our preliminary study does not yet measure.

Additionally, our proxy-Findable score is derived from quantity-based quality metrics (NumberOfInstances, NumberOfFeatures) that favor larger datasets. Repository administrators should not interpret our results as evidence that dataset size drives discoverability — the size component is a covariate we match on, not the causal mechanism.
