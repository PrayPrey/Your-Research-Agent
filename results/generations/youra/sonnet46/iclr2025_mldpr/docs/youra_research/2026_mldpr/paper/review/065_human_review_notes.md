# Human Review Notes — Round 1
## Paper: H-DocComp-v1 — "Automated DTS-Weighted Cross-Repository ML Dataset Documentation Scoring"
**Collected by:** Revision Agent (Round 1)
**Date:** 2026-03-15
**Source review:** 065_review_r1.md

---

## Instructions for Human Reviewer

The following are MINOR issues identified by the adversarial review (Round 1). These issues involve style, grammar, formatting, and editorial judgment decisions that should NOT be auto-fixed by the revision agent. Each issue is documented here for human decision-making.

**Do NOT simply apply all of these mechanically.** Each requires a judgment call about whether the fix is appropriate, consistent with author intent, and worth the revision cost.

---

## MINOR Issues

### MINOR-001: Table Row Ordering Inconsistency (Tables 1 and 4)

**Location:** Table 1 (Section 3.2) vs. Table 4 (Section 5.3)

**Issue:** Tables 1 and 4 list DTS sections in different orders.
- Table 1 order: Motivation, Composition, Collection, Preprocessing, Uses, Distribution
- Table 4 order: Motivation, Composition, Collection, Distribution, Preprocessing, Uses
- Ground truth YAML order: motivation, composition, collection, preprocessing, uses, distribution

Distribution appears before Preprocessing and Uses in Table 4, but after them in Table 1 and the ground truth. This can confuse readers who cross-reference both tables.

**Suggested fix:** Reorder Table 4 rows to match Table 1 ordering (i.e., move Distribution row to the end, after Uses).

**Human judgment needed:** This is a cosmetic fix. The scientific content is unchanged. The current Table 4 ordering (Distribution before the near-zero sections) may have been intentional to keep the near-zero rows visually prominent at the bottom. Decide whether consistency or visual emphasis takes priority.

---

### MINOR-002: UCI Target Population Discrepancy ("~100" vs. 62 collected)

**Location:** Section 3.3, "Target Repositories": `"UCI n≈100 (full population)"`; Section 4.1 Table 2: UCI Collected = 62

**Issue:** Section 3.3 sets UCI target as "~100 (full population)" but only 62 were collected and the ground truth confirms 62. The discrepancy between "~100 full population" and 62 collected is not explained in the data collection section.

**Suggested fix:** Add a footnote or parenthetical in Section 3.3 clarifying: "Initial estimate ~100; actual accessible population via `ucimlrepo` v0.0.7 is 62 datasets." Or alternatively: change "~100 (full population)" to "62 (full accessible population via ucimlrepo)."

**Human judgment needed:** The explanation for why ~100 became 62 may relate to the UCI API's actual accessible scope at time of collection. If the author knows the exact reason (e.g., API pagination limits, dataset availability changes), the note should be specific. The reviewer raised this as a transparency concern.

---

### MINOR-003: Paper Title Subtitle Inconsistency (YAML Header vs. Ground Truth)

**Location:** Paper YAML front-matter header vs. `065_ground_truth.yaml`

**Issue:**
- Paper YAML header title: "Automated DTS-Weighted Cross-Repository ML Dataset Documentation Scoring: **Building the Instrument and Finding What It Cannot Measure**"
- Ground truth `paper_title`: "Automated DTS-Weighted Cross-Repository ML Dataset Documentation Scoring: **Feasibility and the Documentation API Gap**"

These are two different subtitles for the same paper. Internal metadata is inconsistent.

**Suggested fix:** Choose one subtitle and align both the paper YAML header and the ground truth YAML. Either subtitle is acceptable — the current paper subtitle is more evocative while the ground truth subtitle is more descriptive/academic.

**Human judgment needed:** This is a metadata alignment issue. The author should choose the intended final title and update both files consistently. Note that the paper subtitle will appear in all citations and proceedings listings.

---

### MINOR-004: Section 6.5 Broader Impact Too Thin for ICML

**Location:** Section 6.5 "Broader Impact"

**Issue:** The current Broader Impact statement is two sentences and addresses only positive applications. ICML submissions are expected to address potential harms and misuse scenarios as well as benefits.

**Current text:**
> "This work provides an automated, open-source DTS-weighted documentation scoring pipeline for practitioners and platform operators. Automated DTS scores should be interpreted as measuring *structured API field coverage* — a triage tool for identifying obvious documentation gaps, not a replacement for human assessment of dataset fitness-for-purpose."

**Suggested additions to consider:**
- Potential misuse: automated DTS scores used as gatekeeping criteria by platforms before community validation of the metric's construct validity
- Risk of false assurance: high DTS scores (from well-populated API fields) do not guarantee dataset fitness for sensitive applications
- Equity consideration: repositories with richer structured API infrastructure (e.g., HuggingFace) will score systematically higher than equivalent-quality datasets on smaller repositories, which may create unfair competitive advantages in documentation audits

**Human judgment needed:** The author should decide how much to expand and what harms are most salient to the intended audience. Over-expanding the Broader Impact can dilute the paper; the goal is substantive acknowledgment, not exhaustive risk enumeration.

---

### MINOR-005: Abstract p-value Precision

**Location:** Abstract, proxy r statement

**Issue:**
- Abstract says: `"proxy r=0.989, p<0.001"`
- Body (Section 5.2) reports: `"p=5.77×10⁻¹⁰¹"`

"p<0.001" is technically accurate but dramatically understates the significance (the actual p-value is approximately 10^98 orders of magnitude more extreme). Some venues prefer reporting the full value or a tighter bound like "p<10⁻⁹⁰" when the actual value is astronomically small. With n=120 and r=0.989, a reader familiar with statistics will expect a much more extreme p-value than 0.001.

**Suggested fix options:**
1. Keep `p<0.001` (conservative, safe, technically true)
2. Change to `p<10⁻⁹⁰` (more informative without full precision)
3. Report full value in abstract: `p=5.77×10⁻¹⁰¹` (maximally precise but unusual in abstracts)

**Human judgment needed:** Abstract real estate is precious. The improvement from option 1 to option 2 is marginal but may satisfy reviewers who are sensitive to p-value reporting conventions. Option 3 is unusual in abstracts but maximally transparent.

---

### MINOR-006: Rondina et al. Repository Count Discrepancy

**Location:** Section 2.2, sentence: `"Rondina et al. [2025] is the most direct predecessor: manual scoring of 100 datasets across four repositories using DTS"`

**Issue:** The paper states Rondina et al. scored across "four repositories" while the current study covers three repositories (HuggingFace, OpenML, UCI). This is correct as stated (Rondina et al. covered four), but could confuse readers who may assume our study also covers four. No explicit acknowledgment is made that our coverage scope differs.

**Suggested fix:** Add a parenthetical clarification: `"...scoring of 100 datasets across four repositories using DTS, while our study covers three (HuggingFace Hub, OpenML, UCI)"` — or add a brief note that our three-repository scope differs from Rondina et al.'s four.

**Human judgment needed:** This is a minor clarity improvement. The author may prefer to leave it as-is since the corpus definition is clearly stated in Section 3.3 and Table 2. The reviewer noted it as a potential source of reader confusion, not a factual error.

---

### MINOR-007: Oreamuno et al. Reference Placeholder Text Formatting

**Location:** References section, Oreamuno entry

**Issue:** The reference reads: `"Oreamuno, [First Name] et al."` with visible placeholder text `[First Name]`. This is non-standard reference formatting that will be immediately visible to any reviewer and suggests incomplete preparation.

**Current text:**
> `Oreamuno, [First Name] et al. (2024). [UNVERIFIED — Title TBD. Cited as finding 71.52% of HuggingFace Hub dataset cards have substantial undocumented sections via binary field presence checks on n=6,758 cards.] *[Venue TBD]*.`

**Suggested fix options:**
1. Verify the citation and replace with correct author name, title, and venue before submission
2. If unverifiable: use `"Oreamuno et al."` without `[First Name]` (dropping the placeholder), and mark as `[UNVERIFIED]` clearly

**Human judgment needed:** This is a mandatory fix before submission but requires the author to either verify the citation or deliberately adopt a consistent unverified-citation formatting convention. The `[First Name]` placeholder is an artifact of automated generation and should not appear in any submitted version.

---

## Summary Table

| ID | Location | Issue Type | Effort | Priority |
|----|----------|------------|--------|----------|
| MINOR-001 | Tables 1 & 4 | Formatting consistency | Low | Low |
| MINOR-002 | §3.3, Table 2 | Transparency/clarification | Low | Medium |
| MINOR-003 | YAML header | Metadata consistency | Very low | Low |
| MINOR-004 | §6.5 Broader Impact | Content expansion | Medium | Medium (ICML requirement) |
| MINOR-005 | Abstract | Reporting precision | Very low | Low |
| MINOR-006 | §2.2 | Clarity | Very low | Low |
| MINOR-007 | References | Placeholder cleanup | Low | High (submission blocker) |

**Total MINOR issues: 7**

**Note on MINOR-007:** While classified as MINOR in the review, the `[First Name]` placeholder in the references section is arguably a submission-blocking cosmetic issue. It should be resolved before any version is shared externally.

---

## Round 2 Issues

**Collected by:** Revision Agent (Round 2)
**Date:** 2026-03-15
**Source review:** 065_review_r2.md

The following are MINOR issues identified by the adversarial review (Round 2). These require human editorial judgment and must NOT be auto-fixed.

---

### R2-MINOR-001: Table 3 Proxy r Margin — Residual Arithmetic Note if Relative Format Ever Adopted

**Location:** Table 3, Section 5.2

**Issue:** The R2 revision uses absolute percentage-point margins (+21.8 pp and +28.9 pp), which is correct. However, if a future editor ever revisits this table and prefers the relative-excess format (Option B from the review), they must use +41.3% (not +40.9%) for the proxy r row. The value 40.9 cannot be derived from any standard computation and should not reappear.

**Human judgment needed:** No action required for R2. This note is a safeguard for future editorial rounds — if the margin column format is ever changed back to relative excess, the proxy r value must be 41.3%, not 40.9%.

---

### R2-MINOR-002: "pre-registered" Language in §4.2 May Misread at ICML

**Location:** Section 4.2, "Comparison Reference" — sentence: "We compare against pre-registered gate thresholds (coverage ≥ 0.70, proxy r ≥ 0.70)"

**Issue:** At ICML and similar venues, "pre-registered" carries the specific connotation of a formal public pre-registration (e.g., via OSF, AsPredicted, or a registered report). The gate thresholds in this paper were pre-specified in an internal `verification_state.yaml` file (Phase 2B of the YouRA pipeline), not in a public registry. Using "pre-registered" may lead reviewers to search for a registration that does not exist.

**Suggested fix:** Replace "pre-registered" with "pre-specified" or "set prior to experimentation" to convey the same meaning without implying a formal public registry.

**Human judgment needed:** The author should confirm the actual registration status. If no public pre-registration was filed, "pre-specified" is the safer and more accurate term. If a public registration was filed, the registry and ID should be cited explicitly.

---

### R2-MINOR-003: Table 3 Has No Caption

**Location:** Table 3, Section 5.2

**Issue:** Table 3 ("Gate Criteria Results") has no caption. All other tables in the paper have descriptive headers embedded in the text or as bold lead-ins. A brief caption aids self-sufficiency for readers who jump to tables directly.

**Suggested fix:** Add a brief caption such as: "Table 3: Gate criteria thresholds, achieved values, and absolute margins above threshold."

**Human judgment needed:** This is a presentation improvement. The author should decide whether to add a formal caption or leave the table header text as implicit context. In ICML proceedings format, table captions are typically required; this may need to be resolved at formatting stage.

---

### R2-MINOR-004: "confirming" in §6.1 Discussion Is Slightly Strong

**Location:** Section 6.1, sentence: "The r=0.989 proxy correlation, while confirming algorithmic reliability, reflects an important mathematical relationship..."

**Issue:** The word "confirming" is present in a cautious context that immediately walks back its own strength by explaining why r≈1 is expected by construction. This creates a subtle internal tension: the sentence opens with "confirming" (a claim of positive evidence) and then explains why the evidence is weaker than it appears. "Consistent with" or "consistent with but not independently confirming" would be more precisely calibrated.

**Suggested fix:** Change "while confirming algorithmic reliability" to "while consistent with algorithmic reliability" or "while indicating consistent algorithmic behavior."

**Human judgment needed:** This is a minor wording refinement. The author should decide whether "confirming" is the intended register. The current sentence is defensible as written; the suggested change makes the epistemics slightly more precise but at the cost of some rhetorical directness.

---

### R2-MINOR-005: "Structurally Independent" Language in §3.4 — Future Edit Consistency Note

**Location:** Section 3.4, Validation Protocol

**Issue:** The current Section 3.4 correctly states "Both weighted and unweighted scores are computed from the same underlying binary field presence values; they differ only in the weight vector applied." This is accurate and appropriate. However, a note in the Phase 4 validation source file (`04_validation.md`) uses the phrasing "structurally independent" which, if incorporated into a future revision of §3.4, would misrepresent the relationship between the two scores. The two scores are NOT structurally independent — they share the same binary field presence inputs.

**Note for human reviewer:** No change needed in R2. This is a consistency safeguard: if §3.4 is ever revised by referencing `04_validation.md` directly, editors should not adopt the "structurally independent" phrasing. The current R2 language is correct and should be preserved in future rounds.

---

## Summary Table (Round 2 MINOR Issues)

| ID | Location | Issue Type | Effort | Priority |
|----|----------|------------|--------|----------|
| R2-MINOR-001 | Table 3 | Arithmetic consistency note (future-proofing) | None | Low |
| R2-MINOR-002 | §4.2 | Terminology precision (pre-registered vs. pre-specified) | Very low | Medium (venue risk) |
| R2-MINOR-003 | Table 3 | Missing caption | Very low | Low–Medium (ICML formatting) |
| R2-MINOR-004 | §6.1 | Wording precision ("confirming" → "consistent with") | Very low | Low |
| R2-MINOR-005 | §3.4 | Future edit consistency safeguard | None | Low |

**Total new MINOR issues in Round 2: 5**

**Previously documented MINOR issues from Round 1** (MINOR-001 through MINOR-007) remain open for human editorial judgment. Status unchanged.
