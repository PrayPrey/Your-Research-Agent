# Revision Changelog — Round 1
## Paper: H-DocComp-v1 — "Automated DTS-Weighted Cross-Repository ML Dataset Documentation Scoring"
**Revision Agent:** Claude Sonnet 4.6
**Revision Date:** 2026-03-15
**Source paper:** 06_paper.md
**Output paper:** 06_paper_r1.md

---

## Round 1 Changes

### FATAL-001 Fix: "22%" → "~26%" compression claim (3 locations)

**Issue:** The paper claimed "22% compression" in three locations, but the actual calculation is (0.229−0.169)/0.229 × 100 = 26.2%.

---

**Change 1 — Abstract (not present in abstract; confirmed the abstract did not include the "22%" phrase; the abstract only stated the finding without the percentage)**

Confirmed: Abstract does not contain the "22%" claim. No change needed here.

---

**Change 2 — Section 1, Contribution 2**

- Location: Section 1, bullet point 2, final sentence
- Before: `"DTS inverse-frequency weighting compresses the overall score (mean 0.169) by 22% relative to naive field presence counting (mean 0.229)"`
- After: `"DTS inverse-frequency weighting compresses the overall score (mean 0.169) by ~26% relative to naive field presence counting (mean 0.229)"`

---

**Change 3 — Section 5.2, paragraph 1**

- Location: Section 5.2, first body paragraph
- Before: `"The mean weighted DTS score (0.169, std=0.124) is 22% lower than the mean unweighted score (0.229, std=0.150)."`
- After: `"The mean weighted DTS score (0.169, std=0.124) is ~26% lower than the mean unweighted score (0.229, std=0.150) — calculated as (0.229−0.169)/0.229 × 100 = 26.2%."`

---

**Change 4 — Section 5.2 subsection heading renamed (MAJOR-002/007 combined)**

- Location: Section 5.2 heading
- Before: `"### 5.2 DTS Weighting Mechanism (RQ2): A Distinct Quality Signal"`
- After: `"### 5.2 Internal Consistency of DTS Weighting (RQ2)"`
- Reason: Original heading implied weighting produces a "distinct signal" which r=0.989 does not demonstrate; that value confirms internal consistency, not distinctness of construct.

---

### MAJOR-001 + MAJOR-003 + MAJOR-006 Fix: Rondina2025DTS inline disclosure and Table 5 restructure

**Issue:** The unverified citation Rondina et al. [2025] was only disclosed in the references list; the body text gave no warning where the citation was load-bearing. Table 5 presented no quantitative values and used "Consistent? ✓" which was unverifiable against an unverified source. Section 5.4 heading used "Replicates" framing.

---

**Change 5 — Section 2.1, first use of Rondina et al. in body**

- Location: Section 2.1, paragraph about DTS
- Before: `"The Data Transparency Scorecard [Rondina et al., 2025] operationalizes..."`
- After: `"The Data Transparency Scorecard [Rondina et al., 2025; *note: this citation is pending independent verification — see References and Section 6.4*] operationalizes..."`

---

**Change 6 — Section 5.4 heading**

- Location: Section 5.4 heading
- Before: `"### 5.4 Section Asymmetry Replicates Rondina et al. [2025] at 7.58× Scale"`
- After: `"### 5.4 Section Asymmetry Pattern Consistent with Prior Manual Scoring Reports"`
- Reason: "Replicates" implies quantitative comparison with known values; citation is unverified and only qualitative descriptors are available.

---

**Change 7 — Table 5 header, caveat note, and column rename**

- Location: Section 5.4, Table 5
- Before: Table 5 titled "Comparison with Rondina et al. [2025] Manual Scores" with column "Consistent?" and checkmarks ✓ for all rows. No caveat note.
- After: Added explicit caveat paragraph before table noting unverified citation and directional-only nature. Renamed column from "Consistent?" to "Directionally Consistent?". Changed all "✓" entries to "✓ (pending verification)".

---

**Change 8 — Table 5 body text following the table**

- Location: Section 5.4 text after Table 5
- Before: `"The DTS section asymmetry is structural — not an artifact of sampling or manual scoring."`
- After: Added clarifying sentence: `"The per-section pattern observed here (high coverage for lower-weight sections, near-zero for highest-weight sections) is directionally consistent with the patterns described in Rondina et al. [2025], subject to verification of that citation."`

---

**Change 9 — References entry for Rondina et al. [2025] expanded**

- Location: References section
- Before: `"[UNVERIFIED — Title TBD. Cited as primary source for the Data Transparency Scorecard (DTS) framework: 6-section rubric, inverse-frequency weights (Table 2), manual n=100 scoring across HF/OpenML/Kaggle/UCI.]"`
- After: `"[UNVERIFIED — Title TBD. Cited as primary source for the Data Transparency Scorecard (DTS) framework: 6-section rubric, inverse-frequency weights (Table 1), manual n=100 scoring across HF/OpenML/Kaggle/UCI. All DTS section weights and the 7.58× scale comparison in this paper are dependent on this citation. Manual verification required before camera-ready submission.]"`
- Also corrected "(Table 2)" to "(Table 1)" (the DTS taxonomy table is Table 1 in the paper).

---

### MAJOR-002 + MAJOR-007 Fix: Proxy validation framing

**Issue:** Section 5.2 heading implied DTS weighting produced a "distinct quality signal," while r=0.989 only demonstrates internal algorithmic consistency. The near-perfect correlation is partly expected by construction since both scores use the same binary field presence data.

---

**Change 10 — Section 5.2 heading (addressed jointly with FATAL-001 fix above)**

See Change 4 above.

---

**Change 11 — Section 5.2, paragraph after r=0.989 statement**

- Location: Section 5.2, after the r=0.989 sentence
- Before: No contextualizing sentence about why high r is expected.
- After: Added: `"Note that near-perfect r is partially expected by construction — both measures are computed from the same binary field presence values; their rank ordering is therefore similar, and the key distinction is in score magnitude (0.169 vs. 0.229), not in dataset rank ordering. The r=0.989 value confirms the scoring algorithm behaves reliably and consistently; it does not constitute external validation against human expert judgment (see Section 6.1)."`

---

**Change 12 — Section 3.4 Validation Protocol**

- Location: Section 3.4, proxy validation paragraph
- Before: `"This tests internal algorithmic consistency — not construct validity against human judgment (see Section 6.1)."`
- After: `"Both weighted and unweighted scores are computed from the same underlying binary field presence values; they differ only in the weight vector applied. This tests internal algorithmic consistency — not construct validity against human judgment (see Section 6.1)."`

---

**Change 13 — Section 6.1, added mathematical relationship acknowledgment**

- Location: Section 6.1, new third paragraph
- Before: No acknowledgment of why r=0.989 is partly expected.
- After: Added paragraph: `"The r=0.989 proxy correlation, while confirming algorithmic reliability, reflects an important mathematical relationship: both weighted and unweighted scores sum the same binary field presence indicators, differing only in the weight vector. The near-perfect correlation is therefore partly a consequence of this structural similarity, not evidence of independent external validity. Human annotation (n=120, 3 experts) would provide the external validity check that proxy correlation cannot."`

---

### MAJOR-004 Fix: Figure 1 caption expanded

**Issue:** Caption "Per-section DTS coverage rates across repositories" gave insufficient context for a reader to understand why near-zero Preprocessing/Uses rows are *important* rather than merely low.

---

**Change 14 — Figure 1 caption in Section 5.3**

- Location: Section 5.3, sentence introducing Figure 1
- Before: `"Figure 1 (per_section_coverage_heatmap.png) visualizes this 6×3 matrix as a heatmap."`
- After: Expanded to include full caption text inline: `"Figure 1 (per_section_coverage_heatmap.png) visualizes this 6×3 matrix as a heatmap. Figure 1 caption: 'Per-section DTS coverage rates across repositories (6 sections × 3 repositories). Rows are ordered by DTS importance weight (Table 1). Preprocessing (weight=1.8) and Uses (weight=1.5) — the two highest-priority DTS sections — score near-zero across all repositories. This is not a documentation failure but reflects the documentation API gap: these sections exist as free-text prose in dataset cards rather than structured API fields accessible to automated scoring. Lower-weight sections (Motivation, Composition) show substantially higher coverage because their associated fields are structured in repository APIs.'"`

---

### MAJOR-005 Fix: Binary scoring limitation added to Section 6.4

**Issue:** Ground truth L3 ("Binary scoring ignores quality of documentation content: presence ≠ quality") was absent from the paper's Limitations section.

---

**Change 15 — Section 6.4, new L4 limitation added**

- Location: Section 6.4, after existing L3 (cross-sectional snapshot)
- Before: Section 6.4 had three limitations: L1 (proxy validation), L2 (causal claims), L3 (cross-sectional).
- After: Added new L4: `"**L4: Binary presence scoring.** The pipeline measures whether a DTS field is present and non-null, not whether the documented content is accurate or sufficient. A dataset with task_categories: ['nlp'] scores identically to one with detailed task descriptions in the same field. DTS scores derived from API fields should be interpreted as measuring *structured metadata population*, not documentation quality in the full semantic sense. Construct validity against expert qualitative assessment is a planned but not yet completed validation step."`

---

**Change 16 — Section 6.4, new L5 limitation for unverified citation**

- Location: Section 6.4, after new L4
- Before: Not present.
- After: Added L5: `"**L5: Unverified primary citation.** Rondina et al. [2025], the primary source for the DTS framework, six-section taxonomy, and inverse-frequency weights, has not been independently confirmed in Semantic Scholar or other literature databases (see References). All DTS weight values and the 7.58× scale comparison are dependent on this citation's accuracy. Manual verification against the original publication is required before camera-ready submission."`

---

**Change 17 — Section 3.2, binary scoring rationale note added**

- Location: Section 3.2, end of "Rationale for Binary Scoring" paragraph
- Before: Paragraph ended after describing reproducibility benefit.
- After: Added: `"Note that binary presence measures whether a structured field is populated, not the semantic adequacy of the content — see Section 6.4 (L4)."`

---

## Summary of Changes

| Issue ID | Type | Sections Modified | Changes Applied |
|----------|------|-------------------|-----------------|
| FATAL-001 | Fatal fix | §1 Contrib 2, §5.2 | "22%" → "~26%" in 2 body locations; added formula (0.229−0.169)/0.229 × 100 = 26.2% |
| MAJOR-001 | Major fix | §2.1, §5.4, References | Inline citation caveat in §2.1; expanded References note |
| MAJOR-002 | Major fix | §5.2 heading, §5.2 body | Renamed heading; added construction-expectedness caveat |
| MAJOR-003 | Major fix | §5.4, Table 5 | Added caveat block before table; "Consistent?" → "Directionally Consistent?"; added "(pending verification)" to all rows |
| MAJOR-004 | Major fix | §5.3 (Figure 1) | Expanded figure caption inline |
| MAJOR-005 | Major fix | §6.4 | Added L4 (binary scoring) and L5 (unverified citation) |
| MAJOR-006 | Major fix | §5.4 heading | "Replicates" → "Pattern Consistent with Prior..." |
| MAJOR-007 | Major fix | §3.4, §6.1 | Added construction-expectedness language in both sections |

---

## Round 2 Changes

**Revision Agent:** Claude Sonnet 4.6
**Revision Date:** 2026-03-15
**Source paper:** 06_paper_r1.md
**Output paper:** 06_paper_r2.md

---

### R2-MAJOR-001 Fix: Table 3 Margin Column — Corrected to Absolute Percentage-Point Margins

**Issue:** Table 3 "Margin" column reported "+31.1 pp" (Coverage) and "+40.9 pp" (Proxy Pearson r). These values were computed as relative percent-above-threshold rather than standard absolute percentage-point differences. The "pp" (percentage points) label was therefore incorrect. Additionally, the proxy r margin (+40.9) did not even match the relative-excess formula correctly (0.989/0.70 − 1) × 100 = 41.3%.

**Correct absolute percentage-point margins:**
- Coverage: 0.918 − 0.70 = 0.218 = +21.8 pp
- Proxy r: 0.989 − 0.70 = 0.289 = +28.9 pp

**Change — Table 3, Section 5.2**

- Location: Section 5.2, Table 3 "Gate Criteria Results"
- Before:
  ```
  | Coverage rate | ≥ 0.70 | 0.918 | +31.1 pp | ✓ PASS |
  | Proxy Pearson r | ≥ 0.70 | 0.989 | +40.9 pp | ✓ PASS |
  ```
- After:
  ```
  | Coverage rate | ≥ 0.70 | 0.918 | +21.8 pp | ✓ PASS |
  | Proxy Pearson r | ≥ 0.70 | 0.989 | +28.9 pp | ✓ PASS |
  ```
- Computation method: absolute difference (achieved − threshold), which is the standard definition of "percentage points above threshold."

---

### R2-MAJOR-002 Fix: Table 5 "Directionally Consistent?" Column — Replaced ✓ Marks with Explicit Directional Descriptors

**Issue:** Table 5's "Directionally Consistent?" column used ✓ marks across all six rows. Even with the caveat block added in R1, the visual impression of six ✓ symbols creates a false sense of validated comparison against an unverified source (Rondina et al. [2025]). The ✓ symbol is commonly associated with confirmed/verified status, which is not the case here.

**Change — Table 5, Section 5.4**

- Location: Section 5.4, Table 5 column header and all data cells
- Before: Column header "Directionally Consistent?" with cells "✓ (pending verification)" for all rows
- After: Column header renamed to "Pattern Direction"; cells changed from "✓ (pending verification)" to explicit directional descriptors:
  - Motivation: "↑ same direction (unverified)"
  - Composition: "↑ same direction (unverified)"
  - Collection: "↑ same direction (unverified)"
  - Distribution: "↑ same direction (unverified)"
  - Preprocessing: "↓ same direction (unverified)"
  - Uses: "↓ same direction (unverified)"
- Reason: Arrow symbols with explicit "unverified" text accurately convey directional alignment without implying validated agreement. The caveat block preceding the table (added in R1) is preserved.

---

### Summary of Round 2 Changes

| Issue ID | Type | Sections Modified | Changes Applied |
|----------|------|-------------------|-----------------|
| R2-MAJOR-001 | Major fix | §5.2, Table 3 | Margin values corrected: "+31.1 pp" → "+21.8 pp"; "+40.9 pp" → "+28.9 pp" (absolute pp, not relative %) |
| R2-MAJOR-002 | Major fix | §5.4, Table 5 | Column renamed "Directionally Consistent?" → "Pattern Direction"; ✓ symbols replaced with ↑/↓ directional descriptors with "(unverified)" qualifier |
