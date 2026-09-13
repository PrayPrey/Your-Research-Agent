# Research Proposal: Hierarchical Cross-Modal Consistency Learning for Text-to-Audio Generation Evaluation

## 1. Introduction

### Background

The rapid advancement of generative AI has revolutionized content creation across multiple modalities, with audio generation emerging as a particularly dynamic research frontier. Text-to-audio (TTA) generation systems have demonstrated remarkable capabilities in synthesizing speech, music, and environmental sounds from natural language descriptions. However, the field faces a critical bottleneck: the lack of reliable, scalable, and comprehensive evaluation methods that can accurately assess the quality and faithfulness of generated audio.

Current evaluation practices rely heavily on two complementary but individually insufficient approaches. Objective metrics such as Fréchet Audio Distance (FAD), Inception Score (IS), and Kullback-Leibler Divergence capture distributional properties of generated audio but fail to assess semantic alignment with input prompts. Conversely, human evaluation provides nuanced quality assessments but is expensive, time-consuming, non-reproducible, and fundamentally non-scalable. This evaluation gap becomes particularly pronounced when dealing with compositional prompts—complex descriptions involving multiple sound events, temporal relationships, and acoustic attributes (e.g., "a dog barking loudly, followed by distant thunder as rain begins to fall").

Recent efforts have begun addressing this challenge. AQAScore leverages audio-aware large language models for semantic verification, while AudioEval provides multi-dimensional human-annotated datasets for training evaluation models. T2A-Feedback introduces fine-grained AI scoring pipelines for event occurrence and sequence detection. However, none of these approaches systematically addresses the hierarchical nature of audio evaluation across acoustic, semantic, and compositional dimensions simultaneously.

### Research Objectives

This research proposes **HierAudioEval**, a hierarchical evaluation framework for text-to-audio generation that addresses the multi-faceted nature of audio quality assessment. Our specific objectives are:

1. To develop a unified evaluation framework that integrates three complementary assessment levels: acoustic quality, semantic alignment, and compositional consistency.
2. To design a novel compositional evaluation module that parses text prompts into structured event graphs and matches them against detected audio events with temporal boundaries.
3. To create annotated datasets for training compositional evaluation components and validating the complete framework.
4. To demonstrate superior correlation with human judgments compared to existing metrics, particularly for complex compositional prompts.

### Significance

This research addresses a fundamental need in the audio generation community by providing interpretable, scalable evaluation that captures the nuanced relationship between text and audio. The proposed framework will accelerate research iteration cycles, enable fair model comparisons, and provide diagnostic insights into model capabilities and limitations. Furthermore, the compositional evaluation methodology may generalize to other cross-modal generation tasks, contributing broadly to multimodal AI research.

## 2. Methodology

### 2.1 Framework Overview

HierAudioEval comprises three hierarchical evaluation modules that progressively assess audio quality from low-level acoustic properties to high-level compositional structures:

$$\text{HierAudioEval}(x, a) = \alpha \cdot Q_{acoustic}(a) + \beta \cdot S_{semantic}(x, a) + \gamma \cdot C_{compositional}(x, a)$$

where $x$ denotes the text prompt, $a$ represents the generated audio, and $\alpha$, $\beta$, $\gamma$ are learnable combination weights optimized to maximize correlation with human judgments.

### 2.2 Module 1: Acoustic Quality Assessment

The acoustic quality module evaluates perceptual audio quality independent of the text prompt, capturing aspects such as clarity, naturalness, and absence of artifacts.

**Architecture**: We employ a pre-trained audio encoder (PANNs or Audio Spectrogram Transformer) fine-tuned on audio quality datasets. The encoder produces frame-level representations that are aggregated through an attention-weighted pooling mechanism:

$$Q_{acoustic}(a) = \sigma\left(\mathbf{w}^T \cdot \text{AttnPool}\left(f_{encoder}(a)\right)\right)$$

where $f_{encoder}$ extracts audio representations, AttnPool applies learned attention pooling, and $\sigma$ is a sigmoid activation producing scores in $[0, 1]$.

**Training Data**: We leverage existing audio quality datasets including BVCC (speech quality), AudioSet-Quality (general audio), and synthetic degradation augmentation applied to high-quality audio samples.

### 2.3 Module 2: Semantic Alignment Assessment

The semantic alignment module measures correspondence between the text prompt and generated audio content using cross-modal contrastive learning.

**Architecture**: We build upon CLAP (Contrastive Language-Audio Pretraining) embeddings, extending them with a fine-tuned alignment head:

$$S_{semantic}(x, a) = \frac{\exp(\text{sim}(f_t(x), f_a(a)) / \tau)}{\exp(\text{sim}(f_t(x), f_a(a)) / \tau) + \sum_{a' \in \mathcal{N}} \exp(\text{sim}(f_t(x), f_a(a')) / \tau)}$$

where $f_t$ and $f_a$ are text and audio encoders respectively, $\text{sim}(\cdot, \cdot)$ computes cosine similarity, $\tau$ is a temperature parameter, and $\mathcal{N}$ represents a set of negative audio samples.

**Enhancement**: To improve sensitivity to fine-grained semantic differences, we introduce a multi-attribute decomposition approach. The text prompt is parsed into constituent elements (objects, actions, attributes), and alignment is computed for each element separately:

$$S_{semantic}^{enhanced}(x, a) = \frac{1}{|E|} \sum_{e \in E} w_e \cdot S_{semantic}(e, a)$$

where $E$ represents extracted elements and $w_e$ denotes learned importance weights.

### 2.4 Module 3: Compositional Consistency Assessment

The compositional consistency module represents our primary novel contribution, designed to evaluate complex temporal and structural relationships in audio.

#### 2.4.1 Text Prompt Parsing

We employ a fine-tuned language model to parse text prompts into structured **Event Graphs** $G_t = (V_t, E_t)$ where:
- Vertices $V_t$ represent sound events with attributes: $v = (\text{event\_type}, \text{attributes}, \text{temporal\_info})$
- Edges $E_t$ encode temporal and causal relations: $e = (v_i, v_j, r)$ where $r \in \{\text{before}, \text{after}, \text{during}, \text{simultaneous}, \text{causes}\}$

For the example "a dog barking followed by thunder during rain":
- $V_t = \{(\text{dog\_bark}, \emptyset, \text{first}), (\text{thunder}, \emptyset, \text{second}), (\text{rain}, \emptyset, \text{background})\}$
- $E_t = \{(\text{dog\_bark}, \text{thunder}, \text{before}), (\text{thunder}, \text{rain}, \text{during})\}$

#### 2.4.2 Audio Event Detection and Temporal Localization

We develop an audio event detection module that outputs detected events with temporal boundaries:

$$\mathcal{D}(a) = \{(e_i, t_i^{start}, t_i^{end}, c_i)\}_{i=1}^N$$

where $e_i$ is the event class, $t_i^{start}$ and $t_i^{end}$ are temporal boundaries, and $c_i$ is the confidence score.

**Architecture**: A Transformer-based detector operating on mel-spectrogram features with temporal prediction heads:

$$\mathbf{H} = \text{Transformer}(\text{CNN}(\text{MelSpec}(a)))$$
$$\mathbf{e}_i = \text{EventHead}(\mathbf{h}_i), \quad (t_i^{start}, t_i^{end}) = \text{TemporalHead}(\mathbf{h}_i)$$

#### 2.4.3 Temporal Relation Classification

Given detected events, we classify temporal relations between event pairs using a relation classifier:

$$r_{ij} = \text{RelationClassifier}(\mathbf{h}_i, \mathbf{h}_j, |t_i - t_j|)$$

The classifier takes event embeddings and temporal distance as input, outputting relation probabilities.

#### 2.4.4 Graph Matching Score

We construct an audio event graph $G_a = (V_a, E_a)$ from detected events and their relations. The compositional consistency score is computed via graph matching:

$$C_{compositional}(x, a) = \frac{1}{Z} \left( \lambda_V \cdot M_V(V_t, V_a) + \lambda_E \cdot M_E(E_t, E_a) \right)$$

**Vertex Matching**: We compute soft matching between text and audio event sets:

$$M_V(V_t, V_a) = \frac{1}{|V_t|} \sum_{v_t \in V_t} \max_{v_a \in V_a} \text{sim}_{event}(v_t, v_a) \cdot c_{v_a}$$

where $\text{sim}_{event}$ measures semantic similarity between event descriptions and detected classes.

**Edge Matching**: For matched vertex pairs, we evaluate temporal relation consistency:

$$M_E(E_t, E_a) = \frac{1}{|E_t|} \sum_{(v_i, v_j, r_t) \in E_t} \mathbb{1}[r_a(v_i', v_j') = r_t] \cdot \text{conf}(r_a)$$

where $v_i'$, $v_j'$ are matched audio vertices and $r_a$ is the detected relation.

### 2.5 Training Procedure

**Stage 1 - Component Pre-training**:
- Acoustic quality module: Train on quality-annotated datasets with MSE loss
- Semantic alignment module: Fine-tune CLAP with contrastive loss on text-audio pairs
- Event detector: Train on AudioSet with detection and localization losses
- Relation classifier: Train on custom temporal relation annotations

**Stage 2 - End-to-End Optimization**:
We optimize combination weights $(\alpha, \beta, \gamma)$ to maximize correlation with human judgments:

$$\mathcal{L} = -\rho\left(\text{HierAudioEval}(\{x_i, a_i\}), \{h_i\}\right) + \lambda_{reg} ||\theta||_2$$

where $\rho$ denotes Pearson correlation and $\{h_i\}$ are human ratings.

### 2.6 Dataset Construction

**Compositional Annotation Dataset**: We create annotations for 5,000 audio samples from AudioSet and generated audio:
- Event boundaries via semi-automatic annotation with Audacity
- Temporal relations labeled by trained annotators
- Inter-annotator agreement measured via Cohen's kappa

**Evaluation Benchmark**: We curate 1,000 text-audio pairs spanning:
- Simple prompts (single event)
- Compound prompts (multiple independent events)
- Complex compositional prompts (temporal/causal relations)

Each pair receives human ratings on acoustic quality, semantic alignment, and compositional accuracy from 5 annotators.

### 2.7 Experimental Design

**Baselines**: FAD, KL Divergence, CLAP Score, AQAScore, AudioEval's Qwen-DisQA

**Evaluation Metrics**:
- Pearson correlation ($\rho$) with human judgments
- Spearman rank correlation ($\rho_s$)
- Kendall's tau ($\tau$) for ranking consistency
- Stratified analysis by prompt complexity

**Ablation Studies**:
- Individual module contributions
- Impact of compositional module components
- Effect of training data size
- Cross-domain generalization (speech, music, environmental sounds)

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **HierAudioEval Framework**: A complete, open-source evaluation toolkit with trained models, achieving correlation improvements of 15-25% over existing metrics on complex compositional prompts.

2. **Annotated Datasets**: Publicly released datasets including (a) 5,000 audio samples with event boundary and temporal relation annotations, and (b) 1,000 text-audio pairs with multi-dimensional human quality ratings.

3. **Compositional Evaluation Benchmark**: A standardized benchmark for assessing text-to-audio models on compositional understanding, enabling systematic comparison of generative models.

4. **Empirical Insights**: Comprehensive analysis of how different text-to-audio models handle compositional complexity, identifying common failure modes and capability boundaries.

### Scientific Impact

This research contributes a principled methodology for hierarchical cross-modal evaluation that addresses fundamental limitations of existing metrics. The compositional evaluation paradigm—parsing structured representations from text and matching against detected audio structures—provides a generalizable template for evaluating faithfulness in conditional generation tasks. The framework's interpretability (providing scores at acoustic, semantic, and compositional levels) enables diagnostic model analysis beyond single aggregate scores.

### Practical Impact

For audio generation practitioners, HierAudioEval will enable:
- Rapid iteration during model development with reliable automatic feedback
- Fair benchmarking across models and research groups
- Targeted improvement efforts through interpretable sub-scores
- Reduced reliance on expensive human evaluation studies

### Broader Impact

The methodology extends naturally to related domains including text-to-video generation (compositional visual scene evaluation), audio-visual synchronization assessment, and multimodal instruction following. By improving evaluation reliability, this research accelerates progress across the generative AI landscape while establishing evaluation practices that emphasize faithfulness and compositional accuracy—critical properties for trustworthy AI systems.