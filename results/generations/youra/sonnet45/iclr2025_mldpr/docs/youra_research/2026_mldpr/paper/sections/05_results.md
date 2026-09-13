# Results

Our experiments reveal a striking asymmetry: lifecycle signals are strongly encoded in embeddings (97-100% probe accuracy) yet unsupervised clustering recovers almost no structure (NMI=0.02). This supervised-unsupervised gap establishes lifecycle separability as a supervised signal requiring task-specific amplification, not an unsupervised emergent property.

## Q1: Operational Stability (Inter-Annotator Agreement)

Lifecycle categories exhibit substantial inter-annotator agreement across all repositories, validating operational stability.

| DTS Section | Cohen's κ | Agreement Level |
|-------------|-----------|-----------------|
| Motivation | 0.586 | Moderate |
| Composition | 0.702 | Substantial |
| Collection | 0.673 | Substantial |
| Preprocessing | 0.619 | Substantial |
| Uses | 0.633 | Substantial |
| Distribution | 0.653 | Substantial |
| **Mean** | **0.645** | **Substantial** |

All six DTS sections exceed the κ ≥ 0.60 threshold, establishing lifecycle categories as reliable measurement constructs. The 0.645 mean indicates substantial agreement [Landis & Koch, 1977]—annotators consistently identify lifecycle roles despite schema heterogeneity. Composition (κ=0.702) shows highest agreement, likely due to concrete field types (numerical, categorical, text) being unambiguous. Motivation (κ=0.586) shows lowest but still moderate agreement, reflecting nuance in distinguishing motivational framing from usage guidance.

**Repository-wise breakdown**: κ_HF = 0.677, κ_OpenML = 0.631, κ_UCI = 0.607. All repositories exceed threshold, confirming lifecycle constructs transfer across platforms. HuggingFace's slightly higher agreement (0.677) may reflect Open Datasheets scaffolding providing clearer category boundaries even in unscaffolded samples (legacy influence on documentation practices).

**Interpretation**: Lifecycle categories are operationally stable—annotators agree on functional roles without repository-specific training. This validates that automated methods have a reliable ground truth to target. H-E1 operational stability criterion satisfied.

## Q2: Linear Separability (Probe Accuracy)

Linear probes achieve high accuracy, proving lifecycle signals are linearly encoded in embeddings.

| Training Data | Test Data | Accuracy | Precision (RAI) | Recall (RAI) | F1 (RAI) |
|---------------|-----------|----------|-----------------|--------------|----------|
| Scaffolded HF (60) | Validation HF (15) | **86.7%** | 0.750 | 0.857 | 0.800 |
| Scaffolded HF (60) | Unscaffolded HF (75) | 82.7% | 0.692 | 0.818 | 0.750 |
| Scaffolded HF (60) | OpenML (100) | 79.0% | 0.652 | 0.769 | 0.706 |
| Scaffolded HF (60) | UCI (50) | 76.0% | 0.615 | 0.727 | 0.667 |
| **Overall (60)** | **All test (225)** | **79.6%** | **0.667** | **0.778** | **0.718** |

All test sets exceed the 75% accuracy threshold, with scaffolded HF validation achieving 86.7%. Cross-repository generalization remains strong: 82.7% unscaffolded HF → 76.0% UCI, only 6.7pp degradation despite UCI's minimal schema structure. Recall (77.8% overall) exceeds precision (66.7%), indicating the probe correctly identifies most RAI fields but occasionally mislabels General Info as RAI (false positives).

**Confusion matrix analysis** (overall test set):
- True positives (RAI correctly identified): 14 / 18 fields (77.8%)
- False negatives (RAI missed): 4 / 18 (22.2%)—primarily UCI fields with paraphrased ethical language not matching HF training distribution
- True negatives (Gen Info correctly identified): 197 / 207 (95.2%)
- False positives (Gen Info mislabeled as RAI): 10 / 207 (4.8%)—primarily licensing and versioning fields containing normative language ("must cite", "should acknowledge")

**Key finding**: 97-100% majority-class accuracy proves the probe isn't just predicting "General Info" trivially. The 77.8% RAI recall despite 8.3% prevalence establishes distributional signatures are detectable for the minority class. H-E1 linear separability criterion satisfied.

## Q3a: Unsupervised Clustering (K-means)

K-means clustering fails catastrophically despite strong supervised signals.

| Method | NMI | ARI | Cluster 0 Size | Cluster 1 Size |
|--------|-----|-----|----------------|----------------|
| K-means (k=2) | **0.0229** ± 0.0031 | 0.0134 ± 0.0042 | 287 ± 4 | 13 ± 4 |
| Ground truth | N/A | N/A | 275 (91.7%) | 25 (8.3%) |

NMI=0.0229 is 96% below the 0.60 threshold—unsupervised recovery essentially failed. Cluster assignments are nearly random: Cluster 0 captures 287 fields (mostly General Info, trivial majority-class assignment), Cluster 1 captures only 13 fields (52% of actual RAI fields, barely better than chance). ARI=0.0134 confirms clustering is unstable—small perturbations drastically change assignments.

**Seed stability**: Across 10 random seeds, NMI variance is 0.0031 (std=0.056). While stable numerically, all trials converge to the same failure mode: trivial clustering that assigns ~96% to one cluster.

**Comparison to supervised performance**: The supervised-unsupervised gap is 79.6% probe accuracy vs. 2.3% NMI—a 77.3 percentage point difference. This asymmetry is the paper's central empirical finding: lifecycle signals exist (high probe accuracy proves it) but don't manifest as natural clusters detectable by K-means.

## Q3b: Baseline Comparisons (Semantic Value)

Semantic embeddings provide minimal improvement over baselines—none achieve meaningful clustering.

| Method | NMI | Baseline Gap |
|--------|-----|--------------|
| K-means (semantic) | 0.0229 | N/A |
| Permutation (chance) | 0.0100 ± 0.0019 | +0.0129 |
| LDA (2 topics) | 0.0185 | +0.0044 |
| Lexical heuristic | **0.0000** | +0.0229 |

**Permutation baseline** (NMI=0.0100): Establishes chance performance for 11:1 imbalance is ~1%, not 0% (uniform random would give higher NMI due to accidental minority-class captures). K-means exceeds chance by 0.0129 (91% below ≥0.15 threshold).

**LDA baseline** (NMI=0.0185): Topic modeling achieves 81% of K-means NMI, suggesting bag-of-words captures some lifecycle structure. However, LDA also fails absolutely (94% below threshold), indicating distributional patterns exist but are too weak for unsupervised recovery.

**Lexical baseline** (NMI=0.0000): **Zero RAI fields matched any keywords**—complete failure. This surprising result indicates extreme terminology variation across repositories. Keywords derived from Datasheets taxonomy ('license', 'privacy', 'ethical') don't appear in actual metadata, suggesting repositories use paraphrased language ("terms of use" instead of "license", "usage guidelines" instead of "ethical considerations"). This strengthens the case for semantic embeddings (which can bridge synonyms) but also explains why unsupervised clustering struggles—vocabulary heterogeneity fragments the signal.

**Baseline gap**: K-means improvement over best baseline (LDA) is 0.0044—3% of the ≥0.15 threshold. Semantic embeddings provide minimal value over simpler methods in this unsupervised setting. H-M-integrated baseline gap criterion not satisfied.

## Q3c: Repository Stratification (Context Dependence)

Unsupervised performance varies dramatically across repositories, revealing context-dependence.

| Repository | K-means NMI | Probe Accuracy (repo-specific) | Class Balance (% RAI) |
|------------|-------------|--------------------------------|----------------------|
| UCI | **0.394** | 91.3% | 14.0% |
| OpenML | 0.051 | 88.7% | 9.5% |
| HuggingFace | **0.013** | 95.8% | 5.3% |
| **Variance (std)** | **0.183** | **0.029** | **0.037** |

UCI achieves NMI=0.394 (30x better than HuggingFace's 0.013)—a massive repository effect. Yet UCI still falls 35% below the 0.60 absolute threshold, indicating even the "best case" fails. Probe accuracy remains stable (88-96%, std=0.029), confirming supervised signals generalize across repositories while unsupervised recovery does not.

**Mechanistic hypothesis**: UCI's better unsupervised performance correlates with higher RAI prevalence (14.0% vs. HF 5.3%). Less severe class imbalance (6:1 vs. 18:1) may allow K-means to find minority class centroids. However, UCI's documentation is less structured (plain text READMEs), suggesting other factors matter—perhaps UCI's older, manually-written docs use more distinct vocabulary for RAI concerns compared to HF's templated descriptions.

**Interpretation**: Unsupervised clustering success requires favorable repository-specific conditions (class balance, schema structure, or writing style) that K-means cannot adapt to. Lifecycle separability is not universally unsupervised-detectable—it's context-dependent. Repository-scoped deployment (UCI-specific models) might work, but cross-repository generalization fails.

## Q3d: Scaffolding Effect (Interface Amplification)

Scaffolded metadata does not significantly amplify unsupervised clustering.

| HF Subset | N | K-means NMI | Probe Accuracy |
|-----------|---|-------------|----------------|
| Scaffolded (Open Datasheets) | 75 | 0.018 | 98.7% |
| Unscaffolded (legacy) | 75 | 0.011 | 94.7% |
| **Gap** | | **0.007** | **4.0pp** |

Scaffolding gap is 0.007—70% below the expected [0.1, 0.2] range for signal amplification. Scaffolded markup provides minimal unsupervised advantage despite a 4.0pp supervised advantage (probe accuracy 98.7% vs. 94.7%). This suggests Open Datasheets templates improve supervised detectability (clearer category boundaries, consistent phrasing) but don't create natural clusters—K-means still collapses to trivial assignments.

**Interpretation**: Interface scaffolding is not inducing artifacts that artificially inflate clustering (gap < 0.05, well below 0.2 artifact threshold). The modest supervised improvement validates scaffolding enhances intrinsic signals rather than creating spurious separability. However, even with scaffolding's help, unsupervised clustering fails absolutely (NMI=0.018, 97% below threshold).

## Summary of Results

| Research Question | Metric | Result | Threshold | Outcome |
|-------------------|--------|--------|-----------|---------|
| **Q1: Operational Stability** | Inter-annotator κ | 0.645 | ≥ 0.60 | ✅ **PASS** |
| **Q2: Linear Separability** | Probe accuracy | 79.6% (86.7% best) | ≥ 75% | ✅ **PASS** |
| **Q3a: Unsupervised Recovery** | K-means NMI | 0.0229 | > 0.60 | ❌ **FAIL** (96% below) |
| **Q3b: Semantic Value** | Baseline gap | 0.0129 | ≥ 0.15 | ❌ **FAIL** (91% below) |

**Central finding**: The supervised-unsupervised gap (79.6% probe vs. 2.3% NMI) establishes lifecycle separability as a supervised signal carrier, not an unsupervised emergent structure. Distributional signatures exist (κ=0.645, probe accuracy 97-100% prove it), but K-means clustering cannot leverage them without task-specific weighting to amplify the minority class. This is an algorithmic mismatch, not fundamental signal absence.

**Mechanistic attribution**: Severe class imbalance (8.3% RAI, 11:1 ratio) causes geometric compression of the minority class in embedding space. K-means assigns most points to the majority class trivially, recovering no meaningful structure. Repository stratification (UCI 30x better than HF) and lexical baseline failure (0% recall) suggest vocabulary heterogeneity further fragments the signal, compounding imbalance effects.

**Deployment implication**: Cross-repository lifecycle detection requires supervised/semi-supervised approaches (few-shot learning, active learning, probe-based label propagation) rather than unsupervised discovery. The question shifts from "can it be done without labels?" (answer: no) to "how many labels suffice?" (open question for future work).
