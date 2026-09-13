---
source_paper: "arxiv_2210_06313.md"
generated_at: "2026-05-08T05:57:44.244155"
model: "gpt-4o-mini"
summary_chars: 6212
---

# The Lazy Neuron Phenomenon: On Emergence of Activation Sparsity in Transformers

## Key Metadata
- **Authors:** Zonglin Li et al.
- **Year:** 2023
- **Venue:** arXiv
- **Core Contribution:** This paper investigates the phenomenon of activation sparsity in Transformers, highlighting its prevalence, causes, and benefits for model efficiency and robustness.

## Section Summaries

### Abstract
This paper studies the curious phenomenon for machine learning models with Transformer architectures that their activation maps are sparse. By activation map we refer to the intermediate output of the multi-layer perceptrons (MLPs) after a ReLU activation function, and by “sparse” we mean that on average very few entries (e.g., 3.0% for T5-Base and 6.3% for ViT-B16) are nonzero for each input to MLP. Moreover, larger Transformers with more layers and wider MLP hidden dimensions are sparser as measured by the percentage of nonzero entries. Through extensive experiments we demonstrate that the emergence of sparsity is a prevalent phenomenon that occurs for both natural language processing and vision tasks, on both training and evaluation data, for Transformers of various configurations, at layers of all depth levels, as well as for other architectures including MLP-mixers and 2-layer MLPs. We show that sparsity also emerges using training datasets with random labels, or with random inputs, or with infinite amount of data, demonstrating that sparsity is not a result of a specific family of datasets. We discuss how sparsity immediately implies a way to significantly reduce the FLOP count and improve efficiency for Transformers. Moreover, we demonstrate perhaps surprisingly that enforcing an even sparser activation via Top-k thresholding with a small value of k brings a collection of desired but missing properties for Transformers, namely less sensitivity to noisy training data, more robustness to input corruptions, and better calibration for their prediction confidence.

### Introduction & Motivation
The authors explore the surprising observation that while Transformers perform dense computations, their activations in intermediate layers are remarkably sparse once trained. This sparsity, where only a small percentage of neurons activate per input, parallels findings in biological neural systems, suggesting a link to energy efficiency. Despite being built for dense computations, it's crucial to understand the implications of this sparsity for performance and resource usage in deep learning systems, particularly in enhancing robustness to noise, efficiency, and interpretability.

### Methodology
The core analysis involves Transformer architectures such as T5 (Text-to-Text Transfer Transformer) and ViT (Vision Transformer). The sparsity \( s \) of activations is quantified using the percentage of nonzero entries in the activation map after applying ReLU. The formula for the output of an MLP layer is given by:

\[
f(x; K, V) = V \sigma(K^T x)
\]

where \( x \) is the input, \( K \) are the key parameters, and \( V \) are the value parameters. Key hyperparameters for the models include learning rate (e.g., 1e-4), batch size (e.g., 32), and training epochs (e.g., 5). Training utilizes optimizers like Adam with a decay schedule. The input comprises preprocessed text or image data depending on the architecture. Notably, sparsity emerges during training dynamics, suggesting it may arise inherently from the optimization process rather than specific dataset structures. The authors introduce a modified approach, Top-k Transformer, where a thresholding mechanism \( \text{Top}(k) \) applied to activation maps allows control over sparsity, maintaining performance while increasing efficiency.

### Experiments & Results
The study utilized datasets such as the C4 corpus for T5 and ImageNet-21k for ViT, analyzing activation sparsity over various configurations. Key metrics include the average percentage of nonzero activations, which remained low across different layers and configurations. Results summarized indicate:

| Model       | Avg Nonzero Activation (%) | Configurations | 
|-------------|-----------------------------|-----------------|
| T5          | 2.7                         | Base (12 layers)|
| ViT         | 6.3                         | B/16            |

Baseline comparisons include various Transformer architectures, documenting a consistent emergence of sparsity across tasks and settings. The ablation studies reveal that deeper models exhibited greater sparsity, and introducing noise or random datasets reduced sparsity but did not eliminate it completely. Notable findings suggest that models with stricter sparsity enforcement via the Top-k method show improved robustness against noise, better calibration, and similar or superior performance metrics compared to their dense counterparts.

### Discussion & Conclusion
The findings emphasize that sparsity in activation maps is pervasive across different architectures and dataset structures, presenting opportunities for enhancing model efficiency and robustness. The link between sparsity and a model’s ability to handle noisy data is particularly critical, warranting further investigation into methodologies that build upon these properties. The authors suggest leveraging sparsity might yield not just computational benefits but also improve generalization capabilities, indicating promising directions for future research in DNN architectures.

## Key Contributions
- Proving the prevalence of sparse activations in Transformers across various configurations and tasks.
- Introduction of the Top-k Transformer technique to enhance efficiency and robustness during both training and inference.
- Establishing connections between activation sparsity, model calibration, and robustness to noisy data.

## Potential Relevance
The exploration of activation sparsity in Transformers could inform the development of more efficient models for various applications in NLP and vision. The methodology provides a framework for anticipating the effects of sparsity on model performance, which may assist in hypothesis development regarding resource utilization and model reliability under constraints.