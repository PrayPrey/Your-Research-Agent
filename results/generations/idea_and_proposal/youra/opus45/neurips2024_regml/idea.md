# Research Idea

## Title
Certified Unlearning Verification via Multi-Attack Ensemble for GDPR Compliance

## Motivation
GDPR's "right to be forgotten" (Article 17) requires ML service providers to delete user data upon request, but verifying that machine unlearning methods actually remove data influence remains unsolved. Current approaches rely on single attack types (e.g., membership inference) that may miss residual information leakage through other channels. This gap between regulatory requirements and technical verification capabilities creates legal uncertainty for ML deployments and leaves users without meaningful deletion guarantees.

## Main Idea
We propose Certified Unlearning Verification (CUV), a framework that certifies unlearning completeness through statistical indistinguishability testing using a multi-attack ensemble combining membership inference, model inversion, and attribute inference attacks. The core hypothesis: if an unlearned model cannot be distinguished from a never-trained model by any attack in the ensemble (accuracy ≤55% vs. 50% random baseline, p<0.05), then data influence has been practically removed.

The methodology applies all three attacks to unlearned models, using ACMIA-calibrated thresholds for architecture independence. We predict multi-attack verification will detect 15%+ more incomplete unlearning cases than single-attack approaches. The framework enables black-box third-party auditing, providing MLaaS providers with quantifiable compliance certificates. Expected impact includes bridging the gap between probabilistic ML guarantees and regulatory requirements, establishing a practical standard for GDPR-compliant machine unlearning verification.