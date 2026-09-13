---
source_paper: "arxiv_1706_04454.md"
generated_at: "2026-04-24T15:26:31.638957"
model: "gpt-4o-mini"
summary_chars: 7297
---

# An Empirical Study of the Hessian of Over-Parametrized Neural Networks

## Key Metadata
- **Authors:** Levent Sagun et al.
- **Year:** 2018
- **Venue:** Workshop track - ICLR 2018
- **Core Contribution:** This paper investigates the Hessian spectrum of loss surfaces in over-parameterized neural networks, revealing implications for optimization landscapes and generalization properties of various training methods.

## Section Summaries

### Abstract
We study the properties of common loss surfaces through their Hessian matrix. In particular, in the context of deep learning, we empirically show that the spectrum of the Hessian is composed of two parts: (1) the bulk centered near zero, (2) and outliers away from the bulk. We present numerical evidence and mathematical justifications to the following conjectures laid out by Sagun et al. (2016): Fixing data, increasing the number of parameters merely scales the bulk of the spectrum; fixing the dimension and changing the data (for instance adding more clusters or making the data less separable) only affects the outliers. We believe that our observations have striking implications for non-convex optimization in high dimensions. First, the flatness of such landscapes (which can be measured by the singularity of the Hessian) implies that classical notions of basins of attraction may be quite misleading. And that the discussion of wide/narrow basins may be in need of a new perspective around over-parametrization and redundancy that are able to create large connected components at the bottom of the landscape. Second, the dependence of a small number of large eigenvalues to the data distribution can be linked to the spectrum of the covariance matrix of gradients of model outputs. With this in mind, we may reevaluate the connections within the data-architecture-algorithm framework of a model, hoping that it would shed light on the geometry of high-dimensional and non-convex spaces in modern applications. In particular, we present a case that links the two observations: small and large batch gradient descent appear to converge to different basins of attraction but we show that they are in fact connected through their flat region and so belong to the same basin.

### Introduction & Motivation
The paper investigates the second-order properties of the loss surface in supervised learning via the Hessian. Notably, the study queries how common optimization algorithms like Gradient Descent (GD) and Stochastic Gradient Descent (SGD) influence the landscape's characteristics. As models in modern applications tend to be over-parameterized (M ~ N or greater), understanding the relationship between model parameters, data complexity, and optimization dynamics becomes increasingly crucial. The authors aim to empirically analyze how these interactions affect the optimization landscape, specifically regarding Hessian properties and their implications on generalization.

### Methodology
The study employs numerical experiments to examine the Hessian's spectrum in over-parameterized neural networks. The authors utilize a feed-forward neural network with a simplified architecture consisting of two hidden layers, each with multiple nodes. Training datasets vary in complexity, consisting of clusters of samples to explore the Hessian under different conditions.

1. **Parameter Setup**: Neural networks with diverse hidden unit counts (e.g., 10, 30, 50, and 70) have been tested, employing a Mini-batch Stochastic Gradient Descent (SGD) approach, with hyperparameters including a constant learning rate throughout the training process.

2. **Loss Function**: The loss function is defined as:
   \[
   L(w) = \frac{1}{N} \sum_{i=1}^{N} \ell(f(w, x_i), y_i)
   \]
   and is minimized with respect to weights \(w\).

3. **Hessian Calculation**: The Hessian is calculated via exact Hessian-vector products for each weight configuration at the initial and end training phases.

4. **Gauss-Newton Decomposition**: The Hessian's spectrum is expressed using the Gauss-Newton decomposition, allowing insights into their structure via:
   \[
   \nabla^2 L(w) \approx \frac{1}{N} \sum_{i=1}^N \ell''(f(w)) \nabla f(w) \nabla f(w)^T
   \]

5. **Training Procedure**: Newton-type methods, which use second-order information, are contrasted with SGD across multiple experiments to establish differences in convergence characteristics and the influence of weight space dynamics on optimization paths.

### Experiments & Results
1. **Datasets & Setup**: The MNIST dataset, consisting of 1,000 samples, serves as the training base across various experiments. The networks tested have parameters ranging from fully connected architectures (30-70 hidden units) to smaller ones with predefined complexity.

2. **Hessian Spectrum Analysis**: The results consistently demonstrate that the distribution of eigenvalues shows a bulk of small values centered near zero with outlier eigenvalues that exhibit dependency on data distribution:
   - The plot of ordered eigenvalues during the training process reveals that large eigenvalues correspond to a manageable number of classes in the dataset.

3. **Comparison of SGD vs. GD**: The eigenvalue results from small and large mini-batches indicate that large batches yield larger outlier eigenvalues, supporting prior claims regarding the basins of attraction produced by different methods.

4. **Statistical Significance**: The findings are demonstrated statistically significant across varying configurations and are supported by multiple iterations, confirming their reliability.

5. **Negative Eigenvalues**: Even after substantial training, traces of negative eigenvalues signify convergence has yet to be reached, leading to discussions around convergence timescale.

### Discussion & Conclusion
The study concludes that the characteristics of the Hessian indicate that both large-batch and small-batch SGD converge to the same basin in the loss landscape despite variations in eigenvalue distributions. This suggests that the traditional view of "different basins" may be misleading as the surface facilitates connections between solutions. Future explorations should focus on the geometric structure of solution spaces, emphasizing the need to incorporate the effects of architecture and data complexity more rigorously in analyses of optimization landscapes.

## Key Contributions
- Demonstrated that the Hessian spectrum in over-parameterized networks contains significant eigenvalue structure that varies with data complexity.
- Offered new insights into optimization landscapes as influenced by batch sizes in SGD, challenging the traditional notions of isolated basins in the loss surface.
- Established foundational connections between data, architecture, and optimization dynamics to aid in understanding generalization in neural networks.

## Potential Relevance
The paper provides valuable insights into Hessian matrix exploration in neural networks, specifically regarding its implications for optimization strategy and generalization performance. This aligns with ongoing research related to improving deep learning frameworks, enhancing our understanding of convergence properties, and guiding the future design of architectures capable of maintaining efficient training dynamics.