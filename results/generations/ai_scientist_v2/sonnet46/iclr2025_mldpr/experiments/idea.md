## Name

dataset_usage_drift_detection

## Title

Documentation Drift: Mining the Gap Between How ML Datasets Are Documented and How They Are Actually Used

## Short Hypothesis

There exists a systematic and measurable gap between the intended use cases, scope, and constraints stated in ML dataset documentation and the actual usage patterns observed in published research — a phenomenon we call 'documentation drift.' We hypothesize that this drift is (1) widespread and quantifiable via NLP-based mining of paper corpora, (2) correlated with dataset age, popularity, and domain, and (3) predictive of downstream harms such as benchmark saturation, out-of-distribution generalization failures, and ethical misuse. Measuring and surfacing this drift automatically is the most direct way to identify datasets in need of revision, deprecation, or updated documentation, and no existing work does this at scale.

## Related Work

Existing work on dataset documentation (Gebru et al.'s Datasheets for Datasets, Bender & Friedman's Data Statements, Mitchell et al.'s Model Cards) focuses on static artifacts produced at publication time. Yang et al. (ICLR 2024) analyzed dataset cards on HuggingFace at scale but examined documentation completeness rather than the gap between documentation and actual usage. Croissant-RAI (Jain et al., 2024) provides machine-readable metadata formats but does not track usage. Work on benchmark overfitting (e.g., Recht et al. on ImageNet) identifies specific saturation cases but does not provide a general framework for detecting misuse across the dataset ecosystem. Our proposal is distinct in that it operationalizes 'documentation drift' as a measurable quantity by cross-referencing dataset documentation with NLP-extracted usage descriptions from thousands of published papers, enabling systematic, automated auditing of the entire ML dataset ecosystem.

## Abstract

ML datasets are documented at creation time with specific intended uses, population scopes, collection conditions, and known limitations. However, as datasets age and grow in popularity, they are routinely applied in contexts far removed from their original intent — used for tasks they were not designed for, applied to populations they do not represent, or treated as gold standards long after their validity has eroded. We call this phenomenon 'documentation drift' and propose the first systematic framework to detect and quantify it at scale. Our approach mines a large corpus of ML papers (via Semantic Scholar and ArXiv) to extract how datasets are actually used — including the task, domain, population, evaluation context, and claimed conclusions — and compares these extracted usage profiles against the datasets' official documentation using NLP-based semantic similarity and structured schema matching. We apply this framework to the 500 most-cited datasets on HuggingFace and OpenML, producing a 'drift score' for each dataset that quantifies the degree of documentation-usage divergence. We then analyze: (1) which dataset properties predict high drift, (2) whether drift correlates with known cases of benchmark gaming or ethical misuse, and (3) whether drift scores can automatically surface candidates for deprecation or documentation updates. Our system produces an open, continuously updated dashboard integrated with existing repositories, providing dataset maintainers and users with actionable signals about when and how datasets are being misused. This work directly addresses the need for living, usage-aware dataset documentation and provides a practical tool for improving data governance in ML.

## Experiments

1. **Corpus Construction**: Collect 50,000+ ML papers from Semantic Scholar/ArXiv that cite one of the 500 most-cited HuggingFace/OpenML datasets. Use a fine-tuned NLP pipeline (based on SciBERT or GPT-4o with structured prompts) to extract per-paper usage descriptors: task type, application domain, target population, evaluation methodology, and any stated limitations. Validate extraction quality on a 500-paper human-annotated gold set (measuring precision/recall of extracted fields).

2. **Documentation Profile Extraction**: Parse official dataset documentation (README, datasheets, dataset cards) for the same 500 datasets using the same structured schema. Compute a canonical 'intended usage profile' for each dataset.

3. **Drift Score Computation**: Define documentation drift as the semantic distance between the distribution of observed usage profiles and the intended usage profile, computed using embedding-based similarity (e.g., cosine distance in sentence-transformer space) aggregated over all citing papers. Validate this metric by checking whether known misuse cases (e.g., COMPAS used outside criminal justice, ImageNet used for medical imaging) receive high drift scores.

4. **Drift Predictor Analysis**: Fit a regression model predicting drift score from dataset properties (age, citation count, documentation completeness score from Yang et al., domain, license type). Report feature importances and statistical significance.

5. **Correlation with Known Harms**: Manually curate 50 cases of documented dataset misuse or ethical issues from the literature and check whether our drift scores rank these datasets in the top quartile (measuring AUC).

6. **Dashboard and Repository Integration**: Build an open web dashboard showing per-dataset drift scores, top divergent usage patterns, and auto-generated 'usage warnings.' Conduct a user study with 20 ML researchers to evaluate whether drift scores influence their dataset selection decisions.

## Risk Factors And Limitations

1. **NLP extraction quality**: Automatically extracting structured usage information from free-form paper text is noisy; errors in extraction could inflate or deflate drift scores. Mitigation: validate on human-annotated gold set and report confidence intervals.
2. **Documentation quality baseline**: Many datasets have sparse or vague documentation, making it hard to define a clear 'intended use' baseline. Mitigation: use documentation completeness scores and report drift only for datasets with sufficient documentation.
3. **Causal vs. correlational**: High drift scores indicate divergence but do not by themselves prove harm; some legitimate repurposing of datasets is scientifically valid. Mitigation: frame findings descriptively and use human review to distinguish harmful from benign drift.
4. **Coverage bias**: Our corpus is limited to papers indexed on Semantic Scholar/ArXiv, potentially missing grey literature and industry uses.
5. **Scalability of human validation**: The user study and gold-set annotation require significant human effort, though this is within academic lab capacity.

