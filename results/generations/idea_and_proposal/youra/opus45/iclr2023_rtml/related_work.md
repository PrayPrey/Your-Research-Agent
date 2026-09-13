## Related Work

**Related Papers**
1. **Title**: Neural Networks in the Loop: Learning with Stability and Robustness Guarantees
   - **Authors**: Manchester, Wang, Barbara
   - **Summary**: Demonstrates that IQC theory provides built-in certification of robustness and that direct parameterization avoids the need for SDP solvers, serving as a core theoretical framework for robustness IQC formulation.
   - **Year**: 2026

2. **Title**: A Unified Analysis of First-Order Methods for Smooth Games via Integral Quadratic Constraints (arXiv/Semantic Scholar)
   - **Authors**: Zhang, Bao, Lessard, Grosse
   - **Summary**: Extends the IQC framework to stochastic games and shows that tailored quadratic constraints yield tight convergence bounds, providing foundation for stochastic IQC extension to privacy.
   - **Year**: 2020

3. **Title**: Integral Quadratic Constraints for Neural Networks
   - **Authors**: Grönqvist, Rantzer
   - **Summary**: Formulates IQCs for ReLU and Leaky-ReLU nonlinearities, establishing the technical foundation for applying IQC analysis to transformer activations.
   - **Year**: 2022

4. **Title**: DP-FedLoRA: Privacy-Enhanced Federated Fine-Tuning for On-Device LLMs (arXiv:2509.09097)
   - **Authors**: Xu, Shrestha, Chen, Li, Cai
   - **Summary**: Demonstrates that DP-compatible LoRA fine-tuning is practical and achieves competitive performance, providing evidence that LoRA adapters can satisfy privacy constraints.
   - **Year**: 2025

5. **Title**: Differentially Private and Fair Deep Learning
   - **Authors**: Tran et al.
   - **Summary**: Proposes a Lagrangian dual approach for jointly optimizing differential privacy and fairness in deep learning models.
   - **Year**: 2020

6. **Title**: Certified Robustness for LLMs with Self-Denoising
   - **Authors**: Zhang et al.
   - **Summary**: Achieves certified robustness for large language models through randomized smoothing techniques, serving as a robustness-only baseline.
   - **Year**: 2023

7. **Title**: Safe Pruning LoRA: Robust Distance-Guided Pruning for Safety Alignment (arXiv:2506.18931)
   - **Authors**: Ao, Dong, Hu, Ramchurn
   - **Summary**: Reveals that LoRA fine-tuning can compromise safety alignment and highlights the absence of joint robustness-privacy methods in current approaches.
   - **Year**: 2025

**Key Challenges**
1. **Lack of Controllable Trade-offs**: Existing approaches like Lagrangian dual methods for joint DP and fairness do not provide controllable trade-offs between competing objectives.
2. **Absence of Unified Trustworthiness Guarantees**: Current LoRA fine-tuning methods lack unified guarantees that jointly address robustness and privacy, with fine-tuning potentially compromising safety alignment.
3. **No Joint Robustness-Privacy Method**: The literature reveals a gap in methods that simultaneously certify both robustness and privacy properties for LLM adaptation.
4. **Limited Extension to Privacy Domains**: While IQC frameworks have been applied to robustness and convergence analysis, their extension to privacy certification in stochastic settings remains underexplored.
