# Research Proposal

## Title
TouchLLM: Adapting Video-Language Models for Temporal Tactile Representation Learning

---

## 1. Introduction

### Background

Touch sensing represents one of the most fundamental yet computationally underexplored sensory modalities in artificial intelligence. While humans rely heavily on tactile feedback for dexterous manipulation, object recognition, and environmental interaction, computational approaches to tactile processing remain significantly less mature compared to vision or language understanding. The recent proliferation of high-resolution tactile sensors—including optical-based sensors like GelSight and DIGIT, as well as distributed tactile skins—has created unprecedented opportunities for developing sophisticated touch processing algorithms. These sensors generate rich, image-like data streams that capture detailed contact geometry, texture, and deformation patterns during physical interactions.

A critical observation is that tactile data from continuous object manipulation shares fundamental structural similarities with video: both consist of temporally ordered sequences of visual frames where temporal dynamics carry essential semantic information. In tactile sensing, the evolution of contact patterns over time reveals crucial properties such as slip events, texture gradients, hardness variations, and manipulation stability. However, tactile data also exhibits unique characteristics that distinguish it from conventional video: extreme spatial locality (sensing only a small contact patch), intrinsic dependence on active exploratory motions, and fine-grained temporal dynamics that occur at much faster timescales than typical visual events.

Recent advances in Video-Language Models (VLMs) have demonstrated remarkable capabilities in learning temporal visual representations grounded in natural language. Models like VideoCLIP, VideoLLaMA, and others have shown that pretraining on large-scale video-text pairs enables sophisticated temporal reasoning, action understanding, and zero-shot transfer to novel tasks. This success raises an intriguing research question: Can we leverage the temporal reasoning capabilities learned by VLMs to accelerate tactile representation learning, despite the domain shift from internet videos to tactile imagery?

### Research Objectives

This research proposes **TouchLLM**, a novel framework for adapting pretrained Video-Language Models to tactile representation learning. Our primary objectives are:

1. **Develop efficient adaptation mechanisms** that transfer temporal reasoning capabilities from pretrained VLMs to the tactile domain while preserving the unique characteristics of touch sensing.

2. **Enable language-grounded tactile understanding** by creating paired tactile-language datasets that describe contact properties, enabling zero-shot reasoning about tactile properties through natural language.

3. **Incorporate active sensing context** by conditioning tactile representations on proprioceptive signals, capturing the intrinsic relationship between exploratory actions and resulting tactile observations.

4. **Achieve cross-sensor generalization** through sensor-agnostic representation learning that transfers across different tactile sensor modalities.

### Significance

This research addresses several critical challenges identified in the tactile processing literature. First, by leveraging pretrained VLMs, we can overcome data scarcity limitations by transferring knowledge learned from millions of video-text pairs. Second, our language grounding approach provides an intuitive interface for specifying tactile properties, enabling applications in human-robot interaction and assistive technologies. Third, the active sensing conditioning mechanism directly addresses the unique temporal structure of tactile data, distinguishing our approach from generic video understanding methods. Success in this research would significantly lower barriers for AI researchers entering the tactile processing field while advancing the foundations of computational touch science.

---

## 2. Methodology

### 2.1 Overview

The TouchLLM framework consists of three interconnected components: (1) a Tactile-Video Alignment module that maps tactile sensor outputs to the visual embedding space of frozen VLMs, (2) a Touch-Language Grounding mechanism enabling zero-shot tactile understanding through natural language, and (3) an Active Sensing Conditioning module that incorporates proprioceptive signals. Figure 1 (conceptual) illustrates the overall architecture.

### 2.2 Tactile-Video Alignment Module

#### Adapter Architecture

Given a pretrained VLM with frozen visual encoder $\mathcal{V}$ and temporal transformer $\mathcal{T}$, we design a lightweight adapter network $\mathcal{A}_\theta$ that transforms tactile frames into the VLM's visual embedding space. For a tactile video sequence $\mathbf{X}^{(t)} = \{x_1, x_2, ..., x_T\}$ where $x_i \in \mathbb{R}^{H \times W \times C}$ represents individual tactile frames:

$$\mathbf{z}_i^{(tac)} = \mathcal{A}_\theta(\mathbf{x}_i) + \alpha \cdot \mathcal{V}(\mathbf{x}_i)$$

where $\alpha$ is a learnable residual scaling factor initialized to zero, enabling stable training while gradually incorporating pretrained visual features. The adapter $\mathcal{A}_\theta$ consists of:

1. **Sensor-Specific Input Projection**: A convolutional stem that normalizes different tactile sensor outputs (varying resolutions, color spaces, and sensing modalities) to a unified representation:

$$\mathbf{h}_i = \text{Conv}_\text{stem}^\text{sensor}(\mathbf{x}_i) \in \mathbb{R}^{H' \times W' \times D}$$

2. **Tactile Feature Extractor**: A lightweight vision transformer with $L=4$ layers that captures tactile-specific spatial patterns:

$$\mathbf{f}_i = \text{ViT}_\text{tactile}(\mathbf{h}_i) \in \mathbb{R}^{N \times D}$$

3. **Distribution Alignment Layer**: A projection layer with LayerNorm that aligns the statistical properties of tactile features to the VLM's visual embedding distribution:

$$\mathbf{z}_i^{(tac)} = \text{LayerNorm}(\mathbf{W}_p \mathbf{f}_i + \mathbf{b}_p)$$

#### Temporal Encoding

The aligned tactile embeddings are processed through the frozen VLM temporal transformer with tactile-specific positional encodings:

$$\mathbf{Z}^{(tac)} = \mathcal{T}([\mathbf{z}_1^{(tac)} + \mathbf{p}_1, ..., \mathbf{z}_T^{(tac)} + \mathbf{p}_T])$$

where $\mathbf{p}_i$ are learnable temporal position embeddings that capture the typically faster dynamics of tactile events compared to natural videos.

### 2.3 Touch-Language Grounding

#### Tactile-Language Dataset Curation

We construct a paired tactile-language dataset through three complementary strategies:

1. **Automated Captioning Pipeline**: We develop a template-based captioning system that generates descriptions from sensor metadata and task context:
   - Contact descriptions: "The sensor is pressing against a [rough/smooth] [hard/soft] surface"
   - Temporal events: "A slip event is occurring as the object slides [direction]"
   - Force descriptions: "Contact force is [increasing/decreasing/stable]"

2. **Human Annotation**: For a subset of tactile videos, we collect human descriptions through Amazon Mechanical Turk, focusing on subjective tactile properties (e.g., "feels like sandpaper," "squishy like a sponge").

3. **Vision-Language Model Augmentation**: Using the visual similarity between tactile images and contact surfaces, we leverage existing VLMs to generate initial descriptions that are refined with tactile-specific vocabulary.

#### Contrastive Learning Objective

We employ a contrastive loss to align tactile and language representations:

$$\mathcal{L}_\text{TL} = -\frac{1}{2N}\sum_{i=1}^{N}\left[\log\frac{\exp(\text{sim}(\mathbf{z}_i^{(tac)}, \mathbf{z}_i^{(txt)})/\tau)}{\sum_{j=1}^{N}\exp(\text{sim}(\mathbf{z}_i^{(tac)}, \mathbf{z}_j^{(txt)})/\tau)} + \log\frac{\exp(\text{sim}(\mathbf{z}_i^{(txt)}, \mathbf{z}_i^{(tac)})/\tau)}{\sum_{j=1}^{N}\exp(\text{sim}(\mathbf{z}_j^{(txt)}, \mathbf{z}_i^{(tac)})/\tau)}\right]$$

where $\text{sim}(\cdot, \cdot)$ denotes cosine similarity and $\tau$ is a temperature parameter.

### 2.4 Active Sensing Conditioning

Tactile perception is inherently active—the sensory experience depends critically on how the sensor interacts with the environment. We incorporate proprioceptive signals as conditioning context:

#### Proprioceptive Encoding

Given proprioceptive measurements $\mathbf{P} = \{(f_i, \mathbf{q}_i, \dot{\mathbf{q}}_i)\}_{i=1}^{T}$ where $f_i$ represents force magnitude, $\mathbf{q}_i$ is end-effector pose, and $\dot{\mathbf{q}}_i$ is velocity, we encode these as:

$$\mathbf{e}_i^{(prop)} = \text{MLP}([f_i; \mathbf{q}_i; \dot{\mathbf{q}}_i])$$

#### Cross-Attention Integration

Proprioceptive context is integrated through cross-attention layers inserted after each temporal transformer block:

$$\mathbf{Z}'^{(tac)} = \mathbf{Z}^{(tac)} + \text{CrossAttn}(\mathbf{Z}^{(tac)}, \mathbf{E}^{(prop)}, \mathbf{E}^{(prop)})$$

This design allows the model to modulate tactile feature interpretation based on the exploratory action being performed.

### 2.5 Training Procedure

#### Stage 1: Alignment Pretraining
We first pretrain the adapter module using a reconstruction objective on large-scale tactile video data:

$$\mathcal{L}_\text{recon} = \|\mathbf{x}_i - \mathcal{D}(\mathbf{z}_i^{(tac)})\|_2^2$$

where $\mathcal{D}$ is a lightweight decoder. This ensures the adapter captures tactile-relevant information.

#### Stage 2: Multimodal Alignment
We jointly optimize tactile-language alignment and tactile-proprioceptive coherence:

$$\mathcal{L}_\text{total} = \mathcal{L}_\text{TL} + \lambda_1 \mathcal{L}_\text{temporal} + \lambda_2 \mathcal{L}_\text{prop}$$

where $\mathcal{L}_\text{temporal}$ enforces temporal consistency through frame order prediction and $\mathcal{L}_\text{prop}$ ensures proprioceptive-tactile coherence through force prediction.

### 2.6 Experimental Design

#### Datasets

1. **Foundation Tactile Dataset**: 3M+ samples across 13 sensors and 11 tasks
2. **Touch and Go Dataset**: 13,000 tactile videos from 20 object categories
3. **YCB-Tactile Dataset** (to be collected): Tactile interactions with YCB objects including language annotations

#### Evaluation Tasks and Metrics

| Task | Metrics | Baselines |
|------|---------|-----------|
| Tactile Property Recognition | Accuracy, F1-score | T3, TLV-CoRe, UniT |
| Slip Detection | Precision, Recall, AUC-ROC | CNN-LSTM, Temporal CNN |
| Cross-Sensor Generalization | Zero-shot Accuracy | SITR, T3 |
| Language-Guided Retrieval | Recall@K, MRR | CLIP-tactile, RA-Touch |
| Manipulation Policy Learning | Success Rate, Sample Efficiency | ResNet+RNN, VTacO |

#### Ablation Studies

We will systematically evaluate:
- Impact of each component (adapter, language grounding, proprioceptive conditioning)
- Effect of VLM backbone choice (VideoCLIP, VideoLLaMA, InternVideo)
- Scaling behavior with training data size
- Generalization across sensor types (optical vs. capacitive vs. resistive)

---

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **State-of-the-Art Performance**: We expect TouchLLM to achieve significant improvements over existing methods on standard tactile benchmarks:
   - 10-15% improvement in tactile property classification accuracy
   - 20%+ improvement in zero-shot cross-sensor transfer
   - Competitive slip detection with 5x less task-specific training data

2. **Novel Capabilities**: 
   - First demonstration of language-guided tactile reasoning (e.g., "find the softest object")
   - Zero-shot tactile property inference through natural language queries
   - Unified representation supporting both perception and manipulation tasks

3. **Open Resources**:
   - Pretrained TouchLLM models for various VLM backbones
   - Tactile-language dataset with 50,000+ annotated sequences
   - Benchmark suite for evaluating tactile-language models

### Impact

**Scientific Impact**: This research establishes a new paradigm for tactile representation learning that leverages the vast knowledge encoded in pretrained video-language models. By demonstrating successful transfer from the video domain to tactile sensing, we provide evidence that the temporal reasoning capabilities learned from natural videos are sufficiently general to benefit tactile processing. This insight could inspire similar cross-modal transfer approaches for other underexplored sensing modalities.

**Practical Applications**: 
- **Robotic Manipulation**: Language-grounded tactile understanding enables intuitive specification of manipulation goals and failure conditions
- **Prosthetics**: Natural language interfaces for configuring sensory feedback based on user preferences
- **Teleoperation**: Improved tactile feedback interpretation for remote surgery and hazardous environment manipulation
- **Quality Inspection**: Zero-shot detection of surface defects using language descriptions

**Community Building**: By lowering the entry barrier through pretrained models and comprehensive benchmarks, this work will accelerate research at the intersection of touch processing and AI/ML. The open-source release of models and datasets will enable researchers without access to physical tactile sensors to contribute to computational tactile research through simulation and transfer learning studies.

---

## 4. Conclusion

TouchLLM represents a principled approach to bridging the gap between the mature field of video-language understanding and the emerging domain of computational touch processing. By carefully adapting pretrained VLMs while respecting the unique characteristics of tactile sensing—temporal dynamics, active sensing dependencies, and spatial locality—we aim to accelerate the development of sophisticated tactile AI systems. Success in this research would not only advance the state of tactile representation learning but also establish methodological foundations for leveraging large-scale pretrained models in specialized sensing domains.