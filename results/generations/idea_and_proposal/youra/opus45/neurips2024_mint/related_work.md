## Related Work

**Related Papers**
1. **Title**: SafeSwitch: Steering Unsafe LLM Behavior via Internal Activation Signals (2025)
   - **Authors**: Peixuan Han, Cheng Qian, Xiusi Chen, Yuji Zhang, Denghui Zhang, Heng Ji
   - **Summary**: Proposes a dynamic safety framework using internal state monitoring that reduces harmful outputs by 80% with only 6% parameter tuning, though binary activation leads to 48% over-refusal rates.
   - **Year**: 2025

2. **Title**: Towards Inference-time Category-wise Safety Steering for Large Language Models (2024)
   - **Authors**: Amrita Bhattacharjee, Shaona Ghosh, Traian Rebedea, Christopher Parisien
   - **Summary**: Introduces category-specific steering vectors that enable fine-grained safety control at inference time without requiring model retraining.
   - **Year**: 2024

3. **Title**: Safety is Not Only About Refusal: Reasoning-Enhanced Fine-tuning for Interpretable LLM Safety (2025)
   - **Authors**: Yuyou Zhang, Miao Li, William Jongwon Han, Yi-Fan Yao, Zhepeng Cen, Ding Zhao
   - **Summary**: Presents reasoning-enhanced safety fine-tuning with context-awareness that achieves improved safety-utility tradeoffs through explicit reasoning processes.
   - **Year**: 2025

4. **Title**: OR-Bench: An Over-Refusal Benchmark for Large Language Models (2025)
   - **Authors**: Justin Cui, Wei-Lin Chiang, Ion Stoica, Cho-Jui Hsieh
   - **Summary**: Introduces the first large-scale over-refusal benchmark containing 80,000 prompts across 10 categories for systematically measuring LLM over-refusal behavior.
   - **Year**: 2025

5. **Title**: Tradeoff Analysis (Wolf et al.)
   - **Authors**: Wolf et al.
   - **Summary**: Provides theoretical bounds demonstrating that helpfulness is harmed quadratically with steering intensity in safety interventions.
   - **Year**: 2024

**Key Challenges**
1. **Binary Safety Activation**: Current dynamic safety methods like SafeSwitch use binary activation mechanisms that result in high over-refusal rates (48%), lacking nuanced response modulation.

2. **Safety-Utility Tradeoff**: Strong correlation (Spearman 0.878) exists between safety and over-refusal across LLMs, indicating current methods sacrifice utility to achieve safety improvements.

3. **Static Steering Limitations**: Category-wise safety steering approaches lack context-dependent modulation, applying fixed interventions regardless of specific input characteristics.

4. **Reasoning Overhead**: Context-aware safety methods that use explicit reasoning incur computational overhead, requiring multiple processing steps rather than single forward pass solutions.

5. **Quadratic Helpfulness Degradation**: Theoretical analysis shows helpfulness degrades quadratically with steering intensity, making it difficult to maintain utility while increasing safety interventions.
