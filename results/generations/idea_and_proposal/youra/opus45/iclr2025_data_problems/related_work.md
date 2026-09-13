## Related Work

**Related Papers**
1. **Title**: What is Your Data Worth to GPT? LLM-Scale Data Valuation with Influence Functions (arXiv:2405.13954)
   - **Authors**: Choe et al.
   - **Summary**: Introduces LoGra, achieving 6,500x throughput improvement for LLM-scale attribution, providing the calibration data foundation for AC-PMRS.
   - **Year**: 2024

2. **Title**: Mechanistic Data Attribution: Tracing the Training Origins of Interpretable LLM Units (arXiv:2601.21996)
   - **Authors**: Chen et al.
   - **Summary**: Causally validated that repetitive structural data (LaTeX, XML) acts as mechanistic catalyst for memorization, supporting the core assumption of feature-memorization correlation.
   - **Year**: 2026

3. **Title**: LoRIF: Low-Rank Influence Functions for Scalable Training Data Attribution (arXiv:2601.21929)
   - **Authors**: Li et al.
   - **Summary**: Achieves 20x storage reduction enabling gradient-based training data attribution at 70B scale, validating scalability of attribution-based approaches.
   - **Year**: 2026

4. **Title**: DE-COP: Detecting Copyrighted Content in Language Models Training Data
   - **Authors**: Duarte et al.
   - **Summary**: Provides reactive detection of copyrighted content achieving 72% accuracy on black-box models.
   - **Year**: 2024

5. **Title**: Assessing and Mitigating Data Memorization Risks in Fine-Tuned LLMs (arXiv:2508.14062)
   - **Authors**: Ramakrishnan & Balaji
   - **Summary**: Demonstrates that fine-tuning increases privacy leakage from 0-5% to 60-75%, validating the urgency of proactive approaches to memorization risks.
   - **Year**: 2025

6. **Title**: Machine Unlearning of Pre-trained LLMs
   - **Authors**: Yao et al.
   - **Summary**: Achieves 10^5x efficiency compared to retraining for machine unlearning, but remains a reactive approach to addressing memorization.
   - **Year**: 2024

7. **Title**: Supply Chain Provenance (Cross-Domain)
   - **Authors**: Not specified
   - **Summary**: Achieves 91.2% traceability via tagging at origin, providing an inspirational pattern for data ingestion risk scoring approaches.
   - **Year**: 2025

**Key Challenges**
1. **Reactive vs. Proactive Detection**: Existing approaches like DE-COP and machine unlearning operate reactively after memorization has occurred, rather than preventing memorization risks proactively during data ingestion.

2. **Scalability of Attribution Methods**: Traditional training data attribution methods face significant computational and storage barriers when scaling to large language models (70B+ parameters), requiring innovations like low-rank approximations.

3. **Fine-tuning Amplifies Memorization**: Fine-tuning dramatically increases privacy leakage risks (from 0-5% to 60-75%), creating urgent need for proactive risk assessment before training.

4. **Feature-Memorization Correlation**: Understanding which data characteristics (e.g., repetitive structural patterns in LaTeX, XML) mechanistically contribute to memorization remains an active research challenge requiring causal validation.

5. **Cross-Domain Provenance Tracking**: Adapting supply chain traceability concepts to data ingestion pipelines for ML training requires novel approaches to risk scoring at the point of origin.
