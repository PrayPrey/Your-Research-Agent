# Related Work

Our work sits at the intersection of three research areas: ML reproducibility auditing, dataset documentation, and benchmark concentration. We survey each, highlighting why existing work does not address the empirical linkage we investigate.

## ML Reproducibility

Raff [2019] provided the foundational labeled corpus for ML reproducibility research: 255 top-venue papers (NeurIPS, ICML, ICLR, JMLR) from 1984–2017, each with a binary reproducibility label from manual re-implementation attempts. The corpus established that approximately 50% of papers fail independent reproduction and identified paper-level features predictive of success: pseudocode presence, equation count, hyperparameter reporting. Critically, Raff analyzed *paper-quality* features, not *dataset-quality* features — the dataset-level signals we investigate were not available from public APIs at the time of his study.

The ML Reproducibility Challenge [Pineau et al., 2021] extended this work to post-2019 papers using multi-annotator reproduction attempts. NeurIPS, ICML, and other venues have adopted reproducibility checklists [Pineau et al., 2021] requiring code submission, dataset specification, and hyperparameter reporting. These interventions are normative — they specify what *should* be done — but do not empirically test whether documentation presence predicts reproduction success. Our work provides the empirical link that would ground these normative interventions.

Gundersen and Kjensmo [2018] analyzed ML papers for reproducibility factors including experimental setup documentation. Kapoor and Narayanan [2023] identified data leakage as a systematic driver of reproducibility failure in ML across domains. Neither work connects dataset-level metadata APIs to reproducibility labels.

## Dataset Documentation

Gebru et al. [2021] introduced Datasheets for Datasets, proposing a structured documentation framework for datasets covering motivation, composition, collection process, uses, and maintenance. The Datasheets schema has been adopted as the basis for HuggingFace Hub dataset cards and is the foundation of our field-presence completeness metric. Importantly, Gebru et al. propose the schema normatively — they do not test whether dataset card completeness predicts downstream model failure.

Bender et al. [2021] ("Data Statements") and Gebru et al. [2021] both argue that documentation scope fields (intended_use, out_of_scope_use) are critical for preventing out-of-context dataset application — the mechanism we theorize predicts reproducibility failure. Our work is the first attempt to empirically test this theoretical link against a labeled outcome dataset.

YoungXinyu1802 et al. [ICLR 2024] analyzed 7,433 HuggingFace Hub dataset cards, finding improving completeness over time and identifying field-level completion rates. Their analysis covers the overall HF Hub ecosystem but does not characterize coverage for specific reproducibility corpora, does not analyze pre-2018 ML benchmark datasets, and does not connect card completeness to reproducibility outcomes. Our finding that even found HF cards average only 0.41 mean field-presence score complements their temporal analysis by revealing the thinness of retroactively-created cards for foundational benchmarks.

## Benchmark Concentration and Underspecification

D'Amour et al. [2021] introduced *underspecification* as a challenge for credibility in ML: models trained on the same data to the same accuracy may behave very differently at deployment because the training distribution fails to select among many valid predictors. Highly concentrated benchmark datasets — where the entire community has trained and evaluated on the same split — accumulate dataset-specific artifacts that models learn. D'Amour et al. do not operationalize concentration as a measurable quantity or link it to Raff's labels.

Recht et al. [2019] and Engstrom et al. [2020] demonstrated that models trained on CIFAR-10 and ImageNet show substantial accuracy drops on new test sets, consistent with artifact overfitting. These findings motivate our concentration hypothesis: high OpenML run counts as a proxy for benchmark concentration signal elevated artifact accumulation risk.

## Dataset Infrastructure for Reproducibility Studies

Vanschoren et al. [2014] introduced OpenML as a platform for systematic ML experimentation, providing per-dataset run counts and task creation timestamps. OpenML is designed for tabular, classical ML experiments and has been used extensively for AutoML benchmarking [Feurer et al., 2022]. Our work is the first to systematically quantify OpenML's coverage for a deep-learning-heavy reproducibility corpus, finding 22% coverage concentrated in classical tabular datasets — a scope limitation consistent with OpenML's documented design but previously unquantified for Raff's corpus.

Papers With Code [Stojnic et al., 2020] explicitly links ML papers to datasets, code implementations, and benchmark results across all domains. Papers With Code is used in reproducibility research (e.g., "State of ML" reports) and provides the paper-dataset linkage we require. In contrast to HF Hub and OpenML, Papers With Code covers DL vision, NLP, speech, and tabular datasets, making it the natural replacement API for a redesigned infrastructure feasibility study.

## Positioning

No prior work has: (1) empirically tested whether HF Hub and OpenML provide adequate coverage of the Raff 2019 corpus for metadata-based reproducibility auditing, (2) characterized the domain-temporal selection biases of these APIs for pre-2018 ML benchmarks, or (3) proposed Papers With Code as the appropriate primary API for this class of study. We fill all three gaps. Our infrastructure characterization is a prerequisite for any regression study linking dataset metadata signals to Raff's reproducibility labels.
