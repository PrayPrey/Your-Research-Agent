## Related Work

**Related Papers**
1. **Title**: Luo et al. (2023) - Catastrophic Forgetting Increases with Model Scale
   - **Authors**: Not specified
   - **Summary**: Empirical validation showing catastrophic forgetting increases as model scale grows from 1B to 7B parameters. Provides evidence that larger foundation models are more susceptible to forgetting in continual learning scenarios.
   - **Year**: 2023
   - **Citations**: 518

2. **Title**: PIECE - Parameter Importance-based Continual Learning with 0.1% Parameter Updates (Wang, 2025)
   - **Authors**: Wang
   - **Summary**: Demonstrates that updating only 0.1% of parameters can maintain model capabilities in continual learning, but lacks flexibility for adaptive method selection based on task characteristics.
   - **Year**: 2025

3. **Title**: SSR - Self-Synthesized Replay with LoRA (Huang, 2024)
   - **Authors**: Huang
   - **Summary**: Combines LoRA parameter-efficient fine-tuning with self-synthesized replay for continual learning. Effective for high-forgetting multi-domain scenarios but uses fixed configuration rather than task-adaptive selection.
   - **Year**: 2024

4. **Title**: MoE-CT - Mixture of Experts for Continual Training (Li, 2024)
   - **Authors**: Li
   - **Summary**: Uses fixed Mixture of Experts (MoE) architecture for catastrophic forgetting mitigation through architectural isolation. Lacks method diversity and task-adaptive configuration.
   - **Year**: 2024

5. **Title**: DisCo - Domain Shift and Catastrophic Forgetting (Chen & Zhou, 2024)
   - **Authors**: Chen & Zhou
   - **Summary**: Demonstrates that domain shift magnitude affects catastrophic forgetting severity in continual learning scenarios. Provides empirical evidence for the relationship between task characteristics and forgetting.
   - **Year**: 2024

6. **Title**: LoRA: Low-Rank Adaptation of Large Language Models (Hu et al., 2021)
   - **Authors**: Hu et al.
   - **Summary**: Foundational work on parameter-efficient fine-tuning using low-rank matrix decomposition. Updates less than 1% of parameters while maintaining performance, widely adopted as default method in continual learning research.
   - **Year**: 2021

7. **Title**: MAML - Model-Agnostic Meta-Learning
   - **Authors**: Not specified
   - **Summary**: Meta-learning framework demonstrating strong generalization capabilities through fast adaptation with few gradient steps. Provides theoretical foundation for meta-learning approaches in continual learning.
   - **Year**: Not specified

8. **Title**: Model Reference Adaptive Control (MRAC)
   - **Authors**: Not specified
   - **Summary**: Adaptive control system framework where controller monitors tracking error and adjusts parameters online to minimize deviation from reference model. Inspired the online adaptation mechanism in ADORE hypothesis.
   - **Year**: Not specified
   - **Domain**: Control Theory (cross-domain inspiration)

**Key Challenges**
1. **Catastrophic Forgetting at Scale**: Catastrophic forgetting increases with foundation model scale (1B→7B parameters), making continual learning more challenging for larger models that are increasingly deployed in practice.

2. **Lack of Unified Framework**: Parameter-efficient methods (LoRA, Adapters) and forgetting mitigation strategies (EWC, Replay) are studied separately. No unified framework exists for systematically selecting optimal combinations based on task characteristics.

3. **Fixed Strategy Limitations**: Existing work (PIECE, SSR, MoE-CT) uses fixed configurations that cannot adapt to varying task characteristics and forgetting severity. One-size-fits-all approaches are either too conservative (wasting compute) or too aggressive (insufficient forgetting mitigation).

4. **Meta-Training Generalization**: Concern that meta-learning approaches may overfit to meta-training domains and fail to generalize to unseen task distributions and domains in deployment.

5. **Method Composability**: Integration complexity when combining HuggingFace PEFT library, Avalanche framework strategies, and custom replay mechanisms into a unified training loop for continual learning.

6. **Computational Overhead**: Adaptive orchestration systems must maintain low overhead (<5% of training time) to be practical, including task encoding, prediction, and real-time monitoring costs.

7. **Task Characteristic Predictivity**: Challenge of automatically extracting features (domain shift, data size, vocabulary overlap, distribution shift) that reliably predict catastrophic forgetting severity across diverse task sequences.

8. **Online Adaptation Stability**: Risk that noisy forgetting signals during training cause excessive configuration adaptations, potentially degrading performance rather than improving it through unstable parameter adjustments.
