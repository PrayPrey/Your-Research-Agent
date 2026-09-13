## Related Work

**Related Papers**
1. **Title**: Formalizing Data Deletion in the Context of the Right to be Forgotten
   - **Authors**: Garg, Goldwasser, Vasudevan
   - **Summary**: Provides the first rigorous formal definition of data deletion using cryptographic indistinguishability games, establishing the theoretical foundation for formal definitions of machine unlearning verification.
   - **Year**: 2020

2. **Title**: Athena: Probabilistic Verification of Machine Unlearning
   - **Authors**: Sommer, Song, Wagh, Mittal
   - **Summary**: Introduces the first MIA-based verification framework achieving 95%+ confidence certification for machine unlearning verification.
   - **Year**: 2022

3. **Title**: Towards Reliable Forgetting: A Survey on Machine Unlearning Verification
   - **Authors**: Xue et al.
   - **Summary**: Presents a taxonomy of behavioral vs parametric verification approaches and identifies existing verification gaps in the machine unlearning literature.
   - **Year**: 2025

4. **Title**: Statistical MIA: Rethinking Membership Inference Attack for Reliable Unlearning Auditing
   - **Authors**: Sun et al.
   - **Summary**: Demonstrates that MIA-based auditing has inherent statistical errors and proposes a training-free SMIA approach to address these limitations.
   - **Year**: 2026

5. **Title**: Fundamental Limits of Membership Inference Attacks on Machine Learning Models
   - **Authors**: Aubinais, Gassiat, Piantanida
   - **Summary**: Establishes theoretical bounds on MIA effectiveness and shows that discretization enhances security against membership inference attacks.
   - **Year**: 2025

6. **Title**: A Duty to Forget, a Right to be Assured? Vulnerabilities in Machine Unlearning
   - **Authors**: Hu, Wang et al.
   - **Summary**: Identifies over-unlearning vulnerabilities in MLaaS contexts and demonstrates that a certification gap exists in current machine unlearning approaches.
   - **Year**: 2023

7. **Title**: ACMIA: Automatic Calibration for Membership Inference Attack
   - **Authors**: Zare Zade et al.
   - **Summary**: Proposes tunable temperature calibration methodology that improves MIA reliability across different model architectures.
   - **Year**: 2025

**Key Challenges**
1. **Single-Attack Verification Limitations**: Existing verification frameworks like Athena rely on single membership inference attacks, which may not provide comprehensive verification coverage.

2. **Inherent Statistical Errors in MIA-based Auditing**: MIA-based approaches for unlearning auditing suffer from inherent statistical errors that affect reliability of verification results.

3. **Theoretical Bounds on MIA Effectiveness**: Fundamental limits exist on how effective membership inference attacks can be, which verification systems must account for in their design.

4. **Certification Gap in Machine Unlearning**: Current approaches lack robust certification mechanisms, particularly in MLaaS contexts where over-unlearning vulnerabilities have been identified.

5. **Cross-Architecture Reliability**: MIA-based verification methods require calibration to maintain reliability across different model architectures.
