## Related Work

**Related Papers**
1. **Title**: Classification Utility, Fairness, and Compactness via Tunable Information Bottleneck and Rényi Measures (arXiv:2206.10043)
   - **Authors**: Gronowski et al.
   - **Summary**: Demonstrates that variational Information Bottleneck (RFIB) successfully balances utility-fairness trade-off in tabular classification, providing theoretical foundation for IB-based fairness approaches.
   - **Year**: 2022

2. **Title**: Privacy for Fairness: Information Obfuscation for Fair Representation Learning with Local Differential Privacy (arXiv:2402.10473)
   - **Authors**: Xie et al.
   - **Summary**: Shows that LDP randomizers enhance fairness by constraining sensitive information disclosure, proving privacy-fairness synergy rather than conflict.
   - **Year**: 2024

3. **Title**: PFGuard: A Generative Framework with Privacy and Fairness Safeguards (arXiv:2410.02246)
   - **Authors**: Kim, Roh, Heo, Whang
   - **Summary**: Proposes an ensemble of multiple teacher models to resolve privacy-fairness conflicts, achieving differential privacy guarantees and fairness convergence simultaneously.
   - **Year**: 2025 (ICLR)

4. **Title**: Privacy-Preserving Fair Synthetic Tabular Data (arXiv:2503.02968)
   - **Authors**: Sarmin et al.
   - **Summary**: Introduces PF-WGAN which demonstrates balanced trade-off among utility, privacy, and fairness for tabular data generation.
   - **Year**: 2025

5. **Title**: CTGAN - Conditional Tabular GAN
   - **Authors**: Not specified
   - **Summary**: Serves as a utility baseline for conditional tabular data generation.
   - **Year**: Not specified

6. **Title**: DP-CTGAN - Differentially Private CTGAN
   - **Authors**: Not specified
   - **Summary**: Serves as a privacy baseline combining differential privacy with conditional tabular GAN.
   - **Year**: Not specified

7. **Title**: FairTabGen - Fairness-aware tabular generation
   - **Authors**: Not specified
   - **Summary**: Serves as a fairness baseline for fairness-aware tabular data generation.
   - **Year**: Not specified

8. **Title**: Assessment of differentially private synthetic data for utility and fairness
   - **Authors**: Pereira et al. (Microsoft AI for Good)
   - **Summary**: Demonstrates tension between differential privacy and fairness in end-to-end ML pipelines.
   - **Year**: 2024

9. **Title**: Tabular Data Synthesis with Differential Privacy: A Survey
   - **Authors**: Yang et al.
   - **Summary**: Comprehensive survey that identifies the lack of a unified privacy-fairness-utility framework in the field.
   - **Year**: 2024

**Key Challenges**
1. **Privacy-Fairness Tension**: Existing work demonstrates inherent tension between differential privacy and fairness objectives in end-to-end ML pipelines, making simultaneous optimization difficult.
2. **Lack of Unified Framework**: The field lacks a unified framework that jointly addresses privacy, fairness, and utility objectives in synthetic tabular data generation.
3. **Trade-off Balancing**: Achieving balanced trade-offs among utility, privacy, and fairness remains challenging, with most approaches optimizing for one or two objectives at the expense of others.
