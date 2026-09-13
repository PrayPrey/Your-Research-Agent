# Full Pipeline UNATTENDED Mode - Instructions

<critical>
This workflow executes the ENTIRE Anonymous Research Pipeline automatically:
Phase 0 → 1 → 2A → 2B → (2C → 3 → 4) × N → 4.5 → [5] → 6 → 6.5 → 6.5.1
(Phase 5 is optional — skipped when pipeline_options.skip_baseline_comparison=true in module.yaml.
 When skipped: Phase 4.5 (Synthesis) → Phase 6 (Paper Writing) directly)

- Phase 6.5.1 added: Overleaf LaTeX + PDF generation
- Automatic figure insertion from figure_registry.yaml
- Steps renumbered: 0-11 (was 0-10)
- Step 10: Phase 6.5.1 (NEW - LaTeX/PDF)
- Step 11: Final Summary (was Step 10)

- Steps 0-11 (was 0-10)
- Step 4: Extract hypothesis
- Step 5: Phase 2B
- Step 6: Hypothesis Loop
- Step 7: Phase 5
- Step 8: Phase 6
- Step 9: Phase 6.5
- Step 10: Phase 6.5.1 (NEW)
- Step 11: Final Summary (was Step 10)

**⚠️ UNATTENDED MODE - CORRECT DEFINITION:**
```
UNATTENDED ≠ SIMPLIFIED (NOT simplification)
UNATTENDED ≠ SHORTCUT (NOT a shortcut)
UNATTENDED ≠ SKIP_STEPS (NOT skipping steps)
UNATTENDED ≠ FASTER_EXECUTION (NOT faster execution)

UNATTENDED = EXECUTE_ALL_STEPS + NO_USER_CONFIRMATION
           = Execute ALL steps completely + Skip ONLY user prompts
```

**Pre-Step Self-Check (MANDATORY before each phase):**
```
□ Am I about to skip a step-*.md file? → VIOLATION
□ Am I about to skip an MCP tool call? → VIOLATION
□ Am I about to skip a Task agent call? → VIOLATION
□ Am I only skipping [Y/N] confirmation? → ALLOWED
```

**EXECUTION RULES:**
- UNATTENDED MODE is ALWAYS active - NO user confirmations
- Each phase uses `<invoke-workflow>` for guaranteed execution
- Hypothesis loop processes ALL READY hypotheses in dependency order
- Phase 4 MUST_WORK gate failures route to Phase 0 or Phase 2A-Dialogue
- Phase 5 DETERMINES_SUCCESS gate failures route to Phase 0
- Serena Memory saves failure context before routing

**GATE SYSTEM:**
- Phase 4: MUST_WORK (PoC validation) - PASS → Phase 5 (or Phase 6 if skip), FAIL → Phase 0, PARTIAL → Phase 2A-Dialogue
- Phase 5: DETERMINES_SUCCESS (Baseline comparison) - PASS → Phase 6, PARTIAL → Phase 0, SKIPPED → Phase 6 (when skip_baseline_comparison=true)
- Phase 6: Paper generation (no gate, always proceeds to 6.5)
- Phase 6.5: Adversarial review (convergence-based completion, proceeds to 6.5.1)
- Phase 6.5.1: LaTeX/PDF generation (no gate, final output)
</critical>

<critical>
**📖 FILE READING PROTOCOL:**

This instructions.md file is **850+ lines**. Complete execution requires reading the entire file at once.

**✅ Correct Reading:**
```python
Read(file_path="instructions.md") # NO offset/limit parameters
```

**❌ Incorrect Reading (PROHIBITED):**
```python
Read(file_path="instructions.md", offset=0, limit=200) # ❌ Partial reading
Read(file_path="instructions.md", offset=200, limit=200) # ❌ Causes step omission
```

**Why Critical:**
- Full Pipeline orchestrates 12 steps (0-11) - missing any step causes incomplete pipeline execution
- Instructions.md contains sequential steps 0-11 with NO decimal sections

**Section Pattern:** All steps use clean sequential numbering (0, 1, 2, 3... 11) - no decimal sections.
</critical>

---

## Step 0: Initialize & Resume Detection

<critical>
**Resume-First Logic**: Check for existing pipeline before requiring input file.
This enables automatic resume after session restart without re-providing research idea.
</critical>

<action>Step 0.1: Detect existing pipeline</action>

```python
# Scan for ANY research folders (covers Phase 0 through Phase 6.5)
all_folders = glob("docs/youra_research/*/")

existing_pipeline = None
IF all_folders:
    # Find most recent (by folder name with timestamp)
    all_folders.sort(reverse=True)
    existing_pipeline = all_folders[0].rstrip('/')

    display: f"""
🔄 **Existing Pipeline Detected**
   Folder: {existing_pipeline}
   Checking outputs for resume point...
"""
```

<action>Step 0.2: Branch based on pipeline existence</action>

```python
IF existing_pipeline:
    # ═══════════════════════════════════════════════════════════
    # RESUME PATH: Existing pipeline found
    # ═══════════════════════════════════════════════════════════
    research_folder = existing_pipeline

    # Skip to resume detection (Section 0.3)
    GOTO Step 0.3

ELSE:
    # ═══════════════════════════════════════════════════════════
    # NEW PIPELINE PATH: No existing pipeline
    # ═══════════════════════════════════════════════════════════

    <action>Parse input file path from user input</action>

    input_file = "{{user_input}}"

    IF input_file is empty:
        EXIT with error: """
❌ **Research idea file path required**

No existing pipeline found and no input file provided.

Usage:
  /full-pipeline-unattended path/to/research_idea.md

Or resume existing pipeline by running:
  /full-pipeline-unattended
  (if pipeline exists in docs/youra_research/)
"""

    <action>Validate input file exists</action>

    IF NOT file_exists(input_file):
        EXIT with error: f"Input file not found: {input_file}"

    <action>Read research idea content and store as {research_idea_content}</action>

    research_idea_content = read_file(input_file)

    # Create new research folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    research_folder = f"docs/youra_research/{timestamp}_youra_research"
    create_directory(research_folder)

    display: f"""
✨ **New Pipeline Starting**
   Folder: {research_folder}
   Input: {input_file}
"""
```

<critical>
**RESUME DETECTION** - Check existing pipeline state and resume from appropriate phase.
This enables automatic recovery after session restart, /compact, or interruption.
</critical>

<action>Step 0.3: Detect resume point from existing files and state</action>

```python
# Resume detection logic - check in reverse order (latest phase first)
resume_from = "Phase 0" # Default: start fresh

# 1. Check verification_state.yaml (Phase 2B+)
IF file_exists("{research_folder}/verification_state.yaml"):
    state = read_yaml("{research_folder}/verification_state.yaml")

    IF state.workflow.status == "ACTIVE":
        # Find current phase from state
        current_phase = state.workflow.current_phase

        IF current_phase == "Phase 6.5.1":
            # Resume Phase 6.5.1 (Step 10)
            resume_from = "Phase 6.5.1"
        ELIF current_phase == "Phase 6.5":
            # Resume Phase 6.5 (Step 9)
            resume_from = "Phase 6.5"
        ELIF current_phase == "Phase 6":
            # Resume Phase 6 (Step 8)
            resume_from = "Phase 6"
        ELIF current_phase == "Phase 5 Skipped":
            # Phase 5 was skipped by config, resume at Phase 6 (Step 8)
            resume_from = "Phase 6"
        ELIF current_phase == "Phase 5":
            # Resume directly to Phase 5 (Step 8)
            resume_from = "Phase 5"
        ELIF current_phase == "Hypothesis Loop Complete":
            # Sub-hypotheses done, need to run Phase 5 (Step 8)
            resume_from = "Phase 5"
        ELIF current_phase in ["Phase 2C", "Phase 3", "Phase 4"]:
            # Resume hypothesis loop for sub-hypothesis processing
            resume_from = "Hypothesis Loop"
        ELIF current_phase == "Phase 2B":
            resume_from = "Phase 2B"

    ELIF state.workflow.status == "COMPLETED":
        resume_from = "ALREADY_COMPLETE"

# 2. Check Phase 2A Dialogue output
ELIF file_exists("{research_folder}/03_refinement.yaml"):
    refinement = read_yaml("{research_folder}/03_refinement.yaml")
    IF refinement.phase2b_readiness.status == "READY":
        resume_from = "Phase 2B"
    ELSE:
        resume_from = "Phase 2A-Dialogue"

# 3. Check Phase 2A Dialogue in-progress (discussion_log.md exists but structuring not done)
ELIF file_exists("{research_folder}/discussion_log.md"):
    resume_from = "Phase 2A-Dialogue"

# 4. Check Phase 1 output
ELIF file_exists("{research_folder}/01_targeted_research.md"):
    resume_from = "Phase 2A-Dialogue"

# 5. Check Phase 0 output
ELIF file_exists("{research_folder}/00_brainstorm_session.md"):
    resume_from = "Phase 1"
```

<action>Step 0.4: Execute resume based on detected state</action>

```python
IF resume_from == "ALREADY_COMPLETE":
    GOTO Step 11 (Final Summary)
ELIF resume_from == "Phase 6.5.1":
    GOTO Step 10 (Phase 6.5.1)
ELIF resume_from == "Phase 6.5":
    GOTO Step 9 (Phase 6.5)
ELIF resume_from == "Phase 6":
    GOTO Step 8 (Phase 6)
ELIF resume_from == "Phase 5":
    GOTO Step 7 (Phase 5)
ELIF resume_from == "Hypothesis Loop":
    GOTO Step 6 (Hypothesis Loop)
ELIF resume_from == "Phase 2B":
    GOTO Step 5 (Phase 2B)
ELIF resume_from == "Phase 2A-Dialogue":
    GOTO Step 3 (Phase 2A-Dialogue)
ELIF resume_from == "Phase 1":
    GOTO Step 2 (Phase 1)
ELSE: # "Phase 0"
    GOTO Step 1 (Phase 0)
```

---

## Step 1: Execute Phase 0 (Brainstorm)

<critical>
Research Idea Constraints - MUST BE ENFORCED:
- NO ideas requiring manual data generation/labeling
- NO ideas depending on external LLM APIs (OpenAI, Anthropic)
- PREFER: Existing datasets (Defects4J, etc.), synthetic data, self-contained experiments
</critical>

<invoke-workflow
  path="{phase0_workflow}"
  mode="unattended"
  with:
    batch_mode: true
    research_idea_content: "{{research_idea_content}}"
/>

<action>Verify output exists: {research_folder}/00_brainstorm_session.md</action>

<check if="output not exists">
  <invoke-workflow path="{phase0_workflow}" mode="unattended" recovery="true"/>
  <check if="still not exists">
    <goto step="ERROR_EXIT"/>
  </check>
</check>

---

## Step 2: Execute Phase 1 (Research)

<invoke-workflow
  path="{phase1_workflow}"
  mode="unattended"
/>

<action>Verify outputs exist:</action>
- {research_folder}/01_targeted_research.md
- {research_folder}/01_targeted_research_full.md

<check if="outputs not exist">
  <invoke-workflow path="{phase1_workflow}" mode="unattended" recovery="true"/>
  <check if="still not exists">
    <goto step="ERROR_EXIT"/>
  </check>
</check>

---

## Step 3: Execute Phase 2A (Self-Contained Tikitaka Dialogue)

<invoke-workflow
  path="{phase2a_workflow}"
  mode="unattended"
/>

<action>Verify outputs exist:</action>
- {research_folder}/03_refinement.yaml
- {research_folder}/02_synthesis.yaml
- {research_folder}/01_round_table/final_opinions.yaml

<check if="outputs not exist">
  <invoke-workflow path="{phase2a_workflow}" mode="unattended" recovery="true"/>
  <check if="still not exists">
    <goto step="ERROR_EXIT"/>
  </check>
</check>

<action>Check phase2b_readiness.status from 03_refinement.yaml</action>
<check if="phase2b_readiness.status != READY">
  <goto step="ERROR_EXIT"/>
</check>

---

## Step 4: Extract Hypothesis from Phase 2A Outputs

<action>Parse 03_refinement.yaml and 02_synthesis.yaml to extract hypothesis</action>

```python
refinement_file = f"{research_folder}/03_refinement.yaml"
synthesis_file = f"{research_folder}/02_synthesis.yaml"
refinement = parse_yaml(refinement_file)
synthesis = parse_yaml(synthesis_file)
```

<check if="refinement.phase2b_readiness.status != READY">
  <goto step="ERROR_EXIT"/>
</check>

---

## Step 5: Execute Phase 2B (Planning)

<invoke-workflow
  path="{phase2b_workflow}"
  mode="unattended"
/>

<action>Verify outputs exist:</action>
- {research_folder}/02b_verification_plan.md
- {research_folder}/verification_state.yaml

<check if="outputs not exist">
  <invoke-workflow path="{phase2b_workflow}" mode="unattended" recovery="true"/>
  <check if="still not exists">
    <goto step="ERROR_EXIT"/>
  </check>
</check>

---

## Step 6: Execute Hypothesis Loop (Phase 2C → 3 → 4)

<critical>
This step invokes the hypothesis-loop workflow which handles:
- Loading verification_state.yaml
- Gate validation for each hypothesis
- Executing Phase 2C → 3 → 4 per hypothesis (NOT Phase 5)
- Processing Phase 4 gate results (PASS/PARTIAL/FAIL)
- Gate routing on Phase 4 failure:
  - Phase 4 FAIL → Route to Phase 0 (fundamental flaw)
  - Phase 4 PARTIAL (max attempts) → Route to Phase 2A-Dialogue (hypothesis redesign)
- Serena Memory saving before routing (failure context preservation)
- State updates and dependent hypothesis management

This ensures `<invoke-workflow>` tags are processed in workflow.xml context.
</critical>

<action>Set execution_source flag for hypothesis-loop</action>

```python
# hypothesis-loop will EXIT after step-11, returning control here for Phase 5 invocation
state = read_yaml("{verification_state_file}")
state.workflow.execution_source = "full-pipeline"
save_verification_state(state)
```

<invoke-workflow
  path="{hypothesis_loop_workflow}"
  mode="auto"
/>

<critical>
**INVOKE-WORKFLOW COMPLETED - HYPOTHESIS LOOP RETURNED**

hypothesis-loop workflow has finished processing sub-hypotheses and returned control here.
Per workflow.xml rule: "Wait for target workflow COMPLETE execution before proceeding"

Phase 5 is invoked separately in Step 7 below.
</critical>

<action>Check hypothesis-loop result (Phase 4 routing)</action>

```python
# Check workflow status from verification_state.yaml
state = read_yaml("{verification_state_file}")

IF state.workflow.status == "STOPPED":
    # MUST_WORK gate failure - pipeline cannot continue
    GOTO MUST_PASS_FAILURE

ELIF state.workflow.status == "ROUTED":
    # Routing occurred (Phase 4 failure)
    routing = state.workflow.routing

    IF routing.target == "Phase 0":
        # Fundamental flaw - restart from scratch
        # Note: Serena Memory already saved by hypothesis-loop
        GOTO Step 1 (Phase 0)

    ELIF routing.target == "Phase 2A-Dialogue":
        # Hypothesis redesign needed
        # Note: Serena Memory already saved by hypothesis-loop
        GOTO Step 3 (Phase 2A-Dialogue)

# Check for "Hypothesis Loop Complete" state
ELIF state.workflow.current_phase == "Hypothesis Loop Complete":
    # All sub-hypotheses processed, proceed to Phase 5
    GOTO Step 7 (Phase 5)

ELIF state.workflow.status == "COMPLETED":
    # This shouldn't happen (Phase 5 sets COMPLETED)
    # But keep for backward compatibility
    GOTO Step 11 (Final Summary)
```

---

## Step 7: Execute Phase 5 (Baseline Comparison)

<critical>
**Phase 5 Invocation**

Phase 5 is invoked directly from instructions.md to ensure proper workflow.xml execution.
Phase 5 is OPTIONAL — skipped when pipeline_options.skip_baseline_comparison=true in module.yaml.

**Phase 5 Gates:**
- DETERMINES_SUCCESS: Our method must outperform baseline
- PASS → Continue to Step 8 (Phase 6 Paper Writing)
- PARTIAL → Route to Phase 0 (approach fundamentally inferior)
- SKIPPED → Continue to Step 8 (Phase 6 Paper Writing) directly
</critical>

<action>Check skip_baseline_comparison config</action>

```python
# Read module.yaml config for skip option
module_config = read_yaml("{config_source}")
skip_baseline = module_config.get("pipeline_options", {}).get("skip_baseline_comparison", False)

IF skip_baseline:
    # ═══════════════════════════════════════════════════════════
    # SKIP PATH: Phase 5 skipped by config
    # ═══════════════════════════════════════════════════════════
    state = read_yaml("{verification_state_file}")

    # Update verification_state with SKIPPED status
    state.workflow.current_phase = "Phase 5 Skipped"
    state.main_hypothesis.baseline_comparison.status = "SKIPPED"
    state.main_hypothesis.baseline_comparison.gate.result = "SKIPPED"
    state.main_hypothesis.baseline_comparison.skipped_at = datetime.now().isoformat()
    state.main_hypothesis.baseline_comparison.skip_reason = "skip_baseline_comparison=true in module.yaml"
    state.statistics.phase5_statistics.skipped_by_config = True
    state.statistics.phase5_statistics.gate_result = "SKIPPED"
    save_verification_state(state)

    display: """
⏭️ **Phase 5 (Baseline Comparison) SKIPPED**
   Reason: skip_baseline_comparison=true in module.yaml
   Proceeding directly to Phase 6 (Paper Writing)...
   Note: Paper will be written based on Phase 4 integrated results only.
"""

    GOTO Step 8 (Phase 6)
```

<action>Verify readiness for Phase 5</action>

```python
# Verify sub-hypotheses are complete
state = read_yaml("{verification_state_file}")

IF NOT state.workflow.get("sub_hypotheses_complete", False):
    display: "⚠️ Sub-hypotheses not complete - unexpected state"
    GOTO MUST_PASS_FAILURE

# Update state for Phase 5
state.workflow.current_phase = "Phase 5"
save_verification_state(state)

display: """
▶️ **Phase 5 (Baseline Comparison) Starting**
   Target: main_hypothesis validation
   Gate: DETERMINES_SUCCESS
"""
```

<invoke-workflow
  path="{phase5_workflow}"
  mode="unattended"
/>

<critical>
**INVOKE-WORKFLOW COMPLETED - PHASE 5 RETURNED**

Phase 5 workflow has finished baseline comparison and returned control here.
Per workflow.xml rule: "Wait for target workflow COMPLETE execution before proceeding"

**IMMEDIATELY proceed to check Phase 5 results below - DO NOT STOP.**
</critical>

<action>Check Phase 5 result</action>

```python
# Re-read state after Phase 5 completion
state = read_yaml("{verification_state_file}")

IF state.workflow.status == "STOPPED":
    # Unexpected Phase 5 failure
    GOTO MUST_PASS_FAILURE

ELIF state.workflow.status == "ROUTED":
    # Phase 5 PARTIAL - approach inferior to baseline
    routing = state.workflow.routing

    IF routing.target == "Phase 0":
        # Baseline outperforms our method - need new research direction
        # Note: Serena Memory already saved by Phase 5 (phase5_failure_{id}.md)
        display: """
🔴 **DETERMINES_SUCCESS gate PARTIAL**
   Baseline outperforms our method.
   Routing to Phase 0 for new research direction...
"""
        GOTO Step 1 (Phase 0)

ELIF state.workflow.status == "COMPLETED":
    # Phase 5 PASS - proceed to Phase 6 Paper Writing
    display: """
🎉 **DETERMINES_SUCCESS gate PASSED!**
   Main hypothesis validated - our method outperforms baseline.
   Proceeding to Paper Writing...
"""
    # (Old Step 7 redundant check removed)

ELSE:
    display: f"⚠️ Unexpected Phase 5 status: {state.workflow.status}"
    GOTO MUST_PASS_FAILURE
```

---

## Step 8: Execute Phase 6 (Paper Writing)

<critical>
**Phase 6: Academic Paper Generation**

Generate ICML-format academic paper from Phase 0-5 artifacts.
This phase has no gate - it always proceeds to Phase 6.5 upon completion.
Note: When Phase 5 was skipped (skip_baseline_comparison=true), Phase 6 writes the paper
based on Phase 4 integrated results only — no baseline comparison data will be available.
</critical>

<action>Update state for Phase 6</action>

```python
state.workflow.current_phase = "Phase 6"
save_verification_state(state)

display: """
▶️ **Phase 6 (Paper Writing) Starting**
   Target: Generate ICML-format academic paper
   Output: paper/06_paper.md, paper/065_ground_truth.yaml, paper/06_narrative_blueprint.yaml
"""
```

<invoke-workflow
  path="{phase6_workflow}"
  mode="unattended"
/>

<critical>
**INVOKE-WORKFLOW COMPLETED - PHASE 6 RETURNED**

Phase 6 workflow has finished paper generation and returned control here.
Per workflow.xml rule: "Wait for target workflow COMPLETE execution before proceeding"

**IMMEDIATELY proceed to Step 9 (Phase 6.5) - DO NOT STOP.**
</critical>

<action>Verify Phase 6 output</action>

```python
paper_file = "{research_folder}/paper/06_paper.md"

IF NOT file_exists(paper_file):
    display: "⚠️ Paper file missing - attempting retry..."
    invoke_workflow(phase6_workflow, recovery=True)

IF NOT file_exists(paper_file):
    display: "❌ Phase 6 failed to generate paper"
    GOTO ERROR_EXIT

display: "✓ Phase 6 complete - paper generated"
```

---

## Step 9: Execute Phase 6.5 (Adversarial Review)

<critical>
**Phase 6.5: Multi-Round Adversarial Review**

Devil's Advocate review with role separation to identify and fix paper issues.
Uses convergence-based completion (max 3 rounds).
</critical>

<action>Update state for Phase 6.5</action>

```python
state.workflow.current_phase = "Phase 6.5"
save_verification_state(state)

display: """
▶️ **Phase 6.5 (Adversarial Review) Starting**
   Rounds: R1 (Accuracy+Engagement) → R2 (Verification+Credibility) → [R3 (Final Check)]
   Convergence: Fatal=0, Major=0, persuasiveness_passed
   Personas: accuracy_checker, bored_reviewer, skeptical_expert
"""
```

<invoke-workflow
  path="{phase65_workflow}"
  mode="unattended"
/>

<critical>
**INVOKE-WORKFLOW COMPLETED - PHASE 6.5 RETURNED**

Phase 6.5 workflow has finished adversarial review and returned control here.
Per workflow.xml rule: "Wait for target workflow COMPLETE execution before proceeding"

**IMMEDIATELY proceed to Step 10 (Phase 6.5.1) - DO NOT STOP.**
</critical>

<action>Verify Phase 6.5 output</action>

```python
final_paper = "{research_folder}/paper/06_paper_final.md"
review_summary = "{research_folder}/paper/review/065_review_summary.md"

IF file_exists(final_paper):
    display: """
✓ Phase 6.5 complete - final paper ready
  Proceeding to Phase 6.5.1 (LaTeX/PDF generation)...
"""
ELSE:
    display: """
⚠️ Phase 6.5 completed but final paper not found
   Using 06_paper.md as input for Phase 6.5.1
"""
```

---

## Step 10: Execute Phase 6.5.1 (Overleaf LaTeX + PDF)

<critical>
**Phase 6.5.1: Overleaf LaTeX + PDF Generation**

Convert final reviewed paper (06_paper_final.md) to Overleaf-compilable LaTeX project and generate PDF.
Includes automatic figure insertion from figure_registry.yaml with intelligent caption generation.
This is the final output phase - produces submission-ready PDF.
</critical>

<action>Update state for Phase 6.5.1</action>

```python
state.workflow.current_phase = "Phase 6.5.1"
save_verification_state(state)

display: """
▶️ **Phase 6.5.1 (Overleaf LaTeX + PDF) Starting**
   Input: paper/06_paper_final.md
   Output: paper/overleaf/main.pdf
   Features: Automatic figure insertion, ICML 2025 format
"""
```

<invoke-workflow
  path="{phase651_workflow}"
  mode="unattended"
/>

<critical>
**INVOKE-WORKFLOW COMPLETED - PHASE 6.5.1 RETURNED**

Phase 6.5.1 workflow has finished LaTeX/PDF generation and returned control here.
Per workflow.xml rule: "Wait for target workflow COMPLETE execution before proceeding"

**IMMEDIATELY proceed to Step 11 (Final Summary) - DO NOT STOP.**
</critical>

<action>Verify Phase 6.5.1 output</action>

```python
overleaf_pdf = "{research_folder}/paper/overleaf/main.pdf"
overleaf_folder = "{research_folder}/paper/overleaf"

IF file_exists(overleaf_pdf):
    pdf_size = get_file_size(overleaf_pdf)
    display: f"""
✓ Phase 6.5.1 complete - PDF generated
  Location: {overleaf_pdf}
  Size: {pdf_size // 1024}KB
  Overleaf project: {overleaf_folder}
"""
ELSE:
    display: """
⚠️ Phase 6.5.1 completed but PDF not found
   Check {overleaf_folder} for LaTeX project
   Manual compilation may be needed
"""
```

---

## Step 11: Final Summary

<action>Read final verification_state.yaml</action>
<action>Calculate statistics</action>

```python
total = len(hypotheses)
completed = count where status == "COMPLETED"
passed = count where gate.satisfied == True
failed = total - passed
```

<action>Display completion summary</action>

```
═══════════════════════════════════════════════════════════════
            FULL PIPELINE COMPLETE (Phase 0 → 6.5.1)
═══════════════════════════════════════════════════════════════

📊 **Hypothesis Results:**
   Total: {{total}}
   Passed: {{passed}}
   Failed: {{failed}}

📄 **Paper Output:**
   Markdown (Draft): {{paper_file}}
   Markdown (Final): {{final_paper}}
   PDF (Submission): {{overleaf_pdf}}
   Review Summary: {{review_summary}}
   Overleaf Project: {{overleaf_folder}}

🎉 **Ready for Submission!**
   The PDF is ICML 2025 format with all figures included.

═══════════════════════════════════════════════════════════════
```

<goto step="COMPLETE"/>

---

## Error Handling Steps

### MUST_PASS_FAILURE

<critical>
A MUST_WORK gate failed and cannot be routed. Pipeline must stop.
This typically occurs when:
- Critical infrastructure failure
- Unrecoverable validation error
- Dependency chain broken
</critical>

<action>State already saved by hypothesis-loop with workflow.status = "STOPPED"</action>
<action>Report failure summary to user</action>
<goto step="END"/>

### ROUTING_PHASE0

<critical>
Routing to Phase 0 due to:
- Phase 4 FAIL: Fundamental flaw in approach
- Phase 5 PARTIAL: Approach inferior to baseline
Serena Memory has been saved with failure context.
</critical>

<action>Read Serena Memory for context (if resuming)</action>

```python
# Read failure context from Serena Memory
IF routing.source == "Phase 4":
    memory_file = "failure_{hypothesis_id}.md"
ELIF routing.source == "Phase 5":
    memory_file = "phase5_failure_{hypothesis_id}.md"

context = mcp__serena__read_memory(memory_file_name=memory_file)
```

<action>Reset pipeline state for fresh start</action>
<goto step="Step 1"/>

### ROUTING_PHASE2A_DIALOGUE

<critical>
Routing to Phase 2A-Dialogue due to:
- Phase 4 PARTIAL with max attempts reached: Hypothesis needs redesign
Serena Memory has been saved with modification history.
</critical>

<action>Read Serena Memory for context (if resuming)</action>

```python
# Read modification context from Serena Memory
memory_file = "pivot_{hypothesis_id}_{new_hypothesis_id}.md"
context = mcp__serena__read_memory(memory_file_name=memory_file)
```

<action>Reset pipeline state for Phase 2A restart</action>
<goto step="Step 3"/>

### ERROR_EXIT

<action>Save any partial state</action>
<goto step="END"/>

### COMPLETE

<action>Update Archon Pipeline project: all phases = done</action>
<action>Save final verification_state.yaml with workflow.status = "COMPLETED"</action>
<goto step="END"/>

### END

<action>Pipeline execution finished</action>
