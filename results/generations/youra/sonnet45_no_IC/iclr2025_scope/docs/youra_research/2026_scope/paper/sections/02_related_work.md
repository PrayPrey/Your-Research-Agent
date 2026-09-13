# Related Work

Our work sits at the intersection of meta-learning, benchmark-driven method evaluation, and automated machine learning. While prior research assumes dataset characteristics are available for meta-learning, we identify metadata collection as a practical bottleneck.

## Meta-Learning and Algorithm Selection

Meta-learning — "learning to learn" — has a rich history in automating machine learning pipeline design. Hospedales et al. (2020) [3] provide a comprehensive survey covering few-shot learning, neural architecture search, and hyperparameter optimization. AutoML systems like Auto-sklearn (Feurer et al. 2015) [4] and TPOT (Olson et al. 2016) [5] use meta-features (statistical properties of datasets) to warm-start Bayesian optimization or evolutionary search. These approaches **assume dataset characteristics are readily computable** — typically extracting features like number of samples, dimensionality, class balance, and skewness directly from in-memory data.

Our work challenges this assumption in the context of literature-based meta-learning. While AutoML systems operate on datasets already loaded by practitioners, we investigate whether published benchmark results can train a meta-classifier **without requiring dataset downloads**. This use case is relevant for practitioners evaluating method choices before committing computational resources, or researchers synthesizing guidance from existing literature. Prior meta-learning work does not address the extraction bottleneck: how to collect dataset characteristics when datasets are distributed across repositories, APIs, and paper supplements.

Rice (1976) [6] formalized algorithm selection as mapping problem instances to optimal algorithms, introducing the Algorithm Selection Problem framework. Subsequent work (Smith-Miles 2009) [7] developed instance space analysis to visualize problem hardness and algorithm performance regions. However, these frameworks assume **features are known** — they focus on predictive modeling and visualization, not on the practical challenge of feature extraction from heterogeneous sources.

## Benchmark Studies in Supervised Learning

Recent benchmark papers provide rich empirical evidence of method performance variability but do not aggregate findings into predictive models. Zhou et al. (2025) [1] evaluate nine medical imaging datasets in federated learning settings, reporting that no single algorithm (FedAvg, FedProx, SCAFFOLD, FedDyn) consistently achieves top performance across datasets. Small datasets (TB with 668 samples) benefit significantly from DDPM+LS augmentation (+17 percentage points) while large datasets (ColonPath with 10K samples) show minimal improvement (+0.3pp). These results suggest dataset size correlates with augmentation effectiveness, but the paper does not test this correlation explicitly or build a predictor.

Champneys et al. (2024) [2] establish baseline comparisons for nonlinear system identification tasks, finding that NARX-Poly achieves 0.032 RMSE on Wing-Hing saturation benchmark versus 0.126 for LSTM. The structured, low-dimensional nature of physics-informed problems favors polynomial bases over recurrent architectures. Again, this observation is descriptive rather than predictive — no framework is provided to determine when polynomial methods will outperform RNNs on **new** system identification tasks.

Other domain-specific benchmarks (OGB for graphs [8], FedML for federated learning [9], LEAF for federated settings [10]) document method rankings on specific datasets but do not extract generalizable patterns. **The gap**: benchmark papers provide ground truth for meta-learning (method rankings across datasets) but do not attempt to learn predictors from this data. Our work takes the next step — collecting these published results to train a meta-classifier — and discovers that the metadata required for prediction is largely absent from literature.

## Method Selection Heuristics and Guidelines

Practitioners currently rely on informal heuristics for method selection. Afkanpour et al. (2024) [11] conduct a systematic review of federated learning challenges, concluding that "data heterogeneity matters" and practitioners should "consider data structure" when selecting aggregation methods. Liao et al. (2025) [12] characterize heterogeneity in federated learning, providing taxonomies of non-IID data types (label skew, feature skew, quantity skew) but no decision rules for matching data types to methods.

These guidelines are **qualitative and unactionable**: "consider data structure" does not specify which features to measure or how to map features to method families. Domain folklore (vision→CNN, time-series→RNN, tabular→tree ensembles) persists despite evidence that exceptions are common (e.g., Transformers now dominate vision after ViT [13], LSTMs underperform polynomial bases on structured dynamics [2]). Our meta-learning approach would systematize these heuristics into testable predictions, but as our results show, **the prerequisite data does not exist in accessible form**.

## Positioning of This Work

Our contribution is procedural rather than algorithmic. We do not propose a novel meta-learning architecture or feature extraction method. Instead, we identify and quantify a practical bottleneck: **literature-based metadata extraction yields only 14% average coverage for critical dataset characteristics** (sample size, dimensionality, class balance). This finding explains why prior meta-learning work focuses on AutoML scenarios (where datasets are already loaded) rather than literature synthesis scenarios (where datasets must be collected).

We differ from prior work in three ways. First, unlike AutoML systems that assume dataset access, we investigate feasibility of metadata extraction from published sources (APIs, READMEs, paper tables). Second, unlike benchmark papers that report rankings without predictive modeling, we attempt to train a meta-classifier and document why it fails (insufficient metadata, not algorithmic issues). Third, unlike guideline papers that provide qualitative advice, we quantify the data requirements for systematic method selection and demonstrate they are unmet.

**The contribution**: exposing a hidden infrastructure assumption in meta-learning research and proposing two-stage data collection (identification + characteristic extraction) as a field-wide need. This reframes the question from "does meta-learning work for method selection?" to "what data infrastructure must exist to test meta-learning fairly?"

---

**References (partial, to be completed in Step 6):**
[3] Hospedales et al. 2020. Meta-learning survey
[4] Feurer et al. 2015. Auto-sklearn
[5] Olson et al. 2016. TPOT
[6] Rice 1976. Algorithm Selection Problem
[7] Smith-Miles 2009. Instance space analysis
[8] OGB benchmarks (graph datasets)
[9] FedML benchmarks
[10] LEAF benchmarks
[11] Afkanpour et al. 2024. Federated learning systematic review
[12] Liao et al. 2025. Heterogeneity characterization
[13] Dosovitskiy et al. 2021. ViT (Vision Transformer)
