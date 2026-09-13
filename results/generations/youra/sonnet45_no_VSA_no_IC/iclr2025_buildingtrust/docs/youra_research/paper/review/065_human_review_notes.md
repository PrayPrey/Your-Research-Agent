# Human Review Notes - Round 1

**Purpose:** Minor issues deferred from automated revision for human review  
**Date**: 2026-08-19  
**Rounds Completed**: 1  
**Paper Version**: 06_paper_r1.md

---

## Summary by Category

| Category | Count | Priority |
|----------|-------|----------|
| Formatting & Style | 5 | LOW |
| Citation & Cross-Reference | 4 | MEDIUM |
| Clarity & Precision | 4 | MEDIUM |
| Internal Consistency | 2 | LOW |
| **TOTAL** | **15** | - |

**Review Status**: Not blocking acceptance; appropriate for pre-submission polish pass.

---

## Round 1 Deferred Issues

### Formatting & Style (5 issues)

#### HRN-001: Phi symbol inconsistency
**Location**: Throughout paper (first occurrence line 23 in original)  
**Issue**: Uses "φ" (Greek phi symbol) in some places, "phi" (word) in others.  
**Recommendation**: Standardize to:
- Symbol "φ" in equations and when immediately preceding numerical value (e.g., "φ 0.36")
- Word "phi" in prose and compound terms (e.g., "phi coefficient", "partial phi analysis")
- Check ICML LaTeX template Unicode support; use `\phi` if Unicode problematic

**Examples to fix:**
- Line 79 (06_paper.md): "phi coefficient (φ)" → consistent
- Line 89: Formula uses phi, should use φ
- Tables: Check column headers use consistent notation

**Estimated effort**: 15 minutes (find-replace with manual verification)

---

#### HRN-002: Table checkmark symbols
**Location**: Tables 1, 3 (Results section)  
**Issue**: Uses "✓" Unicode checkmark. Verify ICML LaTeX template supports this or convert to `\checkmark` command.  
**Recommendation**: Test compilation:
1. If Unicode renders correctly in ICML template → keep as-is
2. If not → replace with LaTeX `\checkmark` or text "YES"/"PASS"

**Estimated effort**: 5 minutes (test + conditional fix)

---

#### HRN-003: Formula alignment in Methodology
**Location**: Line 89 (phi coefficient formula)  
**Issue**: Formula presented in inline code block. Would benefit from centered equation environment for readability.  
**Recommendation**: Convert to LaTeX equation:

**Before (markdown):**
```
φ = (n11·n22 - n12·n21) / √[(n11+n12)(n21+n22)(n11+n21)(n12+n22)]
```

**After (LaTeX):**
```latex
\begin{equation}
\phi = \frac{n_{11} \cdot n_{22} - n_{12} \cdot n_{21}}{\sqrt{(n_{11}+n_{12})(n_{21}+n_{22})(n_{11}+n_{21})(n_{12}+n_{22})}}
\end{equation}
```

**Estimated effort**: 10 minutes (LaTeX formatting + verification)

---

#### HRN-004: Number formatting consistency
**Location**: Results section line 282 (original: "Five of six")  
**Issue**: Writes "Five of six" in prose; elsewhere uses "5/6" for consistency with quantitative reporting.  
**Recommendation**: Change to "5 of 6" or "5/6" to match style in Tables and other numerical reporting.

**Estimated effort**: 2 minutes (find-replace)

---

#### HRN-005: Bullet formatting in model profiles
**Location**: Results lines 300-306 (model fingerprints description)  
**Issue**: Inconsistent punctuation/spacing in bullet list:
- "GPT-4 profile—Dominant..." (em-dash)
- "Claude-3 profile: Dominant..." (colon)
- "Llama-3 profile: Minimal..." (colon)

**Recommendation**: Standardize to em-dash with space OR colon, not mixed:
- Option A: "GPT-4 profile — Dominant..." (em-dash with spaces)
- Option B: "GPT-4 profile: Dominant..." (colon)

**Estimated effort**: 3 minutes

---

### Citation & Cross-Reference (4 issues)

#### HRN-006: Li & Li 2024 disambiguation
**Location**: Line 55 (Related Work, first mention)  
**Issue**: Paper cites both "Li & Li 2024" (triangular trade-offs) and "Li et al. 2024" (MMTrustEval). First mention of Li & Li should include full distinguishing info.  
**Recommendation**: Change first occurrence to:
"Li & Li (2024, 'Triangular Trade-offs in LLM Trustworthiness')" or similar parenthetical to distinguish from Li et al.

**Check**: Verify 06_references.bib has both entries with distinct keys (e.g., `li2024triangular` vs `li2024mmtrust`)

**Estimated effort**: 5 minutes (citation check + text edit)

---

#### HRN-007: Figure 1 caption reference missing
**Location**: Line 130 (Methodology, Figure 1 description)  
**Issue**: Text states "Figure 1 (difficulty_independence.png)" but image not embedded in markdown. Confirm figure file exists and will be included in submission.  
**Recommendation**:
1. Verify `difficulty_independence.png` exists in figures directory
2. If submitting as supplementary: note in caption "See supplementary materials"
3. If inline: embed using `![Figure 1](path/to/difficulty_independence.png)` in markdown or `\includegraphics` in LaTeX

**Estimated effort**: 10 minutes (file verification + caption update)

---

#### HRN-008: Figure numbering conflict
**Location**: Lines 130 (Figure 1 = difficulty_independence) vs 331 (Figure 1-3 = Coupling Heatmaps)  
**Issue**: Line 130 describes "Figure 1 (difficulty_independence.png)" but line 331 states "Figure 1-3 (Coupling Heatmaps)." These conflict.  
**Recommendation**: Renumber figures consistently:
- **Option A (9 figures total per line 430):**
  - Fig 1: Difficulty independence heatmap
  - Fig 2: Partial vs raw phi scatter
  - Fig 3: Quartile stratified phi
  - Fig 4-6: Coupling heatmaps (GPT-4, Claude-3, Llama-3)
  - Fig 7: [unspecified]
  - Fig 8: Effect size retention
  - Fig 9: [unspecified]

- **Option B (consolidate):**
  - Fig 1: Difficulty independence
  - Fig 2: Partial vs raw phi
  - Fig 3: Quartile stratified phi + coupling heatmaps (multi-panel)
  - Fig 4: Effect size retention

Update all cross-references throughout text.

**Estimated effort**: 20 minutes (figure audit + renumbering)

---

#### HRN-009: References section placeholder
**Location**: Line 420 (References section)  
**Issue**: States "See `06_references.bib` for full BibTeX entries" as placeholder.  
**Recommendation**: Generate full reference list from .bib file or note as "References omitted for review draft" if intentional.

**Action items:**
1. Run BibTeX compiler on 06_references.bib
2. Insert formatted reference list OR
3. Add footnote: "Full references available in BibTeX format; formatted list generated at submission"

**Estimated effort**: Variable (5 min if already compiled, 30 min if manual formatting needed)

---

### Clarity & Precision (4 issues)

#### HRN-010: Difficulty operationalization vague
**Location**: Line 99 (Methodology, partial correlation)  
**Issue**: States "difficulty as a composite score derived from model confidence (simulated in Phase 4; API logprobs in production)" but no formula provided.  
**Recommendation**: Add specificity:
- **Main text**: Brief description (e.g., "difficulty = 1 - mean(logprob(correct_answer))")
- **Appendix**: Full formula with normalization details
- **Inline**: Reference to Appendix ("see Appendix B for operationalization")

**Justification**: Reproducibility—readers cannot replicate partial correlation without knowing difficulty calculation.

**Estimated effort**: 15 minutes (formula documentation + appendix cross-ref)

---

#### HRN-011: 7% noise justification missing
**Location**: Line 164 (Experiments, synthetic data description)  
**Issue**: States "perturbed with 7% noise to introduce model-specific variation" but no justification for 7% choice.  
**Recommendation**: Add brief rationale:
- "7% noise (chosen to maintain signal-to-noise ratio >10:1 for phi 0.35 target)"
- OR cite precedent: "7% noise following [synthetic benchmark paper X]"
- OR acknowledge arbitrary: "7% noise (arbitrary choice for PoC; sensitivity analysis in Appendix C)"

**Estimated effort**: 10 minutes (literature check or appendix note)

---

#### HRN-012: "Combinatorial argument" expansion needed
**Location**: Line 194 (Experiments, h-m2 rationale)  
**Issue**: States "combinatorial argument: 10 pairs = sparse (1-2 pairs), moderate (3-5 pairs), broad (6+ pairs)" without derivation.  
**Recommendation**: Expand in footnote or Appendix:
- Threshold justification: "1-2 pairs = <20% of possible pairs (sparse by definition), 3-5 = 30-50% (moderate), 6+ = >60% (broad/dominant pattern)"
- Or cite convention: "Following precedent in X literature"

**Rationale**: Preregistered thresholds need transparency for replication.

**Estimated effort**: 10 minutes (footnote or appendix addition)

---

#### HRN-013: "Architectural independence" definition ambiguous
**Location**: Line 348 (Discussion)  
**Issue**: States "architecturally independent by default" without defining term. Could mean:
- Separate processing pathways (computational graph structure)?
- No shared parameters (weight isolation)?
- Independent failure modes (empirical observation)?

**Recommendation**: Add clarifying phrase:
"architecturally independent by default (separate processing pathways with no shared failure mechanisms)"

OR define in Introduction when first introducing coupling concept.

**Estimated effort**: 5 minutes (clarification phrase)

---

### Internal Consistency (2 issues)

#### HRN-014: Sample size not mentioned in Abstract
**Location**: Abstract vs Introduction sample size reporting  
**Issue**: Introduction mentions "n=1500 instances across 3 simulated model profiles" but Abstract only states "synthetic benchmark emulation" without sample size.  
**Recommendation**: Add to Abstract sentence 3 for reproducibility context:

**Current**: "...via phi coefficient analysis across 5 dimensions (truthfulness, robustness, fairness, safety, privacy) on synthetic benchmark emulation..."

**Revised**: "...via phi coefficient analysis across 5 dimensions on synthetic benchmark emulation (n=1500 instances, 500 per model profile)..."

**Trade-off**: Adds ~8 words to already-compressed abstract; consider if space allows.

**Estimated effort**: 2 minutes

---

#### HRN-015: Overclaim residual in Conclusion
**Location**: Line 401 (Conclusion, medical diagnosis callback)  
**Issue**: States "make these hidden vulnerabilities visible" which overstates capability.  
**Original concern**: Synthetic data doesn't reveal hidden patterns, it demonstrates detection capability IF patterns exist.

**Revision agent addressed but check**: Line now states "Our methodology framework makes these hidden vulnerabilities measurable" which is better but still slightly strong.

**Recommendation**: Final check—does this align with "methodology demonstration" framing? Consider:
- "Our methodology framework can make these hidden vulnerabilities measurable when applied to real benchmarks"
- OR keep current phrasing if acceptable (marginal)

**Estimated effort**: 2 minutes (review + optional tweak)

---

## Priority Ranking for Human Review

### HIGH PRIORITY (do first):
1. **HRN-008**: Figure numbering conflict (blocks figure cross-references)
2. **HRN-009**: References section placeholder (required for submission)
3. **HRN-010**: Difficulty operationalization (reproducibility issue)

### MEDIUM PRIORITY (improves quality):
4. **HRN-006**: Li & Li citation disambiguation
5. **HRN-007**: Figure 1 file verification
6. **HRN-011**: 7% noise justification
7. **HRN-012**: Combinatorial argument expansion

### LOW PRIORITY (polish):
8. **HRN-001**: Phi symbol consistency
9. **HRN-002**: Checkmark symbols
10. **HRN-003**: Formula alignment
11. **HRN-004**: Number formatting
12. **HRN-005**: Bullet formatting
13. **HRN-013**: Architectural independence definition
14. **HRN-014**: Sample size in abstract
15. **HRN-015**: Conclusion overclaim residual check

---

## Batch Processing Recommendations

### LaTeX Conversion Pass (30 min):
- Fix HRN-001, HRN-002, HRN-003 together when converting to LaTeX

### Figure Management Pass (30 min):
- Fix HRN-007, HRN-008 together during figure embedding

### Appendix Addition Pass (20 min):
- Fix HRN-010, HRN-011, HRN-012 by adding Appendix B (Methods Details)

### Citation Pass (15 min):
- Fix HRN-006, HRN-009 together during reference formatting

### Final Polish Pass (15 min):
- Fix HRN-004, HRN-005, HRN-013, HRN-014, HRN-015 in one sweep

**Total estimated effort**: ~2 hours human time

---

## Sign-off Checklist

After addressing issues, verify:

- [ ] All figures numbered consistently and cross-referenced correctly
- [ ] References section complete (no placeholders)
- [ ] Appendix added with method details (difficulty, noise, thresholds)
- [ ] LaTeX compiles without Unicode errors
- [ ] Citations disambiguated (Li & Li vs Li et al.)
- [ ] Reproducibility details sufficient (difficulty formula, noise justification)
- [ ] Final overclaim check (Conclusion line 401)

---

## Notes for Future Rounds

**If Round 2 review identifies additional MINOR issues:**
- Append to this document as "Round 2 Deferred Issues" section
- Maintain running count of total issues across rounds
- Prioritize any recurring themes (e.g., multiple figure reference issues → systematic problem)

**When to stop deferring:**
- If same issue type appears 3+ times → promote to MAJOR (systematic problem)
- If cumulative MINOR count >25 → schedule dedicated polish session before R3

---

## Maintenance Metadata

- **Document version**: 1.0 (Round 1 only)
- **Last updated**: 2026-08-19
- **Reviewed by**: [Human reviewer name to be added]
- **Status**: OPEN (issues unresolved, awaiting human review)
