## Related Work

**Related Papers**

1. **Title**: SVFit: Parameter-Efficient Fine-Tuning of Large Pre-Trained Models using Singular Value Decomposition
   - **Authors**: Sun et al.
   - **Summary**: Demonstrates 99% task information captured in top-r singular values for task adaptation with 16× fewer parameters than LoRA while maintaining performance across NLU, vision, and LLM tasks.
   - **Year**: 2024

2. **Title**: Soft Weighted Unlearning
   - **Authors**: Qiao et al.
   - **Summary**: Uses influence functions to identify critical parameters for selective unlearning with gradient-based approximation to avoid expensive Hessian computation cost.
   - **Year**: 2025

3. **Title**: Bias-Aware Unlearning
   - **Authors**: Aylapuram et al.
   - **Summary**: Achieves 94-97% demographic parity improvement with <5% accuracy loss via selective forgetting, demonstrating feasibility of post-hoc bias removal through full-model updates.
   - **Year**: 2025

4. **Title**: Transfer Unlearning
   - **Authors**: Lu et al.
   - **Summary**: Empirically demonstrates cross-domain transfer where gender debiasing mitigates race/religion bias in LLMs through masked language modeling experiments.
   - **Year**: 2024

5. **Title**: VectorInstitute/bias-mitigation-unlearning (GitHub)
   - **Authors**: Not specified
   - **Summary**: Provides LLM bias mitigation implementation patterns (no parameter-efficient variants available).
   - **Year**: Not specified

6. **Title**: Fairness Through Awareness
   - **Authors**: Dwork et al.
   - **Summary**: Individual fairness methods treating similar individuals similarly regardless of group membership.
   - **Year**: Not specified

**Key Challenges**

1. **SVD Transfer to Unlearning**: SVFit's SVD approach has been validated for task adaptation (adding capabilities) but remains untested for unlearning (removing capabilities). Adding vs. removing information may utilize different subspaces.

2. **Bias Concentration Assumption**: No validation exists that bias information concentrates in identifiable singular values (>80% bias gradient in top-k) rather than being uniformly distributed across all parameters in neural networks.

3. **PEFT-Scale Cross-Bias Transfer**: While Lu et al. 2024 demonstrated cross-bias transfer at full model scale, the magnitude at PEFT scale (<0.1% parameters) remains unvalidated. Transfer magnitude variability (20-80%) across datasets, model architectures, and attribute pairs needs quantification.

4. **Parameter Efficiency vs. Unlearning Effectiveness Trade-off**: Tension exists between Aylapuram et al. 2025's full model bias-aware unlearning (94-97% improvement) and SVFit's low-rank approximation efficiency. Whether efficiency transfers when operating in opposite directions (removing vs. adding information) is unknown.

5. **Group Fairness Limitations**: Current approaches target demographic parity and equalized odds (group-level metrics) but do not address individual fairness or intersectional bias (e.g., bias against Black women specifically).

6. **Influence Function Computational Cost**: Gradient-based approximations scale O(n), Hessian-based approaches scale O(n²). For 10B+ parameter models, this computational overhead becomes non-trivial despite being cheaper than full unlearning.

7. **Post-Hoc Correction Inefficiency**: Unlearning bias post-deployment is inherently less efficient than training on balanced data from scratch, limiting applicability to scenarios where retraining is prohibitively expensive.

8. **Adversarial Bias Resistance**: Gradient-based unlearning methods may fail against adversarially designed bias (malicious data poisoning designed to resist unlearning).
