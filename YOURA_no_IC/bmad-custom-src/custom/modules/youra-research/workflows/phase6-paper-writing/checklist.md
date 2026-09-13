# Phase 6: Paper Writing - Validation Checklist

## Step Execution Tracking

### Step 1: Initialize
- [ ] Output folder structure created:
  - [ ] `{research_folder}/paper/` created
  - [ ] `paper/sections/` created
  - [ ] `paper/figures/` created
- [ ] **Figures collected from Phase 4 & 5 (LLM-autonomous):**
  - [ ] Phase 4 figures discovered (`{hypothesis_folder}/figures/` and `code/outputs/`)
  - [ ] Phase 5 figures discovered (`baseline_comparison/figures/`)
  - [ ] All discovered figures copied to `paper/figures/`
  - [ ] Sequential figure numbers assigned (fig_1, fig_2, ...)
  - [ ] Section assignments determined based on content
- [ ] Figure registry created (`figure_registry.yaml`) with actual discovered figures
- [ ] **Required artifacts verified:**
  - [ ] `verification_state.yaml` exists
  - [ ] `03_refinement.yaml` exists
  - [ ] `02b_verification_plan.md` exists
  - [ ] At least one hypothesis COMPLETED
  - [ ] `045_validated_hypothesis.md` exists (Phase 4.5 synthesis)
- [ ] Main hypothesis info loaded
- [ ] Checkpoint file initialized (`06_paper_checkpoint.yaml`)

### Step 2: Narrative Design
- [ ] Checkpoint loaded
- [ ] **All Phase 0-5 artifacts loaded for narrative synthesis:**
  - [ ] 00_brainstorm_session.md (if exists)
  - [ ] 01_targeted_research.md
  - [ ] 03_refinement.yaml
  - [ ] 02_synthesis.yaml
  - [ ] 02b_verification_plan.md
  - [ ] 045_validated_hypothesis.md (Phase 4.5 — PRIMARY evidence source)
  - [ ] 05_baseline_comparison.md (per hypothesis, if available)
- [ ] **Narrative Blueprint designed:**
  - [ ] Hook strategy defined (NOT "X is important")
  - [ ] Opening statement crafted
  - [ ] Problem framing at 3 levels (big picture → technical → specific gap)
  - [ ] Key insight (aha moment) articulated
  - [ ] Evidence narrative structured
  - [ ] Section-level goals set (per section)
  - [ ] Conclusion callback to hook planned
- [ ] `06_narrative_blueprint.yaml` saved
- [ ] Checkpoint updated (narrative_design: complete)

### Step 3: Story Group A - Foundation (Introduction + Related Work + Methodology)
- [ ] **Task Agent context** (shared within group)
- [ ] **Input artifacts loaded:**
  - [ ] 06_narrative_blueprint.yaml (REQUIRED)
  - [ ] 045_validated_hypothesis.md (Phase 4.5 — refined claims, verified insight)
  - [ ] 00_brainstorm_session.md (if exists)
  - [ ] 01_targeted_research.md / 01_targeted_research_full.md
  - [ ] 03_refinement.yaml (original hypothesis context)
  - [ ] 02_synthesis.yaml
  - [ ] 02c_experiment_brief.md (per hypothesis)
  - [ ] 03_architecture.md (per hypothesis)
  - [ ] figure_registry.yaml
- [ ] **Introduction generated:**
  - [ ] ~800-1000 words (guideline, not strict)
  - [ ] Hook-based opening (NOT generic "X is important")
  - [ ] Problem framed at 3 levels per narrative blueprint
  - [ ] Key insight previewed
  - [ ] Contributions as story (not just list)
  - [ ] Citations properly formatted
- [ ] **Related Work generated:**
  - [ ] ~600-800 words (guideline)
  - [ ] 2-3 thematic groupings
  - [ ] Minimum 8-10 citations
  - [ ] Citations verified via Semantic Scholar MCP
  - [ ] Positioning statement: existing work insufficient → justify our approach
  - [ ] Differentiates from prior work
  - [ ] No strawman arguments
- [ ] **Methodology generated:**
  - [ ] ~1000-1200 words (guideline)
  - [ ] Connection to key insight from narrative blueprint
  - [ ] Method overview
  - [ ] Key design decisions with rationale (WHY, not just WHAT)
  - [ ] Problem formally defined with notation
  - [ ] Key equations numbered
  - [ ] Sufficient detail for reproduction
  - [ ] Figures integrated naturally (if available)
- [ ] Section files saved:
  - [ ] `sections/01_introduction.md`
  - [ ] `sections/02_related_work.md`
  - [ ] `sections/03_methodology.md`
- [ ] Checkpoint updated (group_a: complete)

### Step 4: Story Group B - Evidence (Experiments + Results + Discussion)
- [ ] **Task Agent context** (shared within group)
- [ ] **Depends on:** Step 3 (Story Group A) completed
- [ ] **Input artifacts loaded:**
  - [ ] 06_narrative_blueprint.yaml (REQUIRED)
  - [ ] 02c_experiment_brief.md (per hypothesis)
  - [ ] 03_prd.md (per hypothesis)
  - [ ] 045_validated_hypothesis.md (Phase 4.5 — PRIMARY evidence source)
  - [ ] 04_validation.md (per hypothesis, optional — for ground truth verification only)
  - [ ] 05_baseline_comparison.md (per hypothesis, if available)
  - [ ] verification_state.yaml
  - [ ] figure_registry.yaml
- [ ] **Experiments generated:**
  - [ ] ~800-1000 words (guideline)
  - [ ] Experimental questions linked to claims from Introduction
  - [ ] Datasets described with statistics and rationale
  - [ ] Baselines listed with citations AND GitHub URLs (if Phase 5 available)
  - [ ] Hyperparameters tabulated
  - [ ] Hardware/software specified
  - [ ] Metrics defined with rationale
  - [ ] Reproducibility addressed
- [ ] **Results generated:**
  - [ ] ~1000-1200 words (guideline)
  - [ ] Main results table with comparison data
  - [ ] **DATA SOURCE:** Phase 5 if available (PRIMARY); Phase 4 if Phase 5 skipped
  - [ ] Statistical significance reported
  - [ ] Ablation study from Phase 4
  - [ ] Each result has "so what?" interpretation
  - [ ] Figures integrated naturally with narrative
- [ ] **Discussion generated:**
  - [ ] ~400-600 words (guideline)
  - [ ] Key findings synthesized
  - [ ] Limitations acknowledged honestly
  - [ ] **Broader Impact Statement PRESENT** (ICML 2025 requirement)
  - [ ] Positive and negative impacts addressed
- [ ] Section files saved:
  - [ ] `sections/04_experiments.md`
  - [ ] `sections/05_results.md`
  - [ ] `sections/06_discussion.md`
- [ ] Checkpoint updated (group_b: complete)

### Step 5: Story Group C - Closure (Conclusion + Abstract LAST)
- [ ] **Task Agent context** (needs full paper context)
- [ ] **Depends on:** Steps 3 AND 4 completed
- [ ] **Input artifacts loaded:**
  - [ ] 06_narrative_blueprint.yaml (REQUIRED)
  - [ ] sections/01_introduction.md (for callback)
  - [ ] sections/03_methodology.md
  - [ ] sections/05_results.md
- [ ] **Conclusion generated FIRST:**
  - [ ] ~300-400 words (guideline)
  - [ ] Callbacks to Introduction hook
  - [ ] Contributions summarized
  - [ ] Key results highlighted
  - [ ] Future work vision
  - [ ] No new information introduced
  - [ ] Memorable ending
- [ ] **Abstract generated LAST (with full context):**
  - [ ] ~150 words
  - [ ] Single paragraph, 4-6 sentences
  - [ ] Contains problem statement
  - [ ] Contains approach summary
  - [ ] Contains key results with ACTUAL numbers (from Phase 4/5)
  - [ ] Contains main contribution
  - [ ] No citations
  - [ ] Compresses full story
- [ ] Section files saved:
  - [ ] `sections/07_conclusion.md`
  - [ ] `sections/00_abstract.md`
- [ ] Checkpoint updated (group_c: complete)

### Step 6: Compile References
- [ ] **Task Agent context** (context isolation)
- [ ] **Depends on:** Steps 3, 4, 5 completed
- [ ] **Input artifacts loaded:**
  - [ ] All section files (for citation extraction)
  - [ ] 01_targeted_research.md / 01_targeted_research_full.md (source)
- [ ] **Semantic Scholar MCP used for verification**
- [ ] References compiled:
  - [ ] All citations collected from sections
  - [ ] BibTeX file generated (`06_references.bib`)
  - [ ] Verification rate >= 90%
  - [ ] Unverified citations flagged
  - [ ] Consistent formatting
  - [ ] Sorted alphabetically
- [ ] Checkpoint updated

### Step 7: Finalize and Merge (Full Context)
- [ ] **Main Session** (FULL CONTEXT required)
- [ ] **Depends on:** Step 6 completed
- [ ] **ALL section files loaded (00-07)**
- [ ] **Cross-section coherence check against narrative blueprint:**
  - [ ] Terminology consistency verified
  - [ ] Claim-evidence alignment verified
  - [ ] Figure references resolved
  - [ ] Hook→Callback arc verified (Introduction ↔ Conclusion)
- [ ] **Final paper assembled (`06_paper.md`):**
  - [ ] All sections merged in correct order
  - [ ] Section numbering correct
  - [ ] Figure-content natural matching
  - [ ] Captions complete
  - [ ] Figure placements inserted
- [ ] **ICML 2025 format compliance (final verification):**
  - [ ] Main paper <= 8 pages
  - [ ] Abstract single paragraph
  - [ ] Impact Statement present
- [ ] **Ground truth extracted for Phase 6.5 adversarial review:**
  - [ ] Actual metric values from Phase 4/5
  - [ ] Claimed vs actual comparison table
  - [ ] Hyperparameters from implementation
  - [ ] Baseline comparison data
  - [ ] `065_ground_truth.yaml` generated
- [ ] Final statistics generated
- [ ] verification_state.yaml updated
- [ ] Checkpoint finalized (status: COMPLETED)

---

## Pre-Execution Checks

### Input Verification
- [ ] `verification_state.yaml` exists and is valid
- [ ] `03_refinement.yaml` exists (required)
- [ ] `02b_verification_plan.md` exists (required)
- [ ] At least one hypothesis has `status: COMPLETED`
- [ ] `045_validated_hypothesis.md` exists (Phase 4.5 synthesis — PRIMARY source)
- [ ] `04_validation.md` exists for completed hypotheses (optional — for ground truth verification)
- [ ] Phase 4 Gate result documented (PASS/PARTIAL/FAIL)
- [ ] **Phase 5 DETERMINES_SUCCESS gate PASSED, OR `baseline_comparison.status == SKIPPED`** (when `skip_baseline_comparison=true`)
- [ ] **`05_baseline_comparison.md` exists** (if Phase 5 was executed; not required when skipped)

### Environment
- [ ] Serena MCP server available (figure discovery, code analysis)
- [ ] Semantic Scholar MCP server available (citation verification)
- [ ] Write access to output folder

---

## DATA SOURCE PRINCIPLE

<critical>
**Phase 6 is reachable when:**
- Phase 5 DETERMINES_SUCCESS gate PASSES, **OR**
- Phase 5 is SKIPPED (`skip_baseline_comparison=true` in module.yaml)

When Phase 5 was executed: baseline comparison data is available and should be used as PRIMARY source.
When Phase 5 was skipped: Phase 4 validation data serves as the primary source for results.
</critical>

### Data Source Mapping

| Paper Section | Primary Source | Secondary Source | Rationale |
|---------------|----------------|------------------|-----------|
| **Baselines** | Phase 5 (if available) | Phase 4 | Official GitHub implementations |
| **Main Results** | **Phase 5** (if available) | **Phase 4** | Fair comparison under identical conditions |
| **Ablation** | Phase 4 | - | Component-wise PoC analysis |
| **Analysis** | Both (or Phase 4 only) | - | Comprehensive interpretation |

---

## Story Group Context Protocol

### Purpose
- Narrative coherence within story groups
- Context isolation between groups
- Full context for Closure and Finalize

### Implementation
- [ ] Step 2 (Narrative Design) runs in Main Session with ALL artifacts
- [ ] Steps 3-5 (Story Groups) run in Task Agent context
- [ ] Within groups: sections share context for narrative coherence
- [ ] Between groups: context isolation (Group B depends on Group A completion but not context)
- [ ] Step 5 (Closure) has access to ALL previous section outputs
- [ ] Step 7 (Finalize) reads ALL sections in Main Session context

---

## MCP Server Usage

### Serena MCP (Figure Discovery & Code Analysis)
- [ ] `mcp__serena__list_dir` for figure folder scan
- [ ] `mcp__serena__find_file` for specific figure types
- [ ] `mcp__serena__get_symbols_overview` for code structure
- [ ] Used in Step 1 (Initialize), Step 3 (Methodology)

### Semantic Scholar MCP (Citation Verification)
- [ ] Used in Step 3 (Related Work)
- [ ] Used in Step 6 (References)
- [ ] Verification rate tracked

---

## MCP ERROR RETRY PROTOCOL Compliance

- [ ] All MCP errors trigger retry
- [ ] 15-second delay between retry attempts
- [ ] Maximum 3 retry attempts per call
- [ ] Only skip/fail after 3 consecutive failures

---

## ICML 2025 Format Compliance

### Structure
- [ ] Main paper <= 8 pages
- [ ] Abstract: single paragraph, no section number
- [ ] Maximum 3 heading levels used
- [ ] Impact Statement in Discussion section
- [ ] References unlimited (separate from page limit)
- [ ] Appendix unlimited (if needed)

### Style
- [ ] Third person voice
- [ ] Present tense for facts, past for experiments
- [ ] No informal language
- [ ] No first-person claims ("I believe")
- [ ] Professional academic tone

### Narrative Quality
- [ ] Hook-based opening (NOT "X is important")
- [ ] Problem framing at 3 levels
- [ ] Key insight clearly articulated
- [ ] Conclusion callbacks to Introduction hook
- [ ] Abstract compresses full story with actual numbers

### Citations
- [ ] Format: [Author et al., Year]
- [ ] All claims supported by citations or data
- [ ] Self-citations appropriate (not excessive)
- [ ] Recent work included (2022-2025)
- [ ] Seminal work referenced

---

## Word Count Summary

| Section | Guideline | Actual | Status |
|---------|-----------|--------|--------|
| Abstract | ~150 words | ___ | [ ] |
| Introduction | ~800-1000 words | ___ | [ ] |
| Related Work | ~600-800 words | ___ | [ ] |
| Methodology | ~1000-1200 words | ___ | [ ] |
| Experiments | ~800-1000 words | ___ | [ ] |
| Results | ~1000-1200 words | ___ | [ ] |
| Discussion | ~400-600 words | ___ | [ ] |
| Conclusion | ~300-400 words | ___ | [ ] |
| **Total** | **~5050-6400 words** | ___ | [ ] |

**Note:** Focus on narrative quality over hitting exact word counts.

---

## Citation Verification Summary

| Metric | Value |
|--------|-------|
| Total Citations | ___ |
| Verified (Semantic Scholar) | ___ |
| Partially Verified | ___ |
| Unverified | ___ |
| **Verification Rate** | ___% |

### Unverified Citations (Require Review)
1. [ ] ___
2. [ ] ___
3. [ ] ___

---

## Output Verification

### Required Outputs

| Output | Location | Verified |
|--------|----------|----------|
| `06_paper.md` | `{research_folder}/paper/` | [ ] |
| `06_references.bib` | `{research_folder}/paper/` | [ ] |
| `06_narrative_blueprint.yaml` | `{research_folder}/paper/` | [ ] |
| `065_ground_truth.yaml` | `{research_folder}/paper/` | [ ] |
| `06_paper_checkpoint.yaml` | `{research_folder}/paper/` | [ ] |
| `figure_registry.yaml` | `{research_folder}/paper/` | [ ] |
| `sections/00_abstract.md` | `{research_folder}/paper/sections/` | [ ] |
| `sections/01_introduction.md` | `{research_folder}/paper/sections/` | [ ] |
| `sections/02_related_work.md` | `{research_folder}/paper/sections/` | [ ] |
| `sections/03_methodology.md` | `{research_folder}/paper/sections/` | [ ] |
| `sections/04_experiments.md` | `{research_folder}/paper/sections/` | [ ] |
| `sections/05_results.md` | `{research_folder}/paper/sections/` | [ ] |
| `sections/06_discussion.md` | `{research_folder}/paper/sections/` | [ ] |
| `sections/07_conclusion.md` | `{research_folder}/paper/sections/` | [ ] |

**NOTE:** Overleaf LaTeX generation is handled by Phase 6.5.1 (after adversarial review).

---

## Figure-Content Integration Quality

### Per-Figure Checklist
- [ ] Context setup (1-2 sentences BEFORE figure)
- [ ] Figure placed immediately after introduction
- [ ] Interpretation (2-3 sentences AFTER figure)
- [ ] Caption includes key takeaway
- [ ] Figure numbered sequentially
- [ ] Referenced in text before appearing

### Figure Verification Matrix

> **Dynamic:** Generate matrix based on figures in `figure_registry.yaml`.

| Fig # | ID | Section | Introduced | Interpreted | Caption OK |
|-------|-----|---------|------------|-------------|------------|
| {n} | {fig_id} | {section} | [ ] | [ ] | [ ] |

*Create one row per figure from the registry.*

---

## Final Quality Gates

### Must Pass (CRITICAL)
- [ ] All 8 sections present
- [ ] Narrative Blueprint generated (Step 2)
- [ ] Broader Impact Statement included
- [ ] No placeholder text remaining
- [ ] No [CITE:...] markers unresolved
- [ ] No [TO BE FILLED] markers remaining
- [ ] Ground truth extracted (`065_ground_truth.yaml`)
- [ ] Hook-based opening (not generic)
- [ ] Conclusion callbacks to Introduction hook
- [ ] Abstract generated LAST with actual numbers

### Should Pass (IMPORTANT)
- [ ] Citation verification rate >= 90%
- [ ] Word counts within guidelines
- [ ] Tables properly formatted
- [ ] Equations numbered and referenced
- [ ] At least 8 citations
- [ ] No grammatical errors (major)

### Nice to Have
- [ ] Appendix with supplementary material
- [ ] Code availability statement
- [ ] Data availability statement
- [ ] Acknowledgements section

---

## UNATTENDED Mode Handling

- [ ] UNATTENDED mode checked throughout workflow
- [ ] Auto-proceed through all steps
- [ ] Error handling continues workflow when possible
- [ ] Citation verification failures logged (not blocking)

---

## Post-Generation Actions

### Immediate Review
- [ ] Read abstract for clarity and actual numbers
- [ ] Verify contributions match results
- [ ] Check narrative coherence (hook → callback)
- [ ] Verify ground truth matches paper claims

### Manual Review Needed
- [ ] Technical accuracy of methodology
- [ ] Correctness of equations
- [ ] Validity of claims
- [ ] Appropriateness of conclusions

### Next Phase
- [ ] Phase 6.5 (Adversarial Review) will review and improve the paper
- [ ] Phase 6.5.1 (Overleaf) will generate LaTeX/PDF after review

---

## Critical Failures (Immediate Fix Required)

- [ ] Narrative Blueprint not generated (Step 2 skipped)
- [ ] Abstract generated before results
- [ ] Generic "X is important" opening used
- [ ] Required input artifacts missing
- [ ] Broader Impact Statement missing (ICML requirement)
- [ ] Ground truth not extracted (Step 7)
- [ ] Placeholder text remaining in final paper
- [ ] Step 7 not reading all sections
- [ ] Figure references broken
- [ ] verification_state.yaml not updated
- [ ] Conclusion does not callback to Introduction hook

---

## Validation Summary

**Total Checks:** 150+
**Required:** Step execution + Story Group context + Narrative quality + ICML compliance + Output verification
**MANDATORY Steps:** Steps 1-7

**Minimum Pass Criteria:**
- All steps (1-7) completed
- Narrative Blueprint generated (Step 2)
- All 8 sections generated via Story Groups
- Abstract generated LAST with actual numbers
- ICML 2025 format compliance passed
- Broader Impact Statement present
- Citation verification rate >= 90%
- Ground truth extracted for Phase 6.5
- verification_state.yaml updated

---

**Validation Result:**
- ✅ PASS: All sections complete, narrative coherent, ICML compliant, ready for adversarial review
- ⚠️ PASS WITH WARNINGS: Minor issues (citations, word counts)
- ❌ FAIL: Critical failures detected

**Completed By:** _______________
**Date:** _______________
**Hypothesis ID:** _______________
**Total Word Count:** _______________

**Reviewer:** _____________
**Date:** {{date}}
**Validator:** Phase 6 Paper Writing Workflow (YouRA Story Group Architecture)
