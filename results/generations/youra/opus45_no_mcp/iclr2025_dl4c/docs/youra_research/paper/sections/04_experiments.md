# Experimental Setup

## Research Questions

We design experiments to answer two research questions:

**RQ1 (Mechanism):** Does error type determine localization reliability, and does unreliable localization cause gradient noise?

**RQ2 (Efficiency):** Does error-type gating improve training efficiency?

RQ1 validates the causal mechanism underlying our approach; RQ2 demonstrates the practical benefit.

## Hypothesis Structure

We decompose RQ1 into four mechanism hypotheses:

- **H-M1:** Fine-grained penalties concentrate gradients at traceback locations
- **H-M2:** Localization accuracy varies by error type (U_line vs U_ignore)  
- **H-M3:** Unreliable localization causes gradient concentration at wrong tokens
- **H-M4:** Gating improves gradient signal-to-noise ratio

For RQ2, we test one existence hypothesis:

- **H-E1:** Error-type gating improves sample efficiency

Each hypothesis specifies success criteria and gate type (MUST_WORK or SHOULD_WORK). We require all MUST_WORK hypotheses (H-M1, H-M3, H-E1) to pass for overall validation.

## Dataset

We use the APPS dataset for all experiments. APPS contains 5,000 training problems across three difficulty levels, providing sufficient volume for statistical power. The dataset's focus on algorithmic problems produces diverse error types, enabling meaningful comparison between U_line and U_ignore categories.

We sample 500 problems per error category for mechanism experiments (H-M1 through H-M4) and use the full training set for efficiency experiments (H-E1).

## Model

We use CodeT5-small (60M parameters) for proof-of-concept validation. While RLTF uses CodeT5-large (770M), the smaller model enables rapid iteration and demonstrates mechanism generality. We expect the gating mechanism to transfer to larger models—the underlying causal chain (traceback → penalty → gradient) is architecture-agnostic.

## Metrics

**Concentration ratio** (H-M1, H-M3): Gradient magnitude at error-line tokens divided by magnitude at non-error tokens. Values >1 indicate concentration at error location.

**Localization accuracy** (H-M2): Percentage of samples where traceback line matches ground-truth bug location (within ±2 lines tolerance).

**Signal-to-noise ratio** (H-M4): Gradient signal at ground-truth locations divided by signal at incorrect locations. Higher values indicate cleaner credit assignment.

**Steps to threshold** (H-E1): Training steps required to reach 30% pass@1 on evaluation set. Lower values indicate better sample efficiency.

## Conditions

We compare three feedback conditions:

- **Coarse-only:** Binary pass/fail reward, no token-level penalties
- **Fine-always:** Standard RLTF with uniform fine-grained penalties
- **Fine-gated:** Our approach—fine-grained for U_line, coarse for U_ignore

For mechanism experiments, we analyze gradient behavior under fine-always to characterize the noise problem, then compare to fine-gated to validate the solution.

## Ground Truth Annotation

For H-M2 and H-M3, we require ground-truth bug locations to measure localization accuracy and gradient concentration at correct tokens. We use synthetic code templates with known bug locations, ensuring deterministic annotation. This simplifies validation but limits generalization claims—we note this as a limitation.
