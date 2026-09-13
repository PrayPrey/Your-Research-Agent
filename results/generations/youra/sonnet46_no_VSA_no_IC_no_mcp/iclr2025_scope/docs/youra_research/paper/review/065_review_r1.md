# Adversarial Review — Round 1

**Paper:** The Cache Format Matters: A Reproducible Baseline and Implementation Protocol for KV Cache Eviction in Modern Transformer Libraries
**Reviewed:** 2026-08-27T07:00:00+00:00
**Reviewer:** Adversary Agent v2 (three-persona)
**Round:** R1 — Accuracy, Engagement, Credibility

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Accuracy | 0 | 1 | NEEDS_WORK |
| Engagement | 0 | 1 | NEEDS_WORK |
| Credibility | 0 | 2 | NEEDS_WORK |
| **TOTAL** | **0** | **4** | NEEDS_WORK |

**Recommendation:** MINOR_REVISION

All numerical claims verified against ground truth — no FATAL accuracy errors. No fundamental engagement failures. Four MAJOR issues identified across accuracy, engagement, and credibility dimensions. All are addressable within the existing paper structure.

---

## Part 1: Accuracy Check (Persona 1: Accuracy Checker)

### Ground Truth Verification Table

| Metric | Paper Claims | Ground Truth | Match? |
|--------|--------------|--------------|--------|
| M0 macro-F1 | 0.0875 | 0.0875 | ✓ |
| M0 NarrativeQA F1 | 0.09 | 0.09 | ✓ |
| M0 HotpotQA F1 | 0.09 | 0.09 | ✓ |
| M0 2WikiMQA F1 | 0.11 | 0.11 | ✓ |
| M0 MuSiQue F1 | 0.06 | 0.06 | ✓ |
| M1 F1 (all tasks) | 0.00 | 0.00 | ✓ |
| KV shape k | 2048 from 4096 | 2048 from 4096 | ✓ |
| Layers confirmed | 32/32 | 32/32 | ✓ |
| Observation window W | 16 | 16 | ✓ |
| Retention ratio | 50% | 50% | ✓ |
| Model | LLaMA-2-7B-chat-hf | LLaMA-2-7B-chat-hf | ✓ |
| Hypothesis status | INCONCLUSIVE | INCONCLUSIVE | ✓ |

All numerical claims match ground truth exactly. No accuracy FATAL issues.

### MAJOR Issues — Accuracy

#### MAJOR-ACC-001: F1 Scale Note Is Present But Insufficiently Prominent

**Location:** Section 4.4 Implementation Details (Note on F1 scale)
**Issue:** The critical note that F1 values are on the raw 0–1 scale (not percentage scale) appears buried in Section 4.4 as a single line. The gate criterion confusion (≥2.0 intended as percentage points, corrected to ≥0.02 raw) is documented in Section 6.2 (L2), but a reader scanning Tables 1–2 will see "0.0875" and "0.09" without immediately knowing these are raw values. The LongBench community norm is to report F1 as percentages. A reviewer may flag the numbers as suspiciously low before reading Section 4.4.

**Evidence:**
- Table 1 header: "M0 F1 (raw)" — the "(raw)" annotation is present but only in the table header, not the Abstract or Section 5 prose.
- Abstract says "macro-F1=0.0875" without "(raw)" qualifier.
- Section 5.1 prose says "macro-average of 8.75%" — inconsistently switches to percentage representation mid-paragraph.

**Impact:** Creates reader confusion: Abstract says 0.0875, Section 5.1 says 8.75%, Table 1 says 0.0875. Inconsistent representation across the same paper is an accuracy/consistency issue.

**Suggested Fix:** Standardize to ONE format throughout. Recommend: use percentage (8.75%) consistently in prose, including Abstract. Tables may show raw values if labeled "(raw scale: divide by 100)". Add a single sentence in Section 4.4 and the Abstract footnote/parenthetical: "(raw scale; 8.75% in standard LongBench reporting)".

---

## Part 2: Engagement Check (Persona 2: Bored Reviewer)

### Bored Reviewer Verdict

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | ✓ | Strong — opens with concrete finding, gives numbers |
| Problem clear in 1 min? | ✓ | Yes — memory bottleneck and eviction policy comparison clear |
| Novelty clear in 2 min? | ✓ | Yes — DynamicCache failure mode novelty well-stated |
| Figure 1 self-explanatory? | N/A | No Figure 1 present — significant weakness |
| Would continue reading? | ✓ | Yes — counterintuitive finding creates curiosity |

**Attention Lost At:** Section 3.1 (Experimental Framework) — dense enumeration list with 7 bullet items describing codebase architecture. Not a rejection trigger but noticeable attention drop.

### No FATAL Engagement Issues

The Abstract hook is strong: "A correctly shaped evicted KV cache does not guarantee correct generation." This is a counterintuitive engineering finding, clearly stated, with numbers. The Bored Reviewer would continue reading. No ENGAGE-FATAL issues.

### MAJOR Issues — Engagement

#### MAJOR-ENG-001: Absence of Figures Significantly Weakens Visual Persuasion

**Location:** Throughout — no figures present
**Issue:** The paper has zero figures. ICML reviewers scan for visual anchors. The most important insight — that M0 works while M1 fails despite identical shapes — would be immediately apparent as a bar chart (M0 F1 bar: 0.09, 0.09, 0.11, 0.06; M1 F1 bars: all 0.00). The diagnostic chain (Table 3) would benefit from a pipeline diagram with ✓/✗ annotations at each step. Without figures, the paper relies entirely on text and tables to carry visual weight that most ICML papers distribute across 2–4 figures.

**Reader Impact:** Reviewer scanning the paper at 3 minutes sees only dense text and three tables. The "at-a-glance" understanding is severely limited. This is a MAJOR weakness, not fatal — the ground_truth.yaml alert_flags already correctly identify this.

**Suggested Fix:** The paper's own statistics block already recommends generating: (1) pipeline diagram with ✓/✗ annotations, (2) M0 per-task F1 bar chart, (3) M1 vs M0 comparison. For the current incomplete experiment, at minimum add a single-panel figure showing M0 vs M1 F1 per task as a side-by-side bar chart — this takes ~10 lines of matplotlib and is essential for a visually persuasive paper.

**Note:** The paper explicitly acknowledges zero figures in its statistics block. This is self-aware but does not mitigate the ICML reviewer's experience.

---

## Part 3: Credibility Check (Persona 3: Skeptical Expert)

### Novelty Claims Audit

| Claim | Location | Verified? | Notes |
|-------|----------|-----------|-------|
| DynamicCache failure undocumented in prior work | §1, §2.4, §6.1 | PLAUSIBLE | No prior KV eviction paper documents post-hoc reconstruction. Claim is appropriately hedged "to our knowledge." |
| First unified codebase for M1/M2 comparison | §1, §2.3 | PLAUSIBLE | Prior work uses per-method codebases. Reasonable claim. |
| Pre-validation protocol (5-example abort) | §1, §3.5 | PLAUSIBLE | Novel operational contribution, appropriately modest in claim. |

No false "first to" claims found. Novelty claims are appropriately hedged with "to our knowledge" qualifiers. CRED-FATAL-001 not triggered.

### Baseline Fairness Audit

This paper does not compare against baselines in the traditional sense — it reports a diagnostic experiment where M1 failed before any comparison was possible. The "baseline" is M0 (full KV), which is the paper's own working condition. No fairness issue.

### MAJOR Issues — Credibility

#### MAJOR-CRED-001: Zero Citation Verification — Unverified arXiv IDs Presented Without Disclaimer in Main Text

**Location:** Section 2 (Related Work), References section
**Issue:** All 7 references are explicitly marked "[UNVERIFIED]" in the paper's statistics block. However, the main text of Section 2 (Related Work) treats these citations as authoritative, citing specific findings ("H2O reports substantial perplexity improvement... at 20% KV retention", "SnapKV reports strong results on LongBench... at 40-60% KV retention", "Spearman r>0.85 on OPT-6.7B"). A reviewer who checks even one citation and finds the arXiv ID wrong, or the attributed finding misquoted, will immediately reject the paper.

**Evidence:** Ground truth alert flag: "All citations are [UNVERIFIED] — Semantic Scholar MCP unavailable in this session. Verify all 7 arXiv IDs before submission." This is rated HIGH severity in the ground truth and is not adequately addressed in the paper itself.

**Impact:** Seven unverified citations with specific quantitative claims attributed to each. If any are wrong — wrong arXiv ID, wrong author order, wrong benchmark number — the credibility of the Related Work section is destroyed. The paper cannot be submitted in this state.

**Suggested Fix:** Before submission: (1) verify all 7 arXiv IDs are valid and match cited works; (2) verify all attributed quantitative claims against the actual papers. Add explicit "(citation verified)" or "(citation unverified — to be verified before submission)" markers in the draft if submitting a camera-ready draft. This is a pre-submission blocker, not a paper content issue.

**Note for Review Context:** This is classified as MAJOR (not FATAL for the review process) because citation verification is a pre-submission task that does not change the paper's scientific content. The paper's findings are independent of whether H2O achieves 20% or 25% retention improvement. However, no paper should be submitted with unverified citations.

#### MAJOR-CRED-002: Page Count Exceeds ICML Limit — No Condensation Strategy in Paper

**Location:** Paper statistics block, Related Work §2.4, Methodology §3.1
**Issue:** The paper's own statistics block estimates ~11 pages against an ICML limit of 8 pages (excluding references). The condensation requirement (~3 pages) is significant. Ground truth alert flag rates this HIGH severity. The paper identifies candidates (Related Work §2.4 and Methodology §3.1) but provides no condensation plan.

**Evidence:** word_counts total ≈ 3865 body words. At 350 words/page for ICML two-column format, this is approximately 11 text-pages. ICML 2025 allows 8 pages + unlimited references.

**Impact:** An ~11-page paper submitted to an 8-page venue will be desk-rejected. This is a formatting blocker.

**Suggested Fix:**
- Section 2.4 ("Why Prior Work Does Not Encounter the DynamicCache Failure") is 1 full page. It can be condensed to 2 paragraphs (~200 words saved, ~0.6 pages).
- Section 3.1 (Experimental Framework) is a dense 7-bullet enumeration. Reduce to 3 bullets or a brief paragraph (~150 words saved, ~0.4 pages).
- Introduction §1 "The Memory Bottleneck" subsection is standard background that can be trimmed or folded into the first paragraph.
- Total savings needed: ~1.5 pages of text. Achievable without losing scientific content.

---

## Part 4: Human Review Notes

| Location | Note | Type |
|----------|------|------|
| §5.1 | "The macro-average of 8.75% is additionally consistent with..." — "additionally consistent" is awkward phrasing | style |
| §6.2 L2 | "F1 > 20" reference — explained in paper but phrasing "sanity check threshold (F1 > 20)" without context first is confusing | clarity |
| §3.3 | "Steps 1-4 are mechanically correct (shape log confirms). Step 5 is where the failure occurs." — sentence fragment "Step 5 is where the failure occurs" is stylistically weak | style |
| §2.1 | "lower-bound baseline" → "lower-bound reference" (StreamingLLM is not a baseline for comparison, it's a reference method) | clarity |
| Abstract | "making direct comparison impossible" → "making direct comparison infeasible" (stronger and more precise) | style |
| §4.3 Table | "Not reached" for M2/M6 Status — consider "Not executed (experiment terminated)" for precision | clarity |

---

## Summary for Revision Agent

### Priority Fix List

1. **MAJOR-ACC-001:** Standardize F1 scale representation — pick ONE format (recommend percentage) and use it consistently in Abstract, prose, and table headers. Current inconsistency (0.0875 in Abstract, 8.75% in §5.1, "raw" in table) will confuse reviewers.

2. **MAJOR-CRED-001:** Add a clear disclaimer in Related Work or a footnote stating all citations require pre-submission verification. Consider adding "(to be verified)" markers to specific quantitative claims attributed to prior work.

3. **MAJOR-CRED-002:** Add a "Formatting Note" section or inline note identifying the condensation plan: §2.4 → 2 paragraphs, §3.1 → 3 bullets, Introduction subsection trimmed. This documents the path to 8-page compliance.

4. **MAJOR-ENG-001:** Add at minimum a figure placeholder (captioned figure description) for the M0 vs M1 bar chart, signaling to reviewers that a figure will be present. Better: generate and insert the actual bar chart.

### Key Concerns

- Citations are unverified — this is the highest-risk pre-submission item. The paper's scientific content is sound, but unverified quantitative claims attributed to prior work are a credibility risk.
- Page count: ~11 pages for an 8-page venue. Condensation is required before submission.

### What's Working

- Abstract hook is excellent — counterintuitive finding stated immediately with evidence.
- All numerical claims match ground truth exactly — no accuracy FATAL issues.
- Hypothesis status (INCONCLUSIVE, not REFUTED) is correctly and consistently stated throughout.
- The DynamicCache failure mode is clearly documented with the diagnostic chain (Table 3).
- Limitations section (§6.2) is honest and specific — L1 through L4 are all legitimate limitations clearly stated.
- The pre-validation protocol (§3.5) is a practical, reusable contribution clearly described.
- Novelty claims are appropriately hedged ("to our knowledge") — no false "first to" claims.
