# Related Work

## Weight-Space Learning

Unterthiner et al. (2020) established the weight-to-accuracy prediction task, demonstrating R² > 0.98 using per-layer statistics (mean, standard deviation, spectral norm) on 120K CNN models. This work proves the task is solvable but sidesteps the symmetry problem through careful feature engineering. Eilertsen et al. (2020) extended this to "classifying the classifier," predicting training hyperparameters from weight distributions. These approaches rely on hand-crafted invariant features, losing structural information.

Schürholt et al. (2022) released Model Zoos, a benchmark of 50K+ neural network checkpoints enabling systematic weight-space research. Their follow-up work, SANE (2024), introduced scalable weight embeddings via sequential token processing, demonstrating property prediction on larger models.

## Permutation Symmetry in Neural Networks

Ainsworth et al. (2022) formalized permutation symmetry in weight space through Git Re-Basin, showing that independently trained networks can be merged by aligning their hidden unit orderings. This work establishes that permutation equivalence is not just theoretical—different training runs produce functionally identical networks at different points in weight space.

Sharma et al. (2024) analyzed variance collapse in model merging, demonstrating that permutation alignment is necessary for meaningful interpolation. These works motivate architectural approaches that respect symmetry rather than learning it from data.

## Permutation-Equivariant Architectures

Zhou et al. (2023) introduced Neural Functional Networks (NFN), providing permutation-equivariant layers for processing neural network weights. Their Neural Functional Transformers extend this to attention-based processing. Tran-Viet et al. (2024) adapted NFN for transformers, releasing 125K transformer checkpoints.

Zaheer et al. (2017) established DeepSets, the foundational framework for permutation-invariant/equivariant set functions. This architecture processes set elements with shared networks and aggregates via permutation-invariant pooling (sum, mean). Our NFN implementation follows this pattern.

## Positioning

Prior work either (1) uses hand-crafted invariant features, or (2) demonstrates equivariant architectures without systematic baseline comparison. No existing work directly answers whether non-equivariant methods can learn weight-to-accuracy mappings given sufficient data. We provide this comparison, finding that equivariance is not merely efficient but necessary.
