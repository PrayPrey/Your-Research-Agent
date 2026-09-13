## Related Work

**Related Papers**
1. **Title**: Shortcut learning in deep neural networks
   - **Authors**: Geirhos, Jacobsen, Michaelis, Zemel, Brendel, Bethge, Wichmann
   - **Summary**: Establishes simplicity bias as a fundamental property of deep neural networks and defines a taxonomy for shortcut learning behaviors.
   - **Year**: 2020

2. **Title**: Beyond Distribution Shift: Spurious Features Through the Lens of Training Dynamics
   - **Authors**: Murali, Puli, Ranganath, Batmanghelich
   - **Summary**: Introduces the Prediction Depth methodology for detecting harmful spurious features by analyzing early layer dynamics during training.
   - **Year**: 2023

3. **Title**: Post hoc Explanations may be Ineffective for Detecting Unknown Spurious Correlation
   - **Authors**: Adebayo, Muelly, Abelson, Kim
   - **Summary**: Demonstrates that post-hoc explanation methods fail to detect unknown spurious features, motivating the need for behavioral approaches to spurious correlation detection.
   - **Year**: 2022

4. **Title**: Just Train Twice (JTT)
   - **Authors**: Liu et al.
   - **Summary**: Proposes a two-stage training method that uses misclassification as a single signal to identify and upweight samples affected by spurious correlations.
   - **Year**: 2021

5. **Title**: GroupDRO
   - **Authors**: Sagawa et al.
   - **Summary**: Introduces distributionally robust optimization that leverages group labels to improve worst-group performance under spurious correlations.
   - **Year**: 2019

6. **Title**: SCER: Spurious Correlation-Aware Embedding Regularization
   - **Authors**: Park et al.
   - **Summary**: Achieves state-of-the-art worst-group improvements through embedding regularization techniques, demonstrating ongoing progress in addressing spurious correlations.
   - **Year**: 2025

7. **Title**: ULE: Unlearning from Experience
   - **Authors**: Mitchell et al.
   - **Summary**: Proposes a student-teacher framework that achieves 29-44% worst-group improvement without requiring group labels.
   - **Year**: 2025

**Key Challenges**
1. **Ineffectiveness of Post-hoc Explanations**: Post-hoc explanation methods fail to detect unknown spurious correlations, limiting their utility for identifying harmful features that were not anticipated during model development.

2. **Reliance on Group Labels**: Many effective methods like GroupDRO require explicit group annotations, which are often unavailable or expensive to obtain in real-world settings.

3. **Single-Signal Detection Limitations**: Approaches like JTT rely on misclassification as a single signal for identifying spurious correlations, potentially missing more nuanced patterns of shortcut learning.

4. **Fundamental Simplicity Bias**: Deep neural networks exhibit an inherent tendency toward simplicity bias, making them prone to learning shortcuts rather than robust features, representing a fundamental architectural challenge.

5. **Ongoing Need for Robust Solutions**: Despite recent progress with methods achieving worst-group improvements, the continued development of new approaches indicates that fully addressing spurious correlations remains an open problem.
