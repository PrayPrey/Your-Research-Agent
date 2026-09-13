# 2. Related Work

Our work sits at the intersection of three bodies of literature: FAIR data principles and their empirical validation, dataset documentation frameworks, and observational causal inference methods applied to scientific repositories. Each body provides essential but individually insufficient context.

## 2.1 FAIR Principles and Empirical Validation

The FAIR Guiding Principles [Wilkinson et al., 2016] define four dimensions for scientific data: Findable (persistent identifiers, rich metadata), Accessible (open protocols, clear access conditions), Interoperable (standardized vocabularies, community formats), and Reusable (clear licenses, provenance, usage guidance). With over 20,000 citations, the framework has become foundational in open science. Tools such as F-UJI [Devaraju and Huber, 2021] automate FAIR compliance assessment against these criteria for general scientific repositories.

However, empirical validation of FAIR compliance effects on research outcomes remains sparse. Studies in general scientific repositories (Zenodo, Pangaea) have reported positive correlations between FAIR scores and download counts [CITATION NEEDED — general science FAIR validation], but these rely on unadjusted correlations without controlling for dataset age, institutional prominence, or domain. No prior work applies matched observational designs to isolate FAIR sub-criteria effects, and no study targets ML-specific repositories where the relationship between discoverability and research engagement has distinct dynamics (run counts, model adoption, benchmark use).

Our work is the first to apply propensity-matched survival analysis to FAIR-outcome questions in ML repositories, revealing that the confounding structure in this domain produces suppressor bias rather than the inflation commonly assumed.

## 2.2 Dataset Documentation Frameworks

The dataset documentation literature [Gebru et al., 2021; Pushkarna et al., 2022] has established qualitative frameworks for what information datasets should include: intended use, collection methodology, demographic representation, and known limitations. Datasheets for Datasets [Gebru et al., 2021] defines documentation dimensions and has been widely adopted as a reporting standard, particularly at NeurIPS and ICML. Data Cards [Pushkarna et al., 2022] operationalize similar dimensions for the HuggingFace platform.

Pineau et al. [2020] linked reproducibility checklists to paper-level reproducibility outcomes, demonstrating that documentation practices correlate with downstream research quality. However, this work operates at the paper level rather than the dataset level and does not measure repository engagement trajectories.

Critically, these frameworks define *what* to document but do not provide large-scale empirical evidence that documentation completeness *causes* higher research adoption. Our work addresses this causal gap specifically for the FAIR Findable dimension, which most directly captures the discoverability properties relevant to initial dataset adoption.

## 2.3 Repository Infrastructure and Usage Analysis

Vanschoren et al. [2014, 2019] introduced OpenML as a collaborative platform for sharing datasets, tasks, flows, and experimental runs. OpenML's structured run history — recording algorithm, hyperparameters, and results for each experimental run — provides a uniquely reliable proxy for deliberate research engagement, more so than download counts which conflate casual access with active use.

The HuggingFace Dataset Hub [Lhoest et al., 2021] provides a parallel infrastructure for NLP and vision datasets, with structured card metadata enabling programmatic access to documentation completeness scores. Together, OpenML and HuggingFace represent the two largest public ML dataset repositories with accessible metadata APIs, making them natural targets for large-scale FAIR-outcome studies.

Prior analyses of OpenML usage patterns have characterized dataset popularity and task diversity [CITATION NEEDED — OpenML usage analysis], but none have applied FAIR scoring to predict engagement trajectories. Our work introduces FAIR sub-criteria scores as a new independent variable in OpenML outcome analysis.

## 2.4 Observational Causal Inference in Data Science

Propensity score matching [Rosenbaum and Rubin, 1983] was developed for observational studies where random assignment to treatment is infeasible. By matching treated and control units on estimated propensity scores (probability of treatment given covariates), it creates pseudo-experimental conditions where confounders are balanced. This method is standard in epidemiology for drug efficacy studies and has been increasingly applied in social science and economics.

In data science contexts, propensity matching has been applied to study platform design effects [CITATION NEEDED] and recommendation system interventions, but its application to dataset repository studies is novel. The key methodological insight motivating our design is that FAIR compliance assignment is not random — it correlates with dataset age, institutional origin, and domain — creating confounders that must be explicitly controlled.

Kaplan-Meier survival analysis [Kaplan and Meier, 1958] and Cox proportional hazards regression [Cox, 1972] provide complementary tools for time-to-event outcomes. Applied to time-to-first-run as our primary outcome, they capture the discovery dynamics of datasets over their lifetime rather than static engagement levels, which is more appropriate for studying the *friction reduction* mechanism that FAIR compliance theoretically provides.

## 2.5 Positioning

Our work differs from prior FAIR-outcome studies by: (1) applying matched observational design rather than unadjusted correlations, (2) targeting ML-specific repositories with run-count DVs rather than generic download counts, (3) disaggregating FAIR sub-criteria to identify which dimension drives adoption, and (4) explicitly characterizing the suppressor confounding structure that makes unadjusted analysis misleading. The combination of these four elements — matched design, ML-specific DVs, sub-criteria disaggregation, and confounding characterization — constitutes our methodological contribution to FAIR empirical validation.
