# Related Work

Our work intersects three research threads: weight-space analysis for model quality prediction, heavy-tailed self-regularization theory, and model zoo construction for population-level analysis.

## Weight-Space Quality Prediction

Unterthiner et al. (2020) established the feasibility of predicting neural network accuracy directly from weight tensors without inference. Using spectral norms, Frobenius norms, and layer-wise statistics, they trained regressors achieving R² ≈ 0.6–0.7 on CNN model populations. This demonstrated that weight statistics encode generalization information. However, their analysis was restricted to convolutional architectures within homogeneous model families. Whether these features transfer to attention-based architectures remains untested.

Eilertsen et al. (2020) extended weight-space analysis to classifier characterization, developing techniques for dissecting the structure of neural network weights. Their methodology provided tools for weight distribution analysis but focused on architectural classification rather than quality prediction. We build on their analytical techniques while targeting cross-architecture quality assessment.

## Heavy-Tailed Self-Regularization Theory

Martin and Mahoney (2021) provided the theoretical foundation for weight-based quality assessment through Heavy-Tailed Self-Regularization (HT-SR) theory. Using Random Matrix Theory and the Hill estimator, they showed that well-trained networks develop heavy-tailed weight distributions characterized by power-law exponents α. Lower α values correlate with better generalization, reflecting implicit regularization during training.

The WeightWatcher tool (Martin et al., 2020) implements this analysis, computing layer-wise α values via singular value decomposition. While the tool supports modern architectures including transformers, systematic validation of HT-SR theory on attention mechanisms has not been conducted. Our work provides this validation, testing whether heavy-tailed signatures emerge in ViT attention layers.

## Model Zoo Construction

Schürholt et al. (2022) introduced the model zoo paradigm for weight-space research at scale, constructing diverse populations of trained models for population-level analysis. Their datasets enabled research on model similarity, weight interpolation, and training dynamics. However, their focus remained on dataset construction rather than cross-architecture prediction transfer.

HuggingFace Model Hub provides an implicit model zoo of unprecedented scale and diversity—over 10,000 vision models spanning multiple architecture families. Unlike curated research zoos, Hub models originate from diverse sources with varying training procedures, creating heterogeneity that challenges cross-model analysis.

## Our Position

Prior work established that (1) weight statistics predict accuracy within architecture families, (2) heavy-tailed theory explains this correlation, and (3) model zoos enable population-level analysis. We address the missing piece: *Does heavy-tailed theory extend to Vision Transformers, and can we achieve bounded variance measurements for cross-architecture comparison?*

Our work differs from prior efforts in three key respects. First, we test on real-world hub diversity rather than curated model zoos. Second, we specifically target attention mechanisms, which have fundamentally different parameter structures than convolutions. Third, we decompose variance sources to identify what controls measurement stability.
