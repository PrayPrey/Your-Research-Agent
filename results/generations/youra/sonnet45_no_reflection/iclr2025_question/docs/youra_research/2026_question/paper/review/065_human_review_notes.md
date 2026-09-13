# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review for human review.  
> **v2.0:** These issues are NOT auto-fixed by AI - human judgment required.

**Generated**: 2026-05-12T14:00:00Z  
**Rounds Completed**: 2 (R1, R2)  
**Paper Version**: 06_paper_final.md

---

## Summary by Category

| Category | Count |
|----------|-------|
| Novelty/Positioning | 2 |
| Structure/Flow | 2 |
| Clarity/Wording | 3 |
| Polish | 1 |
| **TOTAL** | **8** |

---

## Round 1 Issues

### Novelty/Positioning (2 issues)

#### 1. Implicit Novelty Statement (Introduction)
**Location**: Introduction, paragraph 3  
**Issue**: Paper discusses geometric uncertainty without explicitly claiming "first to propose participation ratio for semantic entropy proxy"  
**Current**: "We hypothesized that intrinsic geometric properties of hidden state manifolds could bridge this gap."  
**Suggestion**: Add explicit novelty claim if true: "To our knowledge, this is the first work proposing participation ratio analysis of hidden states as a training-free semantic entropy proxy."  
**Why Human Review**: Requires literature verification to confirm no prior work exists.

#### 2. Workshop Suitability Discussion Missing (Conclusion)
**Location**: Conclusion, final paragraph  
**Issue**: Paper doesn't explicitly position itself as workshop paper or discuss negative result value  
**Current**: Ends with future work roadmap  
**Suggestion**: Add: "This negative result is appropriate for workshop publication, documenting computational barriers that will affect any researcher pursuing geometric uncertainty at scale."  
**Why Human Review**: Subjective positioning decision about target venue.

---

### Structure/Flow (2 issues)

#### 3. Efficiency Contradiction Placement (Discussion)
**Location**: Discussion, Limitations section  
**Issue**: "480× slower than semantic entropy" contradiction appears only in Discussion, not when efficiency is first claimed in Introduction  
**Current**: Introduction claims "<10ms" potential, contradiction revealed on page 8  
**Suggestion**: Either (a) add disclaimer in Introduction ("pending extraction optimization"), or (b) move efficiency discussion forward  
**Why Human Review**: Narrative strategy decision - surprise reveal vs upfront caveat.

#### 4. Prior Work Extraction Gap (Related Work)
**Location**: Related Work, Section 2.3 (Fast Uncertainty Proxies)  
**Issue**: Kossen et al. (2024) probes discussed briefly, but no detailed comparison of approach (supervised vs unsupervised)  
**Current**: Single paragraph, 3 sentences on probes  
**Suggestion**: Expand comparison: "Unlike Kossen et al.'s supervised probes requiring semantic entropy labels for training, our geometric approach hypothesizes training-free spectral features. However, [rest of analysis]"  
**Why Human Review**: Depth vs brevity tradeoff in Related Work section.

---

### Clarity/Wording (3 issues)

#### 5. Jargon Density in Equations (Methodology)
**Location**: Methodology, Section 3.3 (Geometric Feature Computation)  
**Issue**: Participation ratio formula introduced without intuition  
**Current**: "PR = (trace(C))² / (||C||²_F · 8d)"  
**Suggestion**: Add sentence before formula: "The participation ratio measures how uniformly variance is distributed across dimensions - higher values indicate confident states using many features, lower values suggest uncertainty collapsed into fewer directions."  
**Why Human Review**: Balance between rigor and accessibility for non-specialist readers.

#### 6. Repetitive "UNKNOWN" Phrasing (Throughout)
**Location**: Abstract, Introduction, Results, Discussion, Conclusion (5+ occurrences)  
**Issue**: "UNKNOWN" appears repeatedly in similar constructions: "validity UNKNOWN", "status UNKNOWN", "empirical status UNKNOWN"  
**Current**: "The hypothesis validity is **unknown**—neither confirmed nor refuted" (multiple variations)  
**Suggestion**: Vary phrasing: "remains empirically untested", "validity undetermined", "no evidence for or against", "inconclusive outcome"  
**Why Human Review**: Stylistic judgment on repetition tolerance vs. clarity emphasis.

#### 7. Passive Voice Overuse (Results)
**Location**: Results, Section 5 (particularly "Execution Progress")  
**Issue**: Heavy passive voice: "was loaded", "was allocated", "was hung", "was terminated"  
**Current**: "Model: mistralai/Mistral-7B-v0.1 loaded successfully"  
**Suggestion**: Mix with active where appropriate: "We loaded Mistral-7B-v0.1 in 9 seconds", "The extraction process consumed 590 CPU minutes"  
**Why Human Review**: Style preference - passive voice acceptable in experimental reporting.

---

### Polish (1 issue)

#### 8. Confidence Value Origin Missing (Discussion)
**Location**: Discussion, "Confidence Updates" subsection  
**Issue**: Paper states confidence dropped from 0.75 → 0.20 but doesn't explain where 0.75 originated  
**Current**: "Original hypothesis confidence 0.75 (based on theoretical plausibility) reduced to 0.20"  
**Suggestion**: Add rationale for initial 0.75: "We initially assigned 0.75 confidence based on (a) NerVE's successful spectral analysis of weights, (b) Voita et al.'s dimensionality findings, and (c) theoretical coherence of collapsed subspace mechanism."  
**Why Human Review**: Requires judgment on whether confidence origin adds value or is tangential.

---

## Recommended Priority

### Fix First (High Visibility)
1. **Issue #6**: Repetitive "UNKNOWN" phrasing (appears in Abstract and Conclusion - reader's first/last impression)
2. **Issue #5**: Jargon density in equations (barrier to non-specialist readers)

### Fix Second (Readability)
3. **Issue #7**: Passive voice overuse (improves Results section flow)
4. **Issue #3**: Efficiency contradiction placement (narrative coherence)

### Consider (Subjective)
5. **Issue #1**: Novelty statement (depends on literature verification)
6. **Issue #4**: Prior work depth (depth vs brevity tradeoff)
7. **Issue #8**: Confidence origin (adds context but may be tangential)

### Optional (Positioning)
8. **Issue #2**: Workshop suitability discussion (depends on target venue strategy)

---

## Notes for Human Reviewer

**What NOT to Change:**
- All numerical values (verified 100% accurate after R2 corrections)
- INCONCLUSIVE outcome messaging (essential transparency)
- All 4 disclosed limitations (complete and honest)
- Discovery-first abstract framing (R1 improvement)
- Contribution ordering (R1 improvement)

**Style Guidance:**
- Paper adopts formal academic tone with extensive hedging ("may", "suggests", "hypothesize")
- Repetition of "UNKNOWN" is intentional emphasis on transparency, but could be excessive
- Passive voice is discipline-standard for experimental reporting, but active voice acceptable

**Time Estimate:**
- Issues #1-4: ~30-60 minutes (requires rewriting)
- Issues #5-8: ~15-30 minutes (minor edits)
- Total: ~1-2 hours for complete human review

---

*Note: These issues do not block paper acceptance but improve overall quality. Focus on high-visibility sections (Abstract, Conclusion) first.*
