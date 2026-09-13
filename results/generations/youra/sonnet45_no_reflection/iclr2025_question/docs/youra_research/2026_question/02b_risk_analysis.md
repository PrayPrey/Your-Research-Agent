# Risk Analysis Summary - Phase 2B

## Risk-Hypothesis Mapping

| Risk ID | Source | Description | Severity | Affected Hypotheses | Mitigation |
|---------|--------|-------------|----------|---------------------|------------|
| R1 | A1 | SE ground truth insufficient (K=10 not converged) | Medium | H-E1, H-M-integrated | Validation: convergence studies show K=10 sufficient; fallback: increase to K=15-20 |
| R2 | A2 | Layers 24-31 arbitrary, not optimal | High | H-E1, H-M-integrated, H-C1 | Prevention: ablation study across layer ranges; detection: compare performance |
| R3 | A3 | PR unstable with 9 samples (CV > 0.15) | High | H-E1, H-M-integrated | Prevention: bootstrap validation; response: multi-metric ensemble or expand to 12-16 layers |
| R4 | A4 | TruthfulQA-specific, doesn't generalize | Medium | H-E1, H-M-integrated | Scope: document as epistemic QA limitation; future: cross-dataset validation |
| R5 | A5 | Architecture-dependent, Llama-specific | Medium | H-C1 (directly), All (indirectly) | H-C1 tests this explicitly; response: per-architecture calibration protocol |

## Risk Mitigation Strategies

### R1: SE Ground Truth Insufficiency
- **Prevention:** Farquhar et al. validated K=10; convergence studies confirm sufficiency
- **Detection:** If bootstrap SE variance high, flag for investigation
- **Response:** PIVOT to K=15-20 if validation fails; SCOPE to "approximate SE" if convergence issues

### R2: Layer Selection Arbitrary
- **Prevention:** Ablation study in H-M-integrated validates 24-31 empirically
- **Detection:** If other ranges (16-23, 20-27) outperform 24-31, selection is wrong
- **Response:** PIVOT to optimal range; document data-driven justification

### R3: PR Statistical Instability
- **Prevention:** Bootstrap validation (CV < 0.15) in H-E1 protocol
- **Detection:** If CV > 0.20 on bootstrap resamples, PR is too noisy
- **Response:** PIVOT to multi-metric ensemble (PR + eigenvalue decay + condition number); EXPAND to 12-16 layers for more samples

### R4: Dataset-Specific Results
- **Prevention:** TruthfulQA is standard benchmark for epistemic uncertainty
- **Detection:** If cross-domain tests (future work) show poor transfer
- **Response:** SCOPE to "epistemic factual QA" domain; document generalization boundaries

### R5: Architecture Dependence
- **Prevention:** H-C1 explicitly tests Llama-2-7B vs Llama-3-8B
- **Detection:** If |Δρ| > 0.25 in H-C1, architecture-dependence confirmed
- **Response:** SCOPE to Llama-3 specific initially; develop per-architecture calibration protocol

## Critical Risk Summary

**Critical Risks:** 0  
**High Risks:** 2 (R2: Layer selection, R3: PR stability)  
**Medium Risks:** 3 (R1: SE sufficiency, R4: Dataset generalization, R5: Architecture dependence)  
**Low Risks:** 0

**Risk Coverage:** All 5 key assumptions mapped to risks with mitigation strategies. High-severity risks (R2, R3) have explicit validation protocols in hypotheses (H-M ablation, H-E1 bootstrap).
