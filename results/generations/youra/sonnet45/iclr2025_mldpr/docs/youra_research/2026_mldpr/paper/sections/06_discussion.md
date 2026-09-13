# Discussion

Our results establish lifecycle-stage functional separability as a **supervised signal carrier** rather than an unsupervised emergent structure. This distinction clarifies the feasibility landscape for automated cross-repository metadata mapping: the question is not whether lifecycle detection is possible—it demonstrably is (97-100% probe accuracy)—but rather what algorithmic approach enables deployment at scale.

## Interpreting the Supervised-Unsupervised Gap

The 77.3 percentage point gap between supervised (79.6% probe accuracy) and unsupervised performance (2.3% NMI) is the paper's central empirical contribution. This asymmetry reveals three critical insights:

**1. Signal existence is decoupled from clustering detectability.** High inter-annotator agreement (κ=0.645) and linear separability (97-100% probe) prove lifecycle roles are encoded in embeddings as distributional regularities. Yet K-means NMI=0.02 shows these regularities don't manifest as geometric clusters. The failure is algorithmic (K-means assumes balanced, well-separated clusters), not representational (embeddings lack lifecycle information).

**2. Supervised methods amplify minority-class signals through task-specific weighting.** Linear probes learn to upweight RAI-discriminative features (normative language patterns, licensing terminology) despite 8.3% class prevalence. K-means treats all dimensions uniformly, causing minority-class compression. This explains why the same embeddings succeed supervised but fail unsupervised—it's not the representations but the algorithm's ability to handle imbalance.

**3. Unsupervised recovery depends on favorable structural conditions K-means cannot adapt to.** Repository stratification (UCI 30x better than HF) shows clustering success requires repository-specific properties—likely less severe class imbalance (UCI 14% RAI vs. HF 5.3%), simpler schemas, or more distinct RAI vocabulary. Without adaptation mechanisms, K-means collapses to trivial assignments.

## Mechanistic Attribution: Why Clustering Fails

We attribute unsupervised failure primarily to **severe class imbalance** (8.3% RAI, 11:1 ratio), supported by converging evidence:

- **Geometric compression**: K-means cluster sizes (287:13) nearly match class balance (275:25), indicating trivial majority-class assignment rather than semantic discovery.

- **Repository variance**: UCI's 14% RAI prevalence (6:1 ratio) yields NMI=0.39—still failing but 30x better than HF's 5.3% (18:1). This correlation suggests balance is causal, though not definitively proven without controlled rebalancing experiments.

- **Probe-clustering divergence**: Probes achieve 77.8% RAI recall via learned weighting; K-means achieves 52% (barely above 50% chance). Same embeddings, different outcomes—algorithmic mismatch to imbalance, not signal absence.

**Alternative explanations**: Repository heterogeneity (UCI's plainer text vs. HF's templates) or vocabulary variation (lexical baseline 0% recall) may compound imbalance effects by fragmenting the signal across repository-specific phrasings. The 30x performance variance suggests multiple interacting factors. Future work should disentangle balance from vocabulary via controlled experiments (synthetic rebalancing, cross-lingual tests).

## Comparison to Prior Work

Our findings refine understanding of semantic embedding applicability in three ways:

**1. Template-driven vs. discovery approaches complement rather than compete.** Roman et al.'s [2023] Open Datasheets succeeds by imposing structure top-down (templates guide authors toward lifecycle categories). Our unsupervised approach tests bottom-up discovery (can structure be found in heterogeneous text?). Both work in their respective settings: templates within adopting repositories, supervised detection across repositories. The boundary is clear: unsupervised discovery fails for highly imbalanced documentation metadata.

**2. Semantic embeddings enable supervised generalization, not unsupervised discovery.** Sentence-transformers [Reimers & Gurevych, 2019] achieve strong zero-shot performance on balanced semantic similarity tasks (STS-B). Our results show embeddings extend to imbalanced documentation via supervised probes (79.6% cross-repository accuracy) but not via unsupervised clustering (NMI=0.02). This scopes embedding utility: useful for few-shot learning, insufficient for label-free structure discovery under severe imbalance.

**3. Class imbalance in documentation differs from vision/NLP benchmarks.** Standard imbalanced learning [He & Garcia, 2009] addresses 1:10 to 1:100 ratios in classification. Our 1:11 ratio is moderate numerically but extreme geometrically—minority class has only 25 examples in 384-dimensional space (0.065 examples per dimension). Sparsity amplifies imbalance effects: K-means centroids poorly estimated from few minority samples. This suggests documentation metadata requires imbalance-aware clustering (weighted K-means, SMOTE oversampling, or supervised alternatives) even at "moderate" ratios.

## Limitations

**1. Two-tier granularity only.** We tested Roman et al.'s [2023] validated 2-tier structure (General vs. RAI) but not Gebru et al.'s [2018] full 7-stage taxonomy (motivation, composition, collection, preprocessing, uses, distribution, maintenance). Finer granularity would worsen class imbalance (300 fields ÷ 7 categories = 43 per category average, but RAI subcategories like "prohibited uses" likely have <10 examples). **Why acceptable**: 2-tier maximizes signal-to-noise for proof-of-concept; Roman's user validation confirms 2-tier structure is behaviorally meaningful. **Future mitigation**: Hierarchical classification (first predict 2-tier, then refine within each tier) or larger-scale data collection (1000+ fields) to support balanced 7-way splits.

**2. Class imbalance explanation is correlational, not causal.** Repository stratification shows UCI's better performance (NMI=0.39) correlates with higher RAI prevalence (14% vs. HF 5.3%), but we didn't run controlled rebalancing experiments to prove causality. **Why acceptable**: Correlation is suggestive; controlled synthetic rebalancing might introduce artifacts (e.g., SMOTE-generated samples differ from real metadata). **Future mitigation**: Weighted K-means with class-aware centroids, DBSCAN to test density-based clustering, or active learning to efficiently collect more RAI examples.

**3. Three repositories only (HF, OpenML, UCI).** We haven't tested Kaggle, Zenodo, Papers With Code, or domain-specific repositories (medical, genomic). **Why acceptable**: Our repositories span metadata structure spectrum (HF structured with Open Datasheets, UCI unstructured plain text, OpenML intermediate) and cover major ML ecosystems. **Future mitigation**: Extend to Papers With Code (code-first documentation style), Zenodo (research data repositories), Kaggle (competition-focused) to test vocabulary and schema diversity limits.

**4. English-only metadata.** Multilingual generalization untested. **Why acceptable**: English dominates ML repository metadata (>95% on HuggingFace Hub). **Future mitigation**: Multilingual embeddings (mBERT, XLM-R) for cross-lingual lifecycle detection, testing whether lifecycle constructs transfer semantically across languages.

## Broader Impact Statement

Automated cross-repository metadata mapping could improve dataset discoverability and documentation quality assessment at ecosystem scale—positive impact for reproducibility and responsible AI adoption tracking. However, imperfect classification introduces risks:

**Positive impacts**: (1) Researchers conducting meta-analyses gain efficient tools to identify datasets with desired documentation properties across repositories. (2) Repository maintainers can systematically audit documentation completeness and flag underdocumented datasets. (3) Longitudinal tracking of responsible AI documentation adoption becomes feasible at scale, enabling empirical study of documentation practice evolution.

**Risks and mitigations**: (1) **False negatives** (mislabeling RAI fields as General Info) could cause practitioners to overlook important ethical considerations when selecting datasets. **Mitigation**: Deploy with confidence thresholds—flag borderline cases for human review rather than auto-classifying. (2) **False positives** (mislabeling General Info as RAI) waste human reviewer time but are less harmful. **Mitigation**: Optimize for high recall (minimize false negatives) at the cost of precision. (3) **Deployment without validation** on specific repositories could propagate errors. **Mitigation**: Require few-shot calibration (10-20 labels) per new repository to adapt to repository-specific vocabulary and class balance.

**Accountability**: Semi-supervised approaches (our recommended deployment path) inherently require human oversight—labels must be provided by domain experts familiar with responsible AI principles. This human-in-the-loop design prevents fully automated misclassification cascades. Practitioners should treat lifecycle predictions as suggestions requiring validation, not ground truth.

## Future Work Directions

Our results open several promising research directions:

**1. Minimize annotation budget for few-shot lifecycle detection.** Key question: how few labels suffice for cross-repository generalization? Initial experiments (probe trained on 60 scaffolded HF samples) generalize to UCI with 6.7pp accuracy drop. Can active learning select maximally informative examples to reduce this to 10-20 labels per repository? Can meta-learning (MAML, Prototypical Networks) enable one-shot adaptation?

**2. Test class-imbalance-aware clustering methods.** Weighted K-means with class-aware centroid initialization, density-based methods (DBSCAN, HDBSCAN) that adapt to local density, or spectral clustering with imbalance-robust affinity matrices. Our results establish the baseline (vanilla K-means fails); these alternatives test whether algorithmic improvements suffice or whether supervision is fundamentally necessary.

**3. Explain UCI's 30x better unsupervised performance.** Controlled experiments isolating balance (synthetic rebalancing), vocabulary (UCI-style plain text vs. HF templates), and schema complexity (structured fields vs. free-form text). Causal attribution would guide deployment: if balance is causal, focus on rebalancing; if vocabulary matters, adapt preprocessing.

**4. Extend beyond 2-tier to hierarchical lifecycle taxonomy.** Test whether two-stage classification (first General vs. RAI, then subcategories within each) outperforms flat 7-way. Hierarchical probes might leverage coarse-to-fine signal structure, reducing per-category sample requirements.

**5. Deploy ecosystem-wide metadata quality dashboard.** Semi-supervised lifecycle detectors monitoring HF, OpenML, UCI, Kaggle, Zenodo for documentation completeness. Track longitudinal trends (is RAI documentation adoption increasing post-2023 regulatory focus?). Enable automated meta-analyses correlating documentation quality with dataset usage (downloads, citations).

These directions share a common theme: operationalizing the supervised-signal insight for practical deployment. Unsupervised discovery is infeasible (our negative result), but supervised/semi-supervised approaches are demonstrably effective (97-100% probe accuracy). The challenge shifts from "can we detect lifecycle without labels?" to "how efficiently can we propagate labels across repositories?" This reframing redirects research effort toward maximally impactful questions.
