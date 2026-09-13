# 2. Related Work

Our work sits at the intersection of three research streams: ML dataset documentation frameworks, empirical studies of documentation quality, and automated metadata analysis. We review each and identify the specific gaps our pipeline addresses.

## 2.1 Dataset Documentation Frameworks

The documentation framework literature establishes *what* should be recorded about datasets. Gebru et al. [2021] proposed **Datasheets for Datasets**, a foundational template covering seven sections (Motivation, Composition, Collection Process, Preprocessing/Cleaning/Labeling, Uses, Distribution, Maintenance) designed to facilitate informed decision-making by downstream dataset consumers. The datasheet framework has accumulated 2,689+ citations and is the primary reference for defining documentation completeness in empirical studies, including ours via the DTS section taxonomy.

Bender & Friedman [2018] introduced **Data Statements for NLP**, a domain-specific documentation standard covering speaker demographics, speech situation, and curation rationale. While tailored to NLP datasets, Data Statements overlap substantially with the Datasheets framework and inform which fields should appear in language-domain dataset cards on HuggingFace Hub.

Pushkarna et al. [2022] proposed **Data Cards** at Google — a structured documentation format covering dataset lifecycle facts, validated with 20+ real-world production deployments. Data Cards are the operational predecessor to HuggingFace's dataset card format, which adopted structured YAML fields for many Data Card categories in a 2021 platform update. This platform update — HuggingFace's introduction of enforced YAML card structure — is central to the causal research agenda we outline in Section 6.

The Data Transparency Scorecard [Rondina et al., 2025], the documentation framework most directly relevant to our work, operationalizes the Datasheets taxonomy into a 6-section rubric (Motivation, Composition, Collection, Preprocessing, Uses, Distribution) with inverse-frequency weights derived from empirical section rarity across 100 manually-scored datasets. The DTS weights reflect a key insight: sections that are rarely filled in (Collection: weight 2.1, Preprocessing: 1.8) are more informative about documentation effort than universally-present sections (Motivation: 1.0, Distribution: 0.7). We adopt the DTS framework directly and extend its measurement from manual small-N to automated population-scale.

**Gap addressed:** These frameworks specify *what* to document but do not measure compliance at scale. No prior framework paper produces automated cross-repository scoring.

## 2.2 Empirical Studies of Documentation Quality

The empirical literature establishes the *scale* of documentation gaps. Paullada et al. [2021] surveyed limitations of predominant dataset development and use practices in ML research, finding widespread documentation gaps, bias in dataset reuse, and a "data culture" that undervalues documentation investment. Sambasivan et al. [2021] conducted interviews with 53 AI practitioners in three countries, finding that 92% experienced compounding negative effects from poor data quality — which they term "Data Cascades." A root cause they identify is the organizational incentive structure: "Everyone wants to do the model work, not the data work," leading to systematic underinvestment in documentation.

Koch et al. [2021] analyzed dataset usage patterns across ML research communities from 2015–2020, finding increasing concentration on a small number of benchmark datasets and strong influence of institutional prestige on dataset adoption. Their quantitative methodology — measuring dataset reuse via reference counts — provides the methodological precedent for the usage prediction analysis (H-M3) in our future work agenda.

Rondina et al. [2025] is the most direct predecessor to our work. They manually scored 100 datasets from four repositories (HuggingFace Hub, OpenML, Kaggle, UCI) using the DTS rubric, finding that HuggingFace datasets achieve higher completeness than OpenML and UCI, and that the DTS Preprocessing and Collection sections show the lowest coverage across all repositories. Our automated pipeline is designed to verify and extend these findings to the population scale.

**Gap addressed:** Existing empirical studies are limited by manual scoring (restricted to N≤100 for DTS-based analysis) or single-repository scope. No cross-repository automated study applies DTS inverse-frequency weighting.

## 2.3 Automated Metadata Analysis

The most related automated analysis is Oreamuno et al. [2024], who performed binary field presence checks on 6,758 HuggingFace Hub dataset cards, finding that 71.52% of cards have substantial undocumented sections. However, their analysis is (1) single-repository — HuggingFace Hub only — and (2) unweighted — all fields receive equal weight regardless of their importance in the DTS framework. Treating "task_categories" (low DTS weight: 1.0) identically to "preprocessing_steps" (high DTS weight: 1.8) understates the severity of documentation gaps in high-priority sections.

Lhoest et al. [2021] introduced the HuggingFace `datasets` library, which includes the `card_data` structured YAML API that our pipeline queries. The structured API fields available through `card_data` define the upper bound on what automated DTS scoring from HuggingFace can measure — which is precisely the "documentation API gap" our results characterize.

Prior work on automated documentation quality assessment outside ML is also relevant. In the software documentation domain, researchers have developed automated completeness metrics for API documentation and scientific dataset README files [CITATION NEEDED — no verified Semantic Scholar match found for direct precedents]. Within ML, model card analysis tools (e.g., Mitchell et al. [2019] — Model Cards for Model Reporting) define related documentation standards for model artifacts rather than datasets.

**Gap addressed:** Oreamuno et al.'s single-repository unweighted analysis cannot characterize cross-repository patterns or section-level importance. No prior work applies DTS inverse-frequency weighting in an automated cross-repository pipeline.

## 2.4 Our Position

Our work addresses all three gaps simultaneously: we build an automated pipeline (vs. manual), apply DTS inverse-frequency weighting (vs. unweighted), and operate across three repositories (vs. single-repository). The key contribution beyond automation is the *per-section API coverage analysis* — measuring not just whether datasets are scoreable, but which DTS sections are and are not reachable through structured repository APIs. This analysis produces a finding that prior work could not observe: the documentation API gap, where sections with highest DTS importance weights are precisely the sections that structured APIs do not expose as machine-readable fields.
