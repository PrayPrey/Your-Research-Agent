## Related Work

**Related Papers**

1. **Title**: SFI calibration for distributional shift in real-world data (Cheng et al., 2025)
   - **Authors**: Cheng et al.
   - **Summary**: Proposes Sample-Free Isotonic (SFI) regression for recalibrating deployed clinical ML models under distribution shift without requiring labeled calibration samples. Addresses calibration drift in deployed models.
   - **Year**: 2025

2. **Title**: Dynamic healthcare ML: Distribution shift + missingness + timing (Liu et al., 2025)
   - **Authors**: Liu et al.
   - **Summary**: Comprehensive analysis of temporal challenges in healthcare ML including distribution shift, missingness patterns, and irregular timing, demonstrating performance degradation over time with typical 5-10% degradation documented.
   - **Year**: 2025

3. **Title**: Federated learning for privacy-preserving deployment (Bakas et al., 2026)
   - **Authors**: Bakas et al.
   - **Summary**: Federated learning infrastructure for distributed clinical ML deployment, addressing privacy and multi-institutional challenges in healthcare settings.
   - **Year**: 2026

4. **Title**: Adaptive Control Theory: Stability and Performance Guarantees (Åström & Wittenmark, 2020)
   - **Authors**: Åström & Wittenmark
   - **Summary**: Foundational control theory text on adaptive systems covering continuous feedback loops, multi-timescale adaptation, and graduated response strategies for maintaining system stability under changing conditions.
   - **Year**: 2020

5. **Title**: Self-Tuning Regulators in Industrial Control (Bristol, 2018)
   - **Authors**: Bristol
   - **Summary**: Industrial applications of adaptive control demonstrating that online parameter tuning is more efficient than complete system redesign for handling process variations.
   - **Year**: 2018

6. **Title**: How transferable are features in deep neural networks? (Yosinski et al., 2014)
   - **Authors**: Yosinski et al.
   - **Summary**: Empirical study demonstrating that lower layers in neural networks learn general features while upper layers learn task-specific features, establishing layer transferability principles.
   - **Year**: 2014

7. **Title**: Universal Language Model Fine-tuning for Text Classification (ULMFiT) (Howard & Ruder, 2018)
   - **Authors**: Howard & Ruder
   - **Summary**: Discriminative fine-tuning technique where different layers are updated at different rates, with lower layers frozen or lightly tuned, demonstrating feasibility of layer-wise selective updates.
   - **Year**: 2018

8. **Title**: Universal Language Model Fine-tuning (Peters et al., 2019)
   - **Authors**: Peters et al.
   - **Summary**: Partial fine-tuning studies showing that freezing lower layers maintains performance while reducing computational cost.
   - **Year**: 2019

9. **Title**: Overcoming catastrophic forgetting in neural networks (EWC) (Kirkpatrick et al., 2017)
   - **Authors**: Kirkpatrick et al.
   - **Summary**: Elastic Weight Consolidation (EWC) regularization technique preventing catastrophic forgetting during continual learning by constraining updates to important parameters.
   - **Year**: 2017

10. **Title**: Post-deployment monitoring for healthcare ML (Torpmann-Hagen et al., 2024)
    - **Authors**: Torpmann-Hagen et al.
    - **Summary**: Best practices for post-deployment ML monitoring in healthcare covering metrics, alerting, and dashboards for tracking model performance over time.
    - **Year**: 2024

11. **Title**: The ML Test Score: A Rubric for ML Production Readiness (Breck et al., 2017)
    - **Authors**: Breck et al.
    - **Summary**: Google's rubric for assessing ML system production readiness including monitoring, versioning, and rollback capabilities.
    - **Year**: 2017

12. **Title**: The myth of generalizability in clinical prediction models (Futoma et al., 2020)
    - **Authors**: Futoma et al.
    - **Summary**: Empirical study showing clinical ML models degrade severely when transferred across hospitals or time periods, highlighting generalization failures in healthcare settings.
    - **Year**: 2020

13. **Title**: Population-level prediction of type 2 diabetes from claims and lab events (Razavian et al., 2016)
    - **Authors**: Razavian et al.
    - **Summary**: Large-scale clinical prediction system deployed in real healthcare settings, reporting practical deployment challenges including model degradation over time.
    - **Year**: 2016

14. **Title**: Transfer learning in neural networks (Raghu et al., 2019)
    - **Authors**: Raghu et al.
    - **Summary**: Studies on transfer learning demonstrating that lower layers learn general features applicable across domains while upper layers learn task-specific mappings.
    - **Year**: 2019

**Key Challenges**

1. **Distribution Shift in Clinical Data**: Clinical data distributions evolve over time due to demographic changes, treatment protocol updates, and measurement technology changes, causing model performance degradation.

2. **Computational Cost of Model Maintenance**: Full model retraining is computationally expensive (estimated 8 GPU-hours per retrain with 12 retrains/year = 96 GPU-hours/year), creating barriers to sustainable long-term deployment.

3. **Weak Post-Deployment Management**: Most clinical ML systems lack systematic maintenance strategies, relying on ad-hoc manual interventions rather than automated, proactive lifecycle management.

4. **Calibration Drift**: Model output probabilities become miscalibrated over time even when discrimination performance remains stable, affecting clinical decision-making quality.

5. **Feature Stability Uncertainty in Healthcare**: While transfer learning validates lower layer stability in vision domains, it's unclear whether healthcare time series exhibit similar feature stability or more fundamental shifts (new diseases, paradigm-shifting treatments).

6. **Detection Lead Time**: Identifying performance degradation before it drops below clinical acceptability thresholds requires continuous monitoring with appropriate metrics and early warning signals.

7. **Generalization Across Institutions**: Clinical ML models trained at one institution often fail to generalize to other hospitals or time periods, limiting widespread deployment.

8. **Catastrophic Forgetting**: Continual learning approaches that update models continuously face the challenge of forgetting previously learned patterns, requiring regularization techniques that increase computational cost.

9. **Intervention Decision Complexity**: Determining when and how to intervene (recalibrate, retrain specific layers, full retrain, or escalate to human) requires systematic decision protocols rather than manual judgment.

10. **Real-World Deployment Infrastructure**: Operational infrastructure for monitoring, automated retraining pipelines, and escalation workflows is often poorly defined or missing in clinical ML systems.
