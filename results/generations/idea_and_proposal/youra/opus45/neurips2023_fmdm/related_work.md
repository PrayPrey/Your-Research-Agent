## Related Work

**Related Papers**
1. **Title**: Fine-Tuning Large Vision-Language Models as Decision-Making Agents via Reinforcement Learning (arXiv:2405.10292)
   - **Authors**: Zhai, Bai, Lin, Pan, Tong, Zhou, Suhr, Xie, LeCun, Ma, Levine
   - **Summary**: Demonstrates that Chain-of-Thought reasoning is crucial for VLM decision making, showing that 7B parameter models can outperform GPT-4V when combined with RL and CoT approaches.
   - **Year**: 2024

2. **Title**: Improving Vision-Language-Action Model with Online Reinforcement Learning (iRe-VLA) (arXiv:2501.16664)
   - **Authors**: Guo, Zhang, Chen, Ji, Wang, Hu, Chen
   - **Summary**: Proposes iterative RL+SL training to stabilize VLA training, specifically addressing training instability issues in large models.
   - **Year**: 2025

3. **Title**: What Can RL Bring to VLA Generalization? An Empirical Study
   - **Authors**: Liu, Gao, Wei, Chen, Liao, Wu, Yu, Wang
   - **Summary**: Provides empirical evidence that PPO outperforms GRPO/DPO for VLA training and demonstrates that RL substantially enhances execution generalization capabilities.
   - **Year**: 2025

4. **Title**: VLA-R1: Enhancing Reasoning in Vision-Language-Action Models (arXiv:2510.01623)
   - **Authors**: Ye, Zhang, Wang, Wang, Zhang, Zhu
   - **Summary**: Introduces RLVR with verifiable rewards combined with Chain-of-Thought reasoning to achieve superior generalization in vision-language-action models.
   - **Year**: 2025

5. **Title**: Dualformer
   - **Authors**: Not specified (Meta)
   - **Summary**: Presents a single-model dual-process architecture using randomized trace dropping for decision making.
   - **Year**: 2024

6. **Title**: OpenVLA
   - **Authors**: Kim et al.
   - **Summary**: State-of-the-art open-source vision-language-action model serving as a practical performance baseline.
   - **Year**: 2024

7. **Title**: Diffuser
   - **Authors**: Janner et al.
   - **Summary**: Demonstrates that generative diffusion models can effectively serve as planners for sequential decision making.
   - **Year**: 2022

8. **Title**: DDPO
   - **Authors**: Black et al.
   - **Summary**: Shows that reinforcement learning fine-tuning of diffusion models is feasible and effective.
   - **Year**: 2023

**Key Challenges**
1. **Training Instability in Large Models**: VLA models suffer from training instability when applying reinforcement learning, requiring specialized techniques like iterative RL+SL to stabilize the training process.

2. **Lack of Vision-Language Integration in Generative Planners**: Diffusion-based planning approaches (e.g., Diffuser) have not been integrated with vision-language understanding capabilities, limiting their applicability to multimodal decision-making scenarios.

3. **RL for Diffusion Models Limited to Non-Decision Domains**: While RL fine-tuning of diffusion models has been demonstrated (e.g., DDPO), these approaches have been applied to image generation rather than decision-making tasks.

4. **Architectural Design for Dual-Process Reasoning**: Existing dual-process approaches use single-model architectures with techniques like randomized trace dropping, whereas separating proposal and deliberation into distinct modules with explicit interfaces remains underexplored.

5. **Generalization in VLA Execution**: Standard training approaches for VLAs show limited execution generalization, requiring RL-based methods to substantially improve performance on novel scenarios.
