# An Empirical Study of Example Forgetting during Deep Neural Network Learning

**Authors:** Toneva et al.  
**Year:** 2019  
**arXiv ID:** 1812.05159  
**Citations:** ~300  

## Key Contribution

Introduces "example forgetting" as a metric for understanding temporal learning dynamics. Unforgettable examples (learned once, never misclassified) correspond to simple patterns, while forgettable examples (repeatedly learned and forgotten) correspond to complex patterns.

## Core Claims

1. **Temporal Ordering:** Simple patterns (often spurious correlations) are learned earlier and never forgotten, while core features emerge later and undergo forgetting cycles.

2. **Forgetting Events:** The number of times an example is forgotten during training correlates with the complexity of the features required to classify it correctly.

3. **Architecture-Agnostic Pattern:** Forgetting dynamics exist across ResNets, VGGs, and MobileNets, but systematic architectural comparison is absent.

## Mechanism

During early training, gradients flow preferentially to examples that provide strong signal (often spurious correlations). These examples become "unforgettable." Examples requiring more nuanced features are initially misclassified, then learned, then forgotten as the model oscillates between different minima, before finally being stably learned in later epochs.

## Experimental Evidence

- **CIFAR-10:** 30% of training examples are "unforgettable" (learned in first epoch, never forgotten).
- **ImageNet:** Unforgettable examples correspond to texture-based shortcuts; forgettable examples require shape understanding.
- **Curriculum Learning:** Removing unforgettable examples (potential shortcuts) improves generalization.

## Limitations

- Single architecture (ResNet) used for most experiments.
- Temporal metrics (forgetting events) not linked to architectural properties (depth, normalization, attention).
- Optimization effects (learning rate schedules, batch size) not systematically studied.

## Relevance to Gap

Demonstrates temporal learning dynamics exist but lacks quantitative connection to architectural properties like normalization layers or attention mechanisms.
