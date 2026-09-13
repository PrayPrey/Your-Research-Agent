# Related Work

Our work bridges three research areas: parameter-efficient fine-tuning, weight-space learning, and geometric analysis of neural network representations. We position our contribution by examining limitations in each area that motivate our controlled experimental approach.

## Parameter-Efficient Fine-Tuning

Low-Rank Adaptation (LoRA) [Hu et al., 2021] introduced the decomposition $\Delta W = BA$ to constrain weight updates to a low-rank subspace, achieving comparable performance to full fine-tuning with orders of magnitude fewer trainable parameters. Subsequent work has focused on improving LoRA training: DoRA [Liu et al., 2024] decomposes weights into magnitude and direction components, revealing that LoRA's learning pattern differs fundamentally from full fine-tuning; QLoRA [Dettmers et al., 2023] enables efficient fine-tuning of quantized models; and AdaLoRA [Zhang et al., 2023] adaptively allocates rank across layers.

Most relevant to our work, StelLA [Li et al., 2025] employs Stiefel manifold geometry to optimize LoRA training, using USV decomposition to separate input and output subspaces. While StelLA leverages geometric structure to *improve* training, we instead analyze geometric structure to *understand* trained adapters. This distinction is crucial: we treat adapter geometry as an object of study rather than an optimization target.

**Limitation we address:** Existing LoRA research focuses on training improvements, not on understanding the geometric signatures that trained adapters exhibit. The structure of the $B$ matrix column space---which defines the output transformation subspace---has not been systematically analyzed as a representation of task similarity.

## Weight-Space Learning

Weight-space learning treats neural network parameters as data points for downstream analysis. The Model Zoo framework [Schürholt et al., 2022] introduced controlled populations of neural networks with verified provenance, demonstrating that weight-space representations enable model property prediction, generation, and analysis. Follow-up work showed that model zoo diversity affects downstream task performance [Falk et al., 2025], and the SANE architecture [Schürholt et al., 2024] achieved scalable weight-space learning through sequential processing of weight matrices.

This line of research has focused primarily on full neural network models rather than parameter-efficient adapters. Full fine-tuning lacks the structural constraints that make LoRA amenable to geometric analysis: the low-rank decomposition $\Delta W = BA$ confines updates to an interpretable subspace, while full fine-tuning distributes updates across all parameters without such constraints.

**Limitation we address:** Weight-space learning methodology has not been applied to parameter-efficient adapters. We adapt the Model Zoo approach---controlled generation with verified provenance---specifically for LoRA adapters, where the low-rank structure provides natural geometric handles for analysis.

## Geometric Analysis of Representations

Grassmann manifolds---the space of linear subspaces of a fixed dimension---provide a natural framework for comparing neural network representations. Principal angles between subspaces, computed via the SVD of inner products between orthonormal bases, yield the Grassmann geodesic distance [Edelman et al., 1998]. This metric has been applied to subspace clustering [Vidal et al., 2011], domain adaptation [Gong et al., 2012], and representation similarity analysis.

In the context of neural networks, CKA [Kornblith et al., 2019] measures representation similarity across layers and models, while SVCCA [Raghu et al., 2017] uses canonical correlation analysis on singular value decomposed activations. These methods compare *activations* (forward pass outputs) rather than *weights* (learned parameters). For LoRA adapters, weight-space analysis is attractive because it requires no inference: geometric signatures can be computed directly from adapter parameters.

Recent work on task similarity [Huang et al., 2024] proposed consistency measures for fine-tuning scope prediction in graph neural networks, demonstrating that task relationships can be quantified geometrically. FL-TAC [Ping et al., 2024] clusters similar adapters in federated learning settings, though without controlled provenance verification.

**Limitation we address:** Geometric analysis of LoRA adapters has been attempted without controlled experiments. Previous studies used public HuggingFace adapters with mixed provenance (different base models, quantizations, and training procedures), confounding task similarity with experimental artifacts. We provide the first controlled validation where only the training task varies.

## Summary and Positioning

Table 1 summarizes how our work relates to and extends prior research.

| Approach | Focus | Adapter Analysis | Controlled Provenance |
|----------|-------|------------------|----------------------|
| LoRA improvements (DoRA, QLoRA) | Training optimization | No | N/A |
| Weight-space learning (Model Zoos) | Full model analysis | No | Yes |
| Representation geometry (CKA, SVCCA) | Activation comparison | No | Varies |
| Adapter clustering (FL-TAC) | Federated aggregation | Yes | No |
| **Our work** | **Geometric signatures** | **Yes** | **Yes** |

Our contribution fills the gap at the intersection: we apply controlled experimental methodology from weight-space learning to parameter-efficient adapters, using geometric analysis to validate task-similarity signatures. This combination---controlled provenance plus adapter-specific geometry---has not been previously explored.
