---
name: 'step-00-init'
description: 'Initialize Phase 0: Resume detection, failure recovery, auto-fill mode, and Archon pipeline setup'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase0-brainstorm'
workflowFile: '{workflow_path}/workflow.yaml'
thisStepFile: '{workflow_path}/steps/step-00-init.md'
nextStepFile: '{workflow_path}/steps/step-01-session-setup.md'
template: '{workflow_path}/template.md'
default_output_file: '{research_output_path}/00_brainstorm_session.md'
research_folder: '{research_output_path}'
helper_archon_pipeline: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers/archon_pipeline_creation.md'
helper_archon_phase_reset: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers/archon_phase_reset.md'
---

# Step 0: Initialize Phase 0

**Goal:** Set up session with resume detection, failure context recovery, auto-fill mode check, and Archon pipeline initialization

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and File Reading Protocol.

### Step-Specific Rules:
- 🎯 Focus only on initialization: resume detection, failure recovery, auto-fill check, Archon setup
- 🚫 FORBIDDEN to skip resume detection or Archon pipeline creation
- 💬 Approach: Systematic initialization with clear status reporting
- 📋 Ensure all initialization steps complete before proceeding

---

## 0.1 Progressive File System Setup

<critical>
This workflow writes to the output file PROGRESSIVELY after each step.
This enables automatic resume after /compact or context limits.

**Output File:** {default_output_file}
**Placeholder Pattern:** `{{UNFILLED:variable_name}}`
**Filled Content:** Actual text replaces the placeholder
**Skipped Content:** `*Skipped by user*` replaces the placeholder
</critical>

<step-to-placeholder-mapping>
| Step | Placeholders to Fill |
|------|---------------------|
| 0 | `lessons_from_previous_attempts` (ROUTE_TO_0 only, or "N/A - First attempt") |
| 1 | `initial_interest`, `existing_context` |
| 2 | `approach_selection`, `session_plan` |
| 3 | `technique_sessions` |
| 4 | `main_research_question`, `refined_question`, `detailed_questions` |
| 5 | `reference_papers` |
| 6 | `so_what_validation`, `feasibility_validation` |
| 7 | `phase1_research_question`, `phase1_detailed_question`, `phase1_reference_papers`, `key_insights`, `techniques_used`, `areas_for_exploration`, `session_duration`, `next_steps` |
</step-to-placeholder-mapping>

---

## 0.2 Auto-Resume Check

<critical>
DO NOT ask user if they want to resume. Just check and resume automatically.
</critical>

<action>**Check for existing session file:**

1. Check if {default_output_file} exists
2. If NOT exists → Initialize new file from template, proceed to Step 0.3
3. If exists → Read file and determine resume point
</action>

<action>**Determine resume point by checking placeholders:**

Scan order (find FIRST `{{UNFILLED:...}}` pattern):

| Check Location | If UNFILLED | Resume To |
|----------------|-------------|-----------|
| "Initial Interest:" line | `{{UNFILLED:initial_interest}}` | Step 1 |
| "Session Approach:" line | `{{UNFILLED:approach_selection}}` | Step 2 |
| "## Technique Sessions" | `{{UNFILLED:technique_sessions}}` | Step 3 |
| "### Initial Question" | `{{UNFILLED:main_research_question}}` | Step 4 |
| "## Reference Papers" | `{{UNFILLED:reference_papers}}` | Step 5 |
| "### So What Test" | `{{UNFILLED:so_what_validation}}` | Step 6 |
| "## Phase 1 Input Package" | `{{UNFILLED:phase1_research_question}}` | Step 7 |
| NO `{{UNFILLED:...}}` found | - | Session COMPLETE |
</action>

<action>**On resume, load existing data:**

If resuming from Step N (N > 1):
1. Extract all filled content from Steps 1 to N-1
2. Store in memory for context
3. Display brief summary:

"🔄 **Resuming Previous Session**

**Completed:**
- Initial Interest: [brief summary]
- Approach: [selected approach]
- [other completed items...]

**Resuming from:** Step N - [Step Name]

Let's continue!"

4. Jump directly to Step N (do NOT re-ask completed steps)
</action>

<action>**If session is complete:**

If no `{{UNFILLED:...}}` placeholders remain:

"✅ **Session Already Complete**

Your brainstorm session is already finished!

Output file: {default_output_file}

Options:
- [v] View the results
- [n] Start a NEW session (will create new file)
- [p] Proceed to Phase 1"
</action>

---

## 0.3 Failure Context Recovery (Serena Memory)

<critical>
Phase 0 may be invoked after Phase 4 FAIL or Phase 5 PARTIAL.
Check for failure records to inform brainstorming direction.
This section reads **ALL** relevant memory files to understand the complete failure history.
</critical>

<action>**Check for Previous Research Records:**

1. Call `mcp__serena__list_memories()` to get all available memory files
2. **Read ALL .md files** - memory files are self-documenting with complete metadata
3. Extract relevant information directly from file content (routing decisions, lessons learned, etc.)
4. Incorporate all records into brainstorming context
</action>

<action>**Store Failure Context:**

If any failure-related memory files are found:
- Remember all the content from these files as `previous_failure_contexts`
- Note the types of failures encountered (Phase 4 FAIL, Phase 5 PARTIAL, etc.)
- This information will be used in Section 0.4 for informed brainstorm generation
</action>

<action>**Incorporate Failure Context in Later Steps:**

If failure context exists:
- In Interactive Mode (Step 1): Guide away from approaches that failed before
- In Interactive Mode (Step 4): Ensure new research question addresses previous gaps
- In Interactive Mode (Step 6): Validate that new direction won't hit same issues
- In UNATTENDED Mode (Section 0.4): Use context to generate improved brainstorm
</action>

---

## 0.3.5 Archive Verification (Late Recovery)
<critical>
**Purpose:** Ensure previous run's artifacts are archived before starting a new run.

Detection is now based on **residual artifact presence** in the
research folder, NOT on whether `_archive/` exists. This fixes the bug where
Reflection 2+ would skip archiving because a previous archive already existed,
leaving stale files (h-*/, verification_state.yaml, 02b_*, 03_*, etc.) mixed
with the new run's outputs.

**Rule:** If previous_failure_contexts exist AND residual artifacts are found
in the research folder → ALWAYS create a new timestamped archive subfolder and
move residual files into it. Each Reflection gets its own archive.
</critical>

<check if="previous_failure_contexts EXISTS">

<action>**Detect Residual Artifacts (NOT archive folder existence):**

Scan the research folder root for ANY of these residual artifact indicators:
- `h-*/` directories (hypothesis experiment folders)
- `verification_state.yaml`
- `02b_verification_plan.md`
- `02_synthesis.yaml`
- `03_refinement.yaml` or `03_refinement.md`
- `discussion_log.md`
- `phase2a_step_tasks.yaml`
- `01_round_table/` directory
- `paper_config.yaml`
- `papers/` or `paper_summaries/` directories
- `045_validated_hypothesis.md`

**Decision:**
- If ANY residual artifacts found → archive recovery needed (proceed below)
- If NO residual artifacts found → skip archive (already clean)

**IMPORTANT:** The presence or absence of `_archive/` folder is IRRELEVANT.
Only the presence of residual artifacts in the research folder root matters.
</action>

<action>**Execute Archive Recovery (per-Reflection timestamped):**

If residual artifacts detected:
1. Generate timestamp: `{YYYYMMDD}T{HHMMSS}` (e.g., `20260310T100921`)
2. Create archive folder: `{research_folder}/_archive/{timestamp}_reflection_recovery/`
3. **Move ALL non-archive items** from the research folder into the archive:
   - All `.md` files (except `00_brainstorm_session.md` if it was JUST created in this run)
   - All `.yaml` files
   - All subdirectories: `h-*/`, `01_round_table/`, `papers/`, `paper_summaries/`, `paper/`, `.data_cache/`
   - `.tmp` files
   - Excludes ONLY: `_archive/` folder itself, `00_brainstorm_session.md` (current run)
4. Create `_ARCHIVED.md` marker file inside the archive folder:
   ```
   # Archive Record

   **Archived:** {timestamp} (Reflection Recovery)
   **Reason:** ROUTE_TO_0 - Previous run artifacts archived before new Reflection
   **Failure Context:** {summary from previous_failure_contexts}
   **Recovery:** Reflection archive recovery executed at Phase 0 re-entry (Section 0.3.5)
   ```
5. Log: "Archived {N} files/folders to _archive/{timestamp}_reflection_recovery/"
</action>

<action>**Archon Pipeline Terminate Late Recovery:**

> **Reference:** `{helper_archon_phase_reset}` - `terminate_pipeline_on_phase0_routing()`

If failure type is MUST_WORK_FAIL or DETERMINES_SUCCESS_PARTIAL:
1. Extract `pipeline_project_id` from Serena Memory failure files
2. Check if the Pipeline project title starts with `[FAILED]`
3. If NOT terminated → call `terminate_pipeline_on_phase0_routing()` from helper
4. If already terminated → skip (log confirmation)
</action>

</check>

---

## 0.4 Auto-Fill Mode Check (UNATTENDED)

<critical>
Auto-fill mode (UNATTENDED) activates when called from batch pipeline or with unattended flag.
It skips interactive brainstorming and directly generates Phase 1 input package.

**Research Output Path:** `{research_output_path}` (defined in workflow.yaml)
</critical>

<action>**Detection Logic:**

UNATTENDED mode is triggered by ANY of:
1. `batch_mode: true` parameter (from invoke-workflow)
2. `mode="unattended"` in workflow invocation
3. `#batch-mode` marker in input/context text
4. `research_idea_content` parameter present (from full-pipeline-unattended)

If UNATTENDED mode is detected:
- Execute Auto-Fill (below) → END workflow

If NOT UNATTENDED:
- Continue to Section 0.5 (Archon Init) → Interactive Mode
</action>

---

### ⚠️ CRITICAL: Exclusive Routing Decision (0.4.1 vs 0.4.2)

<critical>
**EXECUTE EXACTLY ONE of 0.4.1 or 0.4.2 - NEVER BOTH, NEVER NEITHER**

**Decision Variable:** `previous_failure_contexts` (from Section 0.3)

| Condition | Execute | Skip |
|-----------|---------|------|
| `previous_failure_contexts` EXISTS (any Serena Memory found) | **0.4.1** | 0.4.2 |
| `previous_failure_contexts` EMPTY (no Serena Memory found) | **0.4.2** | 0.4.1 |

**IMPORTANT:**
- The decision is based SOLELY on whether Serena Memory files exist
- It does NOT matter if the input file is new or different
- It does NOT matter if this is a "new research topic"
- If ANY failure memory exists → 0.4.1 (learn from past failures)
- If NO failure memory exists → 0.4.2 (truly fresh start)
</critical>

---

### Template-Based Output Generation (Shared by 0.4.1 and 0.4.2)

<critical>
**Both UNATTENDED modes use the SAME template file:** `{template}` (template.md)

**Process:**
1. Copy `{template}` to `{default_output_file}`
2. Extract values from input and context
3. Replace `{{UNFILLED:placeholder}}` with extracted values
4. Replace `{{date}}` with current date
5. Replace `{{user_name}}` with user name

**Placeholder Mapping:**
| Placeholder | Source |
|-------------|--------|
| `pipeline_project_title` | "Anonymous Pipeline: {initial_interest_summary}" |
| `initial_interest` | Extracted from input Overview |
| `approach_selection` | "Auto-Fill Mode (UNATTENDED)" or "ROUTE_TO_0 (Failure Recovery)" |
| `session_duration` | "< 1 minute (automated extraction)" |
| `existing_context` | First paragraph of input Overview |
| `lessons_from_previous_attempts` | From Serena Memory (0.4.1) or "N/A - First attempt" (0.4.2) |
| `session_plan` | "Auto-extracted from structured input" |
| `technique_sessions` | "Auto-Fill Mode - No interactive sessions" |
| `main_research_question` | Extracted main theme |
| `refined_question` | Synthesized research question |
| `detailed_questions` | Extracted from Topics section |
| `reference_papers` | Extracted or "Not provided - will discover in Phase 1" |
| `so_what_validation` | "Input from established research venue - significance pre-validated" |
| `feasibility_validation` | "Structured input indicates clear research direction" |
| `phase1_research_question` | Same as refined_question |
| `phase1_detailed_question` | Same as detailed_questions |
| `phase1_reference_papers` | Same as reference_papers |
| `key_insights` | "Input contains well-defined research scope" |
| `techniques_used` | "Auto-Fill Mode (structured input extraction)" |
| `areas_for_exploration` | Extracted from Topics not in main question |
| `next_steps` | "Proceed to Phase 1 - Targeted Research" |
</critical>

---

### 0.4.1 Check for Previous Failure Context (ROUTE_TO_0 Case)

<check if="previous_failure_contexts EXISTS (any Serena Memory files found in Section 0.3)">

<critical>
**This is a ROUTE_TO_0 case** - Phase 0 is being re-executed after a previous failure.
The new brainstorm must learn from past mistakes and take a different direction.
</critical>

<action>**Find Previous Brainstorm:**

1. Search within `{research_folder}` for any `00_brainstorm_session.md` files
2. This includes files in `_archive/*/` subfolders (archived from previous attempts)
3. If multiple files found, read the most recent one (by file modification time)
4. Store the content as `previous_brainstorm_content`
</action>

<action>**Generate Informed Brainstorm:**

You now have access to THREE sources of information:

| Source | Description | How to Use |
|--------|-------------|------------|
| 1. **Serena Memory** | All failure/pivot/limitation records from Section 0.3 | Extract lessons learned, approaches to AVOID |
| 2. **Previous Brainstorm** | `00_brainstorm_session.md` from failed attempt (if found) | Understand what was tried before |
| 3. **Current Input** | The `research_idea_content` provided for THIS execution | The NEW research direction to pursue |

<critical>
**MERGE STRATEGY (NEW Input + Past Lessons):**

The goal is to **APPLY lessons learned FROM past failures TO the current new input**.

1. **Start with Current Input** - This is the PRIMARY research direction
2. **Filter through Past Lessons** - Avoid approaches that failed before
3. **Output** - A research direction that:
   - Follows the CURRENT input's topic/theme
   - AVOIDS pitfalls identified in Serena Memory
   - Takes a DIFFERENT approach than what failed before

**Example:**
- Current Input: "Weak supervision learning for image classification"
- Past Failure: "Hypothesis about label noise handling failed because metric was flawed"
- Merged Output: "Weak supervision learning with ROBUST metrics (avoiding the flawed metric approach)"
</critical>

Based on all three contexts, generate a NEW `00_brainstorm_session.md` that:
- **Starts from** the CURRENT input's research direction (not past direction)
- **Analyzes** what went wrong in previous attempts (from Serena Memory)
- **Identifies** approaches to AVOID (from failure root causes and lessons learned)
- **Preserves** what showed PROMISE (from partial results, if applicable to current input)
- **Proposes** a research question that combines current input with lessons learned

Include a "## Lessons from Previous Attempts" section in the output that summarizes:
- What was tried before (briefly)
- Why it failed
- How THIS new direction avoids those pitfalls
</action>

<action>**Generate Output Using Template (ROUTE_TO_0):**

> 📖 **Use Template-Based Output Generation** (see section above)

**4a. Create output file from template:**
1. Copy `{template}` to `{default_output_file}`
2. Replace `{{date}}` with current date
3. Replace `{{user_name}}` with user name

**4b. Fill placeholders with ROUTE_TO_0 context:**

| Placeholder | Value for ROUTE_TO_0 |
|-------------|---------------------|
| `approach_selection` | "ROUTE_TO_0 (Failure Recovery Mode)" |
| `lessons_from_previous_attempts` | Generate summary from Serena Memory (see Merge Strategy above) |
| `initial_interest` | Extracted from CURRENT input (not past) |
| `existing_context` | Combined: current input context + "Retrying after previous failure" |
| Other placeholders | Follow Template-Based Output Generation mapping |

**CRITICAL for ROUTE_TO_0:**
- The `lessons_from_previous_attempts` section MUST contain:
  - What was tried before (from previous brainstorm)
  - Why it failed (from Serena Memory)
  - How THIS direction avoids those pitfalls
- Research question MUST be DIFFERENT from what failed before
</action>

<action>**Save and Complete (ROUTE_TO_0):**

**4c. Create Archon Pipeline Project (Phase Tasks - count depends on skip_baseline_comparison):**

> 📖 **Helper Reference:** `{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers/archon_pipeline_creation.md`

Extract `initial_interest_summary` from the NEW research_question (first 50 chars).

**Read `skip_baseline_comparison` from module.yaml:**
```python
# Read from module.yaml → pipeline_options.skip_baseline_comparison
skip_baseline = module_config.get("pipeline_options", {}).get("skip_baseline_comparison", False)
```

```python
from archon_pipeline_creation import create_pipeline_phase_tasks

result = create_pipeline_phase_tasks(
    project_title=f"Anonymous Pipeline: {initial_interest_summary}",
    project_description="[UNATTENDED][ROUTE_TO_0] Research pipeline - retry after previous failure",
    is_unattended=True,
    skip_baseline_comparison=skip_baseline
)

if result["success"]:
    pipeline_project_id = result["pipeline_project_id"]
    phase_task_ids = result["phase_task_ids"]
    expected = 9 if skip_baseline else 10
    print(f"✅ Pipeline created: {pipeline_project_id}, Phase Tasks: {result['created_count']}/{expected}")
else:
    STOP(f"Pipeline creation failed: {result['message']}")
```

**4d. Update Task Status (Phase 0 → done, Phase 1 → doing):**
```python
mcp__archon__manage_task(action="update", task_id=phase_task_ids["phase0"], status="done")
mcp__archon__manage_task(action="update", task_id=phase_task_ids["phase1"], status="doing")
```
Log: "✅ Phase 0 → done, Phase 1 → doing"

**4e. Complete ROUTE_TO_0 Auto-Fill:**
Display: "✅ ROUTE_TO_0 Auto-Fill Complete (learned from {N} failure records) - Ready for Phase 1: /phase1-targeted"
**END workflow** - skip interactive steps
</action>

</check>

---

### 0.4.2 Standard Auto-Fill (First Execution - No Failure Context)

<check if="previous_failure_contexts is EMPTY (NO Serena Memory files found in Section 0.3)">

<auto-fill-execution>
**When AUTO-FILL MODE is activated (first time, no failure history):**

> 📖 **Use Template-Based Output Generation** (see section above)

**1. Extract Research Components from Input:**

| Component | Extraction Rule |
|-----------|-----------------|
| `research_question` | Identify MAIN research theme from Overview; synthesize if multiple |
| `detailed_question` | Extract from "## Topics" or specific questions listed (max 5) |
| `reference_papers` | Extract if mentioned, otherwise "Not provided - will discover in Phase 1" |
| `initial_interest` | First sentence/theme from Overview section |
| `existing_context` | First paragraph of Overview + "Source Type: Workshop CFP / Structured Input" |

**2. Create Output File from Template:**

```
1. Copy {template} to {default_output_file}
2. Replace {{date}} with current date
3. Replace {{user_name}} with user name
```

**3. Fill Placeholders with Extracted Values:**

> 📖 **Use "Template-Based Output Generation" mapping above** with these overrides:

| Placeholder | Override Value |
|-------------|----------------|
| `approach_selection` | "Auto-Fill Mode (Structured Input Detected)" |
| `lessons_from_previous_attempts` | "N/A - First attempt" |

<action>**4a. Create Archon Pipeline Project (Phase Tasks - count depends on skip_baseline_comparison):**

> 📖 **Helper Reference:** `{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers/archon_pipeline_creation.md`

Extract `initial_interest_summary` from research_question (first 50 chars).

**Read `skip_baseline_comparison` from module.yaml:**
```python
# Read from module.yaml → pipeline_options.skip_baseline_comparison
skip_baseline = module_config.get("pipeline_options", {}).get("skip_baseline_comparison", False)
```

```python
from archon_pipeline_creation import create_pipeline_phase_tasks

result = create_pipeline_phase_tasks(
    project_title=f"Anonymous Pipeline: {initial_interest_summary}",
    project_description="[UNATTENDED] Research pipeline from brainstorm to implementation",
    is_unattended=True,
    skip_baseline_comparison=skip_baseline
)

if result["success"]:
    pipeline_project_id = result["pipeline_project_id"]
    phase_task_ids = result["phase_task_ids"]
    expected = 9 if skip_baseline else 10
    print(f"✅ Pipeline created: {pipeline_project_id}, Phase Tasks: {result['created_count']}/{expected}")
else:
    STOP(f"Pipeline creation failed: {result['message']}")
```
</action>

<action>**4b. Update Task Status (Phase 0 → done, Phase 1 → doing):**
```python
mcp__archon__manage_task(action="update", task_id=phase_task_ids["phase0"], status="done")
mcp__archon__manage_task(action="update", task_id=phase_task_ids["phase1"], status="doing")
```
Log: "✅ Phase 0 → done, Phase 1 → doing"
</action>

<action>**4c. Complete Auto-Fill:**
Display: "✅ Auto-Fill Complete - Ready for Phase 1: /phase1-targeted"
**END workflow** - skip interactive steps
</action>
</auto-fill-execution>

</check>

---

## 0.5 Pipeline Initialization (Archon) - INTERACTIVE MODE ONLY

<critical>
**⚠️ SKIP THIS SECTION if UNATTENDED mode (0.4.1 or 0.4.2 already handled Archon setup)**

This section is ONLY for Interactive Mode (when Section 0.4 was skipped).

Phase 0 is the starting point of the Anonymous Pipeline.
**Always CREATE a new Pipeline Project** - no search/resume logic needed.

- Failure context is passed via Serena Memory (Section 0.3)
- Previous failed pipelines remain as historical records
- Each research attempt has independent tracking
</critical>

<action>**Create Pipeline Project (After Step 1 - initial_interest obtained):**

> 📖 **Helper Reference:** `{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers/archon_pipeline_creation.md`

**Read `skip_baseline_comparison` from module.yaml:**
```python
# Read from module.yaml → pipeline_options.skip_baseline_comparison
skip_baseline = module_config.get("pipeline_options", {}).get("skip_baseline_comparison", False)
```

```python
from archon_pipeline_creation import create_pipeline_phase_tasks

result = create_pipeline_phase_tasks(
    project_title=f"Anonymous Pipeline: {initial_interest_summary}",
    project_description="Research pipeline from brainstorm to implementation",
    is_unattended=False, # Interactive mode
    skip_baseline_comparison=skip_baseline
)

if result["success"]:
    pipeline_project_id = result["pipeline_project_id"]
    phase_task_ids = result["phase_task_ids"]
    expected = 9 if skip_baseline else 10
    print(f"✅ Pipeline created: {pipeline_project_id}, Phase Tasks: {result['created_count']}/{expected}")
else:
    STOP(f"Pipeline creation failed: {result['message']}")
```
</action>

<action>**Store Pipeline IDs for Step 7:**
Save for completion: `pipeline_project_id`, `phase_task_ids`
</action>

---

## 0.6 Initialize Output File - INTERACTIVE MODE ONLY

<critical>
**⚠️ SKIP THIS SECTION if UNATTENDED mode (0.4.1 or 0.4.2 already created output file)**
</critical>

<action>**Create output directory and file:**

1. Ensure directory exists: `{research_output_path}/`
2. Copy {template} to {default_output_file}
3. Replace `{{date}}` with current date
4. Replace `{{user_name}}` with {user_name}
</action>

---

## 0.7 Interactive Mode Router (NEW) - INTERACTIVE MODE ONLY

<critical>
**⚠️ SKIP THIS SECTION if UNATTENDED mode (0.4.1 or 0.4.2 already completed workflow)**
</critical>

<action>**Detect User's Preferred Interactive Mode:**

**Mode Selection Logic:**
- First-time user (no preference stored) → Recommend Discovery Mode
- Returning user → Check for saved preference (if available)
- User can choose either mode

**Present Mode Options:**

"{user_name}, welcome to Phase 0 Brainstorming!

I'm excited to help you discover and refine your research question.

**Choose Your Interactive Mode:**

**[D] Discovery Mode (RECOMMENDED)** - High-energy collaborative exploration
- Generate 20-30 research angles together with anti-bias pivoting
- YES AND facilitation - I build on your ideas
- User control commands anytime ('different angle', 'go deeper', 'I'm ready')
- Default: keep exploring until you say ready
- Best for: Vague interests, creative partnership, breakthrough ideas

**[S] Standard Mode** - Traditional structured approach
- 7-step sequential workflow with technique-based exploration
- Form-based information gathering with clear checkpoints
- Best for: Well-defined directions, systematic exploration

Which mode would you like to use? (D/S)"
</action>

<action if="User selects Discovery Mode (D)">**Route to Discovery Mode:**

"Excellent choice! Let's embark on a high-energy research discovery journey together.

**Discovery Mode - How It Works:**
- We'll generate 20-30 research angles collaboratively
- I'll actively contribute ideas and build on yours (YES AND)
- Every 5-10 angles, I'll consciously pivot domains to avoid clustering
- You're in control with these commands anytime:
  * 'different angle' → I immediately pivot to new direction
  * 'go deeper' → We deep dive the current angle
  * 'next technique' → Move to exploration phase
  * 'I'm ready' → Start synthesizing to one question

**Energy Checkpoints:**
- Every 8-10 exchanges, I'll check your energy
- Default: we keep exploring (quantity first!)
- Synthesis comes AFTER 20-30 angles

**Ready to start?** Let's begin the discovery!"

**Update nextStepFile:**
- Set `nextStepFile = '{workflow_path}/steps/step-01-interactive-discovery.md'`

**Continue to Menu section below**
</action>

<action if="User selects Standard Mode (S)">**Route to Standard Mode:**

"Great! We'll use the traditional 7-step structured workflow.

This mode provides systematic guidance through:
1. Session Setup - Understanding your research interest
2. Approach Selection - Choosing exploration techniques
3. Technique Execution - Facilitated brainstorming
4-7. Synthesis, References, Validation, Completion

**Ready to begin?** Let's start with understanding your research interest."

**Keep nextStepFile unchanged:**
- `nextStepFile = '{workflow_path}/steps/step-01-session-setup.md'` (default)

**Continue to Menu section below**
</action>

</critical>

---

## File Write (Step 0)

<file-write>
**Save progress after Step 0 initialization:**

1. Read {default_output_file}
2. Replace `{{UNFILLED:lessons_from_previous_attempts}}` with:
   - If `previous_failure_contexts` exists: Generate "Lessons from Previous Attempts" summary
   - If no failure context: "N/A - First attempt"
3. Write file back
4. Display: "✅ Step 0 saved"
</file-write>

---

## Menu

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [C] → Load {nextStepFile}</action>

<menu>
**Initialization Complete. Next Action:**

[C] Continue to Step 1

**Note:** Step 1 path determined by Section 0.7 Interactive Mode Router:
- Discovery Mode → {workflow_path}/steps/step-01-interactive-discovery.md
- Standard Mode → {workflow_path}/steps/step-01-session-setup.md (default)

IF C: Load and execute {nextStepFile}
</menu>

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:
- Resume detection completed and appropriate action taken
- **ALL** failure-related Serena Memory files loaded (if any exist)
- Previous brainstorm found and read (for ROUTE_TO_0 case)
- Auto-fill mode correctly detected and handled
- For ROUTE_TO_0: New brainstorm generated considering failure history
- Archon pipeline created with all phase tasks
- **Output file created from template.md** (ALL modes use same template)
- **Placeholders filled with extracted values** (not inline generation)
- User ready for Step 1 or workflow completed (auto-fill mode)

### ❌ SYSTEM FAILURE:
- Skipping resume detection check
- Reading only ONE memory file instead of ALL relevant files
- Not searching for previous brainstorm in research_folder
- **Executing 0.4.2 when Serena Memory files exist (should be 0.4.1)**
- **Misinterpreting "new input file" as "fresh execution" when memories exist**
- Ignoring failure context when generating new brainstorm (ROUTE_TO_0)
- Proceeding without Archon pipeline creation
- Not initializing output file before proceeding
- Skipping auto-fill mode detection when markers present
- **Generating output inline instead of using template.md** (must use template)

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.

---

**Step 0 Complete** - Session initialized
**Next:** Step 1 - Session Setup
