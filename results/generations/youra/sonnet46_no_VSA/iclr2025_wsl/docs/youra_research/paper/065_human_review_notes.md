# Phase 6.5 Human Review Notes (MINOR Issues)

These issues are style/presentation choices deferred to the authors. Not auto-fixed.

---

## MINOR-1: "+6.4pp" vs exact 6.37pp
**Location:** Abstract, Conclusion
**Note:** "6.4 percentage-point improvement" — actual value is 0.9148-0.8511=0.0637=6.37pp. Rounding to 6.4pp is acceptable. Consider changing to "6.37pp" for precision, or "more than 6 percentage points" for readability.

## MINOR-2: Abstract evaluation protocol caveat
**Location:** Abstract
**Note:** Abstract says "R²=0.9148 — a +6.4 percentage-point improvement over CISE" without specifying this is on the same testset under same protocol. The comparison is valid (same protocol, same testset), but a one-phrase note ("on ModelZooDataset CIFAR10-GS testset") would preempt reviewer questions.

## MINOR-3: MSE_perm > MSE_total explanation
**Location:** Section 5.2
**Note:** The explanation of why MSE_perm > MSE_total is physically possible is correct but brief. Consider adding: "Concretely, per-model prediction variance over 50 permutations can be large for a single model even when that model's OOF prediction error is small."

## MINOR-4: Unterthiner R² stated as "0.984" vs ">0.984"
**Location:** Introduction ("R² > 0.984"), Table 3 footnote ("0.984 ceiling")
**Note:** Minor inconsistency — both phrasings are acceptable, but should be unified to one form. Ground truth YAML uses "0.984" as the gate threshold.

## MINOR-5: Kofinas et al. 2024 citation
**Location:** Related Work
**Note:** Listed as "ICLR oral" — verify this is correct (oral vs poster classification). The paper is cited as "Graph Neural Networks for Learning Equivariant Representations of Neural Networks." Confirm venue and presentation type.

## MINOR-6: "doubly invariant" terminology
**Location:** Section 3.2, C2 description; Abstract
**Note:** "Doubly-invariant DeepSets" is used without defining "doubly" on first use. Consider adding "(invariant to both input and output channel permutations)" at first occurrence.
