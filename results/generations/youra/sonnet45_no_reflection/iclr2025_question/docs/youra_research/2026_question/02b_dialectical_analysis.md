# Dialectical Analysis - Phase 2B

## Thesis-Antithesis-Synthesis Framework

### THESIS

**Core Claim:** Under epistemic uncertainty conditions (factual knowledge questions in TruthfulQA), if we extract geometric features (participation ratio, eigenvalue spectrum, condition number) from layers 24-31 hidden states at pre-generation final token position, then these features will achieve Spearman |ρ| > 0.4 correlation with ground-truth semantic entropy, because uncertain model states exhibit lower-dimensional geometric signatures (collapsed subspaces) detectable via spectral analysis of the hidden state manifold.

**Supporting Evidence:**
1. **Theoretical foundation:** INSIDE framework (EigenScore) found hallucinations correlate with lower eigenvalue diversity, supporting collapsed subspace hypothesis
2. **Empirical precedent:** Kossen et al. (2024) demonstrated hidden states predict semantic entropy; we hypothesize intrinsic geometry (no training) carries similar signal
3. **Causal mechanism:** 4-step chain from epistemic uncertainty → subspace collapse → spectral signatures → SE proxy, with each link testable

**Strengths:**
- **Interpretability:** Geometric properties are intrinsic and interpretable (know WHY uncertainty detected), vs black-box probes
- **Production viability:** Single-pass computation (<10ms overhead) enables real-time deployment where sampling methods (500-2000ms) fail
- **Testable predictions:** Clear success criteria (|ρ| > 0.4), falsifiers (|ρ| < 0.3 or wrong direction), and mechanism validation steps

**Expected Outcomes:**
- Primary: Spearman |ρ| > 0.4 between participation ratio and semantic entropy on TruthfulQA test set
- Secondary: Multi-geometric ensemble achieves AUROC > 0.70 for binary uncertainty classification
- Tertiary: Geometric features add ΔAUROC ≥ 0.05 beyond perplexity baseline

---

### ANTITHESIS

**Null Hypothesis (H0):** There is no significant correlation (|ρ| < 0.3 or p > 0.05) between geometric features extracted from pre-generation hidden states and semantic entropy on TruthfulQA. Any observed correlation is spurious and explained by confounds (sequence length, perplexity, token frequency).

**Counter-Arguments:**
1. **Baseline performance:** Farquhar et al. and Kossen et al. achieve AUROC ~0.80 with semantic entropy or trained probes; geometric features may be too weak (target: |ρ| > 0.4 translates to ~AUROC 0.65-0.72, below best baselines)
2. **Mechanism paradox:** Collapsed subspace vs superposition paradox not fully resolved; aleatoric uncertainty may exhibit opposite pattern (higher-dimensional), confounding epistemic detection
3. **Arbitrary choices:** Layer selection (24-31), token position (final pre-generation), and sample count (9 layers) lack empirical justification; may be overfitting to Llama-3-8B specifics

**Potential Failure Points:**
- **R1 (SE sufficiency):** If K=10 sampling doesn't converge, ground truth labels are unreliable
- **R2 (Layer selection):** If layers 24-31 are arbitrary, observed correlation is dataset/model-specific artifact
- **R3 (PR stability):** If 9-layer participation ratio is too noisy (CV > 0.20), features are unreliable for production

**Conditions Under Which H0 Would Be Supported:**
- If |ρ| < 0.3 on TruthfulQA test set (correlation too weak)
- If correlation direction reverses (PR increases with SE, contradicting collapsed subspace)
- If correlation disappears after controlling for confounds (sequence length, perplexity)
- If mechanism step 2 fails: participation ratio doesn't decrease for high-SE questions

---

### SYNTHESIS

**Balanced Assessment:**

The hypothesis H-GeometricUQ-v1 presents a testable claim that intrinsic geometric properties of hidden states can serve as interpretable, production-viable uncertainty proxies. However, the null hypothesis raises valid concerns regarding correlation strength (target |ρ| > 0.4 may be insufficient vs AUROC ~0.80 baselines), mechanism ambiguity (collapsed vs superposition), and empirical justification for design choices (layer range, token position).

**Resolution Path:**

The verification plan addresses this dialectic through:

1. **Foundation verification (H-E1):** Establishes correlation existence before investigating mechanism, with strict falsification criteria (|ρ| < 0.3 → abandon)
2. **Mechanism validation (H-M-integrated):** Tests 4-step causal chain with ablation studies (layer ranges) and controls (epistemic vs non-epistemic tasks) to separate true mechanism from artifacts
3. **Gate conditions:** Allow early detection of H0 support without wasting resources on downstream hypotheses if foundation fails

**Conditions for Thesis Support:**
- H-E1 passes: |ρ| > 0.4 with p < 0.001 and 95% CI excluding 0.3
- H-M-integrated passes: Subspace collapse validated (PR_high < PR_low, p < 0.01), negative PR~SE correlation
- H-C1 passes or partially passes: Architecture invariance demonstrated (|Δρ| ≤ 0.15) or scoped appropriately

**Conditions for Antithesis Support:**
- H-E1 fails: |ρ| < 0.3 or p > 0.05 → correlation doesn't exist, H0 supported
- H-M-integrated fails critically: Correlation direction reverses (PR increases with SE) → mechanism hypothesis wrong, collapsed subspace invalid
- Confound control fails: Correlation disappears after hierarchical regression controlling for sequence length and perplexity

**Nuanced Outcome Possibilities:**

1. **Full Thesis Support:** All hypotheses pass → Geometric uncertainty detection validated with mechanistic understanding
2. **Partial Support (Strong correlation, weak mechanism):** H-E1 passes but H-M fails → Correlation exists but mechanism explanation wrong; PIVOT to black-box correlation approach
3. **Partial Support (Architecture-dependent):** H-E1 and H-M pass but H-C1 fails → SCOPE to Llama-3 specific, document need for per-architecture calibration
4. **No Support:** H-E1 fails → Antithesis supported, abandon geometric approach

---

## Robustness Assessment

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 ROBUSTNESS ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| **Existence** | Geometric features correlate |ρ| > 0.4 with SE | May be artifact or confound | H-E1 with hierarchical regression controls |
| **Mechanism** | Collapsed subspace under epistemic uncertainty | Superposition for aleatoric, wrong pattern | H-M-integrated with t-test + directionality check |
| **Stability** | PR from 9 layers is stable (CV < 0.15) | Too noisy for production | Bootstrap validation in H-E1 |
| **Scope** | Generalizes across Llama architectures | Llama-3 specific overfitting | H-C1 cross-architecture test |
| **Baselines** | Interpretable + fast vs black-box | Weaker performance (AUROC ~0.70 vs 0.80) | Accept tradeoff: speed + interpretability > raw accuracy |

**Overall Robustness Score:** Medium-High

**Confidence in Verification Plan:** 0.75
- High confidence in H-E1 design (clear falsification, controls for confounds)
- Medium confidence in H-M mechanism (collapsed vs superposition tension remains)
- Medium confidence in generalization (H-C1 tests Llama-family only, not broader)

**Critical Vulnerabilities:**
1. Layer/position selection empirically unjustified (addressed via ablation in H-M)
2. PR statistical stability unproven (addressed via bootstrap in H-E1)
3. Correlation strength may be insufficient vs best baselines (accepted tradeoff for interpretability)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Resolution Strategy

The dialectical tension between thesis (geometric features work) and antithesis (spurious correlation) is resolved through:

1. **Falsification-first:** H-E1 designed to fail quickly if correlation doesn't exist
2. **Mechanism validation:** H-M tests WHY correlation exists, not just THAT it exists
3. **Scope realism:** Accept tradeoff of lower AUROC (~0.70) for interpretability + speed
4. **Empirical justification:** Ablation studies replace assumptions with data-driven choices

**Expected Synthesis Outcome:** Partial thesis support - geometric features provide interpretable, fast uncertainty proxy with moderate accuracy, suitable for production real-time deployment where sampling methods fail, but not replacing best offline methods (semantic entropy, trained probes) for maximum accuracy.
