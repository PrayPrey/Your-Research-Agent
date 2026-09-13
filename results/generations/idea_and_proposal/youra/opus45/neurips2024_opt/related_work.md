## Related Work

**Related Papers**
1. **Title**: Universal Sharpness Dynamics in Neural Network Training
   - **Authors**: Dayal Singh Kalra, Tianyu He, Maissam Barkeshli
   - **Summary**: Explains the edge of stability mechanism through 2-layer linear network analysis, identifies a period-doubling route to chaos, and demonstrates that sharpness phenomenology generalizes to real-world scenarios.
   - **Year**: 2023

2. **Title**: Phase diagram of early training dynamics in deep neural networks
   - **Authors**: Dayal Singh Kalra, Maissam Barkeshli
   - **Summary**: Identifies four distinct training regimes (early transient, saturation, progressive sharpening, edge of stability) and determines critical learning rate values that govern transitions between these phases.
   - **Year**: 2023

3. **Title**: A Scalable Measure of Loss Landscape Curvature (arXiv:2601.16979)
   - **Authors**: Dayal Singh Kalra, Jean-Christophe Gagnon-Audet, Andrey Gromov, et al.
   - **Summary**: Introduces critical sharpness (λ_c) measurement requiring only ~10 forward passes, demonstrated at 7B scale on OLMo-2, enabling practical sharpness tracking for large language models.
   - **Year**: 2026

4. **Title**: Scaling Laws for Neural Language Models
   - **Authors**: Kaplan, McCandlish, Henighan, Brown, et al.
   - **Summary**: Establishes power-law scaling relationships showing larger models are more sample-efficient, providing foundational understanding of optimization-scale interaction.
   - **Year**: 2020

5. **Title**: Super Consistency of Neural Network Landscapes
   - **Authors**: Lorenzo Noci, Alexandru Meterez, Thomas Hofmann, Antonio Orvieto
   - **Summary**: Demonstrates that μP maintains consistent sharpness dynamics across scales with spectral properties independent of network size, enabling hyperparameter transfer.
   - **Year**: 2024

6. **Title**: On the Convergence of Adam and Beyond
   - **Authors**: Reddi, Kale, Kumar
   - **Summary**: Identifies convergence issues with Adam in certain training regimes, suggesting that optimizer choice matters for training stability and performance.
   - **Year**: 2018

**Key Challenges**
1. **Static Optimizer Selection**: Current practice uses fixed optimizers (e.g., Adam) throughout LLM training, failing to adapt to different training phases despite evidence that distinct regimes benefit from different optimization dynamics.

2. **Lack of Dynamic Optimizer Switching**: Existing training infrastructure (DeepSpeed, HuggingFace) implements fixed optimizer schedules without dynamic optimizer switching based on loss landscape analysis.

3. **Regime-Specific Convergence Issues**: Adam exhibits convergence problems in certain training regimes, but existing work identifies this issue without addressing dynamic optimizer selection as a solution.

4. **Implicit Phase Handling**: Learning rate warmup and cooldown approaches implicitly acknowledge different training phases require different optimization dynamics, but do not explicitly leverage optimizer scheduling which could be orthogonal and complementary.
