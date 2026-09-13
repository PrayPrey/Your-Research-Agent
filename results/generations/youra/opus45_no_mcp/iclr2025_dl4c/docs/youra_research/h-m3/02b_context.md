# Phase 2B Context: H-M3

## Hypothesis Information

**ID:** h-m3
**Type:** MECHANISM
**Title:** Unreliable Localization Causes Gradient Noise
**Statement:** Under fine-grained feedback with U_ignore errors, if penalties are applied at traceback-reported locations, then gradient signal concentrates at wrong tokens, measurably increasing noise.

**Gate:** SHOULD_WORK
**Prerequisites:** h-m2 (VALIDATED)

## Rationale

Tests the noise injection mechanism - when localization is unreliable, gradients go to wrong places, harming learning. This is a critical step in the causal chain explaining why gating improves efficiency.

## Variables

- **Independent:** error type (U_line vs U_ignore) with fine-grained penalty
- **Dependent:** gradient_error_line / gradient_other ratio
- **Controlled:** penalty magnitude, model state

## Verification Protocol

1. Sample 200+ training examples with U_line errors, 200+ with U_ignore errors
2. Apply fine-grained penalty to each
3. Compute gradient concentration ratio for each sample
4. Compare distributions: mean ratio(U_line) vs mean ratio(U_ignore)
5. Test whether U_ignore shows significantly lower concentration (noisier)

## Success Criteria

- **Primary:** gradient_concentration(U_line) > gradient_concentration(U_ignore)
- **Secondary:** Difference statistically significant (p<0.05)

## Failure Response

- IF fails: EXPLORE whether noise manifests differently

## Dependencies

- **h-m2:** VALIDATED (U_line accuracy=100.0% > U_ignore accuracy=20.0%, chi-square p=9.57e-74)

## Experimental Setup (from Phase 2B)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | APPS (standard) | 5000 training problems; standard code RL benchmark |
| **Model** | CodeT5-large | Same as RLTF baseline; 770M parameters |

**Dataset Details:**
- Source: https://github.com/hendrycks/apps
- Type: standard

**Model Details:**
- Type: encoder-decoder
- Source: Salesforce/codet5-large
- Parameters: 770M

## Previous Hypothesis Results

### H-M2 Validation (Direct Prerequisite)
- **Result:** PASS
- **U_line accuracy:** 100.0%
- **U_ignore accuracy:** 20.0%
- **Chi-square p-value:** 9.57e-74
- **Conclusion:** Error localization DOES vary significantly by type. U_line errors have dramatically higher localization accuracy.

### H-M1 Validation
- **Result:** PASS
- **Mean concentration ratio:** 16.11
- **Mean within 2 lines:** 100%
- **p-value:** 5.72e-270
- **Conclusion:** Fine-grained feedback correctly targets error line tokens with high concentration.

## Key Implications for H-M3

H-M2 established that U_ignore errors have only 20% localization accuracy vs 100% for U_line. H-M3 must now show that when penalties are applied at these wrong locations (80% of the time for U_ignore), the gradient signal becomes measurably noisier - concentrating at incorrect tokens rather than the true error source.

The experiment should measure gradient distribution patterns when:
1. Fine-grained penalty applied to U_line error (expected: concentrated at correct location)
2. Fine-grained penalty applied to U_ignore error (expected: dispersed/wrong location)

Compare these distributions to quantify the noise difference.
