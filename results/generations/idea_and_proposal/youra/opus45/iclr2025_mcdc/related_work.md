## Related Work

**Related Papers**
1. **Title**: Landscaping Linear Mode Connectivity (arXiv:2406.16300)
   - **Authors**: Singh, Adilova, Kamp, Fischer, Scholkopf, Hofmann
   - **Summary**: Proposes a "mountainside and ridge" model to explain barrier height in loss landscapes, introduces a layer-wise linear mode connectivity predictor, and provides theoretical analysis of barrier height with empirical support.
   - **Year**: 2024

2. **Title**: Task Singular Vectors: Reducing Task Interference in Model Merging (arXiv:2412.00081)
   - **Authors**: Gargiulo, Crisostomi, Bucarelli, Scardapane, Silvestri, Rodolà
   - **Summary**: Demonstrates that 10% of parameters (top singular vectors) retain 99% accuracy and introduces TSV-Merge which combines compression with interference reduction for model merging.
   - **Year**: 2024

3. **Title**: A Unified Analysis for Finite Weight Averaging (arXiv:2411.13169)
   - **Authors**: Wang, Shen, Tao, Sun, Zheng, Tao
   - **Summary**: Establishes a convergence bound of O(log(T/k)/√T) for weight averaging and provides theoretical explanation for the advantage of finite weight averaging over standard SGD.
   - **Year**: 2024

4. **Title**: Demystifying Mergeability: Interpretable Properties to Predict Model Merging Success (arXiv:2601.22285)
   - **Authors**: Zhou, Zhao, Yu, Rodolà
   - **Summary**: Identifies subspace overlap and gradient alignment metrics as foundational, method-agnostic prerequisites for model compatibility in merging scenarios.
   - **Year**: 2026

5. **Title**: Model Soups: Averaging Weights of Fine-Tuned Models (arXiv:2203.05482)
   - **Authors**: Wortsman, Ilharco, Gadre et al.
   - **Summary**: Foundational work demonstrating that weight averaging is effective for models residing in the same low error basin, establishing key principles for model merging approaches.
   - **Year**: 2022

**Key Challenges**
1. **Lack of Predictive Metrics for Merge Success**: Current model merging implementations (e.g., TIES merging) lack predictive metrics to assess merge quality before execution, requiring trial-and-error approaches.
2. **No Pre-Merge Quality Prediction for Adapter Composition**: Existing adapter composition methods such as LoRA lack mechanisms to predict merge quality prior to combining adapters.
3. **Task Interference in Model Merging**: When merging models fine-tuned on different tasks, interference between task-specific parameters degrades performance, requiring methods to identify and isolate critical parameter subsets.
4. **Understanding Loss Landscape Barriers**: The relationship between loss landscape geometry and successful model merging remains incompletely characterized, with barrier height being a key factor affecting merge outcomes.
