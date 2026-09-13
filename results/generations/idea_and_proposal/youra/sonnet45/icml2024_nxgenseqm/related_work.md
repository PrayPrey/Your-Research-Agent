## Related Work

**Related Papers**

1. **Title**: The Information Bottleneck Method
   - **Authors**: Tishby, N., Pereira, F. C., & Bialek, W.
   - **Summary**: Establishes that optimal compression preserves minimal sufficient statistics for tasks, providing the theoretical foundation for why compression forces task-relevant encoding through rate-distortion objectives.
   - **Year**: 1999

2. **Title**: Understanding and Improving Length Generalization in Recurrent Models
   - **Authors**: Ricardo Buitrago Ruiz, Albert Gu
   - **Summary**: Identifies the "unexplored states hypothesis" showing that SSMs fail at length generalization because training exposes limited state distribution, and proposes a post-hoc 500-step intervention with Gaussian noise initialization.
   - **Year**: 2025

3. **Title**: Randomized Positional Encodings Boost Length Generalization of Transformers
   - **Authors**: Anian Ruoss, Grégoire Delétang, Tim Genewein, et al.
   - **Summary**: Demonstrates that randomizing positional encodings during training simulates longer positions, achieving +12% length out-of-distribution accuracy through distribution augmentation.
   - **Year**: 2023

4. **Title**: Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality
   - **Authors**: Tri Dao, Albert Gu
   - **Summary**: Establishes state space duality framework showing Transformers and SSMs are mathematically connected via semiseparable matrices, justifying that solutions may transfer across architectures.
   - **Year**: 2024

5. **Title**: Vision Mamba: Efficient Visual Representation Learning with Bidirectional State Space Model
   - **Authors**: Lianghui Zhu, Bencheng Liao, Qian Zhang, et al.
   - **Summary**: Demonstrates bidirectional SSM architecture for vision tasks, showing SSM viability beyond language modeling for image classification and object detection.
   - **Year**: 2024

6. **Title**: Mamba-360: Survey of State Space Models as Transformer Alternative for Long Sequence Modelling
   - **Authors**: B. N. Patro, V. Agneeswaran
   - **Summary**: Provides comprehensive SSM taxonomy documenting current landscape, limitations, and evolution, identifying length generalization as an open research problem.
   - **Year**: 2024

7. **Title**: From S4 to Mamba: A Comprehensive Survey on Structured State Space Models
   - **Authors**: Shriyank Somvanshi, Md Monzurul Islam, et al.
   - **Summary**: Traces SSM evolution from S4 through Mamba, analyzing computational efficiency, memory optimization, and architectural developments in the SSM lineage.
   - **Year**: 2025

8. **Title**: Transformers Can Achieve Length Generalization But Not Robustly
   - **Authors**: Yongchao Zhou, Uri Alon, Xinyun Chen, et al.
   - **Summary**: Shows transformers achieve 2.5× length extrapolation but with fragile performance dependent on seed and format, demonstrating the length generalization challenge spans architectures.
   - **Year**: 2024

9. **Title**: How Many Pretraining Tasks Are Needed for In-Context Learning of Linear Regression?
   - **Authors**: Jingfeng Wu, Difan Zou, Zixiang Chen, et al.
   - **Summary**: Establishes in-context learning statistical foundations showing Bayes optimal performance with few tasks, providing theoretical precedent for understanding emergent capabilities through principled frameworks.
   - **Year**: 2023

10. **Title**: Chain-of-Thought Reasoning Without Prompting
    - **Authors**: Xuezhi Wang, Denny Zhou
    - **Summary**: Demonstrates chain-of-thought reasoning is intrinsic via decoding methods, showing that capabilities can be elicited through training and inference modifications rather than explicit prompting.
    - **Year**: 2024

11. **Title**: MoE-Mamba: Efficient Selective State Space Models with Mixture of Experts
    - **Authors**: Maciej Pióro, Kamil Ciebiera, Krystian Król, et al.
    - **Summary**: Demonstrates SSM+MoE combination achieves 2.35× training speedup, providing a potential future direction for combining bottleneck compression with mixture of experts for efficiency and robustness.
    - **Year**: 2024

**Key Challenges**

1. **Limited State Distribution Exposure**: SSMs trained on fixed-length sequences (e.g., 2k tokens) only expose the model to a limited state distribution, causing failure when tested on longer sequences due to unexplored state spaces.

2. **Length Out-of-Distribution Generalization**: Both Transformers and SSMs struggle with robust length generalization beyond training sequence lengths, with performance being fragile and dependent on factors like random seeds and input formats.

3. **Post-Hoc Intervention Complexity**: Current solutions like Ruiz & Gu's 500-step noise injection require separate fine-tuning stages after pre-training, adding deployment complexity despite minimal compute overhead (~0.1%).

4. **Compression-Performance Tradeoff**: Excessive compression (α < 0.2) may discard necessary information and harm task performance, while insufficient compression (α > 0.9) provides inadequate state distribution expansion.

5. **Cross-Architecture Solutions**: While Transformers benefit from positional encoding augmentation (randomized PE), SSMs require different approaches for state space augmentation, indicating architecture-specific solutions are needed.

6. **Hyperparameter Sensitivity**: Information bottleneck approaches require tuning multiple hyperparameters including compression schedule (α_start, α_end, progression) and rate-distortion weight (λ), with optimal values potentially varying across domains.

7. **Domain Generality**: Optimal compression schedules and hyperparameters may differ between domains (language vs. vision) and between SSM architectures (unidirectional vs. bidirectional), limiting universal applicability.

8. **Scale Ambition**: Achieving 64× length extrapolation (2k→128k) is highly ambitious, as most prior work achieves only 4× (2k→8k) or 16× (2k→32k) extrapolation with significant accuracy degradation.
