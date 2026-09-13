---
source_paper: "arxiv_2512_07853.md"
generated_at: "2026-07-10T05:22:21.891753"
model: "openai/gpt-5.2"
summary_chars: 12132
---

# GPU Memory Prediction for Multimodal Models

## Key Metadata
- **Authors:** Minchul Kang et al.
- **Year:** 2025 (arXiv:2512.07853; SAA’25 listed in manuscript header)
- **Venue:** SAA’25 (October 13, 2025, Seoul, Korea) / arXiv
- **Core Contribution:** A layer-wise, factorized analytical framework to predict *peak* GPU memory usage for *multimodal* model training by explicitly accounting for heterogeneous modules and modality-dependent training behavior, achieving ~8.7% average MAPE on LLaVA-1.5 (7B).

## Section Summaries

### Abstract
As deep learning models in agentic AI systems grow in scale
and complexity, GPU memory requirements increase and
often exceed the available GPU memory capacity, so that
out-of-memory (OoM) errors occur. It is well known that
OoM interrupts the whole training itself and wastes substan-
tial computational resources. Therefore, to prevent OoM,
accurate prediction of GPU memory usage is essential. How-
ever, previous studies focus only on unimodal architectures
and fail to generalize to multimodal models, even though
the multimodal models are a common choice in agentic AI
systems. To address this limitation, we propose a framework
that predicts the peak GPU memory usage by analyzing the
model architecture and training behavior of multimodal mod-
els. Specifically, the framework decomposes the multimodal
model into its constituent layers and applies “factorization”
to estimate the memory usage of each layer. Our evaluation
shows that our framework achieves high prediction accuracy
of ∼8.7% average MAPE.

### Introduction & Motivation
The paper targets a practical training failure mode—GPU out-of-memory (OoM)—that increasingly occurs as *multimodal* (e.g., vision–language) models used in agentic AI systems scale up. Prior GPU-memory predictors largely assume unimodal, homogeneous architectures, making them brittle when applied to multimodal systems with distinct modules (vision encoders, language decoders, projection layers) and modality-specific “frozen vs trainable” behaviors. Profiling-based predictors can incur non-trivial overhead by running multiple iterations, while formula-based predictors often hard-code assumptions tied to specific layer types or architectures. The authors’ gap claim is that there is no robust, architecture-and-training-behavior-aware method that generalizes to heterogeneous multimodal stacks such as LLaVA.

### Methodology
The proposed framework predicts *peak* GPU memory usage for multimodal model training by (i) parsing model structure into modality-aware modules, (ii) decomposing modules into layers, and (iii) *factorizing* each layer’s memory into semantically distinct contributors whose presence depends on training behavior (frozen vs updated). The workflow (Fig. 1 in the manuscript) is:

1. **Model parsing (①–②):** A **Model parser** analyzes the multimodal architecture and extracts top-level **modules** grouped by modality (e.g., *Vision*, *Language*, *Projection*). This explicitly represents heterogeneity that breaks unimodal assumptions.
2. **Training configuration ingestion (③):** A **configuration file** supplies training hyperparameters (the paper explicitly mentions **batch size** as an input). These hyperparameters affect activation sizes and thus peak memory.
3. **Layer decomposition (④):** Each module is decomposed into fine-grained **PyTorch layers** (e.g., `nn.Linear`, embeddings, `LayerNorm`) using the PyTorch API. This produces a canonical list of layer instances across modules, enabling per-layer accounting.
4. **Memory factorization (⑤):** For every layer, the framework separates memory into four factors:
   - **Model parameters** \(M_{\text{param}}\): persistent weights/biases resident during training.
   - **Gradients** \(M_{\text{grad}}\): stored for trainable parameters during backprop until the optimizer step.
   - **Optimizer states** \(M_{\text{opt}}\): extra tensors required by the optimizer (e.g., momentum/variance for Adam-like methods).
   - **Activations** \(M_{\text{act}}\): intermediate forward-pass tensors that must be retained until their backward computation completes.
   
   Crucially, *which factors apply* is conditioned on **training behavior**. For example, a layer inside a **frozen** module has \(M_{\text{param}}\) but typically no \(M_{\text{grad}}\) or \(M_{\text{opt}}\); trainable layers include all relevant factors.
5. **Per-factor analytical prediction (⑥):** A **factor predictor** computes each factor via an analytical equation “per factor.” (The excerpt explicitly notes that the paper emphasizes the *framework* and does **not** provide detailed factor derivations.) Conceptually, the predictor must map layer metadata (tensor shapes, dtype, whether trainable, batch/sequence/image sizes) into byte counts for each factor.
6. **Aggregation into peak memory (⑦):** Predicted peak memory is the sum over layers and modules:
\[
M_{\text{peak}}=\sum_{\text{module}}\sum_{\text{layer}}\left(M_{\text{param}}+M_{\text{opt}}+M_{\text{grad}}+M_{\text{act}}\right)
\tag{1}
\]
A multimodal-specific nuance highlighted by the authors is how \(M_{\text{act}}\) is computed: in multimodal training, activation memory is computed **for modalities whose parameters are being updated**, whereas unimodal predictors implicitly assume a single modality’s activations dominate and follow uniform training behavior.
7. **Handling multimodal training stages:** Using LLaVA as the motivating example, the framework is designed to reflect stage-dependent training: (a) **pre-training** updates only the projection layer (vision + language frozen), then (b) **fine-tuning** updates projection + parts of language while vision remains frozen. This staged “trainability mask” changes which layers contribute \(M_{\text{grad}}\) and \(M_{\text{opt}}\), and thus changes \(M_{\text{peak}}\).

Overall, the methodological novelty is not a single closed-form formula for one architecture, but a *general pipeline* that (i) systematically enumerates layers in heterogeneous modules and (ii) switches memory-factor inclusion based on module/layer trainability—aiming to generalize across multimodal configurations without re-deriving architecture-specific formulas whenever a new module is added.

### Experiments & Results
**Experimental target and scope.** The evaluation described in the excerpt focuses on **LLaVA-1.5 (7B)** as a representative multimodal model with heterogeneous modules (CLIP ViT-L/14 vision encoder, Vicuna-based language decoder, and a projection layer). The authors emphasize evaluation “under diverse hyperparameter settings,” consistent with their goal of predicting memory across training configurations likely to cause OoM.

**What is measured.** The output variable is **peak GPU memory usage** during training (the paper’s primary goal is avoiding OoM). The reported accuracy metric is **MAPE** (Mean Absolute Percentage Error), and the key headline number is an **average MAPE of ~8.7%**. The excerpt does not provide the explicit MAPE formula, confidence intervals, or distributional statistics; it only reports the average.

**Baselines and comparisons.** The paper positions its approach against two families:
- **Profiling-based prediction** methods that run a few iterations to infer peak usage (cited as [3, 12, 13])—argued to incur overhead and time cost.
- **Formulation-based modeling** that predicts per-layer memory with architecture-specific formulas (cited as [2, 6])—argued to fail to generalize to multimodal heterogeneity. The authors state they attempted to apply the method in **[2]** to a multimodal model and found it “does not work at all” because it was designed for a specific unimodal architecture.
However, the excerpt does **not** include numeric baseline error values, runtime overhead comparisons, or a direct head-to-head table beyond the authors’ own MAPE.

**Datasets, splits, training objective, and compute.** The excerpt does not specify datasets, dataset sizes, train/val/test splits, loss functions, optimizer type, GPU model, or profiling methodology (e.g., whether peak memory was measured via `torch.cuda.max_memory_allocated()`), so these cannot be reproduced from the provided text. Notably, memory-prediction experiments can be dataset-agnostic if input tensor shapes are controlled; the excerpt does not clarify whether real training data or synthetic batches were used.

**Main reported result (from excerpt).**

| Model | Task evaluated | Metric | Reported value |
|---|---|---:|---:|
| LLaVA-1.5 (7B) | Peak GPU memory prediction across hyperparameter settings | Avg. MAPE | \(\approx 8.7\%\) |

**Ablations and significance.** The excerpt does not report ablation studies (e.g., removing factorization, ignoring trainability masks, or treating modules as unimodal), nor statistical significance measures.

Interpretation based strictly on reported numbers: the framework achieves single-digit-percent average relative error on a complex multimodal architecture, supporting the authors’ claim that explicitly modeling multimodal module structure and training-stage-dependent trainability improves generalization beyond unimodal memory predictors.

### Discussion & Conclusion
The paper’s key takeaway is that accurate *peak* GPU memory prediction for multimodal training requires modeling both heterogeneous architecture (modules/layers) and heterogeneous training behavior (which parts are frozen vs updated). Their factorized, layer-wise accounting framework achieves ~8.7% average MAPE on LLaVA-1.5 (7B) under varying hyperparameters. A limitation apparent from the excerpt is the lack of published per-factor derivations and incomplete experimental detail (datasets/optimizer/compute/baselines), which makes it harder to assess generality and reproducibility beyond the showcased model.

## Key Contributions
- **Multimodal-aware memory prediction formulation:** Introduces a framework that targets *multimodal* architectures explicitly, rather than assuming a unimodal, homogeneous stack—motivated by agentic AI systems where vision–language models (e.g., LLaVA) are common.
- **Layer-wise “factorization” aligned with training behavior:** Decomposes the model into modules → layers and factorizes each layer’s memory into \(M_{\text{param}}, M_{\text{grad}}, M_{\text{opt}}, M_{\text{act}}\), with factor inclusion conditioned on whether the layer/module is frozen or trainable (capturing stage-wise training and fine-tuning regimes).
- **Peak-memory aggregation across modules and layers:** Provides an explicit aggregation objective for peak memory over heterogeneous modules:
  \[
  M_{\text{peak}}=\sum_{\text{module}}\sum_{\text{layer}}\left(M_{\text{param}}+M_{\text{opt}}+M_{\text{grad}}+M_{\text{act}}\right),
  \]
  and highlights a multimodal-specific nuance that \(M_{\text{act}}\) should be computed over the *updated* modalities rather than assumed uniform.
- **Empirical accuracy on a representative VLM:** Demonstrates ~**8.7% average MAPE** on **LLaVA-1.5 (7B)** under diverse hyperparameter settings, suggesting practical utility for pre-flight OoM avoidance.
- **Positioning against existing predictor families:** Articulates limitations of (i) profiling-based predictors due to iteration overhead and (ii) formula-based unimodal predictors due to lack of generalization when new modules/layers are introduced into multimodal architectures.

## Potential Relevance
The modular parsing + trainability-conditioned factorization offers a blueprint for building *configuration-aware* memory predictors for complex training pipelines (multi-stage fine-tuning, partial freezing, adapter-based tuning), which is directly useful when designing experiments that must fit within fixed GPU budgets. The framework’s separation into \(M_{\text{param}}, M_{\text{grad}}, M_{\text{opt}}, M_{\text{act}}\) also provides a clean scaffold for hypotheses about which factor dominates under specific regimes (e.g., frozen vision encoder vs full fine-tuning) and where memory-saving interventions (checkpointing, optimizer choice, parameter-efficient tuning) should have the largest impact.