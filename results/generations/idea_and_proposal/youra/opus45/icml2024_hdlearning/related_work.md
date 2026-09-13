## Related Work

**Related Papers**
1. **Title**: Frequency Regularization: Unveiling the Spectral Inductive Bias (arXiv:2512.22192)
   - **Authors**: Jiahao Lu
   - **Summary**: Introduces the SSR metric to quantify low-pass filtering intensity in neural networks, demonstrating that L2 regularization suppresses high-frequency components by 3x.
   - **Year**: 2025

2. **Title**: On the Local Complexity of Linear Regions in Deep ReLU Networks (OpenReview:id2CfAgEAk)
   - **Authors**: Niket Patel, Guido Montufar
   - **Summary**: Proposes local complexity (LRD) as a measure of linear region density over input distributions, establishing connections to feature learning and adversarial robustness.
   - **Year**: 2025

3. **Title**: Deep Networks Always Grok and Here is Why (Semantic Scholar:69d15a3ec038)
   - **Authors**: Humayun et al.
   - **Summary**: Demonstrates that linear region phase transitions govern grokking behavior, with local complexity explaining the emergence of generalization.
   - **Year**: 2024

4. **Title**: SGD Performs Variational Inference (Semantic Scholar:940912cfc919)
   - **Authors**: Pratik Chaudhari, Stefano Soatto
   - **Summary**: Shows that SGD minimizes a modified potential with an entropy term, providing theoretical foundations for understanding how gradient-flow dynamics affect bias selection.
   - **Year**: 2017

5. **Title**: Grokking: Generalization Beyond Overfitting (Semantic Scholar:a1d1983a7b19)
   - **Authors**: Power et al.
   - **Summary**: Demonstrates that neural networks can achieve generalization well past the point of overfitting on algorithmic datasets, establishing a key experimental paradigm.
   - **Year**: 2022

6. **Title**: Li2 Framework (Tian et al.)
   - **Authors**: Tian et al.
   - **Summary**: Proposes a single-bias energy framework for predicting grokking behavior in neural networks.
   - **Year**: 2025

7. **Title**: Geiger Phase Diagrams (Geiger et al.)
   - **Authors**: Geiger et al.
   - **Summary**: Develops training regime phase diagrams distinguishing between lazy and rich learning regimes in neural networks.
   - **Year**: 2020

8. **Title**: Are All Linear Regions Created Equal? (PMLR v151)
   - **Authors**: Gamba et al.
   - **Summary**: Establishes correlation between LRD and deep double descent phenomena, showing that density alone is insufficient for characterizing complexity.
   - **Year**: 2022

9. **Title**: Unified View of Grokking, Double Descent (Semantic Scholar:7d417465bdf2)
   - **Authors**: Huang et al.
   - **Summary**: Proposes a circuits competition framework that connects grokking and double descent phenomena under a unified theoretical perspective.
   - **Year**: 2024

**Key Challenges**
1. **Single-Bias Limitation**: Existing frameworks like Li2 focus on single-bias energy models, lacking the ability to capture multi-bias competition dynamics and phase diagrams.
2. **Regime Specificity**: Prior phase diagram approaches (e.g., Geiger) focus on distinguishing lazy vs. rich regimes rather than bias-specific transitions within the rich regime.
3. **Insufficient Complexity Metrics**: Linear region density alone is insufficient for characterizing network complexity, motivating the need for multi-metric approaches.
4. **Lack of Quantitative Prediction**: While unified frameworks connecting grokking and double descent exist, they lack quantitative prediction methodology for phase transitions.
