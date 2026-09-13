---
name: 'step-07-finalize'
description: 'Merge all sections with full context, coherence check, ground truth extraction'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase6-paper-writing'

# File References
thisStepFile: '{workflow_path}/steps/step-07-finalize.md'
workflowFile: '{workflow_path}/workflow.md'
narrativeBlueprint: '{paper_folder}/06_narrative_blueprint.yaml'
---

# Step 07: Final Merge & Ground Truth Extraction

> **Step Position:** Step 6 (References) -> **[Step 7: Final Merge]** -> Phase 6.5 (Adversarial Review)
> **Purpose:** Merge all sections with FULL CONTEXT, coherence check, extract ground truth for Phase 6.5
> **Context Isolation:** NO - This step REQUIRES reading ALL section files
> **Final Output:** `06_paper.md`, `065_ground_truth.yaml`

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules and Role Reinforcement.

### 📖 File Reading Protocol (CRITICAL):

Complete execution of this step file **requires reading the entire file at once**.

---

## FULL CONTEXT REQUIRED

This step is the **ONLY step that reads all sections together**.

**Rationale:**
- Steps 3-5 generated sections in story groups (narrative coherence within groups)
- This step merges with full awareness of all content
- Checks cross-section coherence and consistency
- Ensures proper figure placement and references
- Creates final unified paper
- Extracts ground truth values for Phase 6.5 adversarial review

---

## 1. Read All Section Files

Load ALL section files from `{sections_folder}/`:

```
sections/
├── 00_abstract.md → Read FULL content
├── 01_introduction.md → Read FULL content
├── 02_related_work.md → Read FULL content
├── 03_methodology.md → Read FULL content
├── 04_experiments.md → Read FULL content
├── 05_results.md → Read FULL content
├── 06_discussion.md → Read FULL content
└── 07_conclusion.md → Read FULL content
```

**Action:** Read each file completely and hold in context.

---

## 2. Load Supporting Files

### 2.1 Narrative Blueprint
```
File: {output_folder}/06_narrative_blueprint.yaml
Purpose: Verify paper follows designed narrative
```

### 2.2 References File
```
File: {output_folder}/06_references.bib
Purpose: Include full reference list
```

### 2.3 Figure Registry
```
File: {output_folder}/figure_registry.yaml
Purpose: Verify all figure references are valid
```

### 2.4 Checkpoint
```
File: {output_folder}/06_paper_checkpoint.yaml
Purpose: Verify all sections marked complete
```

---

## 3. Cross-Section Coherence Check

### 3.1 Narrative Blueprint Alignment

Verify paper follows the designed narrative from Step 02:

| Blueprint Element | Implementation | Aligned? |
|-------------------|----------------|----------|
| Hook strategy | Introduction opening | [ ] |
| Problem framing (3 levels) | Introduction | [ ] |
| Key insight | Throughout paper | [ ] |
| Evidence narrative | Results section | [ ] |
| Callback to hook | Conclusion | [ ] |

### 3.2 Terminology Consistency

Check that key terms are used consistently across sections:

| Term | Defined In | Used In | Consistent? |
|------|------------|---------|-------------|
| Method name | Introduction | All sections | [ ] |
| Dataset name | Experiments | Results | [ ] |
| Metric names | Experiments | Results, Abstract | [ ] |
| Baseline names | Experiments | Results | [ ] |

**Fix if inconsistent:** Update terminology in final merge.

### 3.3 Claim-Evidence Alignment

Verify claims in Abstract/Introduction are supported by Results:

| Claim (Abstract/Intro) | Evidence (Results) | Match? |
|------------------------|-------------------|--------|
| "[X%] improvement" | Table 1 shows X% | [ ] |
| "outperforms baselines" | Statistical significance | [ ] |
| "Contribution 1" | Section 5.x demonstrates | [ ] |

### 3.4 Figure References

Verify all figure references resolve:

```markdown
Check: Every "Figure {N}" in text has corresponding image
Check: Every figure in figures/ is referenced in text
Check: Figure numbers are sequential (1, 2, 3...)
```

---

## 4. Assemble Final Paper

### 4.1 Paper Structure

Create `{output_folder}/06_paper.md`:

```markdown
---
title: "{PAPER_TITLE}"
authors:
  - name: "{AUTHOR_NAME}"
    affiliation: "{INSTITUTION}"
    email: "{EMAIL}"
format: "ICML2025"
date: "{YYYY-MM-DD}"
hypothesis_id: "{HYPOTHESIS_ID}"
generated_by: "Anonymous Research Pipeline "
word_count: {TOTAL_WORDS}
figures: {FIGURE_COUNT}
tables: {TABLE_COUNT}
---

{00_abstract.md content}

---

{01_introduction.md content - renumbered as Section 1}

---

{02_related_work.md content - renumbered as Section 2}

---

{03_methodology.md content - renumbered as Section 3}

---

{04_experiments.md content - renumbered as Section 4}

---

{05_results.md content - renumbered as Section 5}

---

{06_discussion.md content - renumbered as Section 6}

---

{07_conclusion.md content - renumbered as Section 7}

---

## References

{06_references.bib content formatted as markdown}

---

## Appendix

{Any appendix content if applicable}
```

### 4.2 Section Number Mapping

Ensure consistent numbering:

| Section File | Paper Number | Title |
|--------------|--------------|-------|
| 00_abstract.md | (no number) | Abstract |
| 01_introduction.md | 1 | Introduction |
| 02_related_work.md | 2 | Related Work |
| 03_methodology.md | 3 | Methodology |
| 04_experiments.md | 4 | Experimental Setup |
| 05_results.md | 5 | Results |
| 06_discussion.md | 6 | Discussion |
| 07_conclusion.md | 7 | Conclusion |

---

## 5. Figure Integration Verification

Load `figure_registry.yaml` and verify for EACH figure:

| Fig # | Section | Integrated? | Reference Before? | Caption OK? |
|-------|---------|-------------|-------------------|-------------|
| {n} | {section} | [ ] | [ ] | [ ] |

### Verification Checklist

- [ ] All figures from registry appear in paper
- [ ] Figure numbers are sequential (1, 2, 3...)
- [ ] Each figure is referenced BEFORE it appears
- [ ] Each figure has descriptive caption
- [ ] No orphaned figures (unreferenced)

---

## 6. ICML 2025 Compliance Verification

### 6.1 Quick Compliance Check

**MUST PASS (Fatal if failed):**

| Requirement | Validated In | Final Check |
|-------------|--------------|-------------|
| Main paper ≤ 8 pages | Word count estimate | [ ] ~{X} pages |
| Abstract single paragraph | Step 5 | [ ] Verified |
| Impact Statement present | Discussion | [ ] Verified |
| All figures captioned | All steps | [ ] Verified |
| No 4+ level headings | All steps | [ ] Verified |

**Page Estimation:** `(total_words / 350) + (figures * 0.3) + (tables * 0.2)`

### 6.2 Final Cleanup

Before marking complete:

- [ ] Remove `[TO BE FILLED]` placeholders
- [ ] Remove `[CITE:...]` unresolved markers
- [ ] Remove section metadata YAML headers
- [ ] Remove TODO comments
- [ ] Verify no broken figure/table references
- [ ] Check grammatical consistency (British/American English)

---

## 7. Extract Ground Truth for Phase 6.5

**CRITICAL:** Extract actual values for adversarial review verification.

### 7.1 Create Ground Truth File

Create `{output_folder}/065_ground_truth.yaml`:

```yaml
# Ground Truth for Phase 6.5 Adversarial Review
# Extracted from Phase 0-5 artifacts and validated paper
# Used by Adversary Agent to verify paper accuracy

version: "1.0"
extracted_at: "{ISO8601}"

# From Phase 4/5 validation reports
metrics:
  main_metric:
    name: "{metric_name}"
    our_value: {actual_value}
    baseline_value: {actual_baseline_value}
    improvement: "{actual_improvement}%"

  secondary_metrics:
    - name: "{metric_name}"
      value: {actual_value}

# From Phase 2C/3
methodology:
  algorithm_name: "{actual_name}"
  key_hyperparameters:
    - name: "{param}"
      value: "{actual_value}"

  training_details:
    epochs: {actual}
    batch_size: {actual}
    learning_rate: {actual}

# From Phase 4 validation
results:
  main_result:
    claimed: "{what paper claims}"
    actual: "{what Phase 4 shows}"
    match: true/false

  ablation_results:
    - experiment: "{name}"
      result: "{actual_result}"

# From Phase 5 baseline comparison
baseline_comparison:
  baselines_used:
    - name: "{baseline_name}"
      our_reported: {value}
      literature_reported: "{value if known}"

  statistical_significance:
    method: "{t-test, etc.}"
    p_value: {actual}
    significant: true/false

# Key claims in paper
claims:
  - claim: "{claim from paper}"
    location: "{section}"
    supporting_evidence: "{what supports it}"
    verified: true/false

# Contribution verification
contributions:
  - contribution: "{contribution statement}"
    evidence_in_paper: "{section/figure/table}"
```

### 7.2 Ground Truth Extraction Sources

| Ground Truth Element | Source |
|---------------------|--------|
| Metric values | `04_validation.md`, `05_baseline_comparison.md` |
| Hyperparameters | `03_prd.md`, `03_architecture.md` |
| Baseline numbers | `05_baseline_comparison.md`, original papers |
| Statistical tests | `04_validation.md`, `05_baseline_comparison.md` |
| Implementation details | Serena MCP code analysis |

---

## 8. Generate Final Statistics

Add to end of paper (or separate file):

```yaml
# Paper Statistics
title: "{title}"
generated: "{ISO8601}"
pipeline_version: "YouRA "

word_counts:
  abstract: {count}
  introduction: {count}
  related_work: {count}
  methodology: {count}
  experiments: {count}
  results: {count}
  discussion: {count}
  conclusion: {count}
  total: {total}

estimated_pages: {count}

figures:
  total: {count}
  from_phase4: {count}
  from_phase5: {count}

tables:
  total: {count}

citations:
  total: {count}
  verified: {count}
  verification_rate: {percentage}%

narrative_coherence:
  follows_blueprint: true
  hook_implemented: true
  callback_present: true
```

---

## 9. Update verification_state.yaml

Update main verification state:

```yaml
paper_writing:
  status: "COMPLETED"
  completed_at: "{ISO8601}"
  outputs:
    paper_file: "{research_folder}/paper/06_paper.md"
    references_file: "{research_folder}/paper/06_references.bib"
    narrative_blueprint: "{research_folder}/paper/06_narrative_blueprint.yaml"
    ground_truth_file: "{research_folder}/paper/065_ground_truth.yaml"
    sections_folder: "{research_folder}/paper/sections/"
    figures_folder: "{research_folder}/paper/figures/"
  statistics:
    total_word_count: {count}
    estimated_pages: {count}
    figures: {count}
    tables: {count}
    citations_total: {count}
    citations_verified: {count}
```

---

## 10. Final Checkpoint Update

Update `06_paper_checkpoint.yaml`:

```yaml
version: "2.0"
created_at: "{original}"
updated_at: "{ISO8601}"

current_step: 7
total_steps: 7
status: "COMPLETED"

# Narrative design
narrative_design:
  status: "complete"
  blueprint_file: "06_narrative_blueprint.yaml"

# Story groups
story_groups:
  group_a:
    status: "complete"
    sections: ["introduction", "related_work", "methodology"]
  group_b:
    status: "complete"
    sections: ["experiments", "results", "discussion"]
  group_c:
    status: "complete"
    sections: ["conclusion", "abstract"]

# Final output
final_paper:
  file: "06_paper.md"
  word_count: {total}
  figures: {count}
  tables: {count}

# Ground truth for adversarial review
ground_truth:
  file: "065_ground_truth.yaml"
  extracted: true

# Coherence checks passed
coherence:
  follows_narrative_blueprint: true
  terminology_consistent: true
  claims_supported: true
  figures_valid: true
  cross_references_valid: true

completed_at: "{ISO8601}"
```

---

## 11. Phase 6 Completion Message

```
╔══════════════════════════════════════════════════════════════════════════╗
║ PHASE 6: PAPER WRITING COMPLETE ║
╠══════════════════════════════════════════════════════════════════════════╣
║ ║
║ 📄 Outputs Generated: ║
║ Paper: paper/06_paper.md ║
║ References: paper/06_references.bib ║
║ Narrative: paper/06_narrative_blueprint.yaml ║
║ Ground Truth: paper/065_ground_truth.yaml ║
║ Sections: paper/sections/ (8 files) ║
║ Figures: paper/figures/ ({N} figures) ║
║ ║
║ ────────────────────────────────────────────────────────────────────────║
║ Word Count Summary: ║
║ Abstract: {X} words ║
║ Introduction: {X} words ║
║ Related Work: {X} words ║
║ Methodology: {X} words ║
║ Experiments: {X} words ║
║ Results: {X} words ║
║ Discussion: {X} words ║
║ Conclusion: {X} words ║
║ ──────────────────────────── ║
║ TOTAL: {X} words (~{Y} pages) ║
║ ║
║ ────────────────────────────────────────────────────────────────────────║
║ Quality Checks: ║
║ ✓ Narrative blueprint followed ║
║ ✓ Story groups generated with coherence ║
║ ✓ Cross-section coherence verified ║
║ ✓ Figure-content matching verified ║
║ ✓ Citations verified ({Z}%) ║
║ ✓ ICML 2025 format compliance passed ║
║ ✓ Ground truth extracted for Phase 6.5 ║
║ ║
║ ⏭️ NEXT: Phase 6.5 - Adversarial Review ║
║ (Overleaf LaTeX generation happens AFTER adversarial review) ║
║ ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

## 12. Proceed to Phase 6.5

**Phase 6 Complete. Proceed to Phase 6.5 - Adversarial Review.**

### Phase 6 Outputs Ready for Phase 6.5:
1. **Paper** (`06_paper.md`) - To be reviewed
2. **Ground Truth** (`065_ground_truth.yaml`) - For accuracy verification
3. **Narrative Blueprint** (`06_narrative_blueprint.yaml`) - For engagement verification
4. **Section Files** (`sections/`) - For targeted revisions

### Phase 6.5 Will:
1. Apply adversarial review (accuracy + persuasiveness)
2. Iterate revisions until convergence
3. Generate final Overleaf LaTeX project (after review complete)

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- All sections read and merged
- Narrative blueprint alignment verified
- Cross-section coherence checked
- Figure integration verified
- Ground truth extracted for Phase 6.5
- 06_paper.md created
- 065_ground_truth.yaml created
- verification_state.yaml updated

### ❌ SYSTEM FAILURE:

- Missing section files
- Coherence issues not detected/fixed
- Ground truth not extracted
- Missing final paper file
- Skipping narrative blueprint verification
- Not updating verification state

**Master Rule:** Phase 6 produces a complete paper PLUS ground truth for adversarial review. Overleaf generation happens in Phase 6.5.1 AFTER review.
