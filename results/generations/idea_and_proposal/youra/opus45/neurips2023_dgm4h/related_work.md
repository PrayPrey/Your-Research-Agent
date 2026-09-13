## Related Work

**Related Papers**
1. **Title**: Fine-grained evaluation of large language models in medicine using non-parametric cognitive diagnostic modeling (arXiv/Nature: s41598-026-36627-7)
   - **Authors**: Tianpeng Zheng, Jiayi Liu, Shicong Feng, Zhehan Jiang
   - **Summary**: Demonstrates that non-parametric cognitive diagnostic models can profile AI performance across 22 medical subdomains, revealing that models with similar total scores exhibit different mastery patterns across clinical competencies.
   - **Year**: 2026

2. **Title**: The challenge of cognitive science for medical diagnosis (PMC9911579)
   - **Authors**: Pat Croskerry et al.
   - **Summary**: Establishes that expert disagreement in medical diagnosis reflects genuine clinical ambiguity through dual-process reasoning rather than simple annotation noise.
   - **Year**: 2023

3. **Title**: Hardness-Aware Model Evaluation (HaME)
   - **Authors**: Mingzhi Xu et al.
   - **Summary**: Introduces B-Gap, HaPrecision, and HaRecall metrics that better identify brittle AI systems through asymmetric cost-benefit analysis of model performance on cases of varying difficulty.
   - **Year**: 2025

4. **Title**: How to Evaluate Medical AI (arXiv:2509.11941)
   - **Authors**: Ilia Kopanichuk et al.
   - **Summary**: Demonstrates that inter-expert variability often exceeds AI-human variability and proposes RPAD/RRAD relative metrics for fairer comparison between AI systems and human experts.
   - **Year**: 2025

5. **Title**: GMAI-MMBench: Comprehensive Multimodal Evaluation Benchmark
   - **Authors**: P. Chen et al.
   - **Summary**: Presents a large-scale benchmark spanning 284 datasets and 38 modalities for medical AI evaluation, though limited to classification tasks with single ground-truth approaches rather than generation.
   - **Year**: 2024

6. **Title**: AgentClinic: Multimodal Agent Benchmark
   - **Authors**: S. Schmidgall et al.
   - **Summary**: Demonstrates that sequential decision-making in clinical scenarios reduces AI accuracy by 10x compared to static benchmarks, validating the need for dynamic validation approaches.
   - **Year**: 2024

7. **Title**: MEDFAIR: Benchmarking Fairness for Medical Imaging
   - **Authors**: Yongshuo Zong, Yongxin Yang, Timothy Hospedales
   - **Summary**: Reveals a 30% fairness gap between demographic subgroups in medical imaging AI and shows that state-of-the-art bias mitigation algorithms do not significantly improve over empirical risk minimization.
   - **Year**: 2022

8. **Title**: Evaluation metrics in medical imaging AI
   - **Authors**: Burak Kocak et al.
   - **Summary**: Argues that multi-metric, context-aware evaluation is essential for medical AI and that foundation models require broader evaluation frameworks beyond traditional performance metrics.
   - **Year**: 2025

**Key Challenges**
1. **Aggregate Score Masking**: Models with similar total scores can exhibit vastly different mastery patterns across medical subdomains, making aggregate metrics insufficient for clinical deployment decisions.

2. **Expert Disagreement as Signal**: Clinical ambiguity manifests as genuine expert disagreement through dual-process reasoning, which current evaluation frameworks incorrectly treat as annotation noise rather than meaningful clinical uncertainty.

3. **Static vs. Dynamic Evaluation Gap**: Sequential clinical decision-making dramatically reduces AI accuracy compared to static benchmark performance, indicating that current evaluation paradigms fail to capture real-world clinical complexity.

4. **Single Ground-Truth Limitations**: Existing comprehensive benchmarks focus on classification with single ground-truth approaches, inadequately addressing generative medical AI tasks where multiple valid outputs exist.

5. **Demographic Fairness Gaps**: Significant performance disparities exist between demographic subgroups, and current bias mitigation techniques provide minimal improvement over baseline methods.

6. **Metric Insufficiency for Foundation Models**: Traditional evaluation metrics are inadequate for assessing foundation models in medical contexts, requiring multi-metric and context-aware evaluation frameworks.
