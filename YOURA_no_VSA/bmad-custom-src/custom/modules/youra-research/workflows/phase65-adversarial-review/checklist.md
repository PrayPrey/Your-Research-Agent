# Phase 6.5: Adversarial Review - Validation Checklist

## Step Execution Tracking

### Step 1: Initialize
- [ ] **Configuration loaded:**
  - [ ] Module paths resolved
  - [ ] review_folder created (`{paper_folder}/review/`)
- [ ] **Required files validated:**
  - [ ] `06_paper.md` exists (FATAL if missing)
  - [ ] `065_ground_truth.yaml` exists (FATAL if missing)
  - [ ] `verification_state.yaml` exists (FATAL if missing)
- [ ] **Recommended files validated:**
  - [ ] `06_narrative_blueprint.yaml` exists (WARNING if missing)
  - [ ] `sections/` folder exists (WARNING if missing)
  - [ ] `06_references.bib` exists (WARNING if missing)
- [ ] **Ground truth loaded from `065_ground_truth.yaml`:**
  - [ ] Performance metrics loaded
  - [ ] Baseline performances loaded
  - [ ] Detection metrics loaded (if applicable)
  - [ ] Methodology facts loaded
  - [ ] Dataset facts loaded
- [ ] **Narrative blueprint loaded (for persuasiveness checks):**
  - [ ] Hook strategy loaded
  - [ ] Key insight loaded
  - [ ] Section goals loaded
- [ ] **Paper claims extracted:**
  - [ ] Performance claims
  - [ ] Detection claims
  - [ ] Methodology claims
  - [ ] Baseline claims
- [ ] **Pre-computed discrepancies calculated**
- [ ] **Checkpoint initialized (`065_review_checkpoint.yaml`):**
  - [ ] Input validation status
  - [ ] Ground truth file reference
  - [ ] Narrative blueprint reference
  - [ ] Pre-computed discrepancies count
  - [ ] Execution mode set (UNATTENDED/INTERACTIVE)

### Step 2: Adversary Round 1 (Accuracy and Engagement)
- [ ] **Task Agent invoked with THREE PERSONAS:**
  - [ ] adversary-agent-v2.md loaded
  - [ ] Paper file provided
  - [ ] Ground truth file provided
  - [ ] Narrative blueprint provided
  - [ ] Sections folder provided
- [ ] **Persona 1 - Accuracy Checker findings:**
  - [ ] Logical conflicts identified
  - [ ] Numerical accuracy verified against ground truth
  - [ ] Methodology consistency checked
  - [ ] Baseline comparison fairness assessed
- [ ] **Persona 2 - Bored Reviewer findings:**
  - [ ] Abstract compelling? (would continue reading?)
  - [ ] Problem clear in 1 minute?
  - [ ] Novelty clear in 2 minutes?
  - [ ] Figure 1 self-explanatory?
  - [ ] Attention loss points identified
- [ ] **Persona 3 - Skeptical Expert findings:**
  - [ ] Novelty overclaims identified
  - [ ] Baseline fairness assessed
  - [ ] Missing limitations flagged
  - [ ] Overclaims detected
- [ ] **Issues categorized by severity:**
  - [ ] FATAL issues flagged (blocks convergence)
  - [ ] MAJOR issues flagged (blocks convergence)
  - [ ] MINOR issues → collected for human_review_notes (NOT auto-fixed)
- [ ] **Review document created (`065_review_r1.md`):**
  - [ ] Issue ID format: `{SEVERITY}-{NUMBER}`
  - [ ] Each issue has location, description, impact, evidence
  - [ ] Persuasiveness checks recorded
- [ ] **Checkpoint updated:**
  - [ ] issues_by_round.R1 populated (by persona)
  - [ ] persuasiveness_checks.R1 populated
  - [ ] current_round = 1

### Step 3: Revision Round 1
- [ ] **Review document loaded**
- [ ] **Paper loaded for revision**
- [ ] **FOR EACH issue (FATAL first, then MAJOR):**
  - [ ] Fix implemented in paper
  - [ ] Change logged in changelog
  - [ ] Issue marked as addressed
- [ ] **MINOR issues collected in `065_human_review_notes.md` (NOT auto-fixed)**
- [ ] **Revised paper saved (`06_paper_r1.md`)**
- [ ] **Changelog created/updated (`065_changelog.md`)**
- [ ] **Checkpoint updated:**
  - [ ] issues_resolved.R1 count
  - [ ] latest_paper_version updated
  - [ ] human_review_notes_count updated

### Step 4: Convergence Check (After R1)
- [ ] **State loaded:**
  - [ ] Checkpoint read
  - [ ] Latest review read
- [ ] **Remaining issues calculated:**
  - [ ] remaining_fatal = found - resolved
  - [ ] remaining_major = found - resolved
- [ ] **Convergence evaluated:**
  - [ ] CONVERGE if: FATAL=0 AND MAJOR=0 AND persuasiveness_passed AND round>=2
  - [ ] CONTINUE if: conditions not met AND round<max_rounds
  - [ ] STOP if: round>=max_rounds AND FATAL>0
- [ ] **Repeated issues checked (same issue found twice = needs human)**
- [ ] **Checkpoint updated with decision**
- [ ] **Routing determined:**
  - [ ] If CONVERGE → Step 7 (Finalize)
  - [ ] If CONTINUE → Step 5 (R2)
  - [ ] If STOP → Manual intervention

### Step 5: Adversary Round 2 (Verification and Credibility)
- [ ] **Task Agent invoked with TWO PERSONAS:**
  - [ ] adversary-agent-v2.md loaded
  - [ ] Latest paper version provided
  - [ ] Ground truth file provided (CRITICAL)
  - [ ] Phase 4/5 files provided for cross-check
- [ ] **Persona 1 - Accuracy Checker findings:**
  - [ ] Mathematical validity errors
  - [ ] Ground truth discrepancies
  - [ ] Metric consistency errors
- [ ] **Persona 3 - Skeptical Expert findings:**
  - [ ] Baseline fairness issues
  - [ ] Signal-performance gap problems
  - [ ] Missing limitations
- [ ] **Serena MCP used for numerical verification**
- [ ] **Issues categorized by severity**
- [ ] **Review document created (`065_review_r2.md`)**
- [ ] **Checkpoint updated:**
  - [ ] issues_by_round.R2 populated (by persona)
  - [ ] current_round = 2

### Step 6: Revision Round 2
- [ ] **R2 review document loaded**
- [ ] **Latest paper version loaded**
- [ ] **FOR EACH issue (FATAL first, then MAJOR):**
  - [ ] Fix implemented
  - [ ] Change logged
  - [ ] Issue marked as addressed
- [ ] **MINOR issues appended to `065_human_review_notes.md`**
- [ ] **Revised paper saved (`06_paper_r2.md`)**
- [ ] **Changelog updated**
- [ ] **Checkpoint updated:**
  - [ ] issues_resolved.R2 count
  - [ ] latest_paper_version updated

### Step 4 (Repeat): Convergence Check (After R2)
- [ ] Same convergence logic as Step 4
- [ ] **Routing determined:**
  - [ ] If CONVERGE → Step 7 (Finalize)
  - [ ] If CONTINUE → R3 (Bored Reviewer only)
  - [ ] If STOP → Manual intervention

### Step 7: Finalize
- [ ] **Final paper version determined:**
  - [ ] Latest revised version identified
  - [ ] `06_paper_final.md` created with review metadata
- [ ] **Human review notes consolidated from all rounds**
- [ ] **Review summary generated (`065_review_summary.md`):**
  - [ ] Executive summary
  - [ ] Persuasiveness assessment
  - [ ] Round-by-round summary (by persona)
  - [ ] Remaining concerns
  - [ ] Sections modified
  - [ ] Quality improvements
  - [ ] Reviewer preparation notes
- [ ] **Changelog finalized**
- [ ] **Checkpoint updated:**
  - [ ] step_7_status = "COMPLETED"
  - [ ] workflow_status = "COMPLETED"
- [ ] **verification_state.yaml updated:**
  - [ ] paper_review.status = "COMPLETED"
  - [ ] paper_review.completed_at set
  - [ ] paper_review.final_paper path set
  - [ ] paper_review.rounds_completed count
  - [ ] paper_review.issues_found total
  - [ ] paper_review.issues_resolved count
  - [ ] paper_review.persuasiveness_passed set
  - [ ] paper_review.human_review_notes path set

**NOTE:** Overleaf LaTeX/PDF generation handled by Phase 6.5.1

---

## Pre-Execution Checks

### Required Inputs
- [ ] Phase 6 completed successfully
- [ ] `06_paper.md` exists in paper folder
- [ ] `065_ground_truth.yaml` exists in paper folder
- [ ] `verification_state.yaml` exists with Phase 4/5 results

### Recommended Inputs
- [ ] `06_narrative_blueprint.yaml` exists (for persuasiveness checks)
- [ ] `sections/` folder exists (for cross-reference)
- [ ] `06_references.bib` exists (for citation verification)

### Environment
- [ ] Serena MCP server available (file discovery, numerical verification)
- [ ] Write access to paper/review folder

---

## Ground Truth Verification Quality

### From `065_ground_truth.yaml` (Phase 6 Step 7)
- [ ] Performance metrics loaded
- [ ] Baseline performances listed
- [ ] Detection metrics listed (if applicable)
- [ ] Methodology facts listed
- [ ] Dataset facts listed

### Cross-Check Against Phase 4/5
- [ ] At least one Phase 4 validation file verified
- [ ] Actual performance numbers cross-referenced
- [ ] Baseline comparison data verified (if Phase 5 available)

---

## Three-Persona Role Separation

### Purpose
- Each persona attacks from a different angle
- Accuracy Checker verifies facts
- Bored Reviewer checks engagement
- Skeptical Expert looks for holes

### Implementation
- [ ] Adversary steps use adversary-agent-v2.md with multi-persona
- [ ] Revision steps use revision-agent.md with author perspective
- [ ] Roles never mixed in same context
- [ ] Ground truth shared but perspectives differ

---

## Issue Severity Classification

### Severity Definitions
| Severity | Definition | Action | Blocks Convergence? |
|----------|------------|--------|---------------------|
| FATAL | Fundamental contradiction or impossible claim | MUST fix or WITHDRAW | **YES** |
| MAJOR | Significant weakness attackable by reviewers | MUST fix with evidence | **YES** |

### MINOR → human_review_notes
- [ ] MINOR issues are NOT auto-fixed
- [ ] MINOR issues collected in `065_human_review_notes.md`
- [ ] Categories: typo, grammar, style, clarity, formatting
- [ ] Left for human review after workflow completes

### Issue Categories by Round
- [ ] Round 1: Accuracy + Engagement
  - [ ] Logical conflicts
  - [ ] Methodology contradictions
  - [ ] Novelty overclaims
  - [ ] Definition inconsistencies
  - [ ] Attention loss points
  - [ ] Unclear problem statement
- [ ] Round 2: Verification + Credibility
  - [ ] Mathematical validity
  - [ ] Baseline fairness
  - [ ] Signal-performance gap
  - [ ] Metric consistency
  - [ ] Missing limitations

---

## Convergence Criteria

### Automatic Convergence
```
CONVERGE if:
  - fatal_issues_remaining == 0
  - major_issues_remaining == 0
  - persuasiveness_passed == true
  - current_round >= 2 # Minimum 2 rounds
```

### Continue to Next Round
```
CONTINUE if:
  - fatal_issues_remaining > 0 OR major_issues_remaining > 0 OR NOT persuasiveness_passed
  - current_round < max_rounds
```

### Force Stop
```
STOP if:
  - current_round >= max_rounds AND fatal_issues_remaining > 0
  - same_issue_repeated >= 2
```

---

## Persuasiveness Checks

- [ ] Abstract compelling? (would continue reading?)
- [ ] Problem clear in 1 minute?
- [ ] Novelty clear in 2 minutes?
- [ ] Figure 1 self-explanatory?
- [ ] Hook avoids "X is important"?
- [ ] Would continue reading? (attention not lost)
- [ ] No false novelty claims?
- [ ] Baselines fairly compared?
- [ ] No overclaims?
- [ ] Limitations present?

---

## MCP Server Usage

### Serena MCP (Numerical Verification)
- [ ] `mcp__serena__find_file` for Phase 4/5 result files
- [ ] `mcp__serena__search_for_pattern` for actual metric values
- [ ] `mcp__serena__list_dir` for result file discovery
- [ ] `mcp__serena__find_symbol` for code verification
- [ ] Used in Step 1 (discovery), Step 5 (MANDATORY numerical verification)

### Semantic Scholar MCP (Citation Verification)
- [ ] Verify baseline numbers against original papers
- [ ] Check citation accuracy
- [ ] Used in Step 2/5 (optional)

---

## MCP ERROR RETRY PROTOCOL Compliance

- [ ] All MCP errors trigger retry
- [ ] 15-second delay between retry attempts
- [ ] Maximum 3 retry attempts per call
- [ ] Only skip/fail after 3 consecutive failures

---

## UNATTENDED Mode Handling

- [ ] UNATTENDED mode checked at convergence points
- [ ] Auto-proceed with recommended action
- [ ] Issues logged but not blocking workflow
- [ ] Manual intervention only if STOP condition
- [ ] MINOR issues collected, not auto-fixed

---

## Output Verification

### Required Outputs

| Output | Location | Verified |
|--------|----------|----------|
| `06_paper_final.md` | `{paper_folder}/` | [ ] |
| `065_ground_truth.yaml` | `{paper_folder}/` | [ ] |
| `065_review_checkpoint.yaml` | `{paper_folder}/review/` | [ ] |
| `065_review_r1.md` | `{paper_folder}/review/` | [ ] |
| `065_review_r2.md` | `{paper_folder}/review/` | [ ] |
| `065_changelog.md` | `{paper_folder}/review/` | [ ] |
| `065_review_summary.md` | `{paper_folder}/review/` | [ ] |
| `065_human_review_notes.md` | `{paper_folder}/review/` | [ ] |
| `06_paper_r1.md` | `{paper_folder}/` | [ ] |
| `06_paper_r2.md` | `{paper_folder}/` | [ ] |

**NOTE:** Overleaf LaTeX project is generated by Phase 6.5.1 (next phase)

### verification_state.yaml Updates
- [ ] `paper_review.status: "COMPLETED"`
- [ ] `paper_review.completed_at` set
- [ ] `paper_review.final_paper` path set
- [ ] `paper_review.rounds_completed` count
- [ ] `paper_review.issues_found` total
- [ ] `paper_review.issues_resolved` count
- [ ] `paper_review.persuasiveness_passed` set
- [ ] `paper_review.human_review_notes` path set

---

## Review Quality

### Adversary Round Quality
- [ ] Three personas applied per round configuration
- [ ] Adversary identifies real issues (not superficial)
- [ ] Issues traceable to specific paper locations
- [ ] Evidence provided for each issue
- [ ] Ground truth comparisons included (accuracy checker)
- [ ] Persuasiveness checks included (bored reviewer)
- [ ] Novelty/claim assessment included (skeptical expert)

### Revision Round Quality
- [ ] All FATAL issues addressed
- [ ] All MAJOR issues addressed
- [ ] MINOR issues collected (NOT auto-fixed)
- [ ] Changes maintain paper coherence
- [ ] Changes logged in changelog

### Final Paper Quality
- [ ] No FATAL issues remaining
- [ ] No MAJOR issues remaining
- [ ] Persuasiveness passed
- [ ] Paper improved from original
- [ ] Review summary accurate

---

## Round Limits

| Action | Max Value |
|--------|-----------|
| Total rounds | 3 |
| Same issue repetitions | 2 |
| FATAL issues acceptable at finish | 0 |
| MAJOR issues acceptable at finish | 0 |

---

## Critical Failures (Immediate Fix Required)

- [ ] Ground truth not loaded from `065_ground_truth.yaml`
- [ ] Narrative blueprint not loaded for persuasiveness checks
- [ ] Three-persona review not applied
- [ ] Role separation violated (adversary and reviser in same context)
- [ ] MINOR issues auto-fixed instead of collected
- [ ] Persuasiveness checks skipped
- [ ] FATAL issues remaining after max rounds
- [ ] Ground truth discrepancies ignored
- [ ] Convergence check skipped
- [ ] Final paper not generated
- [ ] verification_state.yaml not updated

---

## Validation Summary

**Total Checks:** 120+
**Required:** Step execution + Ground truth + Three-persona review + Persuasiveness checks + Convergence
**MANDATORY Steps:** Steps 1, 2, 3, 4, 7 | Steps 5, 6 CONDITIONAL (if R2 needed)
**NOTE:** Overleaf LaTeX/PDF generation is Phase 6.5.1 (separate workflow)

**Minimum Pass Criteria:**
- Ground truth loaded from `065_ground_truth.yaml`
- Three-persona review applied
- At least R1 completed (adversary + revision)
- Convergence check executed with persuasiveness
- MINOR issues collected in human_review_notes (not auto-fixed)
- Final paper generated
- No FATAL issues remaining
- No MAJOR issues remaining
- verification_state.yaml updated

---

**Validation Result:**
- ✅ CONVERGED: All critical issues resolved, persuasiveness passed, ready for Phase 6.5.1
- ⚠️ ACCEPTED_WITH_ISSUES: Minor issues remain in human_review_notes
- ❌ MANUAL_REQUIRED: Critical issues unresolved, human intervention needed

**Rounds Completed:** ___
**Issues Found:** ___
**Issues Resolved:** ___
**Persuasiveness Passed:** ___
**Final Status:** _______________

**Reviewer:** _____________
**Date:** {{date}}
**Validator:** Phase 6.5 Adversarial Review Workflow (YouRA Three-Persona)
