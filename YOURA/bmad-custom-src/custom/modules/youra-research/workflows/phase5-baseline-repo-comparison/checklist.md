# Phase 5: Baseline Comparison - Validation Checklist

## Step Execution Tracking

### Step 1: Initialize
- [ ] **Phase 4 Completion Verified:**
  - [ ] `04_validation.md` exists
  - [ ] `experiment_results.json` exists
  - [ ] `code/outputs/results.csv` exists
  - [ ] ALL sub-hypotheses have Phase 4 COMPLETED status
  - [ ] ALL MUST_WORK gates satisfied
- [ ] **Hypothesis Journey Documented:**
  - [ ] Version information extracted
  - [ ] Version history analyzed
  - [ ] Reflection analysis completed
  - [ ] Journey summary output displayed
- [ ] **Result Integrity Verification (Hallucination Detection):**
  - [ ] Basic existence checks passed
  - [ ] Synthetic/mock data detection passed
  - [ ] Execution evidence verified
  - [ ] File timestamp sanity check passed
- [ ] Required files verified (04_validation.md, results.csv)
- [ ] Phase 2A Refinement read (03_refinement.yaml)
- [ ] Workspace folder structure created
- [ ] Pipeline Project ID retrieved
- [ ] Checkpoint file initialized
- [ ] verification_state.yaml updated:
  - [ ] main_hypothesis.baseline_comparison.status = "IN_PROGRESS"
  - [ ] episode section updated
  - [ ] workflow.current_phase = "Phase 5"
  - [ ] History event logged

### Step 2: Define Comparison
- [ ] Comparison requirements documented
- [ ] Search queries generated (broad enough for 3+ candidates)
- [ ] Evaluation criteria defined
- [ ] Adaptation boundaries specified
- [ ] comparison_plan.md created

### Step 3: Search Repositories
- [ ] Exa search executed
- [ ] **At least 3 candidate repositories found** (need 1 + fallbacks)
- [ ] GitHub URLs validated
- [ ] Repository metadata fetched (stars, activity, language)
- [ ] repo_candidates.md created with ≥3 candidates

### Step 4: Evaluate Candidates (Multi-Baseline)
- [ ] **All candidates cloned** (shallow)
- [ ] Serena code analysis completed for each
- [ ] **Datasets extracted from each candidate** (general data loading patterns)
- [ ] Suitability scores calculated (50% weight)
- [ ] Quality scores calculated (30% weight)
- [ ] Adaptability scores calculated (20% weight)
- [ ] Candidates ranked by final score
- [ ] evaluation_matrix.md created with **all candidates**

### Step 5: Select Top 3 Repositories (Multi-Baseline)
- [ ] **Top 3 candidates selected** based on scores
- [ ] Repository accessibility verified for all 3
- [ ] Adaptation preview generated for each
- [ ] Effort estimate provided for each
- [ ] **Datasets merged** from all 3 baselines
- [ ] selected_baselines.md created (NOT selected_repo.md)
- [ ] Checkpoint updated with baselines array (3 items)

### Step 5.5: Baseline Environment Verification (Mode B)
- [ ] Primary dataset loaded from Phase 4
- [ ] Merged datasets loaded from Step 5
- [ ] **Secondary dataset different from primary**
- [ ] Secondary dataset used by ≥2 baselines (preferred)
- [ ] Model compatibility verified
- [ ] Loading code extracted from baseline
- [ ] dataset_selection.md created with rationale
- [ ] Checkpoint updated with dataset_selection

### Step 6: Setup & Analyze (Multi-Baseline)
- [ ] **All 3 repositories cloned** (full, not shallow)
- [ ] `youra-baseline` branch created for each
- [ ] **Conda environment created for each baseline**
- [ ] Dependencies installed for each
- [ ] **Deep code analysis with Serena for each baseline**
- [ ] Integration points identified for each
- [ ] Compatibility score calculated for each (≥30% to proceed)
- [ ] **Baseline environment verified** (dataset, model, config accessibility)
- [ ] setup_log.md created (includes all 3 baselines)
- [ ] code_analysis.md created (includes all 3 baselines with injection points)
- [ ] **05_tasks.yaml generated**

### Step 7: Adaptation Coding (Mode B)
- [ ] Cycle limit checked (coder_validator_cycles < 3)
- [ ] **Tasks loaded from 05_tasks.yaml**
- [ ] **Archon KB searched BEFORE each code generation (MANDATORY)**
- [ ] **FOR EACH baseline (4 tasks × baselines = 12 max):**
  - [ ] Algorithm Injection generated (replaces/wraps baseline's optimizer)
  - [ ] Metric Injection generated (metrics.py)
  - [ ] Results Saver generated (results_saver.py)
  - [ ] Training Script modifications documented:
    - [ ] **sys.path setup added FIRST** (STEP 0) for adaptations module import
    - [ ] Adapter imports added after sys.path setup
    - [ ] --method argument added (baseline vs ours)
  - [ ] Test files created for EACH component
  - [ ] CHANGES.md generated
- [ ] **Task status updated in 05_tasks.yaml:** pending → doing → review
- [ ] **Mode B Fair Comparison Principle followed:**
  - [ ] Baseline's model architecture UNCHANGED
  - [ ] Baseline's dataset loading UNCHANGED
  - [ ] Baseline's hyperparameters UNCHANGED
  - [ ] ONLY our algorithm/optimizer injected

### Step 8: Validation (Multi-Baseline)
- [ ] **Review tasks loaded from 05_tasks.yaml**
- [ ] **FOR EACH baseline:** Task tool invoked with subagent_type="baseline-validator-agent"
- [ ] **Test Gate executed FIRST** for each baseline (pytest in conda env)
- [ ] Static analysis completed for each (Serena MCP)
- [ ] Runtime validation completed for each (import + 1-epoch test)
- [ ] Error analysis completed for each
- [ ] Archon KB searched for error resolution
- [ ] **Passed tasks marked as 'done' in 05_tasks.yaml** per baseline
- [ ] **Failed tasks marked as 'pending' with error info in 05_tasks.yaml**
- [ ] coder_validator_cycles incremented (if any failed)
- [ ] validation_log.md generated (includes all baselines)
- [ ] Checkpoint updated with per-baseline validation results
- [ ] Routing determined (Step 9 or back to Step 7)

### Step 9: Run Experiments (8 Total Runs)
- [ ] **Pre-flight checks passed:**
  - [ ] Baselines loaded from checkpoint
  - [ ] Datasets loaded (primary + secondary)
  - [ ] Validation passed for all baselines
- [ ] Dynamic entry point discovered (Serena search)
- [ ] **Runner scripts created (Mode B):**
  - [ ] run_{baseline_1}_comparison.sh (2 runs: baseline vs ours)
  - [ ] run_{baseline_2}_comparison.sh (2 runs: baseline vs ours)
  - [ ] run_{baseline_3}_comparison.sh (2 runs: baseline vs ours)
  - [ ] run_all_experiments.sh (master orchestrator)
- [ ] Scripts use BASELINE's config (Mode B principle)
- [ ] Experiments launched with nohup, PID saved
- [ ] **All 6 experiments executed** (3 baselines × 2 methods × 1 seed)
- [ ] ≥90% completion rate achieved (or graceful degradation)
- [ ] Results aggregated from **ALL 6 result sets**
- [ ] comparison_data.csv created with **baseline_repo** and **method** columns (6 rows)
- [ ] **Comparison figures generated (LLM-autonomous):**
  - [ ] LLM analyzed comparison_data.csv structure
  - [ ] LLM analyzed 02c_experiment_brief.md for context
  - [ ] Appropriate figures generated based on data and context
- [ ] results_summary.md created with per-baseline analysis

### Step 10: Generate Report (Mode B Comparison)
- [ ] Hypothesis journey extracted from verification_state.yaml
- [ ] Comparison data loaded from comparison_data.csv (6 rows)
- [ ] **Per-baseline statistics calculated** (baseline vs ours)
- [ ] **Win/lose matrix computed** for each of 3 baselines
- [ ] Per-baseline improvement percentage calculated
- [ ] **LLM-generated comparison figures embedded**
- [ ] Executive summary with gate preview
- [ ] 05_baseline_comparison.md generated (Mode B format)
- [ ] Paper-ready summary included

### Step 10a: Gate Evaluation (Mode B)
- [ ] Retry limit checked (infinite loop prevention)
- [ ] Comparison summary saved to Serena Memory
- [ ] **Mode B Gate Evaluated:**
  - [ ] Win/lose computed for ALL 3 baselines (ours vs baseline_original)
  - [ ] Win counts calculated (X/3 baselines beaten)
  - [ ] Threshold applied (≥2/3 baselines = PASS)
- [ ] **DETERMINES_SUCCESS gate evaluated**
- [ ] Gate result determined (PASS/PARTIAL)
- [ ] If PARTIAL: Detailed failure analysis with win matrix saved to Serena Memory
- [ ] verification_state.yaml updated with gate results
- [ ] Checkpoint updated with Mode B gate results
- [ ] Routing decision determined (Phase 6 or Phase 0)

### Step 10b: Finalize
- [ ] **Benchmark Metrics Calculated:**
  - [ ] Termination quality (proper/improper termination)
  - [ ] Failure recording rate (if PARTIAL)
  - [ ] Gate compliance rate
  - [ ] Aggregate integrity score computed
- [ ] Archon tasks updated to 'done' status (all baselines)
- [ ] **Pipeline Task Update:**
  - [ ] If PASS: Phase 5 Task → done
  - [ ] If PARTIAL: Phase 0 will create new Pipeline
- [ ] Final Serena Memory snapshot saved (if PASS)
- [ ] Checkpoint archived with timestamp
- [ ] verification_state.yaml updated with final status
- [ ] Routing executed:
  - [ ] PASS → Phase 6 (Paper Writing)
  - [ ] PARTIAL → Phase 0 (New research direction)

---

## Pre-Execution Checks

### Phase 4 Completion
- [ ] `04_validation.md` exists
- [ ] `experiment_results.json` exists
- [ ] `code/outputs/results.csv` exists (primary dataset results)
- [ ] Hypothesis validation status is COMPLETED in verification_state.yaml
- [ ] Primary dataset name extracted from Phase 4 config

### Environment
- [ ] Exa MCP server available
- [ ] Serena MCP server can be activated
- [ ] Archon MCP server available
- [ ] gh CLI authenticated (`gh auth status`)
- [ ] Conda available
- [ ] Sufficient disk space for 3 repo clones
- [ ] GPU available (if needed)

---

## Archon Pipeline Integration

### Step Progress Tracking

- [ ] Pipeline Project ID retrieved from verification_state.yaml
- [ ] `current_step` initialized to 1 in checkpoint
- [ ] Step progress updated in checkpoint at each step transition

### Task Management

- [ ] **05_tasks.yaml generated in Step 6** (4 tasks × baselines proceeding = 12 max)
- [ ] Task status flow in YAML: pending → doing → review → done
- [ ] Archon `find_tasks`/`manage_task` **NOT used** for adaptation tasks
- [ ] Archon `rag_search_*` still used for knowledge base search

### Pipeline Task Update (Step 10b)
- [ ] **IF PASS:**
  - [ ] Phase 5 Task → done
  - [ ] Phase 6 Task → doing
- [ ] **IF PARTIAL:**
  - [ ] Failure recorded to Serena Memory
  - [ ] Phase 0 will create new Pipeline Project

---

## MCP ERROR RETRY PROTOCOL Compliance

- [ ] All MCP errors trigger retry
- [ ] 15-second delay between retry attempts
- [ ] Maximum 3 retry attempts per call
- [ ] Only skip/fail after 3 consecutive failures

---

## Multi-Baseline × Multi-Dataset Configuration

### Experiment Configuration
- [ ] Baselines count: matches workflow.yaml `config.experiment.baselines`
- [ ] Methods per baseline: 2 (baseline_original vs ours_injected) — FIXED
- [ ] Seeds: 1 value (from baseline's config) — FIXED
- [ ] **Total runs** = baselines × methods_per_baseline × seeds (per workflow.yaml)

### Mode B Fair Comparison Principle
- [ ] Each baseline uses THEIR OWN model architecture (BASELINE's)
- [ ] Each baseline uses THEIR OWN dataset (BASELINE's)
- [ ] Each baseline uses THEIR OWN hyperparameters (BASELINE's)
- [ ] ONLY difference is the ALGORITHM (baseline's vs ours injected)
- [ ] This is "baseline's home turf" - strong evidence if we still win

---

## Code Adaptation Quality (Per Baseline)

- [ ] Maximum 5 modified files per baseline
- [ ] Maximum 50 lines changed per file
- [ ] Maximum 500 new lines total per baseline
- [ ] No changes to core algorithms
- [ ] No changes to model architecture
- [ ] All changes documented in CHANGES.md per baseline

---

## Statistical Rigor (Multi-Comparison)

- [ ] Sample sizes sufficient (n ≥ 1 per method × dataset)
- [ ] **Per-dataset win/lose clearly determined**
- [ ] **Cross-dataset generalization evaluated**
- [ ] Effect sizes reported alongside win counts
- [ ] Confidence intervals provided where applicable

---

## Reproducibility

- [ ] All hyperparameters documented
- [ ] Random seeds tracked
- [ ] **Conda environments exportable for all 3 baselines**
- [ ] Git commits for all changes (per baseline branch)
- [ ] Reproduction commands documented

---

## Gate Criteria Summary

### Mode B Gate

| Criterion | Threshold | Description |
|-----------|-----------|-------------|
| Overall | ≥2/3 | Must beat at least 2 of 3 baselines (ours > baseline on their turf) |

**Examples:**
- PASS: Win 3/3 baselines → PASS (ours beats all baselines on their own environments)
- PASS: Win 2/3 baselines → PASS (ours beats 2 baselines on their own environments)
- PARTIAL: Win 1/3 baselines → PARTIAL (not enough evidence of superiority)

---

## Gate Routing Summary

| Gate Result | Gate Type | Routing | Serena Memory |
|-------------|-----------|---------|---------------|
| PASS | DETERMINES_SUCCESS | → Phase 6 | Success snapshot saved |
| PARTIAL | DETERMINES_SUCCESS | → Phase 0 | Detailed failure analysis saved |

---

## Error Recovery

### Recoverable Errors
| Error | Recovery Action |
|-------|-----------------|
| Network timeout | Retry with exponential backoff |
| gh rate limit | Wait and retry |
| Single experiment fails | Log and continue |
| Test fails | Fix and re-run |
| One baseline incompatible | Skip, continue with remaining (min 1) |

### Fatal Errors
| Error | Action |
|-------|--------|
| No suitable repos (< 3) | Stop, expand search criteria |
| >30% experiments fail | Stop, investigate |
| All baselines incompatible | Stop, revise search |
| No secondary dataset available | Graceful degradation (single dataset) |

---

## Retry Limits

| Action | Max Retries |
|--------|-------------|
| Coder-Validator cycles | 3 |
| Phase 5 retries | 3 |
| Quick Fix attempts (Step 9) | 3 |
| MCP error retries | 3 |

---

## UNATTENDED Mode Handling

- [ ] UNATTENDED mode checked throughout workflow
- [ ] Auto-proceed through all steps (no user prompts)
- [ ] Error handling continues workflow when possible
- [ ] nohup used for long-running experiments
- [ ] PID saved for experiment monitoring
- [ ] Status checks automated

---

## Output Verification

### Required Outputs

| Output | Location | Verified |
|--------|----------|----------|
| `05_baseline_comparison.md` | `{baseline_folder}/` | [ ] |
| `05_baseline_checkpoint.yaml` | `{baseline_folder}/` | [ ] |
| `05_baseline_checkpoint_archived_*.yaml` | `{baseline_folder}/` | [ ] |
| **`05_tasks.yaml`** | `{baseline_folder}/` | [ ] ← NEW |
| `comparison_data.csv` | `{baseline_folder}/experiments/` | [ ] |
| `results_summary.md` | `{baseline_folder}/` | [ ] |
| `comparison_plan.md` | `{baseline_folder}/` | [ ] |
| `repo_candidates.md` | `{baseline_folder}/` | [ ] |
| `evaluation_matrix.md` | `{baseline_folder}/` | [ ] |
| `selected_baselines.md` | `{baseline_folder}/` | [ ] |
| `dataset_selection.md` | `{baseline_folder}/` | [ ] |
| `setup_log.md` | `{baseline_folder}/` | [ ] |
| `code_analysis.md` | `{baseline_folder}/` | [ ] |
| `validation_log.md` | `{baseline_folder}/` | [ ] |
| LLM-generated figures (*.png) | `{baseline_folder}/figures/` | [ ] |

### verification_state.yaml Updates

**Location Verification:**
- [ ] Updated file is at `{research_folder}/verification_state.yaml`
- [ ] No new file created in `{baseline_folder}`

**Content Updates:**
- [ ] `main_hypothesis.baseline_comparison.status: "COMPLETED"`
- [ ] `main_hypothesis.baseline_comparison.gate.satisfied` set correctly
- [ ] `main_hypothesis.baseline_comparison.gate.result` set
- [ ] `episode.status` updated (COMPLETED or TERMINATED)
- [ ] `episode.terminated_properly: true`
- [ ] `episode.benchmark_metrics` populated
- [ ] `workflow.status` updated

---

## Critical Failures (Immediate Fix Required)

- [ ] current_step not updated in checkpoint (step progress lost)
- [ ] Hallucination/mock data detection skipped
- [ ] Less than 3 baselines selected (minimum 1 required)
- [ ] Mode B Fair Comparison Principle violated (modified baseline's data/model/config)
- [ ] Archon KB search skipped before code generation
- [ ] Task tool not used for validation (direct commands used)
- [ ] Only 1 baseline validated (should be all 3)
- [ ] Less than 6 runs executed without graceful degradation
- [ ] Gate threshold wrong (must be ≥2/3 baselines)
- [ ] Benchmark metrics not calculated
- [ ] Serena Memory not written (comparison summary or failure)
- [ ] Checkpoint not archived
- [ ] verification_state.yaml location wrong
- [ ] Routing decision not executed
- [ ] **Archon `manage_task` used for adaptation tasks**
- [ ] **05_tasks.yaml not generated in Step 6**
- [ ] **Task status not updated in 05_tasks.yaml**

---

## Validation Summary

**Total Checks:** 200+
**Required:** Step execution + Multi-baseline validation + Gate evaluation + Benchmark metrics
**MANDATORY Steps:** All steps (1-10b)

**Minimum Pass Criteria:**
- All steps completed (current_step updated in checkpoint)
- All 3 baselines processed (or graceful degradation with min 1)
- Both datasets used (or graceful degradation)
- Fair Comparison Principle followed
- Multi-Comparison Gate evaluated with correct thresholds
- Benchmark metrics calculated
- verification_state.yaml updated at correct location
- Routing decision determined and recorded

---

**Validation Result:**
- ✅ PASS: Gate passed, ≥2/3 baselines beaten (Mode B), ready for Phase 6
- ❌ PARTIAL: Gate partial, routing to Phase 0 for new research direction

**Completed By:** _______________
**Date:** _______________
**Hypothesis ID:** _______________
**Gate Result:** _______________

**Reviewer:** _____________
**Date:** {{date}}
**Validator:** Phase 5 Baseline Comparison Workflow (YouRA - Mode B)
