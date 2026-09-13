## Related Work

**Related Papers**
1. **Title**: Geometric Regularizers (Xia et al., 2026)
   - **Authors**: Xia et al.
   - **Summary**: Introduced mathematical formulation of dispersive regularizer (L_disp) with proof of collapse prevention in multimodal embedding spaces. Provides the core intervention mechanism for preventing geometric collapse.
   - **Year**: 2026

2. **Title**: Fiber Product (Zhao et al., 2024)
   - **Authors**: Zhao et al.
   - **Summary**: Developed algebraic geometry perspective on cross-modal alignment using fiber product theory. Provides theoretical foundation for meso-level metric design with CCA approximation.
   - **Year**: 2024

3. **Title**: Brain Encoding (Tang et al., 2023)
   - **Authors**: Tang et al.
   - **Summary**: Validated that shared semantic dimensions exist across modalities using brain encoding analysis. Demonstrates RSA (Representational Similarity Analysis) effectiveness for measuring cross-modal alignment, adapted from post-hoc analysis to training-time monitoring.
   - **Year**: 2023

**Key Challenges**
1. **Geometric Collapse Detection**: Current CLIP training lacks automated monitoring for embedding collapse and pathological geometric states, requiring manual inspection or post-hoc analysis to identify issues.

2. **Computational Efficiency vs. Monitoring Granularity**: Computing cross-modal alignment metrics (especially RSA) during training introduces computational overhead that must stay below 5% to be practical, requiring careful optimization through subsampling and approximations.

3. **Intervention Stability**: Introducing geometric regularizers mid-training risks destabilizing the optimization dynamics, requiring conservative policies with warm-up periods, gradual ramp-up, and cooldown mechanisms.

4. **Threshold Calibration Generalization**: Determining when geometric pathologies require intervention depends on dataset-specific dispersion and alignment statistics that don't generalize across datasets, necessitating two-stage calibration (bootstrap + adaptive).

5. **Multi-Scale Monitoring Integration**: Existing work addresses either micro-level (dispersion) or macro-level (alignment) geometric properties in isolation, lacking unified frameworks that monitor and intervene across multiple scales simultaneously.

6. **Performance-Geometry Correlation**: The relationship between geometric health metrics and downstream task performance (zero-shot classification, retrieval) remains empirically underexplored, making it unclear whether geometric interventions translate to practical improvements.
