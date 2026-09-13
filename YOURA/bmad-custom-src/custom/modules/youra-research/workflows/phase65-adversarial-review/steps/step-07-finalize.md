---
name: 'step-07-finalize'
description: 'Generate final paper, review summary, and update all artifacts after review convergence'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase65-adversarial-review'

# File References
thisStepFile: '{workflow_path}/steps/step-07-finalize.md'
nextStepFile: null # END - Final step in Phase 6.5, proceeds to Phase 6.5.1
workflowFile: '{workflow_path}/workflow.md'
---

# Step 7: Finalize Adversarial Review

> **Execution Mode**: Main Session
> **Purpose**: Generate final paper, review summary, and human_review_notes

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and File Reading Protocol.

---

## Prerequisites

This step executes when:
- Convergence criteria met, OR
- Max rounds reached (3), OR
- User override to finalize

---

## PART A: Finalize Review Artifacts

### 7.1 Determine Final Paper Version

```yaml
action: "Identify latest paper version"
logic:
  if rounds_completed includes "R3":
    final_source: "{paper_folder}/06_paper_r3.md"
  elif rounds_completed includes "R2":
    final_source: "{paper_folder}/06_paper_r2.md"
  elif rounds_completed includes "R1":
    final_source: "{paper_folder}/06_paper_r1.md"
  else:
    final_source: "{paper_folder}/06_paper.md" # No changes made
```

### 7.2 Create Final Paper

```yaml
action: "Copy final version to 06_paper_final.md"
source: "{final_source}"
destination: "{paper_folder}/06_paper_final.md"

# Add review metadata to frontmatter
append_metadata:
  adversarial_review:

    completed_at: "{ISO8601}"
    rounds_completed: "{rounds_list}"
    total_issues_found: "{sum of all issues}"
    issues_resolved: "{sum of resolved}"
    final_status: "{CONVERGED / ACCEPTED_WITH_ISSUES}"
    persuasiveness_passed: "{true/false}"
```

### 7.3 Consolidate Human Review Notes

**CRITICAL:** Collect ALL MINOR issues into single file for human review (NOT auto-fixed).

Create/Update `065_human_review_notes.md`:

```markdown
# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review for human review.

**Date**: {ISO8601}
**Rounds Completed**: {N}

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | {N} |
| Grammar | {N} |
| Style | {N} |
| Clarity | {N} |
| Formatting | {N} |

---

## Round 1 Issues

### Typos
1. Section {X}, Line {Y}: "{original}" → suggested: "{correction}"
2. ...

### Grammar
1. Section {X}: "{issue description}"
2. ...

### Style
1. Section {X}: "{awkward phrasing or wordiness issue}"
2. ...

### Clarity
1. Section {X}: "{ambiguous sentence or unclear reference}"
2. ...

### Formatting
1. Section {X}: "{inconsistent formatting issue}"
2. ...

---

## Round 2 Issues

{Same structure as Round 1}

---

## Round 3 Issues (if applicable)

{Same structure}

---

## Recommended Priority

1. **Fix First**: Typos in Abstract, Introduction, Conclusion (high visibility)
2. **Fix Second**: Grammar issues affecting readability
3. **Consider**: Style improvements (subjective)
4. **Optional**: Minor formatting tweaks

---

*Note: These issues do not block paper acceptance but improve overall quality.*
```

### 7.4 Generate Review Summary

Create `065_review_summary.md`:

```markdown
# Adversarial Review Summary

**Paper**: {paper_title}
**Review Completed**: {ISO8601}
**Rounds Completed**: {N}
**Final Status**: {CONVERGED / ACCEPTED_WITH_ISSUES}
**Persuasiveness Check**: {PASSED / FAILED}

---

## Executive Summary

This paper underwent {N} rounds of adversarial review with three-persona analysis
(accuracy_checker, bored_reviewer, skeptical_expert).

| Severity | Found | Resolved | Remaining |
|----------|-------|----------|-----------|
| FATAL | {N} | {N} | 0 |
| MAJOR | {N} | {N} | 0 |

**MINOR Issues**: Collected in `065_human_review_notes.md` (NOT auto-fixed)

---

## Persuasiveness Assessment

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | {PASS/FAIL} | {notes} |
| Problem clear by paragraph 2? | {PASS/FAIL} | {notes} |
| Novelty clear by page 1? | {PASS/FAIL} | {notes} |
| Figure 1 self-explanatory? | {PASS/FAIL} | {notes} |
| Hook avoids "X is important"? | {PASS/FAIL} | {notes} |

---

## Round-by-Round Summary

### Round 1: Three-Persona Review

**Accuracy Checker Findings**:
| Category | Issues Found |
|----------|--------------|
| Claim-Evidence Mismatch | {N} |
| Numerical Inconsistency | {N} |
| Baseline Comparison Fairness | {N} |

**Bored Reviewer Findings**:
| Category | Issues Found |
|----------|--------------|
| Hook Quality | {N} |
| Clarity Issues | {N} |
| Engagement Problems | {N} |

**Skeptical Expert Findings**:
| Category | Issues Found |
|----------|--------------|
| Novelty Questions | {N} |
| Methodology Concerns | {N} |
| Missing Limitations | {N} |

**Key Issues Addressed**:
1. {FATAL-001 description and resolution}
2. {MAJOR-001 description and resolution}

### Round 2 (if applicable)

{Same structure}

### Round 3 (if applicable)

{Same structure}

---

## Sections Modified

| Section | Modifications |
|---------|---------------|
| Abstract | {brief description} |
| Introduction | {brief description} |
| Related Work | {brief description} |
| Methodology | {brief description} |
| Experiments | {brief description} |
| Results | {brief description} |
| Discussion | {brief description} |
| Conclusion | {brief description} |

---

## Quality Improvements

- **Logical Consistency**: {improved/unchanged}
- **Numerical Accuracy**: {improved/unchanged}
- **Novelty Claims**: {refined/unchanged}
- **Baseline Comparison**: {contextualized/unchanged}
- **Persuasiveness**: {improved/unchanged}
- **Hook Quality**: {improved/unchanged}

---

## Reviewer Preparation Notes

Potential remaining attack surfaces for real reviewers:

1. {Acknowledged limitation 1}
2. {Acknowledged limitation 2}

Suggested responses if these are raised:
- {Prepared response 1}
- {Prepared response 2}
```

### 7.5 Finalize Changelog

Ensure `065_changelog.md` has complete record:

```yaml
action: "Finalize changelog"
append:
  ---
  ## Final Summary

  **Total Revisions Made**: {count}
  **Sections Modified**: {list}
  **Word Count Change**: {original} → {final} ({delta})

  **Review Process**:
  - Started: {start_time}
  - Completed: {end_time}
  - Rounds: {N}
  - Personas Used: accuracy_checker, bored_reviewer, skeptical_expert

  **Files Generated**:
  - 06_paper_final.md (final paper)
  - 065_review_summary.md (review summary)
  - 065_human_review_notes.md (MINOR issues for human review)
  - 065_changelog.md (this file)

  **Next Phase**: Phase 6.5.1 (Overleaf LaTeX/PDF generation)
```

---

## PART B: Final Updates

**NOTE:** Overleaf LaTeX generation has been moved to Phase 6.5.1 for:
- Clear separation of concerns (Review vs. Format)
- Improved figure auto-insertion logic in Phase 6.5.1
- Future extensibility (arxiv, NeurIPS formats)

Phase 6.5.1 will automatically execute after this step completes.

---

## PART B: Final Updates

### 7.15 Verification Checklist

#### 7.15.1 Review Artifacts Check

- [ ] `06_paper_final.md` created with review metadata
- [ ] `065_review_summary.md` created with all rounds
- [ ] `065_human_review_notes.md` created with MINOR issues
- [ ] `065_changelog.md` finalized

### 7.16 Update Checkpoint (COMPLETED)

Update `065_review_checkpoint.yaml`:

```yaml
current_step: 7
step_7_status: "COMPLETED"
step_7_completed_at: "{ISO8601}"
workflow_status: "COMPLETED"

# Review artifacts
final_paper: "{paper_folder}/06_paper_final.md"
review_summary: "{review_folder}/065_review_summary.md"
human_review_notes: "{review_folder}/065_human_review_notes.md"
changelog: "{review_folder}/065_changelog.md"

### 7.17 Update Verification State (COMPLETED)

Update `verification_state.yaml`:

```yaml
paper_review:
  status: "COMPLETED"
  completed_at: "{ISO8601}"
  final_paper: "paper/06_paper_final.md"
  rounds_completed: {N}
  issues_found: {total}
  issues_resolved: {resolved}
  persuasiveness_passed: {true/false}
  human_review_notes: "paper/review/065_human_review_notes.md"
```

---

## Output Artifacts (Complete List)

| Artifact | Path | Description |
|----------|------|-------------|
| Final Paper | `{paper_folder}/06_paper_final.md` | Reviewed and revised paper |
| Review Summary | `{review_folder}/065_review_summary.md` | Consolidated review report |
| Human Review Notes | `{review_folder}/065_human_review_notes.md` | MINOR issues for human review |
| Changelog | `{review_folder}/065_changelog.md` | Complete change history |
| Checkpoint | `{review_folder}/065_review_checkpoint.yaml` | Final state |

---

## Final Completion Message

```
╔══════════════════════════════════════════════════════════════════════════╗
║ PHASE 6.5: ADVERSARIAL REVIEW COMPLETE ║
╠══════════════════════════════════════════════════════════════════════════╣
║ ║
║ 📄 Outputs: ║
║ Final Paper: paper/06_paper_final.md ║
║ Review Summary: paper/review/065_review_summary.md ║
║ Human Review Notes: paper/review/065_human_review_notes.md ║
║ Changelog: paper/review/065_changelog.md ║
║ ║
║ ────────────────────────────────────────────────────────────────────────║
║ Review Summary: ║
║ Rounds Completed: {N} ║
║ Issues Found: {total} ║
║ Issues Resolved: {resolved} ║
║ Persuasiveness: {PASSED / FAILED} ║
║ Final Status: {CONVERGED / ACCEPTED_WITH_ISSUES} ║
║ ║
║ ────────────────────────────────────────────────────────────────────────║
║ Review Features: ║
║ ✓ Three-persona adversarial review completed ║
║ - Accuracy Checker: claim verification ║
║ - Bored Reviewer: persuasiveness check ║
║ - Skeptical Expert: novelty/limitations ║
║ ✓ All FATAL and MAJOR issues resolved ║
║ ✓ MINOR issues collected in human_review_notes.md ║
║ ✓ ICML 2025 format compliance verified ║
║ ║
║ ────────────────────────────────────────────────────────────────────────║
║ ➡️ NEXT PHASE: Phase 6.5.1 (Overleaf LaTeX/PDF generation) ║
║ ║
║ Output Location: {research_folder}/paper/ ║
║ ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

## END

**Phase 6.5: Adversarial Review workflow COMPLETE.**

### All Outputs Generated:
1. **Final Paper** (`06_paper_final.md`) - Reviewed and revised
2. **Review Summary** (`065_review_summary.md`) - All issues and resolutions
3. **Human Review Notes** (`065_human_review_notes.md`) - MINOR issues for human review
4. **Changelog** (`065_changelog.md`) - Detailed change history

### Next Phase:
Phase 6.5.1 (Overleaf LaTeX/PDF generation) will execute automatically.

---

## SUCCESS/FAILURE METRICS

### SUCCESS:

- Final paper created with review metadata
- Review summary generated with all rounds
- Human review notes consolidated
- Changelog finalized
- Checkpoint updated to COMPLETED
- verification_state.yaml updated

### SYSTEM FAILURE:

- Skipping finalization steps
- Auto-fixing MINOR issues instead of collecting them
- Not updating checkpoint to COMPLETED
- Not updating verification_state.yaml
- Missing review artifacts (summary, changelog, human_review_notes)

**Master Rule:** This step finalizes the review only. Overleaf LaTeX/PDF generation is handled by Phase 6.5.1.
