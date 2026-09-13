# Methodology

To test whether lifecycle-stage functional separability manifests as unsupervised cluster structure or requires supervised signal amplification, we designed a two-stage validation protocol that isolates failure modes. Stage 1 (H-E1) validates signal existence through inter-annotator agreement and linear probe accuracy. Stage 2 (H-M-integrated) tests unsupervised recovery via clustering and baseline comparisons. This design distinguishes "signal absent" from "clustering fails"—if Stage 1 passes but Stage 2 fails, we conclude lifecycle separability exists as a supervised signal but not as unsupervised structure.

## Overview

Our approach follows four methodological principles:

1. **Two-stage validation to isolate failure modes**: Validate signal existence (operational stability, linear separability) before testing unsupervised clustering, enabling mechanistic attribution when clustering fails.

2. **Cross-repository heterogeneity as primary challenge**: Sample metadata from HuggingFace, OpenML, UCI to test generalization beyond single-repository template-driven success (Roman et al. [2023]).

3. **Frozen embeddings to isolate distributional signals**: Use sentence-transformers without fine-tuning to distinguish "signal exists in metadata text" from "signal exists after task-specific training."

4. **Strong baselines to establish semantic value**: Compare against permutation, topic modeling (LDA), and lexical heuristics to test whether semantic embeddings provide value over simpler approaches.

The hypothesis operationalizes as: **If lifecycle stages exhibit operational stability (κ ≥ 0.60), linear separability (probe accuracy ≥ 0.75), and unsupervised clustering recovery (NMI > 0.60 with baseline gap ≥ 0.15), then lifecycle-stage functional separability enables automated cross-repository metadata mapping without labels.** Failure at any stage refines understanding of lifecycle separability's algorithmic requirements.

## Data Collection and Annotation

### Repository Sampling Strategy

We collected metadata fields from three major repositories chosen for ecosystem importance, API accessibility, and schema heterogeneity:

- **HuggingFace Hub** (150 fields): 75 with Open Datasheets structured markup (scaffolded) and 75 from datasets predating Open Datasheets adoption (unscaffolded). This split tests whether interface scaffolding amplifies intrinsic structure or induces stylistic artifacts.

- **OpenML** (100 fields): Intermediate schema structure—predefined field categories (data, task, flow, run) but free-text descriptions. Tests generalization beyond HuggingFace-specific conventions.

- **UCI Machine Learning Repository** (50 fields): Minimal schema structure—plain text READMEs with variable formatting. Critical for testing whether lifecycle detection requires structured interfaces.

**Rationale for stratified sampling**: Balance repository representation (all three major platforms) while oversampling UCI despite fewer total datasets to ensure generalization beyond structured repositories. Scaffolded vs. unscaffolded split isolates interface effects from intrinsic signals.

**Alternatives considered**: Uniform sampling across repositories (rejected: would undersample UCI, missing critical unstructured case); single-repository focus (rejected: doesn't test cross-repository generalization); larger sample size >500 (deferred: proof-of-concept prioritizes methodological rigor over scale).

### Annotation Protocol

Three expert annotators (ML researchers with ≥5 years experience, familiar with Datasheets for Datasets) independently labeled all 300 fields according to Roman et al.'s [2023] validated 2-tier lifecycle taxonomy:

- **General Information**: Dataset name, source, description, format, size, collection process, temporal coverage, versioning
- **Responsible AI**: Ethical considerations, limitations, intended uses, prohibited uses, privacy concerns, fairness considerations, license restrictions

**Annotation procedure**: Annotators received the Datasheets for Datasets [Gebru et al., 2018] and Open Datasheets [Roman et al., 2023] documentation as references but were blind to repository source and hypothesis. Each annotator labeled all 300 fields independently to compute inter-annotator agreement (Cohen's κ).

**Rationale for 2-tier granularity**: Roman et al. [2023] empirically validated 2-tier structure through formative evaluations with dataset producers. Finer-grained 7-stage Datasheets taxonomy would compound class imbalance issues (already 8.3% RAI in 2-tier split). Scoping to 2-tier maximizes signal-to-noise ratio for proof-of-concept.

## Hypothesis 1 (H-E1): Signal Existence Validation

H-E1 tests whether lifecycle categories exhibit operational stability (reliable measurement construct) and linear separability (distributional signals are geometrically accessible). These are necessary conditions for unsupervised clustering—if H-E1 fails, H-M-integrated cannot be meaningfully tested.

### Inter-Annotator Agreement (Operational Stability)

We computed Cohen's κ for all annotator pairs across 300 fields to measure inter-annotator agreement. κ ≥ 0.60 is the success threshold (substantial agreement by Landis & Koch [1977] guidelines). We report both overall κ_across (all repositories pooled) and κ_within for each repository to identify context-dependence.

**Success criterion**: κ_across ≥ 0.60 validates lifecycle constructs as operationally stable—annotators consistently agree on lifecycle roles despite schema heterogeneity.

**Failure response**: If κ < 0.60 but κ_within ≥ 0.70 for structured repositories (HF, OpenML), pivot to repository-scoped claims (lifecycle is context-dependent). If κ < 0.60 universally, lifecycle constructs lack reliability—abandon hypothesis.

### Linear Probe (Signal Detectability)

We embedded all 300 metadata fields using sentence-transformers (all-MiniLM-L6-v2, 384-dimensional frozen embeddings) and trained logistic regression probes on scaffolded HuggingFace data (75 training samples) to predict 2-tier lifecycle labels. Probe accuracy ≥ 0.75 on held-out data validates linear separability—distributional signatures are geometrically accessible.

**Rationale for frozen embeddings**: Fine-tuning would conflate "signal exists in metadata text" with "signal exists after task-specific training." Frozen embeddings isolate distributional regularities (lexical co-occurrence, normative modality) without task adaptation artifacts.

**Rationale for logistic regression**: Linear probes test whether lifecycle roles are linearly separable in embedding space—a necessary condition for simple clustering methods like K-means. Nonlinear probes (MLPs) would succeed even if information is encoded nonlinearly, obscuring clustering failure modes.

**Success criterion**: Probe accuracy ≥ 0.75 establishes distributional signals are detectable and linearly encoded. This validates that unsupervised clustering failure (if it occurs) is algorithmic mismatch, not signal absence.

**Failure response**: If probe < 0.75, pivot to normative geometry hypothesis (lifecycle is encoded nonlinearly, requiring nonlinear clustering methods) or acknowledge embeddings insufficient for lifecycle detection.

## Hypothesis 2 (H-M-integrated): Unsupervised Clustering Test

H-M-integrated tests whether unsupervised clustering can recover lifecycle structure without labels, assuming H-E1 passed (signal exists and is linearly encoded).

### Clustering Protocol

We applied K-means clustering (k=2, matching 2-tier taxonomy) to the 384-dimensional sentence-transformer embeddings of all 300 fields. Following best practices [Arthur & Vassilvitskii, 2007], we ran 10 independent trials with different random seeds and report mean ± standard deviation for Normalized Mutual Information (NMI) between discovered clusters and ground-truth lifecycle labels.

**Rationale for K-means**: Standard centroid-based clustering assuming spherical, balanced clusters. If K-means fails, class-imbalance-aware methods (weighted K-means, DBSCAN) become necessary—scoping deployment complexity.

**Alternatives considered**: Hierarchical clustering (rejected: still assumes balance), Gaussian Mixture Models (rejected: EM algorithm sensitive to initialization with imbalance), DBSCAN (deferred: density parameter tuning requires validation data, defeating unsupervised premise).

### Baseline Comparisons

To establish semantic value of embeddings, we compared K-means NMI against three baselines:

1. **Permutation baseline** (chance performance): Random 2-way label permutation, repeated 1000 times, report mean NMI.

2. **Topic model baseline** (LDA): Latent Dirichlet Allocation with 2 topics on bag-of-words representations (TF-IDF preprocessing, stop-word removal). Tests whether topic clustering recovers lifecycle structure without semantic embeddings.

3. **Lexical heuristic baseline**: Keyword matching for lifecycle categories—{`license`, `privacy`, `ethical`, `fairness`, `prohibited`} → RAI; {`name`, `source`, `description`, `format`, `size`} → General Info. Tests whether simple lexical patterns suffice, avoiding embeddings entirely.

**Success criteria**: NMI(K-means) > 0.60 AND [NMI(K-means) - max(NMI(baselines))] ≥ 0.15. The 0.60 threshold establishes meaningful clustering recovery (Roman et al. [2023] pilot studies suggested ~60-70% category agreement constitutes "useful" separation). The 0.15 gap establishes semantic embeddings provide value over simpler approaches.

**Failure response**: If NMI < 0.60 OR baseline gap < 0.15, unsupervised discovery fails. Explore alternative clustering methods (weighted K-means, DBSCAN) or pivot to semi-supervised approaches (few-shot learning, active learning).

### Repository Stratification Analysis

To test generalization, we trained repository-specific linear probes (HuggingFace-only, OpenML-only, UCI-only) and measured probe accuracy variance. High variance (>0.15 standard deviation) indicates lifecycle separability is repository-specific rather than universal.

We also computed K-means NMI separately for each repository to identify context-dependence. Large NMI variance suggests unsupervised recovery depends on repository-specific structural properties (schema complexity, documentation writing style, class balance) that K-means cannot adapt to.

### Scaffolding Effect Analysis

To distinguish intrinsic signals from interface-induced artifacts, we compared NMI for scaffolded vs. unscaffolded HuggingFace samples. Signal amplification hypothesis predicts 0.1 ≤ NMI(scaffolded) - NMI(unscaffolded) ≤ 0.2—measurable amplification while preserving intrinsic structure (NMI(unscaffolded) > 0.6 validates intrinsic signal).

**Failure interpretation**: If gap > 0.2, separability is interface-induced (scaffolding creates stylistic homogenization, not intrinsic structure). If gap < 0.05, scaffolding adds no value (templating doesn't amplify distributional signatures).

## Embedding Model Details

We use `sentence-transformers/all-MiniLM-L6-v2` [Reimers & Gurevych, 2019], a 22M-parameter model trained on 1B+ sentence pairs via contrastive learning. Frozen embeddings (384 dimensions) encode semantic similarity in Euclidean space via cosine similarity.

**Rationale for this model**: (1) Lightweight enough for proof-of-concept (300 samples × 384 dimensions = manageable), (2) strong zero-shot performance on semantic textual similarity benchmarks (Spearman's ρ=0.82 on STS-B), (3) widely adopted baseline for semantic embedding research enabling reproducibility.

**Alternatives considered**: Larger models (MPNet, all-mpnet-base-v2) offer marginal accuracy gains (~1-2% on STS) at 2-3x compute cost—deferred to future work. Domain-specific fine-tuning (on Datasheets documentation) would improve performance but conflates "signal exists in text" with "signal exists after training"—violates our methodological principle of isolating distributional signals.

## Evaluation Metrics

- **Normalized Mutual Information (NMI)**: Measures cluster-label agreement, range [0, 1], higher = better. Normalized for cluster size imbalance, making it suitable for our 11:1 class ratio.

- **Inter-annotator agreement (Cohen's κ)**: Measures annotation reliability, κ > 0.60 = substantial agreement [Landis & Koch, 1977].

- **Probe accuracy**: Linear probe classification accuracy on 2-tier lifecycle labels, range [0, 1], higher = better linear separability.

**Rationale**: NMI is standard in clustering evaluation, robust to cluster size differences unlike Rand Index. κ is standard in annotation studies for construct reliability. Probe accuracy directly tests linear separability—necessary condition for K-means success.

## Reproducibility and Code Availability

All experiments use publicly available repositories (HuggingFace Hub API, OpenML API, UCI web scraping), open-source models (sentence-transformers), and standard libraries (scikit-learn for K-means, scipy for NMI computation). Annotation guidelines, sampled field lists, and experimental code will be released upon publication to enable reproduction and extension to additional repositories.

## Summary

Our two-stage methodology isolates failure modes: H-E1 validates signal existence (operational stability via κ, detectability via probe accuracy); H-M-integrated tests unsupervised recovery (clustering NMI, baseline comparisons). If H-E1 passes but H-M-integrated fails, we conclude lifecycle separability manifests as a supervised signal requiring task-specific amplification—not an unsupervised emergent structure. Repository stratification and scaffolding effect analyses identify boundary conditions (context-dependence, interface effects). This design enables principled interpretation of negative results: clustering failure despite strong supervised signals reveals algorithmic mismatch (class imbalance, repository heterogeneity), not fundamental signal absence.
