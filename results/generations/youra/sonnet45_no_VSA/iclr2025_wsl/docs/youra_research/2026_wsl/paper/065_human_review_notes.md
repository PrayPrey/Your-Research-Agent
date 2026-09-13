# Human Review Notes - Minor Issues (Do NOT Auto-Fix)

**Generated:** 2026-07-12  
**Source:** Phase 6.5 Adversarial Review Round 1  
**Purpose:** Collect MINOR issues for human judgment (style, presentation, optional improvements)

---

## MINOR Issue 1: Abstract Density (Bored Reviewer)

**Severity:** MINOR  
**Category:** PRESENTATION  
**Issue:** The abstract is a 13-line single paragraph packed with numbers (88.89%, 100×, R ≈ 1.0, Cohen's d = 3.202, p < 0.001, 0% violation, 14.29% violation, 83.3% edge case accuracy). This is a wall of statistics that risks overwhelming rather than enticing.

**Current Abstract (lines 2-2):**
> Architecture family classification from neural network checkpoints typically requires graph neural networks with 50+ hours of implementation effort and GPU-intensive processing. We demonstrate that two simple statistical features—normalization layer type counts and parameter-mass ratio (fraction of parameters in convolutional vs linear layers)—achieve 88.89% accuracy (95% CI: [65%, 99%]) for 3-way classification (CNN vs Transformer vs Hybrid) on held-out TIMM models, with checkpoint-only extraction completing in 1.02 minutes on CPU (0 MB GPU). Our key insight is that architecture families impose structural constraints observable as checkpoint fingerprints: CNNs use BatchNorm and allocate parameters to convolutional kernels (R ≈ 1.0), while Transformers use LayerNorm and allocate to linear projections (R ≈ 0.0). Through five complementary experiments, we validate that features exhibit perfect scale invariance for CNN family (coefficient of variation = 0.00 across ResNet-{18,34,50,101,152}), exceptionally strong inter-family separation (Cohen's d = 3.202, p < 0.001), and mechanistically verified discriminative power (0% CNN violation rate for BatchNorm usage, 14.29% Transformer violation for LayerNorm). Edge case validation maintains 83.3% accuracy on non-standard architectures with only 1.7% degradation from baseline. This work challenges the assumption that weight-space learning requires complex neural representations, demonstrating that hand-crafted statistical features guided by mechanistic understanding suffice for interpretable, efficient architecture classification at scale.

**Suggested Alternative (3-sentence version):**
> Architecture family classification from neural network checkpoints typically requires graph neural networks with 50+ hours of implementation effort and GPU-intensive processing. We demonstrate that two simple statistical features—normalization layer type counts and parameter-mass ratio—achieve 88.89% accuracy for 3-way classification on held-out TIMM models with checkpoint-only extraction in 1.02 minutes on CPU. This work challenges the assumption that weight-space learning requires complex neural representations, demonstrating that hand-crafted features guided by mechanistic understanding suffice for interpretable, efficient architecture classification at scale.

**Recommendation:** Human decision whether to compress abstract for readability or keep detailed statistics for completeness. No auto-fix.

---

## MINOR Issue 2: Missing Baseline - Name-Based Classifier (Skeptical Expert)

**Severity:** MINOR  
**Category:** BASELINE  
**Issue:** Paper uses 40% TIMM naming alignment to strengthen structural claims, but what's the actual accuracy of naive name-based classifier? Comparing 88.89% to hypothetical 40% baseline would strengthen contribution, but this comparison is NOT made.

**Current Statement (line 345, Discussion):**
> The paradoxical result that TIMM naming alignment was only 40% yet classification succeeded (88.89% accuracy) transforms an assumption violation into positive evidence.

**Suggested Addition:**
> A naive name-based classifier (substring matching 'resnet', 'vit', 'mlp', etc.) achieves [X]% accuracy on our validation set, validating that structural features provide [+Y]pp gain over naming conventions alone.

**Recommendation:** Optional experiment to quantify baseline. If trivial to implement (5-10 lines of code), adds persuasive evidence. If time-consuming, acceptable to omit. No auto-fix without experiment.

---

## MINOR Issue 3: Feature Importance Uncertainty (Skeptical Expert)

**Severity:** MINOR  
**Category:** PRESENTATION  
**Issue:** Logistic regression coefficients are point estimates from single train-val split (seed=42). Different random splits would yield different values, but paper presents 0.7770 as if it's ground truth without uncertainty quantification.

**Current Table 2 (lines 243-251):**
```
| Feature | Avg. Absolute Coefficient | Rank | Interpretation |
|---------|---------------------------|------|----------------|
| `param_mass_ratio` | 0.7770 | 1 | Most discriminative |
```

**Suggested Addition:**
- Report coefficient ± std across 5-fold CV or bootstrap resampling
- Or acknowledge: "Coefficients from single split (seed=42); cross-validation would provide robustness estimates"

**Recommendation:** Standard ML practice accepts single-split coefficients. Adding error bars is optional rigor. No auto-fix—human decision on whether extra precision is worth the effort.

---

## MINOR Issue 4: Edge Case Arithmetic Verification (Skeptical Expert)

**Severity:** MINOR  
**Category:** VERIFICATION  
**Issue:** Table 6 reports "Overall 10/12 correct" (83.3%), but per-family breakdown shows:
- NormFree: 0/3 (0%)
- SENet: 3/3 (100%)
- RegNet: 3/3 (100%)
- ViT-Extreme: 3/3 (100%)

Sum: 0+3+3+3 = 9/12 (75%), not 10/12 (83.3%). Possible arithmetic inconsistency or missing edge case family?

**Verification Needed:**
- Read h-c1/04_validation.md to confirm actual edge case results
- If 9/12 is correct, update Table 6 and abstract claim
- If 10/12 is correct, identify which family had 1/3 accuracy

**Recommendation:** VERIFY before finalizing. Possible transcription error from Phase 6 paper writing. Flagged for human attention.

---

## Summary of Minor Issues

| Issue | Type | Action | Priority |
|-------|------|--------|----------|
| Abstract density | Style | Human decision: compress or keep detailed | LOW |
| Name-based baseline | Baseline | Optional experiment to quantify | MEDIUM |
| Feature importance uncertainty | Presentation | Optional error bars via CV | LOW |
| Edge case arithmetic | Verification | VERIFY h-c1 results | **HIGH** |

**Note:** These are NOT automatically fixed because they require human judgment (style preferences), optional experiments (baselines), or verification against source data (arithmetic). Address before final submission.
