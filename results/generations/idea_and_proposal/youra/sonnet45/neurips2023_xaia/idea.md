# Title
Stakeholder-Adaptive XAI Validation Framework: Enabling Cross-Domain Explainability Comparison Through Meta-Learned Metric Calibration

# Motivation
Current XAI validation methods are domain-specific and incommensurable—radiologists assess medical imaging explanations differently than auditors evaluate fairness explanations. This fragmentation prevents objective cross-domain comparison of XAI effectiveness, hindering systematic progress and knowledge transfer. As XAI applications proliferate across healthcare, fairness, law, and science, practitioners lack evidence-based guidance for selecting methods that work across contexts.

# Main Idea
We hypothesize that stakeholder type (clinician, auditor, end-user, researcher) serves as a bridging variable enabling cross-domain XAI validation. Our framework uses meta-learning to calibrate heterogeneous domain-specific metrics (clinical accuracy, statistical parity, user comprehension) into unified multi-dimensional effectiveness profiles capturing accuracy, trust, comprehension, and fairness.

**Core mechanism:** Meta-learning maps (domain metric, stakeholder type, domain) → calibrated profile, preserving within-domain validity (ρ≥0.8) while enabling cross-domain comparison (target ρ≥0.7).

**Methodology:** 80 stakeholders evaluate 20 XAI systems (10 healthcare, 10 fairness) using domain-native metrics. Meta-learned calibration produces comparable rankings validated against stakeholder consensus.

**Expected impact:** First objective cross-domain XAI effectiveness benchmark, enabling evidence-based method selection and systematic knowledge transfer across domains while maintaining domain-specific validation rigor.