# Human Review Notes
# Paper: SparsityLoRA
# Phase 6.5 Adversarial Review v2.0 — MINOR Issues for Human Review

> **Purpose:** Minor issues collected during adversarial review for human review.
> **v2.0 Policy:** These issues are NOT auto-fixed by AI.
> **Note:** These do not block paper acceptance but improve overall quality.

**Generated**: 2026-05-10
**Rounds Completed**: 2

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 1 |
| Clarity | 2 |
| Formatting/Citation | 2 |
| **Total** | **5** |

---

## Round 1 Issues

### Style

**MINOR-001** [Clarity/Style]: Contribution bullet #1 "first systematic characterization" claim
- **Location**: Introduction §1, contribution (1)
- **Current text**: "The first systematic characterization of LLaMA-3.1-8B's layer-wise MLP activation sparsity profile"
- **Issue**: "First" is a strong claim. Act-LoRA uses activation norms (different measure) but could be seen as a characterization. The distinction (continuous rank magnitude + stability analysis vs. binary layer selection without stability characterization) is valid but needs to be stated within the bullet itself, not just in §2.1.
- **Suggested revision**: "The first systematic characterization of **cross-distribution and cross-threshold stability** of LLaMA-3.1-8B's layer-wise MLP activation sparsity profile for use as a structural prior — quantified via ICC$(3,k)$ and Kendall's $\tau$ analysis."
- **Priority**: Medium

### Clarity

**MINOR-002** [Clarity]: Figure 1 caption is too terse in main paper
- **Location**: Results §5.1, Figure~1 reference
- **Current text**: "Figure~1 (sparsity_profile.png): Per-layer sparsity profile across 32 MLP blocks."
- **Issue**: Section file (sections/05_results.md) has a full informative caption but main paper omits the interpretation ("CV=0.544 confirms significant heterogeneity; early layers 0–2 most sparse, deep layers least")
- **Suggested revision**: Expand to match sections/05_results.md caption which states: "Per-layer MLP activation sparsity across all 32 LLaMA-3.1-8B layers for Alpaca and WikiText-103 calibration sets (ε=0.01). Early layers (0–2) exhibit the highest sparsity; deep layers the lowest. The two dataset profiles closely track each other. CV=0.544 confirms significant heterogeneity (threshold: >0.3)."
- **Priority**: Medium (affects reviewer first impression)

**MINOR-003** [Clarity]: SiLU soft-sparsity limitation (L3) could be more direct
- **Location**: Discussion §6.3, Limitation L3
- **Current text**: "Cross-epsilon τ > 0.96 validates rank ordering robustness, but functional sparsity interpretation requires effective-rank comparison."
- **Issue**: Doesn't directly state what "near-zero" means practically. The concern is that SiLU activations approach-but-don't-reach zero, so "sparsity" is a magnitude approximation. This should be clearer.
- **Suggested revision**: Add sentence: "Specifically, SiLU activations are never exactly zero — our threshold ε defines 'near-zero' magnitude (|a| < ε), not true sparsity. The rank ordering is stable across choices of ε, but whether near-zero activations are functionally equivalent to zero (i.e., negligible effect on output) requires validation via effective-rank or ablation analysis."
- **Priority**: Medium

### Formatting/Citation

**MINOR-004** [Citation]: ARD-LoRA, La-LoRA, Sensitivity-LoRA mention without citation
- **Location**: Related Work §2.1 (in 06_paper_r1.md)
- **Current text**: "More recent methods including AdaLoRA, La-LoRA, and Sensitivity-LoRA [citation needed] use gradient norms, Hessian approximations, or layer sensitivity analysis"
  *(Note: exact text may differ slightly between paper versions)*
- **Issue**: These methods are named in Related Work without citations. Either find references or remove the list.
- **Action**: Search Semantic Scholar for "ARD-LoRA", "La-LoRA", "Sensitivity-LoRA" and add verified citations, OR simplify to "recent gradient-based methods" without naming.
- **Priority**: Low-Medium (affects reviewer credibility check)

**MINOR-005** [Citation]: Act-LoRA BibTeX requires manual verification
- **Location**: 06_references.bib, entry `actlora2025mdpi`
- **Current state**: Placeholder BibTeX added during R1 revision with note "REQUIRES VERIFICATION"
- **Action**: Verify author names, exact title, journal volume/issue/pages, DOI from MDPI Electronics (2025). If not findable, change §2.1 text to remove citation and use parenthetical instead: "A contemporaneous approach (Act-LoRA, MDPI Electronics, 2025) uses..."
- **Priority**: HIGH (citation must be verified or removed before submission)

---

## Round 2 Issues

*[To be appended after R2 review if additional minor issues found]*

---

## Recommended Priority

1. **Fix First** (before submission): MINOR-005 — Act-LoRA citation verification (HIGH)
2. **Fix Second** (review quality): MINOR-002 — Figure 1 caption expansion (affects first impression)
3. **Consider** (optional improvement): MINOR-001 — Contribution bullet precision
4. **Consider** (optional improvement): MINOR-003 — SiLU limitation clarity
5. **Optional**: MINOR-004 — Method citations (low visibility)

---

*Note: These issues do not block paper acceptance but improve overall quality and reviewer experience.*
