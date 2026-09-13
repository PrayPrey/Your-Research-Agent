---
source_paper: "arxiv_2403_11998.md"
generated_at: "2026-08-18T23:53:40.685433"
model: "openai/gpt-5.2"
summary_chars: 13750
---

# Learning Useful Representations of Recurrent Neural Network Weight Matrices

## Key Metadata
- **Authors:** Vincent Herrmann et al.
- **Year:** 2024
- **Venue:** arXiv (2403.11998)
- **Core Contribution:** Proposes and evaluates mechanistic vs. functionalist (probing-based) encoders for LSTM weight matrices, introduces *interactive probing* with theory showing exponential efficiency gains in some settings, and releases two RNN “model zoo” datasets plus an emulation-based self-supervised training objective.

## Section Summaries

### Abstract
Recurrent Neural Networks (RNNs) are general-
purpose parallel-sequential computers. The pro-
gram of an RNN is its weight matrix. How to
learn useful representations of RNN weights that
facilitate RNN analysis as well as downstream
tasks? While the mechanistic approach directly
looks at some RNN’s weights to predict its behav-
ior, the functionalist approach analyzes its overall
functionality—specifically, its input-output map-
ping. We consider several mechanistic approaches
for RNN weights and adapt the permutation equiv-
ariant Deep Weight Space layer for RNNs. Our
two novel functionalist approaches extract infor-
mation from RNN weights by ‘interrogating’ the
RNN through probing inputs. We develop a the-
oretical framework that demonstrates conditions
under which the functionalist approach can gener-
ate rich representations that help determine RNN
behavior. We release the first two ‘model zoo’
datasets for RNN weight representation learning.
One consists of generative models of a class of
formal languages, and the other one of classifiers
of sequentially processed MNIST digits. With
the help of an emulation-based self-supervised
learning technique we compare and evaluate the
different RNN weight encoding techniques on
multiple downstream applications. On the most
challenging one, namely predicting which exact
task the RNN was trained on, functionalist ap-
proaches show clear superiority.

### Introduction & Motivation
The paper targets **representation learning over RNN programs**, i.e., compact embeddings of **RNN/LSTM weight matrices** that are useful for analyzing and predicting model behavior and for downstream tasks (e.g., searching over learned programs). Prior “hyper-representation” work mostly focuses on **feedforward/CNN** weights and faces two core issues that are amplified for RNNs: large parameter counts and **symmetries** (especially hidden-neuron permutation invariance). The authors distinguish **mechanistic** encoders (directly process weights) from **functionalist** encoders (infer properties by interacting with the model’s input–output behavior). They introduce probing-based functionalist encoders—especially **interactive probing**—and show both theoretical and empirical evidence that interaction can be substantially more efficient at identifying model behavior.

### Methodology
The target object is an RNN (assumed **multi-layer LSTM**) parameterized by weights \(\theta \in \Theta\), defining a recurrent map
\[
f_\theta: \mathbb{R}^X \times \mathbb{R}^H \to \mathbb{R}^Y \times \mathbb{R}^H,\quad (x,h_{t-1})\mapsto (y,h_t).
\]
A **weight encoder** \(E_\phi:\Theta\to\mathbb{R}^Z\) maps \(\theta\mapsto z\) (here \(Z=16\)). The paper evaluates **six encoder architectures**:

**Mechanistic encoders (direct weight access):**
1) **Layer-Wise Statistics + MLP:** For each weight matrix, compute mean, std, and quantiles \((0,0.25,0.5,0.75,1)\). For each LSTM layer, produce 12 vectors (4 gates × {input-to-hidden, hidden-to-hidden, bias}), concatenate, then MLP. This is permutation-invariant but *not* universal (many distinct functions share same statistics).
2) **Flattened Weights + MLP:** Flatten all parameters into one vector, feed to MLP. Not permutation-invariant; input-layer parameter count scales as \(O(N^2)\) with hidden size \(N\). Universal approximation (in principle) but generalization suffers due to symmetry.
3) **Parameter Transformer (Schürholt et al., 2021-style):** Treat per-neuron weight rows (+biases) as a sequence and process with an encoder-only Transformer with learned positional encodings (therefore not permutation-invariant). Scales \(O(N)\) in sequence length and input projections; universal as a sequence model.
4) **DWSNet (Navon et al., 2023; Zhou et al., 2023), adapted to LSTMs:** Builds **permutation-equivariant** weight-processing layers so that permuting hidden units results in a corresponding permutation of internal features; a final pooling yields permutation invariance. Claimed to be universal over weight-space functions while respecting symmetry.

**Functionalist encoders (no direct weight access; probe \(f_\theta\)):**
5) **Non-Interactive Probing:** Use fixed learnable probing embeddings \(S_i\) for \(i=1..L\). Each step: \(S_i \xrightarrow{E_I}\) a batch of \(M\) probing inputs \(\hat x_i^{(m)}\); query \(f_\theta\) in batch to get \(\hat y_i^{(m)}=f_\theta(\hat x_i^{(m)})\); transform via \(E_O\) to \(o_i\); aggregate across steps with an LSTM \(E_R\) to output \(z\). Probing inputs are *static* w.r.t. the specific \(\theta\).
6) **Interactive Probing (novel):** Same pipeline, but probing is *adaptive*: the recurrent state (from \(E_R(o_{<i})\)) is fed into \(E_I\) so that each next probe depends on previous outputs \(\hat y_{<i}\), enabling an “interrogation” process.

**Self-supervised pretraining via emulation.** They train encoders using an **Emulator** \(A_\xi\), an RNN with hidden state \(b\), conditioned on the representation \(z=E_\phi(\theta)\):
\[
A_\xi: \mathbb{R}^X \times \mathbb{R}^B \times \mathbb{R}^Z \to \mathbb{R}^Y \times \mathbb{R}^B.
\]
Given a dataset of rollouts \(D=\{(\theta_i,S_{\theta_i})\}\) where \(S_\theta=(x_1,y_1,x_2,y_2,\dots)\) comes from running \(f_\theta\) in an environment \(\mathcal{E}\), encoder+emulator are trained jointly to imitate the original outputs:
\[
\min_{\phi,\xi}\ \mathbb{E}_{(\theta,S)\sim D}\ \sum_{(x_i,y_i)\in S} \mathcal{L}\big(A_\xi(x_i,E_\phi(\theta)),\, y_i\big). \tag{1}
\]
For **continuous** \(y\), \(\mathcal{L}\) is MSE; for **categorical** \(y\), they use **reverse KL divergence** (mode-seeking). Conditioning of \(A_\xi\) on \(z\) is implemented by **adding a linear projection of \(z\) to the BOS token** of the emulator’s input sequence. After pretraining, \(A_\xi\) can be discarded and \(E_\phi\) reused for downstream prediction.

**Theory for probing encoders (why interaction helps).** They formalize “probing” as an *interrogator* \(I_D\) identifying an unknown \(f_C\) from a finite set \(D=\{f_i\}_{i=1}^n\) of distinct total computable functions by querying input–output pairs. They prove: (i) any \(f_C\in D\) can be identified in at most \(|D|-1\) interactions (Prop. 3.1); (ii) worst-case upper bound is \(|D|-1\) for both interactive and non-interactive interrogators (Prop. 3.2); but (iii) there exist sets \(D\) where interactive interrogation needs **exponentially fewer** interactions than any non-interactive scheme (Prop. 3.3). This motivates interactive probing as a sample-efficient way to extract functional signatures.

### Experiments & Results
**Datasets (two released “RNN model zoos”).** Each dataset contains **1000 LSTMs**, all with **2 layers** and **hidden size 32**, trained on many related tasks. For each model, they save weights at **9 fixed training steps**, plus **100 rollouts** \(S_\theta\) and metadata (task identity, performance metrics, etc.). Data are split into train/val/OOD-test with **non-overlapping tasks**; OOD tasks are “structurally slightly different.”

1) **Formal Languages (generative).** Autoregressive LSTMs trained with **teacher forcing** and **cross-entropy language modeling** to generate strings from:
\[
L_{m_b,m_c,m_d}=\{a^n b^{n+m_b} c^{n+m_c} d^{n+m_d}\mid n\ge 0,\ m_b,m_c,m_d\in\{-2,-1,0,1,2\}\}.
\]
Total tasks: \(6^3=216\). Sequence length is **42** including **BOS/EOS**; max \(n=10\), padding with EOS. Performance metric for original RNNs: **proportion of correctly generated strings** in the language. (OOD set: languages with smallest \(|m_b|+|m_c|+|m_d|\).)

2) **Tiled Sequential MNIST (classification).** MNIST digits converted into sequences of **\(49\) tiles of size \(4\times 4\)** (+ BOS/EOS). After each tile, model predicts digit; training loss is mean cross-entropy across positions, but evaluation uses final prediction accuracy. Tasks are **digit rotations**: train/val rotations sampled in \([0,311]^\circ\), OOD rotations in \([312,360]^\circ\). Performance metric: validation **classification accuracy**.

**Training protocol & reporting.** Main experiments use **15 random seeds** per model; results reported as **bootstrapped means with 95% confidence intervals**. For encoders lacking permutation invariance (**Flattened Weights**, **Parameter Transformer**), they augment training by randomly permuting neurons of the input RNN.

**Phase 1: Self-supervised emulation quality.** All encoders output \(Z=16\)-dim embeddings; emulator is a **2-layer LSTM**. Validation emulation losses (Table 2):

| Encoder | Formal Languages loss | Sequential MNIST loss |
|---|---:|---:|
| Layer-Wise Statistics | 0.051 (0.050, 0.053) | 0.039 (0.038, 0.039) |
| Flattened Weights | 0.045 (0.045, 0.046) | 0.024 (0.024, 0.024) |
| Parameter Transformer | 0.043 (0.042, 0.044) | 0.067 (0.067, 0.067) |
| DWSNet | 0.046 (0.046, 0.046) | 0.024 (0.023, 0.025) |
| Non-Interactive Probing | 0.023 (0.019, 0.029) | 0.017 (0.016, 0.017) |
| **Interactive Probing** | **0.015 (0.008, 0.022)** | 0.017 (0.017, 0.018) |

Key outcome: on **Formal Languages**, **interactive probing** is clearly best; on **Sequential MNIST**, **both probing encoders** are best and similar. The paper further checks “cloned performance” by running the emulator conditioned on \(E_\phi(\theta)\); only interactive probing yields high-fidelity emulation across the full performance range on Formal Languages (Figure 5).

**Embedding-space structure (qualitative).** PCA plots of interactive-probing embeddings on Formal Languages show **task-wise clustering** by language and a **within-task gradient** correlated with generation accuracy. For Sequential MNIST, embeddings reflect the **continuous rotation angle** plus accuracy; t-SNE baselines fail to show coherent global structure (Figures 6–7).

**Phase 2: Downstream property prediction.** They train an MLP predictor on frozen pre-trained embeddings (and compare to fully supervised end-to-end training). Properties:
- Formal Languages: **task** (3-hot for \(m_b,m_c,m_d\), trained with BCE), **accuracy** (MSE).
- Sequential MNIST: **task** (rotation angle, MSE), **accuracy** (MSE), **training step** (9-way CE), **generalization gap** (MSE).
To focus on encoder generalization, predictor training data includes **half of the OOD test set** (for both pre-trained and supervised comparisons). Main highlighted result is **task prediction** on OOD (Figure 8):  
- Formal Languages (OOD): **pre-trained interactive probing** substantially outperforms all other encoders and also the purely supervised variants.  
- Sequential MNIST (OOD): **both probing** encoders outperform mechanistic ones; in purely supervised training, **non-interactive probing** is best while interactive probing underperforms (hypothesized due to insufficient supervised signal to learn adaptive probing).

Additional summary from appendix-referenced full results: **DWSNet** is most consistent for “simpler” scalar metadata (accuracy, gap, step), while probing dominates “genuine functional” identification (task).

### Discussion & Conclusion
The paper argues that effective RNN-weight representations require (i) diverse trained-model datasets, (ii) a pretraining objective that enforces functional fidelity (emulation), and (iii) an encoder architecture respecting weight symmetries and/or directly extracting function. Empirically, **functionalist probing**—especially **interactive probing**—best captures algorithmic task identity in the formal-language setting, matching theory that interaction can be exponentially more query-efficient. Limitations include focus on **small LSTMs** and **training stability issues** for interactive probing; authors suggest future work on improved optimization/regularization and scaling probing to larger sequence models (potentially with policy gradients for non-differentiable/expensive targets).

## Key Contributions
- Introduces and systematically compares **six** RNN weight-encoding architectures, including adapting **DWSNet** to **LSTMs** and proposing **non-interactive** and **interactive probing** functionalist encoders.
- Provides a **theoretical interrogation framework** showing interactive probing can require **exponentially fewer** interactions than non-interactive probing for some function families (while sharing the same worst-case bound).
- Releases two first-of-kind **RNN model-zoo datasets** (Formal Languages, Tiled Sequential MNIST) and a practical **emulation-based self-supervised** training approach for RNN weight representations.

## Potential Relevance
Interactive probing is a concrete mechanism for extracting **behavioral signatures** from a black-box sequence model, which is relevant for hypotheses about *functional vs. mechanistic* representations, model auditing, or meta-learning over policies/models. The emulation objective in Eq. (1) offers a reusable pretraining recipe for “model embedding” that can be tested on other architectures (SSMs/Transformers) or other downstream tasks (task inference, capability prediction, generalization forecasting). The released datasets provide a controlled environment to study how well different encoders capture **algorithmic structure** vs. superficial correlates of training.