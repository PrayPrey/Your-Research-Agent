# Related Work

We position our spectral analysis framework against three bodies of related work: SSM-specific PEFT methods that identify *what* doesn't work, SSM theoretical foundations that describe architecture without addressing adaptation, and eigenvalue analysis techniques from control theory that we adapt for the PEFT context.

## Parameter-Efficient Fine-Tuning for SSMs

The challenge of adapting SSM architectures with PEFT methods has received significant recent attention. **SSM-PEFT** [1] provides a comprehensive analysis of fine-tuning methods for State Space Models, introducing Sparse Dimension Tuning (SDT) as an alternative to standard LoRA. Their key finding---that LoRA is ineffective on SSM-specific modules---aligns with our observations, but they do not explain *why* this limitation exists or provide criteria for predicting when projection-only adaptation will succeed.

**MambaPEFT** [2] catalogs over 20 PEFT method variants applied to Mamba architectures, finding that PEFT is generally more effective for Mamba than for Transformers on certain tasks. However, their empirical evaluation lacks a principled selection criterion: given a new task, practitioners cannot predict which PEFT configuration will work. Our spectral horizon framework addresses this gap by providing a measurable boundary condition.

**State-offset Tuning** [3] proposes learning an additive offset to the SSM state $h' = h + \text{offset}$, achieving competitive performance without modifying core parameters. While empirically effective, this method lacks theoretical grounding in SSM dynamics. Our analysis suggests state-offset may succeed because it operates on the state directly rather than through projections, potentially enabling a form of implicit memory extension---a hypothesis we leave for future investigation.

The common limitation across these works is their empirical focus: they identify successful and unsuccessful configurations without explaining the underlying mechanism. We contribute a spectral theory that explains *why* projection-only adaptation faces fundamental limits.

## State Space Model Foundations

**Mamba** [4] introduced selective state spaces with input-dependent discretization, achieving Transformer-competitive performance with linear-time inference. The architecture parameterizes the continuous-time state matrix $A$ through $A_{\log}$, with discretization via the zero-order hold: $\bar{A} = \exp(\Delta A)$. Crucially, while the discretization step $\Delta$ is input-dependent, the $A$ matrix itself is fixed after pretraining.

Earlier SSM work including **S4** [5] and **H3** [6] established the theoretical foundations of structured state spaces for sequence modeling. These works focus on architecture design and training dynamics rather than post-hoc adaptation, leaving the PEFT question unaddressed.

**Linear Attention** variants including RWKV [7] and RetNet [8] share the linear-time inference property but differ in their state dynamics formulation. Our eigenvalue analysis methodology could extend to these architectures, though the specific $H_{\text{spec}}$ computation would require adaptation to their implicit state representations.

## Eigenvalue Analysis and Memory in Recurrent Models

The connection between eigenvalue magnitude and memory capacity in recurrent systems is well-established in control theory and dynamical systems. For discrete-time linear systems $h_t = Ah_{t-1} + Bu_t$, eigenvalues $|\lambda| < 1$ ensure stability, with $|\lambda| \to 1$ corresponding to longer memory [9]. The *spectral radius* $\rho(A) = \max_i |\lambda_i|$ determines the asymptotic decay rate.

In the context of RNNs, **vanishing/exploding gradients** [10] are directly linked to eigenvalue magnitude during backpropagation. Techniques including orthogonal initialization [11] and gated mechanisms [12] address these issues by constraining eigenvalue distributions.

However, prior work has not applied eigenvalue analysis to understand PEFT limitations. We introduce the spectral memory horizon $H_{\text{spec}} = -1/\log|\lambda_{\max}|$ as an operationalization of the longest memory timescale, and we show this quantity is measurable from pretrained weights and predictive of adaptation boundaries.

## Our Positioning

These prior works identify *what* doesn't work (SSM-PEFT, MambaPEFT), describe SSM architecture without addressing adaptation (Mamba, S4), or analyze eigenvalues without considering PEFT (control theory). We unify these threads by:

1. **Connecting spectral properties to PEFT effectiveness:** We show that the eigenvalue-derived $H_{\text{spec}}$ determines the boundary beyond which projection-only LoRA cannot succeed.

2. **Eliminating competing mechanisms:** While theory suggested projection modification could redirect energy to slow eigenmodes (EUH), we empirically demonstrate this mechanism is not operative.

3. **Providing a predictive framework:** Given a task's dependency length and a model's $H_{\text{spec}}$, practitioners can predict whether projection-only LoRA is viable before investing in fine-tuning.

This positions our work as the first to bridge SSM spectral theory with PEFT methodology, providing both mechanistic understanding and practical guidance.

## References

[1] SSM-PEFT: Parameter-Efficient Fine-Tuning for State Space Models. ICML 2025.

[2] MambaPEFT: Comprehensive Analysis of PEFT Methods for Mamba Architectures. ICLR 2025.

[3] State-offset Tuning: Simple and Effective Adaptation for State Space Models. ACL 2025.

[4] Gu, A. and Dao, T. Mamba: Linear-Time Sequence Modeling with Selective State Spaces. arXiv:2312.00752, 2023.

[5] Gu, A., Goel, K., and Re, C. Efficiently Modeling Long Sequences with Structured State Spaces. ICLR 2022.

[6] Fu, D. Y., et al. Hungry Hungry Hippos: Towards Language Modeling with State Space Models. ICLR 2023.

[7] Peng, B., et al. RWKV: Reinventing RNNs for the Transformer Era. EMNLP 2023.

[8] Sun, Y., et al. Retentive Network: A Successor to Transformer for Large Language Models. arXiv:2307.08621, 2023.

[9] Goodwin, G. C., Graebe, S. F., and Salgado, M. E. Control System Design. Prentice Hall, 2001.

[10] Bengio, Y., Simard, P., and Frasconi, P. Learning Long-Term Dependencies with Gradient Descent is Difficult. IEEE Transactions on Neural Networks, 1994.

[11] Arjovsky, M., Shah, A., and Bengio, Y. Unitary Evolution Recurrent Neural Networks. ICML 2016.

[12] Hochreiter, S. and Schmidhuber, J. Long Short-Term Memory. Neural Computation, 1997.
