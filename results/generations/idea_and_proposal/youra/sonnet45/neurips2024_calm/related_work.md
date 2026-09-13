## Related Work

**Related Papers**

1. **Title**: Causality: Models, Reasoning, and Inference (2nd ed.)
   - **Authors**: Pearl, J.
   - **Summary**: Foundational work establishing Pearl's three-rung causal hierarchy (Association, Intervention, Counterfactual) that provides the theoretical framework for structured causal reasoning evaluation.
   - **Year**: 2009

2. **Title**: CLadder: Assessing Causal Reasoning in Language Models (arXiv:2312.04350)
   - **Authors**: Not specified
   - **Summary**: Peer-reviewed benchmark (causalNLP/cladder) for evaluating LLM causal reasoning across Pearl's hierarchy, showing best LLM performance of 57.6% accuracy with no diagnostic insights into failure modes.
   - **Year**: Not specified

3. **Title**: A Mathematical Framework for Transformer Circuits
   - **Authors**: Elhage et al.
   - **Summary**: Foundational mechanistic interpretability work establishing circuits as interpretable subgraphs in transformers, demonstrating attention heads implement specific algorithms like induction heads and name movers.
   - **Year**: 2021

4. **Title**: Causal Tracing in Vision-Language Models
   - **Authors**: Li et al.
   - **Summary**: Demonstrates activation patching successfully isolates component contributions in VLMs, showing middle-layer MHSAs aggregate cross-modal information for object recognition, providing direct methodological precedent for this hypothesis.
   - **Year**: 2025

5. **Title**: MechIR: Mechanistic Interpretability for Information Retrieval
   - **Authors**: Parry et al.
   - **Summary**: Shows mechanistic analysis of IR models enables task-specific understanding and performance prediction, demonstrating transferability of interpretability techniques to predict failures in specialized domains.
   - **Year**: 2025

6. **Title**: From Neuropsychology to Mental Structure
   - **Authors**: Shallice
   - **Summary**: Neuroscience methodology establishing lesion study paradigm (ablate region → measure deficits → infer causal role), providing conceptual foundation for systematic ablation approaches to causal localization.
   - **Year**: 1988

7. **Title**: Lee et al. causal reasoning study (scientifically validated relationships)
   - **Authors**: Lee et al.
   - **Summary**: Causal reasoning evaluation using 40,379 scientifically validated causal relationships from economics/finance journals, reporting 57.6% best LLM accuracy and establishing domain-specific benchmark coverage.
   - **Year**: Not specified

**Key Challenges**

1. **Black-box Evaluation Limitations**: Current benchmarks (CLadder, Lee et al.) measure THAT models fail (57.6% accuracy) but provide no diagnostic insights into WHERE failures occur in model architecture, WHY specific operations fail, WHICH components process causal information, or HOW failures differ across Pearl's hierarchy.

2. **Lack of Component-Level Diagnosis**: Existing evaluation produces only aggregate accuracy metrics with no component-level attribution, circuit identification, or actionable guidance for model developers about which specific attention heads or layers to target for improvement.

3. **No Predictive Capability**: State-of-the-art methods offer no predictive power for failure modes on held-out tasks, operating purely post-hoc without ability to proactively diagnose which task types will fail based on model internals.

4. **Coarse Granularity**: Current approaches provide only rung-level analysis (3 categories) without finer-grained understanding of component-level mechanisms (150+ potential components in typical transformers).

5. **Methodological Transfer Uncertainty**: Mechanistic interpretability has proven successful on concrete tasks (object recognition, information retrieval, factual recall) but remains untested for abstract reasoning domains like causal inference, creating uncertainty about cross-domain transferability.

6. **Distributed vs. Localized Processing Unknown**: Fundamental uncertainty exists about whether abstract causal reasoning exhibits localized processing in specialized circuits or distributed processing across entire model, with no prior empirical evidence establishing bounds on mechanistic interpretability for this domain.

7. **Residual Connection Confounds**: Transformer residual connections create attribution challenges where patching one component affects downstream components, complicating isolation of direct causal effects from cascading secondary effects.

8. **Compute Intensity Barriers**: Thorough mechanistic analysis requires 30-50× more compute than standard evaluation (30-50 GPU-hours vs. 1 GPU-hour), limiting the number of models that can be comprehensively analyzed.
