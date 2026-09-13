# Methodology

## Overview

Building on our observation that testability in constraint-driven contexts is a constraint-satisfiability problem, we design a formal verification system that checks for the existence of (Dataset D, Benchmark B, Metric M) triples in a structured knowledge base and flags known confound patterns. The system prioritizes precision over recall through conservative classification logic: when uncertain, classify as "not testable" to avoid false positives that waste researcher time on infeasible experiments. Our approach consists of four components: (1) automated knowledge base construction from catalog APIs, (2) formal (D,B,M) existence verification, (3) cross-domain confound pattern flagging, and (4) domain boundary detection for novel modalities.

## Knowledge Base Construction

The knowledge base stores (Dataset, Benchmark, Metric) triples extracted from the HuggingFace Datasets Hub API, which provides programmatic access to Papers With Code catalog metadata as of January 2026. Each triple represents a valid experimental configuration where dataset D can be evaluated on benchmark task B using automated metric M.

**Automated Extraction Logic:** We query the API for all datasets with benchmark metadata, parse the structured response to extract dataset names, benchmark task identifiers, and associated metric names, then validate completeness by checking that all three fields are non-empty. Triples with missing fields are discarded. The extraction runs without manual intervention or human curation.

**Rationale:** Manual curation of dataset catalogs (estimated 60-70% coverage in prior work, Bouthillier et al. 2021) creates a maintenance bottleneck as new datasets and benchmarks emerge. Automated API-driven extraction achieves 84% coverage (42/50 well-known datasets, 49 complete triples) while remaining synchronizable with catalog updates. The HuggingFace API provides sufficient metadata quality: 100% of extracted triples contain all required fields (no completeness gaps), and domain distribution (28.6% vision, 28.6% NLP, 11.9% graph, 11.9% video, 9.5% audio, 9.5% other) matches the deep learning research landscape.

**Coverage Limitations:** Eight well-known datasets are missing from the January 2026 snapshot: Pascal VOC, MS COCO (duplicate naming), STL-10, SST-2, Common Voice, tieredImageNet, CUB-200, and Stanford Cars. These gaps reflect catalog incompleteness rather than extraction failures — the datasets either were not indexed in HuggingFace or lacked structured benchmark metadata. Missing datasets span multiple domains (vision: 3, NLP: 1, audio: 1, few-shot learning: 3) with no systematic bias toward a single modality. Multi-source aggregation (HuggingFace + Papers With Code + TensorFlow Datasets + Google Dataset Search) is projected to achieve 95%+ coverage through complementary catalog strengths.

## Formal Verification Logic

Given hypothesis text H and knowledge base KB, the verification system determines testability via existence checking: ∃ (D,B,M) ∈ KB such that H can be expressed as an intervention measurable by metric M over benchmark B on dataset D.

**Keyword Extraction:** We parse hypothesis text H to extract dataset names, benchmark task identifiers, and metric names via substring matching against KB entries. For example, hypothesis "Under CIFAR-10 image classification accuracy conditions, if we apply data augmentation..." extracts (D="CIFAR-10", B="image-classification", M="accuracy"). The extraction requires standard phrasing — hypotheses must explicitly name dataset, benchmark, and metric using recognizable terminology.

**Existence Check:** We query KB for exact triple match: (D_extracted, B_extracted, M_extracted) ∈ KB. If match exists, hypothesis is classified as "testable" (resources available). If no match, hypothesis is "not testable" (constraint violation — missing dataset, incompatible benchmark, or unavailable metric).

**Rationale:** Conservative logic prioritizes precision (0% false positive rate) over recall (10%). False positives waste researcher time on infeasible experiments (high cost: weeks of formulation effort lost). False negatives miss testable opportunities (lower cost: researchers may find alternative formulations). The 10% recall reflects keyword extraction brittleness — paraphrased hypotheses ("improve COCO numbers" vs. "improve COCO mAP") fail to extract metric M, triggering false negatives. Semantic extraction via sentence-BERT embeddings (deferred to future work) is projected to improve recall to 70-80% while maintaining false positive rate below 10%.

**Design Trade-offs Considered:** We evaluated semantic matching (cosine similarity between hypothesis embeddings and KB entry embeddings) as an alternative to keyword extraction. Semantic matching improves recall but introduces uncertainty: similarity threshold 0.8 may accept paraphrased dataset names ("ImageNet" vs. "ILSVRC") but also risks false positives on ambiguous cases ("Flowers" dataset — which variant?). We prioritize false positive avoidance (wasted time) over false negative avoidance (missed opportunities), deferring semantic matching until precision-recall trade-offs can be empirically tuned on labeled validation sets.

## Cross-Domain Confound Pattern Flagging

Confound detection checks hypothesis H against 15 documented confound patterns from deep learning literature (Salesky & Black 2020 NLP, Touvron et al. 2019 vision, Goyal et al. 2017 training). Each pattern encodes a known spurious correlation where two variables co-vary without causal relationship, leading to uninterpretable experimental results.

**Pattern Representation:** Each confound pattern P consists of keyword pairs (variable_1, variable_2) and domain tags. Example NLP pattern: P_tokenizer = {keywords: ["tokenizer", "BLEU"], domain: "NLP", severity: "medium"}. Example vision pattern: P_resolution = {keywords: ["resolution", "architecture"], domain: "vision", severity: "high"}. Patterns are sourced from literature surveys documenting systematic confounds across deep learning subfields.

**Matching Logic:** For hypothesis H, we extract all nouns and technical terms, then check for co-occurrence of confound pattern keywords. If H contains both "resolution" and "architecture" keywords, flag P_resolution confound. If H contains both "tokenizer" and "BLEU", flag P_tokenizer confound. Co-occurrence within the same hypothesis text indicates potential confound risk.

**Cross-Domain Transfer:** We do not filter patterns by hypothesis domain — NLP patterns are tested against vision hypotheses, vision patterns against training hypotheses. This design validates the hypothesis that confounds reflect fundamental DL design choices (preprocessing-metric coupling, architecture-data coupling, hyperparameter interdependencies) that generalize beyond modality boundaries. Empirical validation shows 93.33% precision across 30 labeled cases (14/15 confounded hypotheses correctly flagged, 1/15 false positive on "augmentation strength + same model" where augmentation was varied alone).

**Rationale:** Keyword-based matching achieves high precision (93.33%) without requiring labeled training data or domain-specific rule engineering. Alternative approaches considered: (1) Supervised confound classifier requires labeled confound dataset (unavailable). (2) Unsupervised embedding clustering lacks interpretability for researcher feedback ("Why was this flagged as confounded?"). (3) Domain-specific pattern databases (separate NLP/vision/training rules) require manual curation for each new modality. Keyword matching with cross-domain transfer minimizes engineering effort while maintaining precision.

**Pattern Database Limitations:** The 15 patterns are sourced from 2017-2020 literature (Salesky 2020, Touvron 2019, Goyal 2017), missing post-2020 confounds such as pre-training dataset confounds (transfer learning), contrastive loss confounds (self-supervised learning), and prompt template confounds (large language models). One false negative (pre-training dataset confound) in our validation set stems from this incompleteness. Future work proposes automated literature mining (arXiv abstracts 2020-2026) and crowdsourced pattern contributions to expand coverage.

## Domain Boundary Detection

Domain boundary detection prevents false positives on out-of-scope hypotheses from novel modalities (olfactory AI, haptic deep learning, gustatory classification) where the knowledge base has no coverage.

**Approach:** We compute Jaccard similarity between hypothesis domain keywords and KB domain taxonomy (7 established DL domains: vision, NLP, audio, graph, video, speech, multimodal). Extract nouns from hypothesis H, compare to domain keyword sets (e.g., vision keywords: ["image", "pixel", "resolution", "CNN"]), compute overlap ratio. Threshold 0.7: if max domain similarity < 0.7, classify hypothesis as "not testable" (out-of-scope) without attempting (D,B,M) verification.

**Rationale:** Without boundary detection, hypotheses from unsupported domains reach formal verification, which returns "not testable" due to missing KB entries but provides no explanation. Boundary detection adds interpretability: "Hypothesis domain (olfactory) is outside supported domains (vision/NLP/audio/graph/video/speech/multimodal)." This prevents users from misinterpreting "not testable" as "resources exist but system failed to find them" when the actual issue is domain coverage limitation.

**Validation:** Tested on 10 novel modality hypotheses (olfactory, haptic, gustatory, thermal imaging, hyperspectral agriculture, quantum ML, neuromorphic computing, brain-computer interface, molecular dynamics, affective computing). All 10 correctly flagged as out-of-scope (100% accuracy). Conservative threshold (0.7) may reject borderline cases (multimodal hypotheses with one novel modality + one established modality) — this trade-off favors precision over recall, consistent with overall system design philosophy.

## Implementation Details

The system is implemented in Python 3.8 using standard libraries (no deep learning frameworks required). Knowledge base stored as YAML (49 triples, ~5KB file size). HuggingFace API accessed via REST requests with 30-second timeout. Keyword extraction uses simple substring matching (no NLP parsing libraries). Confound pattern database stored as JSON (15 patterns, ~2KB). Domain boundary detection uses spaCy for noun extraction and Python sets for Jaccard similarity computation.

Total computational cost: <1 second per hypothesis classification (KB lookup + confound checking + boundary detection), <1 minute for full KB construction from API. No GPU required. System runs deterministically (same hypothesis → same classification) with reproducible results (fixed KB snapshot, fixed pattern database).

**Reproducibility:** All code, KB triples, confound patterns, and test sets are available in the supplementary materials. Docker container with frozen dependencies (Python 3.8, PyTorch 1.13, HuggingFace Datasets 2.10) ensures environment reproducibility. Estimated compute budget: <1 GPU-hour for full validation study (KB construction + 20 PoC experiments).
