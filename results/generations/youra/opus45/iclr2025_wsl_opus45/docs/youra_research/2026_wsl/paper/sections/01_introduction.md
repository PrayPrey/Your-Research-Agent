# Introduction

As parameter-efficient fine-tuning proliferates, practitioners accumulate hundreds of LoRA adapters with no principled way to understand their relationships. When facing a new task, which existing adapter should serve as initialization? Which adapters encode similar functional transformations? Current practice relies on metadata tags and manual curation---but the adapters themselves may contain geometric structure that reveals task similarity.

This challenge grows more pressing as LoRA [Hu et al., 2021] becomes the dominant method for large language model customization, with over 17,000 citations and widespread adoption across research and industry. Organizations maintaining collections of domain-specific adapters---what we term *adapter zoos*---lack tools to leverage the internal structure of these artifacts. Without such tools, adapter selection becomes guesswork, and the potential of modular, parameter-efficient fine-tuning remains unrealized.

## The Problem: Opaque Adapter Geometry

At the surface level, LoRA adapters are treated as opaque artifacts. We know the task an adapter was trained on, but not how its learned transformations relate to other adapters in the collection. Prior work has focused primarily on improving LoRA training---through weight decomposition [Liu et al., 2024], manifold constraints [Li et al., 2025], or initialization strategies---rather than understanding the geometric structure that trained adapters exhibit.

Looking deeper, the mathematical structure of LoRA suggests that adapters may encode interpretable geometric signatures. LoRA constrains weight updates to a low-rank subspace: $\Delta W = BA$, where $B \in \mathbb{R}^{d \times r}$ and $A \in \mathbb{R}^{r \times k}$. The column space of the $B$ matrix defines the output transformation subspace. If semantically similar tasks require similar functional transformations, their $B$ matrices should span similar subspaces---a hypothesis that, surprisingly, has never been rigorously validated under controlled experimental conditions.

The gap in existing work is clear: previous attempts to validate LoRA geometric signatures used public adapter collections with uncontrolled provenance---different base models, hyperparameters, and training procedures---confounding task similarity with experimental artifacts. Even when promising effect sizes emerged (Cohen's $d = 0.91$), statistical power was insufficient ($p = 0.127$ with only 8 adapters) to draw reliable conclusions. No prior work has applied the controlled experimental methodology needed to isolate task-specific geometric structure.

## Our Approach: Controlled Validation of Geometric Signatures

We hypothesize that LoRA adapter $B$ matrix column spaces encode task-specific geometric signatures that cluster by semantic similarity, detectable via Grassmann distance under controlled experimental conditions. To test this hypothesis, we adapt the Model Zoo methodology [Schürholt et al., 2022]---originally developed for full neural network populations---to parameter-efficient adapters. By training adapters under identical conditions (same base model, hyperparameters, and training procedure) varying only the task, we isolate task-specific geometric structure from experimental confounds.

Building on this approach, we make the following contributions:

1. **Existence Proof.** We demonstrate that within-category LoRA adapters (e.g., reasoning tasks) exhibit significantly smaller Grassmann distances than between-category adapters (Cohen's $d = 0.77$, $p < 10^{-27}$), establishing that task-category clustering in adapter geometry is real and statistically robust.

2. **Mechanism Validation.** We show that geometric similarity correlates with semantic similarity as defined by FLAN task taxonomy (Spearman $\rho = 0.39$, $p < 10^{-28}$), confirming that the clustering reflects meaningful task relationships rather than arbitrary structure.

3. **Negative Finding.** We find that task-category clustering is distributed uniformly across all transformer layer types (attention and MLP), refuting the hypothesis of layer-specific specialization and revealing that geometric signatures are a global property of adapter structure.

These findings establish geometric foundations for understanding LoRA adapter relationships, enabling future work on principled adapter retrieval, transfer prediction, and intelligent adapter selection.

## Paper Organization

The remainder of this paper is organized as follows. Section 2 situates our work within LoRA research, weight-space learning, and subspace analysis. Section 3 presents our methodology for controlled adapter generation and Grassmann distance analysis. Section 4 describes our experimental design, and Section 5 presents results. Section 6 discusses implications and limitations, and Section 7 concludes with future directions.
